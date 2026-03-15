from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
# 延迟导入以避免循环导入
import logging
from datetime import datetime
import json
import traceback
# 导入认证相关的函数和配置
from jose import JWTError, jwt
from config.settings import settings

logger = logging.getLogger(__name__)

class OperationLogMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        # 对于日志模块的导出操作，允许GET请求；其他情况只记录 POST, PUT, DELETE 请求
        is_log_export = (request.url.path.startswith("/logs") and ("/export" in request.url.path or request.url.path.endswith("-export")) and request.method == "GET")
        if not is_log_export and request.method not in ["POST", "PUT", "DELETE"]:
            await self.app(scope, receive, send)
            return
        
        # 排除登录接口和一些不需要记录的接口
        excluded_paths = ["/login", "/docs", "/openapi.json", "/health", "/users/login"]
        if request.url.path in excluded_paths:
            await self.app(scope, receive, send)
            return

        # 对于日志模块，只记录修改操作（删除、清理等）和导出操作，排除查询操作
        if request.url.path.startswith("/logs"):
            # 定义日志模块中需要记录的操作
            log_tracked_operations = [
                ("/logs/clear", ["DELETE"]),              # 清理系统日志
                ("/logs/login/clear", ["DELETE"]),        # 清理登录日志
                ("/logs/operation/clear", ["DELETE"]),    # 清理操作日志
                ("/logs/access-clear", ["DELETE"]),       # 清理访问日志
                ("/logs/access-config", ["POST"]),        # 更新访问日志配置
                ("/logs/export/", ["GET"]),               # 导出系统日志文件
                ("/logs/login/export", ["GET"]),          # 导出登录日志
                ("/logs/operation/export", ["GET"]),      # 导出操作日志
                ("/logs/access-export", ["GET"]),         # 导出访问日志
            ]
            
            # 检查是否为需要记录的操作
            should_log = False
            for path, methods in log_tracked_operations:
                # 对于包含路径参数的路由（如 /logs/export/{filename}），需要特殊处理
                if path == "/logs/export/" and request.url.path.startswith("/logs/export/") and request.method in methods:
                    should_log = True
                    break
                # 对于访问日志导出和清理操作，需要特殊处理
                elif path in ["/logs/access-export", "/logs/access-clear"] and request.url.path == path and request.method in methods:
                    should_log = True
                    break
                elif request.url.path == path and request.method in methods:
                    should_log = True
                    break
            
            # 如果不是需要记录的操作，则不记录
            if not should_log:
                await self.app(scope, receive, send)
                return

        # 获取请求开始时间
        start_time = datetime.now()
        
        # 尝试获取用户信息
        user_info = await self.get_user_info(request)

        # 处理响应
        async def log_response(message):
            if message["type"] == "http.response.start":
                # 记录操作日志
                await self.log_operation(request, start_time, message["status"], user_info)
            await send(message)

        try:
            await self.app(scope, receive, log_response)
        except Exception as e:
            # 记录错误日志，但不抛出异常以免影响主业务流程
            try:
                await self.log_operation(request, start_time, 500, user_info)
            except:
                pass
            raise e

    async def get_user_info(self, request: Request):
        """从请求中获取用户信息"""
        try:
            # 从Authorization header中获取token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]
                # 解析JWT token获取用户信息
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                username = payload.get("sub")
                if username:
                    # 尝试从数据库获取用户ID
                    try:
                        # 延迟导入以避免循环导入
                        from config.database import AsyncSessionLocal
                        from app.user import models as user_models
                        from sqlalchemy import select
                        
                        db = AsyncSessionLocal()
                        try:
                            result = await db.execute(select(user_models.User).filter(user_models.User.username == username))
                            user = result.scalar_one_or_none()
                            if user:
                                return {"id": user.id, "username": username}
                        finally:
                            await db.close()
                    except Exception as e:
                        logger.warning(f"无法从数据库获取用户ID: {str(e)}")
                    
                    # 如果无法获取用户ID，使用默认值
                    return {"id": 0, "username": username}
            
            return {"id": 0, "username": "unknown"}
        except Exception as e:
            logger.warning(f"无法获取用户信息: {str(e)}")
            return {"id": 0, "username": "unknown"}

    async def log_operation(self, request: Request, start_time: datetime, status_code: int, user_info: dict):
        """记录操作日志"""
        try:
            # 延迟导入以避免循环导入
            from app.log import service, schemas
            from config.database import AsyncSessionLocal
            
            # 根据请求路径确定操作类型
            operation_type = self._determine_operation_type(request)
            
            # 生成更友好的操作描述
            details = self._generate_operation_description(request, user_info.get("username", "unknown"))
            
            # 获取用户信息
            user_id = user_info["id"] if user_info else 0
            username = user_info["username"] if user_info else "unknown"
            
            # 创建操作日志记录
            log_data = schemas.OperationLogCreate(
                user_id=user_id,
                username=username,
                operation_type=operation_type,
                details=details
            )
            
            # 手动创建数据库会话并记录日志
            db = AsyncSessionLocal()
            try:
                await service.create_operation_log(db, log_data)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"记录操作日志到数据库失败: {str(e)}")
                # 不要抛出异常，以免影响主业务流程
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"记录操作日志时出错: {str(e)}")
            # 不要抛出异常，以免影响主业务流程

    def _determine_operation_type(self, request: Request) -> str:
        """确定操作类型"""
        # 根据请求路径确定操作类型
        if request.url.path.startswith("/logs"):
            return "日志审计"
        elif request.url.path.startswith("/system"):
            return "系统设置"
        elif request.url.path.startswith("/users"):
            return "用户管理"
        else:
            # 对于其他路径，根据方法确定操作类型
            if request.method in ["POST", "PUT", "DELETE"]:
                return "其他操作"
            else:
                return "其他操作"

    def _generate_operation_description(self, request: Request, username: str) -> str:
        """生成操作描述"""
        # 定义操作描述映射
        operation_descriptions = {
            "/logs/clear": "清理了系统日志",
            "/logs/login/clear": "清理了登录日志",
            "/logs/operation/clear": "清理了操作日志",
            "/logs/access-clear": "清理了访问日志",
            "/logs/access-config": "更新了访问日志配置",
            "/logs/export/": "导出了系统日志文件",
            "/logs/login/export": "导出了登录日志",
            "/logs/operation/export": "导出了操作日志",
            "/logs/access-export": "导出了访问日志",
            "/system/env-config": "修改了系统环境配置",
            "/system/restart": "重启了系统服务",
            "/users/": "创建了用户",
            "/users/me/password": "修改了密码",
        }
        
        # 查找匹配的操作描述
        description = "执行了操作"
        for path, desc in operation_descriptions.items():
            # 特殊处理用户路由（借鉴这种处理方式）
            if path == "/users/" and request.url.path.startswith("/users/"):
                # 处理用户相关操作，根据方法类型确定具体操作
                if request.method == "POST":
                    description = "创建了用户"
                    break
                elif request.method == "PUT":
                    if request.url.path == "/users/me/password":
                        description = "修改了密码"
                        break
                    else:
                        description = "更新了用户信息"
                        break
                elif request.method == "DELETE":
                    description = "删除了用户"
                    break
                elif request.method == "GET":
                    if request.url.path == "/users/me":
                        description = "查询了个人信息"
                        break
                    elif request.url.path == "/users/":
                        description = "查询了用户列表"
                        break
                    else:
                        description = "查询了用户信息"
                        break
            # 特殊处理日志相关路由（借鉴用户路由的处理方式）
            elif path == "/logs/export/" and request.url.path.startswith("/logs/export/"):
                # 处理日志导出操作
                if request.method == "GET":
                    description = "导出了系统日志文件"
                    break
            elif path == "/logs/login/export" and request.url.path == "/logs/login/export":
                # 处理登录日志导出操作
                if request.method == "GET":
                    description = "导出了登录日志"
                    break
            elif path == "/logs/operation/export" and request.url.path == "/logs/operation/export":
                # 处理操作日志导出操作
                if request.method == "GET":
                    description = "导出了操作日志"
                    break
            elif path == "/logs/access-export" and request.url.path == "/logs/access-export":
                # 处理访问日志导出操作
                if request.method == "GET":
                    description = "导出了访问日志"
                    break
            elif path == "/logs/clear" and request.url.path.startswith("/logs/clear"):
                # 处理日志清理操作
                if request.method == "DELETE":
                    if request.url.path == "/logs/clear":
                        description = "清理了系统日志"
                        break
                    elif request.url.path == "/logs/login/clear":
                        description = "清理了登录日志"
                        break
                    elif request.url.path == "/logs/operation/clear":
                        description = "清理了操作日志"
                        break
                    elif request.url.path == "/logs/access-clear":
                        description = "清理了访问日志"
                        break
            # 特殊处理系统配置路由
            elif path == "/system/env-config" and request.method in ["PUT", "POST"] and request.url.path == "/system/env-config":
                description = desc
                break
            # 特殊处理系统重启路由
            elif path == "/system/restart" and request.method == "POST" and request.url.path == "/system/restart":
                description = desc
                break
            # 特殊处理密码修改路由
            elif path == "/users/me/password" and request.method == "PUT" and request.url.path == "/users/me/password":
                description = desc
                break
            # 其他精确路径匹配
            elif request.url.path == path:
                description = desc
                break
        
        # 生成完整的操作描述
        return f"{username}用户{description}"

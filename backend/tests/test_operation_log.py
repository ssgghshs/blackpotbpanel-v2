#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
操作日志功能测试脚本
"""

import sys
import os
import asyncio

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.log import models, schemas, service
from config.database import Base, engine
from config.settings import settings

async def test_operation_log():
    """测试操作日志功能"""
    # 使用现有的引擎
    
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建测试会话
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 创建操作日志
        operation_log_data = schemas.OperationLogCreate(
            user_id=1,
            username="testuser",
            operation_type="测试操作",
            details="这是一个测试操作日志"
        )
        
        # 测试创建操作日志
        print("测试创建操作日志...")
        created_log = await service.create_operation_log(session, operation_log_data)
        print(f"创建成功: {created_log}")
        
        # 测试获取操作日志列表
        print("\n测试获取操作日志列表...")
        logs = await service.get_operation_logs(session)
        print(f"获取到 {len(logs)} 条操作日志")
        for log in logs:
            print(f"  - {log}")
        
        # 测试获取特定用户的操作日志
        print("\n测试获取特定用户的操作日志...")
        user_logs = await service.get_user_operation_logs(session, user_id=1)
        print(f"用户 1 的操作日志数量: {len(user_logs)}")
        for log in user_logs:
            print(f"  - {log}")

if __name__ == "__main__":
    asyncio.run(test_operation_log())
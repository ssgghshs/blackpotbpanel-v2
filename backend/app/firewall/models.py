# coding: utf-8
# 防火墙数据库模型
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from config.database import FirewallBase
from config.settings import settings
from datetime import datetime
import pytz

def get_localized_datetime():
    """根据配置的时区获取本地化的时间"""
    try:
        # 获取配置的时区
        timezone_str = settings.TIMEZONE if hasattr(settings, 'TIMEZONE') else 'UTC'
        
        # 创建时区对象
        if timezone_str == 'UTC':
            tz = pytz.UTC
        else:
            tz = pytz.timezone(timezone_str)
        
        # 获取当前时间并本地化
        now = datetime.now(tz)
        return now
    except Exception as e:
        # 如果时区配置有问题，回退到UTC
        print(f"时区配置错误，使用UTC: {e}")
        return datetime.now(pytz.UTC)



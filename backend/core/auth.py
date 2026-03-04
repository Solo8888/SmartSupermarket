# 授权模块
# JWT令牌的生成和验证，附带user_id
from datetime import datetime, timedelta, timezone
from pydantic_settings import BaseSettings
import jwt
from typing import Optional

from config import settings


class JWTHandler:
    """JWT令牌处理器"""
    @staticmethod
    def generate_token(user_id: str, expires_in_minutes: Optional[int] = None) -> str:
        """生成JWT令牌
        
        Args:
            user_id: 用户ID
            expires_in_minutes: 过期时间（分钟），默认使用配置中的值
        
        Returns:
            JWT令牌字符串
        """
        if expires_in_minutes is None:
            expires_in_minutes = settings.jwt_expires_minutes
        # 计算过期时间
        expire_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        # 构建payload - 使用时间戳而不是datetime对象
        payload = {
            'user_id': user_id, 
            'expire_at': int(expire_at.timestamp()),
            'issued_at': int(datetime.now(timezone.utc).timestamp())
        }
        # 生成JWT令牌
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token

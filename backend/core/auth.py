# 授权模块
# JWT令牌的生成和验证，附带user_id
from datetime import datetime, timedelta, timezone
from pydantic_settings import BaseSettings
import jwt
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from core.exceptions import UnauthorizedError


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

    @staticmethod
    def verify_token(token: str) -> str:
        """
        验证JWT令牌并提取user_id

        Args:
            token: JWT令牌字符串

        Returns:
            user_id: 验证通过的用户ID

        Raises:
            UnauthorizedError: 令牌无效或过期
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            user_id = payload.get('user_id')
            if user_id is None:
                raise UnauthorizedError("令牌中缺少user_id")
            return str(user_id)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("令牌已过期")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("令牌无效")


security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    获取当前用户ID的依赖项

    Args:
        credentials: HTTP认证凭据

    Returns:
        当前用户的ID
    """
    token = credentials.credentials
    user_id = JWTHandler.verify_token(token)
    return str(user_id)

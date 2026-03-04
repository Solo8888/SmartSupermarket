# 认证相关服务
# 处理手机号认证业务逻辑
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.exceptions import NotFoundError, ServerError
from models.user import User
from core.auth import JWTHandler
from .schemas import LoginResponse

# 密码加密上下文
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService:
    @staticmethod
    def verify_password(password, password1):
        return pwd_context.verify(password, password1)

    def login(self, db: Session, phone: str, password: str) -> dict:
        """
        现有用户登录

        Args:
            db: 数据库会话
            phone: 手机号
            password: 密码

        Returns:
            登录成功后的响应
        """
        try:
            user = db.query(User).filter(User.phone == phone).first()
            if not user:
                raise NotFoundError("用户不存在")
            if not self.verify_password(password, user.password):
                raise NotFoundError("密码错误或用户已被禁用")

            user.updated_at = func.current_timestamp()
            db.commit()
            token = JWTHandler().generate_token(user.id)
            return {
                'message': '登录成功',
                'token': token,
                'user_id': user.id,
            }
        except NotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise ServerError(f"登录失败: {str(e)}")

# 认证相关服务
# 处理手机号认证业务逻辑
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.exceptions import NotFoundError, ServerError, ConflictError
from models.user import User
from core.auth import JWTHandler
from .schemas import LoginResponse, RegisterResponse

# 密码加密上下文
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService:
    @staticmethod
    def verify_password(password, password1):
        return pwd_context.verify(password, password1)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

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
                'access_token': token,
                'token_type': 'bearer',
                'user_id': user.id,
                'phone': user.phone,
                'name': user.username
            }
        except NotFoundError:
            raise
        except Exception as e:
            db.rollback()
            raise ServerError(f"登录失败: {str(e)}")

    def register(self, db: Session, username: str, phone: str, password: str, role: str = 'customer') -> dict:
        """
        新用户注册

        Args:
            db: 数据库会话
            username: 用户名
            phone: 手机号
            password: 密码
            role: 用户角色，默认为customer

        Returns:
            注册成功后的响应
        """
        try:
            # 检查手机号是否已存在
            existing_user = db.query(User).filter(User.phone == phone).first()
            if existing_user:
                raise ConflictError("该手机号已被注册")

            # 检查用户名是否已存在
            existing_username = db.query(User).filter(User.username == username).first()
            if existing_username:
                raise ConflictError("该用户名已被使用")

            # 创建新用户
            hashed_password = self.get_password_hash(password)
            user = User(
                username=username,
                phone=phone,
                password=hashed_password,
                role=role,
                status='active',
                created_at=func.current_timestamp(),
                updated_at=func.current_timestamp()
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return {
                'user_id': user.id,
                'username': user.username,
                'phone': user.phone,
                'role': user.role,
                'message': '注册成功'
            }
        except ConflictError:
            raise
        except Exception as e:
            db.rollback()
            raise ServerError(f"注册失败: {str(e)}")

# 用户模块服务
# 提供用户相关的业务逻辑

from typing import Dict, Any

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.auth import JWTHandler
from models.user import User


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        return self.pwd_context.hash(password)
    
    def login(self, db: Session, phone: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        # 根据手机号查找用户
        user = db.query(User).filter(User.phone == phone).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="手机号或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="手机号或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户是否激活
        if user.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账号已被禁用",
            )
        
        # 创建访问令牌
        access_token = JWTHandler.generate_token(str(user.id))
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role
        }
    
    def register(self, db: Session, username: str, phone: str, password: str, role: str) -> Dict[str, Any]:
        """用户注册"""
        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被注册",
            )
        
        # 检查用户名是否已存在
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用",
            )
        
        # 创建新用户
        hashed_password = self.get_password_hash(password)
        new_user = User(
            username=username,
            phone=phone,
            password=hashed_password,
            role=role,
            status='active'
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "user_id": str(new_user.id),
            "username": new_user.username,
            "phone": new_user.phone,
            "role": new_user.role
        }
    
    def change_password(self, db: Session, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        
        # 验证旧密码
        if not self.verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="旧密码错误",
            )
        
        # 更新密码
        user.password = self.get_password_hash(new_password)
        db.commit()
        
        return {
            "message": "密码修改成功"
        }


class UserService:
    """用户管理服务类"""
    
    @staticmethod
    def get_user_list(db: Session, current_user: User) -> Dict[str, Any]:
        """获取用户列表"""
        # 验证当前用户是否为系统管理员
        if current_user.role != "system_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        
        # 获取所有用户
        users = db.query(User).all()
        
        # 构建响应数据
        user_responses = []
        for user in users:
            user_responses.append({
                "id": str(user.id),
                "username": user.username,
                "phone": user.phone or "",
                "role": user.role,
                "is_active": user.status == 'active',
                "created_at": user.created_at
            })
        
        return {
            "items": user_responses,
            "total": len(user_responses),
            "page": 1,
            "size": len(user_responses)
        }
    
    @staticmethod
    def update_user_role(db: Session, user_id: str, payload: Any, current_user: User) -> Dict[str, Any]:
        """更新用户角色"""
        # 验证当前用户是否为系统管理员
        if current_user.role != "system_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        
        # 更新角色
        user.role = payload.role
        db.commit()
        db.refresh(user)
        
        return {
            "id": str(user.id),
            "username": user.username,
            "phone": user.phone or "",
            "role": user.role,
            "is_active": user.status == 'active',
            "created_at": user.created_at
        }

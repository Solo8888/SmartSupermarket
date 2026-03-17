# 用户服务
# 处理用户相关的业务逻辑

from sqlalchemy.orm import Session
from models.user import User
from .schemas import UserUpdateRole
from core.exceptions import NotFoundError
from sqlalchemy import func


class UserService:
    @staticmethod
    def get_user_list(db: Session, current_user) -> dict:
        """
        获取用户列表

        Args:
            db: 数据库会话
            current_user: 当前用户

        Returns:
            用户列表和总数
        """
        # 查询所有用户
        users = db.query(User).all()
        total = len(users)

        # 转换为字典列表返回
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "gender": user.gender,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in users
        ]

        return {
            "items": user_list,
            "total": total
        }
    
    @staticmethod
    def update_user_role(db: Session, user_id: str, payload: UserUpdateRole, current_user) -> dict:
        """
        更新用户角色

        Args:
            db: 数据库会话
            user_id: 用户ID
            payload: 更新用户角色请求体
            current_user: 当前用户

        Returns:
            更新后的用户信息

        Raises:
            NotFoundError: 用户不存在
        """
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")

        # 更新用户角色
        user.role = payload.role
        db.commit()
        db.refresh(user)

        # 返回更新后的用户信息
        return {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "gender": user.gender,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
# 门店分配服务
# 处理门店分配相关的业务逻辑

from sqlalchemy.orm import Session

from core.exceptions import NotFoundError, ClientError
from models.store import Store
from models.user import User
from models.user_store import UserStore
from .schemas import StoreAllocationCreate


class UserStoreService:
    @staticmethod
    def create_store_allocation(db: Session, payload: StoreAllocationCreate, user) -> dict:
        """
        创建门店分配

        Args:
            db: 数据库会话
            payload: 创建门店分配请求体
            user: 当前用户

        Returns:
            创建成功的门店分配信息

        Raises:
            NotFoundError: 用户或门店不存在
            ClientError: 分配关系已存在
        """
        # 检查用户是否存在
        existing_user = db.query(User).filter(User.id == payload.user_id).first()
        if not existing_user:
            raise NotFoundError("用户不存在")

        # 检查门店是否存在
        existing_store = db.query(Store).filter(Store.id == payload.store_id).first()
        if not existing_store:
            raise NotFoundError("门店不存在")

        # 检查分配关系是否已存在
        existing_allocation = db.query(UserStore).filter(
            UserStore.user_id == payload.user_id,
            UserStore.store_id == payload.store_id
        ).first()
        if existing_allocation:
            raise ClientError("该用户已分配到此门店", "ALLOCATION_EXISTS")

        # 创建新的门店分配
        allocation = UserStore(
            user_id=payload.user_id,
            store_id=payload.store_id
        )

        db.add(allocation)
        db.commit()
        db.refresh(allocation)

        # 转换为字典返回
        return {
            "id": allocation.id,
            "user_id": allocation.user_id,
            "store_id": allocation.store_id,
            "created_at": allocation.created_at
        }
    
    @staticmethod
    def get_user_stores(db: Session, user_id: str, current_user) -> list:
        """
        获取用户的门店列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            current_user: 当前用户

        Returns:
            用户的门店列表

        Raises:
            NotFoundError: 用户不存在
        """
        # 检查用户是否存在
        existing_user = db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            raise NotFoundError("用户不存在")

        # 查询用户的门店分配
        allocations = db.query(UserStore, Store.name.label('store_name')).join(
            Store, UserStore.store_id == Store.id
        ).filter(UserStore.user_id == user_id).all()

        # 转换为字典列表返回
        return [
            {
                "id": allocation.UserStore.id,
                "store_id": allocation.UserStore.store_id,
                "store_name": allocation.store_name,
                "created_at": allocation.UserStore.created_at
            }
            for allocation in allocations
        ]
    
    @staticmethod
    def get_store_users(db: Session, store_id: str, current_user) -> list:
        """
        获取门店的管理员列表

        Args:
            db: 数据库会话
            store_id: 门店ID
            current_user: 当前用户

        Returns:
            门店的管理员列表

        Raises:
            NotFoundError: 门店不存在
        """
        # 检查门店是否存在
        existing_store = db.query(Store).filter(Store.id == store_id).first()
        if not existing_store:
            raise NotFoundError("门店不存在")

        # 查询门店的用户分配
        allocations = db.query(UserStore, User.username.label('username'), User.role.label('role')).join(
            User, UserStore.user_id == User.id
        ).filter(UserStore.store_id == store_id).all()

        # 转换为字典列表返回
        return [
            {
                "id": allocation.UserStore.id,
                "user_id": allocation.UserStore.user_id,
                "username": allocation.username,
                "role": allocation.role,
                "created_at": allocation.UserStore.created_at
            }
            for allocation in allocations
        ]
    
    @staticmethod
    def delete_store_allocation(db: Session, allocation_id: str, current_user) -> dict:
        """
        取消门店分配

        Args:
            db: 数据库会话
            allocation_id: 分配ID
            current_user: 当前用户

        Returns:
            删除成功的信息

        Raises:
            NotFoundError: 分配不存在
        """
        # 检查分配是否存在
        allocation = db.query(UserStore).filter(UserStore.id == allocation_id).first()
        if not allocation:
            raise NotFoundError("分配不存在")

        # 删除分配
        db.delete(allocation)
        db.commit()

        # 返回删除成功信息
        return {
            "message": "门店分配已取消",
            "id": allocation_id
        }

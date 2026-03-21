# 地址簿服务
# 处理地址簿相关的业务逻辑

from sqlalchemy.orm import Session
from models.address_book import AddressBook as Address
from .schemas import AddressCreate
from core.exceptions import ClientError
import uuid


class AddressService:
    @staticmethod
    def create_address(db: Session, payload: AddressCreate, user_id: str) -> dict:
        """
        创建地址

        Args:
            db: 数据库会话
            payload: 创建地址请求体
            user_id: 用户ID

        Returns:
            创建成功的地址信息
        """
        # 如果设置为默认地址，先将该用户的其他地址设置为非默认
        if payload.is_default:
            db.query(Address).filter(Address.user_id == user_id).update({"is_default": False})

        # 创建新地址
        address = Address(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipient=payload.name,
            phone=payload.phone,
            province=payload.province,
            city=payload.city,
            district=payload.district,
            detail_address=payload.address,
            is_default=payload.is_default
        )

        db.add(address)
        db.commit()
        db.refresh(address)

        # 转换为字典返回
        return {
            "id": address.id,
            "user_id": address.user_id,
            "name": address.recipient,
            "phone": address.phone,
            "province": address.province,
            "city": address.city,
            "district": address.district,
            "address": address.detail_address,
            "is_default": address.is_default,
            "created_at": address.created_at,
            "updated_at": address.updated_at
        }

    @staticmethod
    def get_addresses(db: Session, user_id: str) -> list:
        """
        获取用户的地址列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户的地址列表
        """
        # 查询用户的所有地址
        addresses = db.query(Address).filter(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.updated_at.desc()).all()

        # 转换为字典列表返回
        return [
            {
                "id": address.id,
                "user_id": address.user_id,
                "name": address.recipient,
                "phone": address.phone,
                "province": address.province,
                "city": address.city,
                "district": address.district,
                "address": address.detail_address,
                "is_default": address.is_default,
                "created_at": address.created_at,
                "updated_at": address.updated_at
            }
            for address in addresses
        ]

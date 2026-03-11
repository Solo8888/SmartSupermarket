# 订单服务
# 处理订单相关的业务逻辑

from sqlalchemy.orm import Session
from models.order import Order, OrderItem
from models.product import Product
from .schemas import OrderCreate
from core.exceptions import NotFoundError
from sqlalchemy import func
from datetime import datetime
import uuid
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from typing import Optional


class OrderService:
    @staticmethod
    def generate_order_no() -> str:
        """
        生成订单编号
        
        Returns:
            订单编号
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = str(uuid.uuid4())[:8].upper()
        return f'ORD{timestamp}{random_str}'

    @staticmethod
    def create_order(db: Session, payload: OrderCreate, user) -> dict:
        """
        创建订单

        Args:
            db: 数据库会话
            payload: 创建订单请求体
            user: 当前用户

        Returns:
            创建成功的订单信息
        """
        from decimal import Decimal

        # 生成订单编号
        order_no = OrderService.generate_order_no()

        # 计算订单金额
        total_amount = Decimal('0')
        order_items = []

        for item_payload in payload.items:
            # 查询商品信息
            product = db.query(Product).filter(Product.id == item_payload.product_id).first()
            if not product:
                raise ValueError(f"商品 {item_payload.product_id} 不存在")

            # 计算小计
            subtotal = product.price * item_payload.quantity
            total_amount += subtotal

            # 创建订单项
            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                product_image=product.image_url,
                price=product.price,
                quantity=item_payload.quantity,
                subtotal=subtotal
            )
            order_items.append(order_item)

        # 计算最终金额（这里简化处理，没有优惠）
        discount_amount = Decimal('0')
        final_amount = total_amount - discount_amount

        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user.id,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            status='pending',
            shipping_address=payload.shipping_address,
            contact_name=payload.contact_name,
            contact_phone=payload.contact_phone,
            remark=payload.remark
        )

        db.add(order)
        db.flush()

        # 保存订单项
        for order_item in order_items:
            order_item.order_id = order.id
            db.add(order_item)

        db.commit()
        db.refresh(order)

        # 转换为字典返回
        return {
            "id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_time": order.payment_time,
            "shipping_address": order.shipping_address,
            "contact_name": order.contact_name,
            "contact_phone": order.contact_phone,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }

    @staticmethod
    def get_orders(
        db: Session,
        params: Params,
        user,
        status: Optional[str] = None
    ) -> Page[Order]:
        """
        获取订单列表（分页）

        Args:
            db: 数据库会话
            params: 分页参数
            user: 当前用户
            status: 订单状态筛选（可选）

        Returns:
            订单列表（分页）
        """
        query = db.query(Order)

        # 普通用户只能查看自己的订单
        if user.role == 'customer':
            query = query.filter(Order.user_id == user.id)

        # 状态筛选
        if status:
            query = query.filter(Order.status == status)

        # 按创建时间倒序排列
        query = query.order_by(Order.created_at.desc())

        return sqlalchemy_paginate(query, params=params)

    @staticmethod
    def get_order(db: Session, order_id: str, user) -> dict:
        """
        获取订单详情

        Args:
            db: 数据库会话
            order_id: 订单ID
            user: 当前用户

        Returns:
            订单详情（包含订单项）

        Raises:
            NotFoundError: 订单不存在
        """
        # 查询订单
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError("订单不存在")

        # 普通用户只能查看自己的订单
        if user.role == 'customer' and order.user_id != user.id:
            raise NotFoundError("订单不存在")

        # 查询订单项
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

        # 转换订单项为字典列表
        items_dict = []
        for item in order_items:
            items_dict.append({
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_image": item.product_image,
                "price": item.price,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
                "created_at": item.created_at
            })

        # 转换为字典返回
        return {
            "id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_time": order.payment_time,
            "shipping_address": order.shipping_address,
            "contact_name": order.contact_name,
            "contact_phone": order.contact_phone,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": items_dict
        }

    @staticmethod
    def pay_order(db: Session, order_id: str, payment_method: str, user) -> dict:
        """
        支付订单

        Args:
            db: 数据库会话
            order_id: 订单ID
            payment_method: 支付方式（alipay或wechat）
            user: 当前用户

        Returns:
            支付成功的订单信息

        Raises:
            NotFoundError: 订单不存在
            ValueError: 订单状态不正确
        """
        # 查询订单
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError("订单不存在")

        # 普通用户只能支付自己的订单
        if user.role == 'customer' and order.user_id != user.id:
            raise NotFoundError("订单不存在")

        # 验证订单状态
        if order.status != 'pending':
            raise ValueError("只有待支付的订单才能支付")

        # 更新订单状态和支付信息
        order.status = 'paid'
        order.payment_method = payment_method
        order.payment_time = func.current_timestamp()
        order.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(order)

        # 转换为字典返回
        return {
            "id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_time": order.payment_time,
            "shipping_address": order.shipping_address,
            "contact_name": order.contact_name,
            "contact_phone": order.contact_phone,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }

    @staticmethod
    def update_order_status(db: Session, order_id: str, status: str, user) -> dict:
        """
        更新订单状态

        Args:
            db: 数据库会话
            order_id: 订单ID
            status: 新的订单状态
            user: 当前用户

        Returns:
            更新后的订单信息

        Raises:
            NotFoundError: 订单不存在
            ValueError: 订单状态不合法
        """
        # 查询订单
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError("订单不存在")

        # 验证状态合法性
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded']
        if status not in valid_statuses:
            raise ValueError(f"无效的订单状态: {status}")

        # 更新订单状态
        order.status = status
        order.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(order)

        # 转换为字典返回
        return {
            "id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_time": order.payment_time,
            "shipping_address": order.shipping_address,
            "contact_name": order.contact_name,
            "contact_phone": order.contact_phone,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }

    @staticmethod
    def cancel_order(db: Session, order_id: str, user) -> dict:
        """
        取消订单

        Args:
            db: 数据库会话
            order_id: 订单ID
            user: 当前用户

        Returns:
            取消后的订单信息

        Raises:
            NotFoundError: 订单不存在
            ValueError: 订单状态不正确无法取消
        """
        # 查询订单
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError("订单不存在")

        # 普通用户只能取消自己的订单
        if user.role == 'customer' and order.user_id != user.id:
            raise NotFoundError("订单不存在")

        # 验证订单状态（只有待支付或已支付的订单可以取消）
        if order.status not in ['pending', 'paid']:
            raise ValueError("当前订单状态无法取消")

        # 更新订单状态
        order.status = 'cancelled'
        order.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(order)

        # 转换为字典返回
        return {
            "id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_time": order.payment_time,
            "shipping_address": order.shipping_address,
            "contact_name": order.contact_name,
            "contact_phone": order.contact_phone,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }

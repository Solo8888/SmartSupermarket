# 订单模型
# 定义订单相关的数据库模型
import uuid
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='订单ID')
    order_no = Column(String(50), nullable=False, unique=True, comment='订单编号')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='用户ID')
    total_amount = Column(Numeric(10, 2), nullable=False, comment='订单总金额')
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False, comment='优惠金额')
    final_amount = Column(Numeric(10, 2), nullable=False, comment='实付金额')
    status = Column(Enum('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded'), default='pending', nullable=False, comment='订单状态')
    payment_method = Column(Enum('wechat', 'alipay', 'cash', 'card'), nullable=True, comment='支付方式')
    payment_time = Column(DateTime, nullable=True, comment='支付时间')
    shipping_address = Column(Text, nullable=True, comment='收货地址')
    contact_name = Column(String(50), nullable=True, comment='联系人姓名')
    contact_phone = Column(String(20), nullable=True, comment='联系电话')
    remark = Column(Text, nullable=True, comment='备注')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='订单项ID')
    order_id = Column(CHAR(36), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, comment='订单ID')
    product_id = Column(CHAR(36), ForeignKey('products.id', ondelete='SET NULL'), nullable=True, comment='商品ID')
    product_name = Column(String(100), nullable=False, comment='商品名称')
    product_image = Column(String(255), nullable=True, comment='商品图片')
    price = Column(Numeric(10, 2), nullable=False, comment='商品单价')
    quantity = Column(Integer, nullable=False, comment='购买数量')
    subtotal = Column(Numeric(10, 2), nullable=False, comment='小计')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')

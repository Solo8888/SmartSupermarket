# 数据库连接和ORM配置

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_recycle=3600,  # 连接回收时间（秒）
    pool_timeout=30,  # 连接超时时间（秒）
    echo=False,  # 是否输出SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明式基类（所有ORM模型都应继承此类）
Base = declarative_base()

# 导入模型
from .user import User
from .category import Category
from .product import Product
from .inventory import Inventory
from .promotion import Promotion
from .order import Order, OrderItem
from .store import Store
from .user_store import UserStore
from .member_levels import MemberLevel
from .member import Member
from .coupon import Coupon
from .user_coupon import UserCoupon
from .address_book import AddressBook
from .promotion_product import PromotionProduct
from .promotion_category import PromotionCategory
from .cart import Cart, CartItem
from .review import Review
from .store_product import StoreProduct
from .forecast import Forecast, ForecastAdjustment


def get_db() -> Session:
    """
    数据库会话依赖
    用于FastAPI路由中注入数据库会话

    管理会话生命周期 异常时回滚事务

    Returns:
        数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    应在应用启动时调用
    """
    Base.metadata.create_all(bind=engine)

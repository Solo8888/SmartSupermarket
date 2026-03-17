from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import settings
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from core.exceptions import BusinessException, business_exception_handler, general_exception_handler
from routes import user_router, category_router, product_router, upload_router, inventory_router, promotion_router, order_router, store_router, user_store_router
from models import init_db

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加异常处理中间件
@app.exception_handler(BusinessException)
async def handle_business_exception(request, exc: BusinessException):
    return await business_exception_handler(request, exc)


@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception):
    return await general_exception_handler(request, exc)


# 注册路由
app.include_router(user_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(upload_router)
app.include_router(inventory_router)
app.include_router(promotion_router)
app.include_router(order_router)
app.include_router(store_router)
app.include_router(user_store_router)

# 挂载静态文件目录
import os
os.makedirs('uploads/images', exist_ok=True)
app.mount('/uploads', StaticFiles(directory='uploads'), name='uploads')

add_pagination(app)


# ======应用启动事件======
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的初始化操作"""
    init_db()


# ======健康检查路由======
class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str


@app.get("/health", response_model=HealthCheckResponse)
async def healthcheck() -> HealthCheckResponse:
    """
    健康检查接口

    Returns:
        健康状态
    """
    return HealthCheckResponse(status='ok')

from fastapi import FastAPI
from config import settings
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from core.exceptions import BusinessException, business_exception_handler, general_exception_handler

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
# app.include_router()

# add_pagination(app)


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


# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.debug
    )

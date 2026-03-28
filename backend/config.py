# 配置模块
# 读取.env文件并验证配置参数类型

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类，从.env文件读取配置"""
    app_name: str = Field(default='智能超市', alias='APP_NAME')
    app_version: str = Field(default='1.0.0', alias='APP_VERSION')
    debug: bool = Field(default=False, alias='DEBUG')
    
    # JWT配置
    jwt_secret_key: str = Field(default='smart_supermarket_jwt_secret_key_2025_secure_random_key', alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(default='HS256', alias='JWT_ALGORITHM')
    jwt_expires_minutes: int = Field(default=1440, alias='JWT_EXPIRES_MINUTES')
    
    # 数据库配置
    database_url: str = Field(default='mysql+pymysql://root:Emma19900415@mysql:3306/smart_supermarket', alias='DATABASE_URL')
    
    # 服务端口配置
    port: int = Field(default=5000, alias='PORT')
    
    # 后端穿透地址
    backend_url: str = Field(default='http://localhost:5000', alias='BACKEND_URL')
    
    # 客流数据来源配置
    use_camera: bool = Field(default=False, alias='USE_CAMERA')  # 是否使用摄像头获取客流数据

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'


settings = Settings()

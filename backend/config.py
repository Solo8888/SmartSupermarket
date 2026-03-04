# 配置模块
# 读取.env文件并验证配置参数类型

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类，从.env文件读取配置"""
    app_name: str = Field(default='智能超市', alias='APP_NAME')
    app_version: str = Field(default='1.0.0', alias='APP_VERSION')
    debug: bool = Field(default=False, alias='DEBUG')

    # 服务端口配置
    port: int = Field(default=5000, alias='PORT')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'


settings = Settings()

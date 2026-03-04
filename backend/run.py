# 应用启动文件
# 用于启动FastAPI应用

import uvicorn
from config import settings


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )

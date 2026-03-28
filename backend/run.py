# 应用启动文件
# 用于启动FastAPI应用

import uvicorn
import threading
import time
from config import settings
from core.customer_flow_generator import CustomerFlowGenerator
from core.camera_handler import CameraHandler


def run_customer_flow_generator():
    """持续运行客流数据生成器"""
    while True:
        try:
            # 每小时生成一次数据
            generator = CustomerFlowGenerator()
            generator.run(complete_hours=720)
            print("Customer flow data generated successfully")
            # 等待1小时
            time.sleep(3600)  # 1小时 = 3600秒
        except Exception as e:
            print(f"Error in customer flow generator: {e}")
            # 出错后等待10分钟再尝试
            time.sleep(600)


def run_camera_handler():
    """持续运行摄像头处理器"""
    camera_handler = CameraHandler()
    try:
        camera_handler.run()
    except Exception as e:
        print(f"Error in camera handler: {e}")
        # 出错后等待10分钟再尝试
        time.sleep(600)
        run_camera_handler()


if __name__ == "__main__":
    # 根据配置决定启动哪种数据来源
    if not settings.use_camera:
        # 启动客流数据生成器线程
        generator_thread = threading.Thread(target=run_customer_flow_generator, daemon=True)
        generator_thread.start()
        print("Customer flow generator started in background")
    else:
        # 启动摄像头处理器线程
        camera_thread = threading.Thread(target=run_camera_handler, daemon=True)
        camera_thread.start()
        print("Camera handler started in background")
    
    # 启动FastAPI应用
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )

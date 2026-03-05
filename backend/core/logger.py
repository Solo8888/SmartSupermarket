# 日志配置模块
# 提供统一的日志记录功能

import logging
import os
from config import settings

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 创建日志记录器
logger = logging.getLogger('smart_supermarket')
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 导出日志记录器
__all__ = ['logger']
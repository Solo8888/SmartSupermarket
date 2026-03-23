# 上传服务
# 处理文件上传相关的业务逻辑

import os
import uuid
from fastapi import UploadFile, Request
from datetime import datetime
from config import settings


class UploadService:
    @staticmethod
    async def upload_image(file: UploadFile, request: Request) -> dict:
        """
        上传图片

        Args:
            file: 上传的文件
            request: 请求对象

        Returns:
            上传后的文件信息
        """
        # 创建上传目录
        upload_dir = 'uploads/images'
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # 保存文件
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)

        # 返回完整路径，支持内网穿透
        # 尝试从请求中获取正确的基础URL
        base_url = None
        
        # 检查是否有X-Forwarded-Host头（通常由内网穿透服务设置）
        forwarded_host = request.headers.get('X-Forwarded-Host')
        if forwarded_host:
            # 使用与前端相同的协议和主机
            scheme = request.headers.get('X-Forwarded-Proto', 'http')
            base_url = f"{scheme}://{forwarded_host}"
        
        # 如果没有X-Forwarded-Host头，使用请求的主机
        if not base_url:
            scheme = 'https' if request.url.scheme == 'https' else 'http'
            base_url = f"{scheme}://{request.url.netloc}"
        
        return {
            'url': f"{base_url}/uploads/images/{unique_filename}",
            'filename': unique_filename
        }

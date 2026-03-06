# 上传服务
# 处理文件上传相关的业务逻辑

import os
import uuid
from fastapi import UploadFile
from datetime import datetime


class UploadService:
    @staticmethod
    async def upload_image(file: UploadFile) -> dict:
        """
        上传图片

        Args:
            file: 上传的文件

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

        # 返回文件URL
        return {
            'url': f"/uploads/images/{unique_filename}",
            'filename': unique_filename
        }

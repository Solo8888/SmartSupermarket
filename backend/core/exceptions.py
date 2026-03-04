# 异常处理模块
# 定义业务层异常和全局异常处理
import traceback

from fastapi import status
from fastapi.responses import JSONResponse


class BusinessException(Exception):
    """业务层异常基类"""

    def __init__(self, message: str, error_code: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ServerError(BusinessException):
    """服务器错误异常"""

    def __init__(self, message: str, error_code: str = "SERVER_ERROR"):
        super().__init__(message, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotFoundError(BusinessException):
    """资源不存在异常"""

    def __init__(self, message: str = "资源不存在", error_code: str = "NOT_FOUND"):
        super().__init__(message, error_code)


async def business_exception_handler(request, exc: BusinessException):
    """处理业务层异常 - 400类错误简单打印"""
    print(f'[客户端错误] {exc.error_code}: {exc.message}')
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error_code': exc.error_code,
            'message': exc.message,
        }
    )


async def general_exception_handler(request, exc: Exception):
    """处理未预期异常 - 500类错误打印详细错误栈"""
    print(f'[服务器错误] {type(exc).__name__}: {str(exc)}')
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error_code': 'SERVER_ERROR',
            'message': '服务器内部错误',
        }
    )

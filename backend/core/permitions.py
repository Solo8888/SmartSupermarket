# 权限验证相关工具函数
# 提供统一的用户验证和权限检查依赖注入

from typing import Optional, Callable

from fastapi import Header, Depends
from sqlalchemy.orm import Session

from core.auth import JWTHandler
from core.exceptions import UnauthorizedError, ClientError
from models import User, get_db

# 角色权重级别（用于权限判断）
# system_admin > admin > operations_manager = inventory_manager > customer
ROLE_HIERARCHY = {
    'system_admin': 4,
    'admin': 3,
    'operations_manager': 2,
    'inventory_manager': 2,
    'customer': 1,
}


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """
    从 Authorization header 中提取 token

    Args:
        authorization: Authorization header 的值

    Returns:
        token 字符串，或 None

    Raises:
        UnauthorizedError: header 格式错误
    """
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("无效的认证令牌格式")

    return parts[1]


def require_role(required_role, mode: str = 'gte') -> Callable:
    """
    统一的用户验证和权限检查依赖注入

    Args:
        required_role: 所需的角色，可以是单个角色字符串或角色列表
                      - 'admin'/'operations_manager'/'inventory_manager'/'customer' 等：需要特定角色权限
                      - ['customer', 'operations_manager']: 需要任一角色
        mode: 权限检查方式
             - 'gte': 大于等于（默认），用于层级权限判断（如 merchant 及以上）
             - 'eq': 必须等于，用于特定角色限制（如必须是 agent）
             - 'in': 角色在列表中，用于多角色允许

    Returns:
        异步依赖函数，返回 User 对象

    Example:
        # 任何已登录用户可以访问
        @router.get("/devices")
        async def list_devices(user: User = Depends(require_role('merchant'))):
            return {"devices": "..."}

        # 只有 agent 可以执行此操作
        @router.post("/roles/merchants")
        async def add_merchant(user: User = Depends(require_role('agent', mode='eq'))):
            return {"merchant_id": "..."}
            
        # 多个角色中的任一都可以访问
        @router.get("/orders")
        async def list_orders(user: User = Depends(require_role(['customer', 'operations_manager'], mode='in'))):
            return {"orders": "..."}
    """

    if not required_role:
        raise ValueError("required_role 不能为空")

    async def dependency(
            authorization: Optional[str] = Header(
                None,
                description="JWT认证令牌",
                examples=["Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ..."]
            ),
            db: Session = Depends(get_db)
    ) -> User:
        """内部依赖函数"""

        if not authorization:
            raise UnauthorizedError("缺少认证令牌")

        token = extract_token_from_header(authorization)
        if not token:
            raise UnauthorizedError("无效的认证令牌")

        user_id = JWTHandler.verify_token(token)
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise UnauthorizedError("用户不存在")

        if mode == 'in' and isinstance(required_role, list):
            # 角色在列表中
            if user.role not in required_role:
                raise ClientError(
                    f"此操作仅限{', '.join(required_role)}执行",
                    "PERMISSION_DENIED"
                )
        elif mode == 'eq':
            # 必须等于
            if user.role != required_role:
                raise ClientError(
                    f"此操作仅限{required_role}执行",
                    "PERMISSION_DENIED"
                )
        else:  # mode == 'gte'
            # 大于等于
            user_level = ROLE_HIERARCHY.get(user.role, 0)
            required_level = ROLE_HIERARCHY.get(required_role, 0)
            if user_level < required_level:
                raise ClientError(
                    f"您的权限不足，需要{required_role}及以上权限",
                    "PERMISSION_DENIED"
                )

        return user

    return dependency

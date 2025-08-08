from fastapi import Depends, HTTPException, status
from typing import List, Union
from app.core.database.crud.user import get_user
from app.core.security.security import get_current_user

class RoleChecker:
    def __init__(self, allowed_roles: Union[str, List[str]]):
        if isinstance(allowed_roles, str):
            self.allowed_roles = [allowed_roles]
        else:
            self.allowed_roles = allowed_roles

    def __call__(self, current_user = Depends(get_current_user)):
        
        fresh_user = get_user(current_user['id'])
        if not fresh_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        user_role = fresh_user.get('role', 'user')
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется одна из ролей: {', '.join(self.allowed_roles)}"
            )
        
        return fresh_user

class HierarchicalRoleChecker:
    def __init__(self, minimum_role: str):
        self.role_hierarchy = {
            'user': 1,
            'pro_user': 2,
            'admin': 3
        }
        self.minimum_role = minimum_role
        self.minimum_level = self.role_hierarchy.get(minimum_role, 0)

    def __call__(self, current_user = Depends(get_current_user)):
        
        fresh_user = get_user(current_user['id'])
        if not fresh_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        user_role = fresh_user.get('role', 'user')
        user_level = self.role_hierarchy.get(user_role, 0)
        
        if user_level < self.minimum_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется роль {self.minimum_role} или выше"
            )
        
        return fresh_user

require_admin = RoleChecker('admin')
require_pro = HierarchicalRoleChecker('pro_user')
require_admin_or_pro = RoleChecker(['admin', 'pro_user'])

def require_role(role: str):
    return RoleChecker(role)

def require_minimum_role(role: str):
    return HierarchicalRoleChecker(role)
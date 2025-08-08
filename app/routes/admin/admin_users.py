from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.security.security import get_admin_user
from app.core.database.connector import get_generic_repository
from app.core.database.crud.user import update_user_role

router = APIRouter()

@router.get("/")
async def list_users(limit: Optional[int] = Query(default=50), current_user = Depends(get_admin_user)):
    try:
        repo = get_generic_repository("users")
        items = repo.scan_items("users", limit=limit)
        active_users = [user for user in items if user.get('is_active', True)]
        
        for user in active_users:
            user.pop('hashed_password', None)
            user.pop('access_token', None)
            user.pop('refresh_token', None)
        
        return {
            "total": len(active_users),
            "users": active_users,
            "admin": current_user['email']
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка получения пользователей: {str(e)}"
        )

@router.get("/{user_id}")
async def get_user_by_admin(user_id: str, current_user = Depends(get_admin_user)):
    try:
        repo = get_generic_repository("users")
        user = repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        
        user.pop('hashed_password', None)
        user.pop('access_token', None)
        user.pop('refresh_token', None)
        
        return {"user": user, "admin": current_user['email']}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка получения пользователя: {str(e)}"
        )

@router.put("/{user_id}")
async def update_user_by_admin(user_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    try:
        repo = get_generic_repository("users")
        
        existing_user = repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        
        if 'hashed_password' in updates or 'password' in updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Изменение пароля запрещено через этот эндпоинт"
            )
        
        updates.update({
            'updated_at': datetime.now().isoformat(),
            'updated_by_admin': current_user['id']
        })
        
        updated_user = repo.update_by_id(user_id, updates)
        updated_user.pop('hashed_password', None)
        updated_user.pop('access_token', None)
        updated_user.pop('refresh_token', None)
        
        return {
            "message": "Пользователь обновлен администратором",
            "user": updated_user,
            "admin": current_user['email']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка обновления пользователя: {str(e)}"
        )

@router.put("/{user_id}/role")
async def update_user_role_by_admin(user_id: str, role: str, current_user = Depends(get_admin_user)):
    try:
        valid_roles = ['user', 'pro_user', 'admin']
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Недопустимая роль. Доступные: {', '.join(valid_roles)}"
            )
        
        updated_user = update_user_role(user_id, role)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        
        return {
            "message": f"Роль пользователя изменена на {role}",
            "user_id": user_id,
            "new_role": role,
            "admin": current_user['email']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка изменения роли: {str(e)}"
        )

@router.put("/{user_id}/deactivate")
async def deactivate_user_by_admin(user_id: str, current_user = Depends(get_admin_user)):
    try:
        repo = get_generic_repository("users")
        
        existing_user = repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        
        if user_id == current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Нельзя деактивировать самого себя"
            )
        
        repo.update_by_id(user_id, {
            'is_active': False,
            'deactivated_at': datetime.now().isoformat(),
            'deactivated_by_admin': current_user['id']
        })
        
        return {
            "message": "Пользователь деактивирован",
            "user_id": user_id,
            "admin": current_user['email']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка деактивации пользователя: {str(e)}"
        )

@router.put("/{user_id}/activate")
async def activate_user_by_admin(user_id: str, current_user = Depends(get_admin_user)):
    try:
        repo = get_generic_repository("users")
        
        existing_user = repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        
        repo.update_by_id(user_id, {
            'is_active': True,
            'activated_at': datetime.now().isoformat(),
            'activated_by_admin': current_user['id']
        })
        
        return {
            "message": "Пользователь активирован",
            "user_id": user_id,
            "admin": current_user['email']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка активации пользователя: {str(e)}"
        )
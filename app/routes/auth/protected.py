from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database.crud.user import *
from app.schemas.user import UserResponse, UserUpdate
from app.core.security.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(user_update: UserUpdate, current_user = Depends(get_current_user)):
    updates = {}
    if user_update.name is not None:
        updates['name'] = user_update.name
    if user_update.first_name is not None:
        updates['first_name'] = user_update.first_name
    if user_update.last_name is not None:
        updates['last_name'] = user_update.last_name
    
    if not updates:
        return current_user
    
    updated_user = update_user(current_user['id'], **updates)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка обновления профиля")
    
    return updated_user

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    success = logout_user(current_user['id'])
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при выходе из системы")
    
    return {"message": "Успешный выход из системы", "email": current_user['email']}
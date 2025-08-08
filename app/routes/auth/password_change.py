
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any
import random
import string
from datetime import datetime, timedelta

from app.core.database.crud.user import change_user_password
from app.core.security.security import get_current_user, verify_password
from app.core.security.config import settings
from app.core.database import get_otp_repository
from app.services.auth.email_service import send_otp_email

password_router = APIRouter()

def generate_otp_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

@password_router.post("/change-password/request")
async def request_password_change(email: str = Body(..., embed=True), current_user = Depends(get_current_user)):
    if current_user['email'] != email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    if current_user.get('auth_provider') == 'google':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google пользователи не могут изменять пароль")
    
    try:
        otp_repo = get_otp_repository()
        if not otp_repo:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Сервис OTP недоступен")
        
        otp_repo.delete_old_otps_for_email(email, "password_change")
        
        otp_code = generate_otp_code()
        expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
        
        otp_data = {
            'email': email,
            'otp_code': otp_code,
            'otp_type': 'password_change',
            'expires_at': expires_at,
            'user_id': current_user['id']
        }
        
        otp_repo.create_otp(otp_data)
        
        email_sent = send_otp_email(email, otp_code, "password_change")
        
        if not email_sent:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка отправки OTP")
        
        return {
            "message": "OTP код для смены пароля отправлен на email",
            "email": email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка генерации OTP: {str(e)}")

@password_router.post("/change-password/verify")
async def change_password_with_otp(
    email: str = Body(...),
    otp_code: str = Body(...),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user = Depends(get_current_user)
):
    if current_user['email'] != email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Можно изменить только свой пароль")
    
    if current_user.get('auth_provider') == 'google':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google пользователи не могут изменять пароль")
    
    if len(new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Новый пароль должен содержать минимум 8 символов")
    
    if not verify_password(current_password, current_user['hashed_password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль")
    
    try:
        otp_repo = get_otp_repository()
        if not otp_repo:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Сервис OTP недоступен")
        
        otp_record = otp_repo.get_valid_otp(email, otp_code, "password_change")
        if not otp_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный или истекший OTP код")
        
        if otp_record.get('user_id') != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="OTP код не принадлежит данному пользователю")
        
        otp_repo.mark_otp_as_used(otp_record['id'])
        
        updated_user = change_user_password(current_user['id'], new_password)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка изменения пароля")
        
        return {
            "message": "Пароль успешно изменен",
            "email": email,
            "changed_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка смены пароля: {str(e)}")

@password_router.post("/change-password/resend-otp")
async def resend_password_change_otp(email: str = Body(..., embed=True), current_user = Depends(get_current_user)):
    if current_user['email'] != email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Можно запросить OTP только для своего email")
    
    if current_user.get('auth_provider') == 'google':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google пользователи не могут изменять пароль")
    
    try:
        otp_repo = get_otp_repository()
        if not otp_repo:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Сервис OTP недоступен")
        
        otp_repo.delete_old_otps_for_email(email, "password_change")
        
        otp_code = generate_otp_code()
        expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
        
        otp_data = {
            'email': email,
            'otp_code': otp_code,
            'otp_type': 'password_change',
            'expires_at': expires_at,
            'user_id': current_user['id']
        }
        
        otp_repo.create_otp(otp_data)
        
        email_sent = send_otp_email(email, otp_code, "password_change")
        
        if not email_sent:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка отправки OTP")
        
        return {
            "message": "OTP код повторно отправлен",
            "email": email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка повторной отправки OTP: {str(e)}")

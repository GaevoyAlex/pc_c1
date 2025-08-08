from fastapi import APIRouter, HTTPException, status, Query
from app.core.database.crud.user import get_user_by_email
from app.schemas.user import OTPRequest
from app.services.auth.otp_service import generate_and_send_otp

router = APIRouter()

def _validate_user_and_otp_type(email: str, otp_type: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    
    if otp_type not in ["registration", "login", "password_change"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный тип OTP")
    
    if otp_type == "registration" and user.get('is_verified', False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь уже подтвержден")
    
    if otp_type == "login" and not user.get('is_verified', False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сначала подтвердите регистрацию")
    
    return user

@router.post("/resend")
def resend_otp_post(otp_request: OTPRequest):
    user = _validate_user_and_otp_type(otp_request.email, otp_request.otp_type)
    
    otp_sent = generate_and_send_otp(otp_request.email, otp_request.otp_type)
    if not otp_sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка отправки кода подтверждения")
    
    return {
        "message": f"Код подтверждения для {otp_request.otp_type} отправлен повторно",
        "email": otp_request.email,
        "otp_type": otp_request.otp_type
    }

@router.get("/resend")
def resend_otp_get(
    email: str = Query(..., description="Email пользователя"),
    otp_type: str = Query(..., description="Тип OTP: registration, login или password_change")
):
    user = _validate_user_and_otp_type(email, otp_type)
    
    otp_sent = generate_and_send_otp(email, otp_type)
    if not otp_sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка отправки кода подтверждения")
    
    return {
        "message": f"Код подтверждения для {otp_type} отправлен повторно",
        "email": email,
        "otp_type": otp_type
    }

@router.get("/status/{email}")
def get_otp_status(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    
    available_types = []
    if not user.get('is_verified', False):
        available_types.append("registration")
    if user.get('is_verified', False):
        available_types.extend(["login", "password_change"])
    
    return {
        "email": email,
        "is_verified": user.get('is_verified', False),
        "available_otp_types": available_types,
        "user_status": {
            "created_at": user.get('created_at'),
            "auth_provider": user.get('auth_provider', 'local'),
            "is_active": user.get('is_active', True)
        }
    }
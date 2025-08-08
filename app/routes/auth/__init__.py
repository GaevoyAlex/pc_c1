
from fastapi import APIRouter
from datetime import datetime

from .base import router as base_router
from .otp import router as otp_router
from .oauth import router as oauth_router
from .protected import router as protected_router

router = APIRouter()

router.include_router(base_router, tags=["Base Auth"])
router.include_router(otp_router, prefix="/otp", tags=["OTP Management"])
router.include_router(oauth_router, prefix="/oauth", tags=["OAuth"])
router.include_router(protected_router, tags=["Protected"])


@router.get("/status")
async def auth_system_status():

    from app.core.security.config import settings
    from app.services.auth.email_service import test_email_config
    
    try:
        email_config = test_email_config()
        
        return {
            "system": "FastAPI Authentication System",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "modules": {
                "base_auth": {
                    "enabled": True,
                    "endpoints": ["/register", "/verify-registration", "/login", "/verify-login"]
                },
                "otp": {
                    "enabled": True,
                    "expire_minutes": settings.OTP_EXPIRE_MINUTES,
                    "endpoints": ["/otp/resend", "/otp/status", "/otp/cleanup"]
                },
                "oauth": {
                    "enabled": bool(settings.GOOGLE_CLIENT_ID),
                    "providers": ["google"] if settings.GOOGLE_CLIENT_ID else [],
                    "endpoints": ["/oauth/google/login", "/oauth/google/auth"]
                },
                "protected": {
                    "enabled": True,
                    "jwt_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                    "endpoints": ["/me", "/logout", "/sessions"]
                }
            },
            "configuration": {
                "email_configured": email_config.get("smtp_configured", False),
                "google_oauth_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
                "jwt_algorithm": settings.ALGORITHM
            },
            "features": {
                "two_factor_auth": True,
                "email_verification": True,
                "oauth_login": bool(settings.GOOGLE_CLIENT_ID),
                "password_reset": False,  # TODO: implement
                "session_management": True
            }
        }
    except Exception as e:
        return {
            "system": "FastAPI Authentication System",
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/health")
async def auth_health_check():
    try:
        from app.core.security.config import settings
        
        checks = {
            "config_loaded": bool(settings.SECRET_KEY),
            "jwt_configured": bool(settings.SECRET_KEY and settings.ALGORITHM),
            "otp_configured": settings.OTP_EXPIRE_MINUTES > 0,
        }
        
        all_healthy = all(checks.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/endpoints")
async def list_auth_endpoints():

    return {
        "base_authentication": {
            "registration": {
                "POST /auth/register": "Регистрация нового пользователя",
                "POST /auth/verify-registration": "Подтверждение регистрации по OTP"
            },
            "login": {
                "POST /auth/login": "Инициация входа (отправка OTP)",
                "POST /auth/verify-login": "Подтверждение входа по OTP"
            }
        },
        "otp_management": {
            "POST /auth/otp/resend": "Повторная отправка OTP (универсальный)",
            "GET /auth/otp/resend": "Повторная отправка OTP (GET с параметрами)",
            "POST /auth/otp/resend-registration": "Повтор OTP для регистрации",
            "POST /auth/otp/resend-login": "Повтор OTP для входа",
            "GET /auth/otp/status/{email}": "Статус OTP для пользователя",
            "DELETE /auth/otp/cleanup": "Очистка истекших OTP"
        },
        "oauth": {
            "GET /auth/oauth/google/login": "Вход через Google (redirect)",
            "GET /auth/oauth/google/callback": "Google OAuth callback",
            "POST /auth/oauth/google/auth": "Google аутентификация для API",
            "GET /auth/oauth/google/status": "Статус Google OAuth"
        },
        "protected": {
            "GET /auth/me": "Информация о текущем пользователе",
            "PUT /auth/me": "Обновление профиля",
            "POST /auth/logout": "Выход из системы",
            "POST /auth/me/change-password": "Изменение пароля",
            "GET /auth/me/stats": "Статистика аккаунта"
        },
        "system": {
            "GET /auth/status": "Статус системы аутентификации",
            "GET /auth/health": "Проверка здоровья",
            "GET /auth/endpoints": "Список эндпоинтов (этот)"
        }
    }


@router.get("/metrics")
async def auth_metrics():
    """
    Базовые метрики системы аутентификации
    В продакшене здесь можно добавить реальную статистику
    """
    return {
        "system_info": {
            "uptime": "N/A (stateless JWT)",
            "total_endpoints": 20,
            "authentication_methods": ["email/password + OTP", "Google OAuth"]
        },
        "configuration": {
            "jwt_expire_minutes": "from settings",
            "otp_expire_minutes": "from settings", 
            "oauth_providers": ["google"]
        },
        "note": "Для детальных метрик пользователей нужна интеграция с аналитикой"
    }
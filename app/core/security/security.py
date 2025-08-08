

from app.core.security.config import settings
from datetime import datetime, timedelta
from typing import Any, Union, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type_payload: str = payload.get("type")
        
        if user_id is None or token_type_payload != token_type:
            return None
        return user_id
    except JWTError as e:
        print(f"Ошибка проверки JWT токена: {e}")
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(credentials.credentials, "access")
    if user_id is None:
        raise credentials_exception
    
    from app.core.database.crud.user import get_user
    
    user = get_user(user_id)
    if user is None:
        print(f"Пользователь с ID {user_id} не найден в DynamoDB")
        raise credentials_exception
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    if not credentials:
        return None
    
    user_id = verify_token(credentials.credentials, "access")
    if user_id is None:
        return None
    
    from app.core.database.crud.user import get_user
    
    user = get_user(user_id)
    if user is None or not user.get('is_active', True):
        return None
    
    return user

async def get_admin_user(current_user = Depends(get_current_user)):
    from app.core.database.crud.user import get_user
    
    fresh_user = get_user(current_user['id'])
    if not fresh_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    if fresh_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    return fresh_user

async def get_pro_user(current_user = Depends(get_current_user)):
    from app.core.database.crud.user import get_user
    
    fresh_user = get_user(current_user['id'])
    if not fresh_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    user_role = fresh_user.get('role', 'user')
    if user_role not in ['pro_user', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется Pro или Admin подписка"
        )
    return fresh_user

async def check_user_role(required_role: str, current_user = Depends(get_current_user)):

    from app.core.database.crud.user import get_user
    
    fresh_user = get_user(current_user['id'])
    if not fresh_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    user_role = fresh_user.get('role', 'user')
    
    role_hierarchy = {
        'user': 1,
        'pro_user': 2, 
        'admin': 3
    }
    
    required_level = role_hierarchy.get(required_role, 0)
    user_level = role_hierarchy.get(user_role, 0)
    
    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Требуется роль {required_role} или выше"
        )
    
    return fresh_user
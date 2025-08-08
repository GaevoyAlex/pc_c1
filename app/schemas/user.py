from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool
    is_active: bool
    auth_provider: str
    role: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'pro_user', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'Роль должна быть одной из: {", ".join(allowed_roles)}')
        return v

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    code: Optional[str] = None

class OTPVerification(BaseModel):
    email: EmailStr
    otp_code: str

class OTPRequest(BaseModel):
    email: EmailStr
    otp_type: str

class RegistrationResponse(BaseModel):
    message: str
    email: str
    requires_verification: bool

class LoginResponse(BaseModel):
    message: str
    email: str
    requires_otp: bool

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserStats(BaseModel):
    user_info: dict
    account_stats: dict
    security_info: dict

class RoleInfo(BaseModel):
    current_role: str
    available_roles: list
    role_permissions: dict
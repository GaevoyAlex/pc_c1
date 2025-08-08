import os
from dynaconf import Dynaconf

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

print(f"[DEBUG] Current dir: {current_dir}")
print(f"[DEBUG] Project root: {project_root}")
print(f"[DEBUG] Looking for config files in: {project_root}")

settings_path = os.path.join(project_root, 'settings.toml')
secrets_path = os.path.join(project_root, '.secrets.toml')

print(f"[DEBUG] Settings file exists: {os.path.exists(settings_path)}")
print(f"[DEBUG] Secrets file exists: {os.path.exists(secrets_path)}")

_dynaconf = Dynaconf(
    settings_files=[settings_path, secrets_path],
    environments=False,
    load_dotenv=False,
)

class Settings:
    @property
    def PROJECT_NAME(self) -> str:
        return _dynaconf.get("project_name", "FastAPI Auth App")
    
    @property
    def SECRET_KEY(self) -> str:
        return _dynaconf.get("secret_key", "")
    
    @property
    def ALGORITHM(self) -> str:
        return _dynaconf.get("algorithm", "HS256")
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return _dynaconf.get("access_token_expire_minutes", 30)
    
    @property
    def AWS_REGION(self) -> str:
        return _dynaconf.get("aws_region", "")
    
    @property
    def AWS_ACCESS_KEY_ID(self) -> str:
        return _dynaconf.get("aws_access_key_id", "")
    
    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str:
        return _dynaconf.get("aws_secret_access_key", "")
    
    @property
    def AWS_ENDPOINT_URL(self) -> str:
        return _dynaconf.get("aws_endpoint_url", "")
    
    @property
    def DYNAMODB_USERS_TABLE(self) -> str:
        return _dynaconf.get("dynamodb_users_table", "")
    
    @property
    def DYNAMODB_OTP_TABLE(self) -> str:
        return _dynaconf.get("dynamodb_otp_table", "")
    
    @property
    def GOOGLE_CLIENT_ID(self) -> str:
        return _dynaconf.get("google_client_id", "")
    
    @property
    def GOOGLE_CLIENT_SECRET(self) -> str:
        return _dynaconf.get("google_client_secret", "")
    
    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        return _dynaconf.get("google_redirect_uri", "")
    
    @property
    def OTP_EXPIRE_MINUTES(self) -> int:
        return _dynaconf.get("otp_expire_minutes", 10)
    
    @property
    def SMTP_HOST(self) -> str:
        return _dynaconf.get("smtp_host", "smtp.gmail.com")
    
    @property
    def SMTP_PORT(self) -> int:
        return _dynaconf.get("smtp_port", 587)
    
    @property
    def SMTP_TLS(self) -> bool:
        return _dynaconf.get("smtp_tls", True)
    
    @property
    def SMTP_USER(self) -> str:
        return _dynaconf.get("smtp_user", "")
    
    @property
    def SMTP_PASSWORD(self) -> str:
        return _dynaconf.get("smtp_password", "")
    
    @property
    def COINGECKO_API_KEY(self) -> str:
        return _dynaconf.get("coingecko_api_key", "")
    
    @property
    def COINGECKO_PRO_ENABLED(self) -> bool:
        return _dynaconf.get("coingecko_pro_enabled", False)
    
    @property
    def DEVELOPMENT_MODE(self) -> bool:
        return _dynaconf.get("development_mode", True)
    
    @property
    def USE_LOCALSTACK(self) -> bool:
        return _dynaconf.get("use_localstack", False)
    
    @property
    def is_localstack(self) -> bool:
        return bool(self.AWS_ENDPOINT_URL and "localhost" in self.AWS_ENDPOINT_URL)

settings = Settings()

print(f"[DEBUG] AWS_REGION loaded: {settings.AWS_REGION}")
print(f"[DEBUG] DYNAMODB_USERS_TABLE loaded: {settings.DYNAMODB_USERS_TABLE}")
print(f"[DEBUG] SECRET_KEY loaded: {'Yes' if settings.SECRET_KEY else 'No'}")
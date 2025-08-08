from typing import Dict, Any, Optional

from app.core.database.repositories.otp import OTPRepository
from .base import BaseDynamoDBConnector
from .repositories.user import UserRepository
from .repositories.generic import GenericRepository

class DynamoDBConnector(BaseDynamoDBConnector):
    def __init__(self):
        super().__init__()
        self.users: Optional[UserRepository] = None
        self.otp: Optional[OTPRepository] = None
        self._generic_repositories: Dict[str, GenericRepository] = {}
    
    def initiate_connection(self) -> 'DynamoDBConnector':
        if self._initialized:
            return self
        
        self._init_clients()
        self._init_repositories()
        self._initialized = True
        return self
    
    def _init_repositories(self):
        from app.core.security.config import settings
        
        try:
            self.users = UserRepository(settings.DYNAMODB_USERS_TABLE)
            self.users._init_clients()
            self.users._initialized = True
            
            self.otp = OTPRepository(settings.DYNAMODB_OTP_TABLE)
            self.otp._init_clients()
            self.otp._initialized = True
            
            print("[INFO][DynamoDB] - Репозитории инициализированы")
            
        except Exception as e:
            print(f"[ERROR][DynamoDB] - Ошибка инициализации репозиториев: {e}")
    
    def get_repository(self, table_name: str) -> GenericRepository:
        if table_name not in self._generic_repositories:
            repo = GenericRepository(table_name)
            repo._init_clients()
            repo._initialized = True
            self._generic_repositories[table_name] = repo
            print(f"[INFO][DynamoDB] - Создан репозиторий для: {table_name}")
        
        return self._generic_repositories[table_name]
    
    def get_system_info(self) -> Dict[str, Any]:
        try:
            all_tables = list(self.dynamodb.tables.all())
            table_names = [table.name for table in all_tables]
            
            repo_info = {
                'users': bool(self.users),
                'otp': bool(self.otp),
                'generic_repositories': list(self._generic_repositories.keys())
            }
            
            return {
                'status': 'connected',
                'initialized': self._initialized,
                'total_tables': len(table_names),
                'table_names': table_names,
                'repositories': repo_info,
                'cached_tables': len(self._tables)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'initialized': self._initialized
            }
    
    def cleanup_all_expired_data(self) -> Dict[str, int]:
        results = {}
        if self.otp:
            results['otp_codes'] = self.otp.cleanup_expired_otps()
        return results

connector = DynamoDBConnector()

def get_db_connector() -> DynamoDBConnector:
    if not connector._initialized:
        try:
            connector.initiate_connection()
            print("[INFO][DynamoDB] - Коннектор инициализирован")
        except Exception as e:
            print(f"[ERROR][DynamoDB] - Критическая ошибка инициализации: {e}")
            return None
    return connector

def get_user_repository() -> UserRepository:
    conn = get_db_connector()
    return conn.users if conn else None

def get_otp_repository() -> OTPRepository:
    conn = get_db_connector()
    return conn.otp if conn else None

def get_generic_repository(table_name: str) -> GenericRepository:
    conn = get_db_connector()
    return conn.get_repository(table_name) if conn else None
from typing import Dict, Any, Optional, List
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import uuid

from ..base import BaseDynamoDBConnector

class UserRepository(BaseDynamoDBConnector):
    def __init__(self, table_name: str = "users"):
        super().__init__()
        self.table_name = table_name
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_data['id'] = str(uuid.uuid4())
        
        defaults = {
            'is_verified': False,
            'is_active': True,
            'auth_provider': 'local',
            'role': 'user',
            'access_token': '',
            'refresh_token': '',
            'access_token_expires_at': '',
            'refresh_token_expires_at': ''
        }
        
        for key, value in defaults.items():
            user_data.setdefault(key, value)
        
        return self.create_item(self.table_name, user_data)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.get_item(self.table_name, {'id': user_id})
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        items = self.query_items(
            self.table_name,
            key_condition=Key('email').eq(email),
            index_name='email-index'
        )
        return items[0] if items else None
    
    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        items = self.query_items(
            self.table_name,
            key_condition=Key('name').eq(name),
            index_name='name-index'
        )
        return items[0] if items else None
    
    def get_user_by_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        items = self.scan_items(
            self.table_name,
            filter_expression=Attr('refresh_token').eq(refresh_token)
        )
        return items[0] if items else None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.update_item(self.table_name, {'id': user_id}, updates)
    
    def update_tokens(self, user_id: str, access_token: str, refresh_token: str, 
                     access_expires: datetime, refresh_expires: datetime) -> Optional[Dict[str, Any]]:
        updates = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expires_at': access_expires.isoformat(),
            'refresh_token_expires_at': refresh_expires.isoformat()
        }
        return self.update_user(user_id, updates)
    
    def clear_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        updates = {
            'access_token': '',
            'refresh_token': '',
            'access_token_expires_at': '',
            'refresh_token_expires_at': ''
        }
        return self.update_user(user_id, updates)
    
    def verify_user_email(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.update_user(user_id, {'is_verified': True})
    
    def deactivate_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.update_user(user_id, {'is_active': False})
    
    def activate_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.update_user(user_id, {'is_active': True})
    
    def update_user_role(self, user_id: str, role: str) -> Optional[Dict[str, Any]]:
        valid_roles = ['user', 'pro_user', 'admin']
        if role not in valid_roles:
            raise ValueError(f"Недопустимая роль: {role}")
        return self.update_user(user_id, {'role': role})
    
    def get_users_by_provider(self, auth_provider: str) -> List[Dict[str, Any]]:
        return self.scan_items(
            self.table_name,
            filter_expression=Attr('auth_provider').eq(auth_provider)
        )
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        return self.scan_items(
            self.table_name,
            filter_expression=Attr('is_active').eq(True)
        )
    
    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        return self.scan_items(
            self.table_name,
            filter_expression=Attr('role').eq(role)
        )
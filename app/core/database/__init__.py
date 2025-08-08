from .base import BaseDynamoDBConnector
from .repositories.user import UserRepository
from .repositories.otp import OTPRepository
from .repositories.generic import GenericRepository

def get_db_connector():
    from .connector import get_db_connector as _get_db_connector
    return _get_db_connector()

def get_user_repository():
    from .connector import get_user_repository as _get_user_repository
    return _get_user_repository()

def get_otp_repository():
    from .connector import get_otp_repository as _get_otp_repository
    return _get_otp_repository()

def get_generic_repository(table_name: str):
    from .connector import get_generic_repository as _get_generic_repository
    return _get_generic_repository(table_name)

def get_connector():
    from .connector import connector
    return connector

connector = property(lambda self: get_connector())

__all__ = [
    'BaseDynamoDBConnector',
    
    'UserRepository',
    'OTPRepository', 
    'GenericRepository',
    
    'get_db_connector',
    'get_user_repository',
    'get_otp_repository',
    'get_generic_repository',
    'get_connector'
]
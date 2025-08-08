from typing import Dict, Any, Optional, List
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import uuid

from ..base import BaseDynamoDBConnector

class OTPRepository(BaseDynamoDBConnector):
    def __init__(self, table_name: str = "otp_codes"):
        super().__init__()
        self.table_name = table_name
    
    def create_otp(self, otp_data: Dict[str, Any]) -> Dict[str, Any]:
        otp_data['id'] = str(uuid.uuid4())
        otp_data.setdefault('is_used', False)
        return self.create_item(self.table_name, otp_data)
    
    def get_otp_by_id(self, otp_id: str) -> Optional[Dict[str, Any]]:
        return self.get_item(self.table_name, {'id': otp_id})
    
    def get_valid_otp(self, email: str, otp_code: str, otp_type: str) -> Optional[Dict[str, Any]]:
        current_time = datetime.utcnow().isoformat()
        
        items = self.query_items(
            self.table_name,
            key_condition=Key('email').eq(email),
            index_name='email-index',
            filter_expression=(
                Attr('otp_code').eq(otp_code) & 
                Attr('otp_type').eq(otp_type) & 
                Attr('is_used').eq(False) & 
                Attr('expires_at').gt(current_time)
            )
        )
        return items[0] if items else None
    
    def mark_otp_as_used(self, otp_id: str) -> bool:
        updated_item = self.update_item(
            self.table_name,
            key={'id': otp_id},
            updates={'is_used': True}
        )
        return updated_item is not None
    
    def get_otps_by_email(self, email: str, otp_type: str = None) -> List[Dict[str, Any]]:
        filter_expr = None
        if otp_type:
            filter_expr = Attr('otp_type').eq(otp_type)
        
        return self.query_items(
            self.table_name,
            key_condition=Key('email').eq(email),
            index_name='email-index',
            filter_expression=filter_expr
        )
    
    def delete_old_otps_for_email(self, email: str, otp_type: str) -> int:
        items = self.get_otps_by_email(email, otp_type)
        
        deleted_count = 0
        for item in items:
            if self.delete_item(self.table_name, {'id': item['id']}):
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"[INFO][OTP] - Удалено {deleted_count} старых OTP для {email}")
        
        return deleted_count
    
    def cleanup_expired_otps(self) -> int:
        current_time = datetime.utcnow().isoformat()
        
        expired_items = self.scan_items(
            self.table_name,
            filter_expression=Attr('expires_at').lt(current_time)
        )
        
        deleted_count = 0
        for item in expired_items:
            if self.delete_item(self.table_name, {'id': item['id']}):
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"[INFO][OTP] - Удалено {deleted_count} истекших OTP кодов")
        
        return deleted_count
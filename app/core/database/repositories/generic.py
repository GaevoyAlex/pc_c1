from typing import Dict, Any, Optional, List
from boto3.dynamodb.conditions import Key, Attr
import uuid
from datetime import datetime

from ..base import BaseDynamoDBConnector

class GenericRepository(BaseDynamoDBConnector):
    def __init__(self, table_name: str):
        super().__init__()
        self.table_name = table_name
    
    def create(self, data: Dict[str, Any], auto_id: bool = True) -> Dict[str, Any]:
        if auto_id and 'id' not in data:
            data['id'] = str(uuid.uuid4())
        return self.create_item(self.table_name, data)
    
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self.get_item(self.table_name, {'id': item_id})
    
    def update_by_id(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.update_item(self.table_name, {'id': item_id}, updates)
    
    def delete_by_id(self, item_id: str) -> bool:
        return self.delete_item(self.table_name, {'id': item_id})
    
    def list_all(self, limit: int = None) -> List[Dict[str, Any]]:
        return self.scan_items(self.table_name, limit=limit)
    
    def find_by_field(self, field_name: str, field_value: Any, 
                     index_name: str = None) -> List[Dict[str, Any]]:
        if index_name:
            return self.query_items(
                self.table_name,
                key_condition=Key(field_name).eq(field_value),
                index_name=index_name
            )
        else:
            return self.scan_items(
                self.table_name,
                filter_expression=Attr(field_name).eq(field_value)
            )
    
    def find_by_multiple_fields(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        filter_expressions = [Attr(field).eq(value) for field, value in filters.items()]
        combined_filter = filter_expressions[0]
        for expr in filter_expressions[1:]:
            combined_filter = combined_filter & expr
        
        return self.scan_items(self.table_name, filter_expression=combined_filter)
    
    def count_total(self) -> int:
        response = self.get_table(self.table_name).scan(Select='COUNT')
        return response.get('Count', 0)
    
    def get_stats(self) -> Dict[str, Any]:
        items = self.scan_items(self.table_name)
        
        if not items:
            return {
                'total_items': 0,
                'table_name': self.table_name,
                'created_at': datetime.utcnow().isoformat()
            }
        
        field_counts = {}
        for item in items:
            for field in item.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
        
        oldest_item = min(items, key=lambda x: x.get('created_at', ''), default={})
        newest_item = max(items, key=lambda x: x.get('created_at', ''), default={})
        
        return {
            'table_name': self.table_name,
            'total_items': len(items),
            'fields': list(field_counts.keys()),
            'oldest_record': oldest_item.get('created_at'),
            'newest_record': newest_item.get('created_at'),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def bulk_create(self, items: List[Dict[str, Any]], auto_id: bool = True) -> bool:
        if auto_id:
            for item in items:
                if 'id' not in item:
                    item['id'] = str(uuid.uuid4())
        
        try:
            batch_size = 25
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                table = self.get_table(self.table_name)
                
                with table.batch_writer() as batch_writer:
                    for item in batch:
                        if 'created_at' not in item:
                            item['created_at'] = datetime.utcnow().isoformat()
                        if 'updated_at' not in item:
                            item['updated_at'] = datetime.utcnow().isoformat()
                        batch_writer.put_item(Item=item)
            return True
        except Exception as e:
            print(f"[ERROR][DynamoDB] - Ошибка bulk_create в {self.table_name}: {e}")
            return False
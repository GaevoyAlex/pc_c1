import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.security.config import settings

class BaseDynamoDBConnector:
    def __init__(self):
        self.client = None
        self.dynamodb = None
        self._initialized = False
        self._tables = {}
    
    def _init_clients(self):
        try:
            self.client = boto3.client(
                'dynamodb',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            self._test_connection()
            
        except Exception as e:
            print(f"[ERROR][DynamoDB] - Ошибка инициализации: {e}")
            raise e
    
    def _test_connection(self):
        try:
            list(self.dynamodb.tables.all())
        except Exception as e:
            print(f"[ERROR][DynamoDB] - Тест подключения: {e}")
            raise e
    
    def get_table(self, table_name: str):
        if table_name not in self._tables:
            self._tables[table_name] = self.dynamodb.Table(table_name)
        return self._tables[table_name]
    
    def table_exists(self, table_name: str) -> bool:
        try:
            self.client.describe_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            raise e
    
    def create_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if 'created_at' not in item:
                item['created_at'] = datetime.utcnow().isoformat()
            if 'updated_at' not in item:
                item['updated_at'] = datetime.utcnow().isoformat()
            
            table = self.get_table(table_name)
            table.put_item(Item=item)
            return item
            
        except ClientError as e:
            print(f"[ERROR][DynamoDB] - Ошибка создания в {table_name}: {e}")
            raise e
    
    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            table = self.get_table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            print(f"[ERROR][DynamoDB] - Ошибка получения из {table_name}: {e}")
            return None
    
    def update_item(self, table_name: str, key: Dict[str, Any], 
                   updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            update_expression = "SET "
            expression_values = {}
            
            for field, value in updates.items():
                update_expression += f"{field} = :{field}, "
                expression_values[f":{field}"] = value
            
            update_expression = update_expression.rstrip(", ")
            
            table = self.get_table(table_name)
            response = table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return response.get('Attributes')
            
        except ClientError as e:
            print(f"[ERROR][DynamoDB] - Ошибка обновления в {table_name}: {e}")
            return None
    
    def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        try:
            table = self.get_table(table_name)
            table.delete_item(Key=key)
            return True
        except ClientError as e:
            print(f"[ERROR][DynamoDB] - Ошибка удаления из {table_name}: {e}")
            return False
    
    def query_items(self, table_name: str, key_condition: Any, 
                   index_name: str = None, filter_expression: Any = None, 
                   limit: int = None) -> List[Dict[str, Any]]:
        try:
            table = self.get_table(table_name)
            
            query_params = {'KeyConditionExpression': key_condition}
            
            if index_name:
                query_params['IndexName'] = index_name
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            if limit:
                query_params['Limit'] = limit
            
            response = table.query(**query_params)
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"[ERROR][DynamoDB] - Ошибка запроса к {table_name}: {e}")
            return []
    
    def scan_items(self, table_name: str, filter_expression: Any = None, 
                  limit: int = None) -> List[Dict[str, Any]]:
        try:
            table = self.get_table(table_name)
            
            scan_params = {}
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            if limit:
                scan_params['Limit'] = limit
            
            response = table.scan(**scan_params)
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"[ERROR][DynamoDB] - Ошибка сканирования {table_name}: {e}")
            return []
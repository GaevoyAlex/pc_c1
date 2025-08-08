from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
from uuid import UUID
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from core.database.repositories.exchange import BaseRepository
from app.models.market import Token, TokenStats


class TokenRepository(BaseRepository):
    def __init__(self, table_name: str = "tokens"):
        super().__init__(table_name)
    
    async def create_token(self, token_data: Dict[str, Any]) -> Optional[Token]:
        try:
            token = Token(**token_data)
            item = token.model_dump()
            
            for key, value in item.items():
                if isinstance(value, UUID):
                    item[key] = str(value)
                elif isinstance(value, list) and value and isinstance(value[0], UUID):
                    item[key] = [str(v) for v in value]
            
            response = self.table.put_item(Item=item)
            return token
        except Exception as e:
            print(f"[ERROR][TokenRepository] - Ошибка создания токена: {e}")
            return None
    
    async def get_token_by_id(self, token_id: str) -> Optional[Token]:

        try:
            response = self.table.get_item(Key={'id': token_id})
            if 'Item' in response:
                return Token(**response['Item'])
            return None
        except Exception as e:
            print(f"[ERROR][TokenRepository] - Ошибка получения токена {token_id}: {e}")
            return None
    
    async def get_token_by_coingecko_id(self, coingecko_id: str) -> Optional[Token]:
        try:
            response = self.table.scan(
                FilterExpression=Attr('coingecko_id').eq(coingecko_id) & Attr('is_deleted').eq(False)
            )
            if response['Items']:
                return Token(**response['Items'][0])
            return None
        except Exception as e:
            print(f"[ERROR][TokenRepository] - Ошибка получения токена по coingecko_id {coingecko_id}: {e}")
            return None
    
    async def get_tokens_list(self, 
                            page: int = 1, 
                            limit: int = 100, 
                            sort_by: Optional[str] = None) -> Dict[str, Any]:
        try:
            offset = (page - 1) * limit
            
            scan_kwargs = {
                'FilterExpression': Attr('is_deleted').eq(False),
                'Limit': limit + offset  
            }
            
            response = self.table.scan(**scan_kwargs)
            items = response['Items'][offset:offset + limit] if len(response['Items']) > offset else []
            
            count_response = self.table.scan(
                FilterExpression=Attr('is_deleted').eq(False),
                Select='COUNT'
            )
            total_items = count_response['Count']
            
            tokens = [Token(**item) for item in items]
            
            return {
                'data': tokens,
                'pagination': {
                    'current_page': page,
                    'total_pages': (total_items + limit - 1) // limit,
                    'total_items': total_items,
                    'items_per_page': limit
                }
            }
        except Exception as e:
            print(f"[ERROR][TokenRepository] - Ошибка получения списка токенов: {e}")
            return {'data': [], 'pagination': {}}
    
    async def update_token(self, token_id: str, update_data: Dict[str, Any]) -> Optional[Token]:
        try:
            update_expression = "SET "
            expression_values = {}
            
            for key, value in update_data.items():
                if key != 'id':  
                    update_expression += f"{key} = :{key}, "
                    expression_values[f":{key}"] = value
            
            update_expression = update_expression.rstrip(', ')
            
            response = self.table.update_item(
                Key={'id': token_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return Token(**response['Attributes'])
        except Exception as e:
            print(f"[ERROR][TokenRepository] - Ошибка обновления токена {token_id}: {e}")
            return None
    
    async def delete_token(self, token_id: str) -> bool:
        try:
            response = self.table.update_item(
                Key={'id': token_id},
                UpdateExpression='SET is_deleted = :deleted',
                ExpressionAttributeValues={':deleted': True},
                ReturnValues='UPDATED_NEW'
            )
            return True
        except Exception as e:
            print(f"[ERROR][TokenRepository] - Ошибка удаления токена {token_id}: {e}")
            return False


class TokenStatsRepository(BaseRepository):
    def __init__(self, table_name: str = "token_stats"):
        super().__init__(table_name)
    
    async def create_token_stats(self, stats_data: Dict[str, Any]) -> Optional[TokenStats]:
        try:
            stats = TokenStats(**stats_data)
            item = stats.model_dump()
            
            for key, value in item.items():
                if isinstance(value, UUID):
                    item[key] = str(value)
            
            response = self.table.put_item(Item=item)
            return stats
        except Exception as e:
            print(f"[ERROR][TokenStatsRepository] - Ошибка создания статистики: {e}")
            return None
    
    async def get_stats_by_symbol(self, symbol: str) -> Optional[TokenStats]:
        try:
            response = self.table.scan(
                FilterExpression=Attr('symbol').eq(symbol) & Attr('is_deleted').eq(False)
            )
            if response['Items']:
                return TokenStats(**response['Items'][0])
            return None
        except Exception as e:
            print(f"[ERROR][TokenStatsRepository] - Ошибка получения статистики для {symbol}: {e}")
            return None
    
    async def get_stats_by_coingecko_id(self, coingecko_id: str) -> Optional[TokenStats]:
        try:
            response = self.table.scan(
                FilterExpression=Attr('coingecko_id').eq(coingecko_id) & Attr('is_deleted').eq(False)
            )
            if response['Items']:
                return TokenStats(**response['Items'][0])
            return None
        except Exception as e:
            print(f"[ERROR][TokenStatsRepository] - Ошибка получения статистики по coingecko_id {coingecko_id}: {e}")
            return None
    
    async def get_all_token_stats(self, 
                                page: int = 1, 
                                limit: int = 100,
                                sort_by: Optional[str] = None) -> Dict[str, Any]:
        try:
            offset = (page - 1) * limit
            
            scan_kwargs = {
                'FilterExpression': Attr('is_deleted').eq(False),
                'Limit': limit + offset
            }
            
            response = self.table.scan(**scan_kwargs)
            items = response['Items'][offset:offset + limit] if len(response['Items']) > offset else []
            
            count_response = self.table.scan(
                FilterExpression=Attr('is_deleted').eq(False),
                Select='COUNT'
            )
            total_items = count_response['Count']
            
            token_stats = [TokenStats(**item) for item in items]
            
            return {
                'data': token_stats,
                'pagination': {
                    'current_page': page,
                    'total_pages': (total_items + limit - 1) // limit,
                    'total_items': total_items,
                    'items_per_page': limit
                }
            }
        except Exception as e:
            print(f"[ERROR][TokenStatsRepository] - Ошибка получения всех статистик: {e}")
            return {'data': [], 'pagination': {}}
    
    async def update_token_stats(self, stats_id: str, update_data: Dict[str, Any]) -> Optional[TokenStats]:
        try:
            update_expression = "SET "
            expression_values = {}
            
            for key, value in update_data.items():
                if key != 'id':
                    update_expression += f"{key} = :{key}, "
                    expression_values[f":{key}"] = value
            
            update_expression = update_expression.rstrip(', ')
            
            response = self.table.update_item(
                Key={'id': stats_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return TokenStats(**response['Attributes'])
        except Exception as e:
            print(f"[ERROR][TokenStatsRepository] - Ошибка обновления статистики {stats_id}: {e}")
            return None
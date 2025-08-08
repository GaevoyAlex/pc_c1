from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
from uuid import UUID
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from core.database.repositories.exchange import BaseRepository
from app.models.market import Exchange, ExchangesStats


class ExchangeRepository(BaseRepository):
    def __init__(self, table_name: str = "exchanges"):
        super().__init__(table_name)
    
    async def create_exchange(self, exchange_data: Dict[str, Any]) -> Optional[Exchange]:

        try:
            exchange = Exchange(**exchange_data)
            item = exchange.model_dump()
            
            for key, value in item.items():
                if isinstance(value, UUID):
                    item[key] = str(value)
                elif isinstance(value, list) and value and isinstance(value[0], UUID):
                    item[key] = [str(v) for v in value]
            
            response = self.table.put_item(Item=item)
            return exchange
        except Exception as e:
            print(f"[ERROR][ExchangeRepository] - Ошибка создания биржи: {e}")
            return None
    
    async def get_exchange_by_id(self, exchange_id: str) -> Optional[Exchange]:

        try:
            response = self.table.get_item(Key={'id': exchange_id})
            if 'Item' in response:
                return Exchange(**response['Item'])
            return None
        except Exception as e:
            print(f"[ERROR][ExchangeRepository] - Ошибка получения биржи {exchange_id}: {e}")
            return None
    
    async def get_exchange_by_name(self, name: str) -> Optional[Exchange]:

        try:
            response = self.table.scan(
                FilterExpression=Attr('name').eq(name) & Attr('is_deleted').eq(False)
            )
            if response['Items']:
                return Exchange(**response['Items'][0])
            return None
        except Exception as e:
            print(f"[ERROR][ExchangeRepository] - Ошибка получения биржи по имени {name}: {e}")
            return None
    
    async def get_exchanges_list(self, 
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
            
            exchanges = [Exchange(**item) for item in items]
            
            return {
                'data': exchanges,
                'pagination': {
                    'current_page': page,
                    'total_pages': (total_items + limit - 1) // limit,
                    'total_items': total_items,
                    'items_per_page': limit
                }
            }
        except Exception as e:
            print(f"[ERROR][ExchangeRepository] - Ошибка получения списка бирж: {e}")
            return {'data': [], 'pagination': {}}
    
    async def update_exchange(self, exchange_id: str, update_data: Dict[str, Any]) -> Optional[Exchange]:

        try:
            update_expression = "SET "
            expression_values = {}
            
            for key, value in update_data.items():
                if key != 'id':
                    update_expression += f"{key} = :{key}, "
                    expression_values[f":{key}"] = value
            
            update_expression = update_expression.rstrip(', ')
            
            response = self.table.update_item(
                Key={'id': exchange_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return Exchange(**response['Attributes'])
        except Exception as e:
            print(f"[ERROR][ExchangeRepository] - Ошибка обновления биржи {exchange_id}: {e}")
            return None
    
    async def delete_exchange(self, exchange_id: str) -> bool:

        try:
            response = self.table.update_item(
                Key={'id': exchange_id},
                UpdateExpression='SET is_deleted = :deleted',
                ExpressionAttributeValues={':deleted': True},
                ReturnValues='UPDATED_NEW'
            )
            return True
        except Exception as e:
            print(f"[ERROR][ExchangeRepository] - Ошибка удаления биржи {exchange_id}: {e}")
            return False


class ExchangeStatsRepository(BaseRepository):
    def __init__(self, table_name: str = "exchanges_stats"):
        super().__init__(table_name)
    
    async def create_exchange_stats(self, stats_data: Dict[str, Any]) -> Optional[ExchangesStats]:

        try:
            stats = ExchangesStats(**stats_data)
            item = stats.model_dump()
            

            for key, value in item.items():
                if isinstance(value, UUID):
                    item[key] = str(value)
            
            response = self.table.put_item(Item=item)
            return stats
        except Exception as e:
            print(f"[ERROR][ExchangeStatsRepository] - Ошибка создания статистики биржи: {e}")
            return None
    
    async def get_stats_by_exchange_id(self, exchange_id: str) -> Optional[ExchangesStats]:

        try:
            response = self.table.scan(
                FilterExpression=Attr('exchange_id').eq(exchange_id) & Attr('is_deleted').eq(False)
            )
            if response['Items']:
                return ExchangesStats(**response['Items'][0])
            return None
        except Exception as e:
            print(f"[ERROR][ExchangeStatsRepository] - Ошибка получения статистики биржи {exchange_id}: {e}")
            return None
    
    async def get_stats_by_name(self, name: str) -> Optional[ExchangesStats]:

        try:
            response = self.table.scan(
                FilterExpression=Attr('name').eq(name) & Attr('is_deleted').eq(False)
            )
            if response['Items']:
                return ExchangesStats(**response['Items'][0])
            return None
        except Exception as e:
            print(f"[ERROR][ExchangeStatsRepository] - Ошибка получения статистики по имени {name}: {e}")
            return None
    
    async def get_all_exchange_stats(self, 
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
            
            exchange_stats = [ExchangesStats(**item) for item in items]
            
            return {
                'data': exchange_stats,
                'pagination': {
                    'current_page': page,
                    'total_pages': (total_items + limit - 1) // limit,
                    'total_items': total_items,
                    'items_per_page': limit
                }
            }
        except Exception as e:
            print(f"[ERROR][ExchangeStatsRepository] - Ошибка получения всех статистик бирж: {e}")
            return {'data': [], 'pagination': {}}
    
    async def update_exchange_stats(self, stats_id: str, update_data: Dict[str, Any]) -> Optional[ExchangesStats]:

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
            
            return ExchangesStats(**response['Attributes'])
        except Exception as e:
            print(f"[ERROR][ExchangeStatsRepository] - Ошибка обновления статистики биржи {stats_id}: {e}")
            return None
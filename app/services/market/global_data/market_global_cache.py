from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from app.core.database.repositories.generic import GenericRepository

class MarketGlobalsCacheService:
    def __init__(self):
        self.cache_table = "market_globals_cache"
        self.cache_key = "global_market_data"
        self.ttl_hours = 3  # Изменили с 1 на 3 часа
        
    def _get_repository(self):
        return GenericRepository(self.cache_table)
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        try:
            cached_time = datetime.fromisoformat(cache_entry.get('cached_at', ''))
            expiry_time = cached_time + timedelta(hours=self.ttl_hours)
            current_time = datetime.utcnow()
            
            is_valid = current_time < expiry_time
            
            if is_valid:
                time_left = expiry_time - current_time
                print(f"[DEBUG] Cache is valid, expires in {time_left}")
            else:
                print(f"[DEBUG] Cache expired {current_time - expiry_time} ago")
                
            return is_valid
        except Exception as e:
            print(f"[DEBUG] Cache validation error: {e}")
            return False
    
    async def get_cached_data(self) -> Optional[Dict[str, Any]]:
        try:
            repo = self._get_repository()
            cache_entry = repo.get_by_id(self.cache_key)
            
            if cache_entry and self._is_cache_valid(cache_entry):
                print("[DEBUG] Using cached global market data")
                return json.loads(cache_entry.get('data', '{}'))
            
            if cache_entry:
                print("[DEBUG] Cache exists but expired")
            else:
                print("[DEBUG] No cache entry found")
                
            return None
        except Exception as e:
            print(f"[ERROR] Cache retrieval failed: {e}")
            return None
    
    async def set_cache_data(self, data: Dict[str, Any]) -> bool:
        try:
            repo = self._get_repository()
            
            current_time = datetime.utcnow()
            expiry_time = current_time + timedelta(hours=self.ttl_hours)
            
            cache_entry = {
                'id': self.cache_key,
                'data': json.dumps(data),
                'cached_at': current_time.isoformat(),
                'expires_at': expiry_time.isoformat(),
                'ttl_hours': self.ttl_hours
            }
            
            existing = repo.get_by_id(self.cache_key)
            if existing:
                repo.update_by_id(self.cache_key, cache_entry)
                print(f"[DEBUG] Updated cache, expires at {expiry_time}")
            else:
                repo.create(cache_entry, auto_id=False)
                print(f"[DEBUG] Created new cache entry, expires at {expiry_time}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Cache storage failed: {e}")
            return False

market_globals_cache = MarketGlobalsCacheService()
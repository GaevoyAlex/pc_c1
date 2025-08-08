import httpx
import asyncio
from typing import Dict, Any, Optional, List
from app.core.security.config import settings

class CoinGeckoSearchService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.pro_base_url = "https://pro-api.coingecko.com/api/v3"
        self.timeout = 30.0
        
        self.api_key = getattr(settings, 'COINGECKO_API_KEY', None)
        self.use_pro = bool(self.api_key and self.api_key.strip())
        
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Liberandum-Admin/1.0"
        }
        
        if self.use_pro and self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key
            
        return headers
    
    def _get_base_url(self) -> str:
        return self.pro_base_url if self.use_pro else self.base_url
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        try:
            base_url = self._get_base_url()
            headers = self._get_headers()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{base_url}{endpoint}", 
                    params=params, 
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)
                else:
                    print(f"[ERROR][CoinGecko] - HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"[ERROR][CoinGecko] - Request failed: {e}")
            return None
    
    async def search_coins(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            coins_list = await self._make_request("/coins/list")
            if not coins_list:
                return []
            
            query_lower = query.lower().strip()
            results = []
            
            for coin in coins_list:
                coin_id = coin.get('id', '').lower()
                coin_name = coin.get('name', '').lower()
                coin_symbol = coin.get('symbol', '').lower()
                
                if (query_lower in coin_symbol or 
                    query_lower in coin_name or 
                    query_lower in coin_id or
                    coin_symbol == query_lower):
                    
                    results.append({
                        'id': coin.get('id'),
                        'symbol': coin.get('symbol', '').upper(),
                        'name': coin.get('name')
                    })
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            print(f"[ERROR][CoinGecko] - Search failed: {e}")
            return []
    
    async def search_exchanges(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            exchanges_list = await self._make_request("/exchanges/list")
            if not exchanges_list:
                return []
            
            query_lower = query.lower().strip()
            results = []
            
            for exchange in exchanges_list:
                exchange_id = exchange.get('id', '').lower()
                exchange_name = exchange.get('name', '').lower()
                
                if (query_lower in exchange_name or 
                    query_lower in exchange_id):
                    
                    results.append({
                        'id': exchange.get('id'),
                        'name': exchange.get('name')
                    })
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            print(f"[ERROR][CoinGeckoADMIN] - Exchange search failed: {e}")
            return []

coingecko_search_service = CoinGeckoSearchService()
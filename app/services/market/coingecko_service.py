import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
from app.core.security.config import settings

class CoinGeckoService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.pro_base_url = "https://pro-api.coingecko.com/api/v3"
        self.timeout = 30.0
        
        self.api_key = getattr(settings, 'COINGECKO_API_KEY', None)
        self.use_pro = bool(self.api_key and self.api_key.strip())
        
        if self.use_pro:
            print(f"[INFO][CoinGecko] - Using Pro API")
        else:
            print(f"[INFO][CoinGecko] - Using free API (rate limited)")
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Liberandum-API/1.0"
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
                    print(f"[WARNING][CoinGecko] - Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)
                elif response.status_code == 401:
                    print(f"[ERROR][CoinGecko] - Unauthorized. API key issue, switching to free API")
                    if self.use_pro:
                        self.use_pro = False
                        return await self._make_request(endpoint, params)
                    return None
                elif response.status_code == 403:
                    print(f"[ERROR][CoinGecko] - Forbidden. API key invalid, switching to free API")
                    if self.use_pro:
                        self.use_pro = False
                        return await self._make_request(endpoint, params)
                    return None
                elif response.status_code == 404:
                    print(f"[WARNING][CoinGecko] - Token not found: {endpoint}")
                    return None
                else:
                    print(f"[ERROR][CoinGecko] - HTTP {response.status_code}: {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            print(f"[ERROR][CoinGecko] - Request timeout for {endpoint}")
            return None
        except Exception as e:
            print(f"[ERROR][CoinGecko] - Request failed: {e}")
            return None
    
    def _get_days_from_timeframe(self, timeframe: str) -> str:
        timeframe_mapping = {
            "1h": "1",
            "24h": "1", 
            "7d": "7",
            "30d": "30",
            "90d": "90",
            "1y": "365",
            "max": "max"
        }
        return timeframe_mapping.get(timeframe, "1")
    
    def _get_interval_from_timeframe(self, timeframe: str) -> str:
        if timeframe == "1h":
            return "5m" if self.use_pro else "minutely"
        elif timeframe == "24h":
            return "1h" if self.use_pro else "minutely"
        elif timeframe == "7d":
            return "4h" if self.use_pro else "hourly"
        elif timeframe == "30d":
            return "1d" if self.use_pro else "daily"
        else:
            return "1d" if self.use_pro else "daily"
    
    def _generate_fallback_chart_data(self, token_id: str, timeframe: str, currency: str = "usd") -> Dict[str, Any]:
        print(f"[INFO][CoinGecko] - Generating fallback chart data for {token_id}")
        
        base_price = 50000 if token_id == "bitcoin" else 3000 if token_id == "ethereum" else 100
        
        days = self._get_days_from_timeframe(timeframe)
        data_points = 24 if timeframe == "24h" else 168 if timeframe == "7d" else 30
        
        now = int(time.time() * 1000)
        interval_ms = 24 * 60 * 60 * 1000 if timeframe in ["30d", "90d", "1y"] else 60 * 60 * 1000
        
        prices = []
        market_caps = []
        volumes = []
        
        for i in range(data_points):
            timestamp = now - ((data_points - i) * interval_ms)
            
            price_variation = (i / data_points) * 0.1 + (i % 5) * 0.02
            price = base_price * (1 + price_variation)
            
            market_cap = price * 19000000 if token_id == "bitcoin" else price * 120000000
            volume = market_cap * 0.05
            
            prices.append([timestamp, price])
            market_caps.append([timestamp, market_cap])
            volumes.append([timestamp, volume])
        
        price_values = [p[1] for p in prices]
        volume_values = [v[1] for v in volumes]
        
        first_price = prices[0][1] if prices else 0
        last_price = prices[-1][1] if prices else 0
        price_change_percentage = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0
        
        return {
            "token_id": token_id,
            "symbol": token_id.upper()[:3],
            "name": token_id.title(),
            "timeframe": timeframe,
            "currency": currency,
            "data": {
                "prices": prices,
                "market_caps": market_caps,
                "total_volumes": volumes
            },
            "statistics": {
                "price_change_percentage": round(price_change_percentage, 2),
                "highest_price": max(price_values) if price_values else 0,
                "lowest_price": min(price_values) if price_values else 0,
                "average_volume": sum(volume_values) / len(volume_values) if volume_values else 0
            },
            "updated_at": int(time.time() * 1000),
            "api_source": "fallback"
        }
    
    async def get_token_chart_data(self, token_id: str, timeframe: str, currency: str = "usd") -> Optional[Dict[str, Any]]:
        days = self._get_days_from_timeframe(timeframe)
        interval = self._get_interval_from_timeframe(timeframe)
        
        params = {
            "vs_currency": currency,
            "days": days
        }
        
        if self.use_pro and days != "max":
            params["interval"] = interval
        elif not self.use_pro and days != "1":
            params["interval"] = interval
        
        chart_data = await self._make_request(f"/coins/{token_id}/market_chart", params)
        
        if not chart_data:
            print(f"[WARNING][CoinGecko] - No chart data from API, using fallback for {token_id}")
            return self._generate_fallback_chart_data(token_id, timeframe, currency)
        
        coin_info = await self._make_request(f"/coins/{token_id}")
        
        prices = chart_data.get("prices", [])
        market_caps = chart_data.get("market_caps", [])
        volumes = chart_data.get("total_volumes", [])
        
        if not prices:
            print(f"[WARNING][CoinGecko] - Empty price data, using fallback for {token_id}")
            return self._generate_fallback_chart_data(token_id, timeframe, currency)
        
        price_values = [price[1] for price in prices]
        volume_values = [vol[1] for vol in volumes]
        
        first_price = prices[0][1] if prices else 0
        last_price = prices[-1][1] if prices else 0
        price_change_percentage = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0
        
        statistics = {
            "price_change_percentage": round(price_change_percentage, 2),
            "highest_price": max(price_values) if price_values else 0,
            "lowest_price": min(price_values) if price_values else 0,
            "average_volume": sum(volume_values) / len(volume_values) if volume_values else 0
        }
        
        return {
            "token_id": token_id,
            "symbol": coin_info.get("symbol", "").upper() if coin_info else token_id.upper()[:3],
            "name": coin_info.get("name", "") if coin_info else token_id.title(),
            "timeframe": timeframe,
            "currency": currency,
            "data": {
                "prices": prices,
                "market_caps": market_caps,
                "total_volumes": volumes
            },
            "statistics": statistics,
            "updated_at": int(time.time() * 1000),
            "api_source": "pro" if self.use_pro else "free"
        }
    
    async def get_token_current_price(self, token_id: str, currency: str = "usd") -> Optional[Dict[str, Any]]:
        params = {
            "ids": token_id,
            "vs_currencies": currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }
        
        if self.use_pro:
            params.update({
                "include_last_updated_at": "true",
                "precision": "full"
            })
        
        data = await self._make_request("/simple/price", params)
        if not data or token_id not in data:
            return None
        
        token_data = data[token_id]
        
        coin_info = await self._make_request(f"/coins/{token_id}")
        symbol = coin_info.get("symbol", "").upper() if coin_info else token_id.upper()
        
        return {
            "token_id": token_id,
            "symbol": symbol,
            "price": token_data.get(currency, 0),
            "price_change_24h": token_data.get(f"{currency}_24h_change", 0),
            "volume_24h": token_data.get(f"{currency}_24h_vol", 0),
            "market_cap": token_data.get(f"{currency}_market_cap", 0),
            "timestamp": int(time.time() * 1000),
            "last_updated": token_data.get("last_updated_at") if self.use_pro else None,
            "api_source": "pro" if self.use_pro else "free"
        }

coingecko_service = CoinGeckoService()
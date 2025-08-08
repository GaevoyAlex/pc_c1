import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time

from app.core.security.config import settings

class MarketGlobalsService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.pro_base_url = "https://pro-api.coingecko.com/api/v3"
        self.timeout = 30.0
        
        self.api_key = getattr(settings, 'COINGECKO_API_KEY', None)
        self.use_pro = bool(self.api_key and self.api_key.strip())
        
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
                    return None
                elif response.status_code in [401, 403] and self.use_pro:
                    self.use_pro = False
                    return await self._make_request(endpoint, params)
                else:
                    return None
                    
        except Exception:
            return None
    
    async def get_global_data(self) -> Optional[Dict[str, Any]]:
        global_data = await self._make_request("/global")
        
        if not global_data:
            return None
            
        data = global_data.get("data", {})
        
        return {
            "total_market_cap": data.get("total_market_cap", {}).get("usd", 0),
            "total_volume": data.get("total_volume", {}).get("usd", 0),
            "market_cap_percentage": data.get("market_cap_percentage", {}),
            "market_cap_change_percentage_24h_usd": data.get("market_cap_change_percentage_24h_usd", 0),
            "updated_at": data.get("updated_at", 0)
        }
    
    async def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get("https://api.alternative.me/fng/")
                
                if response.status_code == 200:
                    data = response.json()
                    fng_data = data.get("data", [])
                    
                    if fng_data:
                        latest = fng_data[0]
                        return {
                            "value": int(latest.get("value", 0)),
                            "value_classification": latest.get("value_classification", ""),
                            "timestamp": latest.get("timestamp", ""),
                            "time_until_update": latest.get("time_until_update", "")
                        }
                        
            return None
        except Exception:
            return None
    
    async def get_alt_season_index(self) -> Optional[Dict[str, Any]]:
        # Пробуем Playwright скрапинг
        try:
            from app.services.market.global_data.playwright_alt_season_scraper import playwright_scraper
            
            print("[INFO] Trying CoinMarketCap scraping with Playwright...")
            alt_season = await playwright_scraper.scrape_coinmarketcap()
            
            if not alt_season:
                print("[INFO] CoinMarketCap scraping failed, trying BlockchainCenter...")
                alt_season = await playwright_scraper.scrape_blockchaincenter()
            
            if alt_season:
                return alt_season
                
        except ImportError:
            print("[INFO] Playwright not available")
        except Exception as e:
            print(f"[ERROR] Playwright scraping failed: {e}")
        
        return None
    
    async def calculate_fallback_alt_season(self, market_cap_percentage: Dict[str, float]) -> Dict[str, Any]:
        btc_dominance = market_cap_percentage.get("btc", 50.0)
        eth_dominance = market_cap_percentage.get("eth", 15.0)
        
        alt_dominance = 100 - btc_dominance - eth_dominance
        
        if btc_dominance >= 70:
            status = "btc_season"
            intensity = min(100, ((btc_dominance - 50) / 30) * 100)
            description = f"Bitcoin Season - BTC dominance at {btc_dominance:.1f}% (fallback calculation)"
        elif btc_dominance <= 40:
            status = "alt_season"  
            intensity = min(100, ((50 - btc_dominance) / 20) * 100)
            description = f"Alt Season - BTC dominance low at {btc_dominance:.1f}% (fallback calculation)"
        elif alt_dominance >= 45:
            status = "alt_season"
            intensity = min(100, ((alt_dominance - 35) / 20) * 100) 
            description = f"Alt Season - High altcoin dominance at {alt_dominance:.1f}% (fallback calculation)"
        else:
            status = "neutral"
            intensity = 50
            description = f"Neutral Market - BTC {btc_dominance:.1f}%, ALT {alt_dominance:.1f}% (fallback calculation)"
        
        return {
            "alt_season_index": round(intensity, 0),
            "status": status,
            "description": description,
            "source": "dominance_fallback",
            "methodology": "Market cap dominance analysis",
            "btc_dominance": round(btc_dominance, 2),
            "eth_dominance": round(eth_dominance, 2),
            "alt_dominance": round(alt_dominance, 2),
            "updated_at": datetime.utcnow().isoformat()
        }

market_globals_service = MarketGlobalsService()
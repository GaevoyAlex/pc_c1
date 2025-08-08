from typing import Dict, Any, Optional
from datetime import datetime

from app.services.market.global_data.market_global_service import market_globals_service
from app.services.market.global_data.market_global_cache import market_globals_cache
from app.schemas.market_global import GlobalMarketResponse, MarketCapData, FearGreedIndex, AltSeasonData

class GlobalMarketDataService:
    
    async def get_global_market_data(self) -> Optional[GlobalMarketResponse]:
        cached_data = await market_globals_cache.get_cached_data()
        
        if cached_data:
            return self._parse_cached_response(cached_data)
        
        fresh_data = await self._fetch_fresh_data()
        
        if fresh_data:
            await market_globals_cache.set_cache_data(fresh_data)
            return self._parse_response(fresh_data)
        
        return None
    
    async def _fetch_fresh_data(self) -> Optional[Dict[str, Any]]:
        try:
            global_data = await market_globals_service.get_global_data()
            fear_greed = await market_globals_service.get_fear_greed_index()
            
            if not global_data:
                return None
            
            # Сначала пытаемся получить Alt Season через CoinGecko API
            alt_season = await market_globals_service.get_alt_season_index()
            
            # Если не получилось - используем fallback на основе доминирования
            if not alt_season:
                print("[INFO] CoinGecko Alt Season calculation failed, using dominance fallback")
                market_cap_percentage = global_data.get("market_cap_percentage", {})
                alt_season = await market_globals_service.calculate_fallback_alt_season(market_cap_percentage)
            
            return {
                "global_data": global_data,
                "fear_greed": fear_greed,
                "alt_season": alt_season,
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "api"
            }
        except Exception as e:
            print(f"[ERROR] Failed to fetch fresh data: {e}")
            return None
    
    def _parse_response(self, data: Dict[str, Any]) -> GlobalMarketResponse:
        global_data = data.get("global_data", {})
        fear_greed = data.get("fear_greed", {})
        alt_season = data.get("alt_season", {})
        
        market_cap_percentage = global_data.get("market_cap_percentage", {})
        
        return GlobalMarketResponse(
            market_cap=MarketCapData(
                total_market_cap_usd=global_data.get("total_market_cap", 0),
                total_volume_usd=global_data.get("total_volume", 0),
                market_cap_change_24h_percent=global_data.get("market_cap_change_percentage_24h_usd", 0),
                btc_dominance=market_cap_percentage.get("btc", 0),
                eth_dominance=market_cap_percentage.get("eth", 0)
            ),
            fear_greed_index=FearGreedIndex(
                value=fear_greed.get("value", 50),
                value_classification=fear_greed.get("value_classification", "Neutral"),
                timestamp=fear_greed.get("timestamp", ""),
                time_until_update=fear_greed.get("time_until_update")
            ),
            alt_season=AltSeasonData(
                alt_season_index=alt_season.get("alt_season_index", 50),
                status=alt_season.get("status", "neutral"),
                description=alt_season.get("description", ""),
                source=alt_season.get("source", "unknown"),
                btc_dominance=alt_season.get("btc_dominance"),
                eth_dominance=alt_season.get("eth_dominance"),
                alt_dominance=alt_season.get("alt_dominance")
            ),
            last_updated=data.get("fetched_at", ""),
            data_source=data.get("source", "cache")
        )
    
    def _parse_cached_response(self, data: Dict[str, Any]) -> GlobalMarketResponse:
        data["source"] = "cache"
        return self._parse_response(data)

global_market_service = GlobalMarketDataService()
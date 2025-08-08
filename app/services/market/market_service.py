from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database.connector import get_generic_repository
from app.schemas.market import (
    TokenResponse, TokenDetailResponse, TokenListResponse,
    ExchangeListResponse, TokenSparkline,
    HalalStatus, MarketData, Statistics, AllTimeHigh, AllTimeLow, PriceIndicators24h
)

class MarketDataService:
    def __init__(self):
        self.token_stats_table = "LiberandumAggregationTokenStats"
        self.tokens_table = "LiberandumAggregationToken"
        self.exchange_stats_table = "LiberandumAggregationExchangesStats"
        self.exchanges_table = "LiberandumAggregationExchanges"

    def _get_repository(self, table_name: str):
        repo = get_generic_repository(table_name)
        if not repo:
            raise RuntimeError(f"Репозиторий для таблицы {table_name} недоступен")
        return repo

    def get_tokens_list(self, page: int = 1, limit: int = 100, sort: Optional[str] = None) -> TokenListResponse:
        try:
            token_stats_repo = self._get_repository(self.token_stats_table)
            
            scan_limit = min(limit * 2, 50)
            all_token_stats = token_stats_repo.scan_items(self.token_stats_table, limit=scan_limit)
            token_stats = [ts for ts in all_token_stats if not ts.get('is_deleted', False)]
            
            if sort == "market_cap":
                token_stats = sorted(token_stats, 
                    key=lambda x: float(str(x.get('market_cap', 0) or 0).replace(',', '')), 
                    reverse=True)
            elif sort == "volume":
                token_stats = sorted(token_stats, 
                    key=lambda x: float(str(x.get('trading_volume_24h', 0) or 0).replace(',', '')), 
                    reverse=True)
            
            total_items = len(token_stats)
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_stats = token_stats[start_idx:end_idx]
            
            token_responses = []
            for stat in paginated_stats:
                try:
                    token_response = self._convert_token_stats_to_response(stat)
                    token_responses.append(token_response)
                except Exception as e:
                    print(f"[ERROR] Ошибка конвертации токена: {e}")
                    continue
            
            pagination = {
                "current_page": page,
                "total_pages": (total_items + limit - 1) // limit if total_items > 0 else 0,
                "total_items": total_items,
                "items_per_page": limit
            }
            
            return TokenListResponse(data=token_responses, pagination=pagination)
            
        except Exception as e:
            print(f"[ERROR] Критическая ошибка в get_tokens_list: {e}")
            return TokenListResponse(
                data=[], 
                pagination={"current_page": 1, "total_pages": 0, "total_items": 0, "items_per_page": limit}
            )
    
    def _convert_token_stats_to_response(self, token_stats: Dict[str, Any]) -> TokenResponse:
        def safe_float(value, default=0.0):
            try:
                return float(str(value or 0).replace(',', ''))
            except:
                return default
        
        def safe_int(value, default=0):
            try:
                return int(float(str(value or 0).replace(',', '')))
            except:
                return default
        
        sparkline_data = token_stats.get('sparkline_7d', [])
        if not sparkline_data:
            sparkline_data = []
        
        return TokenResponse(
            id=str(token_stats.get('coingecko_id', token_stats.get('symbol', 'unknown'))).lower(),
            symbol=str(token_stats.get('symbol', 'UNKNOWN')).upper(),
            name=str(token_stats.get('coin_name', 'Unknown Token')),
            image=token_stats.get('image', ''),
            current_price=safe_float(token_stats.get('price')),
            market_cap=safe_int(token_stats.get('market_cap')),
            price_change_percentage_24h=safe_float(token_stats.get('price_change_24h')),
            price_change_percentage_7d=safe_float(token_stats.get('price_change_7d')),
            sparkline_in_7d=TokenSparkline(price=sparkline_data)
        )

    def get_token_detail(self, token_id: str) -> Optional[TokenDetailResponse]:
        try:
            token_stats_repo = self._get_repository(self.token_stats_table)
            tokens_repo = self._get_repository(self.tokens_table)
            
            token_stats_results = token_stats_repo.find_by_field('coingecko_id', token_id)
            if not token_stats_results:
                return None
            
            token_stats = token_stats_results[0]
            
            token = None
            if token_stats.get('symbol'):
                token_results = tokens_repo.find_by_field('symbol', token_stats['symbol'])
                if token_results:
                    token = token_results[0]
            
            def safe_float(value, default=0.0):
                try:
                    return float(value or 0)
                except:
                    return default
            
            def safe_int(value, default=0):
                try:
                    return int(float(value or 0))
                except:
                    return default
            
            return TokenDetailResponse(
                id=token_stats.get('coingecko_id', ''),
                symbol=token_stats.get('symbol', '').upper(),
                name=token_stats.get('coin_name', ''),
                image=token.get('avatar_image', '') if token else '',
                current_price=safe_float(token_stats.get('price')),
                price_change_percentage_24h=safe_float(token_stats.get('price_change_24h')),
                halal_status=HalalStatus(
                    is_halal=token_stats.get('is_halal', None),
                    verified=token_stats.get('halal_verified', None)
                ),
                market_data=MarketData(
                    market_cap={"usd": safe_int(token_stats.get('market_cap'))},
                    fully_diluted_valuation={"usd": safe_int(token_stats.get('fully_diluted_valuation'))},
                    total_volume={"usd": safe_int(token_stats.get('trading_volume_24h'))},
                    circulating_supply={"value": safe_int(token_stats.get('circulating_supply'))},
                    max_supply={"value": safe_int(token_stats.get('max_supply'))},
                    total_supply={"value": safe_int(token_stats.get('total_supply'))}
                ),
                statistics=Statistics(
                    all_time_high=AllTimeHigh(
                        price=safe_float(token_stats.get('ath')),
                        date=token_stats.get('ath_date', '')
                    ),
                    all_time_low=AllTimeLow(
                        price=safe_float(token_stats.get('atl')),
                        date=token_stats.get('atl_date', '')
                    ),
                    price_indicators_24h=PriceIndicators24h(
                        min=safe_float(token_stats.get('low_24h')),
                        max=safe_float(token_stats.get('high_24h'))
                    )
                )
            )
            
        except Exception as e:
            print(f"[ERROR][MarketService] - Ошибка получения токена {token_id}: {e}")
            return None

    def get_exchanges_list(self) -> ExchangeListResponse:
        try:
            exchange_stats_repo = self._get_repository(self.exchange_stats_table)
            all_exchange_stats = exchange_stats_repo.scan_items(self.exchange_stats_table, limit=50)
            
            exchange_responses = []
            for idx, stat in enumerate(all_exchange_stats, 1):
                if stat.get('is_deleted', False):
                    continue
                
                exchange_response = {
                    "rank": stat.get('rank', idx),
                    "id": str(stat.get('coingecko_id', stat.get('name', 'unknown'))).lower().replace(' ', '_'),
                    "name": str(stat.get('name', '')),
                    "image": stat.get('image', ''),
                    "halal_status": {
                        "is_halal": stat.get('is_halal', None),
                        "score": stat.get('halal_score', ''),
                        "rating": stat.get('halal_rating', 0)
                    },
                    "trust_score": stat.get('trust_score', 0),
                    "volume_24h_usd": stat.get('trading_volume_24h', 0),
                    "volume_24h_formatted": str(stat.get('trading_volume_24h', 0)),
                    "reserves_usd": stat.get('reserves', 0),
                    "reserves_formatted": str(stat.get('reserves', 0)),
                    "trading_pairs_count": stat.get('trading_pairs', 0),
                    "visitors_monthly": str(stat.get('visitors_monthly', 0)),
                    "supported_fiat": stat.get('supported_fiat', []),
                    "supported_fiat_display": str(stat.get('supported_fiat', [])),
                    "volume_chart_7d": stat.get('volume_chart_7d', []),
                    "exchange_type": stat.get('exchange_type', 'centralized')
                }
                exchange_responses.append(exchange_response)
            
            return ExchangeListResponse(data=exchange_responses)
            
        except Exception as e:
            print(f"[ERROR][MarketService] - Ошибка получения списка бирж: {e}")
            return ExchangeListResponse(data=[])

    def get_exchange_detail(self, exchange_id: str) -> Optional[Dict[str, Any]]:
        try:
            exchange_stats_repo = self._get_repository(self.exchange_stats_table)
            
            exchange_stats_results = exchange_stats_repo.find_by_field('coingecko_id', exchange_id)
            if not exchange_stats_results:
                exchange_name = exchange_id.replace('_', ' ').title()
                exchange_stats_results = exchange_stats_repo.find_by_field('name', exchange_name)
                
            if not exchange_stats_results:
                return None
            
            stats = exchange_stats_results[0]
            
            return {
                "id": stats.get('coingecko_id', exchange_id),
                "name": stats.get('name', ''),
                "image": stats.get('image', ''),
                "halal_status": {
                    "score": stats.get('halal_score', ''),
                    "rating": stats.get('halal_rating', 0),
                    "is_halal": stats.get('is_halal', None)
                },
                "trust_score": stats.get('trust_score', 0),
                "volume_24h_usd": stats.get('trading_volume_24h', 0),
                "total_assets_usd": stats.get('reserves', 0),
                "trading_pairs_count": stats.get('trading_pairs', 0),
                "visitors_monthly": str(stats.get('visitors_monthly', 0)),
                "website_url": stats.get('website_url', ''),
                "supported_fiat": stats.get('supported_fiat', [])
            }
            
        except Exception as e:
            print(f"[ERROR][MarketService] - Ошибка получения деталей биржи {exchange_id}: {e}")
            return None

market_service = MarketDataService()
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from app.core.database.connector import get_generic_repository
from app.schemas.market import (
    TokenResponse, TokenDetailResponse, TokenListResponse, TokenFullStatsResponse,
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

    def _remove_duplicates_by_symbol(self, token_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_symbols: Set[str] = set()
        unique_tokens = []
        
        sorted_tokens = sorted(
            token_stats, 
            key=lambda x: x.get('updated_at', ''), 
            reverse=True
        )
        
        for token in sorted_tokens:
            symbol = token.get('symbol', '').upper()
            if symbol and symbol not in seen_symbols:
                seen_symbols.add(symbol)
                unique_tokens.append(token)
        
        return unique_tokens

    def get_tokens_list(self, page: int = 1, limit: int = 100, sort: Optional[str] = None) -> TokenListResponse:
        try:
            token_stats_repo = self._get_repository(self.token_stats_table)
            tokens_repo = self._get_repository(self.tokens_table)
            
            scan_limit = min(limit * 3, 1000)
            all_token_stats = token_stats_repo.scan_items(self.token_stats_table, limit=scan_limit)
            
            active_token_stats = [ts for ts in all_token_stats if not ts.get('is_deleted', False)]
            unique_token_stats = self._remove_duplicates_by_symbol(active_token_stats)
            
            all_tokens = tokens_repo.scan_items(self.tokens_table, limit=1000)
            tokens_by_symbol = {}
            for token in all_tokens:
                if not token.get('is_deleted', False):
                    symbol = token.get('symbol', '').upper()
                    if symbol:
                        tokens_by_symbol[symbol] = token
            
            sorted_token_stats = self._apply_sorting(unique_token_stats, sort)
            
            total_items = len(sorted_token_stats)
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_stats = sorted_token_stats[start_idx:end_idx]
            
            token_responses = []
            for stat in paginated_stats:
                try:
                    symbol = stat.get('symbol', '').upper()
                    token_data = tokens_by_symbol.get(symbol)
                    token_response = self._convert_token_stats_to_response(stat, token_data)
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

    def _apply_sorting(self, token_stats: List[Dict[str, Any]], sort: Optional[str]) -> List[Dict[str, Any]]:
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
        
        def safe_bool(value, default=False):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes')
            return bool(value)
        
        def get_token_category(token_stat):
            symbol = str(token_stat.get('symbol', '')).upper()
            name = str(token_stat.get('coin_name', '')).lower()
            
            if symbol in ['USDT', 'USDC', 'DAI', 'BUSD', 'FRAX', 'TUSD', 'FDUSD']:
                return "stablecoin"
            elif symbol in ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'AVAX', 'MATIC', 'DOT', 'ATOM', 'NEAR', 'FTM']:
                return "layer1"
            elif 'layer' in name or 'l2' in name or symbol in ['ARB', 'OP', 'MATIC']:
                return "layer2"
            elif any(word in name for word in ['defi', 'swap', 'finance', 'lending', 'protocol']):
                return "defi"
            elif any(word in name for word in ['meme', 'doge', 'shib', 'pepe', 'floki']):
                return "meme"
            else:
                return "other"
        
        if sort == "market_cap":
            return sorted(token_stats, 
                         key=lambda x: safe_float(x.get('market_cap')), 
                         reverse=True)
        
        elif sort == "volume":
            return sorted(token_stats, 
                         key=lambda x: safe_float(x.get('trading_volume_24h')), 
                         reverse=True)
        
        elif sort == "price":
            return sorted(token_stats, 
                         key=lambda x: safe_float(x.get('price')), 
                         reverse=True)
        
        elif sort == "price_change_24h":
            return sorted(token_stats, 
                         key=lambda x: safe_float(x.get('volume_24h_change_24h')), 
                         reverse=True)
        
        elif sort == "price_change_7d":
            return sorted(token_stats, 
                         key=lambda x: safe_float(x.get('price_change_7d')), 
                         reverse=True)
        
        elif sort == "halal":
            return sorted(token_stats, 
                         key=lambda x: (safe_bool(x.get('is_halal'), False), safe_float(x.get('market_cap'))), 
                         reverse=True)
        
        elif sort == "layer1":
            return sorted(token_stats, 
                         key=lambda x: (get_token_category(x) == "layer1", safe_float(x.get('market_cap'))), 
                         reverse=True)
        
        elif sort == "stablecoin":
            return sorted(token_stats, 
                         key=lambda x: (get_token_category(x) == "stablecoin", safe_float(x.get('market_cap'))), 
                         reverse=True)
        
        elif sort == "defi":
            return sorted(token_stats, 
                         key=lambda x: (get_token_category(x) == "defi", safe_float(x.get('market_cap'))), 
                         reverse=True)
        
        elif sort == "meme":
            return sorted(token_stats, 
                         key=lambda x: (get_token_category(x) == "meme", safe_float(x.get('market_cap'))), 
                         reverse=True)
        
        elif sort == "category":
            category_order = {"layer1": 0, "stablecoin": 1, "defi": 2, "layer2": 3, "meme": 4, "other": 5}
            return sorted(token_stats, 
                         key=lambda x: (category_order.get(get_token_category(x), 10), -safe_float(x.get('market_cap'))))
        
        elif sort == "alphabetical":
            return sorted(token_stats, key=lambda x: str(x.get('symbol', '')).upper())
        
        else:
            return sorted(token_stats, 
                         key=lambda x: (safe_int(x.get('market_cap_rank'), 999999), -safe_float(x.get('market_cap'))))

    def get_token_full_stats(self, symbol_or_id: str) -> Optional[TokenFullStatsResponse]:
        try:
            token_stats_repo = self._get_repository(self.token_stats_table)
            
            token_stats_by_symbol = token_stats_repo.find_by_field('symbol', symbol_or_id.upper())
            
            if not token_stats_by_symbol:
                token_stats_by_coingecko = token_stats_repo.find_by_field('coingecko_id', symbol_or_id.lower())
                if not token_stats_by_coingecko:
                    return None
                token_stats = token_stats_by_coingecko
            else:
                token_stats = token_stats_by_symbol
            
            unique_stats = self._remove_duplicates_by_symbol(token_stats)
            if not unique_stats:
                return None
            
            latest_stats = unique_stats[0]
            
            def safe_float(value, default=None):
                try:
                    return float(str(value or 0).replace(',', '')) if value is not None else default
                except:
                    return default
            
            def safe_int(value, default=None):
                try:
                    return int(float(str(value or 0).replace(',', ''))) if value is not None else default
                except:
                    return default
            
            return TokenFullStatsResponse(
                id=latest_stats.get('id', ''),
                symbol=latest_stats.get('symbol', ''),
                coin_name=latest_stats.get('coin_name', ''),
                coingecko_id=latest_stats.get('coingecko_id', ''),
                market_cap=safe_float(latest_stats.get('market_cap')),
                trading_volume_24h=safe_float(latest_stats.get('trading_volume_24h')),
                token_max_supply=safe_int(latest_stats.get('token_max_supply')),
                token_total_supply=safe_int(latest_stats.get('token_total_supply')),
                transactions_count_30d=safe_int(latest_stats.get('transactions_count_30d')),
                volume_1m_change_1m=safe_float(latest_stats.get('volume_1m_change_1m')),
                volume_24h_change_24h=safe_float(latest_stats.get('volume_24h_change_24h')),
                price=safe_float(latest_stats.get('price')),
                ath=safe_float(latest_stats.get('ath')),
                atl=safe_float(latest_stats.get('atl')),
                liquidity_score=safe_float(latest_stats.get('liquidity_score')),
                tvl=safe_float(latest_stats.get('tvl')),
                price_change_24h=safe_float(latest_stats.get('price_change_24h')),
                price_change_7d=safe_float(latest_stats.get('price_change_7d')),
                price_change_30d=safe_float(latest_stats.get('price_change_30d')),
                market_cap_rank=safe_int(latest_stats.get('market_cap_rank')),
                volume_rank=safe_int(latest_stats.get('volume_rank')),
                created_at=latest_stats.get('created_at', ''),
                updated_at=latest_stats.get('updated_at', '')
            )
            
        except Exception as e:
            print(f"[ERROR][MarketService] - Ошибка получения полной статистики токена {symbol_or_id}: {e}")
            return None
    
    def _convert_token_stats_to_response(self, token_stats: Dict[str, Any], token_data: Dict[str, Any] = None) -> TokenResponse:
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
        
        def safe_bool(value, default=None):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes')
            return bool(value)
        
        def get_token_category(token_stat, token):
            if token and token.get('token_category'):
                return token['token_category']
            
            symbol = str(token_stat.get('symbol', '')).upper()
            name = str(token_stat.get('coin_name', '')).lower()
            
            if symbol in ['USDT', 'USDC', 'DAI', 'BUSD', 'FRAX', 'TUSD', 'FDUSD']:
                return "stablecoin"
            elif symbol in ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'AVAX', 'MATIC', 'DOT', 'ATOM', 'NEAR', 'FTM']:
                return "layer1"
            elif 'layer' in name or 'l2' in name or symbol in ['ARB', 'OP', 'MATIC']:
                return "layer2"
            elif any(word in name for word in ['defi', 'swap', 'finance', 'lending', 'protocol']):
                return "defi"
            elif any(word in name for word in ['meme', 'doge', 'shib', 'pepe', 'floki']):
                return "meme"
            else:
                return "other"
        
        sparkline_data = token_stats.get('sparkline_7d', [])
        if not isinstance(sparkline_data, list):
            sparkline_data = []
        
        token_category = get_token_category(token_stats, token_data)
        
        return TokenResponse(
            id=str(token_stats.get('coingecko_id', token_stats.get('symbol', 'unknown'))).lower(),
            symbol=str(token_stats.get('symbol', 'UNKNOWN')).upper(),
            name=str(token_stats.get('coin_name', 'Unknown Token')),
            image=token_data.get('avatar_image', '') if token_data else '',
            current_price=safe_float(token_stats.get('price')),
            market_cap=safe_int(token_stats.get('market_cap')),
            price_change_percentage_24h=safe_float(token_stats.get('volume_24h_change_24h')),
            price_change_percentage_7d=safe_float(token_stats.get('price_change_7d')),
            sparkline_in_7d=TokenSparkline(price=sparkline_data),
            is_halal=safe_bool(token_stats.get('is_halal') or (token_data.get('is_halal') if token_data else None)),
            is_layer_one=token_category == "layer1",
            is_stablecoin=token_category == "stablecoin",
            token_category=token_category,
            market_cap_rank=safe_int(token_stats.get('market_cap_rank')),
            volume_24h=safe_float(token_stats.get('trading_volume_24h')),
            total_supply=safe_float(token_stats.get('token_total_supply')),
            max_supply=safe_float(token_stats.get('token_max_supply'))
        )

    def get_token_detail(self, token_id: str) -> Optional[TokenDetailResponse]:
        try:
            token_stats_repo = self._get_repository(self.token_stats_table)
            tokens_repo = self._get_repository(self.tokens_table)
            
            token_stats_results = token_stats_repo.find_by_field('coingecko_id', token_id)
            if not token_stats_results:
                token_stats_results = token_stats_repo.find_by_field('symbol', token_id.upper())
            
            if not token_stats_results:
                return None
            
            unique_stats = self._remove_duplicates_by_symbol(token_stats_results)
            if not unique_stats:
                return None
            
            token_stats = unique_stats[0]
            
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
                price_change_percentage_24h=safe_float(token_stats.get('volume_24h_change_24h')),
                halal_status=HalalStatus(
                    is_halal=token_stats.get('is_halal', None),
                    verified=token_stats.get('halal_verified', None),
                    halal_score=token_stats.get('halal_score', None)
                ),
                market_data=MarketData(
                    market_cap_usd=safe_int(token_stats.get('market_cap')),
                    fully_diluted_valuation_usd=safe_int(token_stats.get('fully_diluted_valuation')),
                    total_volume_usd=safe_int(token_stats.get('trading_volume_24h')),
                    circulating_supply_value=safe_int(token_stats.get('circulating_supply')),
                    max_supply_value=safe_int(token_stats.get('token_max_supply')),
                    total_supply_value=safe_int(token_stats.get('token_total_supply'))
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
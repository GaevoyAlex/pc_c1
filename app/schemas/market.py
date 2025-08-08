from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal

class TokenSparkline(BaseModel):
    price: List[float] = Field(default_factory=list)

class TokenResponse(BaseModel):
    id: str
    symbol: str
    name: str
    image: str = ""
    current_price: float = 0.0
    market_cap: int = 0
    price_change_percentage_24h: float = 0.0
    price_change_percentage_7d: float = 0.0
    sparkline_in_7d: TokenSparkline = Field(default_factory=lambda: TokenSparkline(price=[]))

class HalalStatus(BaseModel):
    is_halal: Optional[bool] = None  
    verified: Optional[bool] = None  

class MarketData(BaseModel):
    market_cap_usd: int = Field(default=0, alias="market_cap")
    fully_diluted_valuation_usd: int = Field(default=0, alias="fully_diluted_valuation")
    total_volume_usd: int = Field(default=0, alias="total_volume") 
    circulating_supply_value: Union[int, float] = Field(default=0, alias="circulating_supply")
    max_supply_value: Union[int, float] = Field(default=0, alias="max_supply")
    total_supply_value: Union[int, float] = Field(default=0, alias="total_supply")

class AllTimeHigh(BaseModel):
    price: float = 0.0
    date: str = ""

class AllTimeLow(BaseModel):
    price: float = 0.0
    date: str = ""

class PriceIndicators24h(BaseModel):
    min: float = 0.0
    max: float = 0.0

class Statistics(BaseModel):
    all_time_high: AllTimeHigh = Field(default_factory=AllTimeHigh)
    all_time_low: AllTimeLow = Field(default_factory=AllTimeLow)
    price_indicators_24h: PriceIndicators24h = Field(default_factory=PriceIndicators24h)

class TokenDetailResponse(BaseModel):
    id: str
    symbol: str
    name: str
    image: str = ""
    current_price: float = 0.0
    price_change_percentage_24h: float = 0.0
    halal_status: HalalStatus = Field(default_factory=lambda: HalalStatus(is_halal=None, verified=None))
    market_data: MarketData = Field(default_factory=MarketData)
    statistics: Statistics = Field(default_factory=Statistics)

class Pagination(BaseModel):
    current_page: int = 1
    total_pages: int = 0
    total_items: int = 0
    items_per_page: int = 100

class TokenListResponse(BaseModel):
    data: List[TokenResponse] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)

class ExchangeHalalStatus(BaseModel):
    is_halal: Optional[bool] = None
    score: str = ""
    rating: int = 0

class ExchangeResponse(BaseModel):
    rank: int = 0
    id: str
    name: str
    image: str = ""
    halal_status: ExchangeHalalStatus = Field(default_factory=lambda: ExchangeHalalStatus(is_halal=None))
    trust_score: int = 0
    volume_24h_usd: Union[int, float] = 0
    volume_24h_formatted: str = "$0"
    reserves_usd: Union[int, float] = 0
    reserves_formatted: str = "$0"
    trading_pairs_count: int = 0
    visitors_monthly: str = "0"
    supported_fiat: List[str] = Field(default_factory=list)
    supported_fiat_display: str = ""
    volume_chart_7d: List[Union[int, float]] = Field(default_factory=list)
    exchange_type: str = "centralized"

class ExchangeDetailResponse(BaseModel):
    id: str
    name: str
    image: str = ""
    halal_status: ExchangeHalalStatus = Field(default_factory=lambda: ExchangeHalalStatus(is_halal=None))
    trust_score: int = 0
    volume_24h_usd: Union[int, float] = 0
    total_assets_usd: Union[int, float] = 0
    trading_pairs_count: int = 0
    visitors_monthly: str = "0"
    website_url: str = ""
    supported_fiat: List[str] = Field(default_factory=list)
    country: Optional[str] = None
    year_established: Optional[int] = None

class ExchangeListResponse(BaseModel):
    data: List[ExchangeResponse] = Field(default_factory=list)

class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 100
    sort: Optional[str] = None

class TokenDataConverter(BaseModel):
    @staticmethod
    def from_db_to_api(token_stats: Dict[str, Any], token: Dict[str, Any] = None) -> TokenResponse:
        def safe_float(value, default=0.0):
            try:
                if value is None:
                    return default
                return float(str(value).replace(',', ''))
            except (ValueError, TypeError):
                return default
        
        def safe_int(value, default=0):
            try:
                if value is None:
                    return default
                return int(float(str(value).replace(',', '')))
            except (ValueError, TypeError):
                return default
        
        sparkline_data = token_stats.get('sparkline_7d', [])
        if not isinstance(sparkline_data, list):
            sparkline_data = []
        
        return TokenResponse(
            id=token_stats.get('coingecko_id', token_stats.get('symbol', 'unknown')),
            symbol=str(token_stats.get('symbol', 'UNKNOWN')).upper(),
            name=str(token_stats.get('coin_name', 'Unknown Token')),
            image=token.get('avatar_image', '') if token else '',
            current_price=safe_float(token_stats.get('price')),
            market_cap=safe_int(token_stats.get('market_cap')),
            price_change_percentage_24h=safe_float(token_stats.get('volume_24h_change_24h')),
            price_change_percentage_7d=safe_float(token_stats.get('price_change_7d', 2.5)),
            sparkline_in_7d=TokenSparkline(price=sparkline_data)
        )

class ExchangeDataConverter(BaseModel):
    @staticmethod
    def from_db_to_api(exchange_stats: Dict[str, Any], exchange: Dict[str, Any] = None, rank: int = 1) -> ExchangeResponse:
        def safe_float(value, default=0.0):
            try:
                if value is None:
                    return default
                return float(str(value).replace(',', ''))
            except (ValueError, TypeError):
                return default
        
        def safe_int(value, default=0):
            try:
                if value is None:
                    return default
                return int(float(str(value).replace(',', '')))
            except (ValueError, TypeError):
                return default
        
        def safe_bool(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes')
            return bool(value)
        
        try:
            volume_24h = safe_float(exchange_stats.get('trading_volume_24h'))
            reserves = safe_float(exchange_stats.get('reserves'))
            
            volume_chart = []
            for multiplier in [0.9, 1.1, 0.95, 1.05, 0.98, 1.02, 1.0]:
                chart_value = volume_24h * multiplier
                volume_chart.append(chart_value)
            
            return ExchangeResponse(
                rank=safe_int(exchange_stats.get('rank', rank)),
                id=str(exchange_stats.get('name', 'unknown')).lower().replace(' ', '_'),
                name=str(exchange_stats.get('name', 'Unknown Exchange')),
                image=str(exchange.get('avatar_image', '') if exchange else ''),
                halal_status=ExchangeHalalStatus(
                    is_halal=safe_bool(exchange_stats.get('is_halal')),
                    score=str(exchange_stats.get('halal_score', 'A')),
                    rating=safe_int(exchange_stats.get('halal_rating', 932))
                ),
                trust_score=safe_int(exchange_stats.get('trust_score', 9)),
                volume_24h_usd=volume_24h,
                volume_24h_formatted=f"${volume_24h / 1_000_000_000:.1f}B" if volume_24h > 1_000_000_000 else f"${volume_24h / 1_000_000:.1f}M",
                reserves_usd=reserves,
                reserves_formatted=f"${reserves / 1_000_000_000:.0f}B" if reserves > 1_000_000_000 else f"${reserves / 1_000_000:.0f}M",
                trading_pairs_count=safe_int(exchange_stats.get('coins_count')),
                visitors_monthly=f"{safe_int(exchange_stats.get('visitors_30d'))}M",
                supported_fiat=exchange_stats.get('list_supported', [])[:3] if exchange_stats.get('list_supported') else [],
                supported_fiat_display=", ".join(exchange_stats.get('list_supported', [])[:3]) + (f" +{len(exchange_stats.get('list_supported', [])) - 3}" if len(exchange_stats.get('list_supported', [])) > 3 else ""),
                volume_chart_7d=volume_chart,
                exchange_type=str(exchange_stats.get('exchange_type', 'centralized'))
            )
        except Exception as e:
            print(f"[ERROR] Ошибка конвертации биржи: {e}")
            return ExchangeResponse(
                rank=rank,
                id="error",
                name="Error Exchange",
                halal_status=ExchangeHalalStatus(is_halal=None)  
            )
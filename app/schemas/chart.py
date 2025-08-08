from pydantic import BaseModel
from typing import List, Optional, Tuple
from decimal import Decimal

class ChartDataPoint(BaseModel):
    timestamp: int
    value: float

class ChartData(BaseModel):
    prices: List[List[float]]
    market_caps: List[List[float]]
    total_volumes: List[List[float]]

class ChartStatistics(BaseModel):
    price_change_percentage: float
    highest_price: float
    lowest_price: float
    average_volume: float

class TokenChartResponse(BaseModel):
    token_id: str
    symbol: str
    name: str
    timeframe: str
    currency: str
    data: ChartData
    statistics: ChartStatistics
    updated_at: int

class PriceUpdateMessage(BaseModel):
    type: str = "price_update"
    data: dict

class PriceData(BaseModel):
    token_id: str
    symbol: str
    price: float
    price_change_24h: float
    volume_24h: float
    market_cap: float
    timestamp: int
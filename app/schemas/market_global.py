from pydantic import BaseModel
from typing import Dict, Optional

class AltSeasonData(BaseModel):
    alt_season_index: int
    status: str
    description: str
    source: str
    btc_dominance: Optional[float] = None
    eth_dominance: Optional[float] = None
    alt_dominance: Optional[float] = None

class FearGreedIndex(BaseModel):
    value: int
    value_classification: str
    timestamp: str
    time_until_update: Optional[str] = None

class MarketCapData(BaseModel):
    total_market_cap_usd: float
    total_volume_usd: float
    market_cap_change_24h_percent: float
    btc_dominance: float
    eth_dominance: float

class GlobalMarketResponse(BaseModel):
    market_cap: MarketCapData
    fear_greed_index: FearGreedIndex
    alt_season: AltSeasonData
    last_updated: str
    data_source: str
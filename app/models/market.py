from pydantic import BaseModel, Field
from typing import List, Union, Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID, uuid4
import decimal

class ExchangesStats(BaseModel):
    id: str 
    exchange_id: UUID

    name: str
    inflows_1m: List[Decimal] = Field(default=[])
    inflows_1w: List[Decimal] = Field(default=[])
    inflows_24h: List[Decimal] = Field(default=[])
    trading_volume_1m: Union[Decimal, str, None] = Field(default=None)
    trading_volume_1w: Union[Decimal, str, None] = Field(default=None)
    trading_volume_24h: Union[Decimal, str, None] = Field(default=None)
    visitors_30d: Union[int, str, None] = Field(default=None)
    reserves: Union[Decimal, str, None] = Field(default=None)
    list_supported: List[str] = Field(default=[])
    coins_count: int | None = Field(default=None)
    effective_liquidity_24h: Decimal | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)

class Exchange(BaseModel):
    id: str 

    name: str | None = Field(default=None)
    description: str | None = Field(default=None)      
    islamic_account: str | None = Field(default=None)          
    facebook: str | None = Field(default=None)   
    youtube: str | None = Field(default=None)  
    instagram: str | None = Field(default=None)    
    medium: str | None = Field(default=None) 
    discord: str | None = Field(default=None)  
    website: str | None = Field(default=None)  
    twitter: str | None = Field(default=None)  
    reddit: str | None = Field(default=None) 
    repo_link: str | None = Field(default=None)    
    avatar_image: str | None = Field(default=None)       
    native_token_symbol: str | None = Field(default=None)              

    trading_pairs_count: int | None = Field(default=None)

    security_audits: List[UUID] = Field(default=[])
    related_people: List[UUID] = Field(default=[])

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)

class TokenStats(BaseModel):
    id: str 
    symbol: str

    coin_name: str
    coingecko_id: str
    market_cap: Union[Decimal, str, None] = Field(default=None)
    trading_volume_24h: Union[Decimal, str, None] = Field(default=None)
    token_max_supply: Union[int, str, None] = Field(default=None)
    token_total_supply: Union[int, str, None] = Field(default=None)
    transactions_count_30d: Union[int, str, None] = Field(default=None)
    volume_1m_change_1m: Union[int, str, None] = Field(default=None)
    volume_24h_change_24h: Union[Decimal, str, None] = Field(default=None)
    price: Union[Decimal, str, None] = Field(default=None)
    ath: Union[Decimal, str, None] = Field(default=None)
    atl: Union[Decimal, str, None] = Field(default=None)
    liquidity_score: Union[Decimal, str, None] = Field(default=None)
    tvl: Union[Decimal, str, None] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)

class Token(BaseModel):
    id: str 

    coingecko_id: str | None = Field(default=None)

    exchanges: List[UUID] = Field(default=[])
    security_audits: List[UUID] = Field(default=[])
    related_people: List[UUID] = Field(default=[])

    name: str | None = Field(default=None)
    symbol: str | None = Field(default=None)
    description: str | None = Field(default=None)
    instagram: str | None = Field(default=None)
    discord: str | None = Field(default=None)
    website: str | None = Field(default=None)
    facebook: str | None = Field(default=None)
    reddit: str | None = Field(default=None)
    twitter: str | None = Field(default=None)
    repo_link: str | None = Field(default=None)
    whitelabel_link: str | None = Field(default=None)
    tvl: decimal.Decimal | None = Field(default=None)

    avatar_image: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.services.market.market_service import market_service
from app.schemas.market import TokenListResponse, TokenDetailResponse, TokenDataConverter
from app.services.market.coingecko_service import coingecko_service
from app.core.database.connector import get_generic_repository

router = APIRouter()

@router.get("/", response_model=TokenListResponse)
async def get_tokens_list(
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    limit: int = Query(default=100, ge=1, le=250, description="Элементов на странице"),
    sort: Optional[str] = Query(default=None, description="Поле для сортировки")
):
    try:
        if sort and sort not in ["market_cap", "volume"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверное поле сортировки. Доступные: market_cap, volume"
            )
        
        result = market_service.get_tokens_list(page=page, limit=limit, sort=sort)
        return result
        
    except Exception as e:
        print(f"[ERROR][Market] - Ошибка получения списка токенов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения списка токенов"
        )

@router.get("/search", response_model=TokenListResponse)
async def search_tokens(
    q: str = Query(..., min_length=1, description="Название или символ токена"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество результатов")
):
    try:
        tokens_repo = get_generic_repository("LiberandumAggregationToken")
        token_stats_repo = get_generic_repository("LiberandumAggregationTokenStats")
        
        all_tokens = tokens_repo.list_all(limit=500)
        all_token_stats = token_stats_repo.list_all(limit=500)
        
        stats_by_symbol = {}
        for stat in all_token_stats:
            if not stat.get('is_deleted', False):
                symbol = stat.get('symbol', '').upper()
                if symbol:
                    stats_by_symbol[symbol] = stat
        
        query_lower = q.lower().strip()
        results = []
        
        for token in all_tokens:
            if token.get('is_deleted', False):
                continue
                
            name = token.get('name', '').lower()
            symbol = token.get('symbol', '').lower()
            coingecko_id = token.get('coingecko_id', '').lower()
            
            if (query_lower in name or 
                query_lower in symbol or 
                query_lower in coingecko_id or
                symbol == query_lower or
                name.startswith(query_lower)):
                
                token_symbol = token.get('symbol', '').upper()
                token_stats = stats_by_symbol.get(token_symbol)
                
                if token_stats:
                    token_response = TokenDataConverter.from_db_to_api(token_stats, token)
                    results.append(token_response)
            
            if len(results) >= limit:
                break
        
        return TokenListResponse(
            data=results,
            pagination={
                "current_page": 1,
                "total_pages": 1,
                "total_items": len(results),
                "items_per_page": limit
            }
        )
        
    except Exception as e:
        print(f"[ERROR][Market] - Ошибка поиска токенов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка поиска токенов"
        )

@router.get("/{token_id}", response_model=TokenDetailResponse)
async def get_token_detail(token_id: str):
    try:
        result = market_service.get_token_detail(token_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Токен не найден"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR][Market] - Ошибка получения токена {token_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения информации о токене"
        )

@router.get("/{token_id}/chart")
async def get_token_chart(
    token_id: str,
    timeframe: str = Query(..., description="Timeframe for chart data"),
    currency: str = Query("usd", description="Currency for price data"),
):
    try:
        valid_timeframes = ["1h", "24h", "7d", "30d", "90d", "1y", "max"]
        if timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid timeframe. Valid options: {valid_timeframes}"
            )
        
        coingecko_id = _resolve_coingecko_id(token_id)
        
        chart_data = await coingecko_service.get_token_chart_data(
            token_id=coingecko_id,
            timeframe=timeframe,
            currency=currency
        )
        
        if not chart_data:
            raise HTTPException(status_code=404, detail="Token not found")
            
        return chart_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chart for token {token_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def _resolve_coingecko_id(token_id: str) -> str:
    token_stats_repo = market_service._get_repository(market_service.token_stats_table)
    
    coingecko_id = token_id.lower()
    if token_id.upper() == "BTC":
        coingecko_id = "bitcoin"
    elif token_id.upper() == "ETH":
        coingecko_id = "ethereum"
    elif token_id.lower() == "bitcoin":
        coingecko_id = "bitcoin"
    else:
        token_stats_results = token_stats_repo.find_by_field('symbol', token_id.upper())
        if token_stats_results:
            coingecko_id = token_stats_results[0].get('coingecko_id', token_id.lower())
        else:
            token_stats_results = token_stats_repo.find_by_field('coingecko_id', token_id.lower())
            if token_stats_results:
                coingecko_id = token_stats_results[0].get('coingecko_id', token_id.lower())
    
    return coingecko_id
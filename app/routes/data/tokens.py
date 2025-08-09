from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.services.market.market_service import market_service
from app.schemas.market import TokenListResponse, TokenDetailResponse, TokenFullStatsResponse, TokenDataConverter
from app.services.market.coingecko_service import coingecko_service
from app.core.database.connector import get_generic_repository

router = APIRouter()

@router.get("/", response_model=TokenListResponse)
async def get_tokens_list(
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    limit: int = Query(default=100, ge=1, le=250, description="Элементов на странице"),
    sort: Optional[str] = Query(
        default=None, 
        description="Тип сортировки: market_cap, volume, price, price_change_24h, price_change_7d, halal, layer1, stablecoin, defi, meme, category, alphabetical"
    )
):
    """    
    Доступные типы сортировки:
    - market_cap: по рыночной капитализации (по убыванию)
    - volume: по объему торгов за 24ч (по убыванию)  
    - price: по цене (по убыванию)
    - price_change_24h: по изменению цены за 24ч (по убыванию)
    - price_change_7d: по изменению цены за 7д (по убыванию)
    - halal: сначала халяльные токены, потом по market cap
    - layer1: сначала Layer 1 блокчейны, потом по market cap
    - stablecoin: сначала стейблкоины, потом по market cap
    - defi: сначала DeFi токены, потом по market cap
    - meme: сначала мем-токены, потом по market cap
    - alphabetical: по алфавиту (по символу)
    """
    try:
        valid_sorts = [
            "market_cap", "volume", "price", "price_change_24h", "price_change_7d", 
            "halal", "layer1", "stablecoin", "defi", "meme", "category", "alphabetical"
        ]
        
        if sort and sort not in valid_sorts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверное поле сортировки. Доступные: {', '.join(valid_sorts)}"
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
    limit: int = Query(default=20, ge=1, le=100, description="Количество результатов"),
    sort: Optional[str] = Query(default="market_cap", description="Тип сортировки результатов")
):
    """
    Поиск токенов по названию или символу с возможностью сортировки
    """
    try:
        tokens_repo = get_generic_repository("LiberandumAggregationToken")
        token_stats_repo = get_generic_repository("LiberandumAggregationTokenStats")
        
        all_tokens = tokens_repo.list_all(limit=500)
        all_token_stats = token_stats_repo.list_all(limit=500)
        
        unique_stats = market_service._remove_duplicates_by_symbol(all_token_stats)
        
        stats_by_symbol = {}
        for stat in unique_stats:
            if not stat.get('is_deleted', False):
                symbol = stat.get('symbol', '').upper()
                if symbol:
                    stats_by_symbol[symbol] = stat
        
        query_lower = q.lower().strip()
        matching_stats = []
        
        for stat in unique_stats:
            if stat.get('is_deleted', False):
                continue
                
            name = stat.get('coin_name', '').lower()
            symbol = stat.get('symbol', '').lower()
            coingecko_id = stat.get('coingecko_id', '').lower()
            
            if (query_lower in name or 
                query_lower in symbol or 
                query_lower in coingecko_id or
                symbol == query_lower or
                name.startswith(query_lower)):
                
                matching_stats.append(stat)
        
        sorted_stats = market_service._apply_sorting(matching_stats, sort)
        
        limited_stats = sorted_stats[:limit]
        
        tokens_by_symbol = {}
        for token in all_tokens:
            if not token.get('is_deleted', False):
                symbol = token.get('symbol', '').upper()
                if symbol:
                    tokens_by_symbol[symbol] = token
        
        results = []
        for stat in limited_stats:
            symbol = stat.get('symbol', '').upper()
            token_data = tokens_by_symbol.get(symbol)
            token_response = market_service._convert_token_stats_to_response(stat, token_data)
            results.append(token_response)
        
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

@router.get("/{token_id}/stats", response_model=TokenFullStatsResponse)
async def get_token_full_stats(token_id: str):

    try:
        result = market_service.get_token_full_stats(token_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статистика для токена '{token_id}' не найдена"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR][Market] - Ошибка получения полной статистики токена {token_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения статистики токена"
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

# @router.get("/categories/summary")
# async def get_tokens_by_categories():

#     try:
#         token_stats_repo = get_generic_repository("LiberandumAggregationTokenStats")
#         all_token_stats = token_stats_repo.list_all(limit=1000)
        
        
#         unique_stats = market_service._remove_duplicates_by_symbol(all_token_stats)
#         active_stats = [ts for ts in unique_stats if not ts.get('is_deleted', False)]
        
#         def get_token_category(token_stat):
#             symbol = str(token_stat.get('symbol', '')).upper()
#             name = str(token_stat.get('coin_name', '')).lower()
            
#             if symbol in ['USDT', 'USDC', 'DAI', 'BUSD', 'FRAX', 'TUSD', 'FDUSD']:
#                 return "stablecoin"
#             elif symbol in ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'AVAX', 'MATIC', 'DOT', 'ATOM', 'NEAR', 'FTM']:
#                 return "layer1"
#             elif 'layer' in name or 'l2' in name or symbol in ['ARB', 'OP', 'MATIC']:
#                 return "layer2"
#             elif any(word in name for word in ['defi', 'swap', 'finance', 'lending', 'protocol']):
#                 return "defi"
#             elif any(word in name for word in ['meme', 'doge', 'shib', 'pepe', 'floki']):
#                 return "meme"
#             else:
#                 return "other"
        
#         categories = {}
#         for stat in active_stats:
#             category = get_token_category(stat)
#             if category not in categories:
#                 categories[category] = []
#             categories[category].append(stat)
        
#         result = {}
#         for category, tokens in categories.items():
#             sorted_tokens = sorted(
#                 tokens, 
#                 key=lambda x: float(str(x.get('market_cap', 0) or 0).replace(',', '')), 
#                 reverse=True
#             )
            
#             top_tokens = []
#             for token in sorted_tokens[:3]:
#                 top_tokens.append({
#                     "symbol": token.get('symbol', ''),
#                     "name": token.get('coin_name', ''),
#                     "market_cap": float(str(token.get('market_cap', 0) or 0).replace(',', '')),
#                     "price": float(str(token.get('price', 0) or 0).replace(',', ''))
#                 })
            
#             result[category] = {
#                 "count": len(tokens),
#                 "total_market_cap": sum(float(str(t.get('market_cap', 0) or 0).replace(',', '')) for t in tokens),
#                 "top_tokens": top_tokens
#             }
        
#         return result
        
#     except Exception as e:
#         print(f"[ERROR][Market] - Ошибка получения сводки по категориям: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Ошибка получения сводки по категориям"
#         )

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
            unique_stats = market_service._remove_duplicates_by_symbol(token_stats_results)
            if unique_stats:
                coingecko_id = unique_stats[0].get('coingecko_id', token_id.lower())
        else:
            token_stats_results = token_stats_repo.find_by_field('coingecko_id', token_id.lower())
            if token_stats_results:
                unique_stats = market_service._remove_duplicates_by_symbol(token_stats_results)
                if unique_stats:
                    coingecko_id = unique_stats[0].get('coingecko_id', token_id.lower())
    
    return coingecko_id
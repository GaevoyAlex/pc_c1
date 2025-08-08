from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from typing import Dict, Any, Optional
from decimal import Decimal

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController
from app.core.database.connector import get_generic_repository

router = APIRouter()
controller = BaseAdminController("LiberandumAggregationToken", "token")

def safe_decimal(value, default=0):

    try:
        if value is None:
            return Decimal(str(default))
        return Decimal(str(value))
    except (ValueError, TypeError):
        return Decimal(str(default))

@router.get("/")
async def list_tokens(limit: Optional[int] = Query(default=500), current_user = Depends(get_admin_user)):
    return await controller.get_entities_list(limit, current_user)

# @router.post("/")
# async def create_token(token_data: Dict[str, Any], current_user = Depends(get_admin_user)):
#     return await controller.create_entity(token_data, current_user)

@router.get("/{token_id}")
async def get_token(token_id: str, current_user = Depends(get_admin_user)):
    return await controller.get_entity_by_id(token_id, current_user)

@router.put("/{token_id}")
async def update_token(token_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.update_entity(token_id, updates, current_user)

@router.delete("/{token_id}")
async def delete_token(token_id: str, current_user = Depends(get_admin_user)):
    return await controller.delete_entity(token_id, current_user)

@router.post("/create-from-coingecko")
async def create_token_from_coingecko(
    coingecko_id: str = Body(..., embed=True),
    current_user = Depends(get_admin_user)
):
    try:
        from app.services.admin.coingecko_search_service import coingecko_search_service
        
        tokens_repo = get_generic_repository("LiberandumAggregationToken")
        
        existing = tokens_repo.find_by_field("coingecko_id", coingecko_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Токен уже существует"
            )
        
        coin_data = await coingecko_search_service._make_request(f"/coins/{coingecko_id}")
        if not coin_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Токен не найден в CoinGecko"
            )
        
        links = coin_data.get('links', {})
        market_data = coin_data.get('market_data', {})
        
        token_data = {
            'coingecko_id': coin_data.get('id'),
            'name': coin_data.get('name'),
            'symbol': coin_data.get('symbol', '').upper(),
            'description': coin_data.get('description', {}).get('en', '')[:500] if coin_data.get('description', {}).get('en') else '',
            'avatar_image': coin_data.get('image', {}).get('large', ''),
            'website': links.get('homepage', [''])[0] if links.get('homepage') else '',
            'twitter': links.get('twitter_screen_name', ''),
            'repo_link': links.get('repos_url', {}).get('github', [''])[0] if links.get('repos_url', {}).get('github') else '',
            'import_source': 'coingecko'
        }
        
        token_stats_data = {
            'symbol': coin_data.get('symbol', '').upper(),
            'coin_name': coin_data.get('name'),
            'coingecko_id': coin_data.get('id'),
            'market_cap': safe_decimal(market_data.get('market_cap', {}).get('usd')),
            'trading_volume_24h': safe_decimal(market_data.get('total_volume', {}).get('usd')),
            'price': safe_decimal(market_data.get('current_price', {}).get('usd')),
            'ath': safe_decimal(market_data.get('ath', {}).get('usd')),
            'atl': safe_decimal(market_data.get('atl', {}).get('usd')),
            'token_max_supply': safe_decimal(market_data.get('max_supply')),
            'token_total_supply': safe_decimal(market_data.get('total_supply')),
            'price_change_24h': safe_decimal(market_data.get('price_change_percentage_24h')),
            'price_change_7d': safe_decimal(market_data.get('price_change_percentage_7d')),
            'market_cap_rank': coin_data.get('market_cap_rank'),
            'import_source': 'coingecko'
        }
        
        created_token = await controller.create_entity(token_data, current_user)
        created_stats = await BaseAdminController("LiberandumAggregationTokenStats", "Статистика").create_entity(token_stats_data, current_user)
        
        return {
            "message": "Токен создан",
            "token": created_token["entity"],
            "token_stats": created_stats["entity"]
        }
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CoinGecko service недоступен"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания: {str(e)}"
        )
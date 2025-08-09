from fastapi import APIRouter, HTTPException, status

from app.schemas.market_global import GlobalMarketResponse
from app.services.market.global_data.global_market import global_market_service
from app.services.market.global_data.market_global_service import MarketGlobalsService

router = APIRouter()

@router.get("/global", response_model=GlobalMarketResponse)
async def get_global_market_data():
    try:
        result = await global_market_service.get_global_market_data()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Глобальные данные рынка недоступны"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR][GlobalMarket] - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения глобальных данных рынка"
        )
    

# @router.get("/alt-season")
# async def debug_alt_season():
#     cmc_result = await MarketGlobalsService.get_alt_season_index
    
#     return {
#         "coinmarketcap_result": cmc_result,
#         "debug_info": "Check server logs for detailed HTML debugging output"
#     }
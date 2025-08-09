from fastapi import APIRouter

from app.routes.data.tokens import router as tokens_router
from app.routes.data.exchanges import router as exchanges_router
from app.routes.data.websocket import router as websocket_router
from app.routes.data.market_global import router as global_market_router

router = APIRouter()

router.include_router(tokens_router, prefix="/tokens",)
router.include_router(exchanges_router, prefix="/exchanges", )
router.include_router(websocket_router, tags=["WebSocket"])
router.include_router(global_market_router)

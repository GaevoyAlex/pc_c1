from fastapi import APIRouter

from app.routes.data.tokens import router as tokens_router
from app.routes.data.exchanges import router as exchanges_router
from app.routes.data.websocket import router as websocket_router

router = APIRouter()

router.include_router(tokens_router, prefix="/tokens", tags=["Tokens"])
router.include_router(exchanges_router, prefix="/exchanges", tags=["Exchanges"])
router.include_router(websocket_router, tags=["WebSocket"])

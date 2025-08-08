from fastapi import APIRouter

from app.routes.admin.admin_tokens import router as tokens_router
from app.routes.admin.admin_token_stats import router as token_stats_router
from app.routes.admin.admin_exchanges import router as exchanges_router
from app.routes.admin.admin_users import router as users_router
from app.routes.admin.admin_search import router as search_router
from app.routes.admin.admin_roadmaps import router as roadmaps_router
from app.routes.admin.admin_security_audits import router as security_audit_router
from app.routes.admin.admin_people import router as people_router
from app.routes.admin.admin_platform import router as platform_router

router = APIRouter()

router.include_router(tokens_router, prefix="/tokens", tags=["Admin Tokens"])
router.include_router(token_stats_router, prefix="/token-stats", tags=["Admin Token Stats"])
router.include_router(exchanges_router, prefix="/exchanges", tags=["Admin Exchanges"])
router.include_router(users_router, prefix="/users", tags=["Admin Users"])
router.include_router(search_router, prefix="/search", tags=["Admin Search"])
router.include_router(roadmaps_router, prefix="/roadmaps", tags=["Admin Roadmaps"])
router.include_router(security_audit_router, prefix="/security-audit", tags=["Admin Security Audit"])
router.include_router(people_router, prefix="/people", tags=["Admin People"])
router.include_router(platform_router, prefix="/platform", tags=["Admin Platform"])
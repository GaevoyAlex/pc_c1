from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController

router = APIRouter()
controller = BaseAdminController("LiberandumAggregationTokenStats", "token-stats")

@router.post("/")
async def create_token_stats(stats_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.create_entity(stats_data, current_user)

@router.get("/")
async def list_token_stats(limit: Optional[int] = Query(default=500), current_user = Depends(get_admin_user)):
    return await controller.get_entities_list(limit, current_user)

@router.get("/{stats_id}")
async def get_token_stats(stats_id: str, current_user = Depends(get_admin_user)):
    return await controller.get_entity_by_id(stats_id, current_user)

@router.put("/{stats_id}")
async def update_token_stats(stats_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.update_entity(stats_id, updates, current_user)

@router.delete("/{stats_id}")
async def delete_token_stats(stats_id: str, current_user = Depends(get_admin_user)):
    return await controller.delete_entity(stats_id, current_user)
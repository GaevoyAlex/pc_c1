from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController

router = APIRouter()
controller = BaseAdminController("LiberandumAggregationTokenPlatform", "platform")

@router.post("/")
async def create_platform(platform_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.create_entity(platform_data, current_user)

@router.get("/")
async def list_platforms(limit: Optional[int] = Query(default=100), current_user = Depends(get_admin_user)):
    return await controller.get_entities_list(limit, current_user)

@router.get("/{platform_id}")
async def get_platform(platform_id: str, current_user = Depends(get_admin_user)):
    return await controller.get_entity_by_id(platform_id, current_user)

@router.put("/{platform_id}")
async def update_platform(platform_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.update_entity(platform_id, updates, current_user)

@router.delete("/{platform_id}")
async def delete_platform(platform_id: str, current_user = Depends(get_admin_user)):
    return await controller.delete_entity(platform_id, current_user)
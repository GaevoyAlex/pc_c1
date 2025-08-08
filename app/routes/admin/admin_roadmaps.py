from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController

router = APIRouter()
controller = BaseAdminController("LiberandumAggregationRoadMaps", "roadmap")

@router.post("/")
async def create_roadmap(roadmap_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.create_entity(roadmap_data, current_user)

@router.get("/")
async def list_roadmaps(limit: Optional[int] = Query(default=100), current_user = Depends(get_admin_user)):
    return await controller.get_entities_list(limit, current_user)

@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str, current_user = Depends(get_admin_user)):
    return await controller.get_entity_by_id(roadmap_id, current_user)

@router.put("/{roadmap_id}")
async def update_roadmap(roadmap_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.update_entity(roadmap_id, updates, current_user)

@router.delete("/{roadmap_id}")
async def delete_roadmap(roadmap_id: str, current_user = Depends(get_admin_user)):
    return await controller.delete_entity(roadmap_id, current_user)
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController

router = APIRouter()
controller = BaseAdminController("LiberandumAggregationPeople", "people")

@router.post("/")
async def create_person(person_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.create_entity(person_data, current_user)

@router.get("/")
async def list_people(limit: Optional[int] = Query(default=100), current_user = Depends(get_admin_user)):
    return await controller.get_entities_list(limit, current_user)

@router.get("/{person_id}")
async def get_person(person_id: str, current_user = Depends(get_admin_user)):
    return await controller.get_entity_by_id(person_id, current_user)

@router.put("/{person_id}")
async def update_person(person_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.update_entity(person_id, updates, current_user)

@router.delete("/{person_id}")
async def delete_person(person_id: str, current_user = Depends(get_admin_user)):
    return await controller.delete_entity(person_id, current_user)
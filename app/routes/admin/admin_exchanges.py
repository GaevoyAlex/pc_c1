from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController

router = APIRouter()
exchanges_controller = BaseAdminController("LiberandumAggregationExchanges", "exchange")
exchange_stats_controller = BaseAdminController("LiberandumAggregationExchangesStats", "exchange-stats")

@router.post("/")
async def create_exchange(exchange_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await exchanges_controller.create_entity(exchange_data, current_user)

@router.get("/")
async def list_exchanges(limit: Optional[int] = Query(default=250), current_user = Depends(get_admin_user)):
    return await exchanges_controller.get_entities_list(limit, current_user)

@router.get("/{exchange_id}")
async def get_exchange(exchange_id: str, current_user = Depends(get_admin_user)):
    return await exchanges_controller.get_entity_by_id(exchange_id, current_user)

@router.put("/{exchange_id}")
async def update_exchange(exchange_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await exchanges_controller.update_entity(exchange_id, updates, current_user)

@router.delete("/{exchange_id}")
async def delete_exchange(exchange_id: str, current_user = Depends(get_admin_user)):
    return await exchanges_controller.delete_entity(exchange_id, current_user)

@router.post("/stats")
async def create_exchange_stats(stats_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await exchange_stats_controller.create_entity(stats_data, current_user)

@router.get("/stats")
async def list_exchange_stats(limit: Optional[int] = Query(default=50), current_user = Depends(get_admin_user)):
    return await exchange_stats_controller.get_entities_list(limit, current_user)

@router.get("/stats/{stats_id}")
async def get_exchange_stats(stats_id: str, current_user = Depends(get_admin_user)):
    return await exchange_stats_controller.get_entity_by_id(stats_id, current_user)

@router.put("/stats/{stats_id}")
async def update_exchange_stats(stats_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await exchange_stats_controller.update_entity(stats_id, updates, current_user)

@router.delete("/stats/{stats_id}")
async def delete_exchange_stats(stats_id: str, current_user = Depends(get_admin_user)):
    return await exchange_stats_controller.delete_entity(stats_id, current_user)
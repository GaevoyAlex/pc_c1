from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional

from app.core.security.security import get_admin_user
from app.routes.admin.admin_controller import BaseAdminController

router = APIRouter()
controller = BaseAdminController("LiberandumAggregationSecurityAudit", "audit")

@router.post("/")
async def create_security_audit(audit_data: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.create_entity(audit_data, current_user)

@router.get("/")
async def list_security_audits(limit: Optional[int] = Query(default=100), current_user = Depends(get_admin_user)):
    return await controller.get_entities_list(limit, current_user)

@router.get("/{audit_id}")
async def get_security_audit(audit_id: str, current_user = Depends(get_admin_user)):
    return await controller.get_entity_by_id(audit_id, current_user)

@router.put("/{audit_id}")
async def update_security_audit(audit_id: str, updates: Dict[str, Any], current_user = Depends(get_admin_user)):
    return await controller.update_entity(audit_id, updates, current_user)

@router.delete("/{audit_id}")
async def delete_security_audit(audit_id: str, current_user = Depends(get_admin_user)):
    return await controller.delete_entity(audit_id, current_user)
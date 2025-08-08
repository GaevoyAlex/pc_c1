from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
import uuid

from app.core.security.permissions import require_admin
from app.core.database.connector import get_generic_repository
from app.core.security.security import get_admin_user

class BaseAdminController:
    def __init__(self, table_name: str, entity_name: str):
        self.table_name = table_name
        self.entity_name = entity_name
    
    def _get_repository(self):
        return get_generic_repository(self.table_name)
    
    def _add_audit_fields(self, data: Dict[str, Any], admin_id: str, action: str) -> Dict[str, Any]:
        timestamp = datetime.now().isoformat()
        
        if action == "create":
            data.update({
                'id': str(uuid.uuid4()),
                'created_at': timestamp,
                'updated_at': timestamp,
                'is_deleted': False,
                'created_by_admin': admin_id
            })
        elif action == "update":
            data.update({
                'updated_at': timestamp,
                'updated_by_admin': admin_id
            })
        elif action == "delete":
            data.update({
                'is_deleted': True,
                'deleted_at': timestamp,
                'deleted_by_admin': admin_id
            })
        
        return data
    
    async def create_entity(self, entity_data: Dict[str, Any], current_user: Dict[str, Any]):
        try:
            repo = self._get_repository()
            
            entity_data = self._add_audit_fields(entity_data, current_user['id'], "create")
            created_entity = repo.create(entity_data, auto_id=False)
            
            return {
                "message": f"{self.entity_name} создан",
                "entity": created_entity,
                "admin": current_user['email']
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Ошибка создания {self.entity_name.lower()}: {str(e)}"
            )
    
    async def get_entities_list(self, limit: Optional[int], current_user: Dict[str, Any]):
        try:
            repo = self._get_repository()
            items = repo.scan_items(self.table_name, limit=limit)
            active_items = [item for item in items if not item.get('is_deleted', False)]
            
            return {
                "total": len(active_items),
                f"{self.entity_name.lower()}s": active_items,
                "admin": current_user['email']
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Ошибка получения списка {self.entity_name.lower()}: {str(e)}"
            )
    
    async def get_entity_by_id(self, entity_id: str, current_user: Dict[str, Any]):
        try:
            repo = self._get_repository()
            entity = repo.get_by_id(entity_id)
            
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"{self.entity_name} не найден"
                )
            
            return {
                f"{self.entity_name.lower()}": entity,
                "admin": current_user['email']
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Ошибка получения {self.entity_name.lower()}: {str(e)}"
            )
    
    async def update_entity(self, entity_id: str, updates: Dict[str, Any], current_user: Dict[str, Any]):
        try:
            repo = self._get_repository()
            
            existing_entity = repo.get_by_id(entity_id)
            if not existing_entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"{self.entity_name} не найден"
                )
            
            updates = self._add_audit_fields(updates, current_user['id'], "update")
            updated_entity = repo.update_by_id(entity_id, updates)
            
            return {
                "message": f"{self.entity_name} обновлен",
                f"{self.entity_name.lower()}": updated_entity,
                "admin": current_user['email']
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Ошибка обновления {self.entity_name.lower()}: {str(e)}"
            )
    
    async def delete_entity(self, entity_id: str, current_user: Dict[str, Any]):
        try:
            repo = self._get_repository()
            
            existing_entity = repo.get_by_id(entity_id)
            if not existing_entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"{self.entity_name} не найден"
                )
            
            delete_data = self._add_audit_fields({}, current_user['id'], "delete")
            repo.update_by_id(entity_id, delete_data)
            
            return {
                "message": f"{self.entity_name} удален",
                f"{self.entity_name.lower()}_id": entity_id,
                "admin": current_user['email']
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Ошибка удаления {self.entity_name.lower()}: {str(e)}"
            )
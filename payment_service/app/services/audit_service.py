from sqlalchemy.orm import Session
from ..models import AuditLog
from typing import Dict, Any, Optional
import json

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        action: str,
        subscription_id: Optional[int] = None,
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a subscription-related event to the audit_log table.
        """
        try:
            audit_entry = AuditLog(
                subscription_id=subscription_id,
                action=action,
                user_id=user_id,
                device_id=device_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(audit_entry)
            db.commit()
            print(f"📄 Audit: {action} for user {user_id}")
        except Exception as e:
            db.rollback()
            print(f"❌ Failed to create audit log: {e}")

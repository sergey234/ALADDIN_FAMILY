# -*- coding: utf-8 -*-
"""
Notifications API Router
------------------------
REST-эндпоинты для мобильного приложения ALADDIN:
- Получение списка уведомлений семьи
- Пометка уведомления прочитанным
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from security.family.family_notification_manager_enhanced import (
    FamilyNotification,
    NotificationPriority,
    NotificationType,
    family_notification_manager_enhanced,
)


router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

DEFAULT_FAMILY_ID = "family_demo_001"


class NotificationItem(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор уведомления")
    icon: str = Field(..., description="Иконка (эмодзи) уведомления")
    title: str = Field(..., description="Заголовок уведомления")
    message: str = Field(..., description="Текст уведомления")
    type: str = Field(..., description="Тип уведомления")
    priority: str = Field(..., description="Приоритет уведомления")
    timestamp: datetime = Field(..., description="Время создания уведомления в ISO-8601")
    is_read: bool = Field(..., description="Признак прочитанности")
    action_required: bool = Field(..., description="Требуется ли действие")
    action_url: Optional[str] = Field(None, description="URL действия, если требуется")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные данные")


class NotificationListResponse(BaseModel):
    notifications: List[NotificationItem]
    unread_count: int


class MarkReadRequest(BaseModel):
    notification_id: str = Field(..., alias="notificationId")
    family_id: Optional[str] = Field(None, alias="familyId")


class MarkReadResponse(BaseModel):
    success: bool
    unread_count: int


def _resolve_family_id(explicit_family_id: Optional[str]) -> str:
    """Определяет ID семьи для выборки уведомлений"""
    return explicit_family_id or DEFAULT_FAMILY_ID


def _notification_icon(notification: FamilyNotification) -> str:
    """Возвращает emoji-иконку по типу уведомления"""
    mapping = {
        NotificationType.SECURITY_ALERT: "🛡️",
        NotificationType.THREAT_DETECTED: "🚨",
        NotificationType.EMERGENCY: "🚑",
        NotificationType.DAILY_REPORT: "📊",
        NotificationType.FAMILY_STATUS: "👨‍👩‍👧‍👦",
        NotificationType.PAYMENT_SUCCESS: "✅",
        NotificationType.PAYMENT_PENDING: "⌛️",
        NotificationType.PAYMENT_FAILED: "❌",
        NotificationType.QR_CODE_GENERATED: "📲",
        NotificationType.SUBSCRIPTION_ACTIVATED: "🎉",
        NotificationType.SUBSCRIPTION_EXPIRING: "⏳",
        NotificationType.SUBSCRIPTION_EXPIRED: "⚠️",
        NotificationType.REFERRAL_SIGNUP: "🤝",
        NotificationType.REFERRAL_REWARD: "🎁",
        NotificationType.TARIFF_RECOMMENDATION: "💡",
        NotificationType.SYSTEM_UPDATE: "🛠",
        NotificationType.FEATURE_ANNOUNCEMENT: "✨",
        NotificationType.PERSONALIZED_TIP: "📌",
    }
    return mapping.get(notification.notification_type, "🔔")


def _notification_priority(priority: NotificationPriority) -> str:
    """Приводит приоритет к строковому значению"""
    return priority.value if isinstance(priority, NotificationPriority) else str(priority)


def _to_response_item(notification: FamilyNotification) -> NotificationItem:
    """Формирует DTO уведомления для ответа API"""
    return NotificationItem(
        id=notification.notification_id,
        icon=_notification_icon(notification),
        title=notification.title,
        message=notification.message,
        type=notification.notification_type.value,
        priority=_notification_priority(notification.priority),
        timestamp=notification.created_at,
        is_read=notification.is_read,
        action_required=notification.action_required,
        action_url=notification.action_url,
        metadata=notification.metadata or {},
    )


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    familyId: Optional[str] = Query(None, alias="familyId"),
    limit: int = Query(50, ge=1, le=100),
    include_read: bool = Query(True, alias="includeRead"),
) -> NotificationListResponse:
    """Возвращает список уведомлений для мобильного приложения"""
    family_id = _resolve_family_id(familyId)

    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )

    if not include_read:
        all_notifications = [n for n in all_notifications if not n.is_read]

    unread_count = sum(1 for n in all_notifications if not n.is_read)

    sliced_notifications = all_notifications[:limit] if limit > 0 else all_notifications

    return NotificationListResponse(
        notifications=[_to_response_item(notification) for notification in sliced_notifications],
        unread_count=unread_count,
    )


@router.post("/read", response_model=MarkReadResponse)
async def mark_notification_read(payload: MarkReadRequest) -> MarkReadResponse:
    """Помечает уведомление как прочитанное"""
    family_id = _resolve_family_id(payload.family_id)
    success = await family_notification_manager_enhanced.mark_notification_as_read(
        family_id=family_id,
        notification_id=payload.notification_id,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")

    remaining_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    unread_count = sum(1 for notification in remaining_notifications if not notification.is_read)

    return MarkReadResponse(success=True, unread_count=unread_count)



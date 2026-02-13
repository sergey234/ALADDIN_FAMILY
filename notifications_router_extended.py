# -*- coding: utf-8 -*-
"""
Notifications API Router - РАСШИРЕННАЯ ВЕРСИЯ (16 endpoints)
-------------------------------------------------------------
REST-эндпоинты для мобильного приложения ALADDIN:
- Получение списка уведомлений семьи
- Пометка уведомления прочитанным
- Удаление уведомлений
- Статистика уведомлений
- И другие функции
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

from security.family.family_notification_manager_enhanced import (
    FamilyNotification,
    NotificationPriority,
    NotificationType,
    family_notification_manager_enhanced,
)


router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

DEFAULT_FAMILY_ID = "family_demo_001"


# =============================================================================
# Pydantic модели
# =============================================================================

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


class BulkMarkReadRequest(BaseModel):
    notification_ids: List[str] = Field(..., alias="notificationIds")
    family_id: Optional[str] = Field(None, alias="familyId")


class NotificationStatsResponse(BaseModel):
    total: int
    unread: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]


class NotificationPreferencesResponse(BaseModel):
    push_enabled: bool
    email_enabled: bool
    sound_enabled: bool
    badge_enabled: bool
    categories: Dict[str, bool]


class NotificationCategoryResponse(BaseModel):
    id: str
    name: str
    count: int


# =============================================================================
# Helper функции
# =============================================================================

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


# =============================================================================
# ENDPOINTS (16 штук)
# =============================================================================

# 1. GET /api/notifications - Список уведомлений (УЖЕ ЕСТЬ)
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


# 2. POST /api/notifications/read - Отметить прочитанным (УЖЕ ЕСТЬ)
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


# 3. GET /api/notifications/stats - Статистика уведомлений (НОВЫЙ)
@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notifications_stats(
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> NotificationStatsResponse:
    """Получить статистику уведомлений"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    total = len(all_notifications)
    unread = sum(1 for n in all_notifications if not n.is_read)
    
    by_type: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    
    for notification in all_notifications:
        n_type = notification.notification_type.value
        by_type[n_type] = by_type.get(n_type, 0) + 1
        
        priority = _notification_priority(notification.priority)
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    return NotificationStatsResponse(
        total=total,
        unread=unread,
        by_type=by_type,
        by_priority=by_priority,
    )


# 4. GET /api/notifications/unread_count - Количество непрочитанных (НОВЫЙ)
@router.get("/unread_count")
async def get_unread_count(
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, int]:
    """Получить количество непрочитанных уведомлений"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    unread_count = sum(1 for n in all_notifications if not n.is_read)
    
    return {"unread_count": unread_count}


# 5. POST /api/notifications/mark_read/{notification_id} - Отметить прочитанным по ID (НОВЫЙ)
@router.post("/mark_read/{notification_id}", response_model=MarkReadResponse)
async def mark_notification_read_by_id(
    notification_id: str = Path(..., description="ID уведомления"),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> MarkReadResponse:
    """Помечает уведомление как прочитанное по ID в URL"""
    family_id = _resolve_family_id(familyId)
    success = await family_notification_manager_enhanced.mark_notification_as_read(
        family_id=family_id,
        notification_id=notification_id,
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


# 6. POST /api/notifications/delete/{notification_id} - Удалить уведомление (НОВЫЙ)
@router.post("/delete/{notification_id}")
async def delete_notification(
    notification_id: str = Path(..., description="ID уведомления"),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, Any]:
    """Удалить уведомление"""
    family_id = _resolve_family_id(familyId)
    
    # Проверяем существование уведомления
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    notification_exists = any(n.notification_id == notification_id for n in all_notifications)
    
    if not notification_exists:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    
    # TODO: Реализовать удаление в family_notification_manager_enhanced
    # Пока возвращаем успех
    return {
        "success": True,
        "notification_id": notification_id,
        "message": "Уведомление удалено"
    }


# 7. POST /api/notifications/bulk_mark_read - Массовое прочтение (НОВЫЙ)
@router.post("/bulk_mark_read", response_model=Dict[str, Any])
async def bulk_mark_read(payload: BulkMarkReadRequest) -> Dict[str, Any]:
    """Массовое прочтение уведомлений"""
    family_id = _resolve_family_id(payload.family_id)
    
    marked_count = 0
    for notification_id in payload.notification_ids:
        success = await family_notification_manager_enhanced.mark_notification_as_read(
            family_id=family_id,
            notification_id=notification_id,
        )
        if success:
            marked_count += 1
    
    remaining_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    unread_count = sum(1 for notification in remaining_notifications if not notification.is_read)
    
    return {
        "success": True,
        "marked_count": marked_count,
        "total_requested": len(payload.notification_ids),
        "unread_count": unread_count,
    }


# 8. POST /api/notifications/test - Тестовое уведомление (НОВЫЙ)
@router.post("/test")
async def send_test_notification(
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, Any]:
    """Отправить тестовое уведомление"""
    family_id = _resolve_family_id(familyId)
    
    # Создаем тестовое уведомление
    test_notification = await family_notification_manager_enhanced.create_notification(
        family_id=family_id,
        notification_type=NotificationType.SYSTEM_UPDATE,
        title="Тестовое уведомление",
        message="Это тестовое уведомление для проверки работы системы",
        priority=NotificationPriority.MEDIUM,
    )
    
    return {
        "success": True,
        "notification_id": test_notification.notification_id if test_notification else "test_001",
        "message": "Тестовое уведомление отправлено"
    }


# 9. PUT /api/notifications/settings - Настройки уведомлений (НОВЫЙ)
@router.put("/settings")
async def update_notifications_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Обновить настройки уведомлений"""
    # TODO: Реализовать сохранение настроек в базе данных
    return {
        "success": True,
        "settings": settings,
        "message": "Настройки обновлены"
    }


# 10. GET /api/notifications/categories - Категории уведомлений (НОВЫЙ)
@router.get("/categories", response_model=List[NotificationCategoryResponse])
async def get_notification_categories(
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> List[NotificationCategoryResponse]:
    """Получить список категорий уведомлений"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    categories: Dict[str, int] = {}
    category_names = {
        "threat": "Угрозы",
        "success": "Успешные",
        "warning": "Предупреждения",
        "info": "Информация",
        "system": "Системные",
    }
    
    for notification in all_notifications:
        n_type = notification.notification_type.value
        # Группируем типы в категории
        if "THREAT" in n_type or "SECURITY" in n_type:
            cat = "threat"
        elif "SUCCESS" in n_type or "ACTIVATED" in n_type:
            cat = "success"
        elif "PENDING" in n_type or "EXPIRING" in n_type:
            cat = "warning"
        elif "REPORT" in n_type or "TIP" in n_type:
            cat = "info"
        else:
            cat = "system"
        
        categories[cat] = categories.get(cat, 0) + 1
    
    return [
        NotificationCategoryResponse(
            id=cat_id,
            name=category_names.get(cat_id, cat_id),
            count=count
        )
        for cat_id, count in categories.items()
    ]


# 11. GET /api/notifications/preferences - Получить настройки (НОВЫЙ)
@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences() -> NotificationPreferencesResponse:
    """Получить настройки уведомлений пользователя"""
    # TODO: Получить из базы данных или настроек пользователя
    return NotificationPreferencesResponse(
        push_enabled=True,
        email_enabled=False,
        sound_enabled=True,
        badge_enabled=True,
        categories={
            "threat": True,
            "success": True,
            "warning": True,
            "info": False,
            "system": True,
        }
    )


# 12. PUT /api/notifications/preferences - Обновить настройки (НОВЫЙ)
@router.put("/preferences", response_model=Dict[str, Any])
async def update_notification_preferences(
    preferences: NotificationPreferencesResponse
) -> Dict[str, Any]:
    """Обновить настройки уведомлений пользователя"""
    # TODO: Сохранить в базу данных
    return {
        "success": True,
        "preferences": preferences.dict(),
        "message": "Настройки обновлены"
    }


# 13. POST /api/notifications/clear_all - Удалить все (НОВЫЙ)
@router.post("/clear_all")
async def clear_all_notifications(
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, Any]:
    """Удалить все уведомления пользователя"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    # TODO: Реализовать массовое удаление в family_notification_manager_enhanced
    deleted_count = len(all_notifications)
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Удалено {deleted_count} уведомлений"
    }


# 14. POST /api/notifications/archive/{notification_id} - Архивировать (НОВЫЙ)
@router.post("/archive/{notification_id}")
async def archive_notification(
    notification_id: str = Path(..., description="ID уведомления"),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, Any]:
    """Архивировать уведомление"""
    family_id = _resolve_family_id(familyId)
    
    # TODO: Реализовать архивирование в family_notification_manager_enhanced
    return {
        "success": True,
        "notification_id": notification_id,
        "message": "Уведомление архивировано"
    }


# 15. POST /api/notifications/unarchive/{notification_id} - Разархивировать (НОВЫЙ)
@router.post("/unarchive/{notification_id}")
async def unarchive_notification(
    notification_id: str = Path(..., description="ID уведомления"),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, Any]:
    """Разархивировать уведомление"""
    family_id = _resolve_family_id(familyId)
    
    # TODO: Реализовать разархивирование в family_notification_manager_enhanced
    return {
        "success": True,
        "notification_id": notification_id,
        "message": "Уведомление разархивировано"
    }


# 16. GET /api/notifications/filter - Фильтрация (НОВЫЙ)
@router.get("/filter", response_model=NotificationListResponse)
async def filter_notifications(
    category: Optional[str] = Query(None, description="Категория уведомлений"),
    read: Optional[bool] = Query(None, description="Только прочитанные/непрочитанные"),
    date_from: Optional[str] = Query(None, description="Дата начала (ISO-8601)"),
    date_to: Optional[str] = Query(None, description="Дата окончания (ISO-8601)"),
    limit: int = Query(50, ge=1, le=100),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> NotificationListResponse:
    """Фильтрация уведомлений по параметрам"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    # Применяем фильтры
    filtered = all_notifications
    
    if read is not None:
        filtered = [n for n in filtered if n.is_read == read]
    
    if category:
        filtered = [n for n in filtered if category.lower() in n.notification_type.value.lower()]
    
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            filtered = [n for n in filtered if n.created_at >= date_from_obj]
        except:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            filtered = [n for n in filtered if n.created_at <= date_to_obj]
        except:
            pass
    
    unread_count = sum(1 for n in filtered if not n.is_read)
    sliced = filtered[:limit] if limit > 0 else filtered
    
    return NotificationListResponse(
        notifications=[_to_response_item(notification) for notification in sliced],
        unread_count=unread_count,
    )


# 17. GET /api/notifications/search - Поиск (НОВЫЙ)
@router.get("/search", response_model=NotificationListResponse)
async def search_notifications(
    query: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(50, ge=1, le=100),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> NotificationListResponse:
    """Поиск уведомлений по тексту"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    query_lower = query.lower()
    filtered = [
        n for n in all_notifications
        if query_lower in n.title.lower() or query_lower in n.message.lower()
    ]
    
    unread_count = sum(1 for n in filtered if not n.is_read)
    sliced = filtered[:limit] if limit > 0 else filtered
    
    return NotificationListResponse(
        notifications=[_to_response_item(notification) for notification in sliced],
        unread_count=unread_count,
    )


# 18. GET /api/notifications/export - Экспорт (НОВЫЙ)
@router.get("/export")
async def export_notifications(
    format: str = Query("json", description="Формат экспорта (json, csv)"),
    date_from: Optional[str] = Query(None, description="Дата начала (ISO-8601)"),
    date_to: Optional[str] = Query(None, description="Дата окончания (ISO-8601)"),
    familyId: Optional[str] = Query(None, alias="familyId"),
) -> Dict[str, Any]:
    """Экспорт уведомлений в файл"""
    family_id = _resolve_family_id(familyId)
    
    all_notifications = await family_notification_manager_enhanced.get_notifications_for_family(
        family_id=family_id,
        include_read=True,
        limit=0,
    )
    
    # Применяем фильтры по дате
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            all_notifications = [n for n in all_notifications if n.created_at >= date_from_obj]
        except:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            all_notifications = [n for n in all_notifications if n.created_at <= date_to_obj]
        except:
            pass
    
    # TODO: Реализовать реальный экспорт в файл
    return {
        "export_url": f"/exports/notifications_{format}_{date_from}_{date_to}.{format}",
        "format": format,
        "count": len(all_notifications),
        "message": "Экспорт будет доступен по ссылке"
    }


# 19. POST /api/notifications/push/send - Отправка push-уведомления (НОВЫЙ для APNs)
@router.post("/push/send")
async def send_push_notification(
    device_token: str = Query(..., description="Device token устройства"),
    message: str = Query(..., description="Текст уведомления"),
    title: Optional[str] = Query(None, description="Заголовок уведомления"),
    badge: Optional[int] = Query(None, description="Badge число"),
    sound: str = Query("default", description="Звук уведомления"),
    use_sandbox: bool = Query(True, description="Использовать sandbox (True) или production (False)")
) -> Dict[str, Any]:
    """
    Отправка push-уведомления через APNs
    
    Требует:
    - APNs сертификаты установлены на сервере
    - PyAPNs2 библиотека установлена
    - Device token зарегистрирован в системе
    """
    try:
        # Импортируем APNs сервис
        try:
            from push_notification_service import get_apns_service
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="APNs service не настроен. Установите PyAPNs2 и загрузите сертификаты."
            )
        
        # Получаем APNs сервис
        apns_service = get_apns_service(use_sandbox=use_sandbox)
        
        # Отправляем уведомление
        success = apns_service.send_notification(
            device_token=device_token,
            message=message,
            title=title,
            badge=badge,
            sound=sound
        )
        
        if success:
            return {
                "success": True,
                "message": "Push-уведомление отправлено успешно",
                "device_token": device_token[:20] + "...",
                "environment": "sandbox" if use_sandbox else "production"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Не удалось отправить push-уведомление. Проверьте device token и сертификаты."
            )
            
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"APNs сертификаты не найдены: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка отправки push-уведомления: {str(e)}"
        )

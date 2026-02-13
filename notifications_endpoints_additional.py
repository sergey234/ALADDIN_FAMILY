# =============================================================================
# NOTIFICATIONS - ДОПОЛНИТЕЛЬНЫЕ 8 ENDPOINTS (для полного набора из 16)
# =============================================================================

@app.get("/api/notifications/categories")
async def get_notification_categories():
    """Получить список категорий уведомлений"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notification_categories", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "categories": [
                {"id": "threat", "name": "Угрозы", "count": 0},
                {"id": "success", "name": "Успешные", "count": 0},
                {"id": "warning", "name": "Предупреждения", "count": 0},
                {"id": "info", "name": "Информация", "count": 0},
                {"id": "system", "name": "Системные", "count": 0}
            ],
            "source": "mock"
        }

@app.get("/api/notifications/preferences")
async def get_notification_preferences():
    """Получить настройки уведомлений пользователя"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_notification_preferences", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "preferences": {
                "push_enabled": True,
                "email_enabled": False,
                "sound_enabled": True,
                "badge_enabled": True,
                "categories": {
                    "threat": True,
                    "success": True,
                    "warning": True,
                    "info": False,
                    "system": True
                }
            },
            "source": "mock"
        }

@app.put("/api/notifications/preferences")
async def update_notification_preferences(data: dict):
    """Обновить настройки уведомлений пользователя"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("update_notification_preferences", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "success": True,
            "preferences": data.get("preferences", {}),
            "source": "mock"
        }

@app.post("/api/notifications/clear_all")
async def clear_all_notifications():
    """Удалить все уведомления пользователя"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("clear_all_notifications", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "action": "clear_all",
            "deleted_count": 0,
            "source": "mock"
        }

@app.post("/api/notifications/archive/{notification_id}")
async def archive_notification(notification_id: str):
    """Архивировать уведомление"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("archive_notification", {"notification_id": notification_id})
        return result if success else {"error": message, "notification_id": notification_id, "source": "mock"}
    else:
        return {
            "action": "archive",
            "notification_id": notification_id,
            "source": "mock"
        }

@app.post("/api/notifications/unarchive/{notification_id}")
async def unarchive_notification(notification_id: str):
    """Разархивировать уведомление"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("unarchive_notification", {"notification_id": notification_id})
        return result if success else {"error": message, "notification_id": notification_id, "source": "mock"}
    else:
        return {
            "action": "unarchive",
            "notification_id": notification_id,
            "source": "mock"
        }

@app.get("/api/notifications/filter")
async def filter_notifications(
    category: str = None,
    read: bool = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 50
):
    """Фильтрация уведомлений по параметрам"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {
            "category": category,
            "read": read,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit
        }
        success, result, message = sfm_adapter.execute_function("filter_notifications", params)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "notifications": [],
            "filters": {
                "category": category,
                "read": read,
                "date_from": date_from,
                "date_to": date_to
            },
            "limit": limit,
            "source": "mock"
        }

@app.get("/api/notifications/search")
async def search_notifications(query: str, limit: int = 50):
    """Поиск уведомлений по тексту"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("search_notifications", {"query": query, "limit": limit})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "notifications": [],
            "query": query,
            "limit": limit,
            "source": "mock"
        }

@app.get("/api/notifications/export")
async def export_notifications(format: str = "json", date_from: str = None, date_to: str = None):
    """Экспорт уведомлений в файл"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {
            "format": format,
            "date_from": date_from,
            "date_to": date_to
        }
        success, result, message = sfm_adapter.execute_function("export_notifications", params)
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "export_url": f"/exports/notifications_{format}_{date_from}_{date_to}.{format}",
            "format": format,
            "source": "mock"
        }

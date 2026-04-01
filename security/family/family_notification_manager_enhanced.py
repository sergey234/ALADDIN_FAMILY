#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bridge‑module for FamilyNotificationManagerEnhanced.

Продакшен‑рантайм импортирует менеджер уведомлений как:

    from security.family.family_notification_manager_enhanced import ...

Оригинальная реализация находится в пакете `app.security.family`.
Чтобы сохранить совместимость со старыми импортами и не дублировать код,
этот модуль просто ре‑экспортирует публичные объекты из оригинального файла.
"""

from app.security.family.family_notification_manager_enhanced import (  # type: ignore[import]
    FamilyNotification,
    FamilyNotificationManagerEnhanced,
    NotificationChannel,
    NotificationPriority,
    NotificationResult,
    NotificationTemplate,
    NotificationType,
)

# Глобальный singleton, совместимый с тем, как его ожидает notifications_router
family_notification_manager_enhanced = FamilyNotificationManagerEnhanced()


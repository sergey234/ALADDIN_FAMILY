# -*- coding: utf-8 -*-
"""
APNs Push Notification Service для ALADDIN
Отправка push-уведомлений через Apple Push Notification service
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from apns2.client import APNsClient
    from apns2.payload import Payload
    from apns2.credentials import TokenCredentials
    APNS_AVAILABLE = True
except ImportError:
    APNS_AVAILABLE = False
    print("⚠️ PyAPNs2 не установлен. Установите: pip install PyAPNs2")


class APNsService:
    """
    Сервис для отправки push-уведомлений через APNs
    """
    
    def __init__(self, use_sandbox: bool = True):
        """
        Инициализация APNs сервиса
        
        Args:
            use_sandbox: True для development/sandbox, False для production
        """
        if not APNS_AVAILABLE:
            raise ImportError("PyAPNs2 не установлен. Установите: pip install PyAPNs2")
        
        self.use_sandbox = use_sandbox
        self.topic = "family.aladdin.ios"
        
        # Пути к сертификатам
        cert_dir = Path("/opt/aladdin-backend/certificates")
        if use_sandbox:
            cert_path = cert_dir / "apns_development.pem"
            self.host = "api.sandbox.push.apple.com"
        else:
            cert_path = cert_dir / "apns_production.pem"
            self.host = "api.push.apple.com"
        
        # Проверка существования сертификата
        if not cert_path.exists():
            raise FileNotFoundError(
                f"APNs certificate not found: {cert_path}\n"
                f"Пожалуйста, загрузите сертификат на сервер в директорию: {cert_dir}"
            )
        
        # Создание клиента APNs
        try:
            # Используем TokenCredentials для работы с .pem файлами
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            # PyAPNs2 требует разделение сертификата и ключа
            # Если .pem содержит оба - нужно разделить
            # Для упрощения используем прямую загрузку
            self.client = APNsClient(
                credentials=TokenCredentials.from_file(str(cert_path)),
                use_sandbox=use_sandbox
            )
            
            print(f"✅ APNs Service initialized: {'Sandbox' if use_sandbox else 'Production'}")
        except Exception as e:
            print(f"❌ Error initializing APNs client: {e}")
            raise
    
    def send_notification(
        self,
        device_token: str,
        message: str,
        title: Optional[str] = None,
        badge: Optional[int] = None,
        sound: str = "default",
        custom_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Отправка push-уведомления
        
        Args:
            device_token: Device token устройства (hex строка, без пробелов)
            message: Текст уведомления
            title: Заголовок уведомления (опционально)
            badge: Число для badge (опционально)
            sound: Звук уведомления (по умолчанию "default")
            custom_data: Дополнительные данные для приложения
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            # Очистка device token (удаление пробелов и приведение к нижнему регистру)
            device_token = device_token.replace(" ", "").lower()
            
            # Создание payload
            alert = message
            if title:
                alert = {"title": title, "body": message}
            
            payload_dict = {
                "aps": {
                    "alert": alert,
                    "sound": sound
                }
            }
            
            if badge is not None:
                payload_dict["aps"]["badge"] = badge
            
            if custom_data:
                payload_dict.update(custom_data)
            
            payload = Payload(**payload_dict["aps"], custom=custom_data or {})
            
            # Отправка уведомления
            response = self.client.send_notification(
                device_token=device_token,
                payload=payload,
                topic=self.topic
            )
            
            if response.status == "success":
                print(f"✅ Push notification sent successfully to {device_token[:20]}...")
                return True
            else:
                print(f"❌ Push notification failed: {response.reason}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending push notification: {e}")
            return False
    
    def send_custom_notification(
        self,
        device_token: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Отправка кастомного push-уведомления с дополнительными данными
        
        Args:
            device_token: Device token устройства
            data: Словарь с данными уведомления
                {
                    "alert": "Текст уведомления",
                    "title": "Заголовок",
                    "badge": 1,
                    "sound": "default",
                    "custom_data": {...}
                }
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        return self.send_notification(
            device_token=device_token,
            message=data.get("alert", ""),
            title=data.get("title"),
            badge=data.get("badge"),
            sound=data.get("sound", "default"),
            custom_data=data.get("custom_data", {})
        )
    
    def test_connection(self) -> bool:
        """
        Тестирование подключения к APNs
        
        Returns:
            bool: True если подключение успешно
        """
        try:
            # Пробуем отправить тестовое уведомление на несуществующий токен
            # Это не должно работать, но проверит подключение
            test_token = "0" * 64  # Невалидный токен
            payload = Payload(alert="Test", sound="default")
            
            response = self.client.send_notification(
                device_token=test_token,
                payload=payload,
                topic=self.topic
            )
            
            # Если получили ответ (даже ошибку) - подключение работает
            return True
        except Exception as e:
            print(f"❌ APNs connection test failed: {e}")
            return False


# Singleton instances
_apns_service_dev = None
_apns_service_prod = None


def get_apns_service(use_sandbox: bool = True) -> APNsService:
    """
    Получить экземпляр APNs сервиса (singleton)
    
    Args:
        use_sandbox: True для development, False для production
    
    Returns:
        APNsService: Экземпляр сервиса
    """
    global _apns_service_dev, _apns_service_prod
    
    if use_sandbox:
        if _apns_service_dev is None:
            _apns_service_dev = APNsService(use_sandbox=True)
        return _apns_service_dev
    else:
        if _apns_service_prod is None:
            _apns_service_prod = APNsService(use_sandbox=False)
        return _apns_service_prod


# Для обратной совместимости
def send_push_notification(
    device_token: str,
    message: str,
    title: Optional[str] = None,
    badge: Optional[int] = None,
    use_sandbox: bool = True
) -> bool:
    """
    Удобная функция для отправки push-уведомления
    
    Args:
        device_token: Device token устройства
        message: Текст уведомления
        title: Заголовок (опционально)
        badge: Badge число (опционально)
        use_sandbox: True для development, False для production
    
    Returns:
        bool: True если успешно
    """
    service = get_apns_service(use_sandbox=use_sandbox)
    return service.send_notification(
        device_token=device_token,
        message=message,
        title=title,
        badge=badge
    )

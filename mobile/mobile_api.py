#!/usr/bin/env python3
"""
Мобильный API для системы безопасности ALADDIN
Обеспечивает интеграцию с мобильными приложениями
"""

import sys
import os
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
import hmac
import base64

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))


class MobileAPI:
    """Мобильный API для системы ALADDIN"""

    def __init__(self):
        self.devices = {}
        self.family_groups = {}
        self.notifications = []
        self.offline_data = {}
        self.push_tokens = {}

    def register_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Регистрация мобильного устройства"""
        try:
            device_id = device_data.get('device_id')
            device_type = device_data.get('device_type', 'unknown')
            app_version = device_data.get('app_version', '1.0.0')
            family_id = device_data.get('family_id')

            if not device_id:
                return {
                    'success': False,
                    'error': 'device_id is required'
                }

            # Создаем токен устройства
            device_token = self._generate_device_token(device_id)

            # Сохраняем информацию об устройстве
            self.devices[device_id] = {
                'device_id': device_id,
                'device_type': device_type,
                'app_version': app_version,
                'family_id': family_id,
                'device_token': device_token,
                'registered_at': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'status': 'active'
            }

            # Добавляем в семейную группу
            if family_id:
                if family_id not in self.family_groups:
                    self.family_groups[family_id] = []
                self.family_groups[family_id].append(device_id)

            return {
                'success': True,
                'device_token': device_token,
                'expires_in': 3600,
                'permissions': ['read', 'notify', 'location']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def authenticate_device(self, device_token: str) -> Dict[str, Any]:
        """Аутентификация устройства по токену"""
        try:
            # Ищем устройство по токену
            device = None
            for dev_id, dev_data in self.devices.items():
                if dev_data.get('device_token') == device_token:
                    device = dev_data
                    break

            if not device:
                return {
                    'success': False,
                    'error': 'Invalid device token'
                }

            # Обновляем время последнего обращения
            device['last_seen'] = datetime.now().isoformat()

            return {
                'success': True,
                'device_id': device['device_id'],
                'device_type': device['device_type'],
                'family_id': device.get('family_id'),
                'permissions': ['read', 'notify', 'location']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_notification(
            self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка push-уведомления"""
        try:
            device_token = notification_data.get('device_token')
            title = notification_data.get('title', 'ALADDIN Security')
            message = notification_data.get('message', '')
            priority = notification_data.get('priority', 'normal')
            action = notification_data.get('action', 'view_details')

            if not device_token:
                return {
                    'success': False,
                    'error': 'device_token is required'
                }

            # Проверяем аутентификацию
            auth_result = self.authenticate_device(device_token)
            if not auth_result['success']:
                return auth_result

            # Создаем уведомление
            notification_id = f"notif_{int(time.time())}"
            notification = {
                'id': notification_id,
                'device_token': device_token,
                'title': title,
                'message': message,
                'priority': priority,
                'action': action,
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            }

            # Сохраняем уведомление
            self.notifications.append(notification)

            # В реальной системе здесь был бы вызов FCM/APNS
            print(f"📱 Push уведомление отправлено: {title}")

            return {
                'success': True,
                'notification_id': notification_id,
                'sent_at': notification['sent_at']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_offline_data(self, device_token: str) -> Dict[str, Any]:
        """Получение данных для офлайн режима"""
        try:
            # Проверяем аутентификацию
            auth_result = self.authenticate_device(device_token)
            if not auth_result['success']:
                return auth_result

            family_id = auth_result.get('family_id')

            # Подготавливаем данные для офлайн режима
            offline_data = {
                'security_rules': self._get_security_rules(),
                'blocked_sites': self._get_blocked_sites(),
                'family_settings': self._get_family_settings(family_id),
                'emergency_contacts': self._get_emergency_contacts(family_id),
                'last_sync': datetime.now().isoformat()
            }

            return {
                'success': True,
                'offline_data': offline_data,
                'last_sync': offline_data['last_sync']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_location(self, device_token: str,
                        location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление местоположения устройства"""
        try:
            # Проверяем аутентификацию
            auth_result = self.authenticate_device(device_token)
            if not auth_result['success']:
                return auth_result

            device_id = auth_result['device_id']
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')
            accuracy = location_data.get('accuracy', 0)

            if not latitude or not longitude:
                return {
                    'success': False,
                    'error': 'latitude and longitude are required'
                }

            # Обновляем местоположение устройства
            if device_id in self.devices:
                self.devices[device_id]['location'] = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy,
                    'updated_at': datetime.now().isoformat()
                }

            return {
                'success': True,
                'message': 'Location updated'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_family_devices(self, device_token: str) -> Dict[str, Any]:
        """Получение списка устройств семьи"""
        try:
            # Проверяем аутентификацию
            auth_result = self.authenticate_device(device_token)
            if not auth_result['success']:
                return auth_result

            family_id = auth_result.get('family_id')
            if not family_id:
                return {
                    'success': False,
                    'error': 'Device not associated with family'
                }

            # Получаем устройства семьи
            family_devices = []
            for device_id in self.family_groups.get(family_id, []):
                if device_id in self.devices:
                    device = self.devices[device_id].copy()
                    # Убираем чувствительные данные
                    device.pop('device_token', None)
                    family_devices.append(device)

            return {
                'success': True,
                'family_id': family_id,
                'devices': family_devices,
                'count': len(family_devices)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def report_security_event(self, device_token: str,
                              event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отчет о событии безопасности с мобильного устройства"""
        try:
            # Проверяем аутентификацию
            auth_result = self.authenticate_device(device_token)
            if not auth_result['success']:
                return auth_result

            device_id = auth_result['device_id']
            event_type = event_data.get('event_type')

            if not event_type:
                return {
                    'success': False,
                    'error': 'event_type is required'
                }

            # Создаем событие безопасности
            event_id = f"mobile_evt_{int(time.time())}"

            # В реальной системе здесь был бы вызов основной системы
            # безопасности
            print(f"🔒 Событие безопасности от {device_id}: {event_type}")

            return {
                'success': True,
                'event_id': event_id,
                'message': 'Security event reported'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_device_token(self, device_id: str) -> str:
        """Генерация токена устройства"""
        secret = "aladdin_mobile_secret_key_2025"
        timestamp = str(int(time.time()))
        data = f"{device_id}:{timestamp}"
        token = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{token[:32]}.{timestamp}"

    def _get_security_rules(self) -> List[Dict[str, Any]]:
        """Получение правил безопасности для офлайн режима"""
        return [
            {
                'id': 'rule_001',
                'name': 'block_suspicious_sites',
                'type': 'url_filter',
                'enabled': True,
                'pattern': 'malware|phishing|suspicious'
            },
            {
                'id': 'rule_002',
                'name': 'parental_control',
                'type': 'content_filter',
                'enabled': True,
                'categories': ['adult', 'violence', 'gambling']
            }
        ]

    def _get_blocked_sites(self) -> List[str]:
        """Получение списка заблокированных сайтов"""
        return [
            'malware.example.com',
            'phishing.example.com',
            'adult-content.example.com'
        ]

    def _get_family_settings(self, family_id: Optional[str]) -> Dict[str, Any]:
        """Получение настроек семьи"""
        if not family_id:
            return {}

        return {
            'family_id': family_id,
            'parental_controls': {
                'enabled': True,
                'max_screen_time': 120,
                'bedtime': '21:00'
            },
            'child_protection': {
                'enabled': True,
                'age_restrictions': True,
                'location_tracking': True
            }
        }

    def _get_emergency_contacts(
            self, family_id: Optional[str]) -> List[Dict[str, str]]:
        """Получение экстренных контактов"""
        return [
            {
                'name': 'Emergency Services',
                'phone': '+7-800-123-45-67',
                'type': 'emergency'
            },
            {
                'name': 'Family Contact',
                'phone': '+7-900-123-45-67',
                'type': 'family'
            }
        ]


class MobileAPIServer:
    """Сервер мобильного API"""

    def __init__(self, host: str = '0.0.0.0', port: int = 8001):
        self.host = host
        self.port = port
        self.api = MobileAPI()
        self.running = False

    def start(self):
        """Запуск сервера мобильного API"""
        try:
            print(
                f"🚀 Запуск мобильного API сервера на {self.host}:{self.port}")
            print(
                "📱 API доступен по адресу: "
                "http://localhost:8001/mobile/api/v1"
            )
            print("🔗 Документация: http://localhost:8001/docs")
            print("=" * 60)

            # В реальной системе здесь был бы Flask/FastAPI сервер
            # Пока что просто имитируем работу
            self.running = True

            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Остановка мобильного API сервера")
            self.running = False
        except Exception as e:
            print(f"❌ Ошибка сервера: {e}")
            self.running = False

    def stop(self):
        """Остановка сервера"""
        self.running = False


def main():
    """Главная функция"""
    server = MobileAPIServer()
    server.start()


if __name__ == "__main__":
    main()

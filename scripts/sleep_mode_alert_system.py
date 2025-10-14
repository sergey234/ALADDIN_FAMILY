#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 СИСТЕМА АЛЕРТОВ СПЯЩЕГО РЕЖИМА
=================================

Система уведомлений и алертов для спящего режима
Включает email, SMS, push-уведомления и интеграцию с внешними системами

Автор: ALADDIN Security System
Дата: 2025-09-15
Версия: 1.0.0
"""

import asyncio
import json
import os
import smtplib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SleepModeAlertSystem:
    """Система алертов спящего режима"""
    
    def __init__(self):
        self.alert_config = self._load_alert_config()
        self.notification_channels = {
            "email": self._send_email_alert,
            "console": self._send_console_alert,
            "file": self._send_file_alert,
            "webhook": self._send_webhook_alert
        }
        
    def _load_alert_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации алертов"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            },
            "console": {
                "enabled": True,
                "log_level": "INFO"
            },
            "file": {
                "enabled": True,
                "log_file": "logs/sleep_mode_alerts.log"
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "headers": {}
            },
            "alert_rules": {
                "critical_functions_sleeping": {
                    "enabled": True,
                    "channels": ["console", "file", "email"],
                    "message_template": "🚨 КРИТИЧЕСКИЙ АЛЕРТ: Критические функции в спящем режиме: {count}"
                },
                "high_cpu_usage": {
                    "enabled": True,
                    "channels": ["console", "file"],
                    "message_template": "⚠️ ПРЕДУПРЕЖДЕНИЕ: Высокое использование CPU: {cpu_usage}%"
                },
                "high_memory_usage": {
                    "enabled": True,
                    "channels": ["console", "file"],
                    "message_template": "⚠️ ПРЕДУПРЕЖДЕНИЕ: Высокое использование памяти: {memory_usage}%"
                },
                "function_woke_up": {
                    "enabled": True,
                    "channels": ["console", "file"],
                    "message_template": "ℹ️ ИНФОРМАЦИЯ: Функция {function_name} пробуждена"
                },
                "function_sleeping": {
                    "enabled": True,
                    "channels": ["console", "file"],
                    "message_template": "😴 ИНФОРМАЦИЯ: Функция {function_name} переведена в спящий режим"
                }
            }
        }
        
        try:
            config_file = Path("config/sleep_mode_alerts.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Не удалось загрузить конфигурацию алертов: {e}")
        
        return default_config
    
    async def send_alert(self, alert_type: str, data: Dict[str, Any]) -> bool:
        """Отправка алерта"""
        try:
            if alert_type not in self.alert_config.get("alert_rules", {}):
                logger.warning(f"Неизвестный тип алерта: {alert_type}")
                return False
            
            rule = self.alert_config["alert_rules"][alert_type]
            if not rule.get("enabled", False):
                return True
            
            # Формируем сообщение
            message = rule["message_template"].format(**data)
            
            # Отправляем через указанные каналы
            success = True
            for channel in rule.get("channels", []):
                if channel in self.notification_channels:
                    try:
                        await self.notification_channels[channel](message, alert_type, data)
                    except Exception as e:
                        logger.error(f"Ошибка отправки через {channel}: {e}")
                        success = False
                else:
                    logger.warning(f"Неизвестный канал уведомлений: {channel}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка отправки алерта {alert_type}: {e}")
            return False
    
    async def _send_console_alert(self, message: str, alert_type: str, data: Dict[str, Any]) -> None:
        """Отправка алерта в консоль"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # Логирование
        log_level = self.alert_config.get("console", {}).get("log_level", "INFO")
        if log_level == "DEBUG":
            logger.debug(message)
        elif log_level == "INFO":
            logger.info(message)
        elif log_level == "WARNING":
            logger.warning(message)
        elif log_level == "ERROR":
            logger.error(message)
        elif log_level == "CRITICAL":
            logger.critical(message)
    
    async def _send_file_alert(self, message: str, alert_type: str, data: Dict[str, Any]) -> None:
        """Отправка алерта в файл"""
        try:
            log_file = self.alert_config.get("file", {}).get("log_file", "logs/sleep_mode_alerts.log")
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().isoformat()
            alert_entry = {
                "timestamp": timestamp,
                "type": alert_type,
                "message": message,
                "data": data
            }
            
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{json.dumps(alert_entry, ensure_ascii=False)}\n")
                
        except Exception as e:
            logger.error(f"Ошибка записи алерта в файл: {e}")
    
    async def _send_email_alert(self, message: str, alert_type: str, data: Dict[str, Any]) -> None:
        """Отправка алерта по email"""
        try:
            email_config = self.alert_config.get("email", {})
            if not email_config.get("enabled", False):
                return
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = email_config.get("username", "")
            msg['To'] = ", ".join(email_config.get("recipients", []))
            msg['Subject'] = f"ALADDIN Sleep Mode Alert: {alert_type}"
            
            # Тело сообщения
            body = f"""
ALADDIN Security System - Sleep Mode Alert

Тип алерта: {alert_type}
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Сообщение: {message}

Дополнительные данные:
{json.dumps(data, indent=2, ensure_ascii=False)}

---
Система безопасности ALADDIN
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Отправляем email
            server = smtplib.SMTP(email_config.get("smtp_server", ""), email_config.get("smtp_port", 587))
            server.starttls()
            server.login(email_config.get("username", ""), email_config.get("password", ""))
            
            text = msg.as_string()
            server.sendmail(email_config.get("username", ""), email_config.get("recipients", []), text)
            server.quit()
            
            logger.info(f"Email алерт отправлен: {alert_type}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки email алерта: {e}")
    
    async def _send_webhook_alert(self, message: str, alert_type: str, data: Dict[str, Any]) -> None:
        """Отправка алерта через webhook"""
        try:
            webhook_config = self.alert_config.get("webhook", {})
            if not webhook_config.get("enabled", False):
                return
            
            import aiohttp
            
            payload = {
                "timestamp": datetime.now().isoformat(),
                "type": alert_type,
                "message": message,
                "data": data,
                "source": "ALADDIN_SLEEP_MODE"
            }
            
            headers = {
                "Content-Type": "application/json",
                **webhook_config.get("headers", {})
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_config.get("url", ""),
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook алерт отправлен: {alert_type}")
                    else:
                        logger.error(f"Ошибка отправки webhook: {response.status}")
                        
        except Exception as e:
            logger.error(f"Ошибка отправки webhook алерта: {e}")
    
    async def test_alerts(self) -> None:
        """Тестирование системы алертов"""
        logger.info("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ АЛЕРТОВ")
        logger.info("=" * 40)
        
        test_alerts = [
            ("critical_functions_sleeping", {"count": 5}),
            ("high_cpu_usage", {"cpu_usage": 85.5}),
            ("high_memory_usage", {"memory_usage": 90.2}),
            ("function_woke_up", {"function_name": "test_function"}),
            ("function_sleeping", {"function_name": "test_function"})
        ]
        
        for alert_type, data in test_alerts:
            logger.info(f"Тестирование алерта: {alert_type}")
            success = await self.send_alert(alert_type, data)
            if success:
                logger.info(f"✅ Алерт {alert_type} отправлен успешно")
            else:
                logger.error(f"❌ Ошибка отправки алерта {alert_type}")
            
            await asyncio.sleep(1)  # Пауза между тестами
        
        logger.info("🧪 Тестирование завершено")

async def main():
    """Главная функция"""
    print("🚨 СИСТЕМА АЛЕРТОВ СПЯЩЕГО РЕЖИМА")
    print("=" * 40)
    
    alert_system = SleepModeAlertSystem()
    
    # Тестируем систему алертов
    await alert_system.test_alerts()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
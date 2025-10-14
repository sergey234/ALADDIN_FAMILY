#!/usr/bin/env python3
"""
SWITCH TO REPLACEMENT COMPONENTS
Переключение на заменяющие компоненты
"""

import os
import shutil
import logging
from datetime import datetime


def backup_old_components() -> None:
    """Резервное копирование старых компонентов"""
    backup_dir = f"backup_old_components_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    old_components = [
        "security/ai_agents/family_communication_hub.py",
        "security/ai_agents/emergency_response_interface.py", 
        "security/ai_agents/notification_bot.py"
    ]
    
    for component in old_components:
        if os.path.exists(component):
            backup_path = os.path.join(backup_dir, os.path.basename(component))
            shutil.copy2(component, backup_path)
            print(f"✅ Резервная копия создана: {backup_path}")
        else:
            print(f"⚠️  Файл не найден: {component}")


def update_safe_function_manager() -> None:
    """Обновление SafeFunctionManager для использования новых компонентов"""
    manager_file = "security/safe_function_manager.py"
    
    if not os.path.exists(manager_file):
        print(f"❌ Файл не найден: {manager_file}")
        return
    
    # Читаем файл
    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем импорты
    replacements = {
        "from security.ai_agents.family_communication_hub import FamilyCommunicationHub": 
        "from security.ai_agents.family_communication_replacement import FamilyCommunicationReplacement",
        
        "from security.ai_agents.emergency_response_interface import EmergencyResponseInterface":
        "from security.ai_agents.contextual_alert_system import ContextualAlertSystem",
        
        "from security.ai_agents.notification_bot import NotificationBot":
        "from security.ai_agents.smart_notification_manager import SmartNotificationManager"
    }
    
    for old_import, new_import in replacements.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            print(f"✅ Заменен импорт: {old_import} → {new_import}")
    
    # Записываем обновленный файл
    with open(manager_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ SafeFunctionManager обновлен")


def create_integration_script() -> None:
    """Создание скрипта интеграции"""
    integration_script = """#!/usr/bin/env python3
'''
INTEGRATION SCRIPT
Скрипт интеграции заменяющих компонентов
'''

import asyncio
import logging
from security.ai_agents.family_communication_replacement import FamilyCommunicationReplacement
from security.ai_agents.smart_notification_manager import SmartNotificationManager
from security.ai_agents.contextual_alert_system import ContextualAlertSystem

async def main():
    '''Основная функция интеграции'''
    print("🚀 Запуск интеграции заменяющих компонентов...")
    
    # Конфигурация
    config = {
        'telegram_token': 'YOUR_TELEGRAM_BOT_TOKEN',
        'discord_token': 'YOUR_DISCORD_BOT_TOKEN', 
        'twilio_sid': 'YOUR_TWILIO_SID',
        'twilio_token': 'YOUR_TWILIO_TOKEN',
        'twilio_from_number': '+1234567890'
    }
    
    # Инициализация компонентов
    family_hub = FamilyCommunicationReplacement("family_001", config)
    notification_manager = SmartNotificationManager()
    alert_system = ContextualAlertSystem()
    
    # Запуск компонентов
    await family_hub.start()
    await notification_manager.start()
    await alert_system.start()
    
    print("✅ Все компоненты успешно запущены!")
    
    # Тестирование
    stats = await family_hub.get_family_statistics()
    print(f"📊 Статистика: {stats}")
    
    # Остановка
    await family_hub.stop()
    await notification_manager.stop()
    await alert_system.stop()
    
    print("🛑 Все компоненты остановлены")

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    with open("scripts/integrate_replacement_components.py", 'w', encoding='utf-8') as f:
        f.write(integration_script)
    
    print("✅ Скрипт интеграции создан: scripts/integrate_replacement_components.py")


def create_config_template() -> None:
    """Создание безопасного шаблона конфигурации"""
    config_template = """# SECURE CONFIGURATION TEMPLATE
# БЕЗОПАСНЫЙ шаблон конфигурации для заменяющих компонентов
# ВНИМАНИЕ: НЕ ХРАНИТЕ СЕКРЕТЫ В КОДЕ! Используйте переменные окружения!

# Импорт безопасного менеджера конфигурации
from security.secure_config_manager import SecureConfigManager

# Создание менеджера конфигурации
config_manager = SecureConfigManager()

# Загрузка конфигурации из переменных окружения
config = config_manager.load_config()

# Валидация безопасности
validation = config_manager.validate_config()
if not validation['valid']:
    raise ValueError(f"Небезопасная конфигурация: {validation['errors']}")

# Безопасное получение конфигурации
TELEGRAM_BOT_TOKEN = config.telegram_bot_token
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

DISCORD_BOT_TOKEN = config.discord_bot_token
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config.twilio_auth_token
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER', '+1234567890')

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = config.email_password

FIREBASE_SERVER_KEY = config.firebase_server_key
FCM_PROJECT_ID = os.getenv('FCM_PROJECT_ID')

ENCRYPTION_KEY = config.encryption_key
API_RATE_LIMIT = config.api_rate_limit
MAX_MESSAGE_LENGTH = config.max_message_length

# Создание .env.template файла для пользователя
config_manager.create_env_template('.env.template')

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/family_communication.log"
"""
    
    with open("config/replacement_components_config.py", 'w', encoding='utf-8') as f:
        f.write(config_template)
    
    print("✅ Шаблон конфигурации создан: config/replacement_components_config.py")


def main():
    """Основная функция"""
    print("🔄 ПЕРЕКЛЮЧЕНИЕ НА ЗАМЕНЯЮЩИЕ КОМПОНЕНТЫ")
    print("=" * 50)
    
    # 1. Резервное копирование
    print("\n1️⃣ Создание резервных копий...")
    backup_old_components()
    
    # 2. Обновление SafeFunctionManager
    print("\n2️⃣ Обновление SafeFunctionManager...")
    update_safe_function_manager()
    
    # 3. Создание скрипта интеграции
    print("\n3️⃣ Создание скрипта интеграции...")
    create_integration_script()
    
    # 4. Создание шаблона конфигурации
    print("\n4️⃣ Создание шаблона конфигурации...")
    create_config_template()
    
    print("\n✅ ПЕРЕКЛЮЧЕНИЕ ЗАВЕРШЕНО!")
    print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Настройте конфигурацию в config/replacement_components_config.py")
    print("2. Запустите интеграцию: python3 scripts/integrate_replacement_components.py")
    print("3. Протестируйте новые компоненты")
    print("4. Обновите документацию")


if __name__ == "__main__":
    main()
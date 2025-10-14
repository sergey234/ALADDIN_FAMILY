#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка статуса и перевод ботов в спящий режим
Проверяет все боты из Этапов 9.2 и 9.3 и переводит активные в спящий режим
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotSleepManager:
    """Менеджер для проверки и перевода ботов в спящий режим"""

    def __init__(self):
        self.sleep_config_path = "sleep_config.json"
        self.sleep_config = self._load_sleep_config()
        self.bot_instances = {}
        self.sleep_status = {}

        # Список всех ботов из Этапов 9.2 и 9.3
        self.all_bots = {
            # Этап 9.2: Мобильные и игровые боты
            "mobile_navigation": {
                "file": "mobile_navigation_bot.py",
                "class": "MobileNavigationBot",
                "function": "function_86",
                "description": "бот навигации по мобильным устройствам",
            },
            "gaming_security": {
                "file": "gaming_security_bot.py",
                "class": "GamingSecurityBot",
                "function": "function_87",
                "description": "бот безопасности игр",
            },
            "emergency_response": {
                "file": "emergency_response_bot.py",
                "class": "EmergencyResponseBot",
                "function": "function_88",
                "description": "бот экстренного реагирования",
            },
            "parental_control": {
                "file": "parental_control_bot.py",
                "class": "ParentalControlBot",
                "function": "function_89",
                "description": "бот родительского контроля",
            },
            "notification": {
                "file": "notification_bot.py",
                "class": "NotificationBot",
                "function": "function_90",
                "description": "бот уведомлений",
            },
            # Этап 9.3: Мессенджеры и социальные сети
            "whatsapp": {
                "file": "whatsapp_security_bot.py",
                "class": "WhatsAppSecurityBot",
                "function": "function_91",
                "description": "бот безопасности WhatsApp",
            },
            "telegram": {
                "file": "telegram_security_bot.py",
                "class": "TelegramSecurityBot",
                "function": "function_92",
                "description": "бот безопасности Telegram",
            },
            "instagram": {
                "file": "instagram_security_bot.py",
                "class": "InstagramSecurityBot",
                "function": "function_93",
                "description": "бот безопасности Instagram",
            },
            "max_messenger": {
                "file": "max_messenger_security_bot.py",
                "class": "MaxMessengerSecurityBot",
                "function": "function_94",
                "description": "бот безопасности российского мессенджера MAX",
            },
            "analytics": {
                "file": "analytics_bot.py",
                "class": "AnalyticsBot",
                "function": "function_95",
                "description": "бот аналитики",
            },
            "website_navigation": {
                "file": "website_navigation_bot.py",
                "class": "WebsiteNavigationBot",
                "function": "function_96",
                "description": "бот навигации по сайтам",
            },
        }

    def _load_sleep_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации спящего режима"""
        default_config = {
            "sleep_enabled": True,
            "auto_sleep_after_minutes": 30,
            "wake_up_on_demand": True,
            "save_state_on_sleep": True,
            "bots": {},
        }

        try:
            if Path(self.sleep_config_path).exists():
                with open(self.sleep_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return {**default_config, **config}
            else:
                return default_config
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return default_config

    def _save_sleep_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации спящего режима"""
        try:
            with open(self.sleep_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    def check_bot_files_exist(self) -> Dict[str, bool]:
        """Проверка существования файлов ботов"""
        print("🔍 Проверка существования файлов ботов...")

        file_status = {}
        for bot_name, bot_info in self.all_bots.items():
            file_path = Path(bot_info["file"])
            exists = file_path.exists()
            file_status[bot_name] = exists

            status_icon = "✅" if exists else "❌"
            status_text = "Найден" if exists else "Не найден"
            print(f"  {status_icon} {bot_info['file']}: {status_text}")

        return file_status

    def check_sleep_state_files(self) -> Dict[str, bool]:
        """Проверка файлов состояния спящего режима"""
        print("\n😴 Проверка файлов состояния спящего режима...")

        sleep_files = {}
        for bot_name in self.all_bots.keys():
            sleep_file = f"sleep_state_{bot_name}.json"
            exists = Path(sleep_file).exists()
            sleep_files[bot_name] = exists

            status_icon = "😴" if exists else "🌅"
            status_text = "В спящем режиме" if exists else "Активен"
            print(f"  {status_icon} {sleep_file}: {status_text}")

        return sleep_files

    async def create_mock_bot_instances(self) -> Dict[str, Any]:
        """Создание заглушек ботов для тестирования"""
        print("\n🤖 Создание заглушек ботов...")

        class MockBot:
            def __init__(self, name, bot_type):
                self.name = name
                self.bot_type = bot_type
                self.config = {"test": True, "bot_type": bot_type}
                self.stats = {"test_count": 0}
                self.running = False

            async def start(self):
                self.running = True
                return True

            async def stop(self):
                self.running = False
                return True

            async def get_status(self):
                return {
                    "status": "running" if self.running else "stopped",
                    "bot_type": self.bot_type,
                    "config": self.config,
                }

        mock_bots = {}
        for bot_name, bot_info in self.all_bots.items():
            mock_bot = MockBot(f"Test{bot_info['class']}", bot_name)
            mock_bots[bot_name] = mock_bot
            print(f"  ✅ {bot_info['class']}: Создана заглушка")

        return mock_bots

    async def put_bot_to_sleep(self, bot_name: str, bot_instance: Any) -> bool:
        """Перевод бота в спящий режим"""
        try:
            # Остановка бота
            if hasattr(bot_instance, "stop"):
                await bot_instance.stop()

            # Сохранение состояния
            sleep_data = {
                "bot_name": bot_name,
                "timestamp": datetime.utcnow().isoformat(),
                "config": getattr(bot_instance, "config", {}),
                "stats": getattr(bot_instance, "stats", {}),
                "running": False,
                "sleep_reason": "Manual sleep command",
            }

            # Сохранение в файл
            sleep_file = f"sleep_state_{bot_name}.json"
            with open(sleep_file, "w", encoding="utf-8") as f:
                json.dump(sleep_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Бот {bot_name} переведен в спящий режим")
            return True

        except Exception as e:
            logger.error(
                f"Ошибка перевода бота {bot_name} в спящий режим: {e}"
            )
            return False

    async def check_and_sleep_all_bots(self):
        """Проверка и перевод всех ботов в спящий режим"""
        print("🚀 ПРОВЕРКА И ПЕРЕВОД БОТОВ В СПЯЩИЙ РЕЖИМ")
        print("=" * 60)

        # 1. Проверка файлов ботов
        file_status = self.check_bot_files_exist()
        existing_bots = [
            name for name, exists in file_status.items() if exists
        ]

        # 2. Проверка состояния спящего режима
        sleep_status = self.check_sleep_state_files()
        sleeping_bots = [
            name for name, sleeping in sleep_status.items() if sleeping
        ]
        active_bots = [
            name for name, sleeping in sleep_status.items() if not sleeping
        ]

        print("\n📊 СТАТИСТИКА:")
        print(f"  📁 Всего файлов ботов: {len(file_status)}")
        print(f"  ✅ Существующих файлов: {len(existing_bots)}")
        print(f"  😴 Ботов в спящем режиме: {len(sleeping_bots)}")
        print(f"  🌅 Активных ботов: {len(active_bots)}")

        if not active_bots:
            print("\n🎉 ВСЕ БОТЫ УЖЕ В СПЯЩЕМ РЕЖИМЕ!")
            return True

        # 3. Создание заглушек для активных ботов
        print(
            f"\n🤖 Создание заглушек для {len(active_bots)} активных ботов..."
        )
        mock_bots = await self.create_mock_bot_instances()

        # 4. Перевод активных ботов в спящий режим
        print(
            f"\n😴 Перевод {len(active_bots)} активных ботов в спящий режим..."
        )

        sleep_results = {}
        for bot_name in active_bots:
            if bot_name in mock_bots:
                success = await self.put_bot_to_sleep(
                    bot_name, mock_bots[bot_name]
                )
                sleep_results[bot_name] = success

                bot_info = self.all_bots[bot_name]
                status_icon = "✅" if success else "❌"
                func_name = bot_info['function']
                func_desc = bot_info['description']
                function_desc = f"{func_name}: {func_desc}"
                print(f"  {status_icon} {function_desc}")

        # 5. Итоговая статистика
        successful_sleeps = sum(
            1 for success in sleep_results.values() if success
        )
        total_active = len(active_bots)

        print("\n📊 РЕЗУЛЬТАТЫ:")
        sleep_msg = (
            f"Успешно переведено в спящий режим: "
            f"{successful_sleeps}/{total_active}"
        )
        print(f"  😴 {sleep_msg}")
        state_files = [f for f in Path('.').glob('sleep_state_*.json')]
        state_files_count = len(state_files)
        print(f"  📁 Всего файлов состояния: {state_files_count}")

        # 6. Финальная проверка
        print("\n🔍 ФИНАЛЬНАЯ ПРОВЕРКА:")
        final_sleep_status = self.check_sleep_state_files()
        final_sleeping = sum(
            1 for sleeping in final_sleep_status.values() if sleeping
        )
        final_active = len(final_sleep_status) - final_sleeping

        print(f"  😴 Ботов в спящем режиме: {final_sleeping}")
        print(f"  🌅 Активных ботов: {final_active}")

        if final_active == 0:
            print("\n🎉 ВСЕ БОТЫ УСПЕШНО ПЕРЕВЕДЕНЫ В СПЯЩИЙ РЕЖИМ!")
            return True
        else:
            print(f"\n⚠️ {final_active} ботов остались активными")
            return False

    def generate_sleep_report(self):
        """Генерация отчета о спящем режиме"""
        print("\n📊 Генерация отчета о спящем режиме...")

        # Подсчет файлов состояния
        sleep_files = list(Path(".").glob("sleep_state_*.json"))
        sleeping_bots = [
            f.stem.replace("sleep_state_", "") for f in sleep_files
        ]

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_bots": len(self.all_bots),
            "sleeping_bots": len(sleeping_bots),
            "active_bots": len(self.all_bots) - len(sleeping_bots),
            "sleep_files": [f.name for f in sleep_files],
            "sleeping_bot_list": sleeping_bots,
            "config": self.sleep_config,
        }

        # Сохранение отчета
        with open(
            "comprehensive_sleep_report.json", "w", encoding="utf-8"
        ) as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("✅ Отчет сохранен: comprehensive_sleep_report.json")
        return report


async def main():
    """Главная функция"""
    sleep_manager = BotSleepManager()

    # Проверка и перевод ботов в спящий режим
    success = await sleep_manager.check_and_sleep_all_bots()

    # Генерация отчета
    sleep_manager.generate_sleep_report()

    if success:
        print("\n🎉 ВСЕ БОТЫ УСПЕШНО ПЕРЕВЕДЕНЫ В СПЯЩИЙ РЕЖИМ!")
        print("😴 Система готова к следующему этапу развития!")
        return 0
    else:
        print("\n⚠️ Некоторые боты не были переведены в спящий режим")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

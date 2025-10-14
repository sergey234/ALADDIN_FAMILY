#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенное тестирование мессенджер ботов
Тестирование основных функций без внешних зависимостей
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMessengerTest:
    """Упрощенное тестирование мессенджер ботов"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    async def test_bot_creation(self):
        """Тестирование создания ботов"""
        print("🔧 Тестирование создания мессенджер ботов...")
        
        bots_created = 0
        total_bots = 6
        
        # Тест создания WhatsApp бота
        try:
            from whatsapp_security_bot import WhatsAppSecurityBot
            bot = WhatsAppSecurityBot("TestWhatsAppBot")
            print("✅ WhatsAppSecurityBot: Создан")
            bots_created += 1
        except Exception as e:
            print(f"❌ WhatsAppSecurityBot: Ошибка создания - {e}")
        
        # Тест создания Telegram бота
        try:
            from telegram_security_bot import TelegramSecurityBot
            bot = TelegramSecurityBot("TestTelegramBot")
            print("✅ TelegramSecurityBot: Создан")
            bots_created += 1
        except Exception as e:
            print(f"❌ TelegramSecurityBot: Ошибка создания - {e}")
        
        # Тест создания Instagram бота
        try:
            from instagram_security_bot import InstagramSecurityBot
            bot = InstagramSecurityBot("TestInstagramBot")
            print("✅ InstagramSecurityBot: Создан")
            bots_created += 1
        except Exception as e:
            print(f"❌ InstagramSecurityBot: Ошибка создания - {e}")
        
        # Тест создания MAX мессенджер бота
        try:
            from max_messenger_security_bot import MaxMessengerSecurityBot
            bot = MaxMessengerSecurityBot("TestMaxBot")
            print("✅ MaxMessengerSecurityBot: Создан")
            bots_created += 1
        except Exception as e:
            print(f"❌ MaxMessengerSecurityBot: Ошибка создания - {e}")
        
        # Тест создания Analytics бота
        try:
            from analytics_bot import AnalyticsBot
            bot = AnalyticsBot("TestAnalyticsBot")
            print("✅ AnalyticsBot: Создан")
            bots_created += 1
        except Exception as e:
            print(f"❌ AnalyticsBot: Ошибка создания - {e}")
        
        # Тест создания Website Navigation бота
        try:
            from website_navigation_bot import WebsiteNavigationBot
            bot = WebsiteNavigationBot("TestWebsiteBot")
            print("✅ WebsiteNavigationBot: Создан")
            bots_created += 1
        except Exception as e:
            print(f"❌ WebsiteNavigationBot: Ошибка создания - {e}")
        
        print(f"📊 Создано ботов: {bots_created}/{total_bots}")
        self.test_results["bot_creation"] = {
            "status": "success" if bots_created == total_bots else "partial",
            "created": bots_created,
            "total": total_bots
        }
        
        return bots_created == total_bots
    
    async def test_bot_functionality(self):
        """Тестирование базовой функциональности ботов"""
        print("\n🧪 Тестирование базовой функциональности...")
        
        functionality_tests = 0
        total_tests = 0
        
        # Тест WhatsApp бота
        try:
            from whatsapp_security_bot import WhatsAppSecurityBot
            bot = WhatsAppSecurityBot("TestWhatsAppBot")
            
            # Тест инициализации
            if hasattr(bot, 'name') and bot.name == "TestWhatsAppBot":
                functionality_tests += 1
                print("✅ WhatsAppSecurityBot: Инициализация работает")
            total_tests += 1
            
            # Тест конфигурации
            if hasattr(bot, 'config') and isinstance(bot.config, dict):
                functionality_tests += 1
                print("✅ WhatsAppSecurityBot: Конфигурация работает")
            total_tests += 1
            
        except Exception as e:
            print(f"❌ WhatsAppSecurityBot: Ошибка функциональности - {e}")
            total_tests += 2
        
        # Тест Telegram бота
        try:
            from telegram_security_bot import TelegramSecurityBot
            bot = TelegramSecurityBot("TestTelegramBot")
            
            if hasattr(bot, 'name') and bot.name == "TestTelegramBot":
                functionality_tests += 1
                print("✅ TelegramSecurityBot: Инициализация работает")
            total_tests += 1
            
            if hasattr(bot, 'config') and isinstance(bot.config, dict):
                functionality_tests += 1
                print("✅ TelegramSecurityBot: Конфигурация работает")
            total_tests += 1
            
        except Exception as e:
            print(f"❌ TelegramSecurityBot: Ошибка функциональности - {e}")
            total_tests += 2
        
        # Тест Instagram бота
        try:
            from instagram_security_bot import InstagramSecurityBot
            bot = InstagramSecurityBot("TestInstagramBot")
            
            if hasattr(bot, 'name') and bot.name == "TestInstagramBot":
                functionality_tests += 1
                print("✅ InstagramSecurityBot: Инициализация работает")
            total_tests += 1
            
            if hasattr(bot, 'config') and isinstance(bot.config, dict):
                functionality_tests += 1
                print("✅ InstagramSecurityBot: Конфигурация работает")
            total_tests += 1
            
        except Exception as e:
            print(f"❌ InstagramSecurityBot: Ошибка функциональности - {e}")
            total_tests += 2
        
        # Тест MAX мессенджер бота
        try:
            from max_messenger_security_bot import MaxMessengerSecurityBot
            bot = MaxMessengerSecurityBot("TestMaxBot")
            
            if hasattr(bot, 'name') and bot.name == "TestMaxBot":
                functionality_tests += 1
                print("✅ MaxMessengerSecurityBot: Инициализация работает")
            total_tests += 1
            
            if hasattr(bot, 'config') and isinstance(bot.config, dict):
                functionality_tests += 1
                print("✅ MaxMessengerSecurityBot: Конфигурация работает")
            total_tests += 1
            
        except Exception as e:
            print(f"❌ MaxMessengerSecurityBot: Ошибка функциональности - {e}")
            total_tests += 2
        
        # Тест Analytics бота
        try:
            from analytics_bot import AnalyticsBot
            bot = AnalyticsBot("TestAnalyticsBot")
            
            if hasattr(bot, 'name') and bot.name == "TestAnalyticsBot":
                functionality_tests += 1
                print("✅ AnalyticsBot: Инициализация работает")
            total_tests += 1
            
            if hasattr(bot, 'config') and isinstance(bot.config, dict):
                functionality_tests += 1
                print("✅ AnalyticsBot: Конфигурация работает")
            total_tests += 1
            
        except Exception as e:
            print(f"❌ AnalyticsBot: Ошибка функциональности - {e}")
            total_tests += 2
        
        # Тест Website Navigation бота
        try:
            from website_navigation_bot import WebsiteNavigationBot
            bot = WebsiteNavigationBot("TestWebsiteBot")
            
            if hasattr(bot, 'name') and bot.name == "TestWebsiteBot":
                functionality_tests += 1
                print("✅ WebsiteNavigationBot: Инициализация работает")
            total_tests += 1
            
            if hasattr(bot, 'config') and isinstance(bot.config, dict):
                functionality_tests += 1
                print("✅ WebsiteNavigationBot: Конфигурация работает")
            total_tests += 1
            
        except Exception as e:
            print(f"❌ WebsiteNavigationBot: Ошибка функциональности - {e}")
            total_tests += 2
        
        success_rate = (functionality_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Функциональность: {functionality_tests}/{total_tests} ({success_rate:.1f}%)")
        
        self.test_results["functionality"] = {
            "status": "success" if success_rate >= 80 else "partial",
            "passed": functionality_tests,
            "total": total_tests,
            "success_rate": success_rate
        }
        
        return success_rate >= 80
    
    async def test_code_quality(self):
        """Тестирование качества кода"""
        print("\n📝 Тестирование качества кода...")
        
        import subprocess
        import os
        
        bot_files = [
            "whatsapp_security_bot.py",
            "telegram_security_bot.py", 
            "instagram_security_bot.py",
            "max_messenger_security_bot.py",
            "analytics_bot.py",
            "website_navigation_bot.py"
        ]
        
        quality_tests = 0
        total_tests = len(bot_files)
        
        for bot_file in bot_files:
            if os.path.exists(bot_file):
                try:
                    # Проверка синтаксиса
                    result = subprocess.run(
                        ["python3", "-m", "py_compile", bot_file],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        quality_tests += 1
                        print(f"✅ {bot_file}: Синтаксис корректен")
                    else:
                        print(f"❌ {bot_file}: Ошибка синтаксиса - {result.stderr}")
                        
                except Exception as e:
                    print(f"❌ {bot_file}: Ошибка проверки - {e}")
            else:
                print(f"❌ {bot_file}: Файл не найден")
        
        success_rate = (quality_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Качество кода: {quality_tests}/{total_tests} ({success_rate:.1f}%)")
        
        self.test_results["code_quality"] = {
            "status": "success" if success_rate >= 80 else "partial",
            "passed": quality_tests,
            "total": total_tests,
            "success_rate": success_rate
        }
        
        return success_rate >= 80
    
    def generate_test_report(self):
        """Генерация отчета о тестировании"""
        print("\n📊 Генерация отчета о тестировании...")
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if r["status"] == "success"])
        partial_tests = len([r for r in self.test_results.values() if r["status"] == "partial"])
        failed_tests = total_tests - successful_tests - partial_tests
        
        overall_success_rate = ((successful_tests + partial_tests * 0.5) / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "partial_tests": partial_tests,
                "failed_tests": failed_tests,
                "overall_success_rate": overall_success_rate,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Сохранение отчета
        with open("simple_messenger_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчет сохранен: simple_messenger_test_report.json")
        print(f"📈 Общая успешность: {overall_success_rate:.1f}%")
        
        return report
    
    def _generate_recommendations(self):
        """Генерация рекомендаций на основе результатов тестирования"""
        recommendations = []
        
        if "bot_creation" in self.test_results and self.test_results["bot_creation"]["status"] != "success":
            recommendations.append("Исправить ошибки создания ботов")
        
        if "functionality" in self.test_results and self.test_results["functionality"]["success_rate"] < 100:
            recommendations.append("Улучшить функциональность ботов")
        
        if "code_quality" in self.test_results and self.test_results["code_quality"]["success_rate"] < 100:
            recommendations.append("Исправить ошибки качества кода")
        
        if not recommendations:
            recommendations.append("Все тесты прошли успешно - система готова к следующему этапу")
        
        return recommendations
    
    async def run_full_test(self):
        """Запуск полного тестирования"""
        print("🚀 Запуск упрощенного тестирования мессенджер ботов")
        print("=" * 70)
        
        self.start_time = datetime.utcnow()
        
        try:
            # 1. Тестирование создания ботов
            creation_success = await self.test_bot_creation()
            
            # 2. Тестирование функциональности
            functionality_success = await self.test_bot_functionality()
            
            # 3. Тестирование качества кода
            quality_success = await self.test_code_quality()
            
            self.end_time = datetime.utcnow()
            
            # 4. Генерация отчета
            report = self.generate_test_report()
            
            print("\n" + "=" * 70)
            print("🎉 УПРОЩЕННОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
            print(f"📊 Общая успешность: {report['test_summary']['overall_success_rate']:.1f}%")
            print(f"⏱️ Время выполнения: {report['test_summary']['duration']:.2f} секунд")
            print("=" * 70)
            
            return report['test_summary']['overall_success_rate'] >= 70.0
            
        except Exception as e:
            print(f"❌ Критическая ошибка тестирования: {e}")
            return False


async def main():
    """Главная функция тестирования"""
    test_suite = SimpleMessengerTest()
    success = await test_suite.run_full_test()
    
    if success:
        print("\n✅ Тестирование прошло успешно!")
        return 0
    else:
        print("\n❌ Тестирование не прошло!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
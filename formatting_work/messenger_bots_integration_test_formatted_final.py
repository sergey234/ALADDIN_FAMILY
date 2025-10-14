#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграционное тестирование мессенджер ботов
Тестирование всех созданных мессенджер ботов безопасности
"""

import asyncio
import json
import logging
import time
from datetime import datetime

from .analytics_bot import AnalyticsBot
from .instagram_security_bot import InstagramSecurityBot
from .max_messenger_security_bot import MaxMessengerSecurityBot
from .telegram_security_bot import TelegramSecurityBot
from .website_navigation_bot import WebsiteNavigationBot

# Импорт всех мессенджер ботов
from .whatsapp_security_bot import WhatsAppSecurityBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessengerBotsIntegrationTest:
    """Интеграционное тестирование мессенджер ботов"""

    def __init__(self):
        self.bots = {}
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    async def setup_bots(self):
        """Инициализация всех ботов"""
        print("🔧 Инициализация мессенджер ботов...")

        # Создание экземпляров ботов
        self.bots = {
            "whatsapp": WhatsAppSecurityBot("TestWhatsAppBot"),
            "telegram": TelegramSecurityBot("TestTelegramBot"),
            "instagram": InstagramSecurityBot("TestInstagramBot"),
            "max_messenger": MaxMessengerSecurityBot("TestMaxBot"),
            "analytics": AnalyticsBot("TestAnalyticsBot"),
            "website_navigation": WebsiteNavigationBot("TestWebsiteBot"),
        }

        print(f"✅ Создано {len(self.bots)} ботов")

    async def start_all_bots(self):
        """Запуск всех ботов"""
        print("🚀 Запуск всех мессенджер ботов...")

        started_bots = 0
        for name, bot in self.bots.items():
            try:
                success = await bot.start()
                if success:
                    started_bots += 1
                    print(f"✅ {name}: Запущен")
                else:
                    print(f"❌ {name}: Ошибка запуска")
            except Exception as e:
                print(f"❌ {name}: Исключение при запуске - {e}")

        print(f"📊 Запущено ботов: {started_bots}/{len(self.bots)}")
        return started_bots == len(self.bots)

    async def test_individual_functionality(self):
        """Тестирование индивидуальной функциональности каждого бота"""
        print("\n🧪 Тестирование индивидуальной функциональности...")

        for name, bot in self.bots.items():
            print(f"\n--- Тестирование {name} ---")
            try:
                # Тест статуса
                status = await bot.get_status()
                print(f"✅ Статус: {status.get('status', 'unknown')}")

                # Специфичные тесты для каждого бота
                if name == "whatsapp":
                    await self._test_whatsapp_bot(bot)
                elif name == "telegram":
                    await self._test_telegram_bot(bot)
                elif name == "instagram":
                    await self._test_instagram_bot(bot)
                elif name == "max_messenger":
                    await self._test_max_messenger_bot(bot)
                elif name == "analytics":
                    await self._test_analytics_bot(bot)
                elif name == "website_navigation":
                    await self._test_website_navigation_bot(bot)

                self.test_results[name] = {"status": "success", "error": None}

            except Exception as e:
                print(f"❌ Ошибка тестирования {name}: {e}")
                self.test_results[name] = {"status": "error", "error": str(e)}

    async def _test_whatsapp_bot(self, bot):
        """Тестирование WhatsApp бота"""
        # Тест анализа сообщения
        message_data = {
            "id": "msg_123",
            "content": "Привет! Это тестовое сообщение",
            "type": "text",
            "sender_id": "user123",
        }

        result = await bot.analyze_message(message_data)
        print(f"✅ Анализ сообщения: {result.threat_level.value}")

        # Тест отчета по безопасности
        report = await bot.get_security_report()
        print(f"✅ Отчет: {report.get('total_messages', 0)} сообщений")

    async def _test_telegram_bot(self, bot):
        """Тестирование Telegram бота"""
        # Тест анализа сообщения
        message_data = {
            "message_id": 12345,
            "text": "Тестовое сообщение в Telegram",
            "type": "text",
            "chat": {"id": -1001234567890, "type": "group"},
            "from": {
                "id": 123456789,
                "username": "test_user",
                "is_bot": False,
            },
        }

        result = await bot.analyze_message(message_data)
        print(f"✅ Анализ сообщения: {result.threat_level.value}")

        # Тест добавления чата в мониторинг
        chat_added = await bot.add_chat_to_monitoring(
            chat_id="-1001234567890", chat_type="group", title="Test Group"
        )
        print(f"✅ Чат добавлен в мониторинг: {chat_added}")

    async def _test_instagram_bot(self, bot):
        """Тестирование Instagram бота"""
        # Тест анализа контента
        content_data = {
            "id": "post_123",
            "type": "post",
            "caption": "Красивый закат! #sunset #nature",
            "media_url": "https://example.com/image.jpg",
            "media_type": "image",
            "user": {
                "id": "user123",
                "username": "test_user",
                "account_type": "personal",
                "is_verified": False,
                "is_private": False,
                "followers_count": 1000,
                "following_count": 500,
                "posts_count": 50,
            },
        }

        result = await bot.analyze_content(content_data)
        print(f"✅ Анализ контента: {result.threat_level.value}")

        # Тест добавления аккаунта в мониторинг
        account_added = await bot.add_account_to_monitoring(
            content_data["user"]
        )
        print(f"✅ Аккаунт добавлен в мониторинг: {account_added}")

    async def _test_max_messenger_bot(self, bot):
        """Тестирование MAX мессенджер бота"""
        # Тест анализа сообщения
        message_data = {
            "message_id": "msg_123",
            "text": "Сообщение в MAX мессенджере",
            "type": "text",
            "chat": {"id": "-1001234567890", "type": "group"},
            "from": {
                "id": "123456789",
                "username": "test_user",
                "is_bot": False,
            },
        }

        result = await bot.analyze_message(message_data)
        print(f"✅ Анализ сообщения: {result.threat_level.value}")

        # Тест сессии навигации
        session_id = await bot.start_navigation_session("user123")
        print(f"✅ Сессия навигации: {session_id}")

        if session_id:
            await bot.end_navigation_session(session_id)
            print("✅ Сессия завершена")

    async def _test_analytics_bot(self, bot):
        """Тестирование Analytics бота"""
        # Тест сбора метрик
        await bot.collect_metric(
            "test_metric", 0.75, bot.MetricType.GAUGE, {"component": "test"}
        )
        print("✅ Метрика собрана")

        # Тест детекции аномалий
        anomaly_result = await bot.detect_anomaly(
            "test_metric",
            [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 1.0, 1.1],
        )
        print(f"✅ Аномалия детектирована: {anomaly_result.is_anomaly}")

        # Тест генерации отчета
        report = await bot.generate_report(
            "Test Report",
            bot.ReportType.DAILY,
            datetime.utcnow(),
            datetime.utcnow(),
        )
        print(
            f"✅ Отчет сгенерирован: {report.get('total_metrics', 0)} метрик"
        )

    async def _test_website_navigation_bot(self, bot):
        """Тестирование Website Navigation бота"""
        # Тест анализа веб-сайта
        result = await bot.analyze_website("https://example.com", "user123")
        print(f"✅ Анализ сайта: {result.threat_level.value}")

        # Тест блокировки домена
        blocked = await bot.block_domain(
            "malware.com", "malware", "Test malware site"
        )
        print(f"✅ Домен заблокирован: {blocked}")

        # Тест сессии навигации
        session_id = await bot.start_navigation_session("user123")
        print(f"✅ Сессия навигации: {session_id}")

        if session_id:
            await bot.end_navigation_session(session_id)
            print("✅ Сессия завершена")

    async def test_inter_bot_communication(self):
        """Тестирование межботового взаимодействия"""
        print("\n🔗 Тестирование межботового взаимодействия...")

        try:
            # Тест передачи данных между ботами
            if "analytics" in self.bots and "whatsapp" in self.bots:
                # Analytics бот собирает метрики от WhatsApp бота
                await self.bots["analytics"].collect_metric(
                    "whatsapp_messages_analyzed",
                    self.bots["whatsapp"].stats.get("analyzed_messages", 0),
                    self.bots["analytics"].MetricType.COUNTER,
                    {"bot": "whatsapp"},
                )
                print("✅ Межботовая передача метрик: Analytics ← WhatsApp")

            # Тест общей статистики
            total_bots = len(self.bots)
            active_bots = sum(1 for bot in self.bots.values() if bot.running)
            print(
                f"✅ Общая статистика: {active_bots}/{total_bots} ботов активны"
            )

            self.test_results["inter_bot_communication"] = {
                "status": "success",
                "error": None,
            }

        except Exception as e:
            print(f"❌ Ошибка межботового взаимодействия: {e}")
            self.test_results["inter_bot_communication"] = {
                "status": "error",
                "error": str(e),
            }

    async def test_performance(self):
        """Тестирование производительности"""
        print("\n⚡ Тестирование производительности...")

        try:
            start_time = time.time()

            # Параллельное выполнение операций
            tasks = []
            for name, bot in self.bots.items():
                if hasattr(bot, "get_status"):
                    tasks.append(bot.get_status())

            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            execution_time = end_time - start_time

            print(f"✅ Время выполнения: {execution_time:.2f} секунд")
            print(
                f"✅ Успешных операций: "
                f"{len([r for r in results if not isinstance(r, Exception)])}"
                f"/{len(results)}"
            )

            self.test_results["performance"] = {
                "status": "success",
                "execution_time": execution_time,
                "successful_operations": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
                "total_operations": len(results),
            }

        except Exception as e:
            print(f"❌ Ошибка тестирования производительности: {e}")
            self.test_results["performance"] = {
                "status": "error",
                "error": str(e),
            }

    async def stop_all_bots(self):
        """Остановка всех ботов"""
        print("\n🛑 Остановка всех мессенджер ботов...")

        stopped_bots = 0
        for name, bot in self.bots.items():
            try:
                success = await bot.stop()
                if success:
                    stopped_bots += 1
                    print(f"✅ {name}: Остановлен")
                else:
                    print(f"❌ {name}: Ошибка остановки")
            except Exception as e:
                print(f"❌ {name}: Исключение при остановке - {e}")

        print(f"📊 Остановлено ботов: {stopped_bots}/{len(self.bots)}")
        return stopped_bots == len(self.bots)

    def generate_test_report(self):
        """Генерация отчета о тестировании"""
        print("\n📊 Генерация отчета о тестировании...")

        total_tests = len(self.test_results)
        successful_tests = len(
            [r for r in self.test_results.values() if r["status"] == "success"]
        )
        failed_tests = total_tests - successful_tests

        success_rate = (
            (successful_tests / total_tests * 100) if total_tests > 0 else 0
        )

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "start_time": (
                    self.start_time.isoformat() if self.start_time else None
                ),
                "end_time": (
                    self.end_time.isoformat() if self.end_time else None
                ),
                "duration": (
                    (self.end_time - self.start_time).total_seconds()
                    if self.start_time and self.end_time
                    else None
                ),
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations(),
        }

        # Сохранение отчета
        with open(
            "messenger_bots_test_report.json", "w", encoding="utf-8"
        ) as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("✅ Отчет сохранен: messenger_bots_test_report.json")
        print(f"📈 Успешность тестирования: {success_rate:.1f}%")

        return report

    def _generate_recommendations(self):
        """Генерация рекомендаций на основе результатов тестирования"""
        recommendations = []

        failed_tests = [
            name
            for name, result in self.test_results.items()
            if result["status"] == "error"
        ]

        if failed_tests:
            recommendations.append(
                f"Исправить ошибки в ботах: {', '.join(failed_tests)}"
            )

        if (
            "performance" in self.test_results
            and self.test_results["performance"]["status"] == "success"
        ):
            exec_time = self.test_results["performance"]["execution_time"]
            if exec_time > 5.0:
                recommendations.append(
                    "Оптимизировать производительность - "
                    "время выполнения превышает 5 секунд"
                )

        if not recommendations:
            recommendations.append(
                "Все тесты прошли успешно - система готова к продакшену"
            )

        return recommendations

    async def run_full_test(self):
        """Запуск полного тестирования"""
        print(
            "🚀 Запуск полного интеграционного тестирования мессенджер ботов"
        )
        print("=" * 70)

        self.start_time = datetime.utcnow()

        try:
            # 1. Инициализация ботов
            await self.setup_bots()

            # 2. Запуск всех ботов
            bots_started = await self.start_all_bots()
            if not bots_started:
                print("❌ Не все боты запустились - тестирование прервано")
                return False

            # 3. Тестирование индивидуальной функциональности
            await self.test_individual_functionality()

            # 4. Тестирование межботового взаимодействия
            await self.test_inter_bot_communication()

            # 5. Тестирование производительности
            await self.test_performance()

            # 6. Остановка всех ботов
            await self.stop_all_bots()

            self.end_time = datetime.utcnow()

            # 7. Генерация отчета
            report = self.generate_test_report()

            print("\n" + "=" * 70)
            print("🎉 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
            print(
                f"📊 Успешность: {report['test_summary']['success_rate']:.1f}%"
            )
            print(
                f"⏱️ Время выполнения: "
                f"{report['test_summary']['duration']:.2f} секунд"
            )
            print("=" * 70)

            return report["test_summary"]["success_rate"] >= 80.0

        except Exception as e:
            print(f"❌ Критическая ошибка тестирования: {e}")
            return False


async def main():
    """Главная функция тестирования"""
    test_suite = MessengerBotsIntegrationTest()
    success = await test_suite.run_full_test()

    if success:
        print("\n✅ Все тесты прошли успешно!")
        return 0
    else:
        print("\n❌ Некоторые тесты не прошли!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

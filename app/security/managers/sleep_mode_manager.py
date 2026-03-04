#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SleepModeManager - Менеджер спящего режима для мессенджер ботов
Управление переводом ботов в спящий режим и их пробуждением
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SleepModeManager:
    """Менеджер спящего режима для мессенджер ботов"""

    def __init__(self, sleep_config_path: str = "sleep_config.json"):
        self.sleep_config_path = sleep_config_path
        self.sleep_config = self._load_sleep_config()
        self.bot_instances = {}
        self.sleep_status = {}

        # НОВЫЕ АТРИБУТЫ ДЛЯ УЛУЧШЕНИЙ
        self.is_running = False
        self.start_time = None
        self.performance_metrics = {
            "total_sleep_operations": 0,
            "total_wake_operations": 0,
            "avg_sleep_time_seconds": 0.0,
            "last_operation_time": None,
            "total_errors": 0,
            "validation_errors": 0,
        }
        self.health_status = {
            "system_healthy": True,
            "last_health_check": None,
            "health_issues": [],
        }
        self.event_callbacks = []

    def _load_sleep_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации спящего режима"""
        default_config = {
            "sleep_enabled": True,
            "auto_sleep_after_minutes": 30,
            "wake_up_on_demand": True,
            "save_state_on_sleep": True,
            "bots": {
                "whatsapp": {"enabled": True, "priority": 1},
                "telegram": {"enabled": True, "priority": 2},
                "instagram": {"enabled": True, "priority": 3},
                "max_messenger": {"enabled": True, "priority": 4},
                "analytics": {"enabled": True, "priority": 5},
                "website_navigation": {"enabled": True, "priority": 6},
                "mobile_security_agent": {
                    "enabled": True,
                    "priority": 7,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "mobile_security_agent_enhanced": {
                    "enabled": True,
                    "priority": 8,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "mobile_user_ai_agent": {
                    "enabled": True,
                    "priority": 9,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "child_interface_manager": {
                    "enabled": True,
                    "priority": 10,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "parent_control_panel": {
                    "enabled": True,
                    "priority": 11,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "mobile_navigation_bot": {
                    "enabled": True,
                    "priority": 12,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "website_navigation_bot": {
                    "enabled": True,
                    "priority": 13,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "parental_control_bot": {
                    "enabled": True,
                    "priority": 14,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "parental_control_bot_v2_enhanced": {
                    "enabled": True,
                    "priority": 15,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
                "voice_control_manager": {
                    "enabled": True,
                    "priority": 16,
                    "mode": "sleep",
                    "trigger": {"client_active": True},
                },
            },
        }

        try:
            if Path(self.sleep_config_path).exists():
                with open(self.sleep_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return {**default_config, **config}
            else:
                self._save_sleep_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации спящего режима: {e}")
            return default_config

    def _save_sleep_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации спящего режима"""
        try:
            with open(self.sleep_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации спящего режима: {e}")

    async def register_bot(self, bot_name: str, bot_instance: Any) -> bool:
        """Регистрация бота в менеджере спящего режима"""
        try:
            # ВАЛИДАЦИЯ ВХОДНЫХ ПАРАМЕТРОВ
            if not isinstance(bot_name, str) or not bot_name.strip():
                logger.error("bot_name должен быть непустой строкой")
                self.performance_metrics["validation_errors"] += 1
                return False

            if bot_instance is None:
                logger.error("bot_instance не может быть None")
                self.performance_metrics["validation_errors"] += 1
                return False

            if bot_name in self.bot_instances:
                logger.warning(f"Бот {bot_name} уже зарегистрирован")
                return True

            self.bot_instances[bot_name] = {
                "instance": bot_instance,
                "last_activity": datetime.utcnow(),
                "sleep_state": "awake",
                "sleep_data": {},
                "registration_time": datetime.utcnow(),
                "priority": self.sleep_config.get("bots", {})
                .get(bot_name, {})
                .get("priority", 99),
            }

            # ОБНОВЛЕНИЕ МЕТРИК
            self.performance_metrics["last_operation_time"] = datetime.utcnow()

            # ВЫЗОВ СОБЫТИЙНЫХ CALLBACK'ОВ
            await self._trigger_event(
                "bot_registered",
                bot_name,
                {"bot_instance": str(type(bot_instance))},
            )

            logger.info(
                f"Бот {bot_name} зарегистрирован в менеджере спящего режима"
            )
            return True

        except Exception as e:
            logger.error(f"Ошибка регистрации бота {bot_name}: {e}")
            self.performance_metrics["total_errors"] += 1
            return False

    async def put_bot_to_sleep(
        self, bot_name: str, reason: str = "Manual sleep"
    ) -> bool:
        """Перевод бота в спящий режим"""
        try:
            # ВАЛИДАЦИЯ ВХОДНЫХ ПАРАМЕТРОВ
            if not isinstance(bot_name, str) or not bot_name.strip():
                logger.error("bot_name должен быть непустой строкой")
                self.performance_metrics["validation_errors"] += 1
                return False

            if not isinstance(reason, str):
                logger.error("reason должен быть строкой")
                self.performance_metrics["validation_errors"] += 1
                return False

            if bot_name not in self.bot_instances:
                logger.warning(f"Бот {bot_name} не зарегистрирован")
                return False

            bot_info = self.bot_instances[bot_name]
            bot_instance = bot_info["instance"]

            # Проверка, что бот не уже в спящем режиме
            if bot_info["sleep_state"] == "sleeping":
                logger.info(f"Бот {bot_name} уже в спящем режиме")
                return True

            # Сохранение состояния бота
            sleep_data = await self._save_bot_state(bot_name, bot_instance)

            # Остановка бота
            if hasattr(bot_instance, "stop"):
                await bot_instance.stop()

            # Обновление состояния
            bot_info["sleep_state"] = "sleeping"
            bot_info["sleep_data"] = sleep_data
            bot_info["sleep_time"] = datetime.utcnow()
            bot_info["sleep_reason"] = reason

            self.sleep_status[bot_name] = {
                "status": "sleeping",
                "sleep_time": bot_info["sleep_time"].isoformat(),
                "reason": reason,
                "data_saved": len(sleep_data) > 0,
            }

            # ОБНОВЛЕНИЕ МЕТРИК ПРОИЗВОДИТЕЛЬНОСТИ
            self.performance_metrics["total_sleep_operations"] += 1
            self.performance_metrics["last_operation_time"] = datetime.utcnow()

            # ВЫЗОВ СОБЫТИЙНЫХ CALLBACK'ОВ
            await self._trigger_event(
                "bot_sleep",
                bot_name,
                {
                    "reason": reason,
                    "sleep_time": bot_info["sleep_time"].isoformat(),
                },
            )

            logger.info(f"Бот {bot_name} переведен в спящий режим: {reason}")
            return True

        except Exception as e:
            logger.error(
                f"Ошибка перевода бота {bot_name} в спящий режим: {e}"
            )
            return False

    async def wake_up_bot(self, bot_name: str) -> bool:
        """Пробуждение бота из спящего режима"""
        try:
            if bot_name not in self.bot_instances:
                logger.warning(f"Бот {bot_name} не зарегистрирован")
                return False

            bot_info = self.bot_instances[bot_name]

            # Проверка, что бот в спящем режиме
            if bot_info["sleep_state"] != "sleeping":
                logger.info(f"Бот {bot_name} не в спящем режиме")
                return True

            # Восстановление состояния бота
            await self._restore_bot_state(bot_name, bot_info["sleep_data"])

            # Запуск бота
            bot_instance = bot_info["instance"]
            if hasattr(bot_instance, "start"):
                success = await bot_instance.start()
                if not success:
                    logger.error(f"Ошибка запуска бота {bot_name}")
                    return False

            # Обновление состояния
            bot_info["sleep_state"] = "awake"
            bot_info["last_activity"] = datetime.utcnow()
            bot_info["wake_up_time"] = datetime.utcnow()

            self.sleep_status[bot_name] = {
                "status": "awake",
                "wake_up_time": bot_info["wake_up_time"].isoformat(),
                "sleep_duration": (
                    bot_info["wake_up_time"] - bot_info["sleep_time"]
                ).total_seconds(),
            }

            logger.info(f"Бот {bot_name} пробужден из спящего режима")
            return True

        except Exception as e:
            logger.error(f"Ошибка пробуждения бота {bot_name}: {e}")
            return False

    async def _save_bot_state(
        self, bot_name: str, bot_instance: Any
    ) -> Dict[str, Any]:
        """Сохранение состояния бота"""
        try:
            state_data = {
                "bot_name": bot_name,
                "timestamp": datetime.utcnow().isoformat(),
                "config": getattr(bot_instance, "config", {}),
                "stats": getattr(bot_instance, "stats", {}),
                "running": getattr(bot_instance, "running", False),
            }

            # Сохранение в файл
            state_file = f"sleep_state_{bot_name}.json"
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Состояние бота {bot_name} сохранено в {state_file}")
            return state_data

        except Exception as e:
            logger.error(f"Ошибка сохранения состояния бота {bot_name}: {e}")
            return {}

    async def _restore_bot_state(
        self, bot_name: str, sleep_data: Dict[str, Any]
    ) -> bool:
        """Восстановление состояния бота"""
        try:
            if not sleep_data:
                logger.warning(
                    f"Нет данных для восстановления состояния бота {bot_name}"
                )
                return False

            # Восстановление конфигурации
            if "config" in sleep_data:
                bot_instance = self.bot_instances[bot_name]["instance"]
                if hasattr(bot_instance, "config"):
                    bot_instance.config.update(sleep_data["config"])

            logger.info(f"Состояние бота {bot_name} восстановлено")
            return True

        except Exception as e:
            logger.error(
                f"Ошибка восстановления состояния бота {bot_name}: {e}"
            )
            return False

    async def put_all_bots_to_sleep(
        self, reason: str = "System sleep"
    ) -> Dict[str, bool]:
        """Перевод всех ботов в спящий режим"""
        print("😴 Перевод всех мессенджер ботов в спящий режим...")

        results = {}
        for bot_name in self.bot_instances:
            if (
                self.sleep_config["bots"]
                .get(bot_name, {})
                .get("enabled", True)
            ):
                success = await self.put_bot_to_sleep(bot_name, reason)
                results[bot_name] = success
                if success:
                    print(f"✅ {bot_name}: Переведен в спящий режим")
                else:
                    print(f"❌ {bot_name}: Ошибка перевода в спящий режим")

        successful_sleeps = sum(1 for success in results.values() if success)
        total_bots = len(results)

        print(
            f"📊 Переведено в спящий режим: {successful_sleeps}/{total_bots}"
        )
        return results

    async def wake_up_all_bots(self) -> Dict[str, bool]:
        """Пробуждение всех ботов"""
        print("🌅 Пробуждение всех мессенджер ботов...")

        results = {}
        for bot_name in self.bot_instances:
            if (
                self.sleep_config["bots"]
                .get(bot_name, {})
                .get("enabled", True)
            ):
                success = await self.wake_up_bot(bot_name)
                results[bot_name] = success
                if success:
                    print(f"✅ {bot_name}: Пробужден")
                else:
                    print(f"❌ {bot_name}: Ошибка пробуждения")

        successful_wake_ups = sum(1 for success in results.values() if success)
        total_bots = len(results)

        print(f"📊 Пробуждено ботов: {successful_wake_ups}/{total_bots}")
        return results

    async def get_sleep_status(self) -> Dict[str, Any]:
        """Получение статуса спящего режима"""
        return {
            "sleep_enabled": self.sleep_config["sleep_enabled"],
            "total_bots": len(self.bot_instances),
            "sleeping_bots": len(
                [
                    b
                    for b in self.bot_instances.values()
                    if b["sleep_state"] == "sleeping"
                ]
            ),
            "awake_bots": len(
                [
                    b
                    for b in self.bot_instances.values()
                    if b["sleep_state"] == "awake"
                ]
            ),
            "bot_status": self.sleep_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def auto_sleep_check(self) -> None:
        """Автоматическая проверка необходимости перевода в спящий режим"""
        if not self.sleep_config["sleep_enabled"]:
            return

        auto_sleep_minutes = self.sleep_config.get(
            "auto_sleep_after_minutes", 30
        )
        current_time = datetime.utcnow()

        for bot_name, bot_info in self.bot_instances.items():
            if bot_info["sleep_state"] == "awake":
                last_activity = bot_info["last_activity"]
                inactive_minutes = (
                    current_time - last_activity
                ).total_seconds() / 60

                if inactive_minutes >= auto_sleep_minutes:
                    await self.put_bot_to_sleep(
                        bot_name,
                        f"Auto sleep after {inactive_minutes:.1f} "
                        f"minutes of inactivity",
                    )

    def generate_sleep_report(self) -> Dict[str, Any]:
        """Генерация отчета о спящем режиме"""
        sleeping_bots = [
            name
            for name, info in self.bot_instances.items()
            if info["sleep_state"] == "sleeping"
        ]
        awake_bots = [
            name
            for name, info in self.bot_instances.items()
            if info["sleep_state"] == "awake"
        ]

        report = {
            "summary": {
                "total_bots": len(self.bot_instances),
                "sleeping_bots": len(sleeping_bots),
                "awake_bots": len(awake_bots),
                "sleep_enabled": self.sleep_config["sleep_enabled"],
            },
            "sleeping_bots": sleeping_bots,
            "awake_bots": awake_bots,
            "config": self.sleep_config,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Сохранение отчета
        with open("sleep_mode_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def get_status(self) -> str:
        """Получение статуса SleepModeManager"""
        try:
            if hasattr(self, "is_running") and self.is_running:
                return "running"
            else:
                return "stopped"
        except Exception:
            return "unknown"

    def start_sleep(self) -> bool:
        """Запуск системы спящего режима"""
        try:
            self.is_running = True
            logger.info("Система спящего режима запущена")
            return True
        except Exception as e:
            logger.error(f"Ошибка запуска системы спящего режима: {e}")
            return False

    def stop_sleep(self) -> bool:
        """Остановка системы спящего режима"""
        try:
            self.is_running = False
            logger.info("Система спящего режима остановлена")
            return True
        except Exception as e:
            logger.error(f"Ошибка остановки системы спящего режима: {e}")
            return False

    def get_sleep_info(self) -> Dict[str, Any]:
        """Получение информации о системе спящего режима"""
        try:
            return {
                "is_running": getattr(self, "is_running", False),
                "registered_bots": len(self.bot_instances),
                "sleep_config_loaded": self.sleep_config is not None,
                "sleep_status": getattr(self, "sleep_status", {}),
                "config_path": str(getattr(self, "config_path", "")),
                "sleep_data_path": str(getattr(self, "sleep_data_path", "")),
                "auto_sleep_enabled": (
                    self.sleep_config.get("auto_sleep", {}).get(
                        "enabled", False
                    )
                    if self.sleep_config
                    else False
                ),
                "sleep_threshold": (
                    self.sleep_config.get("auto_sleep", {}).get("threshold", 0)
                    if self.sleep_config
                    else 0
                ),
            }
        except Exception as e:
            logger.error(
                f"Ошибка получения информации о системе спящего режима: {e}"
            )
            return {
                "is_running": False,
                "registered_bots": 0,
                "sleep_config_loaded": False,
                "sleep_status": {},
                "config_path": "",
                "sleep_data_path": "",
                "auto_sleep_enabled": False,
                "sleep_threshold": 0,
                "error": str(e),
            }

    # ==================== НОВЫЕ МЕТОДЫ ДЛЯ УЛУЧШЕНИЙ ====================

    async def start_system(self) -> bool:
        """Запуск системы спящего режима"""
        try:
            if self.is_running:
                logger.info("Система уже запущена")
                return True

            self.is_running = True
            self.start_time = datetime.utcnow()

            # ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМЫ
            await self._check_system_health()

            # ВЫЗОВ СОБЫТИЙНЫХ CALLBACK'ОВ
            await self._trigger_event(
                "system_started",
                "system",
                {"start_time": self.start_time.isoformat()},
            )

            logger.info("Система спящего режима запущена")
            return True
        except Exception as e:
            logger.error(f"Ошибка запуска системы: {e}")
            self.performance_metrics["total_errors"] += 1
            return False

    async def stop_system(self) -> bool:
        """Остановка системы спящего режима"""
        try:
            if not self.is_running:
                logger.info("Система уже остановлена")
                return True

            # ВЫЗОВ СОБЫТИЙНЫХ CALLBACK'ОВ
            await self._trigger_event(
                "system_stopping",
                "system",
                {"stop_time": datetime.utcnow().isoformat()},
            )

            self.is_running = False

            logger.info("Система спящего режима остановлена")
            return True
        except Exception as e:
            logger.error(f"Ошибка остановки системы: {e}")
            self.performance_metrics["total_errors"] += 1
            return False

    async def _check_system_health(self) -> bool:
        """Проверка здоровья системы"""
        try:
            health_issues = []

            # Проверяем доступность файловой системы
            try:
                Path(self.sleep_config_path).parent.mkdir(
                    parents=True, exist_ok=True
                )
                test_file = (
                    Path(self.sleep_config_path).parent / "health_check.tmp"
                )
                test_file.write_text("health_check")
                test_file.unlink()
            except Exception as e:
                health_issues.append(f"Файловая система недоступна: {e}")

            # Проверяем конфигурацию
            if not self.sleep_config:
                health_issues.append("Конфигурация не загружена")

            # Проверяем количество ошибок
            if self.performance_metrics["validation_errors"] > 10:
                health_issues.append(
                    f"Слишком много ошибок валидации: "
                    f"{self.performance_metrics['validation_errors']}"
                )

            # Обновляем статус здоровья
            self.health_status = {
                "system_healthy": len(health_issues) == 0,
                "last_health_check": datetime.utcnow(),
                "health_issues": health_issues,
            }

            if health_issues:
                logger.warning(f"Проблемы здоровья системы: {health_issues}")
            else:
                logger.debug("Система здорова")

            return len(health_issues) == 0
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья системы: {e}")
            return False

    async def _trigger_event(
        self, event_type: str, bot_name: str, data: Dict[str, Any]
    ) -> None:
        """Вызов событийных callback'ов"""
        try:
            for callback in self.event_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, bot_name, data)
                    else:
                        callback(event_type, bot_name, data)
                except Exception as e:
                    logger.error(
                        f"Ошибка в callback для события {event_type}: {e}"
                    )
        except Exception as e:
            logger.error(f"Ошибка вызова событий: {e}")

    def add_event_callback(
        self, callback: Callable[[str, str, Dict[str, Any]], None]
    ) -> bool:
        """Добавление callback для событий"""
        try:
            if not callable(callback):
                logger.error("callback должен быть вызываемым объектом")
                self.performance_metrics["validation_errors"] += 1
                return False

            self.event_callbacks.append(callback)
            logger.info("Callback для событий добавлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления callback: {e}")
            self.performance_metrics["total_errors"] += 1
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        try:
            uptime = 0
            if self.start_time:
                uptime = (datetime.utcnow() - self.start_time).total_seconds()

            return {
                "uptime_seconds": uptime,
                "total_sleep_operations": self.performance_metrics[
                    "total_sleep_operations"
                ],
                "total_wake_operations": self.performance_metrics[
                    "total_wake_operations"
                ],
                "total_operations": self.performance_metrics[
                    "total_sleep_operations"
                ]
                + self.performance_metrics["total_wake_operations"],
                "total_errors": self.performance_metrics["total_errors"],
                "validation_errors": self.performance_metrics[
                    "validation_errors"
                ],
                "last_operation_time": (
                    self.performance_metrics["last_operation_time"].isoformat()
                    if self.performance_metrics["last_operation_time"]
                    else None
                ),
                "registered_bots": len(self.bot_instances),
                "event_callbacks": len(self.event_callbacks),
                "is_running": self.is_running,
                "health_status": self.health_status.copy(),
            }
        except Exception as e:
            logger.error(
                f"Ошибка получения статистики производительности: {e}"
            )
            return {}

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_system()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_system()
        if exc_type:
            logger.error(f"Ошибка в контексте: {exc_val}")
        return False


class TestBot:
    """Тестовый бот для демонстрации работы менеджера спящего режима"""

    def __init__(self, name: str = "TestBot"):
        self.name = name
        self.config = {"test": True}
        self.stats = {"test_count": 0}
        self.running = False

    async def start(self) -> bool:
        """Запуск тестового бота"""
        self.running = True
        return True

    async def stop(self) -> bool:
        """Остановка тестового бота"""
        self.running = False
        return True

    def get_info(self) -> Dict[str, Any]:
        """Получение информации о тестовом боте"""
        return {
            "name": self.name,
            "running": self.running,
            "config": self.config,
            "stats": self.stats,
        }


async def test_sleep_mode_manager():
    """Тестирование менеджера спящего режима"""
    print("🧪 Тестирование SleepModeManager...")

    # Создание менеджера
    sleep_manager = SleepModeManager()

    # Создание тестовых ботов

    # Регистрация тестовых ботов
    test_bots = {
        "whatsapp": TestBot("TestWhatsAppBot"),
        "telegram": TestBot("TestTelegramBot"),
        "instagram": TestBot("TestInstagramBot"),
        "max_messenger": TestBot("TestMaxBot"),
        "analytics": TestBot("TestAnalyticsBot"),
        "website_navigation": TestBot("TestWebsiteBot"),
    }

    for name, bot in test_bots.items():
        await sleep_manager.register_bot(name, bot)

    print(f"✅ Зарегистрировано {len(test_bots)} тестовых ботов")

    # Тест перевода в спящий режим
    sleep_results = await sleep_manager.put_all_bots_to_sleep("Test sleep")
    successful_sleeps = sum(1 for success in sleep_results.values() if success)
    print(
        f"✅ Переведено в спящий режим: "
        f"{successful_sleeps}/{len(sleep_results)}"
    )

    # Тест пробуждения
    wake_results = await sleep_manager.wake_up_all_bots()
    successful_wake_ups = sum(
        1 for success in wake_results.values() if success
    )
    print(f"✅ Пробуждено ботов: {successful_wake_ups}/{len(wake_results)}")

    # Тест статуса
    status = await sleep_manager.get_sleep_status()
    print(
        f"✅ Статус: {status['awake_bots']} активных, "
        f"{status['sleeping_bots']} спящих"
    )

    # Генерация отчета
    report = sleep_manager.generate_sleep_report()
    print(f"✅ Отчет сгенерирован: {report['summary']['total_bots']} ботов")

    return successful_sleeps == len(test_bots) and successful_wake_ups == len(
        test_bots
    )


async def main():
    """Главная функция тестирования"""
    success = await test_sleep_mode_manager()

    if success:
        print("\n✅ Тестирование SleepModeManager прошло успешно!")
        return 0
    else:
        print("\n❌ Тестирование SleepModeManager не прошло!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

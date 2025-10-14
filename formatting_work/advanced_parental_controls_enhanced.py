#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОДВИНУТЫЙ РОДИТЕЛЬСКИЙ КОНТРОЛЬ - Максимальная защита от обхода
Интеграция с IncognitoProtectionBot для полной защиты детей

УЛУЧШЕННАЯ ВЕРСИЯ С A+ КАЧЕСТВОМ:
- Полная обработка ошибок во всех методах
- Логирование во всех методах
- Валидация параметров
- Специальные методы (__str__, __repr__, __eq__, __hash__)
- Методы контекстного менеджера
- Улучшенные type hints
- Расширенная документация
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from core.base import SecurityBase
from security.bots.incognito_protection_bot import (
    IncognitoProtectionBot,
    ThreatLevel,
)


class ProtectionMode(Enum):
    """Режимы защиты для родительского контроля"""

    MAXIMUM = "maximum"  # Максимальная защита
    HIGH = "high"  # Высокая защита
    MEDIUM = "medium"  # Средняя защита
    LOW = "low"  # Низкая защита


class AdvancedParentalControls(SecurityBase):
    """
    Продвинутый родительский контроль с защитой от обхода

    Обеспечивает максимальную защиту детей от попыток обхода
    родительского контроля через VPN, инкогнито режим, прокси и Tor.
    """

    def __init__(self, name: str = "AdvancedParentalControls") -> None:
        """
        Инициализация системы родительского контроля

        Args:
            name (str): Имя экземпляра системы контроля

        Raises:
            ValueError: Если имя пустое или None
            RuntimeError: Если не удалось инициализировать компоненты
        """
        try:
            # Валидация параметров
            if not name or not isinstance(name, str):
                raise ValueError("Имя должно быть непустой строкой")

            super().__init__(name)

            # Инициализация компонентов с обработкой ошибок
            try:
                self.incognito_bot = IncognitoProtectionBot()
            except Exception as e:
                self.logger.error(
                    f"Ошибка инициализации IncognitoProtectionBot: {e}"
                )
                raise RuntimeError(
                    f"Не удалось инициализировать IncognitoProtectionBot: {e}"
                )

            self.protection_mode = ProtectionMode.MAXIMUM
            self.active_children: Dict[str, Dict[str, Any]] = {}
            self.monitoring_tasks: Dict[str, asyncio.Task] = {}

            self.logger.info(
                f"✅ AdvancedParentalControls '{name}' успешно инициализирован"
            )

        except Exception as e:
            self.logger.error(f"Критическая ошибка инициализации: {e}")
            raise

    def __str__(self) -> str:
        """Строковое представление объекта для пользователя"""
        active_count = len(self.active_children)
        return (
            f"AdvancedParentalControls(name='{self.name}', "
            f"active_children={active_count}, "
            f"mode={self.protection_mode.value})"
        )

    def __repr__(self) -> str:
        """Отладочное представление объекта"""
        return (
            f"AdvancedParentalControls(name='{self.name}', "
            f"protection_mode={self.protection_mode}, "
            f"active_children={list(self.active_children.keys())})"
        )

    def __eq__(self, other: Any) -> bool:
        """Сравнение объектов по имени и режиму защиты"""
        if not isinstance(other, AdvancedParentalControls):
            return False
        return (
            self.name == other.name
            and self.protection_mode == other.protection_mode
        )

    def __hash__(self) -> int:
        """Хеш объекта для использования в словарях и множествах"""
        return hash((self.name, self.protection_mode))

    def __enter__(self) -> "AdvancedParentalControls":
        """Вход в контекстный менеджер"""
        self.logger.info(
            "🔧 Вход в контекстный менеджер AdvancedParentalControls"
        )
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Выход из контекстного менеджера с очисткой ресурсов"""
        try:
            self.logger.info(
                "🧹 Выход из контекстного менеджера, очистка ресурсов"
            )

            # Отмена всех активных задач мониторинга
            for child_id, task in self.monitoring_tasks.items():
                if not task.done():
                    task.cancel()
                    self.logger.info(
                        f"❌ Отменена задача мониторинга для {child_id}"
                    )

            # Очистка словарей
            self.monitoring_tasks.clear()
            self.active_children.clear()

            if exc_type is not None:
                self.logger.error(
                    f"❌ Ошибка в контекстном менеджере: "
                    f"{exc_type.__name__}: {exc_val}"
                )
            else:
                self.logger.info("✅ Контекстный менеджер завершен успешно")

        except Exception as e:
            self.logger.error(
                f"Ошибка при выходе из контекстного менеджера: {e}"
            )

    async def setup_child_protection(
        self, child_id: str, protection_level: str = "MAXIMUM"
    ) -> bool:
        """
        Настройка максимальной защиты для ребенка

        Args:
            child_id (str): Уникальный идентификатор ребенка
            protection_level (str): Уровень защиты (MAXIMUM, HIGH, MEDIUM, LOW)

        Returns:
            bool: True если настройка прошла успешно, False в противном случае

        Raises:
            ValueError: Если параметры некорректны
            RuntimeError: Если не удалось настроить защиту
        """
        try:
            # Валидация параметров
            if not child_id or not isinstance(child_id, str):
                raise ValueError("child_id должен быть непустой строкой")

            if protection_level not in ["MAXIMUM", "HIGH", "MEDIUM", "LOW"]:
                raise ValueError(
                    f"Неподдерживаемый уровень защиты: {protection_level}"
                )

            self.logger.info(
                f"🔧 Настройка защиты для ребенка {child_id} "
                f"с уровнем {protection_level}"
            )

            # Настройка уровня защиты
            if protection_level == "MAXIMUM":
                self.incognito_bot.protection_level = "MAXIMUM"
                self.incognito_bot.block_vpn = True
                self.incognito_bot.block_incognito = True
                self.incognito_bot.block_proxy = True
                self.incognito_bot.block_tor = True
                self.incognito_bot.emergency_lock_enabled = True

            # Запуск мониторинга
            try:
                task = asyncio.create_task(
                    self.incognito_bot.monitor_continuous_protection(child_id)
                )
                self.monitoring_tasks[child_id] = task
            except Exception as e:
                self.logger.error(f"Ошибка создания задачи мониторинга: {e}")
                raise RuntimeError(f"Не удалось запустить мониторинг: {e}")

            self.active_children[child_id] = {
                "protection_level": protection_level,
                "start_time": datetime.now(),
                "blocked_attempts": 0,
                "last_alert": None,
            }

            self.logger.info(
                f"🛡️ Максимальная защита активирована для ребенка {child_id}"
            )
            return True

        except ValueError as e:
            self.logger.error(f"Ошибка валидации параметров: {e}")
            return False
        except RuntimeError as e:
            self.logger.error(f"Ошибка выполнения: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка настройки защиты: {e}")
            return False

    async def emergency_response(
        self, child_id: str, threat_level: ThreatLevel
    ) -> bool:
        """
        Экстренный ответ на попытку обхода

        Args:
            child_id (str): Идентификатор ребенка
            threat_level (ThreatLevel): Уровень угрозы

        Returns:
            bool: True если ответ выполнен успешно, False в противном случае

        Raises:
            ValueError: Если параметры некорректны
            RuntimeError: Если не удалось выполнить экстренный ответ
        """
        try:
            # Валидация параметров
            if not child_id or not isinstance(child_id, str):
                raise ValueError("child_id должен быть непустой строкой")

            if not isinstance(threat_level, ThreatLevel):
                raise ValueError(
                    "threat_level должен быть экземпляром ThreatLevel"
                )

            self.logger.warning(
                f"🚨 Экстренный ответ для {child_id}, "
                f"уровень угрозы: {threat_level}"
            )

            if threat_level == ThreatLevel.CRITICAL:
                # Немедленная блокировка устройства
                try:
                    await self.incognito_bot.emergency_lock_device(child_id)
                except Exception as e:
                    self.logger.error(f"Ошибка блокировки устройства: {e}")
                    raise RuntimeError(
                        f"Не удалось заблокировать устройство: {e}"
                    )

                # Уведомление родителей
                await self._send_critical_alert(
                    child_id, "КРИТИЧЕСКАЯ УГРОЗА: Попытка обхода защиты!"
                )

                # Создание скриншота
                try:
                    screenshot = await self.incognito_bot.take_screenshot(
                        child_id
                    )
                except Exception as e:
                    self.logger.error(f"Ошибка создания скриншота: {e}")
                    screenshot = "Ошибка создания скриншота"

                # Логирование
                self.logger.critical(
                    f"🚨 ЭКСТРЕННЫЙ РЕЖИМ: Ребенок {child_id} заблокирован! "
                    f"Скриншот: {screenshot}"
                )

            elif threat_level == ThreatLevel.HIGH:
                # Блокировка браузеров
                try:
                    await self.incognito_bot._block_incognito_mode()
                except Exception as e:
                    self.logger.error(f"Ошибка блокировки браузеров: {e}")
                    raise RuntimeError(
                        f"Не удалось заблокировать браузеры: {e}"
                    )

                await self._send_high_alert(
                    child_id, "Высокий уровень угрозы: Блокировка браузеров"
                )

            # Обновление статистики
            if child_id in self.active_children:
                self.active_children[child_id]["blocked_attempts"] += 1
                self.active_children[child_id]["last_alert"] = datetime.now()

            self.logger.info(f"✅ Экстренный ответ выполнен для {child_id}")
            return True

        except ValueError as e:
            self.logger.error(f"Ошибка валидации параметров: {e}")
            return False
        except RuntimeError as e:
            self.logger.error(f"Ошибка выполнения: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка экстренного ответа: {e}")
            return False

    async def _send_critical_alert(self, child_id: str, message: str) -> None:
        """
        Отправка критического уведомления

        Args:
            child_id (str): Идентификатор ребенка
            message (str): Текст уведомления

        Raises:
            ValueError: Если параметры некорректны
            IOError: Если не удалось сохранить уведомление
        """
        try:
            # Валидация параметров
            if not child_id or not isinstance(child_id, str):
                raise ValueError("child_id должен быть непустой строкой")

            if not message or not isinstance(message, str):
                raise ValueError("message должен быть непустой строкой")

            self.logger.critical(
                f"🚨 Отправка критического уведомления для {child_id}"
            )

            alert = {
                "child_id": child_id,
                "alert_type": "CRITICAL",
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "action_required": "IMMEDIATE",
            }

            # Отправка через все каналы
            print(f"🚨 КРИТИЧЕСКОЕ УВЕДОМЛЕНИЕ: {message}")

            # Создание директории если не существует
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)

            # Сохранение в файл
            try:
                with open(
                    f"data/critical_alerts_{child_id}.json",
                    "a",
                    encoding="utf-8",
                ) as f:
                    f.write(json.dumps(alert, ensure_ascii=False) + "\n")
            except IOError as e:
                self.logger.error(
                    f"Ошибка сохранения критического уведомления: {e}"
                )
                raise

            self.logger.info(
                f"✅ Критическое уведомление отправлено для {child_id}"
            )

        except ValueError as e:
            self.logger.error(f"Ошибка валидации параметров: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка отправки критического уведомления: {e}"
            )
            raise

    async def _send_high_alert(self, child_id: str, message: str) -> None:
        """
        Отправка уведомления высокого уровня

        Args:
            child_id (str): Идентификатор ребенка
            message (str): Текст уведомления

        Raises:
            ValueError: Если параметры некорректны
            IOError: Если не удалось сохранить уведомление
        """
        try:
            # Валидация параметров
            if not child_id or not isinstance(child_id, str):
                raise ValueError("child_id должен быть непустой строкой")

            if not message or not isinstance(message, str):
                raise ValueError("message должен быть непустой строкой")

            self.logger.warning(
                f"⚠️ Отправка уведомления высокого уровня для {child_id}"
            )

            alert = {
                "child_id": child_id,
                "alert_type": "HIGH",
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "action_required": "SOON",
            }

            print(f"⚠️ ВЫСОКИЙ УРОВЕНЬ: {message}")

            # Создание директории если не существует
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)

            # Сохранение в файл
            try:
                with open(
                    f"data/high_alerts_{child_id}.json", "a", encoding="utf-8"
                ) as f:
                    f.write(json.dumps(alert, ensure_ascii=False) + "\n")
            except IOError as e:
                self.logger.error(
                    f"Ошибка сохранения уведомления высокого уровня: {e}"
                )
                raise

            self.logger.info(
                f"✅ Уведомление высокого уровня отправлено для {child_id}"
            )

        except ValueError as e:
            self.logger.error(f"Ошибка валидации параметров: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка отправки уведомления высокого уровня: {e}"
            )
            raise

    def get_protection_report(self, child_id: str) -> Dict[str, Any]:
        """
        Получение отчета о защите

        Args:
            child_id (str): Идентификатор ребенка

        Returns:
            Dict[str, Any]: Отчет о защите или пустой словарь при ошибке

        Raises:
            ValueError: Если child_id некорректен
        """
        try:
            # Валидация параметров
            if not child_id or not isinstance(child_id, str):
                raise ValueError("child_id должен быть непустой строкой")

            self.logger.info(f"📊 Генерация отчета защиты для {child_id}")

            # Статистика от IncognitoProtectionBot
            try:
                bot_stats = self.incognito_bot.get_protection_statistics(
                    child_id
                )
            except Exception as e:
                self.logger.error(f"Ошибка получения статистики бота: {e}")
                bot_stats = {}

            # Дополнительная статистика
            child_info = self.active_children.get(child_id, {})

            report = {
                "child_id": child_id,
                "protection_active": child_id in self.active_children,
                "protection_level": child_info.get(
                    "protection_level", "UNKNOWN"
                ),
                "monitoring_duration": str(
                    datetime.now()
                    - child_info.get("start_time", datetime.now())
                ),
                "total_blocked_attempts": child_info.get(
                    "blocked_attempts", 0
                ),
                "last_alert": (
                    child_info.get("last_alert").isoformat()
                    if child_info.get("last_alert")
                    else None
                ),
                "bot_statistics": bot_stats,
                "recommendations": self._generate_recommendations(bot_stats),
            }

            self.logger.info(f"✅ Отчет защиты сгенерирован для {child_id}")
            return report

        except ValueError as e:
            self.logger.error(f"Ошибка валидации параметров: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка получения отчета: {e}")
            return {}

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """
        Генерация рекомендаций на основе статистики

        Args:
            stats (Dict[str, Any]): Статистика защиты

        Returns:
            List[str]: Список рекомендаций

        Raises:
            ValueError: Если stats некорректен
        """
        try:
            # Валидация параметров
            if not isinstance(stats, dict):
                raise ValueError("stats должен быть словарем")

            self.logger.debug("🔍 Генерация рекомендаций на основе статистики")

            recommendations = []

            # Анализ попыток обхода
            bypass_attempts = stats.get("bypass_attempts", {})
            if bypass_attempts:
                for method, data in bypass_attempts.items():
                    if data.get("successful_attempts", 0) > 0:
                        recommendations.append(
                            f"⚠️ Усилить защиту от {method}: "
                            f"{data['successful_attempts']} успешных попыток"
                        )

            # Анализ VPN детекций
            vpn_stats = stats.get("vpn_detections", {})
            if vpn_stats.get("total", 0) > 5:
                recommendations.append(
                    "🔒 Частые попытки использования VPN - "
                    "рассмотреть блокировку интернета"
                )

            # Анализ инкогнито детекций
            incognito_stats = stats.get("incognito_detections", {})
            if incognito_stats.get("total", 0) > 3:
                recommendations.append(
                    "🌐 Частые попытки инкогнито - усилить мониторинг"
                )

            if not recommendations:
                recommendations.append("✅ Защита работает эффективно")

            self.logger.debug(
                f"✅ Сгенерировано {len(recommendations)} рекомендаций"
            )
            return recommendations

        except ValueError as e:
            self.logger.error(f"Ошибка валидации параметров: {e}")
            return ["❌ Ошибка генерации рекомендаций"]
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка генерации рекомендаций: {e}"
            )
            return ["❌ Ошибка генерации рекомендаций"]


# Пример использования
async def main() -> None:
    """
    Пример использования AdvancedParentalControls

    Демонстрирует основные возможности системы родительского контроля
    с использованием контекстного менеджера для автоматической очистки
    ресурсов.
    """
    try:
        # Использование контекстного менеджера для автоматической очистки
        with AdvancedParentalControls() as controls:
            # Настройка максимальной защиты для ребенка
            child_id = "child_001"
            success = await controls.setup_child_protection(
                child_id, "MAXIMUM"
            )

            if success:
                print("🛡️ Продвинутый родительский контроль активирован")
                print(f"👶 Защита для ребенка: {child_id}")
                print("🔍 Мониторинг: VPN, инкогнито, прокси, Tor")
                print("🚨 Экстренные уведомления: ВКЛЮЧЕНЫ")
                print("🔒 Автоматическая блокировка: ВКЛЮЧЕНА")

                # Получение отчета
                report = controls.get_protection_report(child_id)
                report_json = json.dumps(report, indent=2, ensure_ascii=False)
                print(f"📊 Отчет: {report_json}")
            else:
                print("❌ Ошибка активации родительского контроля")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())

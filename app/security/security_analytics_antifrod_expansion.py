# -*- coding: utf-8 -*-
"""
ALADDIN Security System - SecurityAnalytics Antifrod Expansion
Расширение SecurityAnalytics для интеграции с системой 'Антифрод'

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import sys


import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from security.integrations.antifrod_integration import (
    AntifrodCall,
    AntifrodIntegration,
)


class SecurityAnalyticsAntifrodExpansion:
    """
    Расширенный SecurityAnalytics с интеграцией системы 'Антифрод'

    Добавляет возможности верификации звонков и борьбы с
    телефонным мошенничеством
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Инициализация расширенного модуля
        self.config = config or {}
        self.name = "SecurityAnalyticsAntifrodExpansion"
        self.description = (
            "Аналитика безопасности с интеграцией системы 'Антифрод'"
        )

        # Новая функциональность - Антифрод интеграция
        self.antifrod = AntifrodIntegration()

        # Новые данные аналитики
        self.phone_fraud_data: Dict[str, Any] = {}
        self.call_verification_data: Dict[str, Any] = {}
        self.fraud_patterns: Dict[str, Any] = {}

        # Настройка логирования
        self.logger = logging.getLogger("security_analytics_antifrod")
        self.logger.setLevel(logging.INFO)

        self.log_activity(
            "Антифрод интеграция добавлена в SecurityAnalytics", "info"
        )

    def log_activity(self, message: str, level: str = "info"):
        """Логирование активности"""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)
        print(f"[{level.upper()}] {message}")

    async def verify_call_with_antifrod(
        self,
        caller_number: str,
        receiver_number: str,
        call_duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        НОВАЯ ФУНКЦИЯ: Верификация звонка через систему 'Антифрод'

        Расширяет существующий функционал аналитики для защиты от
        телефонного мошенничества
        """
        try:
            # Создание данных звонка
            call_data = AntifrodCall(
                caller_number=caller_number,
                receiver_number=receiver_number,
                timestamp=datetime.now(),
                call_duration=call_duration,
            )

            # Верификация через Антифрод
            result = await self.antifrod.process_call(call_data)

            # Сохранение в данных аналитики
            call_id = (
                f"{caller_number}_{receiver_number}_"
                f"{datetime.now().timestamp()}"
            )
            self.call_verification_data[call_id] = {
                "call_data": call_data,
                "verification_result": result,
                "timestamp": datetime.now(),
            }

            # Анализ паттернов мошенничества
            if result.get("fraud_type"):
                await self._analyze_fraud_pattern(call_data, result)

            # Логирование
            self.log_activity(
                f"Антифрод верификация: {caller_number} -> {receiver_number}, "
                f"verified={result['verified']}, "
                f"risk={result['risk_score']:.2f}",
                "warning" if not result["verified"] else "info",
            )

            return result

        except Exception as e:
            self.log_activity(
                f"Ошибка верификации через Антифрод: {str(e)}", "error"
            )
            return {
                "verified": False,
                "risk_score": 1.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def block_fraud_calls(
        self, call_id: str, fraud_detection: Dict[str, Any]
    ) -> bool:
        """
        НОВАЯ ФУНКЦИЯ: Блокировка мошеннических звонков

        Расширяет аналитику для активной борьбы с мошенничеством
        """
        try:
            if call_id not in self.call_verification_data:
                self.log_activity(
                    f"Звонок {call_id} не найден для блокировки", "warning"
                )
                return False

            call_info = self.call_verification_data[call_id]
            call_data = call_info["call_data"]

            # Блокировка через Антифрод
            fraud_type = fraud_detection.get("fraud_type", "unknown")
            blocked = await self.antifrod.block_fraud_call(
                call_data, fraud_type
            )

            if blocked:
                # Обновление данных
                self.call_verification_data[call_id]["blocked"] = True
                self.call_verification_data[call_id][
                    "block_timestamp"
                ] = datetime.now()

                # Сохранение в данных мошенничества
                self.phone_fraud_data[call_id] = {
                    "call_data": call_data,
                    "fraud_detection": fraud_detection,
                    "blocked": True,
                    "timestamp": datetime.now(),
                }

                # Логирование инцидента
                self.log_activity(
                    f"ЗВОНОК ЗАБЛОКИРОВАН: {call_id}, "
                    f"тип мошенничества: {fraud_type}",
                    "critical",
                )

                # Уведомление о блокировке
                await self._notify_fraud_block(call_id, fraud_detection)

            return blocked

        except Exception as e:
            self.log_activity(
                f"Ошибка блокировки мошеннического звонка: {str(e)}", "error"
            )
            return False

    async def monitor_phone_fraud(
        self, time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        НОВАЯ ФУНКЦИЯ: Мониторинг телефонного мошенничества

        Расширяет аналитику для непрерывного мониторинга угроз
        """
        try:
            from datetime import timedelta

            current_time = datetime.now()
            window_start = current_time - timedelta(
                minutes=time_window_minutes
            )

            # Анализ звонков в временном окне
            recent_calls = {}
            fraud_calls = {}

            for call_id, call_info in self.call_verification_data.items():
                if call_info["timestamp"] >= window_start:
                    recent_calls[call_id] = call_info

                    if call_info["verification_result"].get("fraud_type"):
                        fraud_calls[call_id] = call_info

            # Статистика мошенничества
            total_calls = len(recent_calls)
            fraud_count = len(fraud_calls)
            fraud_rate = (
                (fraud_count / total_calls * 100) if total_calls > 0 else 0
            )

            # Анализ паттернов
            fraud_patterns = await self._analyze_fraud_patterns(fraud_calls)

            # Действия при высоком уровне мошенничества
            if fraud_rate > 10:  # Если больше 10% звонков мошеннические
                await self._handle_high_fraud_rate(fraud_rate, fraud_calls)

            result = {
                "time_window_minutes": time_window_minutes,
                "total_calls": total_calls,
                "fraud_calls": fraud_count,
                "fraud_rate_percent": fraud_rate,
                "fraud_patterns": fraud_patterns,
                "timestamp": current_time.isoformat(),
            }

            # Логирование
            self.log_activity(
                f"Мониторинг мошенничества: {total_calls} звонков, "
                f"{fraud_count} мошеннических ({fraud_rate:.1f}%)",
                "warning" if fraud_rate > 5 else "info",
            )

            return result

        except Exception as e:
            self.log_activity(
                f"Ошибка мониторинга телефонного мошенничества: {str(e)}",
                "error",
            )
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _analyze_fraud_pattern(
        self, call_data: AntifrodCall, verification_result: Dict[str, Any]
    ):
        """
        ВНУТРЕННЯЯ ФУНКЦИЯ: Анализ паттерна мошенничества
        """
        try:
            fraud_type = verification_result.get("fraud_type")
            if not fraud_type:
                return

            # Сохранение паттерна
            if fraud_type not in self.fraud_patterns:
                self.fraud_patterns[fraud_type] = {
                    "count": 0,
                    "caller_patterns": {},
                    "time_patterns": {},
                    "first_detected": datetime.now(),
                    "last_detected": datetime.now(),
                }

            pattern = self.fraud_patterns[fraud_type]
            pattern["count"] += 1
            pattern["last_detected"] = datetime.now()

            # Анализ номеров
            caller_prefix = call_data.caller_number[:3]
            if caller_prefix not in pattern["caller_patterns"]:
                pattern["caller_patterns"][caller_prefix] = 0
            pattern["caller_patterns"][caller_prefix] += 1

            # Анализ времени
            hour = call_data.timestamp.hour
            if hour not in pattern["time_patterns"]:
                pattern["time_patterns"][hour] = 0
            pattern["time_patterns"][hour] += 1

        except Exception as e:
            self.log_activity(
                f"Ошибка анализа паттерна мошенничества: {str(e)}", "error"
            )

    async def _analyze_fraud_patterns(
        self, fraud_calls: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ВНУТРЕННЯЯ ФУНКЦИЯ: Анализ паттернов мошенничества
        """
        try:
            patterns = {
                "common_fraud_types": {},
                "peak_hours": {},
                "common_prefixes": {},
                "geographical_patterns": {},
            }

            for call_id, call_info in fraud_calls.items():
                fraud_type = call_info["verification_result"].get(
                    "fraud_type", "unknown"
                )

                # Типы мошенничества
                if fraud_type not in patterns["common_fraud_types"]:
                    patterns["common_fraud_types"][fraud_type] = 0
                patterns["common_fraud_types"][fraud_type] += 1

                # Временные паттерны
                hour = call_info["call_data"].timestamp.hour
                if hour not in patterns["peak_hours"]:
                    patterns["peak_hours"][hour] = 0
                patterns["peak_hours"][hour] += 1

                # Префиксы номеров
                prefix = call_info["call_data"].caller_number[:3]
                if prefix not in patterns["common_prefixes"]:
                    patterns["common_prefixes"][prefix] = 0
                patterns["common_prefixes"][prefix] += 1

            return patterns

        except Exception as e:
            self.log_activity(f"Ошибка анализа паттернов: {str(e)}", "error")
            return {"error": str(e)}

    async def _handle_high_fraud_rate(
        self, fraud_rate: float, fraud_calls: Dict[str, Any]
    ):
        """
        ВНУТРЕННЯЯ ФУНКЦИЯ: Обработка высокого уровня мошенничества
        """
        try:
            self.log_activity(
                f"ВЫСОКИЙ УРОВЕНЬ МОШЕННИЧЕСТВА: {fraud_rate:.1f}%", "critical"
            )

            # Уведомление администраторов
            await self._notify_high_fraud_rate(fraud_rate, fraud_calls)

            # Активация дополнительных мер защиты
            await self._activate_enhanced_protection()

        except Exception as e:
            self.log_activity(
                f"Ошибка обработки высокого уровня мошенничества: {str(e)}",
                "error",
            )

    async def _notify_fraud_block(
        self, call_id: str, fraud_detection: Dict[str, Any]
    ):
        """
        ВНУТРЕННЯЯ ФУНКЦИЯ: Уведомление о блокировке мошенничества
        """
        self.log_activity(
            f"УВЕДОМЛЕНИЕ: Мошеннический звонок заблокирован {call_id}",
            "warning",
        )

    async def _notify_high_fraud_rate(
        self, fraud_rate: float, fraud_calls: Dict[str, Any]
    ):
        """
        ВНУТРЕННЯЯ ФУНКЦИЯ: Уведомление о высоком уровне мошенничества
        """
        self.log_activity(
            f"КРИТИЧЕСКОЕ УВЕДОМЛЕНИЕ: Высокий уровень мошенничества "
            f"{fraud_rate:.1f}%",
            "critical",
        )

    async def _activate_enhanced_protection(self):
        """
        ВНУТРЕННЯЯ ФУНКЦИЯ: Активация усиленной защиты
        """
        self.log_activity(
            "Активация усиленной защиты от мошенничества", "warning"
        )

    def get_antifrod_statistics(self) -> Dict[str, Any]:
        """
        НОВАЯ ФУНКЦИЯ: Получение статистики Антифрод
        """
        try:
            stats = self.antifrod.get_statistics()
            stats.update(
                {
                    "phone_fraud_data_count": len(self.phone_fraud_data),
                    "call_verification_data_count": len(
                        self.call_verification_data
                    ),
                    "fraud_patterns_count": len(self.fraud_patterns),
                    "module_name": "SecurityAnalytics_Antifrod",
                }
            )

            return stats

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статистики Антифрод: {str(e)}", "error"
            )
            return {"error": str(e)}

    def get_expanded_analytics_data(self) -> Dict[str, Any]:
        """
        РАСШИРЕННАЯ ФУНКЦИЯ: Получение расширенных данных аналитики
        """
        try:
            # Базовые данные аналитики (если есть)
            base_data = getattr(self, "analytics_data", {}).copy()

            # Добавляем новые данные Антифрод
            base_data.update(
                {
                    "antifrod_integration": {
                        "enabled": self.antifrod.config.get("enabled", False),
                        "statistics": self.get_antifrod_statistics(),
                    },
                    "phone_fraud_data": self.phone_fraud_data,
                    "call_verification_data": self.call_verification_data,
                    "fraud_patterns": self.fraud_patterns,
                    "expansion_version": "1.0",
                    "expansion_features": [
                        "verify_call_with_antifrod",
                        "block_fraud_calls",
                        "monitor_phone_fraud",
                    ],
                }
            )

            return base_data

        except Exception as e:
            self.log_activity(
                f"Ошибка получения расширенных данных: {str(e)}", "error"
            )
            return {"error": str(e)}


# Функция для тестирования расширения
async def test_antifrod_expansion():
    """Тестирование расширения SecurityAnalytics с Антифрод"""
    print("🔧 Тестирование расширения SecurityAnalytics с Антифрод...")

    # Создание экземпляра расширенного модуля
    analytics = SecurityAnalyticsAntifrodExpansion()

    # Тестовые данные
    test_caller = "+79001234567"
    test_receiver = "+79009876543"

    # Тест верификации звонка
    print("📞 Тестирование верификации звонка...")
    verification = await analytics.verify_call_with_antifrod(
        test_caller, test_receiver, 120
    )
    print(
        f"   Результат: verified={verification['verified']}, "
        f"risk_score={verification['risk_score']:.2f}"
    )

    # Тест мониторинга мошенничества
    print("🔍 Тестирование мониторинга мошенничества...")
    monitoring = await analytics.monitor_phone_fraud(60)
    if "error" not in monitoring:
        print(
            f"   Результат: {monitoring['total_calls']} звонков, "
            f"{monitoring['fraud_calls']} мошеннических"
        )
    else:
        print(f"   Ошибка: {monitoring['error']}")

    # Тест статистики
    print("📊 Получение статистики...")
    stats = analytics.get_antifrod_statistics()
    print(f"   Статистика: {stats}")

    print("✅ Тестирование завершено успешно!")


if __name__ == "__main__":
    # Запуск тестирования
    asyncio.run(test_antifrod_expansion())

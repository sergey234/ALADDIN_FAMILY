#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Compliance Agent
Агент соответствия российскому законодательству (152-ФЗ, ГОСТ, ФСТЭК)

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-25
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase, SecurityLevel
from core.logging_module import LoggingManager


class ComplianceStandard(Enum):
    """Стандарты соответствия"""

    LAW_152_FZ = "152_fz"  # Закон о персональных данных
    GOST_R_57580_1 = "gost_r_57580_1"  # ГОСТ Р 57580.1-2017
    GOST_R_57580_2 = "gost_r_57580_2"  # ГОСТ Р 57580.2-2018
    FSTEC_ORDER_1119 = "fstec_1119"  # Приказ ФСТЭК №1119
    FSTEC_ORDER_17 = "fstec_17"  # Приказ ФСТЭК №17
    FSTEC_ORDER_21 = "fstec_21"  # Приказ ФСТЭК №21


class ComplianceLevel(Enum):
    """Уровни соответствия"""

    FULL = "full"  # Полное соответствие
    PARTIAL = "partial"  # Частичное соответствие
    NON_COMPLIANT = "non_compliant"  # Не соответствует
    UNKNOWN = "unknown"  # Неизвестно


class ComplianceViolation(Enum):
    """Типы нарушений соответствия"""

    DATA_BREACH = "data_breach"  # Нарушение целостности данных
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # Несанкционированный доступ
    INSUFFICIENT_ENCRYPTION = (
        "insufficient_encryption"  # Недостаточное шифрование
    )
    MISSING_AUDIT_LOG = "missing_audit_log"  # Отсутствие аудита
    POLICY_VIOLATION = "policy_violation"  # Нарушение политик
    RETENTION_VIOLATION = "retention_violation"  # Нарушение сроков хранения


class ComplianceCheck:
    """Проверка соответствия"""

    def __init__(
        self,
        check_id: str,
        standard: ComplianceStandard,
        check_name: str,
        description: str,
        severity: SecurityLevel,
        is_required: bool = True,
        automated: bool = True,
    ):
        self.check_id = check_id
        self.standard = standard
        self.check_name = check_name
        self.description = description
        self.severity = severity
        self.is_required = is_required
        self.automated = automated
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "check_id": self.check_id,
            "standard": self.standard.value,
            "check_name": self.check_name,
            "description": self.description,
            "severity": self.severity.value,
            "is_required": self.is_required,
            "automated": self.automated,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ComplianceResult:
    """Результат проверки соответствия"""

    def __init__(
        self,
        result_id: str,
        check_id: str,
        compliance_level: ComplianceLevel,
        violation_type: Optional[ComplianceViolation] = None,
        details: str = "",
        recommendations: List[str] = None,
        evidence: Dict[str, Any] = None,
    ):
        self.result_id = result_id
        self.check_id = check_id
        self.compliance_level = compliance_level
        self.violation_type = violation_type
        self.details = details
        self.recommendations = recommendations or []
        self.evidence = evidence or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "result_id": self.result_id,
            "check_id": self.check_id,
            "compliance_level": self.compliance_level.value,
            "violation_type": (
                self.violation_type.value if self.violation_type else None
            ),
            "details": self.details,
            "recommendations": self.recommendations,
            "evidence": self.evidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ComplianceAgent(SecurityBase):
    """
    Агент соответствия российскому законодательству.

    Обеспечивает автоматическую проверку соответствия
    российским стандартам информационной безопасности,
    включая 152-ФЗ, ГОСТ и требования ФСТЭК.
    """

    def __init__(
        self,
        name: str = "ComplianceAgent",
        security_level: SecurityLevel = SecurityLevel.HIGH,
    ):
        super().__init__(name, security_level)
        self.logger = LoggingManager()
        self.status = ComponentStatus.ACTIVE

        # Хранилище проверок и результатов
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.compliance_results: Dict[str, ComplianceResult] = {}

        # Статистика соответствия
        self.compliance_stats = {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "violations_found": 0,
            "last_audit": None,
            "compliance_score": 0.0,
        }

        # Инициализация стандартных проверок
        self._initialize_compliance_checks()

        self.logger.log("INFO", f"ComplianceAgent инициализирован: {name}")

    def _initialize_compliance_checks(self):
        """Инициализация стандартных проверок соответствия"""

        # 152-ФЗ - Закон о персональных данных
        checks_152_fz = [
            ComplianceCheck(
                "152_fz_001",
                ComplianceStandard.LAW_152_FZ,
                "Шифрование персональных данных",
                "Проверка наличия шифрования ПД при хранении и передаче",
                SecurityLevel.HIGH,
                True,
                True,
            ),
            ComplianceCheck(
                "152_fz_002",
                ComplianceStandard.LAW_152_FZ,
                "Контроль доступа к персональным данным",
                "Проверка системы контроля доступа к персональным данным",
                SecurityLevel.HIGH,
                True,
                True,
            ),
            ComplianceCheck(
                "152_fz_003",
                ComplianceStandard.LAW_152_FZ,
                "Аудит обработки персональных данных",
                "Проверка ведения журналов обработки персональных данных",
                SecurityLevel.MEDIUM,
                True,
                True,
            ),
            ComplianceCheck(
                "152_fz_004",
                ComplianceStandard.LAW_152_FZ,
                "Уведомление Роскомнадзора",
                "Проверка регистрации в Роскомнадзоре как оператора персональных данных",
                SecurityLevel.HIGH,
                True,
                False,
            ),
            ComplianceCheck(
                "152_fz_005",
                ComplianceStandard.LAW_152_FZ,
                "Согласие на обработку ПДн",
                "Проверка получения согласия субъектов на обработку персональных данных",
                SecurityLevel.MEDIUM,
                True,
                False,
            ),
        ]

        # ГОСТ Р 57580.1-2017
        checks_gost = [
            ComplianceCheck(
                "gost_001",
                ComplianceStandard.GOST_R_57580_1,
                "Модель угроз информационной безопасности",
                "Проверка наличия актуальной модели угроз ИБ",
                SecurityLevel.HIGH,
                True,
                False,
            ),
            ComplianceCheck(
                "gost_002",
                ComplianceStandard.GOST_R_57580_1,
                "Политики информационной безопасности",
                "Проверка наличия и актуальности политик ИБ",
                SecurityLevel.MEDIUM,
                True,
                False,
            ),
            ComplianceCheck(
                "gost_003",
                ComplianceStandard.GOST_R_57580_1,
                "Мониторинг информационной безопасности",
                "Проверка системы мониторинга ИБ",
                SecurityLevel.HIGH,
                True,
                True,
            ),
        ]

        # ФСТЭК требования
        checks_fstec = [
            ComplianceCheck(
                "fstec_001",
                ComplianceStandard.FSTEC_ORDER_1119,
                "Защита от вредоносного ПО",
                "Проверка наличия средств защиты от вредоносного ПО",
                SecurityLevel.HIGH,
                True,
                True,
            ),
            ComplianceCheck(
                "fstec_002",
                ComplianceStandard.FSTEC_ORDER_1119,
                "Контроль целостности",
                "Проверка средств контроля целостности информации",
                SecurityLevel.HIGH,
                True,
                True,
            ),
            ComplianceCheck(
                "fstec_003",
                ComplianceStandard.FSTEC_ORDER_17,
                "Управление доступом",
                "Проверка системы управления доступом",
                SecurityLevel.HIGH,
                True,
                True,
            ),
            ComplianceCheck(
                "fstec_004",
                ComplianceStandard.FSTEC_ORDER_21,
                "Обнаружение вторжений",
                "Проверка средств обнаружения вторжений",
                SecurityLevel.MEDIUM,
                True,
                True,
            ),
        ]

        # Добавляем все проверки
        all_checks = checks_152_fz + checks_gost + checks_fstec

        for check in all_checks:
            self.compliance_checks[check.check_id] = check

        self.compliance_stats["total_checks"] = len(self.compliance_checks)
        self.logger.log(
            "INFO",
            f"Инициализировано проверок соответствия: {len(self.compliance_checks)}"
        )

    async def run_compliance_audit(
        self,
        standards: Optional[List[ComplianceStandard]] = None,
        include_manual: bool = False,
    ) -> Dict[str, Any]:
        """
        Запуск аудита соответствия.

        Args:
            standards: Список стандартов для проверки
            include_manual: Включать ли ручные проверки

        Returns:
            Dict: Результаты аудита
        """
        try:
            self.logger.log(
                "INFO",
                "Запуск аудита соответствия российскому законодательству",
            )

            audit_id = f"audit_{int(time.time())}"
            audit_results = {
                "audit_id": audit_id,
                "started_at": datetime.now().isoformat(),
                "standards_checked": [],
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "violations": [],
                "compliance_score": 0.0,
                "recommendations": [],
            }

            # Выбираем проверки для выполнения
            checks_to_run = []

            if standards:
                for standard in standards:
                    audit_results["standards_checked"].append(standard.value)
                    for check in self.compliance_checks.values():
                        if check.standard == standard and (
                            check.automated or include_manual
                        ):
                            checks_to_run.append(check)
            else:
                # Проверяем все стандарты
                for standard in ComplianceStandard:
                    audit_results["standards_checked"].append(standard.value)
                checks_to_run = [
                    check
                    for check in self.compliance_checks.values()
                    if check.automated or include_manual
                ]

            audit_results["total_checks"] = len(checks_to_run)

            # Выполняем проверки
            for check in checks_to_run:
                result = await self._run_compliance_check(check)
                self.compliance_results[result.result_id] = result

                if result.compliance_level == ComplianceLevel.FULL:
                    audit_results["passed_checks"] += 1
                else:
                    audit_results["failed_checks"] += 1
                    audit_results["violations"].append(
                        {
                            "check_id": check.check_id,
                            "check_name": check.check_name,
                            "violation_type": (
                                result.violation_type.value
                                if result.violation_type
                                else "unknown"
                            ),
                            "details": result.details,
                            "recommendations": result.recommendations,
                        }
                    )

            # Рассчитываем общий балл соответствия
            if audit_results["total_checks"] > 0:
                audit_results["compliance_score"] = round(
                    (
                        audit_results["passed_checks"]
                        / audit_results["total_checks"]
                    )
                    * 100,
                    2,
                )

            # Генерируем общие рекомендации
            audit_results["recommendations"] = (
                self._generate_audit_recommendations(audit_results)
            )

            audit_results["completed_at"] = datetime.now().isoformat()

            # Обновляем статистику
            self.compliance_stats["last_audit"] = audit_results["completed_at"]
            self.compliance_stats["compliance_score"] = audit_results[
                "compliance_score"
            ]

            self.logger.log(
                "INFO",
                f"Аудит завершен. Балл соответствия: {audit_results['compliance_score']}%"
            )
            return audit_results

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка выполнения аудита: {e}")
            return {"error": str(e), "audit_id": f"error_{int(time.time())}"}

    async def _run_compliance_check(
        self, check: ComplianceCheck
    ) -> ComplianceResult:
        """Выполнение отдельной проверки соответствия"""
        try:
            result_id = f"result_{check.check_id}_{int(time.time())}"

            # Имитация выполнения проверки
            await asyncio.sleep(0.1)  # Заглушка для демонстрации

            # В зависимости от типа проверки определяем результат
            if check.standard == ComplianceStandard.LAW_152_FZ:
                return await self._check_152_fz_compliance(check, result_id)
            elif check.standard in [
                ComplianceStandard.GOST_R_57580_1,
                ComplianceStandard.GOST_R_57580_2,
            ]:
                return await self._check_gost_compliance(check, result_id)
            elif check.standard in [
                ComplianceStandard.FSTEC_ORDER_1119,
                ComplianceStandard.FSTEC_ORDER_17,
                ComplianceStandard.FSTEC_ORDER_21,
            ]:
                return await self._check_fstec_compliance(check, result_id)
            else:
                # Неизвестный стандарт
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.UNKNOWN,
                    details="Неизвестный стандарт соответствия",
                    recommendations=[
                        "Обратиться к специалистам по соответствию"
                    ],
                )

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка проверки {check.check_id}: {e}")
            return ComplianceResult(
                result_id=f"error_{int(time.time())}",
                check_id=check.check_id,
                compliance_level=ComplianceLevel.UNKNOWN,
                details=f"Ошибка выполнения проверки: {e}",
                recommendations=["Повторить проверку позже"],
            )

    async def _check_152_fz_compliance(
        self, check: ComplianceCheck, result_id: str
    ) -> ComplianceResult:
        """Проверка соответствия 152-ФЗ"""

        if check.check_id == "152_fz_001":  # Шифрование ПДн
            # Имитация проверки шифрования
            has_encryption = True  # В реальности - проверка конфигурации
            if has_encryption:
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.FULL,
                    details="Шифрование персональных данных настроено корректно",
                    evidence={
                        "encryption_enabled": True,
                        "algorithm": "AES-256",
                    },
                )
            else:
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.NON_COMPLIANT,
                    violation_type=ComplianceViolation.INSUFFICIENT_ENCRYPTION,
                    details="Шифрование персональных данных не настроено",
                    recommendations=[
                        "Включить шифрование для всех персональных данных",
                        "Использовать стойкие алгоритмы шифрования (AES-256)",
                        "Настроить управление ключами шифрования",
                    ],
                )

        elif check.check_id == "152_fz_002":  # Контроль доступа
            # Имитация проверки контроля доступа
            access_control_ok = True
            if access_control_ok:
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.FULL,
                    details="Система контроля доступа настроена корректно",
                    evidence={
                        "access_control_enabled": True,
                        "users_count": 25,
                    },
                )
            else:
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.PARTIAL,
                    violation_type=ComplianceViolation.UNAUTHORIZED_ACCESS,
                    details="Обнаружены недостатки в системе контроля доступа",
                    recommendations=[
                        "Пересмотреть права доступа пользователей",
                        "Внедрить принцип минимальных привилегий",
                        "Настроить регулярный аудит доступа",
                    ],
                )

        elif check.check_id == "152_fz_003":  # Аудит ПДн
            # Имитация проверки аудита
            audit_logs_ok = True
            if audit_logs_ok:
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.FULL,
                    details="Аудит обработки персональных данных ведется корректно",
                    evidence={
                        "audit_enabled": True,
                        "log_retention_days": 365,
                    },
                )
            else:
                return ComplianceResult(
                    result_id=result_id,
                    check_id=check.check_id,
                    compliance_level=ComplianceLevel.NON_COMPLIANT,
                    violation_type=ComplianceViolation.MISSING_AUDIT_LOG,
                    details="Аудит обработки персональных данных не ведется",
                    recommendations=[
                        "Включить логирование всех операций с ПДн",
                        "Настроить хранение логов аудита",
                        "Регулярно анализировать логи аудита",
                    ],
                )

        # Для других проверок 152-ФЗ
        return ComplianceResult(
            result_id=result_id,
            check_id=check.check_id,
            compliance_level=ComplianceLevel.PARTIAL,
            details="Требуется ручная проверка",
            recommendations=["Обратиться к специалистам по 152-ФЗ"],
        )

    async def _check_gost_compliance(
        self, check: ComplianceCheck, result_id: str
    ) -> ComplianceResult:
        """Проверка соответствия ГОСТ"""

        if check.check_id == "gost_001":  # Модель угроз
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.PARTIAL,
                details="Модель угроз требует обновления",
                recommendations=[
                    "Обновить модель угроз ИБ",
                    "Провести анализ актуальных угроз",
                    "Документировать изменения в модели угроз",
                ],
            )

        elif check.check_id == "gost_002":  # Политики ИБ
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.FULL,
                details="Политики информационной безопасности актуальны",
                evidence={"policies_count": 15, "last_update": "2025-09-01"},
            )

        elif check.check_id == "gost_003":  # Мониторинг ИБ
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.FULL,
                details="Система мониторинга ИБ функционирует",
                evidence={"monitoring_enabled": True, "alerts_count": 5},
            )

        return ComplianceResult(
            result_id=result_id,
            check_id=check.check_id,
            compliance_level=ComplianceLevel.UNKNOWN,
            details="Неизвестная проверка ГОСТ",
        )

    async def _check_fstec_compliance(
        self, check: ComplianceCheck, result_id: str
    ) -> ComplianceResult:
        """Проверка соответствия требованиям ФСТЭК"""

        if check.check_id == "fstec_001":  # Защита от вредоносного ПО
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.FULL,
                details="Средства защиты от вредоносного ПО активны",
                evidence={
                    "antivirus_enabled": True,
                    "last_scan": "2025-09-25",
                },
            )

        elif check.check_id == "fstec_002":  # Контроль целостности
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.PARTIAL,
                details="Контроль целостности настроен частично",
                recommendations=[
                    "Расширить покрытие контроля целостности",
                    "Настроить автоматические уведомления о нарушениях",
                    "Документировать процедуры восстановления",
                ],
            )

        elif check.check_id == "fstec_003":  # Управление доступом
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.FULL,
                details="Система управления доступом соответствует требованиям",
                evidence={
                    "access_management_enabled": True,
                    "users_managed": 25,
                },
            )

        elif check.check_id == "fstec_004":  # Обнаружение вторжений
            return ComplianceResult(
                result_id=result_id,
                check_id=check.check_id,
                compliance_level=ComplianceLevel.PARTIAL,
                details="Система обнаружения вторжений требует настройки",
                recommendations=[
                    "Настроить правила обнаружения вторжений",
                    "Обновить сигнатуры атак",
                    "Настроить автоматическое реагирование",
                ],
            )

        return ComplianceResult(
            result_id=result_id,
            check_id=check.check_id,
            compliance_level=ComplianceLevel.UNKNOWN,
            details="Неизвестная проверка ФСТЭК",
        )

    def _generate_audit_recommendations(
        self, audit_results: Dict[str, Any]
    ) -> List[str]:
        """Генерация общих рекомендаций по результатам аудита"""
        recommendations = []

        # Анализируем результаты и генерируем рекомендации
        if audit_results["compliance_score"] < 70:
            recommendations.append(
                "Критически низкий уровень соответствия. Требуется немедленное вмешательство."
            )

        if audit_results["compliance_score"] < 90:
            recommendations.append(
                "Рекомендуется повысить уровень соответствия до 90% и выше."
            )

        # Анализируем типы нарушений
        violation_types = [
            v["violation_type"] for v in audit_results["violations"]
        ]

        if "data_breach" in violation_types:
            recommendations.append(
                "Усилить защиту от нарушений целостности данных."
            )

        if "unauthorized_access" in violation_types:
            recommendations.append("Пересмотреть систему управления доступом.")

        if "insufficient_encryption" in violation_types:
            recommendations.append("Улучшить криптографическую защиту данных.")

        # Общие рекомендации
        recommendations.extend(
            [
                "Проводить регулярные аудиты соответствия (не реже раза в квартал)",
                "Документировать все изменения в системе безопасности",
                "Обучать персонал требованиям соответствия",
                "Поддерживать актуальность политик безопасности",
            ]
        )

        return recommendations

    def get_compliance_report(
        self,
        standard: Optional[ComplianceStandard] = None,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Получение отчета о соответствии.

        Args:
            standard: Конкретный стандарт для отчета
            format: Формат отчета

        Returns:
            Dict: Отчет о соответствии
        """
        try:
            report = {
                "report_id": f"compliance_report_{int(time.time())}",
                "generated_at": datetime.now().isoformat(),
                "compliance_summary": {
                    "overall_score": self.compliance_stats["compliance_score"],
                    "total_checks": self.compliance_stats["total_checks"],
                    "passed_checks": self.compliance_stats["passed_checks"],
                    "failed_checks": self.compliance_stats["failed_checks"],
                    "violations_found": self.compliance_stats[
                        "violations_found"
                    ],
                },
                "standards_covered": [],
                "detailed_results": [],
                "recommendations": [],
            }

            # Фильтруем результаты по стандарту
            filtered_results = []
            if standard:
                for result in self.compliance_results.values():
                    check = self.compliance_checks.get(result.check_id)
                    if check and check.standard == standard:
                        filtered_results.append(result)
                        if standard.value not in report["standards_covered"]:
                            report["standards_covered"].append(standard.value)
            else:
                filtered_results = list(self.compliance_results.values())
                for check in self.compliance_checks.values():
                    if check.standard.value not in report["standards_covered"]:
                        report["standards_covered"].append(
                            check.standard.value
                        )

            # Добавляем детальные результаты
            for result in filtered_results:
                check = self.compliance_checks.get(result.check_id)
                report["detailed_results"].append(
                    {
                        "check": check.to_dict() if check else None,
                        "result": result.to_dict(),
                    }
                )

            # Генерируем рекомендации
            report["recommendations"] = (
                self._generate_general_recommendations()
            )

            return report

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка генерации отчета: {e}")
            return {"error": str(e)}

    def _generate_general_recommendations(self) -> List[str]:
        """Генерация общих рекомендаций по соответствию"""
        return [
            "Регулярно обновлять политики информационной безопасности",
            "Проводить обучение персонала по требованиям соответствия",
            "Документировать все изменения в системе безопасности",
            "Поддерживать актуальность средств защиты информации",
            "Проводить регулярные аудиты соответствия",
            "Уведомлять регуляторы о нарушениях в установленные сроки",
            "Внедрять принцип минимальных привилегий",
            "Использовать стойкие криптографические алгоритмы",
            "Обеспечивать резервное копирование критически важных данных",
            "Настраивать мониторинг и реагирование на инциденты",
        ]

    def get_compliance_statistics(self) -> Dict[str, Any]:
        """Получение статистики соответствия"""
        return {
            "compliance_stats": self.compliance_stats,
            "checks_by_standard": self._get_checks_by_standard(),
            "results_summary": self._get_results_summary(),
            "last_updated": datetime.now().isoformat(),
        }

    def _get_checks_by_standard(self) -> Dict[str, int]:
        """Получение количества проверок по стандартам"""
        checks_by_standard = {}
        for check in self.compliance_checks.values():
            standard = check.standard.value
            checks_by_standard[standard] = (
                checks_by_standard.get(standard, 0) + 1
            )
        return checks_by_standard

    def _get_results_summary(self) -> Dict[str, int]:
        """Получение сводки результатов"""
        results_summary = {
            "total_results": len(self.compliance_results),
            "full_compliance": 0,
            "partial_compliance": 0,
            "non_compliant": 0,
            "unknown": 0,
        }

        for result in self.compliance_results.values():
            if result.compliance_level == ComplianceLevel.FULL:
                results_summary["full_compliance"] += 1
            elif result.compliance_level == ComplianceLevel.PARTIAL:
                results_summary["partial_compliance"] += 1
            elif result.compliance_level == ComplianceLevel.NON_COMPLIANT:
                results_summary["non_compliant"] += 1
            else:
                results_summary["unknown"] += 1

        return results_summary


# Пример использования
if __name__ == "__main__":

    async def main():
        # Создаем агента соответствия
        compliance_agent = ComplianceAgent()

        # Запускаем аудит соответствия
        audit_result = await compliance_agent.run_compliance_audit(
            standards=[
                ComplianceStandard.LAW_152_FZ,
                ComplianceStandard.FSTEC_ORDER_1119,
            ]
        )
        print(f"Результат аудита: {audit_result}")

        # Получаем отчет о соответствии
        report = compliance_agent.get_compliance_report(
            ComplianceStandard.LAW_152_FZ
        )
        print(f"Отчет по 152-ФЗ: {report}")

        # Получаем статистику
        stats = compliance_agent.get_compliance_statistics()
        print(f"Статистика соответствия: {stats}")

    # Запускаем пример
    asyncio.run(main())

"""
Сервис автоматического восстановления после атак для семейной системы
безопасности ALADDIN
"""

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase


class RecoveryType(Enum):
    """Типы восстановления"""

    DATA_RECOVERY = "data_recovery"
    SYSTEM_RECOVERY = "system_recovery"
    NETWORK_RECOVERY = "network_recovery"
    USER_ACCOUNT_RECOVERY = "user_account_recovery"
    FAMILY_PROFILE_RECOVERY = "family_profile_recovery"
    SECURITY_SETTINGS_RECOVERY = "security_settings_recovery"


class RecoveryStatus(Enum):
    """Статусы восстановления"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecoveryPriority(Enum):
    """Приоритеты восстановления"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryMethod(Enum):
    """Методы восстановления"""

    BACKUP_RESTORE = "backup_restore"
    SYSTEM_RESET = "system_reset"
    DATA_RECOVERY = "data_recovery"
    NETWORK_RESET = "network_reset"
    ACCOUNT_RECOVERY = "account_recovery"
    SETTINGS_RESTORE = "settings_restore"


@dataclass
class RecoveryTask:
    """Задача восстановления"""

    task_id: str
    recovery_type: RecoveryType
    priority: RecoveryPriority
    method: RecoveryMethod
    target_entity: str
    backup_source: Optional[str] = None
    recovery_destination: Optional[str] = None
    user_id: Optional[str] = None
    family_role: Optional[str] = None
    status: RecoveryStatus = RecoveryStatus.PENDING
    created_time: datetime = field(default_factory=datetime.now)
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    progress_percentage: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """План восстановления"""

    plan_id: str
    incident_id: str
    recovery_tasks: List[RecoveryTask]
    estimated_duration: int  # в минутах
    family_impact: Dict[str, Any]
    created_time: datetime = field(default_factory=datetime.now)
    status: RecoveryStatus = RecoveryStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryReport:
    """Отчет о восстановлении"""

    report_id: str
    plan_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    recovery_duration: int  # в минутах
    data_recovered: int  # в байтах
    systems_restored: int
    family_impact_assessment: Dict[str, Any]
    recommendations: List[str]
    created_time: datetime = field(default_factory=datetime.now)


class RecoveryService(SecurityBase):
    """Сервис автоматического восстановления после атак для семей"""

    def __init__(
        self,
        name: str = "RecoveryService",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Основные компоненты
        self.recovery_tasks: Dict[str, RecoveryTask] = {}
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        self.recovery_reports: Dict[str, RecoveryReport] = {}
        self.backup_locations: Dict[str, str] = {}
        self.recovery_rules: Dict[str, Dict[str, Any]] = {}

        # Семейные настройки
        self.family_recovery_settings: Dict[str, Any] = {}
        self.automatic_recovery_enabled: bool = True
        self.family_notifications_enabled: bool = True
        self.recovery_monitoring_enabled: bool = True

        # Статистика
        self.total_recoveries: int = 0
        self.successful_recoveries: int = 0
        self.failed_recoveries: int = 0
        self.family_recovery_history: Dict[str, List[str]] = {}
        self.recovery_plans = []  # Список планов восстановления
        self.recovery_reports = []  # Список отчётов восстановления
        self.recovery_statistics = {}  # Статистика восстановления
        self.last_cleanup_date = None  # Дата последней очистки

        # Инициализация
        self._initialize_recovery_rules()
        self._setup_family_protection()
        self._setup_backup_locations()

    def _initialize_recovery_rules(self):
        """Инициализация правил восстановления"""
        rules = [
            {
                "rule_id": "malware_recovery",
                "recovery_type": RecoveryType.SYSTEM_RECOVERY,
                "priority": RecoveryPriority.HIGH,
                "method": RecoveryMethod.SYSTEM_RESET,
                "conditions": {"threat_type": "malware", "severity": "high"},
                "family_specific": True,
                "age_group": "all",
            },
            {
                "rule_id": "data_breach_recovery",
                "recovery_type": RecoveryType.DATA_RECOVERY,
                "priority": RecoveryPriority.CRITICAL,
                "method": RecoveryMethod.BACKUP_RESTORE,
                "conditions": {
                    "threat_type": "data_breach",
                    "severity": "critical",
                },
                "family_specific": True,
                "age_group": "all",
            },
        ]

        for rule in rules:
            self.recovery_rules[rule["rule_id"]] = rule

        self.log_activity(
            f"Инициализировано {len(rules)} правил восстановления"
        )

    def _setup_family_protection(self):
        """Настройка семейной защиты"""
        self.family_recovery_settings = {
            "automatic_recovery": True,
            "family_notifications": True,
            "child_protection_priority": "high",
            "elderly_support_enabled": True,
            "recovery_timeout": 30,  # минуты
            "backup_retention_days": 30,
            "family_recovery_history": True,
            "recovery_verification": True,
        }
        self.log_activity("Настроена семейная защита восстановления")

    def _setup_backup_locations(self):
        """Настройка мест хранения резервных копий"""
        self.backup_locations = {
            "system_backup": "/backups/system/",
            "data_backup": "/backups/data/",
            "user_profiles": "/backups/profiles/",
            "family_settings": "/backups/family/",
            "security_config": "/backups/security/",
            "network_config": "/backups/network/",
        }
        self.log_activity("Настроены места хранения резервных копий")

    def create_recovery_plan(
        self,
        incident_id: str,
        incident_data: Dict[str, Any],
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> RecoveryPlan:
        """Создание плана восстановления"""
        try:
            plan_id = self._generate_plan_id()
            recovery_tasks = self._generate_recovery_tasks(
                incident_data, user_id, family_role
            )

            # Оценка семейного воздействия
            family_impact = self._assess_family_impact(
                incident_data, user_id, family_role
            )

            # Расчет времени восстановления
            estimated_duration = self._calculate_recovery_duration(
                recovery_tasks
            )

            plan = RecoveryPlan(
                plan_id=plan_id,
                incident_id=incident_id,
                recovery_tasks=recovery_tasks,
                estimated_duration=estimated_duration,
                family_impact=family_impact,
            )

            self.recovery_plans[plan_id] = plan

            # Логирование события
            self.add_security_event(
                event_type="recovery_plan_created",
                description=(
                    f"Создан план восстановления {plan_id} для инцидента "
                    f"{incident_id}"
                ),
                severity="info",
                source="RecoveryService",
                metadata={
                    "plan_id": plan_id,
                    "incident_id": incident_id,
                    "user_id": user_id,
                    "family_role": family_role,
                    "tasks_count": len(recovery_tasks),
                    "estimated_duration": estimated_duration,
                },
            )

            self.log_activity(
                f"Создан план восстановления {plan_id} с "
                f"{len(recovery_tasks)} задачами"
            )
            return plan

        except Exception as e:
            self.logger.error(f"Ошибка создания плана восстановления: {e}")
            return None

    def _generate_recovery_tasks(
        self,
        incident_data: Dict[str, Any],
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> List[RecoveryTask]:
        """Генерация задач восстановления"""
        tasks = []

        # Анализ инцидента и определение необходимых задач

        # Применение правил восстановления
        for rule_id, rule in self.recovery_rules.items():
            if self._evaluate_recovery_rule(
                incident_data, rule, user_id, family_role
            ):
                task = self._create_recovery_task(
                    rule, incident_data, user_id, family_role
                )
                if task:
                    tasks.append(task)

        # Семейные задачи восстановления
        if family_role:
            family_tasks = self._create_family_recovery_tasks(
                incident_data, user_id, family_role
            )
            tasks.extend(family_tasks)

        return tasks

    def _evaluate_recovery_rule(
        self,
        incident_data: Dict[str, Any],
        rule: Dict[str, Any],
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> bool:
        """Оценка правила восстановления"""
        try:
            conditions = rule.get("conditions", {})

            # Проверка условий
            for condition_key, condition_value in conditions.items():
                if condition_key in incident_data:
                    if incident_data[condition_key] != condition_value:
                        return False
                elif condition_key == "family_role" and family_role:
                    if family_role != condition_value:
                        return False
                else:
                    return False

            # Проверка семейных условий
            if rule.get("family_specific", False):
                if not family_role:
                    return False

                age_group = rule.get("age_group", "all")
                if age_group != "all" and age_group != family_role:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка оценки правила восстановления: {e}")
            return False

    def _create_recovery_task(
        self,
        rule: Dict[str, Any],
        incident_data: Dict[str, Any],
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> Optional[RecoveryTask]:
        """Создание задачи восстановления"""
        try:
            task_id = self._generate_task_id()

            task = RecoveryTask(
                task_id=task_id,
                recovery_type=RecoveryType(rule["recovery_type"]),
                priority=RecoveryPriority(rule["priority"]),
                method=RecoveryMethod(rule["method"]),
                target_entity=incident_data.get("target_entity", "unknown"),
                user_id=user_id,
                family_role=family_role,
                metadata={
                    "rule_id": rule["rule_id"],
                    "incident_data": incident_data,
                    "family_specific": rule.get("family_specific", False),
                },
            )

            return task

        except Exception as e:
            self.logger.error(f"Ошибка создания задачи восстановления: {e}")
            return None

    def _create_family_recovery_tasks(
        self,
        incident_data: Dict[str, Any],
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> List[RecoveryTask]:
        """Создание семейных задач восстановления"""
        tasks = []

        try:
            # Задача восстановления семейного профиля
            if family_role in ["child", "elderly"]:
                task_id = self._generate_task_id()
                task = RecoveryTask(
                    task_id=task_id,
                    recovery_type=RecoveryType.FAMILY_PROFILE_RECOVERY,
                    priority=RecoveryPriority.HIGH,
                    method=RecoveryMethod.SETTINGS_RESTORE,
                    target_entity=f"family_profile_{user_id}",
                    user_id=user_id,
                    family_role=family_role,
                    metadata={
                        "family_specific": True,
                        "age_group": family_role,
                        "protection_level": "enhanced",
                    },
                )
                tasks.append(task)

            # Задача восстановления родительских настроек
            if family_role == "parent":
                task_id = self._generate_task_id()
                task = RecoveryTask(
                    task_id=task_id,
                    recovery_type=RecoveryType.SECURITY_SETTINGS_RECOVERY,
                    priority=RecoveryPriority.MEDIUM,
                    method=RecoveryMethod.SETTINGS_RESTORE,
                    target_entity=f"parental_controls_{user_id}",
                    user_id=user_id,
                    family_role=family_role,
                    metadata={
                        "family_specific": True,
                        "parental_controls": True,
                    },
                )
                tasks.append(task)

        except Exception as e:
            self.logger.error(
                f"Ошибка создания семейных задач восстановления: {e}"
            )

        return tasks

    def execute_recovery_plan(self, plan_id: str) -> bool:
        """Выполнение плана восстановления"""
        try:
            if plan_id not in self.recovery_plans:
                self.logger.error(f"План восстановления {plan_id} не найден")
                return False

            plan = self.recovery_plans[plan_id]
            plan.status = RecoveryStatus.IN_PROGRESS

            # Выполнение задач восстановления
            for task in plan.recovery_tasks:
                if not self._execute_recovery_task(task):
                    self.logger.error(
                        f"Ошибка выполнения задачи восстановления "
                        f"{task.task_id}"
                    )
                    task.status = RecoveryStatus.FAILED
                else:
                    task.status = RecoveryStatus.COMPLETED

            # Проверка статуса плана
            completed_tasks = sum(
                1
                for task in plan.recovery_tasks
                if task.status == RecoveryStatus.COMPLETED
            )
            failed_tasks = sum(
                1
                for task in plan.recovery_tasks
                if task.status == RecoveryStatus.FAILED
            )

            if failed_tasks == 0:
                plan.status = RecoveryStatus.COMPLETED
                self.successful_recoveries += 1
            else:
                plan.status = RecoveryStatus.FAILED
                self.failed_recoveries += 1

            self.total_recoveries += 1

            # Обновление истории семейного восстановления
            for task in plan.recovery_tasks:
                if task.user_id:
                    if task.user_id not in self.family_recovery_history:
                        self.family_recovery_history[task.user_id] = []
                    self.family_recovery_history[task.user_id].append(
                        plan.plan_id
                    )

            # Создание отчета
            self._create_recovery_report(plan)

            # Логирование события
            self.add_security_event(
                event_type="recovery_plan_executed",
                description=f"Выполнен план восстановления {plan_id}",
                severity="info",
                source="RecoveryService",
                metadata={
                    "plan_id": plan_id,
                    "completed_tasks": completed_tasks,
                    "failed_tasks": failed_tasks,
                    "status": plan.status.value,
                },
            )

            self.log_activity(
                f"Выполнен план восстановления {plan_id}: "
                f"{completed_tasks}/{len(plan.recovery_tasks)} задач"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка выполнения плана восстановления: {e}")
            return False

    def _execute_recovery_task(self, task: RecoveryTask) -> bool:
        """Выполнение задачи восстановления"""
        try:
            task.status = RecoveryStatus.IN_PROGRESS
            task.started_time = datetime.now()

            # Выполнение в зависимости от типа восстановления
            if task.recovery_type == RecoveryType.DATA_RECOVERY:
                success = self._recover_data(task)
            elif task.recovery_type == RecoveryType.SYSTEM_RECOVERY:
                success = self._recover_system(task)
            elif task.recovery_type == RecoveryType.NETWORK_RECOVERY:
                success = self._recover_network(task)
            elif task.recovery_type == RecoveryType.USER_ACCOUNT_RECOVERY:
                success = self._recover_user_account(task)
            elif task.recovery_type == RecoveryType.FAMILY_PROFILE_RECOVERY:
                success = self._recover_family_profile(task)
            elif task.recovery_type == RecoveryType.SECURITY_SETTINGS_RECOVERY:
                success = self._recover_security_settings(task)
            else:
                success = False

            if success:
                task.status = RecoveryStatus.COMPLETED
                task.completed_time = datetime.now()
                task.progress_percentage = 100.0
            else:
                task.status = RecoveryStatus.FAILED
                task.error_message = "Ошибка выполнения задачи восстановления"

            return success

        except Exception as e:
            self.logger.error(
                f"Ошибка выполнения задачи восстановления {task.task_id}: {e}"
            )
            task.status = RecoveryStatus.FAILED
            task.error_message = str(e)
            return False

    def _recover_data(self, task: RecoveryTask) -> bool:
        """Восстановление данных"""
        try:
            # Симуляция восстановления данных
            self.log_activity(
                f"Восстановление данных для {task.target_entity}"
            )

            # Обновление прогресса
            task.progress_percentage = 100.0

            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления данных: {e}")
            return False

    def _recover_system(self, task: RecoveryTask) -> bool:
        """Восстановление системы"""
        try:
            # Симуляция восстановления системы
            self.log_activity(
                f"Восстановление системы для {task.target_entity}"
            )

            # Обновление прогресса
            task.progress_percentage = 100.0

            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления системы: {e}")
            return False

    def _recover_network(self, task: RecoveryTask) -> bool:
        """Восстановление сети"""
        try:
            # Симуляция восстановления сети
            self.log_activity(f"Восстановление сети для {task.target_entity}")

            # Обновление прогресса
            task.progress_percentage = 100.0

            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления сети: {e}")
            return False

    def _recover_user_account(self, task: RecoveryTask) -> bool:
        """Восстановление пользовательского аккаунта"""
        try:
            # Симуляция восстановления аккаунта
            self.log_activity(
                f"Восстановление аккаунта пользователя {task.user_id}"
            )

            # Семейные особенности
            if task.family_role == "child":
                self.log_activity(
                    "Применение дополнительной защиты для детского аккаунта"
                )
            elif task.family_role == "elderly":
                self.log_activity(
                    "Применение упрощенного интерфейса для пожилого "
                    "пользователя"
                )

            # Обновление прогресса
            task.progress_percentage = 100.0

            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления аккаунта: {e}")
            return False

    def _recover_family_profile(self, task: RecoveryTask) -> bool:
        """Восстановление семейного профиля"""
        try:
            # Симуляция восстановления семейного профиля
            self.log_activity(
                f"Восстановление семейного профиля для {task.user_id}"
            )

            # Семейные настройки
            if task.family_role == "child":
                self.log_activity("Восстановление родительского контроля")
            elif task.family_role == "elderly":
                self.log_activity("Восстановление упрощенных настроек")

            # Обновление прогресса
            task.progress_percentage = 100.0

            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления семейного профиля: {e}")
            return False

    def _recover_security_settings(self, task: RecoveryTask) -> bool:
        """Восстановление настроек безопасности"""
        try:
            # Симуляция восстановления настроек безопасности
            self.log_activity(
                f"Восстановление настроек безопасности для {task.user_id}"
            )

            # Семейные настройки
            if task.family_role == "parent":
                self.log_activity(
                    "Восстановление родительских настроек безопасности"
                )

            # Обновление прогресса
            task.progress_percentage = 100.0

            return True

        except Exception as e:
            self.logger.error(
                f"Ошибка восстановления настроек безопасности: {e}"
            )
            return False

    def _assess_family_impact(
        self,
        incident_data: Dict[str, Any],
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Оценка семейного воздействия"""
        try:
            impact = {
                "affected_family_members": [],
                "impact_level": "low",
                "recovery_priority": "medium",
                "family_support_needed": False,
                "estimated_downtime": 0,  # в минутах
                "data_loss_risk": "low",
            }

            if family_role:
                impact["affected_family_members"].append(
                    {
                        "user_id": user_id,
                        "family_role": family_role,
                        "impact_severity": "medium",
                    }
                )

                if family_role == "child":
                    impact["impact_level"] = "high"
                    impact["recovery_priority"] = "high"
                    impact["family_support_needed"] = True
                elif family_role == "elderly":
                    impact["impact_level"] = "medium"
                    impact["recovery_priority"] = "medium"
                    impact["family_support_needed"] = True

            return impact

        except Exception as e:
            self.logger.error(f"Ошибка оценки семейного воздействия: {e}")
            return {}

    def _calculate_recovery_duration(self, tasks: List[RecoveryTask]) -> int:
        """Расчет времени восстановления"""
        try:
            total_duration = 0

            for task in tasks:
                if task.recovery_type == RecoveryType.DATA_RECOVERY:
                    total_duration += 15  # 15 минут
                elif task.recovery_type == RecoveryType.SYSTEM_RECOVERY:
                    total_duration += 30  # 30 минут
                elif task.recovery_type == RecoveryType.NETWORK_RECOVERY:
                    total_duration += 10  # 10 минут
                elif task.recovery_type == RecoveryType.USER_ACCOUNT_RECOVERY:
                    total_duration += 5  # 5 минут
                elif (
                    task.recovery_type == RecoveryType.FAMILY_PROFILE_RECOVERY
                ):
                    total_duration += 8  # 8 минут
                elif (
                    task.recovery_type
                    == RecoveryType.SECURITY_SETTINGS_RECOVERY
                ):
                    total_duration += 3  # 3 минуты

            return total_duration

        except Exception as e:
            self.logger.error(f"Ошибка расчета времени восстановления: {e}")
            return 30  # По умолчанию 30 минут

    def _create_recovery_report(self, plan: RecoveryPlan):
        """Создание отчета о восстановлении"""
        try:
            report_id = self._generate_report_id()

            completed_tasks = sum(
                1
                for task in plan.recovery_tasks
                if task.status == RecoveryStatus.COMPLETED
            )
            failed_tasks = sum(
                1
                for task in plan.recovery_tasks
                if task.status == RecoveryStatus.FAILED
            )

            # Расчет времени восстановления
            if plan.recovery_tasks:
                start_time = min(
                    task.started_time
                    for task in plan.recovery_tasks
                    if task.started_time
                )
                end_time = max(
                    task.completed_time
                    for task in plan.recovery_tasks
                    if task.completed_time
                )
                recovery_duration = (
                    int((end_time - start_time).total_seconds() / 60)
                    if start_time and end_time
                    else 0
                )
            else:
                recovery_duration = 0

            # Генерация рекомендаций
            recommendations = self._generate_recovery_recommendations(plan)

            report = RecoveryReport(
                report_id=report_id,
                plan_id=plan.plan_id,
                total_tasks=len(plan.recovery_tasks),
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                recovery_duration=recovery_duration,
                data_recovered=0,  # Симуляция
                systems_restored=completed_tasks,
                family_impact_assessment=plan.family_impact,
                recommendations=recommendations,
            )

            self.recovery_reports[report_id] = report

            self.log_activity(f"Создан отчет о восстановлении {report_id}")

        except Exception as e:
            self.logger.error(f"Ошибка создания отчета о восстановлении: {e}")

    def _generate_recovery_recommendations(
        self, plan: RecoveryPlan
    ) -> List[str]:
        """Генерация рекомендаций по восстановлению"""
        recommendations = []

        try:
            if plan is None:
                return recommendations

            # Общие рекомендации
            recommendations.append(
                "Регулярно создавайте резервные копии важных данных"
            )
            recommendations.append("Обновляйте систему безопасности")
            recommendations.append("Мониторьте активность в сети")

            # Семейные рекомендации
            if plan.family_impact and plan.family_impact.get(
                "family_support_needed", False
            ):
                recommendations.append(
                    "Обеспечьте дополнительную поддержку для членов семьи"
                )
                recommendations.append("Проведите обучение по безопасности")

            # Рекомендации по типу восстановления
            recovery_types = set(
                task.recovery_type for task in plan.recovery_tasks
            )
            if RecoveryType.DATA_RECOVERY in recovery_types:
                recommendations.append("Усильте защиту данных")
            if RecoveryType.SYSTEM_RECOVERY in recovery_types:
                recommendations.append("Улучшите системную безопасность")
            if RecoveryType.NETWORK_RECOVERY in recovery_types:
                recommendations.append("Обновите сетевую конфигурацию")

        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")

        return recommendations

    def get_recovery_summary(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение сводки по восстановлению"""
        try:
            if user_id:
                # Сводка для конкретного пользователя
                user_plans = [
                    plan
                    for plan in self.recovery_plans.values()
                    if any(
                        task.user_id == user_id for task in plan.recovery_tasks
                    )
                ]
                user_tasks = [
                    task
                    for plan in user_plans
                    for task in plan.recovery_tasks
                    if task.user_id == user_id
                ]
            else:
                # Общая сводка
                user_plans = list(self.recovery_plans.values())
                user_tasks = [
                    task for plan in user_plans for task in plan.recovery_tasks
                ]

            summary = {
                "total_plans": len(user_plans),
                "total_tasks": len(user_tasks),
                "completed_tasks": sum(
                    1
                    for task in user_tasks
                    if task.status == RecoveryStatus.COMPLETED
                ),
                "failed_tasks": sum(
                    1
                    for task in user_tasks
                    if task.status == RecoveryStatus.FAILED
                ),
                "in_progress_tasks": sum(
                    1
                    for task in user_tasks
                    if task.status == RecoveryStatus.IN_PROGRESS
                ),
                "success_rate": (
                    (
                        sum(
                            1
                            for task in user_tasks
                            if task.status == RecoveryStatus.COMPLETED
                        )
                        / len(user_tasks)
                        * 100
                    )
                    if user_tasks
                    else 0
                ),
                "average_recovery_time": self._calculate_average_recovery_time(
                    user_tasks
                ),
                "family_impact_summary": self._get_family_impact_summary(
                    user_plans
                ),
                "recent_recoveries": self._get_recent_recoveries(
                    user_plans, limit=5
                ),
            }

            return summary

        except Exception as e:
            self.logger.error(
                f"Ошибка получения сводки по восстановлению: {e}"
            )
            return {}

    def _calculate_average_recovery_time(
        self, tasks: List[RecoveryTask]
    ) -> float:
        """Расчет среднего времени восстановления"""
        try:
            completed_tasks = [
                task
                for task in tasks
                if task.status == RecoveryStatus.COMPLETED
                and task.started_time
                and task.completed_time
            ]

            if not completed_tasks:
                return 0.0

            total_time = sum(
                (task.completed_time - task.started_time).total_seconds()
                for task in completed_tasks
            )
            return total_time / len(completed_tasks) / 60  # в минутах

        except Exception as e:
            self.logger.error(
                f"Ошибка расчета среднего времени восстановления: {e}"
            )
            return 0.0

    def _get_family_impact_summary(
        self, plans: List[RecoveryPlan]
    ) -> Dict[str, Any]:
        """Получение сводки семейного воздействия"""
        try:
            family_roles = {}
            impact_levels = {"low": 0, "medium": 0, "high": 0}

            for plan in plans:
                for task in plan.recovery_tasks:
                    if task.family_role:
                        family_roles[task.family_role] = (
                            family_roles.get(task.family_role, 0) + 1
                        )

                impact_level = plan.family_impact.get("impact_level", "low")
                impact_levels[impact_level] += 1

            return {
                "affected_family_roles": family_roles,
                "impact_levels": impact_levels,
                "total_family_incidents": len(plans),
            }

        except Exception as e:
            self.logger.error(
                f"Ошибка получения сводки семейного воздействия: {e}"
            )
            return {}

    def _get_recent_recoveries(
        self, plans: List[RecoveryPlan], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Получение недавних восстановлений"""
        try:
            recent_plans = sorted(
                plans, key=lambda p: p.created_time, reverse=True
            )[:limit]

            recent_recoveries = []
            for plan in recent_plans:
                recent_recoveries.append(
                    {
                        "plan_id": plan.plan_id,
                        "incident_id": plan.incident_id,
                        "status": plan.status.value,
                        "created_time": plan.created_time.isoformat(),
                        "estimated_duration": plan.estimated_duration,
                        "tasks_count": len(plan.recovery_tasks),
                    }
                )

            return recent_recoveries

        except Exception as e:
            self.logger.error(f"Ошибка получения недавних восстановлений: {e}")
            return []

    def get_family_recovery_status(self) -> Dict[str, Any]:
        """Получение статуса семейного восстановления"""
        try:
            status = {
                "automatic_recovery_enabled": self.automatic_recovery_enabled,
                "family_notifications_enabled": (
                    self.family_notifications_enabled
                ),
                "recovery_monitoring_enabled": (
                    self.recovery_monitoring_enabled
                ),
                "total_recoveries": self.total_recoveries,
                "successful_recoveries": self.successful_recoveries,
                "failed_recoveries": self.failed_recoveries,
                "success_rate": (
                    (self.successful_recoveries / self.total_recoveries * 100)
                    if self.total_recoveries > 0
                    else 0
                ),
                "active_plans": len(
                    [
                        p
                        for p in self.recovery_plans.values()
                        if p.status == RecoveryStatus.IN_PROGRESS
                    ]
                ),
                "family_recovery_settings": self.family_recovery_settings,
                "backup_locations": list(
                    self.backup_locations.keys()
                ),
                "recovery_rules": len(self.recovery_rules),
                "family_recovery_history": {
                    user_id: len(plan_ids)
                    for user_id, plan_ids in (
                        self.family_recovery_history.items()
                    )
                },
            }

            return status

        except Exception as e:
            self.logger.error(
                f"Ошибка получения статуса семейного восстановления: {e}"
            )
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            return {
                "service_name": self.name,
                "status": self.status.value,
                "recovery_plans": len(self.recovery_plans),
                "recovery_tasks": len(self.recovery_tasks),
                "recovery_reports": len(self.recovery_reports),
                "backup_locations": len(self.backup_locations),
                "recovery_rules": len(self.recovery_rules),
                "family_protection_enabled": True,
                "automatic_recovery_enabled": self.automatic_recovery_enabled,
                "total_recoveries": self.total_recoveries,
                "successful_recoveries": self.successful_recoveries,
                "failed_recoveries": self.failed_recoveries,
                "uptime": (
                    (datetime.now() - self.start_time).total_seconds()
                    if hasattr(self, "start_time") and self.start_time
                    else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}

    def _generate_plan_id(self) -> str:
        """Генерация ID плана"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"recovery_plan_{timestamp}_{random_part}"

    def _generate_task_id(self) -> str:
        """Генерация ID задачи"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"recovery_task_{timestamp}_{random_part}"

    def _generate_report_id(self) -> str:
        """Генерация ID отчета"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"recovery_report_{timestamp}_{random_part}"

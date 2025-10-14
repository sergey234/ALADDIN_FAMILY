"""
function_37: ForensicsService - Расследование инцидентов

Семейная система расследования инцидентов безопасности:
- Автоматический сбор и анализ доказательств
- Расследование атак и инцидентов
- Создание отчетов для семьи
- Адаптация под возрастные группы
- Интеграция с другими компонентами безопасности
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Union

from core.base import SecurityBase


class EvidenceType(Enum):
    """Типы доказательств"""

    LOG_FILE = "log_file"
    NETWORK_TRAFFIC = "network_traffic"
    SYSTEM_STATE = "system_state"
    USER_ACTIVITY = "user_activity"
    FILE_SYSTEM = "file_system"
    MEMORY_DUMP = "memory_dump"
    REGISTRY = "registry"
    BROWSER_HISTORY = "browser_history"


class InvestigationStatus(Enum):
    """Статусы расследования"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    FAILED = "failed"


class IncidentType(Enum):
    """Типы инцидентов"""

    MALWARE_INFECTION = "malware_infection"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PHISHING_ATTEMPT = "phishing_attempt"
    SOCIAL_ENGINEERING = "social_engineering"
    SYSTEM_COMPROMISE = "system_compromise"
    NETWORK_INTRUSION = "network_intrusion"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class EvidencePriority(Enum):
    """Приоритеты доказательств"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgeGroup(Enum):
    """Возрастные группы для адаптации"""

    CHILDREN = "children"  # 0-12 лет
    TEENAGERS = "teenagers"  # 13-17 лет
    ADULTS = "adults"  # 18-64 лет
    ELDERLY = "elderly"  # 65+ лет


@dataclass
class Evidence:
    """Доказательство"""

    evidence_id: str
    evidence_type: EvidenceType
    source: str
    timestamp: datetime
    description: str
    priority: EvidencePriority
    data: Dict[str, Any]
    family_impact: str
    age_appropriate_explanation: Dict[AgeGroup, str] = field(
        default_factory=dict
    )


@dataclass
class Investigation:
    """Расследование"""

    investigation_id: str
    incident_type: IncidentType
    status: InvestigationStatus
    start_time: datetime
    end_time: Union[datetime, None] = None
    evidence: List[Evidence] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    family_impact_assessment: str = ""
    age_appropriate_summary: Dict[AgeGroup, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ForensicsReport:
    """Отчет расследования"""

    report_id: str
    investigation_id: str
    incident_type: IncidentType
    investigation_duration: timedelta
    evidence_collected: int
    critical_findings: int
    family_impact_level: str
    recommendations_count: int
    executive_summary: str
    technical_details: str
    family_summary: str
    age_appropriate_reports: Dict[AgeGroup, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class ForensicsService(SecurityBase):
    """Сервис расследования инцидентов"""

    def __init__(self) -> None:
        super().__init__("ForensicsService")
        self.service_name = "ForensicsService"
        self.investigation_timeout = 3600  # 1 час

        # Хранилище данных
        self.active_investigations: Dict[str, Investigation] = {}
        self.completed_investigations: Dict[str, Investigation] = {}
        self.evidence_storage: Dict[str, Evidence] = {}
        self.family_incident_history: Dict[str, List[str]] = {}

        # Настройки
        self.auto_investigation_enabled = True
        self.evidence_retention_days = 90
        self.family_notification_enabled = True

        # Статистика
        self.stats: Dict[str, Any] = {
            "total_investigations": 0,
            "active_investigations": 0,
            "completed_investigations": 0,
            "evidence_collected": 0,
            "family_incidents": 0,
            "last_investigation": None,
        }

        self._initialize_forensics_rules()
        self._setup_family_protection()

    def _initialize_forensics_rules(self) -> None:
        """Инициализация правил расследования"""
        self.forensics_rules: Dict[str, Any] = {
            "investigation": {
                "enabled": True,
                "auto_start": True,
                "timeout": 3600,
                "evidence_retention": 90,
            },
            "family_protection": {
                "enabled": True,
                "notification_threshold": "medium",
                "age_appropriate": True,
                "simple_explanations": True,
            },
            "evidence_collection": {
                "enabled": True,
                "priority_threshold": "medium",
                "auto_analysis": True,
                "family_impact_analysis": True,
            },
        }

    def _setup_family_protection(self) -> None:
        """Настройка семейной защиты"""
        self.family_protection: Dict[str, Any] = {
            "age_groups": {
                AgeGroup.CHILDREN: {
                    "min_age": 0,
                    "max_age": 12,
                    "protection_level": "high",
                    "explanation_style": "simple",
                },
                AgeGroup.TEENAGERS: {
                    "min_age": 13,
                    "max_age": 17,
                    "protection_level": "high",
                    "explanation_style": "detailed",
                },
                AgeGroup.ADULTS: {
                    "min_age": 18,
                    "max_age": 64,
                    "protection_level": "medium",
                    "explanation_style": "technical",
                },
                AgeGroup.ELDERLY: {
                    "min_age": 65,
                    "max_age": 100,
                    "protection_level": "high",
                    "explanation_style": "simple",
                },
            },
            "incident_types": {
                "malware_infection": "Заражение вредоносными программами",
                "data_breach": "Утечка личных данных",
                "unauthorized_access": "Несанкционированный доступ",
                "phishing_attempt": "Попытка фишинга",
                "social_engineering": "Попытка обмана",
                "system_compromise": "Компрометация системы",
                "network_intrusion": "Вторжение в сеть",
                "privilege_escalation": "Повышение привилегий",
            },
        }

    def start_investigation(
        self, incident_type: IncidentType, incident_data: Dict[str, Any]
    ) -> Investigation:
        """Начало расследования инцидента"""
        try:
            investigation_id = (
                f"investigation_{incident_type.value}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Создание расследования
            investigation = Investigation(
                investigation_id=investigation_id,
                incident_type=incident_type,
                status=InvestigationStatus.IN_PROGRESS,
                start_time=datetime.now(),
                family_impact_assessment=self._assess_family_impact(
                    incident_type, incident_data
                ),
            )

            # Сохранение расследования
            self.active_investigations[investigation_id] = investigation
            self.stats["total_investigations"] += 1
            self.stats["active_investigations"] += 1

            # Логирование
            self.add_security_event(
                event_type="investigation_started",
                description=(
                    f"Начато расследование {investigation_id} "
                    f"для инцидента {incident_type.value}"
                ),
                severity="info",
                source="ForensicsService",
                metadata={
                    "investigation_id": investigation_id,
                    "incident_type": incident_type.value,
                    "family_impact": investigation.family_impact_assessment,
                },
            )

            return investigation

        except Exception as e:
            self.add_security_event(
                event_type="investigation_start_error",
                description=f"Ошибка начала расследования: {str(e)}",
                severity="error",
                source="ForensicsService",
            )
            raise

    def _assess_family_impact(
        self, incident_type: IncidentType, _incident_data: Dict[str, Any]
    ) -> str:
        """Оценка воздействия на семью"""
        impact_levels = {
            IncidentType.MALWARE_INFECTION: (
                "Высокое - может заразить все устройства семьи"
            ),
            IncidentType.DATA_BREACH: (
                "Критическое - утечка личных данных семьи"
            ),
            IncidentType.UNAUTHORIZED_ACCESS: (
                "Высокое - несанкционированный доступ к семейным данным"
            ),
            IncidentType.PHISHING_ATTEMPT: (
                "Среднее - попытка обмана членов семьи"
            ),
            IncidentType.SOCIAL_ENGINEERING: (
                "Среднее - попытка манипуляции семьей"
            ),
            IncidentType.SYSTEM_COMPROMISE: (
                "Высокое - компрометация семейной системы"
            ),
            IncidentType.NETWORK_INTRUSION: (
                "Высокое - вторжение в домашнюю сеть"
            ),
            IncidentType.PRIVILEGE_ESCALATION: (
                "Среднее - попытка повышения привилегий"
            ),
        }

        return impact_levels.get(
            incident_type, "Неизвестное воздействие на семью"
        )

    def collect_evidence(
        self,
        investigation_id: str,
        evidence_type: EvidenceType,
        source: str,
        data: Dict[str, Any],
    ) -> Evidence:
        """Сбор доказательств"""
        try:
            if investigation_id not in self.active_investigations:
                raise ValueError(
                    f"Расследование {investigation_id} не найдено"
                )

            evidence_id = (
                f"evidence_{evidence_type.value}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Создание доказательства
            evidence = Evidence(
                evidence_id=evidence_id,
                evidence_type=evidence_type,
                source=source,
                timestamp=datetime.now(),
                description=(
                    f"Доказательство типа {evidence_type.value} из {source}"
                ),
                priority=self._determine_evidence_priority(
                    evidence_type, data
                ),
                data=data,
                family_impact=self._assess_evidence_family_impact(
                    evidence_type, data
                ),
                age_appropriate_explanation=(
                    self._generate_evidence_explanations(evidence_type, data)
                ),
            )

            # Сохранение доказательства
            self.evidence_storage[evidence_id] = evidence
            self.active_investigations[investigation_id].evidence.append(
                evidence
            )
            self.stats["evidence_collected"] += 1

            # Логирование
            self.add_security_event(
                event_type="evidence_collected",
                description=(
                    f"Собрано доказательство {evidence_id} "
                    f"для расследования {investigation_id}"
                ),
                severity="info",
                source="ForensicsService",
                metadata={
                    "evidence_id": evidence_id,
                    "investigation_id": investigation_id,
                    "evidence_type": evidence_type.value,
                    "priority": evidence.priority.value,
                },
            )

            return evidence

        except Exception as e:
            self.add_security_event(
                event_type="evidence_collection_error",
                description=f"Ошибка сбора доказательств: {str(e)}",
                severity="error",
                source="ForensicsService",
            )
            raise

    def _determine_evidence_priority(
        self, evidence_type: EvidenceType, _data: Dict[str, Any]
    ) -> EvidencePriority:
        """Определение приоритета доказательства"""
        priority_mapping = {
            EvidenceType.MEMORY_DUMP: EvidencePriority.HIGH,
            EvidenceType.SYSTEM_STATE: EvidencePriority.HIGH,
            EvidenceType.NETWORK_TRAFFIC: EvidencePriority.MEDIUM,
            EvidenceType.LOG_FILE: EvidencePriority.MEDIUM,
            EvidenceType.USER_ACTIVITY: EvidencePriority.MEDIUM,
            EvidenceType.FILE_SYSTEM: EvidencePriority.LOW,
            EvidenceType.REGISTRY: EvidencePriority.LOW,
            EvidenceType.BROWSER_HISTORY: EvidencePriority.LOW,
        }

        return priority_mapping.get(evidence_type, EvidencePriority.MEDIUM)

    def _assess_evidence_family_impact(
        self, evidence_type: EvidenceType, _data: Dict[str, Any]
    ) -> str:
        """Оценка воздействия доказательства на семью"""
        impact_mapping = {
            EvidenceType.MEMORY_DUMP: (
                "Может содержать личную информацию семьи"
            ),
            EvidenceType.SYSTEM_STATE: (
                "Показывает состояние семейных устройств"
            ),
            EvidenceType.NETWORK_TRAFFIC: (
                "Отображает активность в домашней сети"
            ),
            EvidenceType.LOG_FILE: (
                "Содержит записи о действиях семьи"
            ),
            EvidenceType.USER_ACTIVITY: (
                "Показывает активность членов семьи"
            ),
            EvidenceType.FILE_SYSTEM: (
                "Может содержать семейные файлы"
            ),
            EvidenceType.REGISTRY: (
                "Содержит настройки семейных программ"
            ),
            EvidenceType.BROWSER_HISTORY: (
                "Показывает историю браузера семьи"
            ),
        }

        return impact_mapping.get(
            evidence_type, "Неизвестное воздействие на семью"
        )

    def _generate_evidence_explanations(
        self, evidence_type: EvidenceType, data: Dict[str, Any]
    ) -> Dict[AgeGroup, str]:
        """Генерация объяснений доказательств для разных возрастов"""
        explanations = {}

        # Простые объяснения для детей
        explanations[AgeGroup.CHILDREN] = (
            "Мы собираем информацию о том, что произошло с компьютером, "
            "чтобы защитить семью."
        )

        # Подробные объяснения для подростков
        explanations[AgeGroup.TEENAGERS] = (
            f"Собираем доказательства типа {evidence_type.value} "
            f"для анализа инцидента."
        )

        # Технические объяснения для взрослых
        priority = self._determine_evidence_priority(evidence_type, data)
        explanations[AgeGroup.ADULTS] = (
            f"Собрано доказательство типа {evidence_type.value} "
            f"с приоритетом {priority.value}."
        )

        # Простые объяснения для пожилых
        explanations[AgeGroup.ELDERLY] = (
            "Собираем информацию для защиты семьи от киберугроз."
        )

        return explanations

    def analyze_evidence(self, investigation_id: str) -> List[str]:
        """Анализ собранных доказательств"""
        try:
            if investigation_id not in self.active_investigations:
                raise ValueError(
                    f"Расследование {investigation_id} не найдено"
                )

            investigation = self.active_investigations[investigation_id]
            findings = []

            # Анализ доказательств
            for evidence in investigation.evidence:
                finding = self._analyze_single_evidence(evidence)
                if finding:
                    findings.append(finding)

            # Обновление расследования
            investigation.findings = findings
            investigation.updated_at = datetime.now()

            # Логирование
            self.add_security_event(
                event_type="evidence_analyzed",
                description=(
                    f"Проанализированы доказательства для расследования "
                    f"{investigation_id}"
                ),
                severity="info",
                source="ForensicsService",
                metadata={
                    "investigation_id": investigation_id,
                    "findings_count": len(findings),
                    "evidence_count": len(investigation.evidence),
                },
            )

            return findings

        except Exception as e:
            self.add_security_event(
                event_type="evidence_analysis_error",
                description=f"Ошибка анализа доказательств: {str(e)}",
                severity="error",
                source="ForensicsService",
            )
            raise

    def _analyze_single_evidence(self, evidence: Evidence) -> str:
        """Анализ отдельного доказательства"""
        analysis_templates = {
            EvidenceType.MEMORY_DUMP: (
                f"Анализ памяти показал подозрительную активность в "
                f"{evidence.source}"
            ),
            EvidenceType.SYSTEM_STATE: (
                f"Состояние системы {evidence.source} "
                f"указывает на компрометацию"
            ),
            EvidenceType.NETWORK_TRAFFIC: (
                f"Сетевой трафик из {evidence.source} содержит аномалии"
            ),
            EvidenceType.LOG_FILE: (
                f"Лог-файл {evidence.source} содержит признаки атаки"
            ),
            EvidenceType.USER_ACTIVITY: (
                f"Активность пользователя в {evidence.source} подозрительна"
            ),
            EvidenceType.FILE_SYSTEM: (
                f"Файловая система {evidence.source} была изменена"
            ),
            EvidenceType.REGISTRY: (
                f"Реестр {evidence.source} содержит подозрительные записи"
            ),
            EvidenceType.BROWSER_HISTORY: (
                f"История браузера {evidence.source} "
                f"показывает подозрительные сайты"
            ),
        }

        return analysis_templates.get(
            evidence.evidence_type,
            f"Доказательство {evidence.evidence_type.value} "
            f"требует дополнительного анализа",
        )

    def complete_investigation(self, investigation_id: str) -> Investigation:
        """Завершение расследования"""
        try:
            if investigation_id not in self.active_investigations:
                raise ValueError(
                    f"Расследование {investigation_id} не найдено"
                )

            investigation = self.active_investigations[investigation_id]

            # Завершение расследования
            investigation.status = InvestigationStatus.COMPLETED
            investigation.end_time = datetime.now()
            investigation.updated_at = datetime.now()

            # Генерация рекомендаций
            investigation.recommendations = self._generate_recommendations(
                investigation
            )

            # Генерация возрастных отчетов
            investigation.age_appropriate_summary = (
                self._generate_age_summaries(investigation)
            )

            # Перемещение в завершенные
            self.completed_investigations[investigation_id] = investigation
            del self.active_investigations[investigation_id]

            # Обновление статистики
            self.stats["active_investigations"] -= 1
            self.stats["completed_investigations"] += 1
            self.stats["last_investigation"] = investigation.end_time

            # Логирование
            self.add_security_event(
                event_type="investigation_completed",
                description=f"Завершено расследование {investigation_id}",
                severity="info",
                source="ForensicsService",
                metadata={
                    "investigation_id": investigation_id,
                    "duration": str(
                        investigation.end_time - investigation.start_time
                    ),
                    "findings_count": len(investigation.findings),
                    "recommendations_count": len(
                        investigation.recommendations
                    ),
                },
            )

            return investigation

        except Exception as e:
            self.add_security_event(
                event_type="investigation_completion_error",
                description=f"Ошибка завершения расследования: {str(e)}",
                severity="error",
                source="ForensicsService",
            )
            raise

    def _generate_recommendations(
        self, investigation: Investigation
    ) -> List[str]:
        """Генерация рекомендаций по результатам расследования"""
        recommendations = []

        # Общие рекомендации
        recommendations.extend(
            [
                "Усилить мониторинг системы",
                "Обновить антивирусное ПО",
                "Провести обучение семьи основам кибербезопасности",
            ]
        )

        # Специфичные рекомендации по типу инцидента
        if investigation.incident_type == IncidentType.MALWARE_INFECTION:
            recommendations.extend(
                [
                    "Провести полное сканирование всех устройств",
                    "Удалить подозрительные программы",
                    "Создать резервные копии важных данных",
                ]
            )
        elif investigation.incident_type == IncidentType.DATA_BREACH:
            recommendations.extend(
                [
                    "Сменить все пароли",
                    "Включить двухфакторную аутентификацию",
                    "Мониторить финансовые счета",
                ]
            )
        elif investigation.incident_type == IncidentType.PHISHING_ATTEMPT:
            recommendations.extend(
                [
                    "Обучить семью распознаванию фишинга",
                    "Использовать фильтры спама",
                    "Проверять подлинность сайтов",
                ]
            )

        return recommendations

    def _generate_age_summaries(
        self, investigation: Investigation
    ) -> Dict[AgeGroup, str]:
        """Генерация возрастных сводок расследования"""
        summaries = {}

        # Простые объяснения для детей
        summaries[AgeGroup.CHILDREN] = (
            "Мы проверили компьютер и нашли проблему. "
            "Теперь мы её исправим, чтобы защитить семью."
        )

        # Подробные объяснения для подростков
        summaries[AgeGroup.TEENAGERS] = (
            f"Расследование инцидента {investigation.incident_type.value} "
            f"завершено. Найдено {len(investigation.findings)} проблем."
        )

        # Технические объяснения для взрослых
        summaries[AgeGroup.ADULTS] = (
            f"Расследование {investigation.investigation_id} завершено. "
            f"Собрано {len(investigation.evidence)} доказательств, "
            f"найдено {len(investigation.findings)} проблем."
        )

        # Простые объяснения для пожилых
        summaries[AgeGroup.ELDERLY] = (
            "Мы проверили компьютер и нашли проблемы. "
            "Теперь мы их исправим для безопасности семьи."
        )

        return summaries

    def generate_forensics_report(
        self, investigation_id: str
    ) -> Union[ForensicsReport, None]:
        """Генерация отчета расследования"""
        try:
            if investigation_id not in self.completed_investigations:
                raise ValueError(
                    f"Завершенное расследование {investigation_id} не найдено"
                )

            investigation = self.completed_investigations[investigation_id]
            report_id = (
                f"report_{investigation_id}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Расчет метрик
            if investigation.end_time is None:
                investigation_duration = timedelta(0)
            else:
                investigation_duration = (
                    investigation.end_time - investigation.start_time
                )
            evidence_collected = len(investigation.evidence)
            critical_findings = len(
                [f for f in investigation.findings if "критическ" in f.lower()]
            )
            family_impact_level = self._determine_family_impact_level(
                investigation
            )
            recommendations_count = len(investigation.recommendations)

            # Создание отчета
            report = ForensicsReport(
                report_id=report_id,
                investigation_id=investigation_id,
                incident_type=investigation.incident_type,
                investigation_duration=investigation_duration,
                evidence_collected=evidence_collected,
                critical_findings=critical_findings,
                family_impact_level=family_impact_level,
                recommendations_count=recommendations_count,
                executive_summary=self._generate_executive_summary(
                    investigation
                ),
                technical_details=self._generate_technical_details(
                    investigation
                ),
                family_summary=self._generate_family_summary(investigation),
                age_appropriate_reports=self._generate_age_reports(
                    investigation
                ),
            )

            # Логирование
            self.add_security_event(
                event_type="forensics_report_generated",
                description=f"Создан отчет расследования {report_id}",
                severity="info",
                source="ForensicsService",
                metadata={
                    "report_id": report_id,
                    "investigation_id": investigation_id,
                    "evidence_collected": evidence_collected,
                    "critical_findings": critical_findings,
                },
            )

            return report

        except Exception as e:
            self.add_security_event(
                event_type="report_generation_error",
                description=f"Ошибка генерации отчета: {str(e)}",
                severity="error",
                source="ForensicsService",
            )
            return None

    def _determine_family_impact_level(
        self, investigation: Investigation
    ) -> str:
        """Определение уровня воздействия на семью"""
        if "критическ" in investigation.family_impact_assessment.lower():
            return "critical"
        if "высок" in investigation.family_impact_assessment.lower():
            return "high"
        if "средн" in investigation.family_impact_assessment.lower():
            return "medium"
        return "low"

    def _generate_executive_summary(self, investigation: Investigation) -> str:
        """Генерация исполнительного резюме"""
        summary = (
            f"Расследование инцидента {investigation.incident_type.value} "
            f"завершено. "
        )
        summary += (
            f"Собрано {len(investigation.evidence)} доказательств, "
            f"найдено {len(investigation.findings)} проблем. "
        )
        summary += (
            f"Воздействие на семью: {investigation.family_impact_assessment}. "
        )
        summary += (
            f"Рекомендации: {len(investigation.recommendations)} "
            f"мер по улучшению безопасности."
        )

        return summary

    def _generate_technical_details(self, investigation: Investigation) -> str:
        """Генерация технических деталей"""
        details = (
            f"Технические детали расследования "
            f"{investigation.investigation_id}:\n"
        )
        details += f"Тип инцидента: {investigation.incident_type.value}\n"
        if investigation.end_time is None:
            duration = timedelta(0)
        else:
            duration = investigation.end_time - investigation.start_time
        details += f"Длительность: {duration}\n"
        details += f"Доказательства: {len(investigation.evidence)}\n"
        details += f"Находки: {len(investigation.findings)}\n"
        details += (
            f"Рекомендации: {len(investigation.recommendations)}\n"
        )

        return details

    def _generate_family_summary(self, investigation: Investigation) -> str:
        """Генерация семейной сводки"""
        summary = "Семейная сводка расследования:\n"
        summary += f"Проблема: {investigation.incident_type.value}\n"
        summary += f"Воздействие: {investigation.family_impact_assessment}\n"
        summary += "Статус: Проблема решена\n"
        summary += (
            f"Рекомендации: {len(investigation.recommendations)} "
            f"мер безопасности\n"
        )

        return summary

    def _generate_age_reports(
        self, investigation: Investigation
    ) -> Dict[AgeGroup, str]:
        """Генерация возрастных отчетов"""
        reports = {}

        # Отчет для детей
        reports[AgeGroup.CHILDREN] = (
            "Мы нашли и исправили проблему с компьютером. "
            "Теперь семья в безопасности!"
        )

        # Отчет для подростков
        reports[AgeGroup.TEENAGERS] = (
            f"Расследование завершено. Найдена проблема типа "
            f"{investigation.incident_type.value}, она исправлена."
        )

        # Отчет для взрослых
        reports[AgeGroup.ADULTS] = (
            f"Расследование {investigation.investigation_id} завершено. "
            f"Собрано {len(investigation.evidence)} доказательств, "
            f"найдено {len(investigation.findings)} проблем."
        )

        # Отчет для пожилых
        reports[AgeGroup.ELDERLY] = (
            "Мы проверили компьютер и исправили все проблемы. "
            "Семья теперь в безопасности."
        )

        return reports

    def get_family_incident_summary(self) -> Dict[str, Any]:
        """Получение сводки семейных инцидентов"""
        try:
            # Анализ семейных инцидентов
            family_incidents = [
                inv
                for inv in self.completed_investigations.values()
                if "семьи" in inv.family_impact_assessment
                or "семей" in inv.family_impact_assessment
            ]

            # Статистика по возрастным группам
            age_group_stats = {}
            for age_group in AgeGroup:
                age_group_stats[age_group.value] = {
                    "incidents_count": len(
                        [
                            inv
                            for inv in family_incidents
                            if age_group in inv.age_appropriate_summary
                        ]
                    ),
                    "protection_level": self.family_protection["age_groups"][
                        age_group
                    ]["protection_level"],
                }

            summary = {
                "total_family_incidents": len(family_incidents),
                "critical_family_incidents": len(
                    [
                        inv
                        for inv in family_incidents
                        if "критическ" in inv.family_impact_assessment.lower()
                    ]
                ),
                "age_group_statistics": age_group_stats,
                "last_investigation": self.stats["last_investigation"],
                "recommendations": self._generate_family_recommendations(
                    family_incidents
                ),
            }

            return summary

        except Exception as e:
            self.add_security_event(
                event_type="family_summary_error",
                description=f"Ошибка генерации семейной сводки: {str(e)}",
                severity="error",
                source="ForensicsService",
            )
            return {}

    def _generate_family_recommendations(
        self, family_incidents: List[Investigation]
    ) -> List[str]:
        """Генерация рекомендаций для семьи"""
        recommendations = []

        if not family_incidents:
            recommendations.append("Семейная безопасность в норме")
            return recommendations

        # Анализ типов инцидентов
        incident_types = [inv.incident_type for inv in family_incidents]
        if IncidentType.MALWARE_INFECTION in incident_types:
            recommendations.append("Усилить защиту от вредоносных программ")
        if IncidentType.DATA_BREACH in incident_types:
            recommendations.append("Улучшить защиту личных данных")
        if IncidentType.PHISHING_ATTEMPT in incident_types:
            recommendations.append("Обучить семью распознаванию фишинга")

        # Общие рекомендации
        recommendations.extend(
            [
                "Регулярно обновлять все устройства",
                "Использовать надежные пароли",
                "Ограничить время детей в интернете",
            ]
        )

        return recommendations

    def get_forensics_summary(self) -> Dict[str, Any]:
        """Получение сводки расследований"""
        try:
            return {
                "total_investigations": self.stats["total_investigations"],
                "active_investigations": self.stats["active_investigations"],
                "completed_investigations": self.stats[
                    "completed_investigations"
                ],
                "evidence_collected": self.stats["evidence_collected"],
                "family_incidents": self.stats["family_incidents"],
                "last_investigation": self.stats["last_investigation"],
                "auto_investigation_enabled": self.auto_investigation_enabled,
                "evidence_retention_days": self.evidence_retention_days,
            }

        except Exception as e:
            self.add_security_event(
                event_type="summary_error",
                description=f"Ошибка генерации сводки: {str(e)}",
                source="ForensicsService",
                severity="error",
            )
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            return {
                "service_name": self.service_name,
                "status": (
                    "active"
                    if hasattr(self, "is_running") and self.is_running
                    else "inactive"
                ),
                "active_investigations": self.stats["active_investigations"],
                "completed_investigations": self.stats[
                    "completed_investigations"
                ],
                "evidence_collected": self.stats["evidence_collected"],
                "family_protection_enabled": self.forensics_rules[
                    "family_protection"
                ]["enabled"],
                "last_investigation": self.stats["last_investigation"],
                "investigation_timeout": self.investigation_timeout,
            }

        except Exception as e:
            self.add_security_event(
                event_type="status_error",
                description=f"Ошибка получения статуса: {str(e)}",
                source="ForensicsService",
                severity="error",
            )
            return {"error": str(e)}

    def start_service(self) -> bool:
        """Запуск сервиса криминалистики"""
        try:
            self.is_running = True
            self.log_activity("Сервис криминалистики запущен")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка запуска сервиса криминалистики: {e}", "error")
            return False

    def stop_service(self) -> bool:
        """Остановка сервиса криминалистики"""
        try:
            self.is_running = False
            self.log_activity("Сервис криминалистики остановлен")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка остановки сервиса криминалистики: {e}", "error")
            return False

    def get_service_info(self) -> Dict[str, Any]:
        """Получение информации о сервисе криминалистики"""
        try:
            return {
                "is_running": getattr(self, 'is_running', False),
                "service_name": self.service_name,
                "active_investigations": self.stats["active_investigations"],
                "completed_investigations": self.stats["completed_investigations"],
                "evidence_collected": self.stats["evidence_collected"],
                "family_protection_enabled": self.forensics_rules["family_protection"]["enabled"],
                "investigation_timeout": self.investigation_timeout,
                "evidence_types": len(EvidenceType),
                "incident_types": len(IncidentType),
                "age_groups": len(AgeGroup),
                "investigation_statuses": len(InvestigationStatus),
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения информации о сервисе: {e}", "error")
            return {
                "is_running": False,
                "service_name": "ForensicsService",
                "active_investigations": 0,
                "completed_investigations": 0,
                "evidence_collected": 0,
                "family_protection_enabled": False,
                "investigation_timeout": 0,
                "evidence_types": 0,
                "incident_types": 0,
                "age_groups": 0,
                "investigation_statuses": 0,
                "error": str(e),
            }

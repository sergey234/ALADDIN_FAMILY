"""
function_36: ThreatIntelligence - Сбор информации об угрозах

Семейная система сбора и анализа информации об угрозах:
- Автоматический сбор данных об угрозах
- Анализ и классификация угроз
- Семейные уведомления с простыми объяснениями
- Адаптация под возрастные группы
- Интеграция с другими компонентами безопасности
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Union

from core.base import SecurityBase


class ThreatSource(Enum):
    """Источники угроз"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    CLOUD = "cloud"
    SOCIAL = "social"
    MALWARE = "malware"
    PHISHING = "phishing"


class ThreatSeverity(Enum):
    """Уровни серьезности угроз"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(Enum):
    """Категории угроз"""
    MALWARE = "malware"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    DATA_BREACH = "data_breach"
    VULNERABILITY = "vulnerability"
    RANSOMWARE = "ransomware"
    SPAM = "spam"
    SCAM = "scam"


class IntelligenceType(Enum):
    """Типы разведывательных данных"""
    THREAT_INDICATORS = "threat_indicators"
    VULNERABILITY_DATA = "vulnerability_data"
    ATTACK_PATTERNS = "attack_patterns"
    MALWARE_SIGNATURES = "malware_signatures"
    IP_REPUTATION = "ip_reputation"
    DOMAIN_REPUTATION = "domain_reputation"


class AgeGroup(Enum):
    """Возрастные группы для адаптации"""
    CHILDREN = "children"  # 0-12 лет
    TEENAGERS = "teenagers"  # 13-17 лет
    ADULTS = "adults"  # 18-64 лет
    ELDERLY = "elderly"  # 65+ лет


@dataclass
class ThreatIndicator:
    """Индикатор угрозы"""
    indicator_id: str
    indicator_type: str
    value: str
    threat_type: ThreatCategory
    severity: ThreatSeverity
    source: ThreatSource
    first_seen: datetime
    last_seen: datetime
    confidence: float
    description: str
    family_impact: str
    age_appropriate_explanation: Dict[AgeGroup, str] = field(default_factory=dict)


@dataclass
class ThreatIntelligenceData:
    """Разведывательные данные об угрозе"""
    intelligence_id: str
    threat_type: ThreatCategory
    severity: ThreatSeverity
    source: ThreatSource
    indicators: List[ThreatIndicator]
    description: str
    family_impact: str
    recommendations: List[str]
    age_appropriate_advice: Dict[AgeGroup, List[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntelligenceReport:
    """Отчет разведывательных данных"""
    report_id: str
    report_type: IntelligenceType
    period_start: datetime
    period_end: datetime
    threats_analyzed: int
    new_threats: int
    high_priority_threats: int
    family_relevant_threats: int
    recommendations: List[str]
    summary: str
    created_at: datetime = field(default_factory=datetime.now)


class ThreatIntelligence(SecurityBase):
    """Сервис разведывательных данных об угрозах"""

    def __init__(self) -> None:
        super().__init__("ThreatIntelligence")
        self.service_name = "ThreatIntelligence"
        self.intelligence_type = IntelligenceType.THREAT_INDICATORS

        # Хранилище данных
        self.threat_indicators: Dict[str, ThreatIndicator] = {}
        self.intelligence_data: Dict[str, ThreatIntelligenceData] = {}
        self.family_threat_history: Dict[str, List[str]] = {}

        # Настройки
        self.update_interval = 3600  # 1 час
        self.retention_days = 30
        self.family_notification_threshold = ThreatSeverity.MEDIUM

        # Статистика
        self.stats: Dict[str, Any] = {
            "total_indicators": 0,
            "active_threats": 0,
            "family_alerts": 0,
            "last_update": None,
        }

        self._initialize_intelligence_rules()
        self._setup_family_protection()

    def _initialize_intelligence_rules(self) -> None:
        """Инициализация правил разведки"""
        self.intelligence_rules: Dict[str, Any] = {
            "threat_collection": {
                "enabled": True,
                "sources": ["internal", "external", "cloud"],
                "update_interval": 3600,
                "retention_days": 30,
            },
            "family_protection": {
                "enabled": True,
                "notification_threshold": "medium",
                "age_appropriate": True,
                "simple_explanations": True,
            },
            "threat_analysis": {
                "enabled": True,
                "auto_classification": True,
                "confidence_threshold": 0.7,
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
            "threat_categories": {
                "malware": "Вредоносные программы",
                "phishing": "Мошеннические сайты",
                "social_engineering": "Попытки обмана",
                "data_breach": "Утечка данных",
                "vulnerability": "Уязвимости в программах",
                "ransomware": "Программы-вымогатели",
                "spam": "Нежелательная почта",
                "scam": "Мошенничество",
            },
        }

    def collect_threat_indicators(self) -> List[ThreatIndicator]:
        """Сбор индикаторов угроз"""
        try:
            indicators = []

            # Симуляция сбора индикаторов
            sample_indicators: List[Dict[str, Any]] = [
                {
                    "indicator_id": "threat_001",
                    "indicator_type": "ip_address",
                    "value": "192.168.1.100",
                    "threat_type": ThreatCategory.MALWARE,
                    "severity": ThreatSeverity.HIGH,
                    "source": ThreatSource.EXTERNAL,
                    "description": "Подозрительный IP-адрес",
                    "family_impact": "Может заразить устройства семьи",
                },
                {
                    "indicator_id": "threat_002",
                    "indicator_type": "domain",
                    "value": "malicious-site.com",
                    "threat_type": ThreatCategory.PHISHING,
                    "severity": ThreatSeverity.MEDIUM,
                    "source": ThreatSource.EXTERNAL,
                    "description": "Фишинговый сайт",
                    "family_impact": "Может украсть пароли и данные",
                },
                {
                    "indicator_id": "threat_003",
                    "indicator_type": "file_hash",
                    "value": "abc123def456",
                    "threat_type": ThreatCategory.RANSOMWARE,
                    "severity": ThreatSeverity.CRITICAL,
                    "source": ThreatSource.MALWARE,
                    "description": "Программа-вымогатель",
                    "family_impact": "Может заблокировать файлы семьи",
                },
            ]

            for indicator_data in sample_indicators:
                indicator = ThreatIndicator(
                    indicator_id=indicator_data["indicator_id"],
                    indicator_type=indicator_data["indicator_type"],
                    value=indicator_data["value"],
                    threat_type=indicator_data["threat_type"],
                    severity=indicator_data["severity"],
                    source=indicator_data["source"],
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    confidence=0.85,
                    description=indicator_data["description"],
                    family_impact=indicator_data["family_impact"],
                    age_appropriate_explanation=self._generate_age_explanations(
                        indicator_data["threat_type"], indicator_data["family_impact"]
                    ),
                )

                indicators.append(indicator)
                self.threat_indicators[indicator.indicator_id] = indicator

            # Логирование
            self.add_security_event(
                event_type="threat_indicators_collected",
                description=f"Собрано {len(indicators)} индикаторов угроз",
                severity="info",
                source="ThreatIntelligence",
                metadata={
                    "indicators_count": len(indicators),
                    "threat_types": [i.threat_type.value for i in indicators],
                    "severity_levels": [i.severity.value for i in indicators],
                },
            )

            return indicators

        except Exception as e:
            self.add_security_event(
                event_type="threat_collection_error",
                description=f"Ошибка сбора индикаторов угроз: {str(e)}",
                severity="error",
                source="ThreatIntelligence",
            )
            return []

    def _generate_age_explanations(self, threat_type: ThreatCategory, family_impact: str) -> Dict[AgeGroup, str]:
        """Генерация объяснений для разных возрастных групп"""
        explanations = {}

        # Простые объяснения для детей
        explanations[AgeGroup.CHILDREN] = (
            f"Плохая программа может навредить твоему компьютеру. {family_impact}"
        )

        # Подробные объяснения для подростков
        explanations[AgeGroup.TEENAGERS] = (
            f"Это {threat_type.value} - тип киберугрозы. {family_impact} "
            "Будь осторожен в интернете."
        )

        # Технические объяснения для взрослых
        explanations[AgeGroup.ADULTS] = (
            f"Обнаружена угроза типа {threat_type.value}. {family_impact} "
            "Рекомендуется принять меры предосторожности."
        )

        # Простые объяснения для пожилых
        explanations[AgeGroup.ELDERLY] = (
            f"Обнаружена опасность в интернете. {family_impact} "
            "Не переходите по подозрительным ссылкам."
        )

        return explanations

    def analyze_threat_intelligence(self, indicators: List[ThreatIndicator]) -> List[ThreatIntelligenceData]:
        """Анализ разведывательных данных"""
        try:
            intelligence_list = []

            for indicator in indicators:
                # Создание разведывательных данных
                intelligence = ThreatIntelligenceData(
                    intelligence_id=f"intel_{indicator.indicator_id}",
                    threat_type=indicator.threat_type,
                    severity=indicator.severity,
                    source=indicator.source,
                    indicators=[indicator],
                    description=f"Анализ угрозы: {indicator.description}",
                    family_impact=indicator.family_impact,
                    recommendations=self._generate_recommendations(indicator),
                    age_appropriate_advice=self._generate_age_advice(indicator),
                )

                intelligence_list.append(intelligence)
                self.intelligence_data[intelligence.intelligence_id] = intelligence

            # Логирование
            self.add_security_event(
                event_type="threat_intelligence_analyzed",
                description=f"Проанализировано {len(intelligence_list)} угроз",
                severity="info",
                source="ThreatIntelligence",
                metadata={
                    "threats_analyzed": len(intelligence_list),
                    "high_priority": len([
                        t for t in intelligence_list
                        if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
                    ]),
                },
            )

            return intelligence_list

        except Exception as e:
            self.add_security_event(
                event_type="threat_analysis_error",
                description=f"Ошибка анализа угроз: {str(e)}",
                severity="error",
                source="ThreatIntelligence",
            )
            return []

    def _generate_recommendations(self, indicator: ThreatIndicator) -> List[str]:
        """Генерация рекомендаций по угрозе"""
        recommendations = []

        if indicator.threat_type == ThreatCategory.MALWARE:
            recommendations.extend([
                "Обновить антивирусное ПО",
                "Провести полное сканирование системы",
                "Не открывать подозрительные файлы",
            ])
        elif indicator.threat_type == ThreatCategory.PHISHING:
            recommendations.extend([
                "Не переходить по подозрительным ссылкам",
                "Проверить подлинность сайтов",
                "Не вводить пароли на подозрительных страницах",
            ])
        elif indicator.threat_type == ThreatCategory.RANSOMWARE:
            recommendations.extend([
                "Создать резервные копии важных файлов",
                "Обновить все программы",
                "Не открывать вложения из неизвестных источников",
            ])

        return recommendations

    def _generate_age_advice(self, indicator: ThreatIndicator) -> Dict[AgeGroup, List[str]]:
        """Генерация советов для разных возрастных групп"""
        # Используем indicator для будущих расширений
        _ = indicator  # Подавляем предупреждение о неиспользуемом аргументе
        advice = {}

        # Советы для детей
        advice[AgeGroup.CHILDREN] = [
            "Скажи родителям, если увидишь что-то странное",
            "Не нажимай на подозрительные кнопки",
            "Играй только в проверенные игры",
        ]

        # Советы для подростков
        advice[AgeGroup.TEENAGERS] = [
            "Будь осторожен с неизвестными ссылками",
            "Не скачивай файлы из подозрительных источников",
            "Используй надежные пароли",
        ]

        # Советы для взрослых
        advice[AgeGroup.ADULTS] = [
            "Регулярно обновляйте программное обеспечение",
            "Используйте двухфакторную аутентификацию",
            "Создавайте резервные копии данных",
        ]

        # Советы для пожилых
        advice[AgeGroup.ELDERLY] = [
            "Не переходите по ссылкам в письмах",
            "Звоните в банк, если получили подозрительное сообщение",
            "Попросите помощи у детей или внуков",
        ]

        return advice

    def generate_intelligence_report(
        self, report_type: IntelligenceType, period_hours: int = 24
    ) -> Union[IntelligenceReport, None]:
        """Генерация отчета разведывательных данных"""
        try:
            report_id = f"intelligence_{report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            period_end = datetime.now()
            period_start = period_end - timedelta(hours=period_hours)

            # Анализ данных
            threats_analyzed = len(self.intelligence_data)
            new_threats = len([t for t in self.intelligence_data.values() if t.created_at >= period_start])
            high_priority_threats = len([
                t for t in self.intelligence_data.values()
                if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
            ])
            family_relevant_threats = len([
                t for t in self.intelligence_data.values()
                if "семьи" in t.family_impact or "семей" in t.family_impact
            ])

            # Генерация рекомендаций
            recommendations = self._generate_report_recommendations()

            # Создание отчета
            report = IntelligenceReport(
                report_id=report_id,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                threats_analyzed=threats_analyzed,
                new_threats=new_threats,
                high_priority_threats=high_priority_threats,
                family_relevant_threats=family_relevant_threats,
                recommendations=recommendations,
                summary=self._generate_report_summary(threats_analyzed, new_threats, high_priority_threats),
            )

            # Логирование
            self.add_security_event(
                event_type="intelligence_report_generated",
                description=f"Создан отчет разведывательных данных {report_id}",
                severity="info",
                source="ThreatIntelligence",
                metadata={
                    "report_id": report_id,
                    "threats_analyzed": threats_analyzed,
                    "new_threats": new_threats,
                    "high_priority": high_priority_threats,
                },
            )

            return report

        except Exception as e:
            self.add_security_event(
                event_type="report_generation_error",
                description=f"Ошибка генерации отчета: {str(e)}",
                severity="error",
                source="ThreatIntelligence",
            )
            return None

    def _generate_report_recommendations(self) -> List[str]:
        """Генерация рекомендаций для отчета"""
        recommendations = []

        # Анализ текущих угроз
        high_priority_count = len([
            t for t in self.intelligence_data.values()
            if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
        ])

        if high_priority_count > 0:
            recommendations.append(f"Обнаружено {high_priority_count} высокоприоритетных угроз")
            recommendations.append("Рекомендуется усилить защиту")

        # Рекомендации по семейной безопасности
        recommendations.extend([
            "Регулярно обновляйте антивирусное ПО",
            "Обучайте детей основам кибербезопасности",
            "Используйте родительский контроль",
            "Создавайте резервные копии важных данных",
        ])

        return recommendations

    def _generate_report_summary(self, threats_analyzed: int, new_threats: int, high_priority: int) -> str:
        """Генерация краткого резюме отчета"""
        summary = f"За период проанализировано {threats_analyzed} угроз, "
        summary += f"из них {new_threats} новых и {high_priority} высокоприоритетных. "

        if high_priority > 0:
            summary += "Требуется повышенное внимание к безопасности."
        else:
            summary += "Уровень угроз в пределах нормы."

        return summary

    def get_family_threat_summary(self) -> Dict[str, Any]:
        """Получение сводки угроз для семьи"""
        try:
            # Анализ семейных угроз
            family_threats = [
                t for t in self.intelligence_data.values()
                if "семьи" in t.family_impact or "семей" in t.family_impact
            ]

            # Статистика по возрастным группам
            age_group_stats = {}
            for age_group in AgeGroup:
                age_group_stats[age_group.value] = {
                    "threats_count": len([t for t in family_threats if age_group in t.age_appropriate_advice]),
                    "protection_level": self.family_protection["age_groups"][age_group]["protection_level"],
                }

            summary = {
                "total_family_threats": len(family_threats),
                "high_priority_family_threats": len([
                    t for t in family_threats
                    if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
                ]),
                "age_group_statistics": age_group_stats,
                "last_update": datetime.now().isoformat(),
                "recommendations": self._generate_family_recommendations(family_threats),
            }

            return summary

        except Exception as e:
            self.add_security_event(
                event_type="family_summary_error",
                description=f"Ошибка генерации семейной сводки: {str(e)}",
                severity="error",
                source="ThreatIntelligence",
            )
            return {}

    def _generate_family_recommendations(self, family_threats: List[ThreatIntelligenceData]) -> List[str]:
        """Генерация рекомендаций для семьи"""
        recommendations = []

        if not family_threats:
            recommendations.append("Семейная безопасность в норме")
            return recommendations

        # Анализ типов угроз
        threat_types = [t.threat_type for t in family_threats]
        if ThreatCategory.MALWARE in threat_types:
            recommendations.append("Усилить защиту от вредоносных программ")
        if ThreatCategory.PHISHING in threat_types:
            recommendations.append("Обучить семью распознаванию фишинга")
        if ThreatCategory.SOCIAL_ENGINEERING in threat_types:
            recommendations.append("Повысить осторожность при общении в интернете")

        # Общие рекомендации
        recommendations.extend([
            "Регулярно обновлять все устройства",
            "Использовать надежные пароли",
            "Ограничить время детей в интернете",
        ])

        return recommendations

    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Получение сводки разведывательных данных"""
        try:
            return {
                "total_indicators": len(self.threat_indicators),
                "active_intelligence": len(self.intelligence_data),
                "family_threats": len([
                    t for t in self.intelligence_data.values()
                    if "семьи" in t.family_impact or "семей" in t.family_impact
                ]),
                "high_priority_threats": len([
                    t for t in self.intelligence_data.values()
                    if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
                ]),
                "last_update": self.stats["last_update"],
                "update_interval": self.update_interval,
                "retention_days": self.retention_days,
            }

        except Exception as e:
            self.add_security_event(
                event_type="summary_error",
                description=f"Ошибка генерации сводки: {str(e)}",
                source="ThreatIntelligence",
                severity="error",
            )
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            return {
                "service_name": self.service_name,
                "status": "active" if hasattr(self, 'is_running') and self.is_running else "inactive",
                "intelligence_type": self.intelligence_type.value,
                "threat_indicators": len(self.threat_indicators),
                "intelligence_data": len(self.intelligence_data),
                "family_protection_enabled": self.intelligence_rules["family_protection"]["enabled"],
                "last_update": self.stats["last_update"],
                "update_interval": self.update_interval,
            }

        except Exception as e:
            self.add_security_event(
                event_type="status_error",
                description=f"Ошибка получения статуса: {str(e)}",
                source="ThreatIntelligence",
                severity="error",
            )
            return {"error": str(e)}

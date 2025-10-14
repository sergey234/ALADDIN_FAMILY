# -*- coding: utf-8 -*-
"""
ALADDIN Security System - ThreatDetection
Обнаружение угроз - КРИТИЧНО

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import datetime
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Путь к файлу конфигурации правил обнаружения угроз
THREAT_DETECTION_CONFIG = "data/threats/detection_rules.json"


class ThreatSeverity(Enum):
    """Уровень серьезности угрозы"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatStatus(Enum):
    """Статус угрозы"""

    DETECTED = "detected"
    ANALYZING = "analyzing"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class ThreatType(Enum):
    """Типы угроз"""

    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    UNKNOWN = "unknown"


@dataclass
class ThreatIndicator:
    """
    Индикатор угрозы.
    """

    indicator_id: str
    name: str
    pattern: str  # Регулярное выражение или строка для обнаружения
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float  # 0.0 - 1.0
    description: str
    source: str  # Источник индикатора
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "name": self.name,
            "pattern": self.pattern,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "description": self.description,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThreatIndicator":
        return cls(
            indicator_id=data["indicator_id"],
            name=data["name"],
            pattern=data["pattern"],
            threat_type=ThreatType(data["threat_type"]),
            severity=ThreatSeverity(data["severity"]),
            confidence=data["confidence"],
            description=data["description"],
            source=data["source"],
            created_at=data.get(
                "created_at", datetime.datetime.now().isoformat()
            ),
            updated_at=data.get(
                "updated_at", datetime.datetime.now().isoformat()
            ),
            enabled=data.get("enabled", True),
        )


@dataclass
class ThreatDetection:
    """
    Обнаруженная угроза.
    """

    detection_id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    status: ThreatStatus
    source_ip: Optional[str] = None
    target_ip: Optional[str] = None
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    description: str = ""
    indicators: List[str] = field(default_factory=list)  # ID индикаторов
    confidence: float = 0.0
    detected_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    analyzed_at: Optional[str] = None
    resolved_at: Optional[str] = None
    mitigation_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "source_ip": self.source_ip,
            "target_ip": self.target_ip,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "description": self.description,
            "indicators": self.indicators,
            "confidence": self.confidence,
            "detected_at": self.detected_at,
            "analyzed_at": self.analyzed_at,
            "resolved_at": self.resolved_at,
            "mitigation_actions": self.mitigation_actions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThreatDetection":
        return cls(
            detection_id=data["detection_id"],
            threat_type=ThreatType(data["threat_type"]),
            severity=ThreatSeverity(data["severity"]),
            status=ThreatStatus(data["status"]),
            source_ip=data.get("source_ip"),
            target_ip=data.get("target_ip"),
            user_id=data.get("user_id"),
            device_id=data.get("device_id"),
            description=data.get("description", ""),
            indicators=data.get("indicators", []),
            confidence=data.get("confidence", 0.0),
            detected_at=data.get(
                "detected_at", datetime.datetime.now().isoformat()
            ),
            analyzed_at=data.get("analyzed_at"),
            resolved_at=data.get("resolved_at"),
            mitigation_actions=data.get("mitigation_actions", []),
        )


class DetectionMetrics:
    """
    Метрики обнаружения угроз.
    """

    def __init__(self):
        self.total_detections = 0
        self.confirmed_threats = 0
        self.false_positives = 0
        self.avg_confidence = 0.0
        self.detection_by_type: Dict[str, int] = {}
        self.detection_by_severity: Dict[str, int] = {}
        self.last_updated = datetime.datetime.now().isoformat()

    def update_metrics(self, detection: ThreatDetection):
        """Обновляет метрики на основе нового обнаружения."""
        self.total_detections += 1

        if detection.status == ThreatStatus.CONFIRMED:
            self.confirmed_threats += 1
        elif detection.status == ThreatStatus.FALSE_POSITIVE:
            self.false_positives += 1

        # Обновляем среднюю уверенность
        if self.total_detections > 0:
            self.avg_confidence = (
                self.avg_confidence * (self.total_detections - 1)
                + detection.confidence
            ) / self.total_detections

        # Обновляем счетчики по типам
        threat_type = detection.threat_type.value
        self.detection_by_type[threat_type] = (
            self.detection_by_type.get(threat_type, 0) + 1
        )

        # Обновляем счетчики по серьезности
        severity = detection.severity.value
        self.detection_by_severity[severity] = (
            self.detection_by_severity.get(severity, 0) + 1
        )

        self.last_updated = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_detections": self.total_detections,
            "confirmed_threats": self.confirmed_threats,
            "false_positives": self.false_positives,
            "avg_confidence": self.avg_confidence,
            "detection_by_type": self.detection_by_type,
            "detection_by_severity": self.detection_by_severity,
            "last_updated": self.last_updated,
        }


class ThreatDetection:
    """
    Модуль обнаружения угроз.
    """

    def __init__(self, config_path: str = THREAT_DETECTION_CONFIG):
        self.config_path = config_path
        self.indicators: List[ThreatIndicator] = self._load_indicators()
        self.detections: List[ThreatDetection] = []
        self.metrics = DetectionMetrics()
        self.alert_threshold = 0.7  # Порог уверенности для алертов

    def _load_indicators(self) -> List[ThreatIndicator]:
        """Загружает индикаторы угроз из файла."""
        if not os.path.exists(self.config_path):
            return self._create_default_indicators()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [
                    ThreatIndicator.from_dict(ind)
                    for ind in data.get("indicators", [])
                ]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки индикаторов угроз: {e}")
            return self._create_default_indicators()

    def _create_default_indicators(self) -> List[ThreatIndicator]:
        """Создает набор индикаторов по умолчанию."""
        default_indicators = [
            ThreatIndicator(
                indicator_id="malware_001",
                name="Подозрительный исполняемый файл",
                pattern=r"\.(exe|bat|cmd|scr|pif|com)$",
                threat_type=ThreatType.MALWARE,
                severity=ThreatSeverity.HIGH,
                confidence=0.8,
                description="Обнаружен подозрительный исполняемый файл",
                source="file_analysis",
            ),
            ThreatIndicator(
                indicator_id="phishing_001",
                name="Подозрительная ссылка",
                pattern=r"https?://[a-zA-Z0-9.-]*\.(tk|ml|ga|cf|gq)",
                threat_type=ThreatType.PHISHING,
                severity=ThreatSeverity.MEDIUM,
                confidence=0.6,
                description="Обнаружена подозрительная ссылка",
                source="url_analysis",
            ),
            ThreatIndicator(
                indicator_id="ddos_001",
                name="Аномальный трафик",
                pattern=r"requests_per_second:\s*[5-9][0-9]{2,}",
                threat_type=ThreatType.DDOS,
                severity=ThreatSeverity.HIGH,
                confidence=0.7,
                description="Обнаружен аномально высокий трафик",
                source="network_analysis",
            ),
        ]
        self._save_indicators(default_indicators)
        return default_indicators

    def _save_indicators(self, indicators: List[ThreatIndicator]):
        """Сохраняет индикаторы в файл."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(
                {"indicators": [ind.to_dict() for ind in indicators]},
                f,
                indent=4,
                ensure_ascii=False,
            )

    def add_indicator(self, indicator: ThreatIndicator):
        """Добавляет новый индикатор угрозы."""
        self.indicators.append(indicator)
        self._save_indicators(self.indicators)
        print(f"Добавлен индикатор угрозы: {indicator.name}")

    def update_indicator(
        self, indicator_id: str, new_data: Dict[str, Any]
    ) -> bool:
        """Обновляет существующий индикатор."""
        for i, indicator in enumerate(self.indicators):
            if indicator.indicator_id == indicator_id:
                updated_indicator = ThreatIndicator.from_dict(
                    {**indicator.to_dict(), **new_data}
                )
                self.indicators[i] = updated_indicator
                self._save_indicators(self.indicators)
                print(f"Индикатор '{indicator_id}' обновлен.")
                return True
        print(f"Индикатор '{indicator_id}' не найден.")
        return False

    def delete_indicator(self, indicator_id: str) -> bool:
        """Удаляет индикатор по ID."""
        initial_len = len(self.indicators)
        self.indicators = [
            ind for ind in self.indicators if ind.indicator_id != indicator_id
        ]
        if len(self.indicators) < initial_len:
            self._save_indicators(self.indicators)
            print(f"Индикатор '{indicator_id}' удален.")
            return True
        print(f"Индикатор '{indicator_id}' не найден.")
        return False

    def analyze_data(
        self,
        data: str,
        source_ip: Optional[str] = None,
        target_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> List[ThreatDetection]:
        """
        Анализирует данные на предмет угроз.
        Возвращает список обнаруженных угроз.
        """
        detections = []

        for indicator in self.indicators:
            if not indicator.enabled:
                continue

            # Простая проверка по паттерну (в реальной системе здесь был бы regex)
            if indicator.pattern in data:
                detection = ThreatDetection(
                    detection_id=f"threat_{int(time.time())}_{len(detections)}",
                    threat_type=indicator.threat_type,
                    severity=indicator.severity,
                    status=ThreatStatus.DETECTED,
                    source_ip=source_ip,
                    target_ip=target_ip,
                    user_id=user_id,
                    device_id=device_id,
                    description=indicator.description,
                    indicators=[indicator.indicator_id],
                    confidence=indicator.confidence,
                )
                detections.append(detection)
                print(
                    f"Обнаружена угроза: {indicator.name} (уверенность: {indicator.confidence})"
                )

        # Добавляем обнаружения в список
        self.detections.extend(detections)

        # Обновляем метрики
        for detection in detections:
            self.metrics.update_metrics(detection)

        return detections

    def confirm_threat(self, detection_id: str) -> bool:
        """Подтверждает угрозу как реальную."""
        for detection in self.detections:
            if detection.detection_id == detection_id:
                detection.status = ThreatStatus.CONFIRMED
                detection.analyzed_at = datetime.datetime.now().isoformat()
                print(f"Угроза '{detection_id}' подтверждена.")
                return True
        print(f"Обнаружение '{detection_id}' не найдено.")
        return False

    def mark_false_positive(self, detection_id: str) -> bool:
        """Помечает угрозу как ложное срабатывание."""
        for detection in self.detections:
            if detection.detection_id == detection_id:
                detection.status = ThreatStatus.FALSE_POSITIVE
                detection.analyzed_at = datetime.datetime.now().isoformat()
                print(
                    f"Обнаружение '{detection_id}' помечено как ложное срабатывание."
                )
                return True
        print(f"Обнаружение '{detection_id}' не найдено.")
        return False

    def resolve_threat(
        self, detection_id: str, mitigation_actions: List[str]
    ) -> bool:
        """Разрешает угрозу с указанными действиями по устранению."""
        for detection in self.detections:
            if detection.detection_id == detection_id:
                detection.status = ThreatStatus.RESOLVED
                detection.resolved_at = datetime.datetime.now().isoformat()
                detection.mitigation_actions = mitigation_actions
                print(f"Угроза '{detection_id}' разрешена.")
                return True
        print(f"Обнаружение '{detection_id}' не найдено.")
        return False

    def get_detections(
        self,
        status: Optional[ThreatStatus] = None,
        threat_type: Optional[ThreatType] = None,
    ) -> List[ThreatDetection]:
        """Возвращает список обнаружений с опциональной фильтрацией."""
        filtered = self.detections

        if status:
            filtered = [d for d in filtered if d.status == status]

        if threat_type:
            filtered = [d for d in filtered if d.threat_type == threat_type]

        return filtered

    def get_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики обнаружения угроз."""
        return self.metrics.to_dict()

    def get_high_confidence_detections(self) -> List[ThreatDetection]:
        """Возвращает обнаружения с высокой уверенностью."""
        return [
            d for d in self.detections if d.confidence >= self.alert_threshold
        ]

    def export_detections(self, file_path: str):
        """Экспортирует обнаружения в файл."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                [d.to_dict() for d in self.detections],
                f,
                indent=4,
                ensure_ascii=False,
            )
        print(f"Обнаружения экспортированы в: {file_path}")

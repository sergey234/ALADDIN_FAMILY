# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Zero Trust Service
Упрощенная Zero Trust архитектура для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from core.base import SecurityBase
from core.security_base import IncidentSeverity, SecurityEvent, ThreatType


class TrustLevel(Enum):
    """Уровни доверия"""

    UNTRUSTED = "untrusted"  # Недоверенный
    LOW = "low"  # Низкий
    MEDIUM = "medium"  # Средний
    HIGH = "high"  # Высокий
    FULL = "full"  # Полный


class AccessDecision(Enum):
    """Решения по доступу"""

    ALLOW = "allow"  # Разрешить
    DENY = "deny"  # Запретить
    CHALLENGE = "challenge"  # Требовать дополнительную аутентификацию
    MONITOR = "monitor"  # Разрешить с мониторингом


class DeviceType(Enum):
    """Типы устройств"""

    MOBILE = "mobile"  # Мобильное устройство
    TABLET = "tablet"  # Планшет
    DESKTOP = "desktop"  # Настольный компьютер
    LAPTOP = "laptop"  # Ноутбук
    SMART_TV = "smart_tv"  # Умный телевизор
    IOT = "iot"  # IoT устройство


class NetworkType(Enum):
    """Типы сетей"""

    HOME = "home"  # Домашняя сеть
    WORK = "work"  # Рабочая сеть
    PUBLIC = "public"  # Публичная сеть
    UNKNOWN = "unknown"  # Неизвестная сеть


@dataclass
class DeviceProfile:
    """Профиль устройства"""

    device_id: str
    device_name: str
    device_type: DeviceType
    user_id: str
    family_id: str
    mac_address: str
    ip_address: str
    os_version: str
    app_version: str
    last_seen: datetime = field(default_factory=datetime.now)
    trust_score: float = 0.0
    is_trusted: bool = False
    security_patches: List[str] = field(default_factory=list)
    installed_apps: List[str] = field(default_factory=list)


@dataclass
class AccessRequest:
    """Запрос на доступ"""

    request_id: str
    user_id: str
    device_id: str
    resource: str
    action: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    network_type: NetworkType = NetworkType.UNKNOWN
    location: Optional[str] = None
    risk_score: float = 0.0


@dataclass
class AccessPolicy:
    """Политика доступа"""

    policy_id: str
    name: str
    description: str
    resource_pattern: str
    user_conditions: Dict[str, Any]
    device_conditions: Dict[str, Any]
    network_conditions: Dict[str, Any]
    time_conditions: Dict[str, Any]
    trust_requirements: TrustLevel
    action: AccessDecision
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class ZeroTrustService(SecurityBase):
    """
    Упрощенная Zero Trust архитектура для семей
    Принцип "Никогда не доверяй, всегда проверяй"
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ZeroTrustService", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.device_profiles: Dict[str, DeviceProfile] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.access_history: List[AccessRequest] = []
        self.trust_scores: Dict[str, float] = {}
        self.blocked_devices: Set[str] = set()
        self.suspicious_activities: List[SecurityEvent] = []
        self.activity_log: List[SecurityEvent] = []

        # Настройки по умолчанию
        self.default_trust_threshold = 0.7
        self.session_timeout = timedelta(hours=8)
        self.max_failed_attempts = 3
        self.trust_decay_rate = 0.1  # Снижение доверия в день

        self._initialize_default_policies()

    def _initialize_default_policies(self) -> None:
        """Инициализация политик по умолчанию"""
        try:
            # Политика для домашней сети
            home_policy = AccessPolicy(
                policy_id="home_network_policy",
                name="Домашняя сеть",
                description="Политика для устройств в домашней сети",
                resource_pattern="*",
                user_conditions={"family_member": True},
                device_conditions={
                    "device_type": ["mobile", "tablet", "desktop", "laptop"]
                },
                network_conditions={"network_type": "home"},
                time_conditions={"time_range": "06:00-23:00"},
                trust_requirements=TrustLevel.MEDIUM,
                action=AccessDecision.ALLOW,
            )
            self.access_policies[home_policy.policy_id] = home_policy

            # Политика для публичной сети
            public_policy = AccessPolicy(
                policy_id="public_network_policy",
                name="Публичная сеть",
                description="Политика для устройств в публичной сети",
                resource_pattern="*",
                user_conditions={"family_member": True},
                device_conditions={
                    "device_type": ["mobile", "tablet", "laptop"]
                },
                network_conditions={"network_type": "public"},
                time_conditions={"time_range": "06:00-22:00"},
                trust_requirements=TrustLevel.HIGH,
                action=AccessDecision.CHALLENGE,
            )
            self.access_policies[public_policy.policy_id] = public_policy

            # Политика для IoT устройств
            iot_policy = AccessPolicy(
                policy_id="iot_device_policy",
                name="IoT устройства",
                description="Политика для IoT устройств",
                resource_pattern="iot/*",
                user_conditions={"family_member": True},
                device_conditions={"device_type": ["iot", "smart_tv"]},
                network_conditions={"network_type": "home"},
                time_conditions={"time_range": "00:00-23:59"},
                trust_requirements=TrustLevel.LOW,
                action=AccessDecision.MONITOR,
            )
            self.access_policies[iot_policy.policy_id] = iot_policy

            self.logger.info(
                "Инициализированы политики Zero Trust по умолчанию"
            )

        except Exception as e:
            self.logger.error(f"Ошибка инициализации политик: {e}")

    def register_device(
        self,
        device_id: str,
        device_name: str,
        device_type: DeviceType,
        user_id: str,
        family_id: str,
        mac_address: str,
        ip_address: str,
        os_version: str,
        app_version: str,
    ) -> bool:
        """
        Регистрация нового устройства
        Args:
            device_id: ID устройства
            device_name: Название устройства
            device_type: Тип устройства
            user_id: ID пользователя
            family_id: ID семьи
            mac_address: MAC адрес
            ip_address: IP адрес
            os_version: Версия ОС
            app_version: Версия приложения
        Returns:
            bool: True если устройство зарегистрировано
        """
        try:
            # Проверяем, не заблокировано ли устройство
            if device_id in self.blocked_devices:
                self.logger.warning(
                    f"Попытка регистрации заблокированного устройства {device_id}"
                )
                return False

            # Создаем профиль устройства
            device_profile = DeviceProfile(
                device_id=device_id,
                device_name=device_name,
                device_type=device_type,
                user_id=user_id,
                family_id=family_id,
                mac_address=mac_address,
                ip_address=ip_address,
                os_version=os_version,
                app_version=app_version,
                trust_score=0.5,  # Начальный уровень доверия
            )

            self.device_profiles[device_id] = device_profile

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="device_registered",
                severity=IncidentSeverity.LOW,
                description=f"Зарегистрировано устройство {device_name} ({device_id})",
                source="ZeroTrustService",
            )
            self.activity_log.append(event)

            self.logger.info(
                f"Зарегистрировано устройство {device_name} ({device_id})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка регистрации устройства: {e}")
            return False

    def update_device_trust(
        self, device_id: str, trust_score: float, reason: str
    ) -> bool:
        """
        Обновление уровня доверия устройства
        Args:
            device_id: ID устройства
            trust_score: Новый уровень доверия (0.0-1.0)
            reason: Причина изменения
        Returns:
            bool: True если обновление успешно
        """
        try:
            if device_id not in self.device_profiles:
                self.logger.warning(f"Устройство {device_id} не найдено")
                return False

            device = self.device_profiles[device_id]
            old_trust = device.trust_score
            device.trust_score = max(0.0, min(1.0, trust_score))
            device.is_trusted = (
                device.trust_score >= self.default_trust_threshold
            )
            device.last_seen = datetime.now()

            # Сохраняем историю изменений доверия
            self.trust_scores[f"{device_id}_{int(time.time())}"] = (
                device.trust_score
            )

            # Создаем событие безопасности
            severity = IncidentSeverity.LOW
            if abs(old_trust - device.trust_score) > 0.3:
                severity = IncidentSeverity.MEDIUM

            event = SecurityEvent(
                event_type="device_trust_updated",
                severity=severity,
                description=f"Изменен уровень доверия устройства {device_id}: {old_trust:.2f} -> {device.trust_score:.2f}. Причина: {reason}",
                source="ZeroTrustService",
            )
            self.activity_log.append(event)

            self.logger.info(
                f"Обновлен уровень доверия устройства {device_id}: {old_trust:.2f} -> {device.trust_score:.2f}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления доверия устройства: {e}")
            return False

    def evaluate_access_request(
        self,
        user_id: str,
        device_id: str,
        resource: str,
        action: str,
        context: Dict[str, Any],
    ) -> Tuple[AccessDecision, str, float]:
        """
        Оценка запроса на доступ
        Args:
            user_id: ID пользователя
            device_id: ID устройства
            resource: Ресурс
            action: Действие
            context: Контекст запроса
        Returns:
            Tuple[AccessDecision, str, float]: (решение, обоснование, риск)
        """
        try:
            # Создаем запрос на доступ
            request = AccessRequest(
                request_id=f"{user_id}_{device_id}_{int(time.time())}",
                user_id=user_id,
                device_id=device_id,
                resource=resource,
                action=action,
                context=context,
            )

            # Проверяем, зарегистрировано ли устройство
            if device_id not in self.device_profiles:
                self._log_suspicious_activity(
                    f"Попытка доступа с незарегистрированного устройства {device_id}",
                    IncidentSeverity.HIGH,
                )
                return (
                    AccessDecision.DENY,
                    "Устройство не зарегистрировано",
                    1.0,
                )

            device = self.device_profiles[device_id]

            # Проверяем, не заблокировано ли устройство
            if device_id in self.blocked_devices:
                self._log_suspicious_activity(
                    f"Попытка доступа с заблокированного устройства {device_id}",
                    IncidentSeverity.HIGH,
                )
                return AccessDecision.DENY, "Устройство заблокировано", 1.0

            # Проверяем уровень доверия устройства
            if device.trust_score < 0.3:
                self._log_suspicious_activity(
                    f"Попытка доступа с устройства с низким доверием {device_id}",
                    IncidentSeverity.MEDIUM,
                )
                return (
                    AccessDecision.DENY,
                    "Низкий уровень доверия устройства",
                    device.trust_score,
                )

            # Применяем политики доступа
            decision, reason, risk = self._apply_access_policies(
                request, device
            )

            # Сохраняем запрос в историю
            request.risk_score = risk
            self.access_history.append(request)

            # Обновляем уровень доверия на основе результата
            if decision == AccessDecision.DENY:
                self.update_device_trust(
                    device_id, device.trust_score - 0.1, "Отказ в доступе"
                )
            elif decision == AccessDecision.ALLOW:
                self.update_device_trust(
                    device_id, device.trust_score + 0.05, "Успешный доступ"
                )

            return decision, reason, risk

        except Exception as e:
            self.logger.error(f"Ошибка оценки запроса на доступ: {e}")
            return AccessDecision.DENY, f"Ошибка системы: {e}", 1.0

    def _apply_access_policies(
        self, request: AccessRequest, device: DeviceProfile
    ) -> Tuple[AccessDecision, str, float]:
        """Применение политик доступа"""
        try:
            # Определяем тип сети
            network_type = self._determine_network_type(
                request.context.get("ip_address", "")
            )
            request.network_type = network_type

            # Применяем политики в порядке приоритета
            for policy in self.access_policies.values():
                if not policy.is_active:
                    continue

                if self._matches_policy(request, device, policy):
                    # Вычисляем риск
                    risk = self._calculate_risk(request, device, policy)

                    # Принимаем решение
                    if risk > 0.8:
                        return (
                            AccessDecision.DENY,
                            f"Высокий риск: {policy.name}",
                            risk,
                        )
                    elif risk > 0.6:
                        return (
                            AccessDecision.CHALLENGE,
                            f"Требуется дополнительная аутентификация: {policy.name}",
                            risk,
                        )
                    elif risk > 0.4:
                        return (
                            AccessDecision.MONITOR,
                            f"Доступ с мониторингом: {policy.name}",
                            risk,
                        )
                    else:
                        return (
                            AccessDecision.ALLOW,
                            f"Доступ разрешен: {policy.name}",
                            risk,
                        )

            # Если политика не найдена, применяем политику по умолчанию
            return (
                AccessDecision.CHALLENGE,
                "Требуется дополнительная аутентификация",
                0.5,
            )

        except Exception as e:
            self.logger.error(f"Ошибка применения политик: {e}")
            return AccessDecision.DENY, f"Ошибка политик: {e}", 1.0

    def _matches_policy(
        self,
        request: AccessRequest,
        device: DeviceProfile,
        policy: AccessPolicy,
    ) -> bool:
        """Проверка соответствия запроса политике"""
        try:
            # Проверяем паттерн ресурса
            if not self._matches_pattern(
                request.resource, policy.resource_pattern
            ):
                return False

            # Проверяем условия пользователя
            if not self._check_user_conditions(
                request.user_id, policy.user_conditions
            ):
                return False

            # Проверяем условия устройства
            if not self._check_device_conditions(
                device, policy.device_conditions
            ):
                return False

            # Проверяем условия сети
            if not self._check_network_conditions(
                request.network_type, policy.network_conditions
            ):
                return False

            # Проверяем временные условия
            if not self._check_time_conditions(
                request.timestamp, policy.time_conditions
            ):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка проверки политики: {e}")
            return False

    def _matches_pattern(self, resource: str, pattern: str) -> bool:
        """Проверка соответствия ресурса паттерну"""
        if pattern == "*":
            return True

        # Простая проверка с подстановочными знаками
        import fnmatch

        return fnmatch.fnmatch(resource, pattern)

    def _check_user_conditions(
        self, user_id: str, conditions: Dict[str, Any]
    ) -> bool:
        """Проверка условий пользователя"""
        # Здесь можно добавить проверку роли пользователя, возраста и т.д.
        return True

    def _check_device_conditions(
        self, device: DeviceProfile, conditions: Dict[str, Any]
    ) -> bool:
        """Проверка условий устройства"""
        if "device_type" in conditions:
            allowed_types = conditions["device_type"]
            if isinstance(allowed_types, str):
                allowed_types = [allowed_types]
            if device.device_type.value not in allowed_types:
                return False

        return True

    def _check_network_conditions(
        self, network_type: NetworkType, conditions: Dict[str, Any]
    ) -> bool:
        """Проверка условий сети"""
        if "network_type" in conditions:
            allowed_networks = conditions["network_type"]
            if isinstance(allowed_networks, str):
                allowed_networks = [allowed_networks]
            if network_type.value not in allowed_networks:
                return False

        return True

    def _check_time_conditions(
        self, timestamp: datetime, conditions: Dict[str, Any]
    ) -> bool:
        """Проверка временных условий"""
        if "time_range" in conditions:
            time_range = conditions["time_range"]
            if "-" in time_range:
                start_time, end_time = time_range.split("-")
                current_time = timestamp.strftime("%H:%M")
                if not (start_time <= current_time <= end_time):
                    return False

        return True

    def _calculate_risk(
        self,
        request: AccessRequest,
        device: DeviceProfile,
        policy: AccessPolicy,
    ) -> float:
        """Вычисление уровня риска"""
        try:
            risk = 0.0

            # Базовый риск на основе уровня доверия устройства
            risk += (1.0 - device.trust_score) * 0.4

            # Риск на основе типа сети
            if request.network_type == NetworkType.PUBLIC:
                risk += 0.3
            elif request.network_type == NetworkType.UNKNOWN:
                risk += 0.2

            # Риск на основе времени
            hour = request.timestamp.hour
            if hour < 6 or hour > 23:
                risk += 0.2

            # Риск на основе типа устройства
            if device.device_type in [DeviceType.IOT, DeviceType.SMART_TV]:
                risk += 0.1

            # Риск на основе контекста
            if "suspicious_activity" in request.context:
                risk += 0.3

            return min(1.0, risk)

        except Exception as e:
            self.logger.error(f"Ошибка вычисления риска: {e}")
            return 1.0

    def _determine_network_type(self, ip_address: str) -> NetworkType:
        """Определение типа сети по IP адресу"""
        try:
            # Простая логика определения типа сети
            if (
                ip_address.startswith("192.168.")
                or ip_address.startswith("10.")
                or ip_address.startswith("172.")
            ):
                return NetworkType.HOME
            elif ip_address.startswith("203.") or ip_address.startswith(
                "8.8."
            ):
                return NetworkType.PUBLIC
            else:
                return NetworkType.UNKNOWN

        except Exception as e:
            self.logger.error(f"Ошибка определения типа сети: {e}")
            return NetworkType.UNKNOWN

    def block_device(self, device_id: str, reason: str) -> bool:
        """
        Блокировка устройства
        Args:
            device_id: ID устройства
            reason: Причина блокировки
        Returns:
            bool: True если устройство заблокировано
        """
        try:
            self.blocked_devices.add(device_id)

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="device_blocked",
                severity=IncidentSeverity.HIGH,
                description=f"Заблокировано устройство {device_id}. Причина: {reason}",
                source="ZeroTrustService",
            )
            self.activity_log.append(event)

            self.logger.warning(
                f"Заблокировано устройство {device_id}. Причина: {reason}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка блокировки устройства: {e}")
            return False

    def unblock_device(self, device_id: str, reason: str) -> bool:
        """
        Разблокировка устройства
        Args:
            device_id: ID устройства
            reason: Причина разблокировки
        Returns:
            bool: True если устройство разблокировано
        """
        try:
            if device_id in self.blocked_devices:
                self.blocked_devices.remove(device_id)

                # Создаем событие безопасности
                event = SecurityEvent(
                    event_type="device_unblocked",
                    severity=IncidentSeverity.MEDIUM,
                    description=f"Разблокировано устройство {device_id}. Причина: {reason}",
                    source="ZeroTrustService",
                )
                self.activity_log.append(event)

                self.logger.info(
                    f"Разблокировано устройство {device_id}. Причина: {reason}"
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Ошибка разблокировки устройства: {e}")
            return False

    def get_device_trust_report(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение отчета о доверии устройства
        Args:
            device_id: ID устройства
        Returns:
            Optional[Dict[str, Any]]: Отчет о доверии
        """
        try:
            if device_id not in self.device_profiles:
                return None

            device = self.device_profiles[device_id]

            # Получаем историю изменений доверия
            trust_history = []
            for key, score in self.trust_scores.items():
                if key.startswith(device_id):
                    timestamp = key.split("_")[-1]
                    trust_history.append(
                        {
                            "timestamp": datetime.fromtimestamp(
                                int(timestamp)
                            ),
                            "trust_score": score,
                        }
                    )

            # Получаем статистику доступа
            access_stats = self._get_device_access_stats(device_id)

            return {
                "device_id": device_id,
                "device_name": device.device_name,
                "device_type": device.device_type.value,
                "current_trust_score": device.trust_score,
                "is_trusted": device.is_trusted,
                "is_blocked": device_id in self.blocked_devices,
                "last_seen": device.last_seen,
                "trust_history": sorted(
                    trust_history, key=lambda x: x["timestamp"]
                ),
                "access_stats": access_stats,
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения отчета о доверии: {e}")
            return None

    def _get_device_access_stats(self, device_id: str) -> Dict[str, Any]:
        """Получение статистики доступа устройства"""
        try:
            device_requests = [
                req
                for req in self.access_history
                if req.device_id == device_id
            ]

            if not device_requests:
                return {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                }

            # Подсчитываем статистику (упрощенная версия)
            total_requests = len(device_requests)
            successful_requests = len(
                [req for req in device_requests if req.risk_score < 0.5]
            )
            failed_requests = total_requests - successful_requests

            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (
                    successful_requests / total_requests
                    if total_requests > 0
                    else 0
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статистики доступа: {e}")
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
            }

    def _log_suspicious_activity(
        self, description: str, severity: IncidentSeverity
    ) -> None:
        """Логирование подозрительной активности"""
        try:
            event = SecurityEvent(
                event_type="suspicious_activity",
                severity=severity,
                description=description,
                source="ZeroTrustService",
            )
            self.suspicious_activities.append(event)
            self.activity_log.append(event)

        except Exception as e:
            self.logger.error(
                f"Ошибка логирования подозрительной активности: {e}"
            )

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса Zero Trust Service
        Returns:
            Dict[str, Any]: Статус сервиса
        """
        try:
            # Получаем базовый статус
            base_status = super().get_status()

            # Добавляем специфичную информацию
            status = {
                **base_status,
                "total_devices": len(self.device_profiles),
                "trusted_devices": len(
                    [d for d in self.device_profiles.values() if d.is_trusted]
                ),
                "blocked_devices": len(self.blocked_devices),
                "total_policies": len(self.access_policies),
                "active_policies": len(
                    [p for p in self.access_policies.values() if p.is_active]
                ),
                "total_access_requests": len(self.access_history),
                "suspicious_activities": len(self.suspicious_activities),
                "average_trust_score": (
                    sum(d.trust_score for d in self.device_profiles.values())
                    / len(self.device_profiles)
                    if self.device_profiles
                    else 0
                ),
                "device_types": {
                    device_type.value: len(
                        [
                            d
                            for d in self.device_profiles.values()
                            if d.device_type == device_type
                        ]
                    )
                    for device_type in DeviceType
                },
            }

            return status

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

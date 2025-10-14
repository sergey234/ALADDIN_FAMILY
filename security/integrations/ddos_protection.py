#!/usr/bin/env python3
"""
🛡️ ALADDIN - DDoS Protection Integration
Интеграция для защиты от DDoS атак

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List


@dataclass
class DDoSAttackAnalysis:
    """Результат анализа DDoS атаки"""

    attack_id: str
    is_ddos: bool
    attack_type: str
    severity: str
    source_ips: List[str]
    requests_per_second: float
    attack_duration: int
    blocked_requests: int
    timestamp: datetime
    details: Dict[str, Any]


class DDoSProtection:
    """
    Система защиты от DDoS атак.
    Мониторит сетевой трафик и блокирует подозрительную активность.
    """

    def __init__(
        self, config_path: str = "config/ddos_protection_config.json"
    ):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Статистика
        self.total_requests_monitored = 0
        self.ddos_attacks_detected = 0
        self.blocked_requests = 0

        # Мониторинг трафика
        self.ip_request_counts = defaultdict(deque)
        self.ip_last_request = defaultdict(datetime.now)
        self.blocked_ips = set()

        # Пороги для детекции
        self.request_thresholds = self.load_ddos_thresholds()

    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию защиты от DDoS"""
        try:
            import json

            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию
            default_config = {
                "enabled": True,
                "strict_mode": True,
                "auto_block_attacks": True,
                "monitor_http": True,
                "monitor_https": True,
                "monitor_tcp": True,
                "monitor_udp": True,
                "protection_level": "maximum",
                "rate_limiting": True,
                "ip_whitelist": [],
                "ip_blacklist": [],
            }
            return default_config

    def setup_logger(self) -> logging.Logger:
        """Настройка логирования"""
        logger = logging.getLogger("ddos_protection")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_ddos_thresholds(self) -> Dict[str, Any]:
        """Загружает пороги для детекции DDoS атак"""
        return {
            "requests_per_minute": 1000,  # Максимум запросов в минуту от одного IP
            "requests_per_second": 50,  # Максимум запросов в секунду от одного IP
            "concurrent_connections": 100,  # Максимум одновременных соединений
            "bandwidth_threshold": 1000000,  # Порог по трафику (байт/сек)
            "attack_duration_threshold": 60,  # Минимальная длительность атаки (сек)
            "unique_ip_threshold": 1000,  # Порог уникальных IP для распределенной атаки
        }

    def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализирует HTTP запрос на предмет DDoS атаки.

        Args:
            request_data: Данные запроса

        Returns:
            Dict[str, Any]: Результат анализа
        """
        self.logger.info(
            f"Анализ запроса: {request_data.get('method', 'UNKNOWN')} {request_data.get('path', '/')}"
        )

        source_ip = request_data.get("source_ip", "unknown")
        user_agent = request_data.get("user_agent", "")
        request_time = datetime.now()

        # Проверка на заблокированные IP
        if source_ip in self.blocked_ips:
            return {
                "is_blocked": True,
                "reason": "ip_blocked",
                "source_ip": source_ip,
                "timestamp": request_time,
            }

        # Проверка whitelist
        if source_ip in self.config.get("ip_whitelist", []):
            return {
                "is_blocked": False,
                "reason": "whitelisted",
                "source_ip": source_ip,
                "timestamp": request_time,
            }

        # Обновление статистики запросов
        self.total_requests_monitored += 1
        self.ip_request_counts[source_ip].append(request_time)
        self.ip_last_request[source_ip] = request_time

        # Очистка старых запросов (старше 1 минуты)
        cutoff_time = request_time - timedelta(minutes=1)
        while (
            self.ip_request_counts[source_ip]
            and self.ip_request_counts[source_ip][0] < cutoff_time
        ):
            self.ip_request_counts[source_ip].popleft()

        # Подсчет запросов в последнюю минуту
        requests_last_minute = len(self.ip_request_counts[source_ip])

        # Проверка порогов
        is_suspicious = False
        suspicious_reasons = []

        if (
            requests_last_minute
            > self.request_thresholds["requests_per_minute"]
        ):
            is_suspicious = True
            suspicious_reasons.append("high_request_rate")

        # Проверка на подозрительный User-Agent
        if self.is_suspicious_user_agent(user_agent):
            is_suspicious = True
            suspicious_reasons.append("suspicious_user_agent")

        # Проверка на повторяющиеся запросы
        if self.is_repetitive_request(request_data):
            is_suspicious = True
            suspicious_reasons.append("repetitive_request")

        # Принятие решения о блокировке
        should_block = is_suspicious and self.config.get(
            "auto_block_attacks", True
        )

        if should_block:
            self.block_ip(source_ip)
            self.blocked_requests += 1

        result = {
            "is_blocked": should_block,
            "is_suspicious": is_suspicious,
            "reason": "suspicious_activity" if is_suspicious else "normal",
            "suspicious_reasons": suspicious_reasons,
            "requests_last_minute": requests_last_minute,
            "source_ip": source_ip,
            "timestamp": request_time,
        }

        self.logger.info(
            f"DDoS analysis: {source_ip}, blocked={should_block}, suspicious={is_suspicious}"
        )
        return result

    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Проверяет, является ли User-Agent подозрительным"""
        suspicious_patterns = [
            "bot",
            "crawler",
            "spider",
            "scraper",
            "python-requests",
            "curl",
            "wget",
            "masscan",
            "nmap",
            "sqlmap",
        ]

        user_agent_lower = user_agent.lower()
        return any(
            pattern in user_agent_lower for pattern in suspicious_patterns
        )

    def is_repetitive_request(self, request_data: Dict[str, Any]) -> bool:
        """Проверяет, является ли запрос повторяющимся"""
        # В реальной системе здесь была бы более сложная логика
        # для определения повторяющихся запросов
        return False

    def block_ip(self, ip_address: str, duration_minutes: int = 60):
        """Блокирует IP адрес на указанное время"""
        self.blocked_ips.add(ip_address)
        self.logger.warning(
            f"IP {ip_address} заблокирован на {duration_minutes} минут"
        )

        # Планируем разблокировку через указанное время
        asyncio.create_task(
            self.unblock_ip_after_delay(ip_address, duration_minutes)
        )

    async def unblock_ip_after_delay(
        self, ip_address: str, delay_minutes: int
    ):
        """Разблокирует IP адрес через указанное время"""
        await asyncio.sleep(delay_minutes * 60)
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            self.logger.info(f"IP {ip_address} разблокирован")

    async def detect_ddos_attack(
        self, traffic_data: List[Dict[str, Any]]
    ) -> DDoSAttackAnalysis:
        """
        Детектирует DDoS атаку на основе анализа трафика.

        Args:
            traffic_data: Данные о сетевом трафике

        Returns:
            DDoSAttackAnalysis: Результат анализа
        """
        self.logger.info(
            f"Детекция DDoS атаки на основе {len(traffic_data)} записей трафика"
        )

        attack_id = f"ddos_{datetime.now().timestamp()}"
        is_ddos = False
        attack_type = "none"
        severity = "low"
        source_ips = []
        requests_per_second = 0.0
        attack_duration = 0
        blocked_requests = 0

        # Анализ источника атак
        ip_counts = defaultdict(int)
        total_requests = len(traffic_data)

        for request in traffic_data:
            source_ip = request.get("source_ip", "unknown")
            ip_counts[source_ip] += 1

            # Анализ каждого запроса
            analysis = self.analyze_request(request)
            if analysis.get("is_blocked"):
                blocked_requests += 1

        # Определение типа атаки
        unique_ips = len(ip_counts)
        max_requests_from_single_ip = (
            max(ip_counts.values()) if ip_counts else 0
        )

        if unique_ips > self.request_thresholds["unique_ip_threshold"]:
            is_ddos = True
            attack_type = "distributed_ddos"
            severity = "high"
        elif (
            max_requests_from_single_ip
            > self.request_thresholds["requests_per_minute"]
        ):
            is_ddos = True
            attack_type = "volumetric_ddos"
            severity = "medium"
        elif total_requests > 10000:  # Большое количество запросов
            is_ddos = True
            attack_type = "application_layer_ddos"
            severity = "medium"

        # Расчет метрик
        source_ips = list(ip_counts.keys())
        if traffic_data:
            time_span = (
                max(
                    req.get("timestamp", datetime.now())
                    for req in traffic_data
                )
                - min(
                    req.get("timestamp", datetime.now())
                    for req in traffic_data
                )
            ).total_seconds()
            if time_span > 0:
                requests_per_second = total_requests / time_span
                attack_duration = int(time_span)

        # Обновление статистики
        if is_ddos:
            self.ddos_attacks_detected += 1

        analysis = DDoSAttackAnalysis(
            attack_id=attack_id,
            is_ddos=is_ddos,
            attack_type=attack_type,
            severity=severity,
            source_ips=source_ips,
            requests_per_second=requests_per_second,
            attack_duration=attack_duration,
            blocked_requests=blocked_requests,
            timestamp=datetime.now(),
            details={
                "total_requests": total_requests,
                "unique_source_ips": unique_ips,
                "max_requests_from_single_ip": max_requests_from_single_ip,
            },
        )

        self.logger.info(
            f"DDoS attack detection: {attack_id}, is_ddos={is_ddos}, type={attack_type}, severity={severity}"
        )
        return analysis

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику защиты от DDoS"""
        attack_detection_rate = (
            self.ddos_attacks_detected
            / max(self.total_requests_monitored, 1)
            * 100
        )
        block_rate = (
            self.blocked_requests / max(self.total_requests_monitored, 1) * 100
        )

        return {
            "total_requests_monitored": self.total_requests_monitored,
            "ddos_attacks_detected": self.ddos_attacks_detected,
            "blocked_requests": self.blocked_requests,
            "currently_blocked_ips": len(self.blocked_ips),
            "attack_detection_rate": attack_detection_rate,
            "block_rate": block_rate,
            "enabled": self.config.get("enabled", True),
            "protection_level": self.config.get("protection_level", "medium"),
            "thresholds": self.request_thresholds,
        }

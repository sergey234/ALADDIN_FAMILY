#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN VPN - DDoS Protection System
Система защиты от DDoS атак для VPN сервиса
"""

import ipaddress
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AttackPattern:
    """Паттерн атаки"""

    ip: str
    attack_type: str
    severity: int  # 1-10
    timestamp: datetime
    requests_count: int
    blocked: bool = False


@dataclass
class ProtectionRule:
    """Правило защиты"""

    name: str
    max_requests: int
    time_window: int  # секунды
    block_duration: int  # секунды
    enabled: bool = True


class ALADDINDDoSProtection:
    """Система защиты от DDoS атак ALADDIN VPN"""

    def __init__(self):
        self.attack_patterns: Dict[str, List[AttackPattern]] = defaultdict(
            list
        )
        self.blocked_ips: Dict[str, datetime] = {}
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        self.protection_rules: List[ProtectionRule] = []
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self.attack_threshold = 100  # запросов в минуту
        self.block_duration = 3600  # 1 час

        # Инициализация правил защиты
        self._initialize_protection_rules()

        # Запуск фоновых задач
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._monitor_attacks())

    def _initialize_protection_rules(self):
        """Инициализация правил защиты"""
        self.protection_rules = [
            ProtectionRule(
                name="Rate Limiting",
                max_requests=100,
                time_window=60,
                block_duration=300,
            ),
            ProtectionRule(
                name="Burst Protection",
                max_requests=20,
                time_window=10,
                block_duration=600,
            ),
            ProtectionRule(
                name="Suspicious Activity",
                max_requests=50,
                time_window=30,
                block_duration=1800,
            ),
            ProtectionRule(
                name="High Volume Attack",
                max_requests=500,
                time_window=60,
                block_duration=3600,
            ),
        ]

    def _check_ip_lists(self, ip: str) -> Tuple[Optional[bool], Optional[str]]:
        """Проверка IP в whitelist и blacklist"""
        if ip in self.whitelist:
            return True, "Whitelisted IP"
        if ip in self.blacklist:
            return False, "Blacklisted IP"
        return None, None

    def _check_temporary_block(self, ip: str) -> Tuple[Optional[bool], Optional[str]]:
        """Проверка временной блокировки IP"""
        if ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip]:
                return (
                    False,
                    f"Temporarily blocked until {self.blocked_ips[ip]}",
                )
            else:
                del self.blocked_ips[ip]
        return None, None

    def _update_request_count(self, ip: str) -> None:
        """Обновление счетчика запросов"""
        current_time = datetime.now()
        self.request_counts[ip].append(current_time)

        # Очистка старых запросов
        cutoff_time = current_time - timedelta(minutes=5)
        while (
            self.request_counts[ip]
            and self.request_counts[ip][0] < cutoff_time
        ):
            self.request_counts[ip].popleft()

    async def _check_protection_rules(self, ip: str) -> Tuple[bool, str]:
        """Проверка правил защиты"""
        for rule in self.protection_rules:
            if not rule.enabled:
                continue

            if self._check_rule_violation(ip, rule):
                await self._block_ip(ip, rule.name, rule.block_duration)
                return False, f"Blocked by {rule.name}"

        return True, "Rules check passed"

    async def check_request(self, ip: str, endpoint: str) -> Tuple[bool, str]:
        """
        Проверка запроса на DDoS атаку

        Args:
            ip: IP адрес клиента
            endpoint: Эндпоинт запроса

        Returns:
            Tuple[bool, str]: (разрешен, причина)
        """
        try:
            # Проверка IP списков
            result, reason = self._check_ip_lists(ip)
            if result is not None:
                return result, reason

            # Проверка временной блокировки
            result, reason = self._check_temporary_block(ip)
            if result is not None:
                return result, reason

            # Обновление счетчика запросов
            self._update_request_count(ip)

            # Проверка правил защиты
            allowed, reason = await self._check_protection_rules(ip)
            if not allowed:
                return allowed, reason

            # Дополнительные проверки
            if await self._detect_attack_pattern(ip):
                await self._block_ip(ip, "Attack Pattern", self.block_duration)
                return False, "Attack pattern detected"

            return True, "Request allowed"

        except Exception as e:
            logger.error(f"Ошибка проверки DDoS защиты: {e}")
            return True, "Error in protection check"

    def _check_rule_violation(self, ip: str, rule: ProtectionRule) -> bool:
        """Проверка нарушения правила"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=rule.time_window)

        # Подсчет запросов в окне времени
        recent_requests = [
            req_time
            for req_time in self.request_counts[ip]
            if req_time > cutoff_time
        ]

        return len(recent_requests) > rule.max_requests

    async def _detect_attack_pattern(self, ip: str) -> bool:
        """Детекция паттернов атак"""
        # Проверка на подозрительную активность
        recent_requests = list(self.request_counts[ip])
        if len(recent_requests) < 10:
            return False

        # Анализ интервалов между запросами
        intervals = []
        for i in range(1, len(recent_requests)):
            interval = (
                recent_requests[i] - recent_requests[i - 1]
            ).total_seconds()
            intervals.append(interval)

        # Проверка на бот-активность (слишком регулярные интервалы)
        if len(intervals) > 5:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(
                intervals
            )

            # Если интервалы слишком регулярные (низкая вариация)
            if variance < 0.1 and avg_interval < 1.0:
                return True

        # Проверка на burst атаку
        if len(recent_requests) > 50:
            return True

        return False

    async def _block_ip(self, ip: str, reason: str, duration: int):
        """Блокировка IP адреса"""
        block_until = datetime.now() + timedelta(seconds=duration)
        self.blocked_ips[ip] = block_until

        # Запись в лог атаки
        attack = AttackPattern(
            ip=ip,
            attack_type=reason,
            severity=8,
            timestamp=datetime.now(),
            requests_count=len(self.request_counts[ip]),
            blocked=True,
        )

        self.attack_patterns[ip].append(attack)

        logger.warning(f"IP {ip} заблокирован: {reason} до {block_until}")

    async def _cleanup_old_data(self):
        """Очистка старых данных"""
        while True:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=24)

                # Очистка старых паттернов атак
                for ip in list(self.attack_patterns.keys()):
                    self.attack_patterns[ip] = [
                        pattern
                        for pattern in self.attack_patterns[ip]
                        if pattern.timestamp > cutoff_time
                    ]
                    if not self.attack_patterns[ip]:
                        del self.attack_patterns[ip]

                # Очистка истекших блокировок
                expired_blocks = [
                    ip
                    for ip, block_time in self.blocked_ips.items()
                    if current_time > block_time
                ]
                for ip in expired_blocks:
                    del self.blocked_ips[ip]

                await asyncio.sleep(300)  # Каждые 5 минут

            except Exception as e:
                logger.error(f"Ошибка очистки данных: {e}")
                await asyncio.sleep(60)

    async def _monitor_attacks(self):
        """Мониторинг атак"""
        while True:
            try:
                current_time = datetime.now()

                # Анализ текущих атак
                active_attacks = len(self.blocked_ips)
                total_requests = sum(
                    len(requests) for requests in self.request_counts.values()
                )

                if active_attacks > 0:
                    logger.info(
                        f"Активных атак: {active_attacks}, Всего запросов: {total_requests}"
                    )

                # Автоматическое добавление в blacklist при повторных атаках
                for ip, patterns in self.attack_patterns.items():
                    recent_attacks = [
                        p
                        for p in patterns
                        if (current_time - p.timestamp).total_seconds() < 3600
                    ]

                    if len(recent_attacks) > 5:
                        self.blacklist.add(ip)
                        logger.warning(
                            f"IP {ip} добавлен в blacklist за повторные атаки"
                        )

                await asyncio.sleep(60)  # Каждую минуту

            except Exception as e:
                logger.error(f"Ошибка мониторинга атак: {e}")
                await asyncio.sleep(60)

    def add_to_whitelist(self, ip: str):
        """Добавление IP в whitelist"""
        self.whitelist.add(ip)
        logger.info(f"IP {ip} добавлен в whitelist")

    def add_to_blacklist(self, ip: str):
        """Добавление IP в blacklist"""
        self.blacklist.add(ip)
        logger.info(f"IP {ip} добавлен в blacklist")

    def get_protection_stats(self) -> Dict:
        """Получение статистики защиты"""
        return {
            "blocked_ips": len(self.blocked_ips),
            "whitelist_size": len(self.whitelist),
            "blacklist_size": len(self.blacklist),
            "active_requests": sum(
                len(requests) for requests in self.request_counts.values()
            ),
            "attack_patterns": len(self.attack_patterns),
            "protection_rules": len(
                [r for r in self.protection_rules if r.enabled]
            ),
        }

    def get_attack_logs(self, limit: int = 100) -> List[Dict]:
        """Получение логов атак"""
        all_attacks = []
        for ip, patterns in self.attack_patterns.items():
            for pattern in patterns:
                all_attacks.append(
                    {
                        "ip": pattern.ip,
                        "attack_type": pattern.attack_type,
                        "severity": pattern.severity,
                        "timestamp": pattern.timestamp.isoformat(),
                        "requests_count": pattern.requests_count,
                        "blocked": pattern.blocked,
                    }
                )

        # Сортировка по времени (новые сначала)
        all_attacks.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_attacks[:limit]


# Глобальный экземпляр защиты
ddos_protection = ALADDINDDoSProtection()


async def check_ddos_protection(ip: str, endpoint: str) -> Tuple[bool, str]:
    """Проверка DDoS защиты (удобная функция)"""
    return await ddos_protection.check_request(ip, endpoint)


if __name__ == "__main__":
    # Тестирование системы защиты
    async def test_ddos_protection():
        print("🧪 Тестирование DDoS защиты ALADDIN VPN...")

        # Тест нормального запроса
        allowed, reason = await check_ddos_protection(
            "192.168.1.100", "/api/status"
        )
        print(f"✅ Нормальный запрос: {allowed} - {reason}")

        # Тест атаки
        print("🔥 Симуляция DDoS атаки...")
        for i in range(150):  # Превышаем лимит
            allowed, reason = await check_ddos_protection(
                "192.168.1.200", "/api/connect"
            )
            if not allowed:
                print(f"🚫 IP заблокирован: {reason}")
                break

        # Статистика
        stats = ddos_protection.get_protection_stats()
        print(f"📊 Статистика защиты: {stats}")

        # Логи атак
        attacks = ddos_protection.get_attack_logs(5)
        print(f"🚨 Последние атаки: {len(attacks)}")
        for attack in attacks:
            print(
                f"   - {attack['ip']}: {attack['attack_type']} (severity: {attack['severity']})"
            )

    # Запуск тестов
    asyncio.run(test_ddos_protection())

"""
Split Tunneling для ALADDIN VPN
Позволяет направлять только определенный трафик через VPN
"""

import ipaddress
import json
import logging as std_logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import asyncio

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class RoutingRule(Enum):
    """Правила маршрутизации"""

    VPN_ONLY = "vpn_only"  # Только через VPN
    BYPASS_VPN = "bypass_vpn"  # Обход VPN
    SMART_ROUTING = "smart"  # Умная маршрутизация


class TrafficType(Enum):
    """Типы трафика"""

    WEB_BROWSING = "web"
    STREAMING = "streaming"
    GAMING = "gaming"
    WORK_APPS = "work"
    SOCIAL_MEDIA = "social"
    BANKING = "banking"
    TORRENT = "torrent"
    ALL = "all"


@dataclass
class SplitTunnelRule:
    """Правило split tunneling"""

    rule_id: str
    name: str
    description: str
    traffic_type: TrafficType
    routing_rule: RoutingRule
    domains: List[str]
    ip_ranges: List[str]
    ports: List[int]
    protocols: List[str]
    is_active: bool = True
    priority: int = 100
    created_at: float = 0.0


@dataclass
class TrafficStats:
    """Статистика трафика"""

    total_packets: int = 0
    vpn_packets: int = 0
    bypass_packets: int = 0
    bytes_through_vpn: int = 0
    bytes_bypassed: int = 0
    last_updated: float = 0.0


class ALADDINSplitTunneling:
    """Split Tunneling для ALADDIN VPN"""

    def __init__(self):
        self.rules: Dict[str, SplitTunnelRule] = {}
        self.traffic_stats = TrafficStats()
        self.is_enabled = False
        self.default_routing = RoutingRule.VPN_ONLY

        # Кэш для быстрого поиска правил
        self.domain_cache: Dict[str, str] = {}
        self.ip_cache: Dict[str, str] = {}

        # Создаем правила по умолчанию
        self._create_default_rules()

        logger.info("Split Tunneling инициализирован")

    def _create_default_rules(self):
        """Создание правил по умолчанию"""
        default_rules = [
            {
                "rule_id": "banking_bypass",
                "name": "Банковские приложения",
                "description": "Обход VPN для банковских приложений",
                "traffic_type": TrafficType.BANKING,
                "routing_rule": RoutingRule.BYPASS_VPN,
                "domains": [
                    "sberbank.ru",
                    "tinkoff.ru",
                    "vtb.ru",
                    "gazprombank.ru",
                    "alfabank.ru",
                    "raiffeisen.ru",
                    "rosbank.ru",
                ],
                "ip_ranges": [],
                "ports": [443, 80],
                "protocols": ["tcp", "https"],
            },
            {
                "rule_id": "streaming_vpn",
                "name": "Стриминговые сервисы",
                "description": "Через VPN для доступа к контенту",
                "traffic_type": TrafficType.STREAMING,
                "routing_rule": RoutingRule.VPN_ONLY,
                "domains": [
                    "netflix.com",
                    "youtube.com",
                    "twitch.tv",
                    "hulu.com",
                    "disney.com",
                    "hbo.com",
                    "amazon.com",
                ],
                "ip_ranges": [],
                "ports": [443, 80, 8080],
                "protocols": ["tcp", "https", "http"],
            },
            {
                "rule_id": "gaming_bypass",
                "name": "Игровой трафик",
                "description": "Обход VPN для игр (низкая задержка)",
                "traffic_type": TrafficType.GAMING,
                "routing_rule": RoutingRule.BYPASS_VPN,
                "domains": [
                    "steam.com",
                    "epicgames.com",
                    "battle.net",
                    "origin.com",
                    "uplay.com",
                    "gog.com",
                    "xbox.com",
                    "playstation.com",
                ],
                "ip_ranges": [],
                "ports": [80, 443, 27015, 27016, 27017, 27018, 27019, 27020],
                "protocols": ["tcp", "udp"],
            },
            {
                "rule_id": "work_apps_smart",
                "name": "Рабочие приложения",
                "description": "Умная маршрутизация для рабочих приложений",
                "traffic_type": TrafficType.WORK_APPS,
                "routing_rule": RoutingRule.SMART_ROUTING,
                "domains": [
                    "office.com",
                    "google.com",
                    "microsoft.com",
                    "slack.com",
                    "zoom.us",
                    "teams.microsoft.com",
                    "notion.so",
                ],
                "ip_ranges": [],
                "ports": [443, 80],
                "protocols": ["tcp", "https"],
            },
            {
                "rule_id": "social_media_vpn",
                "name": "Социальные сети",
                "description": "Через VPN для приватности",
                "traffic_type": TrafficType.SOCIAL_MEDIA,
                "routing_rule": RoutingRule.VPN_ONLY,
                "domains": [
                    "facebook.com",
                    "instagram.com",
                    "twitter.com",
                    "tiktok.com",
                    "linkedin.com",
                    "vk.com",
                    "ok.ru",
                    "telegram.org",
                ],
                "ip_ranges": [],
                "ports": [443, 80],
                "protocols": ["tcp", "https"],
            },
        ]

        for rule_data in default_rules:
            rule = SplitTunnelRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                traffic_type=TrafficType(rule_data["traffic_type"]),
                routing_rule=RoutingRule(rule_data["routing_rule"]),
                domains=rule_data["domains"],
                ip_ranges=rule_data["ip_ranges"],
                ports=rule_data["ports"],
                protocols=rule_data["protocols"],
                created_at=time.time(),
            )
            self.add_rule(rule)

    def add_rule(self, rule: SplitTunnelRule) -> bool:
        """Добавление правила split tunneling"""
        try:
            self.rules[rule.rule_id] = rule

            # Обновляем кэши
            self._update_domain_cache(rule)
            self._update_ip_cache(rule)

            logger.info(f"Правило {rule.name} добавлено")
            return True

        except Exception as e:
            logger.error(f"Ошибка добавления правила: {e}")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Удаление правила"""
        try:
            if rule_id in self.rules:
                rule = self.rules[rule_id]

                # Удаляем из кэшей
                self._remove_from_domain_cache(rule)
                self._remove_from_ip_cache(rule)

                del self.rules[rule_id]
                logger.info(f"Правило {rule_id} удалено")
                return True
            else:
                logger.warning(f"Правило {rule_id} не найдено")
                return False

        except Exception as e:
            logger.error(f"Ошибка удаления правила: {e}")
            return False

    def update_rule(self, rule_id: str, **kwargs) -> bool:
        """Обновление правила"""
        try:
            if rule_id in self.rules:
                rule = self.rules[rule_id]

                # Обновляем поля
                for key, value in kwargs.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)

                # Обновляем кэши
                self._update_domain_cache(rule)
                self._update_ip_cache(rule)

                logger.info(f"Правило {rule_id} обновлено")
                return True
            else:
                logger.warning(f"Правило {rule_id} не найдено")
                return False

        except Exception as e:
            logger.error(f"Ошибка обновления правила: {e}")
            return False

    def _update_domain_cache(self, rule: SplitTunnelRule):
        """Обновление кэша доменов"""
        try:
            for domain in rule.domains:
                self.domain_cache[domain.lower()] = rule.rule_id
        except Exception as e:
            logger.error(f"Ошибка обновления кэша доменов: {e}")

    def _update_ip_cache(self, rule: SplitTunnelRule):
        """Обновление кэша IP адресов"""
        try:
            for ip_range in rule.ip_ranges:
                self.ip_cache[ip_range] = rule.rule_id
        except Exception as e:
            logger.error(f"Ошибка обновления кэша IP: {e}")

    def _remove_from_domain_cache(self, rule: SplitTunnelRule):
        """Удаление из кэша доменов"""
        try:
            for domain in rule.domains:
                if domain.lower() in self.domain_cache:
                    del self.domain_cache[domain.lower()]
        except Exception as e:
            logger.error(f"Ошибка удаления из кэша доменов: {e}")

    def _remove_from_ip_cache(self, rule: SplitTunnelRule):
        """Удаление из кэша IP адресов"""
        try:
            for ip_range in rule.ip_ranges:
                if ip_range in self.ip_cache:
                    del self.ip_cache[ip_range]
        except Exception as e:
            logger.error(f"Ошибка удаления из кэша IP: {e}")

    def _check_domain_rule(self, domain: str) -> Tuple[Optional[RoutingRule], Optional[str]]:
        """Проверка правила для домена"""
        domain_lower = domain.lower()
        if domain_lower in self.domain_cache:
            rule_id = self.domain_cache[domain_lower]
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                if rule.is_active:
                    return rule.routing_rule, rule_id
        return None, None

    def _check_ip_rule(self, ip_address: str) -> Tuple[Optional[RoutingRule], Optional[str]]:
        """Проверка правила для IP адреса"""
        for ip_range, rule_id in self.ip_cache.items():
            if self._ip_in_range(ip_address, ip_range):
                if rule_id in self.rules:
                    rule = self.rules[rule_id]
                    if rule.is_active:
                        return rule.routing_rule, rule_id
        return None, None

    def _check_port_protocol_rule(
        self, port: int, protocol: str
    ) -> Tuple[Optional[RoutingRule], Optional[str]]:
        """Проверка правила для порта и протокола"""
        for rule in self.rules.values():
            if (
                rule.is_active
                and port in rule.ports
                and protocol.lower() in [p.lower() for p in rule.protocols]
            ):
                return rule.routing_rule, rule.rule_id
        return None, None

    def get_routing_decision(
        self,
        domain: Optional[str] = None,
        ip_address: Optional[str] = None,
        port: Optional[int] = None,
        protocol: Optional[str] = None,
    ) -> Tuple[RoutingRule, Optional[str]]:
        """Получение решения о маршрутизации для трафика"""
        try:
            # Проверяем домен
            if domain:
                rule, rule_id = self._check_domain_rule(domain)
                if rule is not None:
                    return rule, rule_id

            # Проверяем IP адрес
            if ip_address:
                rule, rule_id = self._check_ip_rule(ip_address)
                if rule is not None:
                    return rule, rule_id

            # Проверяем порт и протокол
            if port and protocol:
                rule, rule_id = self._check_port_protocol_rule(port, protocol)
                if rule is not None:
                    return rule, rule_id

            # Возвращаем правило по умолчанию
            return self.default_routing, None

        except Exception as e:
            logger.error(f"Ошибка получения решения о маршрутизации: {e}")
            return self.default_routing, None

    def _ip_in_range(self, ip: str, ip_range: str) -> bool:
        """Проверка, входит ли IP в диапазон"""
        try:
            if "/" in ip_range:
                # CIDR нотация
                network = ipaddress.ip_network(ip_range, strict=False)
                return ipaddress.ip_address(ip) in network
            else:
                # Точный IP
                return ip == ip_range
        except Exception as e:
            logger.error(f"Ошибка проверки IP диапазона: {e}")
            return False

    def process_traffic(
        self,
        domain: Optional[str] = None,
        ip_address: Optional[str] = None,
        port: Optional[int] = None,
        protocol: Optional[str] = None,
        packet_size: int = 0,
    ) -> bool:
        """Обработка трафика через split tunneling"""
        try:
            routing_rule, rule_id = self.get_routing_decision(
                domain, ip_address, port, protocol
            )

            # Обновляем статистику
            self.traffic_stats.total_packets += 1
            self.traffic_stats.last_updated = time.time()

            if routing_rule == RoutingRule.VPN_ONLY:
                self.traffic_stats.vpn_packets += 1
                self.traffic_stats.bytes_through_vpn += packet_size
                logger.debug(
                    f"Трафик {domain or ip_address} направлен через VPN"
                )
                return True
            elif routing_rule == RoutingRule.BYPASS_VPN:
                self.traffic_stats.bypass_packets += 1
                self.traffic_stats.bytes_bypassed += packet_size
                logger.debug(f"Трафик {domain or ip_address} обходит VPN")
                return False
            else:  # SMART_ROUTING
                # Умная маршрутизация (можно расширить логику)
                if self._should_use_vpn_for_smart_routing(domain, ip_address):
                    self.traffic_stats.vpn_packets += 1
                    self.traffic_stats.bytes_through_vpn += packet_size
                    logger.debug(
                        f"Умная маршрутизация: трафик {domain or ip_address} через VPN"
                    )
                    return True
                else:
                    self.traffic_stats.bypass_packets += 1
                    self.traffic_stats.bytes_bypassed += packet_size
                    logger.debug(
                        f"Умная маршрутизация: трафик {domain or ip_address} обходит VPN"
                    )
                    return False

        except Exception as e:
            logger.error(f"Ошибка обработки трафика: {e}")
            return False

    def _should_use_vpn_for_smart_routing(
        self, domain: Optional[str], ip: Optional[str]
    ) -> bool:
        """Определение использования VPN для умной маршрутизации"""
        try:
            # Простая логика (можно расширить)
            if domain:
                # Проверяем, является ли домен "приватным"
                private_domains = ["office.com", "internal.company.com"]
                if any(priv in domain.lower() for priv in private_domains):
                    return False  # Не через VPN для внутренних доменов

            # По умолчанию через VPN для умной маршрутизации
            return True

        except Exception as e:
            logger.error(f"Ошибка умной маршрутизации: {e}")
            return True

    def enable_split_tunneling(self):
        """Включение split tunneling"""
        self.is_enabled = True
        logger.info("Split Tunneling включен")

    def disable_split_tunneling(self):
        """Отключение split tunneling"""
        self.is_enabled = False
        logger.info("Split Tunneling отключен")

    def set_default_routing(self, routing: RoutingRule):
        """Установка маршрутизации по умолчанию"""
        self.default_routing = routing
        logger.info(f"Маршрутизация по умолчанию установлена: {routing.value}")

    def get_traffic_stats(self) -> Dict[str, Any]:
        """Получение статистики трафика"""
        try:
            total_bytes = (
                self.traffic_stats.bytes_through_vpn
                + self.traffic_stats.bytes_bypassed
            )

            return {
                "total_packets": self.traffic_stats.total_packets,
                "vpn_packets": self.traffic_stats.vpn_packets,
                "bypass_packets": self.traffic_stats.bypass_packets,
                "bytes_through_vpn": self.traffic_stats.bytes_through_vpn,
                "bytes_bypassed": self.traffic_stats.bytes_bypassed,
                "total_bytes": total_bytes,
                "vpn_percentage": (
                    (self.traffic_stats.bytes_through_vpn / total_bytes * 100)
                    if total_bytes > 0
                    else 0
                ),
                "bypass_percentage": (
                    (self.traffic_stats.bytes_bypassed / total_bytes * 100)
                    if total_bytes > 0
                    else 0
                ),
                "last_updated": self.traffic_stats.last_updated,
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики трафика: {e}")
            return {}

    def get_rules_summary(self) -> Dict[str, Any]:
        """Получение сводки правил"""
        try:
            active_rules = [
                rule for rule in self.rules.values() if rule.is_active
            ]

            return {
                "total_rules": len(self.rules),
                "active_rules": len(active_rules),
                "rules_by_type": {
                    traffic_type.value: len(
                        [
                            r
                            for r in active_rules
                            if r.traffic_type == traffic_type
                        ]
                    )
                    for traffic_type in TrafficType
                },
                "rules_by_routing": {
                    routing.value: len(
                        [r for r in active_rules if r.routing_rule == routing]
                    )
                    for routing in RoutingRule
                },
                "is_enabled": self.is_enabled,
                "default_routing": self.default_routing.value,
            }
        except Exception as e:
            logger.error(f"Ошибка получения сводки правил: {e}")
            return {}

    def export_rules(self, filepath: str) -> bool:
        """Экспорт правил в файл"""
        try:
            rules_data = []
            for rule in self.rules.values():
                rules_data.append(
                    {
                        "rule_id": rule.rule_id,
                        "name": rule.name,
                        "description": rule.description,
                        "traffic_type": rule.traffic_type.value,
                        "routing_rule": rule.routing_rule.value,
                        "domains": rule.domains,
                        "ip_ranges": rule.ip_ranges,
                        "ports": rule.ports,
                        "protocols": rule.protocols,
                        "is_active": rule.is_active,
                        "priority": rule.priority,
                        "created_at": rule.created_at,
                    }
                )

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Правила экспортированы в {filepath}")
            return True

        except Exception as e:
            logger.error(f"Ошибка экспорта правил: {e}")
            return False

    def import_rules(self, filepath: str) -> bool:
        """Импорт правил из файла"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                rules_data = json.load(f)

            imported_count = 0
            for rule_data in rules_data:
                rule = SplitTunnelRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    traffic_type=TrafficType(rule_data["traffic_type"]),
                    routing_rule=RoutingRule(rule_data["routing_rule"]),
                    domains=rule_data["domains"],
                    ip_ranges=rule_data["ip_ranges"],
                    ports=rule_data["ports"],
                    protocols=rule_data["protocols"],
                    is_active=rule_data["is_active"],
                    priority=rule_data["priority"],
                    created_at=rule_data["created_at"],
                )

                if self.add_rule(rule):
                    imported_count += 1

            logger.info(f"Импортировано {imported_count} правил из {filepath}")
            return True

        except Exception as e:
            logger.error(f"Ошибка импорта правил: {e}")
            return False


# Пример использования
def main():
    """Основная функция для тестирования"""
    split_tunnel = ALADDINSplitTunneling()

    print("=== SPLIT TUNNELING ALADDIN VPN ===")

    # Включаем split tunneling
    split_tunnel.enable_split_tunneling()
    print("✅ Split Tunneling включен")

    # Тестируем различные домены
    test_domains = [
        "sberbank.ru",  # Банковский - должен обходить VPN
        "netflix.com",  # Стриминг - должен идти через VPN
        "steam.com",  # Игры - должен обходить VPN
        "facebook.com",  # Социальные сети - должен идти через VPN
        "google.com",  # По умолчанию - зависит от настройки
    ]

    print("\n🧪 Тестирование маршрутизации:")
    for domain in test_domains:
        routing, rule_id = split_tunnel.get_routing_decision(domain=domain)
        rule_name = (
            split_tunnel.rules[rule_id].name if rule_id else "По умолчанию"
        )
        print(f"  {domain}: {routing.value} ({rule_name})")

    # Тестируем обработку трафика
    print("\n📊 Тестирование обработки трафика:")
    for domain in test_domains[:3]:
        use_vpn = split_tunnel.process_traffic(
            domain=domain, port=443, protocol="https", packet_size=1024
        )
        print(f"  {domain}: {'VPN' if use_vpn else 'Bypass'}")

    # Получаем статистику
    stats = split_tunnel.get_traffic_stats()
    print("\n📈 Статистика трафика:")
    print(f"  Всего пакетов: {stats['total_packets']}")
    print(
        f"  Через VPN: {stats['vpn_packets']} ({stats['vpn_percentage']:.1f}%)"
    )
    print(
        f"  Обход VPN: {stats['bypass_packets']} ({stats['bypass_percentage']:.1f}%)"
    )

    # Получаем сводку правил
    summary = split_tunnel.get_rules_summary()
    print("\n📋 Сводка правил:")
    print(f"  Всего правил: {summary['total_rules']}")
    print(f"  Активных: {summary['active_rules']}")
    print(f"  Включен: {summary['is_enabled']}")
    print(f"  По умолчанию: {summary['default_routing']}")


if __name__ == "__main__":
    main()

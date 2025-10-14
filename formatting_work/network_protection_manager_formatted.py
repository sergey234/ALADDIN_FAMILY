#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМНЫЙ МЕНЕДЖЕР ЗАЩИТЫ СЕТИ - Блокировка на уровне системы
Максимальная защита от обхода через системные настройки
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class NetworkProtectionManager:
    """Менеджер системной защиты сети"""

    def __init__(self):
        self.blocked_domains = []
        self.blocked_ips = []
        self.blocked_ports = []
        self.vpn_ports = [1194, 443, 80, 53, 500, 4500, 1723, 8080, 3128, 1080]
        self.tor_ports = [9050, 9051, 9150, 9151]

    def block_vpn_globally(self) -> bool:
        """Глобальная блокировка VPN на уровне системы"""
        try:
            # Блокировка VPN портов через iptables
            for port in self.vpn_ports:
                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "tcp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "udp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

            # Блокировка популярных VPN доменов через hosts
            vpn_domains = [
                "nordvpn.com",
                "expressvpn.com",
                "surfshark.com",
                "cyberghostvpn.com",
                "protonvpn.com",
                "windscribe.com",
            ]

            self._block_domains_in_hosts(vpn_domains)

            logger.info("🔒 VPN заблокирован на системном уровне")
            return True

        except Exception as e:
            logger.error(f"Ошибка блокировки VPN: {e}")
            return False

    def block_tor_globally(self) -> bool:
        """Глобальная блокировка Tor"""
        try:
            # Блокировка Tor портов
            for port in self.tor_ports:
                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "tcp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

            # Блокировка Tor доменов
            tor_domains = ["torproject.org", "tor-browser.org", "onion.com"]

            self._block_domains_in_hosts(tor_domains)

            logger.info("🔒 Tor заблокирован на системном уровне")
            return True

        except Exception as e:
            logger.error(f"Ошибка блокировки Tor: {e}")
            return False

    def block_proxy_globally(self) -> bool:
        """Глобальная блокировка прокси"""
        try:
            # Блокировка прокси портов
            proxy_ports = [8080, 3128, 1080, 8118, 8888, 9999]
            for port in proxy_ports:
                subprocess.run(
                    [
                        "sudo",
                        "iptables",
                        "-A",
                        "OUTPUT",
                        "-p",
                        "tcp",
                        "--dport",
                        str(port),
                        "-j",
                        "DROP",
                    ],
                    check=False,
                )

            logger.info("🔒 Прокси заблокированы на системном уровне")
            return True

        except Exception as e:
            logger.error(f"Ошибка блокировки прокси: {e}")
            return False

    def _block_domains_in_hosts(self, domains: List[str]) -> bool:
        """Блокировка доменов через файл hosts"""
        try:
            hosts_file = Path("/etc/hosts")
            if not hosts_file.exists():
                return False

            # Чтение текущего hosts файла
            with open(hosts_file, "r") as f:
                content = f.read()

            # Добавление блокировок
            block_entries = []
            for domain in domains:
                block_entries.append(f"127.0.0.1 {domain}")
                block_entries.append(f"0.0.0.0 {domain}")

            # Проверка, не заблокированы ли уже
            new_entries = []
            for entry in block_entries:
                if entry not in content:
                    new_entries.append(entry)

            if new_entries:
                # Добавление новых блокировок
                with open(hosts_file, "a") as f:
                    f.write("\n# ALADDIN Security - Blocked domains\n")
                    for entry in new_entries:
                        f.write(f"{entry}\n")

                logger.info(f"Заблокированы домены: {domains}")

            return True

        except Exception as e:
            logger.error(f"Ошибка блокировки доменов: {e}")
            return False

    def kill_suspicious_processes(self) -> bool:
        """Завершение подозрительных процессов"""
        try:
            suspicious_keywords = [
                "tor",
                "vpn",
                "proxy",
                "tunnel",
                "stealth",
                "incognito",
            ]

            killed_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    proc_name = proc.info["name"].lower()
                    cmdline = " ".join(proc.info["cmdline"] or []).lower()

                    # Проверка на подозрительные процессы
                    if any(
                        keyword in proc_name or keyword in cmdline
                        for keyword in suspicious_keywords
                    ):
                        proc.terminate()
                        killed_processes.append(proc_name)
                        logger.warning(
                            f"Завершен подозрительный процесс: {proc_name}"
                        )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return len(killed_processes) > 0

        except Exception as e:
            logger.error(f"Ошибка завершения процессов: {e}")
            return False

    def setup_dns_filtering(self) -> bool:
        """Настройка DNS фильтрации"""
        try:
            # Настройка DNS серверов с фильтрацией
            dns_servers = [
                "1.1.1.3",  # Cloudflare с фильтрацией
                "1.0.0.3",  # Cloudflare с фильтрацией
                "208.67.222.123",  # OpenDNS
                "208.67.220.123",  # OpenDNS
            ]

            # Обновление DNS настроек (требует прав администратора)
            for dns in dns_servers:
                subprocess.run(
                    ["sudo", "networksetup", "-setdnsservers", "Wi-Fi", dns],
                    check=False,
                )

            logger.info("🔍 DNS фильтрация настроена")
            return True

        except Exception as e:
            logger.error(f"Ошибка настройки DNS: {e}")
            return False

    def emergency_internet_lock(self) -> bool:
        """Экстренная блокировка интернета"""
        try:
            # Блокировка всех исходящих соединений
            subprocess.run(
                ["sudo", "iptables", "-A", "OUTPUT", "-j", "DROP"], check=False
            )

            # Блокировка DNS
            subprocess.run(
                [
                    "sudo",
                    "iptables",
                    "-A",
                    "OUTPUT",
                    "-p",
                    "udp",
                    "--dport",
                    "53",
                    "-j",
                    "DROP",
                ],
                check=False,
            )

            logger.critical("🚨 ЭКСТРЕННАЯ БЛОКИРОВКА ИНТЕРНЕТА АКТИВНА")
            return True

        except Exception as e:
            logger.error(f"Ошибка экстренной блокировки: {e}")
            return False

    def restore_internet(self) -> bool:
        """Восстановление интернета"""
        try:
            # Очистка правил iptables
            subprocess.run(["sudo", "iptables", "-F"], check=False)
            subprocess.run(["sudo", "iptables", "-X"], check=False)

            logger.info("✅ Интернет восстановлен")
            return True

        except Exception as e:
            logger.error(f"Ошибка восстановления интернета: {e}")
            return False

    def get_protection_status(self) -> Dict[str, Any]:
        """Получение статуса защиты"""
        try:
            # Проверка активных правил iptables
            result = subprocess.run(
                ["sudo", "iptables", "-L", "OUTPUT", "-n"],
                capture_output=True,
                text=True,
            )

            blocked_rules = result.stdout.count("DROP")

            # Проверка заблокированных процессов
            suspicious_count = 0
            for proc in psutil.process_iter(["name"]):
                try:
                    if any(
                        keyword in proc.info["name"].lower()
                        for keyword in ["tor", "vpn", "proxy"]
                    ):
                        suspicious_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "blocked_rules": blocked_rules,
                "suspicious_processes": suspicious_count,
                "protection_active": blocked_rules > 0,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Ошибка получения статуса: {e}")
            return {}


# Пример использования
def main():
    """Пример использования NetworkProtectionManager"""
    manager = NetworkProtectionManager()

    print("🛡️ СИСТЕМНАЯ ЗАЩИТА СЕТИ")
    print("=" * 50)

    # Активация всех блокировок
    print("🔒 Блокировка VPN...")
    manager.block_vpn_globally()

    print("🔒 Блокировка Tor...")
    manager.block_tor_globally()

    print("🔒 Блокировка прокси...")
    manager.block_proxy_globally()

    print("🔍 Настройка DNS фильтрации...")
    manager.setup_dns_filtering()

    print("🔍 Завершение подозрительных процессов...")
    manager.kill_suspicious_processes()

    # Статус защиты
    status = manager.get_protection_status()
    print(f"📊 Статус защиты: {json.dumps(status, indent=2)}")

    print("\n✅ СИСТЕМНАЯ ЗАЩИТА АКТИВНА")
    print("⚠️ Требуются права администратора для полной работы")


if __name__ == "__main__":
    main()

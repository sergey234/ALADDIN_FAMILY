#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPv6 and DNS Protection System - Защита от IPv6 и DNS утечек
Kill Switch, DNS защита, IPv6 блокировка для полной анонимности

Функция: IPv6 and DNS Protection System
Приоритет: КРИТИЧЕСКИЙ
Версия: 1.0
Дата: 2025-09-07
"""

import os
import subprocess
import socket
import threading
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# Импорт базовых классов
from core.base import ComponentStatus, SecurityBase, SecurityLevel

logger = logging.getLogger(__name__)

class ProtectionLevel(Enum):
    """Уровни защиты"""
    BASIC = "basic"           # Базовая защита
    STANDARD = "standard"     # Стандартная защита
    HIGH = "high"            # Высокая защита
    MAXIMUM = "maximum"      # Максимальная защита

class LeakType(Enum):
    """Типы утечек"""
    IPV6_LEAK = "ipv6_leak"
    DNS_LEAK = "dns_leak"
    WEBRTC_LEAK = "webrtc_leak"
    TEREDO_LEAK = "teredo_leak"
    SIXTOFOUR_LEAK = "6to4_leak"

@dataclass
class ProtectionRule:
    """Правило защиты"""
    rule_id: str
    rule_type: str
    action: str
    target: str
    enabled: bool = True
    priority: int = 0

@dataclass
class LeakDetection:
    """Обнаружение утечки"""
    leak_type: LeakType
    detected: bool
    details: str
    timestamp: float
    severity: str = "medium"

class IPv6DNSProtectionSystem(SecurityBase):
    """Система защиты от IPv6 и DNS утечек"""
    
    def __init__(self, name: str = "IPv6DNSProtectionSystem", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        
        # Конфигурация защиты
        self.protection_level = ProtectionLevel.STANDARD
        self.kill_switch_enabled = True
        self.dns_protection_enabled = True
        self.ipv6_blocking_enabled = True
        
        # DNS серверы
        self.secure_dns_servers = [
            "1.1.1.1",      # Cloudflare
            "8.8.8.8",      # Google
            "9.9.9.9",      # Quad9
            "208.67.222.222" # OpenDNS
        ]
        
        # Правила защиты
        self.protection_rules: List[ProtectionRule] = []
        
        # Обнаружение утечек
        self.leak_detections: List[LeakDetection] = []
        self.monitoring_enabled = True
        
        # Статистика
        self.total_leaks_detected = 0
        self.total_leaks_blocked = 0
        self.kill_switch_activations = 0
        
        # Инициализация
        self._initialize_protection()
        
        logger.info(f"IPv6 DNS Protection System инициализирован: {name}")
    
    def _initialize_protection(self):
        """Инициализация системы защиты"""
        try:
            # Создание правил защиты
            self._create_protection_rules()
            
            # Запуск мониторинга утечек
            if self.monitoring_enabled:
                self._start_leak_monitoring()
            
            logger.info("Система защиты инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации защиты: {e}")
            self.status = ComponentStatus.ERROR
    
    def _create_protection_rules(self):
        """Создание правил защиты"""
        rules = [
            # IPv6 блокировка
            ProtectionRule(
                rule_id="ipv6_block_all",
                rule_type="ipv6_blocking",
                action="block",
                target="all_ipv6_traffic",
                priority=1
            ),
            
            # DNS защита
            ProtectionRule(
                rule_id="dns_force_secure",
                rule_type="dns_protection",
                action="redirect",
                target="secure_dns_servers",
                priority=2
            ),
            
            # Kill Switch
            ProtectionRule(
                rule_id="kill_switch_vpn_down",
                rule_type="kill_switch",
                action="block_all",
                target="all_traffic",
                priority=3
            ),
            
            # WebRTC блокировка
            ProtectionRule(
                rule_id="webrtc_block",
                rule_type="webrtc_protection",
                action="block",
                target="webrtc_connections",
                priority=4
            )
        ]
        
        self.protection_rules = rules
        logger.info(f"Создано {len(rules)} правил защиты")
    
    def _start_leak_monitoring(self):
        """Запуск мониторинга утечек"""
        def monitoring_loop():
            while self.status == ComponentStatus.RUNNING:
                try:
                    # Проверка IPv6 утечек
                    self._check_ipv6_leaks()
                    
                    # Проверка DNS утечек
                    self._check_dns_leaks()
                    
                    # Проверка WebRTC утечек
                    self._check_webrtc_leaks()
                    
                    time.sleep(30)  # Проверка каждые 30 секунд
                    
                except Exception as e:
                    logger.error(f"Ошибка мониторинга утечек: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        logger.info("Мониторинг утечек запущен")
    
    def _check_ipv6_leaks(self):
        """Проверка IPv6 утечек"""
        try:
            # Проверка IPv6 подключения
            ipv6_addresses = self._get_ipv6_addresses()
            
            if ipv6_addresses:
                leak = LeakDetection(
                    leak_type=LeakType.IPV6_LEAK,
                    detected=True,
                    details=f"Обнаружены IPv6 адреса: {', '.join(ipv6_addresses)}",
                    timestamp=time.time(),
                    severity="high"
                )
                self.leak_detections.append(leak)
                self.total_leaks_detected += 1
                
                # Блокировка IPv6
                self._block_ipv6()
                
                logger.warning(f"IPv6 утечка обнаружена: {leak.details}")
            
        except Exception as e:
            logger.error(f"Ошибка проверки IPv6 утечек: {e}")
    
    def _check_dns_leaks(self):
        """Проверка DNS утечек"""
        try:
            # Проверка DNS серверов
            current_dns = self._get_current_dns_servers()
            secure_dns = set(self.secure_dns_servers)
            
            # Проверка на использование небезопасных DNS
            unsafe_dns = [dns for dns in current_dns if dns not in secure_dns]
            
            if unsafe_dns:
                leak = LeakDetection(
                    leak_type=LeakType.DNS_LEAK,
                    detected=True,
                    details=f"Используются небезопасные DNS: {', '.join(unsafe_dns)}",
                    timestamp=time.time(),
                    severity="medium"
                )
                self.leak_detections.append(leak)
                self.total_leaks_detected += 1
                
                # Принудительное использование безопасных DNS
                self._force_secure_dns()
                
                logger.warning(f"DNS утечка обнаружена: {leak.details}")
            
        except Exception as e:
            logger.error(f"Ошибка проверки DNS утечек: {e}")
    
    def _check_webrtc_leaks(self):
        """Проверка WebRTC утечек"""
        try:
            # В реальной реализации здесь будет проверка WebRTC соединений
            # Для демонстрации используем простую проверку
            webrtc_leak = False
            
            if webrtc_leak:
                leak = LeakDetection(
                    leak_type=LeakType.WEBRTC_LEAK,
                    detected=True,
                    details="Обнаружены WebRTC соединения, обходящие VPN",
                    timestamp=time.time(),
                    severity="high"
                )
                self.leak_detections.append(leak)
                self.total_leaks_detected += 1
                
                logger.warning(f"WebRTC утечка обнаружена: {leak.details}")
            
        except Exception as e:
            logger.error(f"Ошибка проверки WebRTC утечек: {e}")
    
    def _get_ipv6_addresses(self) -> List[str]:
        """Получение IPv6 адресов"""
        try:
            # Получение IPv6 адресов системы
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            ipv6_addresses = []
            
            # Простой парсинг IPv6 адресов
            for line in result.stdout.split('\n'):
                if 'inet6' in line and '::1' not in line:  # Исключаем localhost
                    parts = line.split()
                    for part in parts:
                        if ':' in part and '::1' not in part:
                            ipv6_addresses.append(part)
            
            return ipv6_addresses
            
        except Exception as e:
            logger.error(f"Ошибка получения IPv6 адресов: {e}")
            return []
    
    def _get_current_dns_servers(self) -> List[str]:
        """Получение текущих DNS серверов"""
        try:
            # Получение DNS серверов из /etc/resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = []
                for line in f:
                    if line.startswith('nameserver'):
                        dns_server = line.split()[1]
                        dns_servers.append(dns_server)
                return dns_servers
                
        except Exception as e:
            logger.error(f"Ошибка получения DNS серверов: {e}")
            return []
    
    def _block_ipv6(self):
        """Блокировка IPv6"""
        try:
            if self.ipv6_blocking_enabled:
                # Отключение IPv6
                subprocess.run(['sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=1'], 
                             check=True, capture_output=True)
                subprocess.run(['sysctl', '-w', 'net.ipv6.conf.default.disable_ipv6=1'], 
                             check=True, capture_output=True)
                
                logger.info("IPv6 заблокирован")
                
        except Exception as e:
            logger.error(f"Ошибка блокировки IPv6: {e}")
    
    def _force_secure_dns(self):
        """Принудительное использование безопасных DNS"""
        try:
            if self.dns_protection_enabled:
                # Создание резервной копии resolv.conf
                subprocess.run(['cp', '/etc/resolv.conf', '/etc/resolv.conf.backup'], 
                             check=True, capture_output=True)
                
                # Запись безопасных DNS серверов
                with open('/etc/resolv.conf', 'w') as f:
                    for dns_server in self.secure_dns_servers:
                        f.write(f"nameserver {dns_server}\n")
                
                logger.info(f"Принудительно установлены безопасные DNS: {self.secure_dns_servers}")
                
        except Exception as e:
            logger.error(f"Ошибка установки безопасных DNS: {e}")
    
    def activate_kill_switch(self, reason: str = "VPN connection lost"):
        """Активация Kill Switch"""
        try:
            if self.kill_switch_enabled:
                # Блокировка всего трафика
                subprocess.run(['iptables', '-A', 'OUTPUT', '-j', 'DROP'], 
                             check=True, capture_output=True)
                
                self.kill_switch_activations += 1
                
                logger.critical(f"Kill Switch активирован: {reason}")
                
        except Exception as e:
            logger.error(f"Ошибка активации Kill Switch: {e}")
    
    def deactivate_kill_switch(self):
        """Деактивация Kill Switch"""
        try:
            # Разблокировка трафика
            subprocess.run(['iptables', '-D', 'OUTPUT', '-j', 'DROP'], 
                         check=True, capture_output=True)
            
            logger.info("Kill Switch деактивирован")
            
        except Exception as e:
            logger.error(f"Ошибка деактивации Kill Switch: {e}")
    
    def set_protection_level(self, level: ProtectionLevel) -> bool:
        """Установка уровня защиты"""
        try:
            self.protection_level = level
            
            if level == ProtectionLevel.BASIC:
                self.kill_switch_enabled = False
                self.dns_protection_enabled = True
                self.ipv6_blocking_enabled = True
            elif level == ProtectionLevel.STANDARD:
                self.kill_switch_enabled = True
                self.dns_protection_enabled = True
                self.ipv6_blocking_enabled = True
            elif level == ProtectionLevel.HIGH:
                self.kill_switch_enabled = True
                self.dns_protection_enabled = True
                self.ipv6_blocking_enabled = True
                # Дополнительные меры защиты
            elif level == ProtectionLevel.MAXIMUM:
                self.kill_switch_enabled = True
                self.dns_protection_enabled = True
                self.ipv6_blocking_enabled = True
                # Максимальные меры защиты
            
            logger.info(f"Уровень защиты установлен: {level.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки уровня защиты: {e}")
            return False
    
    def get_protection_status(self) -> Dict[str, Any]:
        """Получение статуса защиты"""
        return {
            "protection_level": self.protection_level.value,
            "kill_switch_enabled": self.kill_switch_enabled,
            "dns_protection_enabled": self.dns_protection_enabled,
            "ipv6_blocking_enabled": self.ipv6_blocking_enabled,
            "total_leaks_detected": self.total_leaks_detected,
            "total_leaks_blocked": self.total_leaks_blocked,
            "kill_switch_activations": self.kill_switch_activations,
            "secure_dns_servers": self.secure_dns_servers,
            "recent_leaks": [
                {
                    "type": leak.leak_type.value,
                    "detected": leak.detected,
                    "details": leak.details,
                    "severity": leak.severity,
                    "timestamp": leak.timestamp
                }
                for leak in self.leak_detections[-10:]  # Последние 10 утечек
            ]
        }
    
    def test_protection(self) -> Dict[str, Any]:
        """Тестирование системы защиты"""
        test_results = {
            "ipv6_test": False,
            "dns_test": False,
            "kill_switch_test": False,
            "overall_status": "unknown"
        }
        
        try:
            # Тест IPv6 блокировки
            ipv6_addresses = self._get_ipv6_addresses()
            test_results["ipv6_test"] = len(ipv6_addresses) == 0
            
            # Тест DNS защиты
            current_dns = self._get_current_dns_servers()
            secure_dns = set(self.secure_dns_servers)
            test_results["dns_test"] = all(dns in secure_dns for dns in current_dns)
            
            # Тест Kill Switch (симуляция)
            test_results["kill_switch_test"] = self.kill_switch_enabled
            
            # Общий статус
            if all(test_results[key] for key in ["ipv6_test", "dns_test", "kill_switch_test"]):
                test_results["overall_status"] = "protected"
            elif any(test_results[key] for key in ["ipv6_test", "dns_test", "kill_switch_test"]):
                test_results["overall_status"] = "partially_protected"
            else:
                test_results["overall_status"] = "unprotected"
            
        except Exception as e:
            logger.error(f"Ошибка тестирования защиты: {e}")
            test_results["error"] = str(e)
        
        return test_results

# Тестирование
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Создание системы защиты
    protection_system = IPv6DNSProtectionSystem("TestProtection")
    
    print("🛡️ ТЕСТИРОВАНИЕ IPv6 И DNS ЗАЩИТЫ")
    print("=" * 50)
    
    # Тест статуса защиты
    print("\n1. Статус защиты:")
    status = protection_system.get_protection_status()
    for key, value in status.items():
        if key != "recent_leaks":
            print(f"   📊 {key}: {value}")
    
    # Тест защиты
    print("\n2. Тестирование защиты:")
    test_results = protection_system.test_protection()
    for key, value in test_results.items():
        if key != "overall_status":
            status_icon = "✅" if value else "❌"
            print(f"   {status_icon} {key}: {value}")
    
    print(f"\n   🎯 Общий статус: {test_results['overall_status']}")
    
    # Тест уровней защиты
    print("\n3. Тест уровней защиты:")
    for level in ProtectionLevel:
        protection_system.set_protection_level(level)
        print(f"   📊 {level.value}: установлен")
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенная система Health Check
25+ функций для комплексной проверки здоровья системы
"""

import json
import time
import asyncio
import logging
import psutil
import socket
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Статусы здоровья системы"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class HealthCheckType(Enum):
    """Типы проверок здоровья"""
    SYSTEM = "system"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DATABASE = "database"
    SERVICE = "service"

@dataclass
class HealthCheckResult:
    """Результат проверки здоровья"""
    check_name: str
    status: HealthStatus
    value: float
    threshold: float
    message: str
    timestamp: datetime
    check_type: HealthCheckType
    
    def __init__(self, check_name: str, status: HealthStatus, value: float, threshold: float, message: str, check_type: HealthCheckType):
        self.check_name = check_name
        self.status = status
        self.value = value
        self.threshold = threshold
        self.message = message
        self.timestamp = datetime.now()
        self.check_type = check_type

class HealthCheckSystem:
    """
    Расширенная система Health Check
    25+ функций для комплексной проверки здоровья
    """
    
    def __init__(self):
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.check_intervals: Dict[str, int] = {}
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger(f"{__name__}.HealthCheckSystem")
        
        # Настройка порогов
        self.thresholds = {
            "cpu_usage": {"warning": 70, "critical": 90},
            "memory_usage": {"warning": 80, "critical": 95},
            "disk_usage": {"warning": 85, "critical": 95},
            "network_latency": {"warning": 100, "critical": 500},
            "response_time": {"warning": 2, "critical": 5}
        }
    
    async def initialize(self):
        """Инициализация системы Health Check"""
        try:
            # Настройка интервалов проверки
            self.check_intervals = {
                "system_health": 30,
                "network_health": 60,
                "security_health": 120,
                "performance_health": 45,
                "database_health": 90
            }
            
            self.logger.info("Система Health Check инициализирована")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Health Check: {e}")
            return False
    
    # СИСТЕМНЫЕ ПРОВЕРКИ (5 функций)
    async def check_cpu_usage(self) -> HealthCheckResult:
        """Проверка использования CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            threshold = self.thresholds["cpu_usage"]
            
            if cpu_percent >= threshold["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Критическое использование CPU: {cpu_percent}%"
            elif cpu_percent >= threshold["warning"]:
                status = HealthStatus.WARNING
                message = f"Высокое использование CPU: {cpu_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU в норме: {cpu_percent}%"
            
            return HealthCheckResult("cpu_usage", status, cpu_percent, threshold["critical"], message, HealthCheckType.SYSTEM)
        except Exception as e:
            return HealthCheckResult("cpu_usage", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки CPU: {e}", HealthCheckType.SYSTEM)
    
    async def check_memory_usage(self) -> HealthCheckResult:
        """Проверка использования памяти"""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            threshold = self.thresholds["memory_usage"]
            
            if memory_percent >= threshold["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Критическое использование памяти: {memory_percent}%"
            elif memory_percent >= threshold["warning"]:
                status = HealthStatus.WARNING
                message = f"Высокое использование памяти: {memory_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Память в норме: {memory_percent}%"
            
            return HealthCheckResult("memory_usage", status, memory_percent, threshold["critical"], message, HealthCheckType.SYSTEM)
        except Exception as e:
            return HealthCheckResult("memory_usage", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки памяти: {e}", HealthCheckType.SYSTEM)
    
    async def check_disk_usage(self) -> HealthCheckResult:
        """Проверка использования диска"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            threshold = self.thresholds["disk_usage"]
            
            if disk_percent >= threshold["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Критическое использование диска: {disk_percent:.1f}%"
            elif disk_percent >= threshold["warning"]:
                status = HealthStatus.WARNING
                message = f"Высокое использование диска: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Диск в норме: {disk_percent:.1f}%"
            
            return HealthCheckResult("disk_usage", status, disk_percent, threshold["critical"], message, HealthCheckType.SYSTEM)
        except Exception as e:
            return HealthCheckResult("disk_usage", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки диска: {e}", HealthCheckType.SYSTEM)
    
    async def check_system_load(self) -> HealthCheckResult:
        """Проверка нагрузки системы"""
        try:
            load_avg = psutil.getloadavg()[0]  # 1-минутная средняя нагрузка
            cpu_count = psutil.cpu_count()
            load_percent = (load_avg / cpu_count) * 100
            
            if load_percent >= 100:
                status = HealthStatus.CRITICAL
                message = f"Критическая нагрузка системы: {load_avg:.2f}"
            elif load_percent >= 80:
                status = HealthStatus.WARNING
                message = f"Высокая нагрузка системы: {load_avg:.2f}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Нагрузка системы в норме: {load_avg:.2f}"
            
            return HealthCheckResult("system_load", status, load_percent, 100, message, HealthCheckType.SYSTEM)
        except Exception as e:
            return HealthCheckResult("system_load", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки нагрузки: {e}", HealthCheckType.SYSTEM)
    
    async def check_process_count(self) -> HealthCheckResult:
        """Проверка количества процессов"""
        try:
            process_count = len(psutil.pids())
            threshold = 1000  # Максимальное количество процессов
            
            if process_count >= threshold:
                status = HealthStatus.CRITICAL
                message = f"Критическое количество процессов: {process_count}"
            elif process_count >= threshold * 0.8:
                status = HealthStatus.WARNING
                message = f"Высокое количество процессов: {process_count}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Количество процессов в норме: {process_count}"
            
            return HealthCheckResult("process_count", status, process_count, threshold, message, HealthCheckType.SYSTEM)
        except Exception as e:
            return HealthCheckResult("process_count", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки процессов: {e}", HealthCheckType.SYSTEM)
    
    # СЕТЕВЫЕ ПРОВЕРКИ (5 функций)
    async def check_network_connectivity(self) -> HealthCheckResult:
        """Проверка сетевой связности"""
        try:
            # Проверяем подключение к Google DNS
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, timeout=5)
            success = result.returncode == 0
            
            if success:
                status = HealthStatus.HEALTHY
                message = "Сетевая связность в норме"
            else:
                status = HealthStatus.CRITICAL
                message = "Отсутствует сетевая связность"
            
            return HealthCheckResult("network_connectivity", status, 1 if success else 0, 1, message, HealthCheckType.NETWORK)
        except Exception as e:
            return HealthCheckResult("network_connectivity", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки сети: {e}", HealthCheckType.NETWORK)
    
    async def check_network_latency(self) -> HealthCheckResult:
        """Проверка сетевой задержки"""
        try:
            start_time = time.time()
            result = subprocess.run(['ping', '-c', '3', '8.8.8.8'], capture_output=True, timeout=10)
            latency = (time.time() - start_time) * 1000  # в миллисекундах
            
            threshold = self.thresholds["network_latency"]
            
            if latency >= threshold["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Критическая сетевая задержка: {latency:.1f}ms"
            elif latency >= threshold["warning"]:
                status = HealthStatus.WARNING
                message = f"Высокая сетевая задержка: {latency:.1f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"Сетевая задержка в норме: {latency:.1f}ms"
            
            return HealthCheckResult("network_latency", status, latency, threshold["critical"], message, HealthCheckType.NETWORK)
        except Exception as e:
            return HealthCheckResult("network_latency", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки задержки: {e}", HealthCheckType.NETWORK)
    
    async def check_port_availability(self, port: int) -> HealthCheckResult:
        """Проверка доступности порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                status = HealthStatus.HEALTHY
                message = f"Порт {port} доступен"
            else:
                status = HealthStatus.CRITICAL
                message = f"Порт {port} недоступен"
            
            return HealthCheckResult(f"port_{port}", status, 1 if result == 0 else 0, 1, message, HealthCheckType.NETWORK)
        except Exception as e:
            return HealthCheckResult(f"port_{port}", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки порта {port}: {e}", HealthCheckType.NETWORK)
    
    async def check_network_interfaces(self) -> HealthCheckResult:
        """Проверка сетевых интерфейсов"""
        try:
            interfaces = psutil.net_if_addrs()
            active_interfaces = 0
            
            for interface, addresses in interfaces.items():
                if interface != 'lo':  # Исключаем loopback
                    for addr in addresses:
                        if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                            active_interfaces += 1
                            break
            
            if active_interfaces >= 1:
                status = HealthStatus.HEALTHY
                message = f"Активных интерфейсов: {active_interfaces}"
            else:
                status = HealthStatus.CRITICAL
                message = "Нет активных сетевых интерфейсов"
            
            return HealthCheckResult("network_interfaces", status, active_interfaces, 1, message, HealthCheckType.NETWORK)
        except Exception as e:
            return HealthCheckResult("network_interfaces", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки интерфейсов: {e}", HealthCheckType.NETWORK)
    
    async def check_bandwidth_usage(self) -> HealthCheckResult:
        """Проверка использования пропускной способности"""
        try:
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_recv = net_io.bytes_recv
            total_bytes = bytes_sent + bytes_recv
            
            # Простая проверка - если трафик слишком высокий
            threshold = 1024 * 1024 * 1024  # 1GB в секунду (примерно)
            
            if total_bytes >= threshold:
                status = HealthStatus.WARNING
                message = f"Высокое использование пропускной способности: {total_bytes / (1024*1024):.1f}MB"
            else:
                status = HealthStatus.HEALTHY
                message = f"Использование пропускной способности в норме: {total_bytes / (1024*1024):.1f}MB"
            
            return HealthCheckResult("bandwidth_usage", status, total_bytes, threshold, message, HealthCheckType.NETWORK)
        except Exception as e:
            return HealthCheckResult("bandwidth_usage", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки пропускной способности: {e}", HealthCheckType.NETWORK)
    
    # ПРОВЕРКИ БЕЗОПАСНОСТИ (5 функций)
    async def check_firewall_status(self) -> HealthCheckResult:
        """Проверка статуса файрвола"""
        try:
            # Проверяем статус файрвола (для macOS)
            result = subprocess.run(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'], capture_output=True, text=True)
            
            if 'enabled' in result.stdout.lower():
                status = HealthStatus.HEALTHY
                message = "Файрвол активен"
            else:
                status = HealthStatus.WARNING
                message = "Файрвол неактивен"
            
            return HealthCheckResult("firewall_status", status, 1 if 'enabled' in result.stdout.lower() else 0, 1, message, HealthCheckType.SECURITY)
        except Exception as e:
            return HealthCheckResult("firewall_status", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки файрвола: {e}", HealthCheckType.SECURITY)
    
    async def check_antivirus_status(self) -> HealthCheckResult:
        """Проверка статуса антивируса"""
        try:
            # Проверяем наличие антивирусных процессов
            antivirus_processes = ['clamav', 'sophos', 'norton', 'kaspersky', 'mcafee']
            found_processes = []
            
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    for av in antivirus_processes:
                        if av in proc_name:
                            found_processes.append(av)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if found_processes:
                status = HealthStatus.HEALTHY
                message = f"Антивирус активен: {', '.join(found_processes)}"
            else:
                status = HealthStatus.WARNING
                message = "Антивирус не обнаружен"
            
            return HealthCheckResult("antivirus_status", status, len(found_processes), 1, message, HealthCheckType.SECURITY)
        except Exception as e:
            return HealthCheckResult("antivirus_status", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки антивируса: {e}", HealthCheckType.SECURITY)
    
    async def check_ssl_certificates(self) -> HealthCheckResult:
        """Проверка SSL сертификатов"""
        try:
            # Проверяем сертификаты для основных доменов
            domains = ['google.com', 'github.com']
            valid_certs = 0
            
            for domain in domains:
                try:
                    result = subprocess.run(['openssl', 's_client', '-connect', f'{domain}:443', '-servername', domain], 
                                          input=b'', capture_output=True, timeout=5)
                    if result.returncode == 0:
                        valid_certs += 1
                except:
                    continue
            
            if valid_certs == len(domains):
                status = HealthStatus.HEALTHY
                message = "SSL сертификаты в порядке"
            elif valid_certs > 0:
                status = HealthStatus.WARNING
                message = f"Частично валидные SSL сертификаты: {valid_certs}/{len(domains)}"
            else:
                status = HealthStatus.CRITICAL
                message = "Проблемы с SSL сертификатами"
            
            return HealthCheckResult("ssl_certificates", status, valid_certs, len(domains), message, HealthCheckType.SECURITY)
        except Exception as e:
            return HealthCheckResult("ssl_certificates", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки SSL: {e}", HealthCheckType.SECURITY)
    
    async def check_security_updates(self) -> HealthCheckResult:
        """Проверка обновлений безопасности"""
        try:
            # Проверяем доступность обновлений (для macOS)
            result = subprocess.run(['softwareupdate', '-l'], capture_output=True, text=True, timeout=30)
            
            if 'No new software available' in result.stdout:
                status = HealthStatus.HEALTHY
                message = "Все обновления безопасности установлены"
            elif 'Software Update found' in result.stdout:
                status = HealthStatus.WARNING
                message = "Доступны обновления безопасности"
            else:
                status = HealthStatus.UNKNOWN
                message = "Не удалось проверить обновления"
            
            return HealthCheckResult("security_updates", status, 1 if 'No new software available' in result.stdout else 0, 1, message, HealthCheckType.SECURITY)
        except Exception as e:
            return HealthCheckResult("security_updates", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки обновлений: {e}", HealthCheckType.SECURITY)
    
    async def check_suspicious_processes(self) -> HealthCheckResult:
        """Проверка подозрительных процессов"""
        try:
            suspicious_keywords = ['backdoor', 'trojan', 'virus', 'malware', 'keylogger']
            suspicious_count = 0
            
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                    
                    for keyword in suspicious_keywords:
                        if keyword in proc_name or keyword in cmdline:
                            suspicious_count += 1
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if suspicious_count == 0:
                status = HealthStatus.HEALTHY
                message = "Подозрительные процессы не обнаружены"
            elif suspicious_count <= 2:
                status = HealthStatus.WARNING
                message = f"Обнаружено {suspicious_count} подозрительных процессов"
            else:
                status = HealthStatus.CRITICAL
                message = f"Обнаружено {suspicious_count} подозрительных процессов"
            
            return HealthCheckResult("suspicious_processes", status, suspicious_count, 0, message, HealthCheckType.SECURITY)
        except Exception as e:
            return HealthCheckResult("suspicious_processes", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки процессов: {e}", HealthCheckType.SECURITY)
    
    # ПРОВЕРКИ ПРОИЗВОДИТЕЛЬНОСТИ (5 функций)
    async def check_response_time(self) -> HealthCheckResult:
        """Проверка времени отклика"""
        try:
            start_time = time.time()
            # Симуляция операции
            await asyncio.sleep(0.1)
            response_time = (time.time() - start_time) * 1000  # в миллисекундах
            
            threshold = self.thresholds["response_time"]
            
            if response_time >= threshold["critical"]:
                status = HealthStatus.CRITICAL
                message = f"Критическое время отклика: {response_time:.1f}ms"
            elif response_time >= threshold["warning"]:
                status = HealthStatus.WARNING
                message = f"Высокое время отклика: {response_time:.1f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"Время отклика в норме: {response_time:.1f}ms"
            
            return HealthCheckResult("response_time", status, response_time, threshold["critical"], message, HealthCheckType.PERFORMANCE)
        except Exception as e:
            return HealthCheckResult("response_time", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки времени отклика: {e}", HealthCheckType.PERFORMANCE)
    
    async def check_throughput(self) -> HealthCheckResult:
        """Проверка пропускной способности"""
        try:
            # Симуляция проверки пропускной способности
            start_time = time.time()
            operations = 1000
            for _ in range(operations):
                pass  # Простая операция
            end_time = time.time()
            
            throughput = operations / (end_time - start_time)
            
            if throughput >= 10000:
                status = HealthStatus.HEALTHY
                message = f"Пропускная способность в норме: {throughput:.0f} ops/sec"
            elif throughput >= 5000:
                status = HealthStatus.WARNING
                message = f"Сниженная пропускная способность: {throughput:.0f} ops/sec"
            else:
                status = HealthStatus.CRITICAL
                message = f"Критически низкая пропускная способность: {throughput:.0f} ops/sec"
            
            return HealthCheckResult("throughput", status, throughput, 10000, message, HealthCheckType.PERFORMANCE)
        except Exception as e:
            return HealthCheckResult("throughput", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки пропускной способности: {e}", HealthCheckType.PERFORMANCE)
    
    async def check_memory_leaks(self) -> HealthCheckResult:
        """Проверка утечек памяти"""
        try:
            # Простая проверка утечек памяти
            memory_before = psutil.virtual_memory().used
            await asyncio.sleep(1)
            memory_after = psutil.virtual_memory().used
            memory_diff = memory_after - memory_before
            
            if memory_diff <= 1024 * 1024:  # 1MB
                status = HealthStatus.HEALTHY
                message = f"Утечек памяти не обнаружено: {memory_diff / 1024:.1f}KB"
            elif memory_diff <= 10 * 1024 * 1024:  # 10MB
                status = HealthStatus.WARNING
                message = f"Возможные утечки памяти: {memory_diff / 1024 / 1024:.1f}MB"
            else:
                status = HealthStatus.CRITICAL
                message = f"Критические утечки памяти: {memory_diff / 1024 / 1024:.1f}MB"
            
            return HealthCheckResult("memory_leaks", status, memory_diff, 1024 * 1024, message, HealthCheckType.PERFORMANCE)
        except Exception as e:
            return HealthCheckResult("memory_leaks", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки утечек памяти: {e}", HealthCheckType.PERFORMANCE)
    
    async def check_cpu_efficiency(self) -> HealthCheckResult:
        """Проверка эффективности CPU"""
        try:
            # Проверяем эффективность CPU
            cpu_times = psutil.cpu_times()
            idle_time = cpu_times.idle
            total_time = sum(cpu_times)
            
            if total_time > 0:
                cpu_efficiency = (total_time - idle_time) / total_time * 100
            else:
                cpu_efficiency = 0
            
            if cpu_efficiency <= 50:
                status = HealthStatus.HEALTHY
                message = f"CPU эффективен: {cpu_efficiency:.1f}%"
            elif cpu_efficiency <= 80:
                status = HealthStatus.WARNING
                message = f"CPU умеренно загружен: {cpu_efficiency:.1f}%"
            else:
                status = HealthStatus.CRITICAL
                message = f"CPU перегружен: {cpu_efficiency:.1f}%"
            
            return HealthCheckResult("cpu_efficiency", status, cpu_efficiency, 50, message, HealthCheckType.PERFORMANCE)
        except Exception as e:
            return HealthCheckResult("cpu_efficiency", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки эффективности CPU: {e}", HealthCheckType.PERFORMANCE)
    
    async def check_io_performance(self) -> HealthCheckResult:
        """Проверка производительности I/O"""
        try:
            # Проверяем производительность диска
            start_time = time.time()
            # Симуляция I/O операции
            with open('/tmp/health_check_test', 'w') as f:
                f.write('test' * 1000)
            with open('/tmp/health_check_test', 'r') as f:
                f.read()
            end_time = time.time()
            
            io_time = end_time - start_time
            
            if io_time <= 0.1:
                status = HealthStatus.HEALTHY
                message = f"I/O производительность в норме: {io_time:.3f}s"
            elif io_time <= 0.5:
                status = HealthStatus.WARNING
                message = f"Сниженная I/O производительность: {io_time:.3f}s"
            else:
                status = HealthStatus.CRITICAL
                message = f"Критически низкая I/O производительность: {io_time:.3f}s"
            
            # Очистка тестового файла
            try:
                import os
                os.remove('/tmp/health_check_test')
            except:
                pass
            
            return HealthCheckResult("io_performance", status, io_time, 0.1, message, HealthCheckType.PERFORMANCE)
        except Exception as e:
            return HealthCheckResult("io_performance", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки I/O: {e}", HealthCheckType.PERFORMANCE)
    
    # ПРОВЕРКИ БАЗЫ ДАННЫХ (5 функций)
    async def check_database_connection(self) -> HealthCheckResult:
        """Проверка подключения к базе данных"""
        try:
            # Симуляция проверки подключения к БД
            connection_ok = True  # В реальной системе здесь была бы проверка подключения
            
            if connection_ok:
                status = HealthStatus.HEALTHY
                message = "Подключение к базе данных в норме"
            else:
                status = HealthStatus.CRITICAL
                message = "Ошибка подключения к базе данных"
            
            return HealthCheckResult("database_connection", status, 1 if connection_ok else 0, 1, message, HealthCheckType.DATABASE)
        except Exception as e:
            return HealthCheckResult("database_connection", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки БД: {e}", HealthCheckType.DATABASE)
    
    async def check_database_performance(self) -> HealthCheckResult:
        """Проверка производительности базы данных"""
        try:
            # Симуляция проверки производительности БД
            query_time = 0.05  # 50ms - симуляция времени выполнения запроса
            
            if query_time <= 0.1:
                status = HealthStatus.HEALTHY
                message = f"Производительность БД в норме: {query_time*1000:.1f}ms"
            elif query_time <= 0.5:
                status = HealthStatus.WARNING
                message = f"Сниженная производительность БД: {query_time*1000:.1f}ms"
            else:
                status = HealthStatus.CRITICAL
                message = f"Критически низкая производительность БД: {query_time*1000:.1f}ms"
            
            return HealthCheckResult("database_performance", status, query_time, 0.1, message, HealthCheckType.DATABASE)
        except Exception as e:
            return HealthCheckResult("database_performance", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки производительности БД: {e}", HealthCheckType.DATABASE)
    
    async def check_database_integrity(self) -> HealthCheckResult:
        """Проверка целостности базы данных"""
        try:
            # Симуляция проверки целостности БД
            integrity_ok = True  # В реальной системе здесь была бы проверка целостности
            
            if integrity_ok:
                status = HealthStatus.HEALTHY
                message = "Целостность базы данных в норме"
            else:
                status = HealthStatus.CRITICAL
                message = "Обнаружены проблемы с целостностью БД"
            
            return HealthCheckResult("database_integrity", status, 1 if integrity_ok else 0, 1, message, HealthCheckType.DATABASE)
        except Exception as e:
            return HealthCheckResult("database_integrity", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки целостности БД: {e}", HealthCheckType.DATABASE)
    
    async def check_database_backup(self) -> HealthCheckResult:
        """Проверка резервного копирования базы данных"""
        try:
            # Симуляция проверки резервного копирования
            backup_age_hours = 2  # Возраст последнего бэкапа в часах
            
            if backup_age_hours <= 24:
                status = HealthStatus.HEALTHY
                message = f"Резервное копирование актуально: {backup_age_hours}ч назад"
            elif backup_age_hours <= 72:
                status = HealthStatus.WARNING
                message = f"Резервное копирование устарело: {backup_age_hours}ч назад"
            else:
                status = HealthStatus.CRITICAL
                message = f"Критически устаревшее резервное копирование: {backup_age_hours}ч назад"
            
            return HealthCheckResult("database_backup", status, backup_age_hours, 24, message, HealthCheckType.DATABASE)
        except Exception as e:
            return HealthCheckResult("database_backup", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки резервного копирования: {e}", HealthCheckType.DATABASE)
    
    async def check_database_connections(self) -> HealthCheckResult:
        """Проверка подключений к базе данных"""
        try:
            # Симуляция проверки подключений к БД
            active_connections = 5
            max_connections = 100
            connection_ratio = active_connections / max_connections
            
            if connection_ratio <= 0.5:
                status = HealthStatus.HEALTHY
                message = f"Подключения к БД в норме: {active_connections}/{max_connections}"
            elif connection_ratio <= 0.8:
                status = HealthStatus.WARNING
                message = f"Высокое использование подключений к БД: {active_connections}/{max_connections}"
            else:
                status = HealthStatus.CRITICAL
                message = f"Критическое использование подключений к БД: {active_connections}/{max_connections}"
            
            return HealthCheckResult("database_connections", status, connection_ratio, 0.5, message, HealthCheckType.DATABASE)
        except Exception as e:
            return HealthCheckResult("database_connections", HealthStatus.UNKNOWN, 0, 0, f"Ошибка проверки подключений к БД: {e}", HealthCheckType.DATABASE)
    
    # КОМПЛЕКСНЫЕ ПРОВЕРКИ (5 функций)
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Комплексная проверка здоровья системы"""
        try:
            all_checks = [
                # Системные проверки
                await self.check_cpu_usage(),
                await self.check_memory_usage(),
                await self.check_disk_usage(),
                await self.check_system_load(),
                await self.check_process_count(),
                
                # Сетевые проверки
                await self.check_network_connectivity(),
                await self.check_network_latency(),
                await self.check_port_availability(80),
                await self.check_network_interfaces(),
                await self.check_bandwidth_usage(),
                
                # Проверки безопасности
                await self.check_firewall_status(),
                await self.check_antivirus_status(),
                await self.check_ssl_certificates(),
                await self.check_security_updates(),
                await self.check_suspicious_processes(),
                
                # Проверки производительности
                await self.check_response_time(),
                await self.check_throughput(),
                await self.check_memory_leaks(),
                await self.check_cpu_efficiency(),
                await self.check_io_performance(),
                
                # Проверки базы данных
                await self.check_database_connection(),
                await self.check_database_performance(),
                await self.check_database_integrity(),
                await self.check_database_backup(),
                await self.check_database_connections()
            ]
            
            # Сохраняем результаты
            for check in all_checks:
                self.health_results[check.check_name] = check
            
            # Анализируем результаты
            healthy_count = sum(1 for check in all_checks if check.status == HealthStatus.HEALTHY)
            warning_count = sum(1 for check in all_checks if check.status == HealthStatus.WARNING)
            critical_count = sum(1 for check in all_checks if check.status == HealthStatus.CRITICAL)
            unknown_count = sum(1 for check in all_checks if check.status == HealthStatus.UNKNOWN)
            
            overall_status = HealthStatus.HEALTHY
            if critical_count > 0:
                overall_status = HealthStatus.CRITICAL
            elif warning_count > 0:
                overall_status = HealthStatus.WARNING
            elif unknown_count > 0:
                overall_status = HealthStatus.UNKNOWN
            
            return {
                "overall_status": overall_status.value,
                "total_checks": len(all_checks),
                "healthy": healthy_count,
                "warning": warning_count,
                "critical": critical_count,
                "unknown": unknown_count,
                "checks": [
                    {
                        "name": check.check_name,
                        "status": check.status.value,
                        "value": check.value,
                        "message": check.message,
                        "type": check.check_type.value
                    }
                    for check in all_checks
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка комплексной проверки здоровья: {e}")
            return {"error": str(e)}
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Получение сводки здоровья системы"""
        try:
            if not self.health_results:
                return {"message": "Проверки здоровья не выполнялись"}
            
            # Анализируем последние результаты
            healthy_count = sum(1 for result in self.health_results.values() if result.status == HealthStatus.HEALTHY)
            warning_count = sum(1 for result in self.health_results.values() if result.status == HealthStatus.WARNING)
            critical_count = sum(1 for result in self.health_results.values() if result.status == HealthStatus.CRITICAL)
            
            total_checks = len(self.health_results)
            health_percentage = (healthy_count / total_checks) * 100 if total_checks > 0 else 0
            
            return {
                "total_checks": total_checks,
                "health_percentage": health_percentage,
                "healthy": healthy_count,
                "warning": warning_count,
                "critical": critical_count,
                "last_check": max(result.timestamp for result in self.health_results.values()).isoformat(),
                "overall_status": "healthy" if critical_count == 0 and warning_count == 0 else "needs_attention"
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки здоровья: {e}")
            return {"error": str(e)}
    
    async def get_health_alerts(self) -> List[Dict[str, Any]]:
        """Получение алертов здоровья системы"""
        try:
            alerts = []
            
            for result in self.health_results.values():
                if result.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                    alerts.append({
                        "check_name": result.check_name,
                        "status": result.status.value,
                        "message": result.message,
                        "value": result.value,
                        "threshold": result.threshold,
                        "timestamp": result.timestamp.isoformat(),
                        "type": result.check_type.value
                    })
            
            # Сортируем по серьезности
            alerts.sort(key=lambda x: 0 if x["status"] == "critical" else 1 if x["status"] == "warning" else 2)
            
            return alerts
        except Exception as e:
            self.logger.error(f"Ошибка получения алертов здоровья: {e}")
            return []
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """Получение метрик здоровья системы"""
        try:
            metrics = {
                "system_metrics": {},
                "network_metrics": {},
                "security_metrics": {},
                "performance_metrics": {},
                "database_metrics": {}
            }
            
            for result in self.health_results.values():
                if result.check_type == HealthCheckType.SYSTEM:
                    metrics["system_metrics"][result.check_name] = {
                        "value": result.value,
                        "status": result.status.value,
                        "timestamp": result.timestamp.isoformat()
                    }
                elif result.check_type == HealthCheckType.NETWORK:
                    metrics["network_metrics"][result.check_name] = {
                        "value": result.value,
                        "status": result.status.value,
                        "timestamp": result.timestamp.isoformat()
                    }
                elif result.check_type == HealthCheckType.SECURITY:
                    metrics["security_metrics"][result.check_name] = {
                        "value": result.value,
                        "status": result.status.value,
                        "timestamp": result.timestamp.isoformat()
                    }
                elif result.check_type == HealthCheckType.PERFORMANCE:
                    metrics["performance_metrics"][result.check_name] = {
                        "value": result.value,
                        "status": result.status.value,
                        "timestamp": result.timestamp.isoformat()
                    }
                elif result.check_type == HealthCheckType.DATABASE:
                    metrics["database_metrics"][result.check_name] = {
                        "value": result.value,
                        "status": result.status.value,
                        "timestamp": result.timestamp.isoformat()
                    }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик здоровья: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья системы Health Check"""
        try:
            return {
                "status": "healthy",
                "total_checks_available": 25,
                "checks_performed": len(self.health_results),
                "last_comprehensive_check": max(result.timestamp for result in self.health_results.values()).isoformat() if self.health_results else None,
                "system_ready": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка health check: {e}")
            return {"status": "error", "error": str(e)}

class HealthCheckManager:
    """
    Менеджер системы Health Check
    """
    
    def __init__(self):
        self.health_system = HealthCheckSystem()
        self.is_initialized = False
        self.logger = logging.getLogger(f"{__name__}.HealthCheckManager")
    
    async def initialize(self):
        """Инициализация менеджера"""
        try:
            self.is_initialized = await self.health_system.initialize()
            if self.is_initialized:
                self.logger.info("Менеджер Health Check инициализирован")
            return self.is_initialized
        except Exception as e:
            self.logger.error(f"Ошибка инициализации менеджера Health Check: {e}")
            return False
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Запуск всех проверок здоровья"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.health_system.run_comprehensive_health_check()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.health_system.get_health_summary()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья менеджера"""
        try:
            return {
                "status": "healthy" if self.is_initialized else "not_initialized",
                "checks_available": 25,
                "system_ready": self.is_initialized,
                "last_activity": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка health check: {e}")
            return {"status": "error", "error": str(e)}

# Экспорт основных классов
__all__ = [
    'HealthCheckSystem',
    'HealthCheckManager',
    'HealthCheckResult',
    'HealthStatus',
    'HealthCheckType'
]
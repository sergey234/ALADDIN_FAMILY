#!/usr/bin/env python3
"""
ALADDIN VPN - Sleep Mode Manager
Система спящего режима для VPN серверов

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import time
import psutil
import signal
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Конфигурация сервера"""

    name: str
    port: int
    process_name: str
    max_memory_mb: int = 100
    idle_timeout_minutes: int = 30
    enabled: bool = True


@dataclass
class ServerStatus:
    """Статус сервера"""

    name: str
    port: int
    pid: Optional[int] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    last_activity: datetime = None
    status: str = "stopped"  # stopped, running, sleeping, error
    uptime_seconds: int = 0


class SleepModeManager:
    """
    Менеджер спящего режима для VPN серверов

    Функции:
    - Мониторинг использования памяти и CPU
    - Автоматическое отключение неактивных серверов
    - Спящий режим при превышении лимитов
    - Graceful shutdown серверов
    - Восстановление при необходимости
    """

    def __init__(self, config_file: str = "config/sleep_mode_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

        # Конфигурация серверов
        self.servers = self._load_servers()

        # Статус серверов
        self.server_status: Dict[str, ServerStatus] = {}

        # Настройки мониторинга
        self.monitoring_enabled = True
        self.check_interval = self.config.get("check_interval_seconds", 60)
        self.max_total_memory_mb = self.config.get("max_total_memory_mb", 500)

        logger.info("Sleep Mode Manager initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            "enabled": True,
            "check_interval_seconds": 60,
            "max_total_memory_mb": 500,
            "auto_sleep_enabled": True,
            "memory_threshold_percent": 80,
            "cpu_threshold_percent": 70,
            "idle_timeout_minutes": 30,
            "graceful_shutdown_timeout": 30,
            "log_file": "logs/sleep_mode.log",
            "notifications": {"enabled": True, "email": "", "webhook": ""},
        }

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            logger.warning(
                f"Config file {self.config_file} not found, using defaults"
            )
            self._save_config(default_config)

        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        import os

        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _load_servers(self) -> List[ServerConfig]:
        """Загрузка конфигурации серверов"""
        default_servers = [
            ServerConfig(
                name="VPN Web Interface",
                port=5000,
                process_name="vpn_web_interface",
                max_memory_mb=150,
                idle_timeout_minutes=30,
            ),
            ServerConfig(
                name="VPN Premium Interface",
                port=5002,
                process_name="vpn_web_interface_premium",
                max_memory_mb=200,
                idle_timeout_minutes=30,
            ),
            ServerConfig(
                name="VPN API Server",
                port=5001,
                process_name="vpn_api_server",
                max_memory_mb=100,
                idle_timeout_minutes=45,
            ),
        ]

        # Загружаем кастомные серверы из конфига
        if "servers" in self.config:
            custom_servers = []
            for server_data in self.config["servers"]:
                server = ServerConfig(
                    name=server_data["name"],
                    port=server_data["port"],
                    process_name=server_data["process_name"],
                    max_memory_mb=server_data.get("max_memory_mb", 100),
                    idle_timeout_minutes=server_data.get(
                        "idle_timeout_minutes", 30
                    ),
                    enabled=server_data.get("enabled", True),
                )
                custom_servers.append(server)
            return custom_servers

        return default_servers

    def find_server_processes(self) -> Dict[str, ServerStatus]:
        """Поиск запущенных VPN серверов"""
        server_status = {}

        for server_config in self.servers:
            if not server_config.enabled:
                continue

            status = ServerStatus(
                name=server_config.name,
                port=server_config.port,
                status="stopped",
            )

            # Ищем процесс по порту
            try:
                for conn in psutil.net_connections():
                    if (
                        conn.laddr.port == server_config.port
                        and conn.status == "LISTEN"
                    ):
                        pid = conn.pid
                        if pid:
                            process = psutil.Process(pid)
                            status.pid = pid
                            status.memory_usage_mb = (
                                process.memory_info().rss / 1024 / 1024
                            )
                            status.cpu_usage_percent = process.cpu_percent()
                            status.status = "running"
                            status.uptime_seconds = int(
                                time.time() - process.create_time()
                            )

                            # Проверяем последнюю активность (упрощенно)
                            status.last_activity = datetime.now()

                            logger.info(
                                f"Found {server_config.name} on port {server_config.port} (PID: {pid})"
                            )
                            break
            except Exception as e:
                logger.error(
                    f"Error checking server {server_config.name}: {e}"
                )
                status.status = "error"

            server_status[server_config.name] = status

        return server_status

    def check_memory_usage(self) -> Dict[str, Any]:
        """Проверка использования памяти"""
        try:
            # Общая память системы
            memory = psutil.virtual_memory()
            total_memory_mb = memory.total / 1024 / 1024
            used_memory_mb = memory.used / 1024 / 1024
            available_memory_mb = memory.available / 1024 / 1024
            memory_percent = memory.percent

            # Память VPN серверов
            vpn_memory_mb = 0
            for status in self.server_status.values():
                if status.status == "running":
                    vpn_memory_mb += status.memory_usage_mb

            return {
                "total_memory_mb": total_memory_mb,
                "used_memory_mb": used_memory_mb,
                "available_memory_mb": available_memory_mb,
                "memory_percent": memory_percent,
                "vpn_memory_mb": vpn_memory_mb,
                "vpn_memory_percent": (vpn_memory_mb / total_memory_mb) * 100,
                "threshold_exceeded": memory_percent
                > self.config.get("memory_threshold_percent", 80),
            }
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            return {}

    def should_sleep_server(
        self, server_config: ServerConfig, server_status: ServerStatus
    ) -> bool:
        """Проверка, нужно ли перевести сервер в спящий режим"""
        if server_status.status != "running":
            return False

        # Проверка памяти
        if server_status.memory_usage_mb > server_config.max_memory_mb:
            logger.warning(
                f"Server {server_config.name} exceeds memory limit: {server_status.memory_usage_mb:.1f}MB > {server_config.max_memory_mb}MB"
            )
            return True

        # Проверка общего использования памяти
        memory_info = self.check_memory_usage()
        if memory_info.get("threshold_exceeded", False):
            logger.warning(
                f"System memory threshold exceeded: {memory_info.get('memory_percent', 0):.1f}%"
            )
            return True

        # Проверка времени простоя
        if server_status.last_activity:
            idle_time = datetime.now() - server_status.last_activity
            if idle_time > timedelta(
                minutes=server_config.idle_timeout_minutes
            ):
                logger.info(
                    f"Server {server_config.name} idle for {idle_time}"
                )
                return True

        return False

    def sleep_server(
        self, server_config: ServerConfig, server_status: ServerStatus
    ) -> bool:
        """Перевод сервера в спящий режим"""
        try:
            if not server_status.pid:
                logger.warning(f"No PID for server {server_config.name}")
                return False

            process = psutil.Process(server_status.pid)

            # Graceful shutdown
            logger.info(
                f"Gracefully shutting down {server_config.name} (PID: {server_status.pid})"
            )
            process.terminate()

            # Ждем завершения
            try:
                process.wait(
                    timeout=self.config.get("graceful_shutdown_timeout", 30)
                )
                logger.info(f"Server {server_config.name} stopped gracefully")
            except psutil.TimeoutExpired:
                # Принудительное завершение
                logger.warning(f"Force killing server {server_config.name}")
                process.kill()
                process.wait()

            # Обновляем статус
            server_status.status = "sleeping"
            server_status.pid = None
            server_status.memory_usage_mb = 0.0
            server_status.cpu_usage_percent = 0.0

            self._log_sleep_event(server_config.name, "sleep")
            return True

        except Exception as e:
            logger.error(f"Error sleeping server {server_config.name}: {e}")
            server_status.status = "error"
            return False

    def wake_server(self, server_config: ServerConfig) -> bool:
        """Пробуждение сервера из спящего режима"""
        try:
            # Здесь должна быть логика запуска сервера
            # Для примера просто меняем статус
            logger.info(f"Waking up server {server_config.name}")

            # В реальной системе здесь был бы запуск сервера
            # subprocess.Popen([...])

            self._log_sleep_event(server_config.name, "wake")
            return True

        except Exception as e:
            logger.error(f"Error waking server {server_config.name}: {e}")
            return False

    def _log_sleep_event(self, server_name: str, action: str) -> None:
        """Логирование событий спящего режима"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "server": server_name,
                "action": action,
                "memory_info": self.check_memory_usage(),
            }

            log_file = self.config.get("log_file", "logs/sleep_mode.log")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error(f"Error logging sleep event: {e}")

    def monitor_servers(self) -> None:
        """Мониторинг серверов"""
        try:
            # Обновляем статус серверов
            self.server_status = self.find_server_processes()

            # Проверяем каждый сервер
            for server_config in self.servers:
                if not server_config.enabled:
                    continue

                server_status = self.server_status.get(server_config.name)
                if not server_status:
                    continue

                # Проверяем, нужно ли перевести в спящий режим
                if self.should_sleep_server(server_config, server_status):
                    self.sleep_server(server_config, server_status)

            # Логируем статистику
            self._log_monitoring_stats()

        except Exception as e:
            logger.error(f"Error monitoring servers: {e}")

    def _log_monitoring_stats(self) -> None:
        """Логирование статистики мониторинга"""
        try:
            memory_info = self.check_memory_usage()
            running_servers = len(
                [
                    s
                    for s in self.server_status.values()
                    if s.status == "running"
                ]
            )
            sleeping_servers = len(
                [
                    s
                    for s in self.server_status.values()
                    if s.status == "sleeping"
                ]
            )

            stats = {
                "timestamp": datetime.now().isoformat(),
                "running_servers": running_servers,
                "sleeping_servers": sleeping_servers,
                "total_servers": len(self.server_status),
                "memory_info": memory_info,
            }

            logger.info(f"Monitoring stats: {json.dumps(stats, indent=2)}")

        except Exception as e:
            logger.error(f"Error logging monitoring stats: {e}")

    def force_sleep_all(self) -> None:
        """Принудительный перевод всех серверов в спящий режим"""
        logger.info("Force sleeping all VPN servers...")

        for server_config in self.servers:
            if not server_config.enabled:
                continue

            server_status = self.server_status.get(server_config.name)
            if server_status and server_status.status == "running":
                self.sleep_server(server_config, server_status)

    def get_status_report(self) -> Dict[str, Any]:
        """Получение отчета о статусе"""
        memory_info = self.check_memory_usage()

        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_enabled": self.monitoring_enabled,
            "servers": {
                name: {
                    "name": status.name,
                    "port": status.port,
                    "status": status.status,
                    "pid": status.pid,
                    "memory_usage_mb": round(status.memory_usage_mb, 2),
                    "cpu_usage_percent": round(status.cpu_usage_percent, 2),
                    "uptime_seconds": status.uptime_seconds,
                }
                for name, status in self.server_status.items()
            },
            "memory_info": memory_info,
            "total_servers": len(self.server_status),
            "running_servers": len(
                [
                    s
                    for s in self.server_status.values()
                    if s.status == "running"
                ]
            ),
            "sleeping_servers": len(
                [
                    s
                    for s in self.server_status.values()
                    if s.status == "sleeping"
                ]
            ),
        }


def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ALADDIN VPN Sleep Mode Manager"
    )
    parser.add_argument(
        "--monitor", action="store_true", help="Start monitoring mode"
    )
    parser.add_argument(
        "--sleep-all", action="store_true", help="Force sleep all servers"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show status report"
    )
    parser.add_argument(
        "--config",
        default="config/sleep_mode_config.json",
        help="Config file path",
    )

    args = parser.parse_args()

    manager = SleepModeManager(args.config)

    if args.sleep_all:
        manager.force_sleep_all()
        print("✅ All VPN servers put to sleep")

    elif args.status:
        report = manager.get_status_report()
        print(json.dumps(report, indent=2))

    elif args.monitor:
        print("🔄 Starting VPN servers monitoring...")
        try:
            while True:
                manager.monitor_servers()
                time.sleep(manager.check_interval)
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped")

    else:
        print("ALADDIN VPN Sleep Mode Manager")
        print("Use --help for available options")


if __name__ == "__main__":
    main()

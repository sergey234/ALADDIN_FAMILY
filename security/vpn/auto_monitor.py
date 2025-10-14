#!/usr/bin/env python3
"""
ALADDIN VPN - Auto Monitor
Автоматический мониторинг и управление VPN серверами

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List


class VPNMonitor:
    """Монитор VPN серверов"""

    def __init__(self):
        self.config = {
            "check_interval": 60,  # Проверка каждые 60 секунд
            "memory_threshold": 80,  # 80% использования памяти
            "min_free_memory_mb": 1000,  # Минимум 1GB свободной памяти
            "idle_timeout_minutes": 30,  # 30 минут простоя
            "log_file": "vpn_monitor.log",
        }

        self.last_activity = {}
        self.running = True

        # Обработчик сигналов для корректного завершения
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        self.log("🛑 Received shutdown signal, stopping monitor...")
        self.running = False

    def log(self, message: str) -> None:
        """Логирование с записью в файл"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        try:
            with open(self.config["log_file"], "a") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def _get_processes_by_ports(self) -> List[str]:
        """Получение PID процессов по портам"""
        try:
            result = subprocess.run(
                ["lsof", "-ti:5000,5002,5001"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")
            return []
        except Exception as e:
            self.log(f"Error getting processes by ports: {e}")
            return []

    def _get_process_info(self, pid: str, port: int) -> Dict[str, Any]:
        """Получение информации о конкретном процессе"""
        try:
            ps_result = subprocess.run(
                [
                    "ps",
                    "-p",
                    pid,
                    "-o",
                    "pid,ppid,pcpu,pmem,etime,command",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if ps_result.returncode == 0:
                lines = ps_result.stdout.strip().split("\n")
                if len(lines) > 1:
                    data = lines[1].split()
                    if len(data) >= 6:
                        return {
                            "pid": int(pid),
                            "port": port,
                            "cpu_percent": (
                                float(data[2]) if data[2] != "-" else 0.0
                            ),
                            "memory_percent": (
                                float(data[3]) if data[3] != "-" else 0.0
                            ),
                            "uptime": data[4],
                            "command": " ".join(data[5:]),
                        }
            return {}
        except Exception as e:
            self.log(f"Error getting process info for PID {pid}: {e}")
            return {}

    def find_vpn_processes(self) -> Dict[str, Dict[str, Any]]:
        """Поиск VPN процессов с детальной информацией"""
        processes = {}
        try:
            pids = self._get_processes_by_ports()
            ports = [5000, 5002, 5001]

            for i, pid in enumerate(pids):
                if pid and i < len(ports):
                    port = ports[i]
                    process_info = self._get_process_info(pid, port)
                    if process_info:
                        processes[f"port_{port}"] = process_info

            return processes
        except Exception as e:
            self.log(f"Error finding processes: {e}")
            return {}

    def get_memory_usage(self) -> Dict[str, float]:
        """Получение информации о памяти"""
        try:
            # Используем vm_stat для macOS
            result = subprocess.run(
                ["vm_stat"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                memory_info = {}

                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = (
                            key.strip()
                            .replace(" ", "_")
                            .replace("(", "")
                            .replace(")", "")
                        )
                        value = value.strip().replace(".", "").replace("K", "")
                        if value.isdigit():
                            memory_info[key] = (
                                int(value) / 1024
                            )  # Convert to MB

                # Расчет использования памяти
                if (
                    "Pages_free" in memory_info
                    and "Pages_active" in memory_info
                ):
                    total_mb = (
                        memory_info.get("Pages_free", 0)
                        + memory_info.get("Pages_active", 0)
                        + memory_info.get("Pages_inactive", 0)
                        + memory_info.get("Pages_wired", 0)
                    )
                    used_mb = memory_info.get(
                        "Pages_active", 0
                    ) + memory_info.get("Pages_wired", 0)
                    used_percent = (
                        (used_mb / total_mb * 100) if total_mb > 0 else 0
                    )

                    return {
                        "total_mb": total_mb,
                        "used_mb": used_mb,
                        "free_mb": total_mb - used_mb,
                        "used_percent": used_percent,
                    }

            return {
                "total_mb": 0,
                "used_mb": 0,
                "free_mb": 0,
                "used_percent": 0,
            }

        except Exception as e:
            self.log(f"Error getting memory usage: {e}")
            return {
                "total_mb": 0,
                "used_mb": 0,
                "free_mb": 0,
                "used_percent": 0,
            }

    def should_sleep_processes(
        self,
        processes: Dict[str, Dict[str, Any]],
        memory_info: Dict[str, float],
    ) -> bool:
        """Проверка, нужно ли отключить процессы"""

        # Проверка 1: Использование памяти
        if memory_info["used_percent"] > self.config["memory_threshold"]:
            self.log(
                f"Memory usage high: {memory_info['used_percent']:.1f}% > {self.config['memory_threshold']}%"
            )
            return True

        # Проверка 2: Свободная память
        if memory_info["free_mb"] < self.config["min_free_memory_mb"]:
            self.log(
                f"Low free memory: {memory_info['free_mb']:.1f}MB < {self.config['min_free_memory_mb']}MB"
            )
            return True

        # Проверка 3: Время простоя процессов
        now = datetime.now()
        for name, process_info in processes.items():
            if name not in self.last_activity:
                self.last_activity[name] = now
                continue

            idle_time = now - self.last_activity[name]
            if idle_time > timedelta(
                minutes=self.config["idle_timeout_minutes"]
            ):
                self.log(f"Process {name} idle for {idle_time}")
                return True

        return False

    def kill_processes(self, processes: Dict[str, Dict[str, Any]]) -> bool:
        """Отключение процессов"""
        success = True

        for name, process_info in processes.items():
            try:
                pid = process_info["pid"]
                port = process_info["port"]

                self.log(f"Stopping {name} on port {port} (PID: {pid})...")

                # Graceful shutdown
                os.kill(pid, signal.SIGTERM)
                time.sleep(3)

                # Проверяем, завершился ли процесс
                try:
                    os.kill(pid, 0)
                    # Процесс еще жив, принудительно завершаем
                    self.log(f"Force killing {name} (PID: {pid})...")
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)
                except ProcessLookupError:
                    # Процесс завершился
                    self.log(f"✅ {name} stopped gracefully")

                # Удаляем из отслеживания
                if name in self.last_activity:
                    del self.last_activity[name]

            except ProcessLookupError:
                self.log(f"✅ {name} already stopped")
            except Exception as e:
                self.log(f"❌ Error stopping {name}: {e}")
                success = False

        return success

    def update_activity(self, processes: Dict[str, Dict[str, Any]]) -> None:
        """Обновление времени последней активности"""
        now = datetime.now()
        for name in processes.keys():
            self.last_activity[name] = now

    def save_status(
        self,
        action: str,
        processes: Dict[str, Dict[str, Any]],
        memory_info: Dict[str, float],
    ) -> None:
        """Сохранение статуса"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "processes": processes,
                "memory_info": memory_info,
                "monitor_config": self.config,
            }

            with open("vpn_monitor_status.json", "w") as f:
                json.dump(status, f, indent=2)

        except Exception as e:
            self.log(f"Error saving status: {e}")

    def run_monitor(self) -> None:
        """Запуск мониторинга"""
        self.log("🚀 VPN Monitor started")

        while self.running:
            try:
                # 1. Находим VPN процессы
                processes = self.find_vpn_processes()

                # 2. Получаем информацию о памяти
                memory_info = self.get_memory_usage()

                # 3. Логируем текущий статус
                if processes:
                    self.log(f"Found {len(processes)} VPN processes")
                    for name, info in processes.items():
                        self.log(
                            f"  {name}: PID {info['pid']}, CPU {info['cpu_percent']:.1f}%, Memory {info['memory_percent']:.1f}%"
                        )
                else:
                    self.log("No VPN processes found")

                self.log(
                    f"Memory: {memory_info['used_percent']:.1f}% used ({memory_info['used_mb']:.1f}MB / {memory_info['total_mb']:.1f}MB)"
                )

                # 4. Проверяем, нужно ли отключить процессы
                if processes and self.should_sleep_processes(
                    processes, memory_info
                ):
                    self.log(
                        "🛑 Conditions met for sleep mode - stopping VPN processes..."
                    )

                    if self.kill_processes(processes):
                        self.log("✅ VPN processes successfully stopped")
                        self.save_status("sleep", processes, memory_info)
                    else:
                        self.log("❌ Some processes could not be stopped")
                elif processes:
                    # Обновляем время активности
                    self.update_activity(processes)
                    self.log("✅ VPN processes running normally")
                else:
                    self.log("😴 All VPN processes in sleep mode")

                # 5. Ждем до следующей проверки
                self.log(
                    f"⏰ Next check in {self.config['check_interval']} seconds..."
                )
                time.sleep(self.config["check_interval"])

            except KeyboardInterrupt:
                self.log("🛑 Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in monitor loop: {e}")
                time.sleep(10)  # Ждем 10 секунд перед повтором

        self.log("🏁 VPN Monitor stopped")


def main():
    """Главная функция"""
    monitor = VPNMonitor()
    monitor.run_monitor()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ALADDIN VPN - Auto Sleep Manager
Простой менеджер автоматического отключения VPN серверов

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
from datetime import datetime
from typing import Any, Dict, List


def log_message(message: str) -> None:
    """Простое логирование"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def find_vpn_processes() -> Dict[str, int]:
    """Поиск VPN процессов"""
    processes = {}

    try:
        # Ищем процессы по портам
        result = subprocess.run(
            ["lsof", "-ti:5000,5002,5001"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for i, pid in enumerate(pids):
                if pid:
                    port = [5000, 5002, 5001][i] if i < 3 else 0
                    processes[f"port_{port}"] = int(pid)
                    log_message(f"Found VPN process on port {port}: PID {pid}")

        return processes

    except Exception as e:
        log_message(f"Error finding processes: {e}")
        return {}


def get_memory_usage() -> Dict[str, float]:
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
                        memory_info[key] = int(value) / 1024  # Convert to MB

            # Примерная оценка использования памяти
            if "Pages_free" in memory_info and "Pages_active" in memory_info:
                total_mb = (
                    memory_info.get("Pages_free", 0)
                    + memory_info.get("Pages_active", 0)
                    + memory_info.get("Pages_inactive", 0)
                    + memory_info.get("Pages_wired", 0)
                )
                used_mb = memory_info.get("Pages_active", 0) + memory_info.get(
                    "Pages_wired", 0
                )
                used_percent = (
                    (used_mb / total_mb * 100) if total_mb > 0 else 0
                )

                return {
                    "total_mb": total_mb,
                    "used_mb": used_mb,
                    "used_percent": used_percent,
                }

        return {"total_mb": 0, "used_mb": 0, "used_percent": 0}

    except Exception as e:
        log_message(f"Error getting memory usage: {e}")
        return {"total_mb": 0, "used_mb": 0, "used_percent": 0}


def kill_vpn_processes(processes: Dict[str, int]) -> bool:
    """Отключение VPN процессов"""
    success = True

    for name, pid in processes.items():
        try:
            log_message(f"Stopping {name} (PID: {pid})...")

            # Сначала пробуем graceful shutdown
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)

            # Проверяем, завершился ли процесс
            try:
                os.kill(pid, 0)  # Проверка существования процесса
                # Если дошли сюда, процесс еще жив
                log_message(f"Force killing {name} (PID: {pid})...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            except ProcessLookupError:
                # Процесс уже завершился
                log_message(f"{name} stopped gracefully")

        except ProcessLookupError:
            log_message(f"{name} already stopped")
        except Exception as e:
            log_message(f"Error stopping {name}: {e}")
            success = False

    return success


def check_if_should_sleep() -> bool:
    """Проверка, нужно ли отключить VPN серверы"""
    memory_info = get_memory_usage()

    # Критерии для отключения
    memory_threshold = 80  # 80% использования памяти
    min_memory_mb = 1000  # Минимум 1GB свободной памяти

    if memory_info["used_percent"] > memory_threshold:
        log_message(
            f"Memory usage high: {memory_info['used_percent']:.1f}% > {memory_threshold}%"
        )
        return True

    if memory_info["total_mb"] - memory_info["used_mb"] < min_memory_mb:
        log_message(
            f"Low available memory: {memory_info['total_mb'] - memory_info['used_mb']:.1f}MB < {min_memory_mb}MB"
        )
        return True

    return False


def save_sleep_status(
    processes: Dict[str, int], memory_info: Dict[str, float]
) -> None:
    """Сохранение статуса отключения"""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "action": "sleep",
            "processes_stopped": list(processes.keys()),
            "memory_info": memory_info,
            "reason": "automatic_sleep_mode",
        }

        with open("vpn_sleep_status.json", "w") as f:
            json.dump(status, f, indent=2)

        log_message("Sleep status saved to vpn_sleep_status.json")

    except Exception as e:
        log_message(f"Error saving sleep status: {e}")


def main():
    """Главная функция"""
    log_message("🔍 ALADDIN VPN Auto Sleep Manager started")

    # 1. Проверяем VPN процессы
    processes = find_vpn_processes()

    if not processes:
        log_message("✅ No VPN processes found - already in sleep mode")
        return

    log_message(f"Found {len(processes)} VPN processes")

    # 2. Проверяем использование памяти
    memory_info = get_memory_usage()
    log_message(
        f"Memory usage: {memory_info['used_percent']:.1f}% ({memory_info['used_mb']:.1f}MB / {memory_info['total_mb']:.1f}MB)"
    )

    # 3. Решаем, нужно ли отключать
    should_sleep = check_if_should_sleep()

    if should_sleep:
        log_message("🛑 Memory usage high - putting VPN servers to sleep...")

        # 4. Отключаем процессы
        success = kill_vpn_processes(processes)

        if success:
            log_message("✅ VPN servers successfully put to sleep")
            save_sleep_status(processes, memory_info)
        else:
            log_message("❌ Some VPN servers could not be stopped")
    else:
        log_message("✅ Memory usage is normal - keeping VPN servers running")


if __name__ == "__main__":
    main()

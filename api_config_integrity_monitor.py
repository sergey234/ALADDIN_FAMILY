#!/usr/bin/env python3
"""
🚀 ALADDIN API CONFIGURATION INTEGRITY MONITOR
Система мониторинга целостности API конфигураций

Автоматически отслеживает изменения в API настройках
и предотвращает несанкционированные модификации.
"""

import os
import json
import hashlib
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Настройка логирования
logging.basicConfig(
    filename='api_config_integrity.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class APIConfigIntegrityMonitor:
    """
    Монитор целостности API конфигураций
    Отслеживает изменения и предотвращает несанкционированные модификации
    """

    INTEGRITY_LOG_FILE = "api_integrity_monitor.log"
    ALERT_LOG_FILE = "api_integrity_alerts.log"
    BASELINE_FILE = "api_config_baseline.json"
    MONITOR_CONFIG_FILE = "integrity_monitor_config.json"

    # Критические файлы для мониторинга
    CRITICAL_FILES = [
        "api_gateway_complete.py",
        "api_gateway_final.py",
        "api_gateway_production_final.py",
        "sfm_adapter_fixed.py",
        "sfm_adapter.py",
        "server_manager.py",
        "api_config_lockdown_system.py",
        "api_config_backup_system.py"
    ]

    # Критические JSON конфиги
    CRITICAL_JSON_FILES = [
        "*.json"
    ]

    def __init__(self):
        self.baseline = self._load_baseline()
        self.monitor_config = self._load_monitor_config()
        self.alerts_enabled = True
        self.auto_backup_enabled = True

        # Настройка алертов
        self._setup_alert_logging()

    def _load_baseline(self) -> Dict[str, Any]:
        """Загрузка базовой линии конфигураций"""
        if os.path.exists(self.BASELINE_FILE):
            try:
                with open(self.BASELINE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Ошибка загрузки базовой линии: {e}")
        return {"files": {}, "json_configs": {}, "created_at": None}

    def _save_baseline(self):
        """Сохранение базовой линии"""
        try:
            with open(self.BASELINE_FILE, 'w') as f:
                json.dump(self.baseline, f, indent=2)
        except Exception as e:
            logging.error(f"Ошибка сохранения базовой линии: {e}")

    def _load_monitor_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации монитора"""
        if os.path.exists(self.MONITOR_CONFIG_FILE):
            try:
                with open(self.MONITOR_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Ошибка загрузки конфигурации монитора: {e}")

        # Конфигурация по умолчанию
        return {
            "check_interval": 300,  # 5 минут
            "alert_on_change": True,
            "auto_backup_on_change": True,
            "strict_mode": True,
            "allowed_modifiers": ["APIConfigLockdown", "root", "system"]
        }

    def _setup_alert_logging(self):
        """Настройка логирования алертов"""
        alert_logger = logging.getLogger('alerts')
        alert_logger.setLevel(logging.WARNING)

        # Файл алертов
        alert_handler = logging.FileHandler(self.ALERT_LOG_FILE)
        alert_handler.setFormatter(logging.Formatter(
            '%(asctime)s - ALERT - %(message)s'
        ))
        alert_logger.addHandler(alert_handler)

        self.alert_logger = alert_logger

    def calculate_file_hash(self, filepath: str) -> str:
        """Вычисление SHA256 хэша файла"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logging.error(f"Ошибка вычисления хэша файла {filepath}: {e}")
            return ""

    def scan_critical_files(self) -> Dict[str, Any]:
        """
        Сканирование всех критических файлов
        """
        current_state = {
            "scan_timestamp": datetime.now().isoformat(),
            "files": {},
            "json_configs": {}
        }

        # Сканируем Python файлы
        for filename in self.CRITICAL_FILES:
            if os.path.exists(filename):
                file_hash = self.calculate_file_hash(filename)
                file_size = os.path.getsize(filename)
                modified_time = datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()

                current_state["files"][filename] = {
                    "hash": file_hash,
                    "size": file_size,
                    "modified": modified_time,
                    "exists": True
                }
            else:
                current_state["files"][filename] = {
                    "exists": False,
                    "error": "File not found"
                }

        # Сканируем JSON файлы
        for pattern in self.CRITICAL_JSON_FILES:
            for json_file in Path(".").glob(pattern):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        data_hash = hashlib.sha256(
                            json.dumps(data, sort_keys=True).encode()
                        ).hexdigest()

                    current_state["json_configs"][json_file.name] = {
                        "hash": data_hash,
                        "size": len(json.dumps(data)),
                        "modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat(),
                        "exists": True
                    }
                except Exception as e:
                    current_state["json_configs"][json_file.name] = {
                        "exists": False,
                        "error": str(e)
                    }

        return current_state

    def detect_changes(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обнаружение изменений в файлах
        """
        changes = {
            "timestamp": datetime.now().isoformat(),
            "modified_files": [],
            "new_files": [],
            "deleted_files": [],
            "json_changes": [],
            "severity": "LOW"
        }

        # Проверяем Python файлы
        baseline_files = self.baseline.get("files", {})
        current_files = current_state.get("files", {})

        for filename, current_info in current_files.items():
            baseline_info = baseline_files.get(filename)

            if baseline_info is None:
                # Новый файл
                changes["new_files"].append(filename)
                changes["severity"] = "MEDIUM"
            elif not current_info.get("exists", False):
                # Файл удален
                changes["deleted_files"].append(filename)
                changes["severity"] = "HIGH"
            elif current_info.get("hash") != baseline_info.get("hash"):
                # Файл изменен
                change_info = {
                    "file": filename,
                    "old_hash": baseline_info.get("hash", ""),
                    "new_hash": current_info.get("hash", ""),
                    "old_modified": baseline_info.get("modified", ""),
                    "new_modified": current_info.get("modified", "")
                }
                changes["modified_files"].append(change_info)

                # Определяем серьезность изменения
                if filename in ["api_gateway_complete.py", "sfm_adapter_fixed.py"]:
                    changes["severity"] = "CRITICAL"
                elif changes["severity"] != "CRITICAL":
                    changes["severity"] = "HIGH"

        # Проверяем JSON конфиги
        baseline_json = self.baseline.get("json_configs", {})
        current_json = current_state.get("json_configs", {})

        for filename, current_info in current_json.items():
            baseline_info = baseline_json.get(filename)

            if baseline_info is None:
                changes["json_changes"].append({
                    "file": filename,
                    "type": "new",
                    "severity": "MEDIUM"
                })
            elif not current_info.get("exists", False):
                changes["json_changes"].append({
                    "file": filename,
                    "type": "deleted",
                    "severity": "HIGH"
                })
            elif current_info.get("hash") != baseline_info.get("hash"):
                changes["json_changes"].append({
                    "file": filename,
                    "type": "modified",
                    "old_hash": baseline_info.get("hash", ""),
                    "new_hash": current_info.get("hash", ""),
                    "severity": "HIGH"
                })

        return changes

    def create_change_alert(self, changes: Dict[str, Any]) -> str:
        """
        Создание алерта об изменениях
        """
        alert_message = f"🚨 API CONFIG INTEGRITY ALERT - {changes['severity']}\n"
        alert_message += f"Time: {changes['timestamp']}\n\n"

        if changes["modified_files"]:
            alert_message += f"📝 MODIFIED FILES ({len(changes['modified_files'])}):\n"
            for change in changes["modified_files"]:
                alert_message += f"  - {change['file']}\n"

        if changes["new_files"]:
            alert_message += f"🆕 NEW FILES ({len(changes['new_files'])}):\n"
            for filename in changes["new_files"]:
                alert_message += f"  - {filename}\n"

        if changes["deleted_files"]:
            alert_message += f"🗑️  DELETED FILES ({len(changes['deleted_files'])}):\n"
            for filename in changes["deleted_files"]:
                alert_message += f"  - {filename}\n"

        if changes["json_changes"]:
            alert_message += f"🔧 JSON CHANGES ({len(changes['json_changes'])}):\n"
            for change in changes["json_changes"]:
                alert_message += f"  - {change['file']} ({change['type']})\n"

        alert_message += "\n⚠️  IMMEDIATE INVESTIGATION REQUIRED!"

        return alert_message

    def handle_changes(self, changes: Dict[str, Any]) -> bool:
        """
        Обработка обнаруженных изменений
        """
        if not any([changes["modified_files"], changes["new_files"],
                   changes["deleted_files"], changes["json_changes"]]):
            return True  # Нет изменений

        # Логируем изменения
        logging.info(f"Обнаружены изменения конфигурации: {changes['severity']}")

        # Создаем алерт
        alert_message = self.create_change_alert(changes)
        self.alert_logger.warning(alert_message)

        print(alert_message)

        # Автоматическое резервное копирование при изменениях
        if self.auto_backup_enabled and changes["severity"] in ["HIGH", "CRITICAL"]:
            print("\n💾 Создание экстренной резервной копии...")
            try:
                import api_config_backup_system
                backup_system = api_config_backup_system.APIConfigBackupSystem()
                backup_name = backup_system.create_immutable_backup(
                    f"Emergency backup - {changes['severity']} changes detected"
                )
                if backup_name:
                    print(f"✅ Экстренная копия создана: {backup_name}")
            except Exception as e:
                logging.error(f"Ошибка создания экстренной копии: {e}")

        # В strict mode блокируем дальнейшую работу при критических изменениях
        if self.monitor_config.get("strict_mode", False) and changes["severity"] == "CRITICAL":
            print("\n🚫 СТРОГИЙ РЕЖИМ: Критические изменения обнаружены!")
            print("🔒 Система заблокирована до ручной проверки.")
            return False

        return True

    def establish_baseline(self) -> bool:
        """
        Установление базовой линии для мониторинга
        """
        print("📊 Установление базовой линии API конфигураций...")

        current_state = self.scan_critical_files()
        changes = self.detect_changes(current_state)

        if changes["severity"] != "LOW":
            print("⚠️  Обнаружены существующие изменения перед установлением базовой линии!")
            print("Рекомендуется проверить конфигурации перед продолжением.")

            user_input = input("Продолжить установление базовой линии? (yes/no): ")
            if user_input.lower() != "yes":
                return False

        # Устанавливаем базовую линию
        self.baseline = current_state
        self.baseline["created_at"] = datetime.now().isoformat()
        self._save_baseline()

        print("✅ Базовая линия установлена!")
        print(f"📅 Время: {self.baseline['created_at']}")
        print(f"📁 Файлов отслеживается: {len(self.baseline.get('files', {}))}")
        print(f"🔧 JSON конфигов: {len(self.baseline.get('json_configs', {}))}")

        return True

    def run_integrity_check(self) -> Dict[str, Any]:
        """
        Запуск проверки целостности
        """
        print("🔍 Запуск проверки целостности API конфигураций...")

        current_state = self.scan_critical_files()
        changes = self.detect_changes(current_state)

        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "OK" if changes["severity"] == "LOW" else "CHANGES_DETECTED",
            "severity": changes["severity"],
            "changes": changes,
            "baseline_age": None
        }

        if self.baseline.get("created_at"):
            baseline_time = datetime.fromisoformat(self.baseline["created_at"])
            result["baseline_age"] = str(datetime.now() - baseline_time)

        # Обрабатываем изменения
        success = self.handle_changes(changes)

        if success:
            print(f"✅ Проверка завершена: {result['status']} (Severity: {result['severity']})")
        else:
            print(f"❌ Проверка заблокирована: {result['status']} (Severity: {result['severity']})")
            result["status"] = "BLOCKED"

        return result

    def start_continuous_monitoring(self, interval_seconds: int = 300):
        """
        Запуск непрерывного мониторинга
        """
        print(f"👀 Запуск непрерывного мониторинга (интервал: {interval_seconds} сек)...")
        print("Нажмите Ctrl+C для остановки")

        try:
            while True:
                result = self.run_integrity_check()

                if result["status"] == "BLOCKED":
                    print("🚫 Мониторинг остановлен из-за критических изменений!")
                    break

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n🛑 Мониторинг остановлен пользователем")

    def get_integrity_report(self) -> str:
        """
        Получение отчета о целостности
        """
        report = "# 🚀 ALADDIN API CONFIGURATION INTEGRITY REPORT\n\n"
        report += f"**Дата отчета:** {datetime.now().isoformat()}\n\n"

        if self.baseline.get("created_at"):
            baseline_time = datetime.fromisoformat(self.baseline["created_at"])
            age = datetime.now() - baseline_time
            report += f"**Базовая линия:** {self.baseline['created_at']} ({age.days} дней)\n\n"
        else:
            report += "**Базовая линия:** НЕ УСТАНОВЛЕНА\n\n"

        # Проверяем текущее состояние
        current_state = self.scan_critical_files()
        changes = self.detect_changes(current_state)

        report += f"## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ\n\n"
        report += f"- **Статус:** {'✅ OK' if changes['severity'] == 'LOW' else '⚠️  CHANGES DETECTED'}\n"
        report += f"- **Серьезность:** {changes['severity']}\n"
        report += f"- **Проверено файлов:** {len(current_state.get('files', {}))}\n"
        report += f"- **JSON конфигов:** {len(current_state.get('json_configs', {}))}\n\n"

        if changes["modified_files"]:
            report += f"## 📝 ИЗМЕНЕННЫЕ ФАЙЛЫ ({len(changes['modified_files'])})\n\n"
            for change in changes["modified_files"]:
                report += f"- `{change['file']}`\n"

        if changes["new_files"]:
            report += f"## 🆕 НОВЫЕ ФАЙЛЫ ({len(changes['new_files'])})\n\n"
            for filename in changes["new_files"]:
                report += f"- `{filename}`\n"

        if changes["deleted_files"]:
            report += f"## 🗑️  УДАЛЕННЫЕ ФАЙЛЫ ({len(changes['deleted_files'])})\n\n"
            for filename in changes["deleted_files"]:
                report += f"- `{filename}`\n"

        return report


def main():
    """
    Основная функция для демонстрации монитора целостности
    """
    print("🚀 ALADDIN API CONFIGURATION INTEGRITY MONITOR")
    print("=" * 55)

    monitor = APIConfigIntegrityMonitor()

    print(f"📊 Базовая линия: {'Установлена' if monitor.baseline.get('created_at') else 'Не установлена'}")

    # Проверяем, нужно ли установить базовую линию
    if not monitor.baseline.get("created_at"):
        print("\n🔧 Базовая линия не установлена.")
        user_input = input("Установить базовую линию сейчас? (yes/no): ")

        if user_input.lower() == "yes":
            if monitor.establish_baseline():
                print("✅ Базовая линия установлена!")
            else:
                print("❌ Ошибка установки базовой линии!")
                return

    # Запускаем проверку целостности
    print("\n🔍 Запуск проверки целостности...")
    result = monitor.run_integrity_check()

    # Генерируем отчет
    report = monitor.get_integrity_report()
    report_file = f"integrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 Отчет сохранен: {report_file}")

    # Предлагаем запустить непрерывный мониторинг
    if result["status"] == "OK":
        user_input = input("\n👀 Запустить непрерывный мониторинг? (yes/no): ")
        if user_input.lower() == "yes":
            interval = int(input("Интервал проверки (секунды, по умолчанию 300): ") or "300")
            monitor.start_continuous_monitoring(interval)


if __name__ == "__main__":
    main()
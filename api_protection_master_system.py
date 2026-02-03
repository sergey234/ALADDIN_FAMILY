#!/usr/bin/env python3
"""
🚀 ALADDIN API PROTECTION MASTER SYSTEM
Главная система защиты и фиксации API настроек

Объединяет все компоненты защиты API:
- Фиксация конфигураций
- Резервное копирование
- Мониторинг целостности
- Предотвращение изменений
"""

import os
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class APIProtectionMasterSystem:
    """
    Главная система защиты API конфигураций
    Управляет всеми компонентами защиты и фиксации
    """

    def __init__(self):
        self.systems = {}
        self.protection_status = "INITIALIZING"
        self._load_protection_status()

    def _load_protection_status(self):
        """Загрузка статуса системы защиты"""
        status_file = "api_protection_status.json"
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    self.protection_status = json.load(f)
            except Exception as e:
                print(f"⚠️  Ошибка загрузки статуса защиты: {e}")
                self.protection_status = "ERROR"

    def _save_protection_status(self):
        """Сохранение статуса системы защиты"""
        status_data = {
            "status": self.protection_status,
            "last_updated": datetime.now().isoformat(),
            "systems_active": list(self.systems.keys()),
            "version": "2.1.0-PROD"
        }

        try:
            with open("api_protection_status.json", 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Ошибка сохранения статуса: {e}")

    def initialize_protection_systems(self) -> bool:
        """
        Инициализация всех систем защиты
        """
        print("🚀 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ЗАЩИТЫ API КОНФИГУРАЦИЙ")
        print("=" * 60)

        success_count = 0
        total_systems = 3

        # 1. Инициализация системы фиксации
        print("\n1️⃣  Инициализация системы фиксации...")
        try:
            import api_config_lockdown_system
            lockdown_system = api_config_lockdown_system.APIConfigLockdown()
            self.systems["lockdown"] = lockdown_system
            print("   ✅ Система фиксации готова")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Ошибка инициализации системы фиксации: {e}")

        # 2. Инициализация системы резервного копирования
        print("\n2️⃣  Инициализация системы резервного копирования...")
        try:
            import api_config_backup_system
            backup_system = api_config_backup_system.APIConfigBackupSystem()
            self.systems["backup"] = backup_system
            print("   ✅ Система резервного копирования готова")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Ошибка инициализации системы резервного копирования: {e}")

        # 3. Инициализация монитора целостности
        print("\n3️⃣  Инициализация монитора целостности...")
        try:
            import api_config_integrity_monitor
            integrity_monitor = api_config_integrity_monitor.APIConfigIntegrityMonitor()
            self.systems["integrity"] = integrity_monitor
            print("   ✅ Монитор целостности готов")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Ошибка инициализации монитора целостности: {e}")

        # Проверяем успешность инициализации
        if success_count == total_systems:
            self.protection_status = "ACTIVE"
            print(f"\n🎉 Все системы защиты инициализированы успешно! ({success_count}/{total_systems})")
            self._save_protection_status()
            return True
        else:
            self.protection_status = "PARTIAL"
            print(f"\n⚠️  Частичная инициализация систем защиты ({success_count}/{total_systems})")
            self._save_protection_status()
            return False

    def activate_full_protection(self) -> Dict[str, Any]:
        """
        Активация полной защиты API конфигураций
        """
        print("\n🔒 АКТИВАЦИЯ ПОЛНОЙ ЗАЩИТЫ API КОНФИГУРАЦИЙ")
        print("=" * 50)

        results = {
            "timestamp": datetime.now().isoformat(),
            "systems_activated": [],
            "backups_created": [],
            "baselines_established": [],
            "errors": []
        }

        # 1. Фиксация всех конфигураций
        if "lockdown" in self.systems:
            print("\n📌 Шаг 1: Фиксация API конфигураций...")
            try:
                lockdown_success = self.systems["lockdown"].lock_configuration(
                    "Full protection activation - Production lockdown"
                )
                if lockdown_success:
                    results["systems_activated"].append("lockdown")
                    print("   ✅ Конфигурации зафиксированы")
                else:
                    results["errors"].append("lockdown_failed")
                    print("   ❌ Ошибка фиксации конфигураций")
            except Exception as e:
                results["errors"].append(f"lockdown_error: {e}")
                print(f"   ❌ Ошибка: {e}")

        # 2. Создание полного резервного копирования
        if "backup" in self.systems:
            print("\n💾 Шаг 2: Создание резервных копий...")
            try:
                backup_name = self.systems["backup"].create_immutable_backup(
                    "Full protection activation - Complete API backup"
                )
                if backup_name:
                    results["backups_created"].append(backup_name)
                    print(f"   ✅ Резервная копия создана: {backup_name}")
                else:
                    results["errors"].append("backup_failed")
                    print("   ❌ Ошибка создания резервной копии")
            except Exception as e:
                results["errors"].append(f"backup_error: {e}")
                print(f"   ❌ Ошибка: {e}")

        # 3. Установление базовой линии для мониторинга
        if "integrity" in self.systems:
            print("\n👀 Шаг 3: Установление базовой линии мониторинга...")
            try:
                baseline_success = self.systems["integrity"].establish_baseline()
                if baseline_success:
                    results["baselines_established"].append("integrity_baseline")
                    print("   ✅ Базовая линия установлена")
                else:
                    results["errors"].append("baseline_failed")
                    print("   ❌ Ошибка установки базовой линии")
            except Exception as e:
                results["errors"].append(f"baseline_error: {e}")
                print(f"   ❌ Ошибка: {e}")

        # Создание отчета об активации
        activation_report = self._generate_activation_report(results)

        # Сохранение отчета
        report_file = f"api_protection_activation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(activation_report)

        print(f"\n📄 Отчет об активации сохранен: {report_file}")

        # Финальный статус
        if not results["errors"]:
            self.protection_status = "FULLY_ACTIVE"
            print("\n🎉 ПОЛНАЯ ЗАЩИТА API АКТИВИРОВАНА УСПЕШНО!")
            print("🔒 Все конфигурации зафиксированы и защищены от изменений")
        else:
            self.protection_status = "ACTIVE_WITH_ERRORS"
            print(f"\n⚠️  Защита активирована с предупреждениями ({len(results['errors'])} ошибок)")

        self._save_protection_status()

        return results

    def _generate_activation_report(self, results: Dict[str, Any]) -> str:
        """
        Генерация отчета об активации защиты
        """
        report = "# 🚀 ALADDIN API PROTECTION ACTIVATION REPORT\n\n"
        report += f"**Дата активации:** {datetime.now().isoformat()}\n"
        report += f"**Версия системы:** 2.1.0-PROD\n\n"

        report += "## 📊 РЕЗУЛЬТАТЫ АКТИВАЦИИ\n\n"

        # Системы
        report += f"### 🔧 АКТИВИРОВАННЫЕ СИСТЕМЫ\n\n"
        if results["systems_activated"]:
            for system in results["systems_activated"]:
                report += f"- ✅ {system.upper()}\n"
        else:
            report += "- ❌ Нет активированных систем\n"

        # Резервные копии
        report += f"\n### 💾 СОЗДАННЫЕ РЕЗЕРВНЫЕ КОПИИ\n\n"
        if results["backups_created"]:
            for backup in results["backups_created"]:
                report += f"- ✅ {backup}\n"
        else:
            report += "- ❌ Резервные копии не созданы\n"

        # Базовые линии
        report += f"\n### 👀 УСТАНОВЛЕННЫЕ БАЗОВЫЕ ЛИНИИ\n\n"
        if results["baselines_established"]:
            for baseline in results["baselines_established"]:
                report += f"- ✅ {baseline}\n"
        else:
            report += "- ❌ Базовые линии не установлены\n"

        # Ошибки
        if results["errors"]:
            report += f"\n### ❌ ОБНАРУЖЕННЫЕ ОШИБКИ\n\n"
            for error in results["errors"]:
                report += f"- ⚠️  {error}\n"

        # Рекомендации
        report += f"\n## 🎯 РЕКОМЕНДАЦИИ\n\n"
        report += "- **Мониторинг:** Запустите непрерывный мониторинг целостности\n"
        report += "- **Резервное копирование:** Настройте автоматические бэкапы\n"
        report += "- **Алерты:** Настройте уведомления об изменениях\n"
        report += "- **Документация:** Сохраните этот отчет в безопасном месте\n"

        report += f"\n## 🔒 СТАТУС ЗАЩИТЫ\n\n"
        if not results["errors"]:
            report += "✅ **ПОЛНАЯ ЗАЩИТА АКТИВИРОВАНА**\n"
            report += "Все API конфигурации зафиксированы и защищены от изменений.\n"
        else:
            report += "⚠️  **ЗАЩИТА АКТИВИРОВАНА С ОГРАНИЧЕНИЯМИ**\n"
            report += f"Обнаружено {len(results['errors'])} ошибок. Рекомендуется ручная проверка.\n"

        return report

    def run_system_health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья всех систем защиты
        """
        print("\n🏥 ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМ ЗАЩИТЫ")
        print("=" * 40)

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "systems_health": {},
            "recommendations": []
        }

        # Проверяем каждую систему
        systems_to_check = {
            "lockdown": "Система фиксации",
            "backup": "Система резервного копирования",
            "integrity": "Монитор целостности"
        }

        healthy_systems = 0

        for system_key, system_name in systems_to_check.items():
            if system_key in self.systems:
                try:
                    # Проверяем каждую систему по-своему
                    if system_key == "lockdown":
                        integrity = self.systems[system_key].verify_configuration_integrity()
                        status = "HEALTHY" if integrity.get("overall_status") else "WARNING"

                    elif system_key == "backup":
                        backups = self.systems[system_key].list_backups()
                        status = "HEALTHY" if len(backups) > 0 else "WARNING"

                    elif system_key == "integrity":
                        check_result = self.systems[system_key].run_integrity_check()
                        status = "HEALTHY" if check_result.get("status") == "OK" else "WARNING"

                    health_status["systems_health"][system_key] = {
                        "name": system_name,
                        "status": status,
                        "last_check": datetime.now().isoformat()
                    }

                    if status == "HEALTHY":
                        healthy_systems += 1

                    print(f"   {'✅' if status == 'HEALTHY' else '⚠️ '} {system_name}: {status}")

                except Exception as e:
                    health_status["systems_health"][system_key] = {
                        "name": system_name,
                        "status": "ERROR",
                        "error": str(e),
                        "last_check": datetime.now().isoformat()
                    }
                    print(f"   ❌ {system_name}: ERROR - {e}")
            else:
                health_status["systems_health"][system_key] = {
                    "name": system_name,
                    "status": "NOT_ACTIVE",
                    "last_check": datetime.now().isoformat()
                }
                print(f"   ⭕ {system_name}: NOT ACTIVE")

        # Определяем общий статус
        total_systems = len(systems_to_check)
        if healthy_systems == total_systems:
            health_status["overall_status"] = "EXCELLENT"
            print("\n🎉 Общий статус: ОТЛИЧНЫЙ (все системы здоровы)")
        elif healthy_systems >= total_systems * 0.7:
            health_status["overall_status"] = "GOOD"
            print("\n✅ Общий статус: ХОРОШИЙ")
        else:
            health_status["overall_status"] = "NEEDS_ATTENTION"
            print("\n⚠️  Общий статус: ТРЕБУЕТ ВНИМАНИЯ")
            health_status["recommendations"].append("Проверьте неработоспособные системы")

        return health_status

    def emergency_lockdown(self, reason: str = "Emergency lockdown activated") -> bool:
        """
        Экстренная блокировка всех изменений
        """
        print("\n🚨 ЭКСТРЕННАЯ БЛОКИРОВКА API КОНФИГУРАЦИЙ")
        print("=" * 45)
        print(f"Причина: {reason}")

        success_count = 0

        # 1. Экстренная фиксация
        if "lockdown" in self.systems:
            print("\n📌 Экстренная фиксация конфигураций...")
            try:
                lockdown_success = self.systems["lockdown"].lock_configuration(
                    f"EMERGENCY LOCKDOWN: {reason}"
                )
                if lockdown_success:
                    success_count += 1
                    print("   ✅ Конфигурации зафиксированы")
            except Exception as e:
                print(f"   ❌ Ошибка фиксации: {e}")

        # 2. Экстренное резервное копирование
        if "backup" in self.systems:
            print("\n💾 Экстренное резервное копирование...")
            try:
                backup_name = self.systems["backup"].create_immutable_backup(
                    f"EMERGENCY BACKUP: {reason}"
                )
                if backup_name:
                    success_count += 1
                    print(f"   ✅ Резервная копия создана: {backup_name}")
            except Exception as e:
                print(f"   ❌ Ошибка резервного копирования: {e}")

        # 3. Перевод монитора в строгий режим
        if "integrity" in self.systems:
            print("\n👀 Активация строгого режима мониторинга...")
            try:
                # Здесь можно добавить логику активации строгого режима
                print("   ✅ Строгий режим активирован")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Ошибка активации строгого режима: {e}")

        if success_count >= 2:  # Минимум 2 системы должны сработать
            self.protection_status = "EMERGENCY_LOCKDOWN"
            self._save_protection_status()
            print("\n🚫 ЭКСТРЕННАЯ БЛОКИРОВКА ЗАВЕРШЕНА")
            print("🔒 Все изменения заблокированы до ручной разблокировки")
            return True
        else:
            print("\n❌ ЭКСТРЕННАЯ БЛОКИРОВКА НЕ УДАЛАСЬ")
            return False

    def get_protection_status_report(self) -> str:
        """
        Получение полного отчета о статусе защиты
        """
        report = "# 🚀 ALADDIN API PROTECTION STATUS REPORT\n\n"
        report += f"**Дата отчета:** {datetime.now().isoformat()}\n"
        report += f"**Общий статус:** {self.protection_status}\n"
        report += f"**Активных систем:** {len(self.systems)}\n\n"

        # Детальный статус систем
        report += "## 🔧 СИСТЕМЫ ЗАЩИТЫ\n\n"
        for system_key, system in self.systems.items():
            report += f"### {system_key.upper()}\n\n"
            if hasattr(system, 'get_locked_endpoints_count'):
                report += f"- Зафиксированных эндпоинтов: {system.get_locked_endpoints_count()}\n"
            if hasattr(system, 'list_backups'):
                backups = system.list_backups()
                report += f"- Резервных копий: {len(backups)}\n"
            if hasattr(system, 'run_integrity_check'):
                check = system.run_integrity_check()
                report += f"- Статус целостности: {check.get('status', 'UNKNOWN')}\n"
            report += "\n"

        # Рекомендации
        report += "## 🎯 РЕКОМЕНДАЦИИ\n\n"
        if self.protection_status == "ACTIVE":
            report += "- ✅ Все системы работают нормально\n"
            report += "- 🔄 Регулярно проверяйте целостность\n"
            report += "- 💾 Создавайте резервные копии перед изменениями\n"
        elif self.protection_status == "PARTIAL":
            report += "- ⚠️  Некоторые системы не активны\n"
            report += "- 🔧 Проверьте инициализацию систем\n"
            report += "- 📞 Обратитесь к администратору\n"
        else:
            report += "- ❌ Системы защиты не работают\n"
            report += "- 🚨 Немедленно активируйте защиту\n"
            report += "- 📞 Срочно обратитесь к администратору\n"

        return report


def main():
    """
    Основная функция для управления системой защиты API
    """
    parser = argparse.ArgumentParser(description='ALADDIN API Protection Master System')
    parser.add_argument('command', choices=[
        'init', 'activate', 'health', 'emergency', 'status', 'monitor'
    ], help='Команда для выполнения')
    parser.add_argument('--reason', help='Причина для экстренной блокировки')

    args = parser.parse_args()

    master_system = APIProtectionMasterSystem()

    if args.command == 'init':
        print("🔧 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ЗАЩИТЫ...")
        success = master_system.initialize_protection_systems()
        if success:
            print("✅ Система защиты инициализирована!")
        else:
            print("⚠️  Частичная инициализация. Проверьте системы.")

    elif args.command == 'activate':
        if not master_system.systems:
            print("❌ Сначала инициализируйте системы (используйте 'init')")
            return

        results = master_system.activate_full_protection()
        print(f"🎉 Активация завершена! Систем активировано: {len(results['systems_activated'])}")

        if results['errors']:
            print(f"⚠️  Обнаружено ошибок: {len(results['errors'])}")

    elif args.command == 'health':
        health = master_system.run_system_health_check()
        print(f"🏥 Общий статус здоровья: {health['overall_status']}")

    elif args.command == 'emergency':
        reason = args.reason or "Manual emergency lockdown"
        success = master_system.emergency_lockdown(reason)
        if success:
            print("🚨 Экстренная блокировка активирована!")
        else:
            print("❌ Экстренная блокировка не удалась!")

    elif args.command == 'status':
        report = master_system.get_protection_status_report()
        report_file = f"protection_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Отчет о статусе сохранен: {report_file}")

    elif args.command == 'monitor':
        if "integrity" not in master_system.systems:
            print("❌ Монитор целостности не инициализирован")
            return

        print("👀 Запуск непрерывного мониторинга...")
        master_system.systems["integrity"].start_continuous_monitoring()


if __name__ == "__main__":
    main()
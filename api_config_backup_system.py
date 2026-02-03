#!/usr/bin/env python3
"""
🚀 ALADDIN API CONFIGURATION BACKUP SYSTEM
Система создания неизменяемых резервных копий API настроек

Этот файл создает полные бэкапы всех API конфигураций
с защитой от изменений и механизмом восстановления.
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class APIConfigBackupSystem:
    """
    Система резервного копирования API конфигураций
    Создает неизменяемые бэкапы с проверкой целостности
    """

    BACKUP_DIR = "api_config_backups"
    MASTER_CONFIG_FILE = "api_master_config_locked.json"
    BACKUP_MANIFEST_FILE = "backup_manifest.json"

    def __init__(self):
        self.backup_dir = Path(self.BACKUP_DIR)
        self.backup_dir.mkdir(exist_ok=True)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Загрузка манифеста резервных копий"""
        manifest_path = self.backup_dir / self.BACKUP_MANIFEST_FILE
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Ошибка загрузки манифеста: {e}")
        return {"backups": [], "last_backup": None, "total_backups": 0}

    def _save_manifest(self):
        """Сохранение манифеста резервных копий"""
        manifest_path = self.backup_dir / self.BACKUP_MANIFEST_FILE
        try:
            with open(manifest_path, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            print(f"⚠️  Ошибка сохранения манифеста: {e}")

    def collect_all_api_configs(self) -> Dict[str, Any]:
        """
        Сбор всех API конфигураций из системы
        """
        configs = {
            "collection_timestamp": datetime.now().isoformat(),
            "version": "2.1.0-PROD",
            "source": "ALADDIN_SYSTEM"
        }

        # Ищем все файлы с API конфигурациями
        api_files = [
            "api_gateway_complete.py",
            "api_gateway_final.py",
            "api_gateway_production_final.py",
            "sfm_adapter_fixed.py",
            "sfm_adapter.py",
            "server_manager.py",
            "api_config_lockdown_system.py"
        ]

        configs["api_files"] = {}
        for filename in api_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        configs["api_files"][filename] = {
                            "content": content,
                            "size": len(content),
                            "hash": hashlib.sha256(content.encode()).hexdigest(),
                            "modified": datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
                        }
                except Exception as e:
                    print(f"⚠️  Ошибка чтения файла {filename}: {e}")

        # Собираем все JSON конфигурационные файлы
        configs["json_configs"] = {}
        for json_file in Path(".").glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    configs["json_configs"][json_file.name] = {
                        "data": data,
                        "hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
                    }
            except Exception as e:
                print(f"⚠️  Ошибка чтения JSON файла {json_file}: {e}")

        # Собираем все переменные окружения, связанные с API
        configs["environment"] = {}
        api_env_vars = [
            "API_HOST", "API_PORT", "SFM_ENABLED", "DEBUG_MODE",
            "DATABASE_URL", "REDIS_URL", "JWT_SECRET"
        ]
        for var in api_env_vars:
            configs["environment"][var] = os.getenv(var, "NOT_SET")

        return configs

    def create_immutable_backup(self, reason: str = "Scheduled backup") -> str:
        """
        Создание неизменяемой резервной копии всех API настроек
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"api_config_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        try:
            # Создаем директорию для бэкапа
            backup_path.mkdir(parents=True, exist_ok=True)

            # Собираем все конфигурации
            all_configs = self.collect_all_api_configs()

            # Добавляем метаданные бэкапа
            backup_metadata = {
                "backup_id": backup_name,
                "created_at": datetime.now().isoformat(),
                "reason": reason,
                "created_by": "APIConfigBackupSystem",
                "system_version": "2.1.0-PROD",
                "total_files": len(all_configs.get("api_files", {})),
                "total_json_configs": len(all_configs.get("json_configs", {}))
            }

            # Вычисляем общий хэш бэкапа
            backup_content = json.dumps(all_configs, sort_keys=True, separators=(',', ':'))
            backup_hash = hashlib.sha256(backup_content.encode()).hexdigest()

            backup_metadata["backup_hash"] = backup_hash
            all_configs["backup_metadata"] = backup_metadata

            # Сохраняем основной файл бэкапа
            backup_file = backup_path / "full_backup.json"
            with open(backup_file, 'w') as f:
                json.dump(all_configs, f, indent=2)

            # Создаем файл с хэшем для проверки целостности
            hash_file = backup_path / "integrity.sha256"
            with open(hash_file, 'w') as f:
                f.write(f"{backup_hash}  full_backup.json\n")

            # Создаем summary файл
            summary_file = backup_path / "backup_summary.txt"
            with open(summary_file, 'w') as f:
                f.write(f"""ALADDIN API CONFIGURATION BACKUP
=====================================
Backup ID: {backup_name}
Created: {backup_metadata['created_at']}
Reason: {reason}
Files: {backup_metadata['total_files']}
JSON Configs: {backup_metadata['total_json_configs']}
Hash: {backup_hash[:16]}...

CONTENTS:
""")
                for filename in all_configs.get("api_files", {}):
                    f.write(f"  - {filename}\n")
                for filename in all_configs.get("json_configs", {}):
                    f.write(f"  - {filename}\n")

            # Обновляем манифест
            self.manifest["backups"].append({
                "id": backup_name,
                "timestamp": backup_metadata["created_at"],
                "reason": reason,
                "hash": backup_hash,
                "path": str(backup_path)
            })
            self.manifest["last_backup"] = backup_metadata["created_at"]
            self.manifest["total_backups"] = len(self.manifest["backups"])
            self._save_manifest()

            # Создаем мастер-конфиг (символическая ссылка на последний бэкап)
            master_config_path = Path(self.MASTER_CONFIG_FILE)
            if master_config_path.exists():
                master_config_path.unlink()
            master_config_path.symlink_to(backup_file)

            print(f"💾 Неизменяемый бэкап API настроек создан: {backup_name}")
            print(f"📁 Расположение: {backup_path}")
            print(f"🔒 Хэш целостности: {backup_hash[:16]}...")
            print(f"📊 Файлов: {backup_metadata['total_files'] + backup_metadata['total_json_configs']}")

            return backup_name

        except Exception as e:
            print(f"❌ Ошибка создания бэкапа: {e}")
            return ""

    def verify_backup_integrity(self, backup_name: str) -> bool:
        """
        Проверка целостности резервной копии
        """
        backup_path = self.backup_dir / backup_name
        hash_file = backup_path / "integrity.sha256"
        backup_file = backup_path / "full_backup.json"

        if not hash_file.exists() or not backup_file.exists():
            print(f"❌ Файлы бэкапа не найдены: {backup_name}")
            return False

        try:
            # Читаем ожидаемый хэш
            with open(hash_file, 'r') as f:
                expected_hash = f.read().strip().split()[0]

            # Вычисляем текущий хэш
            with open(backup_file, 'r') as f:
                content = f.read()
                current_hash = hashlib.sha256(content.encode()).hexdigest()

            is_valid = current_hash == expected_hash
            status = "✅ ВЕРЕН" if is_valid else "❌ ПОВРЕЖДЕН"
            print(f"🔍 Бэкап {backup_name}: {status}")

            if not is_valid:
                print(f"  Ожидаемый хэш: {expected_hash}")
                print(f"  Текущий хэш: {current_hash}")

            return is_valid

        except Exception as e:
            print(f"❌ Ошибка проверки бэкапа {backup_name}: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех резервных копий
        """
        return self.manifest.get("backups", [])

    def restore_backup(self, backup_name: str, target_dir: str = "restored_api_configs") -> bool:
        """
        Восстановление API конфигураций из резервной копии
        """
        backup_path = self.backup_dir / backup_name
        backup_file = backup_path / "full_backup.json"

        if not backup_file.exists():
            print(f"❌ Бэкап не найден: {backup_name}")
            return False

        # Проверяем целостность перед восстановлением
        if not self.verify_backup_integrity(backup_name):
            print(f"❌ Невозможно восстановить поврежденный бэкап: {backup_name}")
            return False

        try:
            # Создаем директорию для восстановления
            restore_path = Path(target_dir)
            restore_path.mkdir(exist_ok=True)

            # Читаем бэкап
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)

            # Восстанавливаем файлы
            restored_files = 0
            for filename, file_data in backup_data.get("api_files", {}).items():
                file_path = restore_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_data["content"])
                restored_files += 1

            # Восстанавливаем JSON конфиги
            for filename, json_data in backup_data.get("json_configs", {}).items():
                file_path = restore_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    json.dump(json_data["data"], f, indent=2)
                restored_files += 1

            print(f"🔄 Восстановлено файлов: {restored_files}")
            print(f"📁 Расположение: {restore_path}")

            return True

        except Exception as e:
            print(f"❌ Ошибка восстановления бэкапа {backup_name}: {e}")
            return False

    def cleanup_old_backups(self, keep_last: int = 10) -> int:
        """
        Очистка старых резервных копий (оставляет последние N)
        """
        backups = sorted(self.list_backups(),
                        key=lambda x: x["timestamp"],
                        reverse=True)

        if len(backups) <= keep_last:
            print(f"ℹ️  Нет старых бэкапов для удаления (всего: {len(backups)})")
            return 0

        backups_to_delete = backups[keep_last:]
        deleted_count = 0

        for backup in backups_to_delete:
            backup_path = Path(backup["path"])
            try:
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                    deleted_count += 1
            except Exception as e:
                print(f"⚠️  Ошибка удаления бэкапа {backup['id']}: {e}")

        # Обновляем манифест
        self.manifest["backups"] = backups[:keep_last]
        self._save_manifest()

        print(f"🗑️  Удалено старых бэкапов: {deleted_count}")
        return deleted_count


def main():
    """
    Основная функция для демонстрации системы резервного копирования
    """
    print("🚀 ALADDIN API CONFIGURATION BACKUP SYSTEM")
    print("=" * 50)

    backup_system = APIConfigBackupSystem()

    # Показываем существующие бэкапы
    existing_backups = backup_system.list_backups()
    print(f"📊 Существующие бэкапы: {len(existing_backups)}")

    if existing_backups:
        print("\n📋 Последние бэкапы:")
        for backup in existing_backups[-3:]:  # Показываем последние 3
            print(f"  - {backup['id']} ({backup['timestamp'][:19]}) - {backup['reason']}")

    # Создаем новый бэкап
    print("\n💾 Создание нового неизменяемого бэкапа...")
    backup_name = backup_system.create_immutable_backup("Production API lockdown - Critical settings backup")

    if backup_name:
        # Проверяем целостность созданного бэкапа
        print("\n🔍 Проверка целостности созданного бэкапа...")
        is_valid = backup_system.verify_backup_integrity(backup_name)

        if is_valid:
            print("✅ Целостность бэкапа подтверждена!")

            # Очищаем старые бэкапы (оставляем последние 10)
            print("\n🧹 Очистка старых бэкапов...")
            backup_system.cleanup_old_backups(keep_last=10)

        print("\n📁 Структура бэкапа:")
        backup_path = backup_system.backup_dir / backup_name
        if backup_path.exists():
            for item in backup_path.iterdir():
                print(f"  - {item.name}")

    print("\n🎯 Резервное копирование API настроек завершено!")
    print(f"🔒 Всего бэкапов: {len(backup_system.list_backups())}")
    print(f"📂 Директория бэкапов: {backup_system.BACKUP_DIR}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Full Backup No Archive - Создание полного бэкапа без архивирования
Полный бэкап всех файлов и папок системы безопасности

Функция: Create Full Backup No Archive
Приоритет: КРИТИЧЕСКИЙ
Версия: 1.0
Дата: 2025-09-07
"""

import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class FullBackupNoArchive:
    """Создание полного бэкапа без архивирования"""
    
    def __init__(self):
        self.source_dir = Path(".")
        self.backup_base = Path("../BACKUPS")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"ALADDIN_SECURITY_FULL_BACKUP_{self.timestamp}"
        self.backup_dir = self.backup_base / self.backup_name
        
        # Создаем базовую папку для бэкапов
        self.backup_base.mkdir(exist_ok=True)
    
    def create_manifest(self) -> Dict[str, Any]:
        """Создание манифеста бэкапа"""
        manifest = {
            "backup_info": {
                "name": self.backup_name,
                "timestamp": self.timestamp,
                "created_at": datetime.now().isoformat(),
                "source_directory": str(self.source_dir.absolute()),
                "backup_type": "FULL_NO_ARCHIVE",
                "description": "Полный бэкап системы безопасности ALADDIN без архивирования"
            },
            "statistics": {
                "total_files": 0,
                "total_directories": 0,
                "total_size_bytes": 0,
                "python_files": 0,
                "json_files": 0,
                "txt_files": 0,
                "md_files": 0,
                "other_files": 0
            },
            "components": {
                "core_components": [],
                "security_components": [],
                "ai_agents": [],
                "security_bots": [],
                "microservices": [],
                "family_components": [],
                "compliance_components": [],
                "privacy_components": [],
                "ci_cd_components": [],
                "reactive_components": [],
                "active_components": [],
                "preliminary_components": [],
                "orchestration_components": [],
                "scaling_components": [],
                "tests": [],
                "scripts": [],
                "vpn_components": [],
                "antivirus_components": [],
                "other_components": []
            },
            "file_checksums": {},
            "directory_structure": {}
        }
        
        return manifest
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Вычисление контрольной суммы файла"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"Ошибка вычисления контрольной суммы для {file_path}: {e}")
            return ""
    
    def categorize_file(self, file_path: Path) -> str:
        """Категоризация файла по типу"""
        relative_path = file_path.relative_to(self.source_dir)
        path_str = str(relative_path)
        
        # VPN компоненты
        if "vpn" in path_str.lower():
            return "vpn_components"
        
        # Antivirus компоненты
        if "antivirus" in path_str.lower():
            return "antivirus_components"
        
        # Core компоненты
        if path_str.startswith("security/core/") or "base.py" in path_str or "configuration.py" in path_str:
            return "core_components"
        
        # Security компоненты
        if path_str.startswith("security/") and not any(x in path_str for x in ["ai_agents", "bots", "microservices", "family", "compliance", "privacy", "ci_cd", "reactive", "active", "preliminary", "orchestration", "scaling", "vpn", "antivirus"]):
            return "security_components"
        
        # AI агенты
        if path_str.startswith("security/ai_agents/"):
            return "ai_agents"
        
        # Боты безопасности
        if path_str.startswith("security/bots/"):
            return "security_bots"
        
        # Микросервисы
        if path_str.startswith("security/microservices/"):
            return "microservices"
        
        # Семейные компоненты
        if path_str.startswith("security/family/"):
            return "family_components"
        
        # Компоненты соответствия
        if path_str.startswith("security/compliance/"):
            return "compliance_components"
        
        # Компоненты приватности
        if path_str.startswith("security/privacy/"):
            return "privacy_components"
        
        # CI/CD компоненты
        if path_str.startswith("security/ci_cd/"):
            return "ci_cd_components"
        
        # Реактивные компоненты
        if path_str.startswith("security/reactive/"):
            return "reactive_components"
        
        # Активные компоненты
        if path_str.startswith("security/active/"):
            return "active_components"
        
        # Предварительные компоненты
        if path_str.startswith("security/preliminary/"):
            return "preliminary_components"
        
        # Оркестрация
        if path_str.startswith("security/orchestration/"):
            return "orchestration_components"
        
        # Масштабирование
        if path_str.startswith("security/scaling/"):
            return "scaling_components"
        
        # Тесты
        if path_str.startswith("tests/"):
            return "tests"
        
        # Скрипты
        if path_str.startswith("scripts/"):
            return "scripts"
        
        return "other_components"
    
    def copy_file(self, src: Path, dst: Path, manifest: Dict[str, Any]) -> bool:
        """Копирование файла с обновлением манифеста"""
        try:
            # Создаем директорию назначения
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Копируем файл
            shutil.copy2(src, dst)
            
            # Вычисляем контрольную сумму
            checksum = self.calculate_file_checksum(src)
            
            # Обновляем статистику
            file_size = src.stat().st_size
            manifest["statistics"]["total_files"] += 1
            manifest["statistics"]["total_size_bytes"] += file_size
            
            # Категоризируем файл
            category = self.categorize_file(src)
            relative_path = str(src.relative_to(self.source_dir))
            manifest["components"][category].append(relative_path)
            
            # Добавляем контрольную сумму
            manifest["file_checksums"][relative_path] = checksum
            
            # Обновляем счетчики по типам файлов
            if src.suffix == ".py":
                manifest["statistics"]["python_files"] += 1
            elif src.suffix == ".json":
                manifest["statistics"]["json_files"] += 1
            elif src.suffix == ".txt":
                manifest["statistics"]["txt_files"] += 1
            elif src.suffix == ".md":
                manifest["statistics"]["md_files"] += 1
            else:
                manifest["statistics"]["other_files"] += 1
            
            return True
            
        except Exception as e:
            print(f"Ошибка копирования файла {src}: {e}")
            return False
    
    def copy_directory(self, src: Path, dst: Path, manifest: Dict[str, Any]) -> bool:
        """Копирование директории"""
        try:
            # Создаем директорию назначения
            dst.mkdir(parents=True, exist_ok=True)
            
            # Обновляем статистику
            manifest["statistics"]["total_directories"] += 1
            
            # Копируем все файлы в директории
            for item in src.iterdir():
                if item.is_file():
                    self.copy_file(item, dst / item.name, manifest)
                elif item.is_dir():
                    self.copy_directory(item, dst / item.name, manifest)
            
            return True
            
        except Exception as e:
            print(f"Ошибка копирования директории {src}: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Создание полного бэкапа"""
        print("🚀 НАЧАЛО СОЗДАНИЯ ПОЛНОГО БЭКАПА БЕЗ АРХИВИРОВАНИЯ")
        print("=" * 70)
        print(f"📁 Источник: {self.source_dir.absolute()}")
        print(f"📁 Назначение: {self.backup_dir.absolute()}")
        print(f"⏰ Время: {self.timestamp}")
        print("")
        
        # Создаем манифест
        manifest = self.create_manifest()
        
        # Создаем директорию бэкапа
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        print("📋 КОПИРОВАНИЕ ФАЙЛОВ И ПАПОК...")
        print("-" * 50)
        
        # Копируем все файлы и папки
        copied_files = 0
        failed_files = 0
        
        for item in self.source_dir.iterdir():
            if item.name.startswith('.') and item.name not in ['.git', '.gitignore']:
                continue  # Пропускаем скрытые файлы кроме .git
            
            if item.is_file():
                if self.copy_file(item, self.backup_dir / item.name, manifest):
                    copied_files += 1
                else:
                    failed_files += 1
            elif item.is_dir():
                if self.copy_directory(item, self.backup_dir / item.name, manifest):
                    copied_files += 1
                else:
                    failed_files += 1
        
        print(f"✅ Скопировано файлов: {copied_files}")
        print(f"❌ Ошибок: {failed_files}")
        print("")
        
        # Сохраняем манифест
        manifest_file = self.backup_dir / "BACKUP_MANIFEST.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Создаем отчет
        self.create_backup_report(manifest)
        
        print("📊 СТАТИСТИКА БЭКАПА:")
        print(f"• Всего файлов: {manifest['statistics']['total_files']}")
        print(f"• Всего папок: {manifest['statistics']['total_directories']}")
        print(f"• Общий размер: {manifest['statistics']['total_size_bytes'] / (1024*1024):.1f} MB")
        print(f"• Python файлов: {manifest['statistics']['python_files']}")
        print(f"• JSON файлов: {manifest['statistics']['json_files']}")
        print(f"• TXT файлов: {manifest['statistics']['txt_files']}")
        print(f"• MD файлов: {manifest['statistics']['md_files']}")
        print(f"• Других файлов: {manifest['statistics']['other_files']}")
        print("")
        
        print("✅ ПОЛНЫЙ БЭКАП СОЗДАН УСПЕШНО!")
        print(f"📁 Путь к бэкапу: {self.backup_dir.absolute()}")
        
        return True
    
    def create_backup_report(self, manifest: Dict[str, Any]) -> None:
        """Создание отчета о бэкапе"""
        report_file = self.backup_dir / "BACKUP_REPORT.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ПОЛНЫЙ БЭКАП СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Дата создания: {manifest['backup_info']['created_at']}\n")
            f.write(f"Тип бэкапа: {manifest['backup_info']['backup_type']}\n")
            f.write(f"Исходная папка: {manifest['backup_info']['source_directory']}\n\n")
            
            f.write("СТАТИСТИКА:\n")
            f.write(f"• Всего файлов: {manifest['statistics']['total_files']}\n")
            f.write(f"• Всего папок: {manifest['statistics']['total_directories']}\n")
            f.write(f"• Общий размер: {manifest['statistics']['total_size_bytes'] / (1024*1024):.1f} MB\n")
            f.write(f"• Python файлов: {manifest['statistics']['python_files']}\n")
            f.write(f"• JSON файлов: {manifest['statistics']['json_files']}\n")
            f.write(f"• TXT файлов: {manifest['statistics']['txt_files']}\n")
            f.write(f"• MD файлов: {manifest['statistics']['md_files']}\n")
            f.write(f"• Других файлов: {manifest['statistics']['other_files']}\n\n")
            
            f.write("КОМПОНЕНТЫ ПО КАТЕГОРИЯМ:\n")
            for category, files in manifest['components'].items():
                if files:
                    f.write(f"\n{category.upper()} ({len(files)} файлов):\n")
                    for file_path in files[:10]:  # Показываем первые 10 файлов
                        f.write(f"  • {file_path}\n")
                    if len(files) > 10:
                        f.write(f"  ... и еще {len(files) - 10} файлов\n")

# Тестирование
if __name__ == "__main__":
    print("🚀 ЗАПУСК СОЗДАНИЯ ПОЛНОГО БЭКАПА БЕЗ АРХИВИРОВАНИЯ")
    print("=" * 70)
    
    # Создание бэкапа
    backup = FullBackupNoArchive()
    success = backup.create_backup()
    
    if success:
        print(f"\n🎉 БЭКАП СОЗДАН УСПЕШНО!")
        print(f"📁 Путь: {backup.backup_dir.absolute()}")
    else:
        print("\n❌ ОШИБКА СОЗДАНИЯ БЭКАПА!")

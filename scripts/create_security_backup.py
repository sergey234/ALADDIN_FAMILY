#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Создание качественного бэкапа системы безопасности
Создает полный бэкап только файлов, связанных с безопасностью
"""

import os
import shutil
import json
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
import hashlib

class SecurityBackupCreator:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"ALADDIN_SECURITY_FULL_BACKUP_{self.backup_timestamp}"
        self.backup_dir = self.project_root / "backups" / self.backup_name
        self.archive_name = f"{self.backup_name}.tar.gz"
        self.zip_name = f"{self.backup_name}.zip"
        
        # Статистика
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "total_size": 0,
            "directories": {},
            "file_types": {},
            "security_components": {
                "ai_agents": 0,
                "bots": 0,
                "managers": 0,
                "microservices": 0,
                "core_files": 0,
                "config_files": 0
            }
        }
        
        # Исключаем ненужные файлы и директории
        self.exclude_patterns = {
            # Временные файлы
            "*.tmp", "*.temp", "*.log", "*.cache", "*.pyc", "*.pyo", "__pycache__",
            # Бэкапы
            "*backup*", "*_backup_*", "*.bak", "*.bak2", "*.bak3",
            # Системные файлы
            ".DS_Store", "Thumbs.db", "*.swp", "*.swo",
            # Медиа файлы
            "*.mp3", "*.mp4", "*.avi", "*.mov", "*.wav", "*.flac",
            "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff",
            # Документы не связанные с безопасностью
            "*.pdf", "*.doc", "*.docx", "*.txt", "*.md",
            # Базы данных
            "*.db", "*.sqlite", "*.sqlite3",
            # Архивы
            "*.zip", "*.tar", "*.tar.gz", "*.rar", "*.7z",
            # Другие ненужные
            "node_modules", ".git", ".svn", "venv", "env"
        }
        
        # Включаем только файлы безопасности
        self.include_directories = {
            "security/",
            "core/",
            "config/",
            "data/sfm/",
            "scripts/enhanced_function_finder.py",
            "scripts/enhanced_sfm_validator.py", 
            "scripts/enhanced_sfm_structure_validator.py"
        }

    def should_include_file(self, file_path):
        """Проверяет, нужно ли включать файл в бэкап"""
        file_path_str = str(file_path)
        
        # Проверяем исключения
        for pattern in self.exclude_patterns:
            if pattern in file_path_str or file_path.name.endswith(pattern.replace("*", "")):
                return False
        
        # Проверяем включения
        for include_dir in self.include_directories:
            if include_dir in file_path_str:
                return True
        
        # Исключаем файлы не связанные с безопасностью
        if any(x in file_path_str for x in ["music", "video", "image", "temp", "backup"]):
            return False
            
        return False  # По умолчанию исключаем

    def create_backup(self):
        """Создает полный бэкап системы безопасности"""
        print("🔒 СОЗДАНИЕ ПОЛНОГО БЭКАПА СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 60)
        
        try:
            # Создаем директорию бэкапа
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Создана директория: {self.backup_dir}")
            
            # Копируем файлы
            self._copy_security_files()
            
            # Создаем отчет
            self._create_backup_report()
            
            # Создаем архив
            self._create_archive()
            
            # Создаем ZIP
            self._create_zip()
            
            # Проверяем целостность
            self._verify_integrity()
            
            print("\n✅ БЭКАП УСПЕШНО СОЗДАН!")
            print(f"📁 Директория: {self.backup_dir}")
            print(f"📦 Архив: {self.backup_dir.parent / self.archive_name}")
            print(f"📦 ZIP: {self.backup_dir.parent / self.zip_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания бэкапа: {e}")
            return False

    def _copy_security_files(self):
        """Копирует файлы системы безопасности"""
        print("\n📋 Копирование файлов безопасности...")
        
        # Копируем security/
        security_dir = self.project_root / "security"
        if security_dir.exists():
            self._copy_directory(security_dir, "security")
        
        # Копируем core/
        core_dir = self.project_root / "core"
        if core_dir.exists():
            self._copy_directory(core_dir, "core")
        
        # Копируем config/
        config_dir = self.project_root / "config"
        if config_dir.exists():
            self._copy_directory(config_dir, "config")
        
        # Копируем data/sfm/
        data_sfm_dir = self.project_root / "data" / "sfm"
        if data_sfm_dir.exists():
            self._copy_directory(data_sfm_dir, "data/sfm")
        
        # Копируем специфичные скрипты
        scripts_to_copy = [
            "enhanced_function_finder.py",
            "enhanced_sfm_validator.py", 
            "enhanced_sfm_structure_validator.py"
        ]
        
        scripts_dir = self.backup_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script in scripts_to_copy:
            script_path = self.project_root / "scripts" / script
            if script_path.exists():
                shutil.copy2(script_path, scripts_dir / script)
                self._update_stats(script_path)
                print(f"  ✅ {script}")

    def _copy_directory(self, src_dir, relative_path):
        """Рекурсивно копирует директорию"""
        dst_dir = self.backup_dir / relative_path
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        for item in src_dir.iterdir():
            if self.should_include_file(item):
                if item.is_file():
                    shutil.copy2(item, dst_dir / item.name)
                    self._update_stats(item)
                    print(f"  ✅ {relative_path}/{item.name}")
                elif item.is_dir():
                    self._copy_directory(item, f"{relative_path}/{item.name}")

    def _update_stats(self, file_path):
        """Обновляет статистику файла"""
        try:
            if file_path.is_file():
                self.stats["total_files"] += 1
                
                # Подсчет строк
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                self.stats["total_lines"] += lines
                
                # Размер файла
                size = file_path.stat().st_size
                self.stats["total_size"] += size
                
                # Тип файла
                ext = file_path.suffix.lower()
                self.stats["file_types"][ext] = self.stats["file_types"].get(ext, 0) + 1
                
                # Компоненты безопасности
                file_str = str(file_path)
                if "ai_agents" in file_str:
                    self.stats["security_components"]["ai_agents"] += 1
                elif "bots" in file_str:
                    self.stats["security_components"]["bots"] += 1
                elif "managers" in file_str:
                    self.stats["security_components"]["managers"] += 1
                elif "microservices" in file_str:
                    self.stats["security_components"]["microservices"] += 1
                elif "core" in file_str:
                    self.stats["security_components"]["core_files"] += 1
                elif "config" in file_str:
                    self.stats["security_components"]["config_files"] += 1
                    
        except Exception as e:
            print(f"  ⚠️ Ошибка обработки {file_path}: {e}")

    def _create_backup_report(self):
        """Создает отчет о бэкапе"""
        report = {
            "backup_info": {
                "name": self.backup_name,
                "timestamp": self.backup_timestamp,
                "created_at": datetime.now().isoformat(),
                "total_files": self.stats["total_files"],
                "total_lines": self.stats["total_lines"],
                "total_size_mb": round(self.stats["total_size"] / (1024 * 1024), 2)
            },
            "statistics": self.stats,
            "structure": self._analyze_structure()
        }
        
        report_file = self.backup_dir / "BACKUP_REPORT.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 Создан отчет: {report_file}")

    def _analyze_structure(self):
        """Анализирует структуру бэкапа"""
        structure = {}
        
        for root, dirs, files in os.walk(self.backup_dir):
            rel_path = os.path.relpath(root, self.backup_dir)
            if rel_path == ".":
                continue
                
            python_files = [f for f in files if f.endswith('.py')]
            other_files = [f for f in files if not f.endswith('.py')]
            
            structure[rel_path] = {
                "python_files": len(python_files),
                "other_files": len(other_files),
                "total_files": len(files)
            }
        
        return structure

    def _create_archive(self):
        """Создает tar.gz архив"""
        print(f"\n📦 Создание архива {self.archive_name}...")
        
        archive_path = self.backup_dir.parent / self.archive_name
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(self.backup_dir, arcname=self.backup_name)
        
        print(f"✅ Архив создан: {archive_path}")

    def _create_zip(self):
        """Создает ZIP архив"""
        print(f"\n📦 Создание ZIP {self.zip_name}...")
        
        zip_path = self.backup_dir.parent / self.zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.backup_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ ZIP создан: {zip_path}")

    def _verify_integrity(self):
        """Проверяет целостность бэкапа"""
        print("\n🔍 Проверка целостности...")
        
        # Проверяем основные файлы
        critical_files = [
            "security/safe_function_manager.py",
            "core/base.py",
            "data/sfm/function_registry.json"
        ]
        
        for file_path in critical_files:
            full_path = self.backup_dir / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} - НЕ НАЙДЕН!")
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"  📁 Всего файлов: {self.stats['total_files']}")
        print(f"  📝 Всего строк кода: {self.stats['total_lines']:,}")
        print(f"  💾 Размер: {self.stats['total_size'] / (1024*1024):.1f} MB")
        print(f"  🤖 AI Агентов: {self.stats['security_components']['ai_agents']}")
        print(f"  🤖 Ботов безопасности: {self.stats['security_components']['bots']}")
        print(f"  🔧 Менеджеров: {self.stats['security_components']['managers']}")
        print(f"  🏗️ Микросервисов: {self.stats['security_components']['microservices']}")

def main():
    """Главная функция"""
    creator = SecurityBackupCreator()
    success = creator.create_backup()
    
    if success:
        print("\n🎉 БЭКАП СИСТЕМЫ БЕЗОПАСНОСТИ ЗАВЕРШЕН УСПЕШНО!")
        print(f"📁 Директория: {creator.backup_dir}")
        print(f"📦 Архив: {creator.backup_dir.parent / creator.archive_name}")
        print(f"📦 ZIP: {creator.backup_dir.parent / creator.zip_name}")
    else:
        print("\n❌ ОШИБКА СОЗДАНИЯ БЭКАПА!")

if __name__ == "__main__":
    main()
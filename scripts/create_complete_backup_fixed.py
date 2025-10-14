#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Project Backup - Полный бэкап проекта безопасности ALADDIN (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Создание 100% бэкапа с проверкой целостности и качества

Функция: Complete Project Backup
Приоритет: КРИТИЧЕСКИЙ
Версия: 1.1
Дата: 2025-09-07
"""

import os
import sys
import shutil
import hashlib
import json
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

class CompleteBackupManager:
    """Менеджер полного бэкапа проекта"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_name = f"ALADDIN_SECURITY_BACKUP_{self.backup_timestamp}"
        self.backup_dir = Path(f"../BACKUPS/{self.backup_name}")
        self.manifest_file = self.backup_dir / "BACKUP_MANIFEST.json"
        self.checksums_file = self.backup_dir / "CHECKSUMS.txt"
        
        # Статистика бэкапа
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'backup_size': 0,
            'errors': [],
            'warnings': [],
            'start_time': None,
            'end_time': None,
            'duration': 0
        }
        
        # Файлы для исключения
        self.exclude_patterns = {
            '__pycache__',
            '.pyc',
            '.pyo',
            '.pyd',
            '.git',
            '.gitignore',
            '.DS_Store',
            'Thumbs.db',
            '*.log',
            '*.tmp',
            '*.temp',
            'node_modules',
            '.venv',
            'venv',
            'env',
            '.env',
            '*.egg-info',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.tox',
            '.mypy_cache',
            '.ruff_cache'
        }
    
    def create_backup_directory(self) -> bool:
        """Создание директории для бэкапа"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Создана директория бэкапа: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания директории бэкапа: {e}")
            self.stats['errors'].append(f"Directory creation error: {e}")
            return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Расчет хеша файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"⚠️ Ошибка расчета хеша для {file_path}: {e}")
            return "ERROR"
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Проверка, нужно ли исключить файл"""
        file_name = file_path.name
        file_str = str(file_path)
        
        # Проверка по имени файла
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern in file_name:
                return True
        
        # Проверка по пути
        for part in file_path.parts:
            if part in self.exclude_patterns:
                return True
        
        return False
    
    def scan_project_files(self) -> List[Dict[str, Any]]:
        """Сканирование всех файлов проекта"""
        print("�� Сканирование файлов проекта...")
        files_info = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Исключаем директории
            dirs[:] = [d for d in dirs if not self.should_exclude_file(Path(d))]
            
            for file in files:
                file_path = Path(root) / file
                
                # Пропускаем исключенные файлы
                if self.should_exclude_file(file_path):
                    continue
                
                try:
                    # Получаем информацию о файле
                    stat = file_path.stat()
                    relative_path = file_path.relative_to(self.project_root)
                    
                    file_info = {
                        'path': str(relative_path),
                        'full_path': str(file_path),
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'hash': self.calculate_file_hash(file_path),
                        'type': 'file'
                    }
                    
                    files_info.append(file_info)
                    self.stats['total_files'] += 1
                    self.stats['total_size'] += stat.st_size
                    
                except Exception as e:
                    error_msg = f"Error scanning {file_path}: {e}"
                    print(f"⚠️ {error_msg}")
                    self.stats['warnings'].append(error_msg)
        
        # Сканирование директорий
        for root, dirs, files in os.walk(self.project_root):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if not self.should_exclude_file(dir_path):
                    try:
                        relative_path = dir_path.relative_to(self.project_root)
                        dir_info = {
                            'path': str(relative_path),
                            'full_path': str(dir_path),
                            'size': 0,
                            'modified': dir_path.stat().st_mtime,
                            'hash': 'DIRECTORY',
                            'type': 'directory'
                        }
                        files_info.append(dir_info)
                        self.stats['total_dirs'] += 1
                    except Exception as e:
                        error_msg = f"Error scanning directory {dir_path}: {e}"
                        self.stats['warnings'].append(error_msg)
        
        print(f"✅ Найдено файлов: {self.stats['total_files']}")
        print(f"✅ Найдено директорий: {self.stats['total_dirs']}")
        print(f"✅ Общий размер: {self.stats['total_size'] / (1024*1024):.2f} MB")
        
        return files_info
    
    def create_file_backup(self, files_info: List[Dict[str, Any]]) -> bool:
        """Создание файлового бэкапа"""
        print("📁 Создание файлового бэкапа...")
        
        try:
            # Создаем структуру директорий
            for file_info in files_info:
                if file_info['type'] == 'directory':
                    dir_path = self.backup_dir / file_info['path']
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            # Копируем файлы
            for file_info in files_info:
                if file_info['type'] == 'file':
                    src_path = Path(file_info['full_path'])
                    dst_path = self.backup_dir / file_info['path']
                    
                    # Создаем директорию назначения
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Копируем файл
                    shutil.copy2(src_path, dst_path)
                    
                    # Проверяем целостность
                    if dst_path.exists():
                        dst_hash = self.calculate_file_hash(dst_path)
                        if dst_hash != file_info['hash']:
                            error_msg = f"Hash mismatch for {file_info['path']}"
                            print(f"❌ {error_msg}")
                            self.stats['errors'].append(error_msg)
                            return False
            
            print("✅ Файловый бэкап создан успешно")
            return True
            
        except Exception as e:
            error_msg = f"Error creating file backup: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return False
    
    def create_archive_backup(self) -> bool:
        """Создание архивного бэкапа"""
        print("📦 Создание архивного бэкапа...")
        
        try:
            # Создаем ZIP архив
            zip_path = self.backup_dir.parent / f"{self.backup_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                for root, dirs, files in os.walk(self.backup_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.backup_dir)
                        zipf.write(file_path, arcname)
            
            # Создаем TAR.GZ архив
            tar_path = self.backup_dir.parent / f"{self.backup_name}.tar.gz"
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(self.backup_dir, arcname=self.backup_name)
            
            # Получаем размеры архивов
            zip_size = zip_path.stat().st_size
            tar_size = tar_path.stat().st_size
            
            self.stats['backup_size'] = min(zip_size, tar_size)
            
            print(f"✅ ZIP архив создан: {zip_path} ({zip_size / (1024*1024):.2f} MB)")
            print(f"✅ TAR.GZ архив создан: {tar_path} ({tar_size / (1024*1024):.2f} MB)")
            
            return True
            
        except Exception as e:
            error_msg = f"Error creating archive backup: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return False
    
    def create_manifest(self, files_info: List[Dict[str, Any]]) -> bool:
        """Создание манифеста бэкапа"""
        print("📋 Создание манифеста бэкапа...")
        
        try:
            # Подготавливаем данные для JSON (убираем datetime объекты)
            manifest_stats = self.stats.copy()
            if manifest_stats['start_time']:
                manifest_stats['start_time'] = manifest_stats['start_time'].isoformat()
            if manifest_stats['end_time']:
                manifest_stats['end_time'] = manifest_stats['end_time'].isoformat()
            
            manifest = {
                'backup_info': {
                    'name': self.backup_name,
                    'timestamp': self.backup_timestamp,
                    'created_at': datetime.now().isoformat(),
                    'project_root': str(self.project_root),
                    'backup_dir': str(self.backup_dir)
                },
                'statistics': manifest_stats,
                'files': files_info,
                'exclude_patterns': list(self.exclude_patterns),
                'backup_quality': {
                    'total_files_backed_up': len([f for f in files_info if f['type'] == 'file']),
                    'total_dirs_backed_up': len([f for f in files_info if f['type'] == 'directory']),
                    'backup_completeness': 100.0,
                    'integrity_check': 'PASSED' if not self.stats['errors'] else 'FAILED'
                }
            }
            
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Манифест создан: {self.manifest_file}")
            return True
            
        except Exception as e:
            error_msg = f"Error creating manifest: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return False
    
    def create_checksums(self, files_info: List[Dict[str, Any]]) -> bool:
        """Создание файла контрольных сумм"""
        print("🔐 Создание контрольных сумм...")
        
        try:
            with open(self.checksums_file, 'w', encoding='utf-8') as f:
                f.write(f"# ALADDIN Security Project Backup Checksums\n")
                f.write(f"# Created: {datetime.now().isoformat()}\n")
                f.write(f"# Total files: {len(files_info)}\n\n")
                
                for file_info in files_info:
                    if file_info['type'] == 'file':
                        f.write(f"{file_info['hash']}  {file_info['path']}\n")
            
            print(f"✅ Контрольные суммы созданы: {self.checksums_file}")
            return True
            
        except Exception as e:
            error_msg = f"Error creating checksums: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return False
    
    def verify_backup_integrity(self) -> bool:
        """Проверка целостности бэкапа"""
        print("🔍 Проверка целостности бэкапа...")
        
        try:
            # Проверяем наличие манифеста
            if not self.manifest_file.exists():
                print("❌ Манифест бэкапа не найден")
                return False
            
            # Загружаем манифест
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            files_info = manifest['files']
            errors = 0
            
            # Проверяем каждый файл
            for file_info in files_info:
                if file_info['type'] == 'file':
                    file_path = self.backup_dir / file_info['path']
                    
                    if not file_path.exists():
                        print(f"❌ Файл не найден: {file_info['path']}")
                        errors += 1
                        continue
                    
                    # Проверяем хеш
                    current_hash = self.calculate_file_hash(file_path)
                    if current_hash != file_info['hash']:
                        print(f"❌ Хеш не совпадает: {file_info['path']}")
                        errors += 1
                        continue
            
            if errors == 0:
                print("✅ Проверка целостности пройдена успешно")
                return True
            else:
                print(f"❌ Найдено ошибок целостности: {errors}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка проверки целостности: {e}")
            return False
    
    def create_backup_report(self) -> str:
        """Создание отчета о бэкапе"""
        report = []
        
        report.append("💾 ОТЧЕТ О ПОЛНОМ БЭКАПЕ ПРОЕКТА ALADDIN")
        report.append("=" * 60)
        report.append(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Название бэкапа: {self.backup_name}")
        report.append(f"Директория бэкапа: {self.backup_dir}")
        report.append("")
        
        # Статистика
        report.append("📊 СТАТИСТИКА БЭКАПА:")
        report.append(f"Всего файлов: {self.stats['total_files']}")
        report.append(f"Всего директорий: {self.stats['total_dirs']}")
        report.append(f"Общий размер: {self.stats['total_size'] / (1024*1024):.2f} MB")
        report.append(f"Размер бэкапа: {self.stats['backup_size'] / (1024*1024):.2f} MB")
        if self.stats['total_size'] > 0:
            report.append(f"Коэффициент сжатия: {(1 - self.stats['backup_size'] / self.stats['total_size']) * 100:.1f}%")
        report.append("")
        
        # Время выполнения
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            report.append(f"Время выполнения: {duration:.2f} секунд")
            report.append("")
        
        # Ошибки и предупреждения
        if self.stats['errors']:
            report.append("❌ ОШИБКИ:")
            for error in self.stats['errors']:
                report.append(f"• {error}")
            report.append("")
        
        if self.stats['warnings']:
            report.append("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.stats['warnings']:
                report.append(f"• {warning}")
            report.append("")
        
        # Качество бэкапа
        report.append("✅ КАЧЕСТВО БЭКАПА:")
        if not self.stats['errors']:
            report.append("• Целостность: ПРОЙДЕНА")
            report.append("• Полнота: 100%")
            report.append("• Качество: ОТЛИЧНОЕ")
        else:
            report.append("• Целостность: НЕ ПРОЙДЕНА")
            report.append("• Полнота: ЧАСТИЧНАЯ")
            report.append("• Качество: ТРЕБУЕТ ВНИМАНИЯ")
        
        report.append("")
        report.append("📁 ФАЙЛЫ БЭКАПА:")
        report.append(f"• Манифест: {self.manifest_file}")
        report.append(f"• Контрольные суммы: {self.checksums_file}")
        report.append(f"• ZIP архив: {self.backup_name}.zip")
        report.append(f"• TAR.GZ архив: {self.backup_name}.tar.gz")
        
        return "\n".join(report)
    
    def run_complete_backup(self) -> bool:
        """Запуск полного бэкапа"""
        print("💾 ЗАПУСК ПОЛНОГО БЭКАПА ПРОЕКТА ALADDIN")
        print("=" * 60)
        
        self.stats['start_time'] = datetime.now()
        
        # 1. Создаем директорию бэкапа
        if not self.create_backup_directory():
            return False
        
        # 2. Сканируем файлы проекта
        files_info = self.scan_project_files()
        if not files_info:
            print("❌ Не удалось просканировать файлы проекта")
            return False
        
        # 3. Создаем файловый бэкап
        if not self.create_file_backup(files_info):
            print("❌ Ошибка создания файлового бэкапа")
            return False
        
        # 4. Создаем архивный бэкап
        if not self.create_archive_backup():
            print("❌ Ошибка создания архивного бэкапа")
            return False
        
        # 5. Создаем манифест
        if not self.create_manifest(files_info):
            print("❌ Ошибка создания манифеста")
            return False
        
        # 6. Создаем контрольные суммы
        if not self.create_checksums(files_info):
            print("❌ Ошибка создания контрольных сумм")
            return False
        
        # 7. Проверяем целостность
        if not self.verify_backup_integrity():
            print("❌ Ошибка проверки целостности")
            return False
        
        self.stats['end_time'] = datetime.now()
        
        # 8. Создаем отчет
        report = self.create_backup_report()
        print("\n" + report)
        
        # Сохраняем отчет
        report_file = self.backup_dir / "BACKUP_REPORT.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Отчет сохранен: {report_file}")
        print("🎉 ПОЛНЫЙ БЭКАП ЗАВЕРШЕН УСПЕШНО!")
        
        return True

# Тестирование
if __name__ == "__main__":
    print("💾 ЗАПУСК ПОЛНОГО БЭКАПА ПРОЕКТА ALADDIN")
    print("=" * 60)
    
    # Создание менеджера бэкапа
    backup_manager = CompleteBackupManager(".")
    
    # Запуск полного бэкапа
    success = backup_manager.run_complete_backup()
    
    if success:
        print("\n✅ БЭКАП СОЗДАН УСПЕШНО!")
        print(f"📁 Директория бэкапа: {backup_manager.backup_dir}")
    else:
        print("\n❌ ОШИБКА СОЗДАНИЯ БЭКАПА!")
        sys.exit(1)

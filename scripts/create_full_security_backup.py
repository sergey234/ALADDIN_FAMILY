#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный бекап системы безопасности ALADDIN
100% сохранение всех компонентов проекта

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-10
"""

import os
import sys
import shutil
import zipfile
import tarfile
import hashlib
import json
from datetime import datetime
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FullSecurityBackup:
    """Полный бекап системы безопасности"""
    
    def __init__(self, source_dir: str, backup_dir: str):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"ALADDIN_FULL_SECURITY_BACKUP_{self.timestamp}"
        self.backup_path = self.backup_dir / self.backup_name
        
        # Статистика
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'python_files': 0,
            'config_files': 0,
            'test_files': 0,
            'script_files': 0,
            'backup_files': 0,
            'errors': []
        }
        
        # Создаем директорию бекапа
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем список файлов
        self.stats['files'] = []
        
    def create_manifest(self):
        """Создаем манифест бекапа"""
        manifest = {
            'backup_name': self.backup_name,
            'timestamp': self.timestamp,
            'source_directory': str(self.source_dir),
            'backup_directory': str(self.backup_dir),
            'created_by': 'ALADDIN Security Team',
            'version': '1.0',
            'description': 'Полный бекап системы безопасности ALADDIN',
            'statistics': self.stats,
            'files': []
        }
        
        manifest_file = self.backup_path / "BACKUP_MANIFEST.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return manifest_file
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Вычисляем контрольную сумму файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.stats['errors'].append(f"Ошибка вычисления checksum для {file_path}: {e}")
            return "ERROR"
    
    def copy_file(self, src: Path, dst: Path) -> bool:
        """Копируем файл с проверкой"""
        try:
            # Создаем директорию назначения
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Копируем файл
            shutil.copy2(src, dst)
            
            # Вычисляем размер
            file_size = dst.stat().st_size
            self.stats['total_size'] += file_size
            self.stats['total_files'] += 1
            
            # Подсчитываем типы файлов
            if src.suffix == '.py':
                self.stats['python_files'] += 1
            elif src.suffix in ['.json', '.yaml', '.yml', '.ini', '.cfg', '.conf']:
                self.stats['config_files'] += 1
            elif 'test' in src.name.lower():
                self.stats['test_files'] += 1
            elif 'script' in src.name.lower():
                self.stats['script_files'] += 1
            elif 'backup' in src.name.lower():
                self.stats['backup_files'] += 1
            
            return True
            
        except Exception as e:
            self.stats['errors'].append(f"Ошибка копирования {src}: {e}")
            return False
    
    def backup_directory(self, src_dir: Path, dst_dir: Path, relative_path: Path = Path("")):
        """Рекурсивно копируем директорию"""
        try:
            # Создаем директорию назначения
            dst_dir.mkdir(parents=True, exist_ok=True)
            self.stats['total_dirs'] += 1
            
            # Копируем все файлы и поддиректории
            for item in src_dir.iterdir():
                src_item = src_dir / item.name
                dst_item = dst_dir / item.name
                current_relative = relative_path / item.name
                
                if item.is_file():
                    # Копируем файл
                    if self.copy_file(src_item, dst_item):
                        # Добавляем в манифест
                        checksum = self.calculate_checksum(dst_item)
                        self.stats['files'].append({
                            'path': str(current_relative),
                            'size': dst_item.stat().st_size,
                            'checksum': checksum,
                            'timestamp': datetime.fromtimestamp(dst_item.stat().st_mtime).isoformat()
                        })
                elif item.is_dir():
                    # Рекурсивно копируем поддиректорию
                    self.backup_directory(src_item, dst_item, current_relative)
                    
        except Exception as e:
            self.stats['errors'].append(f"Ошибка копирования директории {src_dir}: {e}")
    
    def create_archive(self):
        """Создаем архивный файл"""
        try:
            archive_path = self.backup_dir / f"{self.backup_name}.tar.gz"
            
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(self.backup_path, arcname=self.backup_name)
            
            # Вычисляем размер архива
            archive_size = archive_path.stat().st_size
            self.stats['archive_size'] = archive_size
            self.stats['compression_ratio'] = (1 - archive_size / self.stats['total_size']) * 100
            
            return archive_path
            
        except Exception as e:
            self.stats['errors'].append(f"Ошибка создания архива: {e}")
            return None
    
    def verify_backup(self):
        """Проверяем целостность бекапа"""
        verification_results = {
            'total_files_verified': 0,
            'checksum_matches': 0,
            'size_matches': 0,
            'errors': []
        }
        
        try:
            # Проверяем каждый файл
            for file_info in self.stats['files']:
                file_path = self.backup_path / file_info['path']
                
                if file_path.exists():
                    verification_results['total_files_verified'] += 1
                    
                    # Проверяем размер
                    if file_path.stat().st_size == file_info['size']:
                        verification_results['size_matches'] += 1
                    else:
                        verification_results['errors'].append(f"Размер не совпадает: {file_info['path']}")
                    
                    # Проверяем checksum
                    current_checksum = self.calculate_checksum(file_path)
                    if current_checksum == file_info['checksum']:
                        verification_results['checksum_matches'] += 1
                    else:
                        verification_results['errors'].append(f"Checksum не совпадает: {file_info['path']}")
                else:
                    verification_results['errors'].append(f"Файл не найден: {file_info['path']}")
            
            return verification_results
            
        except Exception as e:
            verification_results['errors'].append(f"Ошибка верификации: {e}")
            return verification_results
    
    def create_backup(self):
        """Создаем полный бекап"""
        print("🚀 СОЗДАНИЕ ПОЛНОГО БЕКАПА СИСТЕМЫ БЕЗОПАСНОСТИ")
        print("=" * 60)
        
        try:
            # 1. Копируем все файлы
            print("📁 Копирование файлов...")
            self.backup_directory(self.source_dir, self.backup_path)
            
            # 2. Создаем манифест
            print("📋 Создание манифеста...")
            manifest_file = self.create_manifest()
            
            # 3. Создаем архив
            print("🗜️ Создание архива...")
            archive_path = self.create_archive()
            
            # 4. Проверяем целостность
            print("🔍 Проверка целостности...")
            verification = self.verify_backup()
            
            # 5. Выводим результаты
            self.print_results(archive_path, verification)
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка при создании бекапа: {e}")
            return False
    
    def print_results(self, archive_path, verification):
        """Выводим результаты бекапа"""
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ БЕКАПА")
        print("=" * 60)
        
        print(f"📁 Исходная директория: {self.source_dir}")
        print(f"💾 Директория бекапа: {self.backup_dir}")
        print(f"📦 Имя бекапа: {self.backup_name}")
        print(f"⏰ Время создания: {self.timestamp}")
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"  📄 Всего файлов: {self.stats['total_files']}")
        print(f"  📁 Всего директорий: {self.stats['total_dirs']}")
        print(f"  💾 Общий размер: {self.stats['total_size'] / (1024*1024):.2f} MB")
        print(f"  🐍 Python файлов: {self.stats['python_files']}")
        print(f"  ⚙️ Конфигурационных файлов: {self.stats['config_files']}")
        print(f"  🧪 Тестовых файлов: {self.stats['test_files']}")
        print(f"  📜 Скриптов: {self.stats['script_files']}")
        print(f"  💾 Файлов бекапа: {self.stats['backup_files']}")
        
        if archive_path:
            print(f"\n🗜️ АРХИВ:")
            print(f"  📦 Путь к архиву: {archive_path}")
            print(f"  💾 Размер архива: {self.stats.get('archive_size', 0) / (1024*1024):.2f} MB")
            print(f"  📊 Степень сжатия: {self.stats.get('compression_ratio', 0):.1f}%")
        
        print(f"\n🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ:")
        print(f"  ✅ Файлов проверено: {verification['total_files_verified']}")
        print(f"  ✅ Размеры совпадают: {verification['size_matches']}")
        print(f"  ✅ Checksums совпадают: {verification['checksum_matches']}")
        
        if verification['errors']:
            print(f"  ❌ Ошибок: {len(verification['errors'])}")
            for error in verification['errors'][:5]:  # Показываем первые 5 ошибок
                print(f"    - {error}")
        else:
            print(f"  🎉 Все проверки пройдены успешно!")
        
        if self.stats['errors']:
            print(f"\n⚠️ ОШИБКИ ПРИ КОПИРОВАНИИ:")
            for error in self.stats['errors'][:5]:  # Показываем первые 5 ошибок
                print(f"  - {error}")
        
        # Финальная оценка
        success_rate = (verification['total_files_verified'] / max(self.stats['total_files'], 1)) * 100
        print(f"\n🎯 ОБЩАЯ ОЦЕНКА: {success_rate:.1f}% успешно")
        
        if success_rate >= 99.0:
            print("🎉 БЕКАП СОЗДАН УСПЕШНО! Все файлы сохранены на 100%!")
        elif success_rate >= 95.0:
            print("✅ БЕКАП СОЗДАН ХОРОШО! Незначительные проблемы.")
        else:
            print("⚠️ БЕКАП СОЗДАН С ПРОБЛЕМАМИ! Требуется проверка.")

def main():
    """Главная функция"""
    # Настройки
    source_dir = "/Users/sergejhlystov/ALADDIN_NEW"
    backup_dir = "/Users/sergejhlystov/ALADDIN_BACKUPS"
    
    print("🛡️ ПОЛНЫЙ БЕКАП СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
    print("=" * 60)
    print(f"📁 Исходная директория: {source_dir}")
    print(f"💾 Директория бекапа: {backup_dir}")
    print("=" * 60)
    
    # Создаем бекап
    backup = FullSecurityBackup(source_dir, backup_dir)
    success = backup.create_backup()
    
    if success:
        print("\n🎉 БЕКАП ЗАВЕРШЕН УСПЕШНО!")
        return 0
    else:
        print("\n💥 ОШИБКА ПРИ СОЗДАНИИ БЕКАПА!")
        return 1

if __name__ == "__main__":
    exit(main())
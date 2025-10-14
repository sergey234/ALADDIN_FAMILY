#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Backup Quality - Проверка качества и целостности бэкапа
Детальная проверка всех аспектов созданного бэкапа

Функция: Verify Backup Quality
Приоритет: КРИТИЧЕСКИЙ
Версия: 1.0
Дата: 2025-09-07
"""

import os
import json
import hashlib
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class BackupQualityVerifier:
    """Проверка качества бэкапа"""
    
    def __init__(self, backup_dir: str):
        self.backup_dir = Path(backup_dir)
        self.manifest_file = self.backup_dir / "BACKUP_MANIFEST.json"
        self.checksums_file = self.backup_dir / "CHECKSUMS.txt"
        self.verification_results = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': [],
            'errors': [],
            'quality_score': 0.0
        }
    
    def verify_manifest_exists(self) -> bool:
        """Проверка наличия манифеста"""
        self.verification_results['total_checks'] += 1
        
        if self.manifest_file.exists():
            self.verification_results['passed_checks'] += 1
            print("✅ Манифест бэкапа найден")
            return True
        else:
            self.verification_results['failed_checks'] += 1
            self.verification_results['errors'].append("Манифест бэкапа не найден")
            print("❌ Манифест бэкапа не найден")
            return False
    
    def verify_checksums_file_exists(self) -> bool:
        """Проверка наличия файла контрольных сумм"""
        self.verification_results['total_checks'] += 1
        
        if self.checksums_file.exists():
            self.verification_results['passed_checks'] += 1
            print("✅ Файл контрольных сумм найден")
            return True
        else:
            self.verification_results['failed_checks'] += 1
            self.verification_results['errors'].append("Файл контрольных сумм не найден")
            print("❌ Файл контрольных сумм не найден")
            return False
    
    def verify_manifest_structure(self) -> bool:
        """Проверка структуры манифеста"""
        self.verification_results['total_checks'] += 1
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_keys = ['backup_info', 'statistics', 'files', 'backup_quality']
            missing_keys = [key for key in required_keys if key not in manifest]
            
            if not missing_keys:
                self.verification_results['passed_checks'] += 1
                print("✅ Структура манифеста корректна")
                return True
            else:
                self.verification_results['failed_checks'] += 1
                error_msg = f"Отсутствуют ключи в манифесте: {missing_keys}"
                self.verification_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            self.verification_results['failed_checks'] += 1
            error_msg = f"Ошибка чтения манифеста: {e}"
            self.verification_results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def verify_file_integrity(self) -> bool:
        """Проверка целостности файлов"""
        self.verification_results['total_checks'] += 1
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            files_info = manifest['files']
            integrity_errors = 0
            
            for file_info in files_info:
                if file_info['type'] == 'file':
                    file_path = self.backup_dir / file_info['path']
                    
                    if not file_path.exists():
                        print(f"❌ Файл не найден: {file_info['path']}")
                        integrity_errors += 1
                        continue
                    
                    # Проверяем хеш
                    current_hash = self.calculate_file_hash(file_path)
                    if current_hash != file_info['hash']:
                        print(f"❌ Хеш не совпадает: {file_info['path']}")
                        integrity_errors += 1
                        continue
            
            if integrity_errors == 0:
                self.verification_results['passed_checks'] += 1
                print("✅ Целостность всех файлов проверена")
                return True
            else:
                self.verification_results['failed_checks'] += 1
                error_msg = f"Найдено ошибок целостности: {integrity_errors}"
                self.verification_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            self.verification_results['failed_checks'] += 1
            error_msg = f"Ошибка проверки целостности: {e}"
            self.verification_results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
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
            return "ERROR"
    
    def verify_archive_integrity(self) -> bool:
        """Проверка целостности архивов"""
        self.verification_results['total_checks'] += 1
        
        try:
            # Проверяем ZIP архив
            zip_path = self.backup_dir.parent / f"{self.backup_dir.name}.zip"
            if zip_path.exists():
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    if zipf.testzip() is None:
                        print("✅ ZIP архив целостен")
                    else:
                        print("❌ ZIP архив поврежден")
                        self.verification_results['failed_checks'] += 1
                        return False
            else:
                print("⚠️ ZIP архив не найден")
                self.verification_results['warnings'].append("ZIP архив не найден")
            
            # Проверяем TAR.GZ архив
            tar_path = self.backup_dir.parent / f"{self.backup_dir.name}.tar.gz"
            if tar_path.exists():
                with tarfile.open(tar_path, 'r:gz') as tar:
                    # Простая проверка - пытаемся получить список файлов
                    tar.getnames()
                    print("✅ TAR.GZ архив целостен")
            else:
                print("⚠️ TAR.GZ архив не найден")
                self.verification_results['warnings'].append("TAR.GZ архив не найден")
            
            self.verification_results['passed_checks'] += 1
            return True
            
        except Exception as e:
            self.verification_results['failed_checks'] += 1
            error_msg = f"Ошибка проверки архивов: {e}"
            self.verification_results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def verify_backup_completeness(self) -> bool:
        """Проверка полноты бэкапа"""
        self.verification_results['total_checks'] += 1
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Проверяем ключевые директории
            key_directories = [
                'core',
                'security',
                'scripts',
                'tests',
                'docs'
            ]
            
            missing_dirs = []
            for dir_name in key_directories:
                dir_path = self.backup_dir / dir_name
                if not dir_path.exists():
                    missing_dirs.append(dir_name)
            
            if not missing_dirs:
                self.verification_results['passed_checks'] += 1
                print("✅ Все ключевые директории присутствуют")
                return True
            else:
                self.verification_results['failed_checks'] += 1
                error_msg = f"Отсутствуют ключевые директории: {missing_dirs}"
                self.verification_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            self.verification_results['failed_checks'] += 1
            error_msg = f"Ошибка проверки полноты: {e}"
            self.verification_results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def verify_backup_statistics(self) -> bool:
        """Проверка статистики бэкапа"""
        self.verification_results['total_checks'] += 1
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            stats = manifest['statistics']
            files_info = manifest['files']
            
            # Проверяем соответствие статистики
            actual_files = len([f for f in files_info if f['type'] == 'file'])
            actual_dirs = len([f for f in files_info if f['type'] == 'directory'])
            
            if (actual_files == stats['total_files'] and 
                actual_dirs == stats['total_dirs']):
                self.verification_results['passed_checks'] += 1
                print("✅ Статистика бэкапа корректна")
                return True
            else:
                self.verification_results['failed_checks'] += 1
                error_msg = f"Несоответствие статистики: файлы {actual_files}/{stats['total_files']}, директории {actual_dirs}/{stats['total_dirs']}"
                self.verification_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            self.verification_results['failed_checks'] += 1
            error_msg = f"Ошибка проверки статистики: {e}"
            self.verification_results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def calculate_quality_score(self) -> float:
        """Расчет оценки качества бэкапа"""
        if self.verification_results['total_checks'] == 0:
            return 0.0
        
        score = (self.verification_results['passed_checks'] / 
                self.verification_results['total_checks']) * 100
        
        # Штрафы за ошибки и предупреждения
        error_penalty = len(self.verification_results['errors']) * 5
        warning_penalty = len(self.verification_results['warnings']) * 2
        
        score = max(0, score - error_penalty - warning_penalty)
        
        return round(score, 2)
    
    def generate_verification_report(self) -> str:
        """Генерация отчета о проверке"""
        report = []
        
        report.append("🔍 ОТЧЕТ О ПРОВЕРКЕ КАЧЕСТВА БЭКАПА")
        report.append("=" * 60)
        report.append(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Директория бэкапа: {self.backup_dir}")
        report.append("")
        
        # Результаты проверки
        report.append("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
        report.append(f"Всего проверок: {self.verification_results['total_checks']}")
        report.append(f"Пройдено: {self.verification_results['passed_checks']}")
        report.append(f"Не пройдено: {self.verification_results['failed_checks']}")
        report.append(f"Предупреждения: {len(self.verification_results['warnings'])}")
        report.append(f"Ошибки: {len(self.verification_results['errors'])}")
        report.append("")
        
        # Оценка качества
        quality_score = self.calculate_quality_score()
        self.verification_results['quality_score'] = quality_score
        
        report.append("🎯 ОЦЕНКА КАЧЕСТВА:")
        if quality_score >= 95:
            report.append(f"🟢 ОТЛИЧНОЕ: {quality_score}/100")
        elif quality_score >= 85:
            report.append(f"🟡 ХОРОШЕЕ: {quality_score}/100")
        elif quality_score >= 70:
            report.append(f"🟠 УДОВЛЕТВОРИТЕЛЬНОЕ: {quality_score}/100")
        else:
            report.append(f"🔴 НЕУДОВЛЕТВОРИТЕЛЬНОЕ: {quality_score}/100")
        report.append("")
        
        # Ошибки
        if self.verification_results['errors']:
            report.append("❌ ОШИБКИ:")
            for error in self.verification_results['errors']:
                report.append(f"• {error}")
            report.append("")
        
        # Предупреждения
        if self.verification_results['warnings']:
            report.append("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.verification_results['warnings']:
                report.append(f"• {warning}")
            report.append("")
        
        # Рекомендации
        report.append("💡 РЕКОМЕНДАЦИИ:")
        if quality_score >= 95:
            report.append("• Бэкап готов к использованию")
            report.append("• Рекомендуется регулярное создание бэкапов")
        elif quality_score >= 85:
            report.append("• Бэкап пригоден к использованию")
            report.append("• Рекомендуется исправить предупреждения")
        elif quality_score >= 70:
            report.append("• Бэкап требует внимания")
            report.append("• Рекомендуется пересоздать бэкап")
        else:
            report.append("• Бэкап не рекомендуется к использованию")
            report.append("• Требуется полное пересоздание бэкапа")
        
        return "\n".join(report)
    
    def run_verification(self) -> bool:
        """Запуск полной проверки бэкапа"""
        print("🔍 ЗАПУСК ПРОВЕРКИ КАЧЕСТВА БЭКАПА")
        print("=" * 60)
        
        # Выполняем все проверки
        checks = [
            self.verify_manifest_exists,
            self.verify_checksums_file_exists,
            self.verify_manifest_structure,
            self.verify_file_integrity,
            self.verify_archive_integrity,
            self.verify_backup_completeness,
            self.verify_backup_statistics
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                print(f"❌ Ошибка при выполнении проверки: {e}")
                self.verification_results['errors'].append(f"Check error: {e}")
        
        # Генерируем отчет
        report = self.generate_verification_report()
        print("\n" + report)
        
        # Сохраняем отчет
        report_file = self.backup_dir / "VERIFICATION_REPORT.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Отчет о проверке сохранен: {report_file}")
        
        # Возвращаем результат
        quality_score = self.calculate_quality_score()
        return quality_score >= 85

# Тестирование
if __name__ == "__main__":
    print("🔍 ЗАПУСК ПРОВЕРКИ КАЧЕСТВА БЭКАПА")
    print("=" * 60)
    
    # Находим последний бэкап
    backups_dir = Path("../BACKUPS")
    if not backups_dir.exists():
        print("❌ Директория бэкапов не найдена")
        exit(1)
    
    # Ищем последний бэкап
    backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir() and d.name.startswith("ALADDIN_SECURITY_BACKUP_")]
    if not backup_dirs:
        print("❌ Бэкапы не найдены")
        exit(1)
    
    latest_backup = max(backup_dirs, key=lambda x: x.stat().st_mtime)
    print(f"📁 Проверяем бэкап: {latest_backup}")
    
    # Создание верификатора
    verifier = BackupQualityVerifier(latest_backup)
    
    # Запуск проверки
    success = verifier.run_verification()
    
    if success:
        print("\n✅ ПРОВЕРКА ПРОЙДЕНА УСПЕШНО!")
    else:
        print("\n❌ ПРОВЕРКА НЕ ПРОЙДЕНА!")
        exit(1)

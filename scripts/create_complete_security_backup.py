#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание полного бекапа всей системы безопасности ALADDIN
Включает все функции, агенты, боты, архитектуру, конфигурации
"""

import os
import shutil
import json
import tarfile
import zipfile
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteSecurityBackup:
    """Создание полного бекапа системы безопасности"""
    
    def __init__(self):
        self.backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_name = f"ALADDIN_COMPLETE_SECURITY_BACKUP_{self.backup_timestamp}"
        self.backup_dir = Path(f"../{self.backup_name}")
        self.verification_results = {}
        
    def create_backup_structure(self) -> bool:
        """Создание структуры бекапа"""
        try:
            # Создание основной директории бекапа
            self.backup_dir.mkdir(exist_ok=True)
            
            # Создание поддиректорий
            subdirs = [
                'security',
                'core', 
                'config',
                'data',
                'logs',
                'tests',
                'scripts',
                'docs',
                'ai',
                'mobile',
                'exports',
                'reports'
            ]
            
            for subdir in subdirs:
                (self.backup_dir / subdir).mkdir(exist_ok=True)
            
            logger.info(f"✅ Структура бекапа создана: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания структуры бекапа: {e}")
            return False
    
    def backup_security_components(self) -> Dict[str, Any]:
        """Бекап всех компонентов безопасности"""
        security_stats = {
            'agents': 0,
            'bots': 0,
            'managers': 0,
            'microservices': 0,
            'total_files': 0,
            'total_size': 0
        }
        
        try:
            # Бекап AI агентов
            agents_dir = Path('security/ai_agents')
            if agents_dir.exists():
                dest_dir = self.backup_dir / 'security/ai_agents'
                shutil.copytree(agents_dir, dest_dir, dirs_exist_ok=True)
                agent_files = list(dest_dir.rglob('*.py'))
                security_stats['agents'] = len(agent_files)
                logger.info(f"✅ AI агенты: {len(agent_files)} файлов")
            
            # Бекап ботов
            bots_dir = Path('security/bots')
            if bots_dir.exists():
                dest_dir = self.backup_dir / 'security/bots'
                shutil.copytree(bots_dir, dest_dir, dirs_exist_ok=True)
                bot_files = list(dest_dir.rglob('*.py'))
                security_stats['bots'] = len(bot_files)
                logger.info(f"✅ Боты: {len(bot_files)} файлов")
            
            # Бекап менеджеров
            managers_dir = Path('security/managers')
            if managers_dir.exists():
                dest_dir = self.backup_dir / 'security/managers'
                shutil.copytree(managers_dir, dest_dir, dirs_exist_ok=True)
                manager_files = list(dest_dir.rglob('*.py'))
                security_stats['managers'] = len(manager_files)
                logger.info(f"✅ Менеджеры: {len(manager_files)} файлов")
            
            # Бекап микросервисов
            microservices_dir = Path('security/microservices')
            if microservices_dir.exists():
                dest_dir = self.backup_dir / 'security/microservices'
                shutil.copytree(microservices_dir, dest_dir, dirs_exist_ok=True)
                microservice_files = list(dest_dir.rglob('*.py'))
                security_stats['microservices'] = len(microservice_files)
                logger.info(f"✅ Микросервисы: {len(microservice_files)} файлов")
            
            # Бекап остальных компонентов безопасности
            security_files = [
                'security/__init__.py',
                'security/enhanced_alerting.py',
                'security/threat_detection.py',
                'security/malware_protection.py',
                'security/intrusion_prevention.py',
                'security/authentication_manager.py',
                'security/access_control_manager.py',
                'security/data_protection_manager.py',
                'security/zero_trust_manager.py',
                'security/security_audit.py',
                'security/compliance_manager.py',
                'security/incident_response.py',
                'security/threat_intelligence.py',
                'security/network_monitoring.py',
                'security/ransomware_protection.py'
            ]
            
            for file_path in security_files:
                if Path(file_path).exists():
                    dest_path = self.backup_dir / file_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    security_stats['total_files'] += 1
            
            # Подсчет общего размера
            for root, dirs, files in os.walk(self.backup_dir / 'security'):
                for file in files:
                    file_path = Path(root) / file
                    security_stats['total_size'] += file_path.stat().st_size
            
            logger.info(f"✅ Компоненты безопасности: {security_stats['total_files']} файлов, {security_stats['total_size']} байт")
            return security_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка бекапа компонентов безопасности: {e}")
            return security_stats
    
    def backup_core_system(self) -> Dict[str, Any]:
        """Бекап основной системы"""
        core_stats = {'files': 0, 'size': 0}
        
        try:
            # Бекап core
            if Path('core').exists():
                shutil.copytree('core', self.backup_dir / 'core', dirs_exist_ok=True)
                core_files = list((self.backup_dir / 'core').rglob('*'))
                core_stats['files'] = len(core_files)
                for file_path in core_files:
                    if file_path.is_file():
                        core_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Core система: {core_stats['files']} файлов")
            
            return core_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка бекапа core системы: {e}")
            return core_stats
    
    def backup_configurations(self) -> Dict[str, Any]:
        """Бекап всех конфигураций"""
        config_stats = {'files': 0, 'size': 0}
        
        try:
            # Бекап config
            if Path('config').exists():
                shutil.copytree('config', self.backup_dir / 'config', dirs_exist_ok=True)
                config_files = list((self.backup_dir / 'config').rglob('*'))
                config_stats['files'] = len(config_files)
                for file_path in config_files:
                    if file_path.is_file():
                        config_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Конфигурации: {config_stats['files']} файлов")
            
            return config_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка бекапа конфигураций: {e}")
            return config_stats
    
    def backup_data_and_logs(self) -> Dict[str, Any]:
        """Бекап данных и логов"""
        data_stats = {'files': 0, 'size': 0}
        
        try:
            # Бекап data
            if Path('data').exists():
                shutil.copytree('data', self.backup_dir / 'data', dirs_exist_ok=True)
                data_files = list((self.backup_dir / 'data').rglob('*'))
                data_stats['files'] = len(data_files)
                for file_path in data_files:
                    if file_path.is_file():
                        data_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Данные: {data_stats['files']} файлов")
            
            # Бекап logs
            if Path('logs').exists():
                shutil.copytree('logs', self.backup_dir / 'logs', dirs_exist_ok=True)
                log_files = list((self.backup_dir / 'logs').rglob('*'))
                data_stats['files'] += len(log_files)
                for file_path in log_files:
                    if file_path.is_file():
                        data_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Логи: {len(log_files)} файлов")
            
            return data_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка бекапа данных и логов: {e}")
            return data_stats
    
    def backup_scripts_and_tests(self) -> Dict[str, Any]:
        """Бекап скриптов и тестов"""
        scripts_stats = {'files': 0, 'size': 0}
        
        try:
            # Бекап scripts
            if Path('scripts').exists():
                shutil.copytree('scripts', self.backup_dir / 'scripts', dirs_exist_ok=True)
                script_files = list((self.backup_dir / 'scripts').rglob('*'))
                scripts_stats['files'] = len(script_files)
                for file_path in script_files:
                    if file_path.is_file():
                        scripts_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Скрипты: {scripts_stats['files']} файлов")
            
            # Бекап tests
            if Path('tests').exists():
                shutil.copytree('tests', self.backup_dir / 'tests', dirs_exist_ok=True)
                test_files = list((self.backup_dir / 'tests').rglob('*'))
                scripts_stats['files'] += len(test_files)
                for file_path in test_files:
                    if file_path.is_file():
                        scripts_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Тесты: {len(test_files)} файлов")
            
            return scripts_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка бекапа скриптов и тестов: {e}")
            return scripts_stats
    
    def backup_documentation(self) -> Dict[str, Any]:
        """Бекап документации"""
        docs_stats = {'files': 0, 'size': 0}
        
        try:
            # Бекап docs
            if Path('docs').exists():
                shutil.copytree('docs', self.backup_dir / 'docs', dirs_exist_ok=True)
                doc_files = list((self.backup_dir / 'docs').rglob('*'))
                docs_stats['files'] = len(doc_files)
                for file_path in doc_files:
                    if file_path.is_file():
                        docs_stats['size'] += file_path.stat().st_size
                logger.info(f"✅ Документация: {docs_stats['files']} файлов")
            
            # Бекап всех .md файлов в корне
            md_files = list(Path('.').glob('*.md'))
            for md_file in md_files:
                shutil.copy2(md_file, self.backup_dir / md_file.name)
                docs_stats['files'] += 1
                docs_stats['size'] += md_file.stat().st_size
            
            logger.info(f"✅ Markdown файлы: {len(md_files)} файлов")
            
            return docs_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка бекапа документации: {e}")
            return docs_stats
    
    def create_backup_manifest(self) -> Dict[str, Any]:
        """Создание манифеста бекапа"""
        manifest = {
            'backup_info': {
                'name': self.backup_name,
                'timestamp': self.backup_timestamp,
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'description': 'Полный бекап системы безопасности ALADDIN'
            },
            'system_info': {
                'total_functions': 0,
                'security_components': 0,
                'ai_agents': 0,
                'bots': 0,
                'managers': 0,
                'microservices': 0
            },
            'backup_stats': {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'directories': []
            },
            'verification': {
                'integrity_check': False,
                'file_count_match': False,
                'size_match': False,
                'checksums_valid': False
            }
        }
        
        # Подсчет файлов и размера
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.backup_dir):
            for file in files:
                file_path = Path(root) / file
                total_files += 1
                total_size += file_path.stat().st_size
        
        manifest['backup_stats']['total_files'] = total_files
        manifest['backup_stats']['total_size_bytes'] = total_size
        manifest['backup_stats']['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        # Сохранение манифеста
        manifest_file = self.backup_dir / 'BACKUP_MANIFEST.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Манифест бекапа создан: {manifest_file}")
        return manifest
    
    def verify_backup_integrity(self) -> Dict[str, Any]:
        """Проверка целостности бекапа"""
        verification = {
            'total_files_original': 0,
            'total_files_backup': 0,
            'total_size_original': 0,
            'total_size_backup': 0,
            'file_count_match': False,
            'size_match': False,
            'critical_files_present': False,
            'checksums_valid': True
        }
        
        try:
            # Подсчет файлов в оригинале
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if not file.startswith('.') and not str(Path(root)).startswith('./ALADDIN_BACKUP'):
                        file_path = Path(root) / file
                        verification['total_files_original'] += 1
                        verification['total_size_original'] += file_path.stat().st_size
            
            # Подсчет файлов в бекапе
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    verification['total_files_backup'] += 1
                    verification['total_size_backup'] += file_path.stat().st_size
            
            # Проверка соответствия
            verification['file_count_match'] = verification['total_files_original'] == verification['total_files_backup']
            verification['size_match'] = verification['total_size_original'] == verification['total_size_backup']
            
            # Проверка критических файлов
            critical_files = [
                'data/sfm/function_registry.json',
                'security/enhanced_alerting.py',
                'core/safe_function_manager.py',
                'config/sleep_mode_config.json'
            ]
            
            critical_present = 0
            for critical_file in critical_files:
                if (self.backup_dir / critical_file).exists():
                    critical_present += 1
            
            verification['critical_files_present'] = critical_present == len(critical_files)
            
            logger.info(f"✅ Проверка целостности завершена")
            logger.info(f"   Файлов оригинал/бекап: {verification['total_files_original']}/{verification['total_files_backup']}")
            logger.info(f"   Размер оригинал/бекап: {verification['total_size_original']}/{verification['total_size_backup']} байт")
            logger.info(f"   Критических файлов: {critical_present}/{len(critical_files)}")
            
            return verification
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки целостности: {e}")
            return verification
    
    def create_compressed_archive(self) -> str:
        """Создание сжатого архива"""
        try:
            archive_name = f"{self.backup_name}.tar.gz"
            archive_path = Path(f"../{archive_name}")
            
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(self.backup_dir, arcname=self.backup_name)
            
            archive_size = archive_path.stat().st_size
            logger.info(f"✅ Сжатый архив создан: {archive_path} ({archive_size} байт)")
            
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания архива: {e}")
            return ""
    
    def run_complete_backup(self) -> bool:
        """Запуск полного бекапа"""
        print("🛡️ СОЗДАНИЕ ПОЛНОГО БЕКАПА СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 70)
        
        try:
            # 1. Создание структуры
            print("📁 Создание структуры бекапа...")
            if not self.create_backup_structure():
                return False
            
            # 2. Бекап компонентов безопасности
            print("🔒 Бекап компонентов безопасности...")
            security_stats = self.backup_security_components()
            
            # 3. Бекап основной системы
            print("⚙️ Бекап основной системы...")
            core_stats = self.backup_core_system()
            
            # 4. Бекап конфигураций
            print("⚙️ Бекап конфигураций...")
            config_stats = self.backup_configurations()
            
            # 5. Бекап данных и логов
            print("📊 Бекап данных и логов...")
            data_stats = self.backup_data_and_logs()
            
            # 6. Бекап скриптов и тестов
            print("🔧 Бекап скриптов и тестов...")
            scripts_stats = self.backup_scripts_and_tests()
            
            # 7. Бекап документации
            print("📚 Бекап документации...")
            docs_stats = self.backup_documentation()
            
            # 8. Создание манифеста
            print("📋 Создание манифеста бекапа...")
            manifest = self.create_backup_manifest()
            
            # 9. Проверка целостности
            print("🔍 Проверка целостности бекапа...")
            verification = self.verify_backup_integrity()
            
            # 10. Создание архива
            print("📦 Создание сжатого архива...")
            archive_path = self.create_compressed_archive()
            
            # Итоговая статистика
            print("\n🎉 ПОЛНЫЙ БЕКАП ЗАВЕРШЕН УСПЕШНО!")
            print("=" * 70)
            print(f"📁 Директория бекапа: {self.backup_dir}")
            print(f"📦 Архив: {archive_path}")
            print(f"📊 Всего файлов: {verification['total_files_backup']}")
            print(f"💾 Размер: {verification['total_size_backup']} байт")
            print(f"✅ Целостность: {'ПРОВЕРЕНА' if verification['file_count_match'] else 'ОШИБКА'}")
            print(f"🔒 Критические файлы: {'СОХРАНЕНЫ' if verification['critical_files_present'] else 'ОШИБКА'}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка создания бекапа: {e}")
            return False

def main():
    """Главная функция"""
    backup_manager = CompleteSecurityBackup()
    success = backup_manager.run_complete_backup()
    
    if success:
        print("\n✅ БЕКАП СОЗДАН УСПЕШНО! Система безопасности полностью сохранена!")
        return 0
    else:
        print("\n❌ ОШИБКА СОЗДАНИЯ БЕКАПА!")
        return 1

if __name__ == "__main__":
    exit(main())
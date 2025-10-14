#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Safe Duplicate Mover
Безопасный перенос дублирующих файлов в папку FORMATTING_WORK/duplicates/
и удаление их из SFM registry
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import logging

class SafeDuplicateMover:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.duplicates_dir = self.project_root / "security" / "formatting_work" / "duplicates"
        self.sfm_registry = self.project_root / "data" / "sfm" / "function_registry.json"
        
        # Список файлов для переноса (из анализа)
        self.files_to_move = [
            # Security Analytics
            "security/security_analytics.py",  # 684 строки, 350 очков
            
            # Security Monitoring  
            "security/security_monitoring_backup.py",  # 837 строк, 480 очков
            "security/security_monitoring.py",  # 166 строк, 135 очков
            
            # Incident Response
            "security/incident_response.py",  # 776 строк, 545 очков
            
            # Circuit Breaker
            "security/ai_agents/circuit_breaker_main.py",  # 512 строк, 535 очков
            "security/microservices/circuit_breaker.py",  # 452 строки, 395 очков
            "security/microservices/circuit_breaker_extra.py",  # 227 строк, 175 очков
            
            # Malware Protection
            "security/malware_protection_old_backup_20250928_125507.py",  # 391 строка, 260 очков
            
            # Intrusion Prevention
            "security/intrusion_prevention.py",  # 687 строк, 390 очков
            
            # Device Security
            "security/device_security.py",  # 2209 строк, 1025 очков
            
            # Network Monitoring
            "security/network_monitoring.py",  # 1969 строк, 1130 очков
            
            # Put to Sleep
            "security/microservices/put_to_sleep.py",  # 159 строк, 90 очков
            
            # User Interface Manager
            "security/managers/user_interface_manager_main.py",  # 332 строки, 280 очков
            
            # Parental Control Bot
            "security/bots/parental_control_bot_v2.py",  # 218 строк, 235 очков
            
            # Notification Bot
            "security/ai_agents/notification_bot_main.py",  # 428 строк, 335 очков
            "security/bots/notification_bot_extra.py",  # 198 строк, 225 очков
            
            # Universal Privacy Manager
            "security/privacy/universal_privacy_manager_new.py",  # 606 строк, 500 очков
            
            # Elderly Interface Manager
            "security/ai_agents/elderly_interface_manager_backup.py",  # 715 строк, 420 очков
            
            # Family Profile Manager
            "security/family/family_profile_manager.py",  # 399 строк, 265 очков
            
            # Child Protection
            "security/family/child_protection_new.py",  # 656 строк, 350 очков
            
            # Trust Scoring
            "security/preliminary/trust_scoring.py",  # 459 строк, 315 очков
            
            # Behavioral Analysis
            "security/preliminary/behavioral_analysis.py",  # 663 строки, 360 очков
            
            # Mobile Security Agent
            "security/ai_agents/mobile_security_agent_backup_20250921_103531.py",  # 2361 строка, 1145 очков
            "security/ai_agents/mobile_security_agent_extra.py",  # 712 строк, 375 очков
            "security/ai_agents/mobile_security_agent_main.py",  # 695 строк, 375 очков
            
            # Phishing Protection Agent
            "security/ai_agents/phishing_protection_agent_backup_20250921_104040.py",  # 699 строк, 440 очков
            
            # Family Communication Hub
            "security/ai_agents/family_communication_hub_backup_20250921_103829.py",  # 413 строк, 280 очков
            "security/ai_agents/family_communication_hub_a_plus.py",  # 361 строка, 210 очков
            
            # Behavioral Analytics Engine
            "security/ai_agents/behavioral_analytics_engine_extra.py",  # 454 строки, 295 очков
            "security/ai_agents/behavioral_analytics_engine_main.py",  # 371 строка, 225 очков
            
            # Financial Protection Hub
            "security/ai_agents/financial_protection_hub_backup_20250921_104412.py",  # 862 строки, 530 очков
            
            
            # __init__ files (17 files)
            "security/ai_agents/__init__.py",
            "security/bots/__init__.py", 
            "security/managers/__init__.py",
            "security/microservices/__init__.py",
            "security/family/__init__.py",
            "security/privacy/__init__.py",
            "security/compliance/__init__.py",
            "security/active/__init__.py",
            "security/reactive/__init__.py",
            "security/ai/__init__.py",
            "security/core/__init__.py",
            "security/ci_cd/__init__.py",
            "security/vpn/__init__.py",
            "security/scaling/__init__.py",
            "security/orchestration/__init__.py",
            "security/preliminary/__init__.py"
        ]
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SafeDuplicateMover")
        
    def create_backup_manifest(self):
        """Создает манифест перенесенных файлов"""
        manifest = {
            "moved_at": datetime.now().isoformat(),
            "total_files": len(self.files_to_move),
            "reason": "Удаление дублирующих файлов из активной системы",
            "files": []
        }
        
        for file_path in self.files_to_move:
            full_path = self.project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                manifest["files"].append({
                    "original_path": str(file_path),
                    "moved_to": f"security/formatting_work/duplicates/{file_path.split('/')[-1]}",
                    "size_bytes": stat.st_size,
                    "lines": self.count_lines(full_path),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return manifest
        
    def count_lines(self, file_path):
        """Подсчитывает количество строк в файле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
            
    def move_file(self, source_path, dest_path):
        """Безопасно перемещает файл"""
        try:
            # Создаем директорию назначения если не существует
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Перемещаем файл
            shutil.move(str(source_path), str(dest_path))
            self.logger.info(f"✅ Перемещен: {source_path} → {dest_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка перемещения {source_path}: {e}")
            return False
            
    def remove_from_sfm_registry(self):
        """Удаляет файлы из SFM registry"""
        try:
            if not self.sfm_registry.exists():
                self.logger.warning("SFM registry не найден")
                return False
                
            # Загружаем текущий registry
            with open(self.sfm_registry, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                
            # Создаем резервную копию
            backup_path = self.sfm_registry.with_suffix('.backup_before_cleanup.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            self.logger.info(f"✅ Создана резервная копия: {backup_path}")
            
            # Удаляем записи о перемещенных файлах
            removed_count = 0
            for file_path in self.files_to_move:
                file_name = Path(file_path).name
                # Ищем и удаляем записи по имени файла
                keys_to_remove = []
                for key, value in registry.items():
                    if isinstance(value, dict) and value.get('file_path', '').endswith(file_name):
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del registry[key]
                    removed_count += 1
                    self.logger.info(f"🗑️ Удалена запись из SFM: {key}")
            
            # Сохраняем обновленный registry
            with open(self.sfm_registry, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"✅ Удалено {removed_count} записей из SFM registry")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления SFM registry: {e}")
            return False
            
    def move_duplicates(self):
        """Основная функция переноса дубликатов"""
        self.logger.info("🚀 Начало безопасного переноса дубликатов...")
        
        # Создаем манифест
        manifest = self.create_backup_manifest()
        
        moved_count = 0
        failed_count = 0
        
        for file_path in self.files_to_move:
            source_path = self.project_root / file_path
            
            if not source_path.exists():
                self.logger.warning(f"⚠️ Файл не найден: {source_path}")
                failed_count += 1
                continue
                
            # Создаем путь назначения
            dest_path = self.duplicates_dir / source_path.name
            
            # Проверяем, не существует ли уже файл в назначении
            if dest_path.exists():
                # Добавляем timestamp к имени
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = dest_path.stem, timestamp, dest_path.suffix
                dest_path = dest_path.parent / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            
            # Перемещаем файл
            if self.move_file(source_path, dest_path):
                moved_count += 1
            else:
                failed_count += 1
        
        # Сохраняем манифест
        manifest_path = self.duplicates_dir / "MOVED_FILES_MANIFEST.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        # Обновляем SFM registry
        self.remove_from_sfm_registry()
        
        # Итоговая статистика
        self.logger.info("="*80)
        self.logger.info("📊 ИТОГОВАЯ СТАТИСТИКА ПЕРЕНОСА:")
        self.logger.info(f"✅ Успешно перемещено: {moved_count} файлов")
        self.logger.info(f"❌ Ошибок: {failed_count} файлов")
        self.logger.info(f"📁 Папка дубликатов: {self.duplicates_dir}")
        self.logger.info(f"📋 Манифест: {manifest_path}")
        self.logger.info("="*80)
        
        return moved_count, failed_count

if __name__ == "__main__":
    mover = SafeDuplicateMover()
    moved, failed = mover.move_duplicates()
    
    if failed == 0:
        print("🎉 Все файлы успешно перемещены!")
    else:
        print(f"⚠️ Перемещено {moved} файлов, {failed} ошибок")
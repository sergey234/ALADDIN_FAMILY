"""
Система защиты от Ransomware для ALADDIN Security System
Автоматическое резервное копирование и мониторинг подозрительной активности
"""

import os
import hashlib
import shutil
import time
import threading
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json
import asyncio

# Упрощенная реализация без внешних зависимостей
class FileSystemEventHandler:
    """Упрощенный обработчик событий файловой системы"""
    def __init__(self, protection_system):
        self.protection_system = protection_system
    
    def on_modified(self, event):
        pass
    
    def on_created(self, event):
        pass

class Observer:
    """Упрощенный наблюдатель файловой системы"""
    def __init__(self):
        self.handlers = []
    
    def schedule(self, handler, path, recursive=True):
        self.handlers.append((handler, path, recursive))
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def join(self):
        pass

@dataclass
class RansomwareSignature:
    """Сигнатура ransomware атаки"""
    name: str
    file_extensions: Set[str]
    suspicious_patterns: List[str]
    behavior_indicators: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL

@dataclass
class BackupInfo:
    """Информация о резервной копии"""
    backup_id: str
    timestamp: datetime
    file_path: str
    file_hash: str
    file_size: int
    backup_location: str
    is_encrypted: bool = False

@dataclass
class RansomwareAlert:
    """Алерт о подозрительной активности"""
    alert_id: str
    timestamp: datetime
    alert_type: str
    severity: str
    description: str
    affected_files: List[str]
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None

class RansomwareProtectionSystem:
    """
    Система защиты от Ransomware
    Мониторинг, резервное копирование и блокировка подозрительной активности
    """
    
    def __init__(self, name: str = "RansomwareProtection"):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.monitored_directories: Set[str] = set()
        self.backup_directory = "backups/ransomware_protection"
        self.alert_threshold = 10  # Количество подозрительных файлов для алерта
        self.backup_interval = 300  # 5 минут
        self.max_backups = 100  # Максимальное количество резервных копий
        
        # Сигнатуры ransomware
        self.ransomware_signatures = self._load_ransomware_signatures()
        
        # Мониторинг файлов
        self.file_hashes: Dict[str, str] = {}
        self.suspicious_files: Set[str] = set()
        self.encrypted_files: Set[str] = set()
        
        # Статистика
        self.stats = {
            'files_monitored': 0,
            'backups_created': 0,
            'alerts_generated': 0,
            'threats_blocked': 0,
            'last_backup': None,
            'last_scan': None
        }
        
        # Создаем директорию для резервных копий
        os.makedirs(self.backup_directory, exist_ok=True)
        
    def _load_ransomware_signatures(self) -> List[RansomwareSignature]:
        """Загрузка сигнатур ransomware"""
        signatures = [
            RansomwareSignature(
                name="WannaCry",
                file_extensions={".wncry", ".wannacry", ".locked"},
                suspicious_patterns=["WannaCry", "Wanna Decrypt0r", "Wanna Decryptor"],
                behavior_indicators=["mass_file_encryption", "bitcoin_demand", "timer_display"],
                risk_level="CRITICAL"
            ),
            RansomwareSignature(
                name="Locky",
                file_extensions={".locky", ".zepto", ".odin", ".thor"},
                suspicious_patterns=["Locky", "Zepto", "Odin", "Thor"],
                behavior_indicators=["mass_file_encryption", "ransom_note"],
                risk_level="HIGH"
            ),
            RansomwareSignature(
                name="CryptoLocker",
                file_extensions={".cryptolocker", ".encrypted"},
                suspicious_patterns=["CryptoLocker", "Your files are encrypted"],
                behavior_indicators=["mass_file_encryption", "bitcoin_payment"],
                risk_level="HIGH"
            ),
            RansomwareSignature(
                name="Cerber",
                file_extensions={".cerber", ".cerber3", ".cerber4"},
                suspicious_patterns=["Cerber", "Cerber3", "Cerber4"],
                behavior_indicators=["mass_file_encryption", "tor_payment"],
                risk_level="HIGH"
            ),
            RansomwareSignature(
                name="GenericRansomware",
                file_extensions={".encrypted", ".locked", ".crypted", ".crypto"},
                suspicious_patterns=["encrypted", "locked", "crypted", "crypto"],
                behavior_indicators=["mass_file_encryption", "ransom_note"],
                risk_level="MEDIUM"
            )
        ]
        return signatures
    
    def start_monitoring(self, directories: List[str]) -> bool:
        """Запуск мониторинга директорий"""
        try:
            self.monitored_directories.update(directories)
            self.is_running = True
            
            # Запускаем мониторинг файловой системы
            self._start_file_monitoring()
            
            # Запускаем автоматическое резервное копирование
            self._start_backup_scheduler()
            
            # Запускаем периодическое сканирование
            self._start_periodic_scanning()
            
            self.logger.info(f"Защита от ransomware запущена для {len(directories)} директорий")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска защиты от ransomware: {e}")
            return False
    
    def _start_file_monitoring(self):
        """Запуск мониторинга файловой системы"""
        self.observer = Observer()
        
        for directory in self.monitored_directories:
            if os.path.exists(directory):
                event_handler = RansomwareFileHandler(self)
                self.observer.schedule(event_handler, directory, recursive=True)
        
        self.observer.start()
    
    def _start_backup_scheduler(self):
        """Запуск планировщика резервного копирования"""
        def backup_scheduler():
            while self.is_running:
                try:
                    self._create_automatic_backup()
                    time.sleep(self.backup_interval)
                except Exception as e:
                    self.logger.error(f"Ошибка в планировщике резервного копирования: {e}")
                    time.sleep(60)  # Ждем минуту при ошибке
        
        backup_thread = threading.Thread(target=backup_scheduler, daemon=True)
        backup_thread.start()
    
    def _start_periodic_scanning(self):
        """Запуск периодического сканирования"""
        def periodic_scanner():
            while self.is_running:
                try:
                    self._scan_for_ransomware()
                    time.sleep(60)  # Сканируем каждую минуту
                except Exception as e:
                    self.logger.error(f"Ошибка в периодическом сканировании: {e}")
                    time.sleep(60)
        
        scan_thread = threading.Thread(target=periodic_scanner, daemon=True)
        scan_thread.start()
    
    def _create_automatic_backup(self) -> bool:
        """Создание автоматической резервной копии"""
        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"auto_backup_{backup_timestamp}"
            
            # Создаем резервную копию для каждой мониторируемой директории
            for directory in self.monitored_directories:
                if os.path.exists(directory):
                    backup_path = os.path.join(self.backup_directory, backup_id, os.path.basename(directory))
                    os.makedirs(backup_path, exist_ok=True)
                    
                    # Копируем файлы
                    shutil.copytree(directory, backup_path, dirs_exist_ok=True)
                    
                    # Создаем манифест резервной копии
                    self._create_backup_manifest(backup_path, backup_id)
            
            self.stats['backups_created'] += 1
            self.stats['last_backup'] = datetime.now()
            
            # Очищаем старые резервные копии
            self._cleanup_old_backups()
            
            self.logger.info(f"Автоматическая резервная копия создана: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            return False
    
    def _create_backup_manifest(self, backup_path: str, backup_id: str):
        """Создание манифеста резервной копии"""
        manifest = {
            'backup_id': backup_id,
            'timestamp': datetime.now().isoformat(),
            'backup_path': backup_path,
            'files': [],
            'total_size': 0
        }
        
        total_size = 0
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_hash = self._calculate_file_hash(file_path)
                
                manifest['files'].append({
                    'path': file_path,
                    'size': file_size,
                    'hash': file_hash,
                    'timestamp': os.path.getmtime(file_path)
                })
                
                total_size += file_size
        
        manifest['total_size'] = total_size
        
        # Сохраняем манифест
        manifest_path = os.path.join(backup_path, 'backup_manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def _cleanup_old_backups(self):
        """Очистка старых резервных копий"""
        try:
            backup_dirs = [d for d in os.listdir(self.backup_directory) 
                          if os.path.isdir(os.path.join(self.backup_directory, d))]
            
            if len(backup_dirs) > self.max_backups:
                # Сортируем по времени создания
                backup_dirs.sort(key=lambda x: os.path.getctime(os.path.join(self.backup_directory, x)))
                
                # Удаляем самые старые
                for old_backup in backup_dirs[:-self.max_backups]:
                    old_path = os.path.join(self.backup_directory, old_backup)
                    shutil.rmtree(old_path)
                    self.logger.info(f"Удалена старая резервная копия: {old_backup}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка очистки старых резервных копий: {e}")
    
    def _scan_for_ransomware(self):
        """Сканирование на наличие ransomware"""
        try:
            suspicious_count = 0
            new_suspicious_files = set()
            
            for directory in self.monitored_directories:
                if not os.path.exists(directory):
                    continue
                    
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Проверяем расширение файла
                        if self._is_suspicious_file(file_path):
                            new_suspicious_files.add(file_path)
                            suspicious_count += 1
                        
                        # Проверяем содержимое файла
                        if self._contains_ransomware_patterns(file_path):
                            new_suspicious_files.add(file_path)
                            suspicious_count += 1
            
            # Обновляем список подозрительных файлов
            self.suspicious_files.update(new_suspicious_files)
            
            # Генерируем алерт при превышении порога
            if suspicious_count >= self.alert_threshold:
                self._generate_ransomware_alert(suspicious_count, new_suspicious_files)
            
            self.stats['last_scan'] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования на ransomware: {e}")
    
    def _is_suspicious_file(self, file_path: str) -> bool:
        """Проверка файла на подозрительность по расширению"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        for signature in self.ransomware_signatures:
            if file_ext in signature.file_extensions:
                return True
        
        return False
    
    def _contains_ransomware_patterns(self, file_path: str) -> bool:
        """Проверка файла на наличие паттернов ransomware"""
        try:
            if not os.path.exists(file_path) or os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB
                return False
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Читаем первые 1024 символа
                
                for signature in self.ransomware_signatures:
                    for pattern in signature.suspicious_patterns:
                        if pattern.lower() in content.lower():
                            return True
                            
        except Exception:
            pass  # Игнорируем ошибки чтения файла
        
        return False
    
    def _generate_ransomware_alert(self, suspicious_count: int, suspicious_files: List[str]):
        """Генерация алерта о ransomware"""
        alert = RansomwareAlert(
            alert_id=f"ransomware_alert_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type="RANSOMWARE_DETECTED",
            severity="CRITICAL",
            description=f"Обнаружено {suspicious_count} подозрительных файлов, возможна ransomware атака",
            affected_files=list(suspicious_files)
        )
        
        # Сохраняем алерт
        self._save_alert(alert)
        
        # Блокируем подозрительные файлы
        self._block_suspicious_files(suspicious_files)
        
        self.stats['alerts_generated'] += 1
        self.logger.critical(f"RANSOMWARE АЛЕРТ: {alert.description}")
    
    def _save_alert(self, alert: RansomwareAlert):
        """Сохранение алерта"""
        try:
            alert_file = os.path.join(self.backup_directory, f"alert_{alert.alert_id}.json")
            
            alert_data = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'description': alert.description,
                'affected_files': alert.affected_files,
                'source_ip': alert.source_ip,
                'user_agent': alert.user_agent
            }
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                json.dump(alert_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Ошибка сохранения алерта: {e}")
    
    def _block_suspicious_files(self, suspicious_files: List[str]):
        """Блокировка подозрительных файлов"""
        try:
            for file_path in suspicious_files:
                # Перемещаем файл в карантин
                quarantine_dir = os.path.join(self.backup_directory, "quarantine")
                os.makedirs(quarantine_dir, exist_ok=True)
                
                filename = os.path.basename(file_path)
                quarantine_path = os.path.join(quarantine_dir, f"quarantined_{int(time.time())}_{filename}")
                
                shutil.move(file_path, quarantine_path)
                self.logger.warning(f"Файл перемещен в карантин: {file_path} -> {quarantine_path}")
                
        except Exception as e:
            self.logger.error(f"Ошибка блокировки подозрительных файлов: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Вычисление хеша файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def get_status(self) -> Dict[str, any]:
        """Получение статуса системы защиты от ransomware"""
        return {
            'name': self.name,
            'is_running': self.is_running,
            'monitored_directories': list(self.monitored_directories),
            'suspicious_files_count': len(self.suspicious_files),
            'encrypted_files_count': len(self.encrypted_files),
            'stats': self.stats,
            'backup_directory': self.backup_directory,
            'alert_threshold': self.alert_threshold,
            'max_backups': self.max_backups
        }
    
    def stop(self):
        """Остановка системы защиты от ransomware"""
        self.is_running = False
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        self.logger.info("Защита от ransomware остановлена")

class RansomwareFileHandler(FileSystemEventHandler):
    """Обработчик событий файловой системы для обнаружения ransomware"""
    
    def __init__(self, protection_system: RansomwareProtectionSystem):
        self.protection_system = protection_system
        self.logger = logging.getLogger(__name__)
    
    def on_modified(self, event):
        """Обработка изменения файла"""
        if not event.is_directory:
            self._check_file(event.src_path)
    
    def on_created(self, event):
        """Обработка создания файла"""
        if not event.is_directory:
            self._check_file(event.src_path)
    
    def _check_file(self, file_path: str):
        """Проверка файла на подозрительность"""
        try:
            if self.protection_system._is_suspicious_file(file_path):
                self.protection_system.suspicious_files.add(file_path)
                self.logger.warning(f"Обнаружен подозрительный файл: {file_path}")
                
                # Немедленно создаем резервную копию
                self.protection_system._create_automatic_backup()
                
        except Exception as e:
            self.logger.error(f"Ошибка проверки файла {file_path}: {e}")

# Пример использования
if __name__ == "__main__":
    # Создаем систему защиты от ransomware
    ransomware_protection = RansomwareProtectionSystem()
    
    # Запускаем мониторинг
    directories_to_monitor = [
        "ALADDIN_NEW/security",
        "ALADDIN_NEW/core",
        "ALADDIN_NEW/tests"
    ]
    
    if ransomware_protection.start_monitoring(directories_to_monitor):
        print("✅ Защита от ransomware запущена")
        
        # Получаем статус
        status = ransomware_protection.get_status()
        print(f"📊 Статус: {status['is_running']}")
        print(f"📁 Мониторируемые директории: {len(status['monitored_directories'])}")
        print(f"⚠️ Подозрительные файлы: {status['suspicious_files_count']}")
        
        # Останавливаем через 60 секунд (для демонстрации)
        import time
        time.sleep(60)
        ransomware_protection.stop()
        print("🛑 Защита от ransomware остановлена")
    else:
        print("❌ Ошибка запуска защиты от ransomware")
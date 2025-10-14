#!/usr/bin/env python3
"""
Система защиты реестра функций ALADDIN
Предотвращает случайное удаление функций и обеспечивает целостность данных
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/registry_protection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RegistryProtectionSystem:
    """Система защиты реестра функций от случайного удаления"""
    
    def __init__(self, registry_path: str = "data/sfm/function_registry.json"):
        self.registry_path = Path(registry_path)
        self.backup_dir = Path("data/sfm/backups")
        self.protection_log = Path("logs/registry_protection.log")
        
        # Создаём необходимые директории
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.protection_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Загружаем текущий реестр
        self.current_registry = self._load_registry()
        self.original_count = len(self.current_registry.get("functions", {}))
        
        logger.info(f"🛡️ Система защиты реестра инициализирована")
        logger.info(f"📊 Текущее количество функций: {self.original_count}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Безопасная загрузка реестра"""
        try:
            if not self.registry_path.exists():
                logger.warning(f"⚠️ Реестр не найден: {self.registry_path}")
                return {"functions": {}, "version": "1.0", "last_updated": datetime.now().isoformat()}
            
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Валидация формата
            if not self._validate_registry_format(registry):
                logger.error("❌ Неверный формат реестра!")
                return {"functions": {}, "version": "1.0", "last_updated": datetime.now().isoformat()}
            
            return registry
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки реестра: {e}")
            return {"functions": {}, "version": "1.0", "last_updated": datetime.now().isoformat()}
    
    def _validate_registry_format(self, registry: Dict[str, Any]) -> bool:
        """Валидация формата реестра"""
        try:
            # Проверяем обязательные поля
            if "functions" not in registry:
                logger.error("❌ Отсутствует поле 'functions'")
                return False
            
            # Проверяем что functions - это словарь
            if not isinstance(registry["functions"], dict):
                logger.error("❌ Поле 'functions' должно быть словарём")
                return False
            
            # Проверяем структуру функций
            for func_id, func_data in registry["functions"].items():
                if not isinstance(func_data, dict):
                    logger.error(f"❌ Функция {func_id} должна быть словарём")
                    return False
                
                required_fields = ["name", "status"]
                for field in required_fields:
                    if field not in func_data:
                        logger.error(f"❌ У функции {func_id} отсутствует поле '{field}'")
                        return False
            
            logger.info("✅ Формат реестра корректен")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации формата: {e}")
            return False
    
    def create_backup(self) -> str:
        """Создание резервной копии реестра"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"registry_backup_{timestamp}.json"
            
            # Копируем текущий реестр
            shutil.copy2(self.registry_path, backup_path)
            
            logger.info(f"💾 Создана резервная копия: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания резервной копии: {e}")
            return ""
    
    def check_function_deletion(self, new_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка на удаление функций"""
        current_functions = set(self.current_registry.get("functions", {}).keys())
        new_functions = set(new_registry.get("functions", {}).keys())
        
        deleted_functions = current_functions - new_functions
        added_functions = new_functions - current_functions
        
        result = {
            "deleted_count": len(deleted_functions),
            "added_count": len(added_functions),
            "deleted_functions": list(deleted_functions),
            "added_functions": list(added_functions),
            "current_count": len(current_functions),
            "new_count": len(new_functions)
        }
        
        if deleted_functions:
            logger.warning(f"⚠️ Обнаружено удаление {len(deleted_functions)} функций: {list(deleted_functions)}")
        
        if added_functions:
            logger.info(f"✅ Добавлено {len(added_functions)} функций: {list(added_functions)}")
        
        return result
    
    def protect_registry_write(self, new_registry: Dict[str, Any], force: bool = False) -> bool:
        """Защищённая запись в реестр с проверками"""
        try:
            # Создаём резервную копию
            backup_path = self.create_backup()
            
            # Валидируем новый реестр
            if not self._validate_registry_format(new_registry):
                logger.error("❌ Новый реестр не прошёл валидацию!")
                return False
            
            # Проверяем на удаление функций
            deletion_info = self.check_function_deletion(new_registry)
            
            # Если функции удаляются и не принудительная запись
            if deletion_info["deleted_count"] > 0 and not force:
                logger.critical("🚨 ОБНАРУЖЕНО УДАЛЕНИЕ ФУНКЦИЙ!")
                logger.critical(f"Удалено функций: {deletion_info['deleted_count']}")
                logger.critical(f"Удалённые функции: {deletion_info['deleted_functions']}")
                logger.critical("❌ ЗАПИСЬ ЗАБЛОКИРОВАНА! Используйте force=True для принудительной записи")
                return False
            
            # Записываем новый реестр
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(new_registry, f, indent=2, ensure_ascii=False)
            
            # Обновляем текущий реестр
            self.current_registry = new_registry
            
            # Логируем изменения
            self._log_registry_changes(deletion_info, backup_path)
            
            logger.info("✅ Реестр успешно обновлён")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка записи реестра: {e}")
            return False
    
    def _log_registry_changes(self, deletion_info: Dict[str, Any], backup_path: str) -> None:
        """Логирование изменений реестра"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "registry_update",
            "backup_path": backup_path,
            "changes": deletion_info
        }
        
        try:
            with open(self.protection_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"❌ Ошибка записи лога: {e}")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Получение статуса реестра"""
        current_count = len(self.current_registry.get("functions", {}))
        
        return {
            "registry_path": str(self.registry_path),
            "current_functions_count": current_count,
            "original_functions_count": self.original_count,
            "functions_lost": max(0, self.original_count - current_count),
            "last_updated": self.current_registry.get("last_updated", "unknown"),
            "registry_exists": self.registry_path.exists(),
            "backup_count": len(list(self.backup_dir.glob("registry_backup_*.json")))
        }
    
    def list_functions(self) -> List[str]:
        """Список всех функций в реестре"""
        return list(self.current_registry.get("functions", {}).keys())
    
    def get_function_info(self, func_id: str) -> Optional[Dict[str, Any]]:
        """Информация о конкретной функции"""
        return self.current_registry.get("functions", {}).get(func_id)

def main():
    """Тестирование системы защиты реестра"""
    print("🛡️ ТЕСТИРОВАНИЕ СИСТЕМЫ ЗАЩИТЫ РЕЕСТРА")
    print("=" * 50)
    
    # Инициализация системы
    protection = RegistryProtectionSystem()
    
    # Показываем статус
    status = protection.get_registry_status()
    print(f"📊 Статус реестра:")
    print(f"   • Функций сейчас: {status['current_functions_count']}")
    print(f"   • Функций изначально: {status['original_functions_count']}")
    print(f"   • Потеряно функций: {status['functions_lost']}")
    print(f"   • Резервных копий: {status['backup_count']}")
    
    # Показываем список функций
    functions = protection.list_functions()
    print(f"\n🔍 Функции в реестре ({len(functions)}):")
    for i, func_id in enumerate(functions[:10], 1):
        print(f"   {i}. {func_id}")
    
    if len(functions) > 10:
        print(f"   ... и ещё {len(functions) - 10} функций")
    
    print(f"\n✅ Система защиты реестра активна!")
    print(f"📁 Лог защиты: {protection.protection_log}")

if __name__ == "__main__":
    main()
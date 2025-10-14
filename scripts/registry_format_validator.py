#!/usr/bin/env python3
"""
Валидатор формата реестра функций ALADDIN
Проверяет и исправляет ошибки формата данных
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/registry_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RegistryFormatValidator:
    """Валидатор и исправитель формата реестра функций"""
    
    def __init__(self, registry_path: str = "data/sfm/function_registry.json"):
        self.registry_path = Path(registry_path)
        self.validation_log = Path("logs/registry_validation.log")
        
        # Создаём директорию для логов
        self.validation_log.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔍 Валидатор формата реестра инициализирован")
    
    def validate_registry(self, registry: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Валидация реестра функций
        Возвращает: (is_valid, errors, fixed_registry)
        """
        errors = []
        fixed_registry = registry.copy()
        
        try:
            # 1. Проверка структуры верхнего уровня
            if not isinstance(registry, dict):
                errors.append("❌ Реестр должен быть словарём")
                return False, errors, registry
            
            # 2. Проверка обязательных полей
            required_top_fields = ["functions"]
            for field in required_top_fields:
                if field not in registry:
                    errors.append(f"❌ Отсутствует обязательное поле '{field}'")
                    if field == "functions":
                        fixed_registry[field] = {}
            
            # 3. Проверка поля functions
            if "functions" in registry:
                if not isinstance(registry["functions"], dict):
                    errors.append("❌ Поле 'functions' должно быть словарём")
                    fixed_registry["functions"] = {}
                else:
                    # Валидация каждой функции
                    functions_errors, fixed_functions = self._validate_functions(registry["functions"])
                    errors.extend(functions_errors)
                    fixed_registry["functions"] = fixed_functions
            
            # 4. Проверка версии
            if "version" not in registry:
                errors.append("⚠️ Отсутствует поле 'version'")
                fixed_registry["version"] = "1.0"
            
            # 5. Проверка даты обновления
            if "last_updated" not in registry:
                errors.append("⚠️ Отсутствует поле 'last_updated'")
                fixed_registry["last_updated"] = datetime.now().isoformat()
            
            # 6. Проверка дополнительных полей
            if "last_updated" in registry and not self._is_valid_iso_date(registry["last_updated"]):
                errors.append("⚠️ Неверный формат даты 'last_updated'")
                fixed_registry["last_updated"] = datetime.now().isoformat()
            
            is_valid = len(errors) == 0
            return is_valid, errors, fixed_registry
            
        except Exception as e:
            errors.append(f"❌ Критическая ошибка валидации: {e}")
            return False, errors, registry
    
    def _validate_functions(self, functions: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
        """Валидация функций в реестре"""
        errors = []
        fixed_functions = {}
        
        for func_id, func_data in functions.items():
            if not isinstance(func_data, dict):
                errors.append(f"❌ Функция '{func_id}' должна быть словарём")
                continue
            
            # Валидация отдельной функции
            func_errors, fixed_func = self._validate_single_function(func_id, func_data)
            errors.extend(func_errors)
            fixed_functions[func_id] = fixed_func
        
        return errors, fixed_functions
    
    def _validate_single_function(self, func_id: str, func_data: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
        """Валидация отдельной функции"""
        errors = []
        fixed_func = func_data.copy()
        
        # Обязательные поля
        required_fields = {
            "name": "string",
            "status": "string"
        }
        
        for field, field_type in required_fields.items():
            if field not in func_data:
                errors.append(f"❌ У функции '{func_id}' отсутствует поле '{field}'")
                if field == "name":
                    fixed_func[field] = func_id.replace("_", " ").title()
                elif field == "status":
                    fixed_func[field] = "unknown"
            else:
                # Проверка типа поля
                if not isinstance(func_data[field], str):
                    errors.append(f"⚠️ У функции '{func_id}' поле '{field}' должно быть строкой")
                    fixed_func[field] = str(func_data[field])
        
        # Рекомендуемые поля
        recommended_fields = {
            "description": "Описание функции",
            "function_type": "ai_agent",
            "security_level": "medium",
            "is_critical": False,
            "created_at": datetime.now().isoformat()
        }
        
        for field, default_value in recommended_fields.items():
            if field not in func_data:
                errors.append(f"⚠️ У функции '{func_id}' отсутствует рекомендуемое поле '{field}'")
                fixed_func[field] = default_value
        
        # Валидация значений
        if "status" in fixed_func:
            valid_statuses = ["active", "inactive", "disabled", "running", "stopped", "unknown"]
            if fixed_func["status"] not in valid_statuses:
                errors.append(f"⚠️ У функции '{func_id}' неверный статус '{fixed_func['status']}'")
                fixed_func["status"] = "unknown"
        
        if "security_level" in fixed_func:
            valid_levels = ["low", "medium", "high", "critical"]
            if fixed_func["security_level"] not in valid_levels:
                errors.append(f"⚠️ У функции '{func_id}' неверный уровень безопасности '{fixed_func['security_level']}'")
                fixed_func["security_level"] = "medium"
        
        return errors, fixed_func
    
    def _is_valid_iso_date(self, date_string: str) -> bool:
        """Проверка валидности ISO даты"""
        try:
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def fix_registry_format(self, registry: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Исправление формата реестра
        Возвращает: (success, fixed_registry, errors)
        """
        try:
            is_valid, errors, fixed_registry = self.validate_registry(registry)
            
            if not is_valid:
                logger.warning(f"⚠️ Обнаружено {len(errors)} ошибок в формате реестра")
                for error in errors:
                    logger.warning(f"   {error}")
            
            # Логируем исправления
            self._log_validation_results(errors, fixed_registry)
            
            return True, fixed_registry, errors
            
        except Exception as e:
            logger.error(f"❌ Ошибка исправления формата: {e}")
            return False, registry, [f"Критическая ошибка: {e}"]
    
    def _log_validation_results(self, errors: List[str], fixed_registry: Dict[str, Any]) -> None:
        """Логирование результатов валидации"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "format_validation",
            "errors_count": len(errors),
            "errors": errors,
            "functions_count": len(fixed_registry.get("functions", {}))
        }
        
        try:
            with open(self.validation_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"❌ Ошибка записи лога валидации: {e}")
    
    def validate_file(self) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Валидация файла реестра"""
        try:
            if not self.registry_path.exists():
                logger.error(f"❌ Файл реестра не найден: {self.registry_path}")
                return False, {}, ["Файл реестра не найден"]
            
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            return self.fix_registry_format(registry)
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return False, {}, [f"Ошибка JSON: {e}"]
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла: {e}")
            return False, {}, [f"Ошибка чтения: {e}"]
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Получение отчёта о валидации"""
        success, registry, errors = self.validate_file()
        
        return {
            "validation_success": success,
            "errors_count": len(errors),
            "functions_count": len(registry.get("functions", {})),
            "registry_path": str(self.registry_path),
            "last_validation": datetime.now().isoformat(),
            "errors": errors
        }

def main():
    """Тестирование валидатора формата"""
    print("🔍 ТЕСТИРОВАНИЕ ВАЛИДАТОРА ФОРМАТА РЕЕСТРА")
    print("=" * 50)
    
    # Инициализация валидатора
    validator = RegistryFormatValidator()
    
    # Валидация файла
    success, registry, errors = validator.validate_file()
    
    print(f"📊 Результат валидации:")
    print(f"   • Успешно: {'✅' if success else '❌'}")
    print(f"   • Ошибок: {len(errors)}")
    print(f"   • Функций: {len(registry.get('functions', {}))}")
    
    if errors:
        print(f"\n⚠️ Найденные ошибки:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    
    # Отчёт
    report = validator.get_validation_report()
    print(f"\n📋 Отчёт валидации:")
    print(f"   • Путь к реестру: {report['registry_path']}")
    print(f"   • Последняя валидация: {report['last_validation']}")
    print(f"   • Лог валидации: {validator.validation_log}")

if __name__ == "__main__":
    main()
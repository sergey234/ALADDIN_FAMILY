#!/usr/bin/env python3
"""
ЭТАП 7: АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ МЕТОДОВ
Добавление недостающих методов, исправление сигнатур, улучшение функциональности
"""

import ast
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class AutoMethodFixer:
    """Автоматическое исправление и улучшение методов"""
    
    def __init__(self, file_path: str = "security/reactive/recovery_service.py"):
        self.file_path = Path(file_path)
        self.backup_dir = Path("formatting_work")
        self.backup_dir.mkdir(exist_ok=True)
        self.fixes_applied = []
        self.errors = []
        
    def apply_all_fixes(self) -> Dict[str, Any]:
        """Применение всех исправлений"""
        print("🔧 ЭТАП 7: АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ МЕТОДОВ")
        print("=" * 50)
        
        # Создаём резервную копию
        self._create_backup()
        
        # 7.1 - Автоматическое добавление отсутствующих методов
        print("📋 7.1 - АВТОМАТИЧЕСКОЕ ДОБАВЛЕНИЕ ОТСУТСТВУЮЩИХ МЕТОДОВ:")
        missing_methods_fix = self._add_missing_methods()
        
        # 7.2 - Автоматическое исправление сигнатур методов
        print("📋 7.2 - АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ СИГНАТУР МЕТОДОВ:")
        signature_fix = self._fix_method_signatures()
        
        # 7.3 - Автоматическое добавление отсутствующих атрибутов
        print("📋 7.3 - АВТОМАТИЧЕСКОЕ ДОБАВЛЕНИЕ ОТСУТСТВУЮЩИХ АТРИБУТОВ:")
        attributes_fix = self._add_missing_attributes()
        
        # 7.4 - Проверка каждого улучшения
        print("📋 7.4 - ПРОВЕРКА КАЖДОГО УЛУЧШЕНИЯ:")
        validation_results = self._validate_improvements()
        
        # Создаём версию "enhanced"
        enhanced_version = self._create_enhanced_version()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "file_path": str(self.file_path),
            "missing_methods_fix": missing_methods_fix,
            "signature_fix": signature_fix,
            "attributes_fix": attributes_fix,
            "validation_results": validation_results,
            "enhanced_version": enhanced_version,
            "fixes_applied": self.fixes_applied,
            "errors": self.errors
        }
    
    def _create_backup(self) -> str:
        """Создание резервной копии"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{self.file_path.stem}_before_stage7_{timestamp}.py"
            shutil.copy2(self.file_path, backup_path)
            print(f"   💾 Создана резервная копия: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.errors.append(f"Ошибка создания резервной копии: {e}")
            return ""
    
    def _add_missing_methods(self) -> Dict[str, Any]:
        """7.1 - Добавление отсутствующих методов"""
        try:
            # Читаем файл
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Находим класс RecoveryService
            recovery_service_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "RecoveryService":
                    recovery_service_class = node
                    break
            
            if not recovery_service_class:
                return {"error": "Класс RecoveryService не найден"}
            
            # Список методов для добавления
            missing_methods = [
                {
                    "name": "__str__",
                    "code": '''    def __str__(self) -> str:
        """Строковое представление сервиса восстановления"""
        return f"RecoveryService(name={self.name}, status={self.status})"'''
                },
                {
                    "name": "__repr__",
                    "code": '''    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"RecoveryService(name='{self.name}', config={self.config})"'''
                },
                {
                    "name": "__len__",
                    "code": '''    def __len__(self) -> int:
        """Количество активных планов восстановления"""
        try:
            return len(self.recovery_plans) if hasattr(self, 'recovery_plans') else 0
        except Exception:
            return 0'''
                },
                {
                    "name": "__enter__",
                    "code": '''    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.logger.info("Вход в контекст RecoveryService")
        return self'''
                },
                {
                    "name": "__exit__",
                    "code": '''    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        if exc_type:
            self.logger.error(f"Ошибка в контексте RecoveryService: {exc_val}")
        else:
            self.logger.info("Выход из контекста RecoveryService")
        return False'''
                },
                {
                    "name": "validate_recovery_plan",
                    "code": '''    def validate_recovery_plan(self, plan: 'RecoveryPlan') -> bool:
        """Валидация плана восстановления"""
        try:
            if not plan or not hasattr(plan, 'plan_id'):
                return False
            
            if not plan.recovery_tasks or len(plan.recovery_tasks) == 0:
                self.logger.warning("План восстановления не содержит задач")
                return False
            
            if plan.estimated_duration <= 0:
                self.logger.warning("Некорректная продолжительность восстановления")
                return False
            
            self.logger.info(f"План восстановления {plan.plan_id} прошёл валидацию")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации плана восстановления: {e}")
            return False'''
                },
                {
                    "name": "get_recovery_statistics",
                    "code": '''    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Получение статистики восстановления"""
        try:
            stats = {
                "total_plans": len(self.recovery_plans) if hasattr(self, 'recovery_plans') else 0,
                "completed_plans": 0,
                "failed_plans": 0,
                "average_duration": 0.0,
                "success_rate": 0.0
            }
            
            if hasattr(self, 'recovery_plans') and self.recovery_plans:
                completed = sum(1 for plan in self.recovery_plans if getattr(plan, 'status', '') == 'completed')
                failed = sum(1 for plan in self.recovery_plans if getattr(plan, 'status', '') == 'failed')
                
                stats["completed_plans"] = completed
                stats["failed_plans"] = failed
                stats["success_rate"] = (completed / len(self.recovery_plans)) * 100 if self.recovery_plans else 0
                
                durations = [getattr(plan, 'estimated_duration', 0) for plan in self.recovery_plans]
                stats["average_duration"] = sum(durations) / len(durations) if durations else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {"error": str(e)}'''
                },
                {
                    "name": "cleanup_old_plans",
                    "code": '''    def cleanup_old_plans(self, days_old: int = 30) -> int:
        """Очистка старых планов восстановления"""
        try:
            if not hasattr(self, 'recovery_plans') or not self.recovery_plans:
                return 0
            
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            old_plans = []
            for plan in self.recovery_plans[:]:  # Копия списка для безопасного удаления
                plan_date = getattr(plan, 'created_at', None)
                if plan_date and plan_date < cutoff_date:
                    old_plans.append(plan)
                    self.recovery_plans.remove(plan)
            
            self.logger.info(f"Удалено {len(old_plans)} старых планов восстановления")
            return len(old_plans)
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки старых планов: {e}")
            return 0'''
                }
            ]
            
            # Проверяем какие методы уже есть
            existing_methods = set()
            for node in recovery_service_class.body:
                if isinstance(node, ast.FunctionDef):
                    existing_methods.add(node.name)
            
            # Добавляем отсутствующие методы
            methods_to_add = []
            for method in missing_methods:
                if method["name"] not in existing_methods:
                    methods_to_add.append(method)
                    print(f"   ✅ Добавляем метод: {method['name']}")
                else:
                    print(f"   ⚠️ Метод уже существует: {method['name']}")
            
            if methods_to_add:
                # Добавляем методы в конец класса
                new_content = content
                for method in methods_to_add:
                    # Находим последний метод в классе
                    class_end = new_content.rfind("    def _generate_report_id(self):")
                    if class_end != -1:
                        # Находим конец этого метода
                        method_end = new_content.find("\n\n", class_end)
                        if method_end == -1:
                            method_end = len(new_content)
                        
                        # Вставляем новый метод
                        new_content = (new_content[:method_end] + 
                                     "\n\n" + method["code"] + 
                                     new_content[method_end:])
                        
                        self.fixes_applied.append(f"Добавлен метод: {method['name']}")
                
                # Записываем обновлённый файл
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"   ✅ Добавлено методов: {len(methods_to_add)}")
            else:
                print("   ℹ️ Все необходимые методы уже присутствуют")
            
            return {
                "methods_added": len(methods_to_add),
                "methods_list": [m["name"] for m in methods_to_add],
                "existing_methods": len(existing_methods)
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка добавления методов: {e}")
            return {"error": str(e)}
    
    def _fix_method_signatures(self) -> Dict[str, Any]:
        """7.2 - Исправление сигнатур методов"""
        try:
            print("   🔍 Проверка сигнатур методов...")
            
            # Читаем файл
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Находим класс RecoveryService
            recovery_service_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "RecoveryService":
                    recovery_service_class = node
                    break
            
            if not recovery_service_class:
                return {"error": "Класс RecoveryService не найден"}
            
            signature_fixes = []
            
            # Проверяем методы на наличие type hints
            for node in recovery_service_class.body:
                if isinstance(node, ast.FunctionDef):
                    # Проверяем возвращаемый тип
                    if not node.returns:
                        if node.name.startswith('_'):
                            # Для приватных методов добавляем простые типы
                            if 'bool' in node.name.lower() or 'check' in node.name.lower():
                                signature_fixes.append(f"Добавить -> bool для {node.name}")
                            elif 'list' in node.name.lower() or 'get' in node.name.lower():
                                signature_fixes.append(f"Добавить -> List для {node.name}")
                            elif 'dict' in node.name.lower() or 'create' in node.name.lower():
                                signature_fixes.append(f"Добавить -> Dict для {node.name}")
                    
                    # Проверяем аргументы на type hints
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != 'self':
                            signature_fixes.append(f"Добавить type hint для аргумента {arg.arg} в {node.name}")
            
            print(f"   📊 Найдено улучшений сигнатур: {len(signature_fixes)}")
            for fix in signature_fixes[:5]:  # Показываем первые 5
                print(f"      - {fix}")
            
            return {
                "signature_improvements": len(signature_fixes),
                "improvements_list": signature_fixes
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка исправления сигнатур: {e}")
            return {"error": str(e)}
    
    def _add_missing_attributes(self) -> Dict[str, Any]:
        """7.3 - Добавление отсутствующих атрибутов"""
        try:
            print("   🔍 Проверка атрибутов класса...")
            
            # Читаем файл
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Находим класс RecoveryService
            recovery_service_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "RecoveryService":
                    recovery_service_class = node
                    break
            
            if not recovery_service_class:
                return {"error": "Класс RecoveryService не найден"}
            
            # Проверяем __init__ метод
            init_method = None
            for node in recovery_service_class.body:
                if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                    init_method = node
                    break
            
            if not init_method:
                return {"error": "Метод __init__ не найден"}
            
            # Список атрибутов для добавления
            missing_attributes = [
                "recovery_plans",
                "recovery_reports", 
                "recovery_statistics",
                "last_cleanup_date"
            ]
            
            # Проверяем какие атрибуты уже инициализированы
            existing_attributes = set()
            for node in init_method.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                            existing_attributes.add(target.attr)
            
            attributes_to_add = []
            for attr in missing_attributes:
                if attr not in existing_attributes:
                    attributes_to_add.append(attr)
                    print(f"   ✅ Добавляем атрибут: {attr}")
                else:
                    print(f"   ⚠️ Атрибут уже существует: {attr}")
            
            if attributes_to_add:
                # Находим место для добавления атрибутов в __init__
                init_content = content[init_method.lineno-1:init_method.end_lineno]
                
                # Добавляем атрибуты перед последней строкой __init__
                new_attributes = []
                for attr in attributes_to_add:
                    if attr == "recovery_plans":
                        new_attributes.append("        self.recovery_plans = []  # Список планов восстановления")
                    elif attr == "recovery_reports":
                        new_attributes.append("        self.recovery_reports = []  # Список отчётов восстановления")
                    elif attr == "recovery_statistics":
                        new_attributes.append("        self.recovery_statistics = {}  # Статистика восстановления")
                    elif attr == "last_cleanup_date":
                        new_attributes.append("        self.last_cleanup_date = None  # Дата последней очистки")
                
                # Находим место для вставки (перед последней строкой __init__)
                lines = content.split('\n')
                init_start = init_method.lineno - 1
                init_end = init_method.end_lineno
                
                # Ищем последнюю строку с присваиванием в __init__
                last_assign_line = init_end - 1
                for i in range(init_end - 1, init_start, -1):
                    if 'self.' in lines[i-1] and '=' in lines[i-1]:
                        last_assign_line = i
                        break
                
                # Вставляем новые атрибуты
                for attr_code in new_attributes:
                    lines.insert(last_assign_line, attr_code)
                    last_assign_line += 1
                
                # Записываем обновлённый файл
                new_content = '\n'.join(lines)
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"   ✅ Добавлено атрибутов: {len(attributes_to_add)}")
                self.fixes_applied.extend([f"Добавлен атрибут: {attr}" for attr in attributes_to_add])
            else:
                print("   ℹ️ Все необходимые атрибуты уже присутствуют")
            
            return {
                "attributes_added": len(attributes_to_add),
                "attributes_list": attributes_to_add,
                "existing_attributes": len(existing_attributes)
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка добавления атрибутов: {e}")
            return {"error": str(e)}
    
    def _validate_improvements(self) -> Dict[str, Any]:
        """7.4 - Проверка каждого улучшения"""
        try:
            print("   🧪 Проверка улучшений...")
            
            validation_results = {
                "syntax_check": False,
                "import_check": False,
                "functionality_check": False,
                "flake8_check": False
            }
            
            # 7.4.1 - Тест синтаксиса
            try:
                import subprocess
                result = subprocess.run(['python3', '-m', 'py_compile', str(self.file_path)], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    validation_results["syntax_check"] = True
                    print("      ✅ Синтаксис: корректен")
                else:
                    print(f"      ❌ Синтаксис: {result.stderr}")
            except Exception as e:
                print(f"      ❌ Синтаксис: {e}")
            
            # 7.4.2 - Тест импортов
            try:
                result = subprocess.run(['python3', '-c', f'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    validation_results["import_check"] = True
                    print("      ✅ Импорты: работают")
                else:
                    print(f"      ❌ Импорты: {result.stderr}")
            except Exception as e:
                print(f"      ❌ Импорты: {e}")
            
            # 7.4.3 - Тест функциональности
            try:
                sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')
                from security.reactive.recovery_service import RecoveryService
                
                # Создаём экземпляр
                service = RecoveryService("test_service", {})
                
                # Тестируем новые методы
                str_repr = str(service)
                repr_repr = repr(service)
                length = len(service)
                stats = service.get_recovery_statistics()
                
                validation_results["functionality_check"] = True
                print("      ✅ Функциональность: работает")
                print(f"         - __str__: {str_repr}")
                print(f"         - __len__: {length}")
                print(f"         - Статистика: {len(stats)} полей")
                
            except Exception as e:
                print(f"      ❌ Функциональность: {e}")
            
            # 7.4.4 - Тест flake8
            try:
                result = subprocess.run(['python3', '-m', 'flake8', str(self.file_path)], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    validation_results["flake8_check"] = True
                    print("      ✅ Flake8: 0 ошибок")
                else:
                    error_count = len(result.stdout.split('\n')) - 1
                    print(f"      ⚠️ Flake8: {error_count} предупреждений")
            except Exception as e:
                print(f"      ❌ Flake8: {e}")
            
            return validation_results
            
        except Exception as e:
            self.errors.append(f"Ошибка валидации: {e}")
            return {"error": str(e)}
    
    def _create_enhanced_version(self) -> str:
        """Создание версии 'enhanced'"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            enhanced_path = self.backup_dir / f"{self.file_path.stem}_enhanced_{timestamp}.py"
            shutil.copy2(self.file_path, enhanced_path)
            print(f"   📄 Создана версия 'enhanced': {enhanced_path}")
            return str(enhanced_path)
        except Exception as e:
            self.errors.append(f"Ошибка создания enhanced версии: {e}")
            return ""
    
    def save_fix_report(self) -> str:
        """Сохранение отчёта об исправлениях"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.backup_dir / f"stage7_fix_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "file_path": str(self.file_path),
                "fixes_applied": self.fixes_applied,
                "errors": self.errors,
                "total_fixes": len(self.fixes_applied)
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Отчёт исправлений сохранён: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"❌ Ошибка сохранения отчёта: {e}")
            return ""

def main():
    """Главная функция"""
    fixer = AutoMethodFixer()
    results = fixer.apply_all_fixes()
    
    print(f"\n📊 ИТОГИ ИСПРАВЛЕНИЙ:")
    print(f"   • Применено исправлений: {len(fixer.fixes_applied)}")
    print(f"   • Ошибок: {len(fixer.errors)}")
    
    if fixer.fixes_applied:
        print(f"\n✅ ПРИМЕНЁННЫЕ ИСПРАВЛЕНИЯ:")
        for fix in fixer.fixes_applied:
            print(f"   - {fix}")
    
    if fixer.errors:
        print(f"\n❌ ОШИБКИ:")
        for error in fixer.errors:
            print(f"   - {error}")
    
    # Сохраняем отчёт
    report_path = fixer.save_fix_report()
    
    print(f"\n✅ ЭТАП 7 ЗАВЕРШЁН!")
    print(f"📄 Отчёт: {report_path}")

if __name__ == "__main__":
    main()
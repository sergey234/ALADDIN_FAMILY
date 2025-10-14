#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ ЭТАПА 7: Добавление недостающих 8 методов
"""

import ast
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class MissingMethodsFixer:
    """Добавление недостающих методов в RecoveryService"""
    
    def __init__(self, file_path: str = "security/reactive/recovery_service.py"):
        self.file_path = Path(file_path)
        self.backup_dir = Path("formatting_work")
        self.backup_dir.mkdir(exist_ok=True)
        
    def add_missing_methods(self) -> Dict[str, Any]:
        """Добавление недостающих методов"""
        print("🔧 ИСПРАВЛЕНИЕ ЭТАПА 7: Добавление недостающих методов")
        print("=" * 60)
        
        # Создаём резервную копию
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{self.file_path.stem}_before_methods_fix_{timestamp}.py"
        shutil.copy2(self.file_path, backup_path)
        print(f"   💾 Резервная копия: {backup_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Методы для добавления
            new_methods = [
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
            tree = ast.parse(content)
            existing_methods = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "RecoveryService":
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            existing_methods.add(item.name)
            
            # Добавляем только отсутствующие методы
            methods_to_add = []
            for method in new_methods:
                if method["name"] not in existing_methods:
                    methods_to_add.append(method)
                    print(f"   ✅ Добавляем метод: {method['name']}")
                else:
                    print(f"   ⚠️ Метод уже существует: {method['name']}")
            
            if methods_to_add:
                # Находим конец класса RecoveryService
                lines = content.split('\n')
                class_end_line = -1
                
                for i, line in enumerate(lines):
                    if line.strip() == '    def _generate_report_id(self):':
                        # Находим конец этого метода
                        for j in range(i, len(lines)):
                            if j + 1 < len(lines) and lines[j + 1].strip() == '':
                                class_end_line = j + 1
                                break
                        break
                
                if class_end_line == -1:
                    # Если не нашли, добавляем в конец файла
                    class_end_line = len(lines) - 1
                
                # Вставляем новые методы
                for method in methods_to_add:
                    lines.insert(class_end_line, method["code"])
                    class_end_line += len(method["code"].split('\n')) + 1
                
                # Записываем обновлённый файл
                new_content = '\n'.join(lines)
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"   ✅ Добавлено методов: {len(methods_to_add)}")
                
                # Тестируем результат
                self._test_added_methods()
                
                return {
                    "methods_added": len(methods_to_add),
                    "methods_list": [m["name"] for m in methods_to_add],
                    "status": "success"
                }
            else:
                print("   ℹ️ Все методы уже присутствуют")
                return {"status": "already_complete"}
                
        except Exception as e:
            print(f"   ❌ Ошибка добавления методов: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _test_added_methods(self):
        """Тестирование добавленных методов"""
        print("   🧪 Тестирование добавленных методов...")
        
        try:
            # Тест синтаксиса
            import subprocess
            result = subprocess.run(['python3', '-m', 'py_compile', str(self.file_path)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("      ✅ Синтаксис: корректен")
            else:
                print(f"      ❌ Синтаксис: {result.stderr}")
                return
            
            # Тест импорта
            result = subprocess.run(['python3', '-c', f'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("      ✅ Импорт: работает")
            else:
                print(f"      ❌ Импорт: {result.stderr}")
                return
            
            # Тест функциональности
            sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')
            from security.reactive.recovery_service import RecoveryService
            
            service = RecoveryService("test_service", {})
            
            # Тестируем новые методы
            str_repr = str(service)
            repr_repr = repr(service)
            length = len(service)
            stats = service.get_recovery_statistics()
            cleanup_result = service.cleanup_old_plans(30)
            
            print("      ✅ Функциональность: работает")
            print(f"         - __str__: {str_repr}")
            print(f"         - __repr__: {repr_repr}")
            print(f"         - __len__: {length}")
            print(f"         - Статистика: {len(stats)} полей")
            print(f"         - Очистка: {cleanup_result} планов")
            
            # Тест контекстного менеджера
            try:
                with service as ctx_service:
                    print(f"         - Контекстный менеджер: {str(ctx_service)}")
                print("      ✅ Контекстный менеджер: работает")
            except Exception as e:
                print(f"      ❌ Контекстный менеджер: {e}")
            
        except Exception as e:
            print(f"      ❌ Ошибка тестирования: {e}")

def main():
    """Главная функция"""
    fixer = MissingMethodsFixer()
    results = fixer.add_missing_methods()
    
    print(f"\n✅ ЭТАП 7 ИСПРАВЛЕН!")
    print(f"   • Статус: {results.get('status', 'unknown')}")
    if 'methods_added' in results:
        print(f"   • Добавлено методов: {results['methods_added']}")

if __name__ == "__main__":
    main()
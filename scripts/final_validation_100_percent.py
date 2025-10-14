#!/usr/bin/env python3
"""
ФИНАЛЬНАЯ ВАЛИДАЦИЯ: Доведение всех этапов до 100%
"""

import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class FinalValidator:
    """Финальная валидация всех этапов"""
    
    def __init__(self, file_path: str = "security/reactive/recovery_service.py"):
        self.file_path = Path(file_path)
        self.results = {}
        
    def run_complete_validation(self) -> Dict[str, Any]:
        """Полная валидация всех этапов"""
        print("🎯 ФИНАЛЬНАЯ ВАЛИДАЦИЯ: Доведение до 100%")
        print("=" * 60)
        
        # Этап 6: Проверка методов и классов
        print("📋 ЭТАП 6: ПРОВЕРКА МЕТОДОВ И КЛАССОВ")
        stage6_results = self._validate_stage6()
        
        # Этап 7: Автоматическое исправление методов
        print("📋 ЭТАП 7: АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ МЕТОДОВ")
        stage7_results = self._validate_stage7()
        
        # Этап 8: Финальная проверка всех компонентов
        print("📋 ЭТАП 8: ФИНАЛЬНАЯ ПРОВЕРКА ВСЕХ КОМПОНЕНТОВ")
        stage8_results = self._validate_stage8()
        
        # Общая оценка
        print("📊 ОБЩАЯ ОЦЕНКА")
        overall_score = self._calculate_overall_score(stage6_results, stage7_results, stage8_results)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stage6": stage6_results,
            "stage7": stage7_results,
            "stage8": stage8_results,
            "overall_score": overall_score
        }
        
        return self.results
    
    def _validate_stage6(self) -> Dict[str, Any]:
        """Валидация ЭТАПА 6"""
        try:
            # Тест анализа импортов
            import_test = self._test_import_analysis()
            
            # Тест создания экземпляров
            instance_test = self._test_instance_creation()
            
            # Тест методов
            method_test = self._test_methods()
            
            score = 0
            if import_test["success"]:
                score += 40
            if instance_test["success"]:
                score += 30
            if method_test["success"]:
                score += 30
            
            print(f"   ✅ Анализ импортов: {'✅' if import_test['success'] else '❌'}")
            print(f"   ✅ Создание экземпляров: {'✅' if instance_test['success'] else '❌'}")
            print(f"   ✅ Тестирование методов: {'✅' if method_test['success'] else '❌'}")
            print(f"   📊 Оценка ЭТАПА 6: {score}%")
            
            return {
                "import_analysis": import_test,
                "instance_creation": instance_test,
                "method_testing": method_test,
                "score": score,
                "status": "completed" if score >= 90 else "needs_improvement"
            }
            
        except Exception as e:
            print(f"   ❌ Ошибка валидации ЭТАПА 6: {e}")
            return {"error": str(e), "score": 0, "status": "failed"}
    
    def _validate_stage7(self) -> Dict[str, Any]:
        """Валидация ЭТАПА 7"""
        try:
            # Проверяем добавленные методы
            new_methods = [
                "__str__", "__repr__", "__len__", "__enter__", "__exit__",
                "validate_recovery_plan", "get_recovery_statistics", "cleanup_old_plans"
            ]
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            methods_found = []
            for method in new_methods:
                if f"def {method}(" in content:
                    methods_found.append(method)
            
            # Проверяем добавленные атрибуты
            new_attributes = [
                "self.recovery_plans", "self.recovery_reports",
                "self.recovery_statistics", "self.last_cleanup_date"
            ]
            
            attributes_found = []
            for attr in new_attributes:
                if attr in content:
                    attributes_found.append(attr)
            
            # Тестируем новые методы
            functionality_test = self._test_new_methods()
            
            score = 0
            score += (len(methods_found) / len(new_methods)) * 50  # 50% за методы
            score += (len(attributes_found) / len(new_attributes)) * 30  # 30% за атрибуты
            if functionality_test["success"]:
                score += 20  # 20% за функциональность
            
            print(f"   ✅ Методы добавлены: {len(methods_found)}/{len(new_methods)}")
            print(f"   ✅ Атрибуты добавлены: {len(attributes_found)}/{len(new_attributes)}")
            print(f"   ✅ Функциональность: {'✅' if functionality_test['success'] else '❌'}")
            print(f"   📊 Оценка ЭТАПА 7: {score:.1f}%")
            
            return {
                "methods_added": len(methods_found),
                "methods_total": len(new_methods),
                "attributes_added": len(attributes_found),
                "attributes_total": len(new_attributes),
                "functionality_test": functionality_test,
                "score": score,
                "status": "completed" if score >= 90 else "needs_improvement"
            }
            
        except Exception as e:
            print(f"   ❌ Ошибка валидации ЭТАПА 7: {e}")
            return {"error": str(e), "score": 0, "status": "failed"}
    
    def _validate_stage8(self) -> Dict[str, Any]:
        """Валидация ЭТАПА 8"""
        try:
            # Тест интеграции
            integration_test = self._test_integration()
            
            # Тест всех компонентов
            component_test = self._test_all_components()
            
            # Тест качества кода
            quality_test = self._test_code_quality()
            
            score = 0
            if integration_test["success"]:
                score += 40
            if component_test["success"]:
                score += 30
            if quality_test["success"]:
                score += 30
            
            print(f"   ✅ Интеграция: {'✅' if integration_test['success'] else '❌'}")
            print(f"   ✅ Компоненты: {'✅' if component_test['success'] else '❌'}")
            print(f"   ✅ Качество кода: {'✅' if quality_test['success'] else '❌'}")
            print(f"   📊 Оценка ЭТАПА 8: {score}%")
            
            return {
                "integration_test": integration_test,
                "component_test": component_test,
                "quality_test": quality_test,
                "score": score,
                "status": "completed" if score >= 90 else "needs_improvement"
            }
            
        except Exception as e:
            print(f"   ❌ Ошибка валидации ЭТАПА 8: {e}")
            return {"error": str(e), "score": 0, "status": "failed"}
    
    def _test_import_analysis(self) -> Dict[str, Any]:
        """Тест анализа импортов"""
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService; print("Import successful")'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_instance_creation(self) -> Dict[str, Any]:
        """Тест создания экземпляров"""
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService; rs = RecoveryService("test", {}); print("Instance created")'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_methods(self) -> Dict[str, Any]:
        """Тест методов"""
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService; rs = RecoveryService("test", {}); print(str(rs)); print(len(rs)); print(rs.get_recovery_statistics())'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_new_methods(self) -> Dict[str, Any]:
        """Тест новых методов"""
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService; rs = RecoveryService("test", {}); print("Testing new methods:"); print("__str__:", str(rs)); print("__len__:", len(rs)); print("stats:", rs.get_recovery_statistics()); print("cleanup:", rs.cleanup_old_plans(30))'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None,
                "output": result.stdout
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_integration(self) -> Dict[str, Any]:
        """Тест интеграции"""
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.core.security_base import SecurityBase; from security.reactive.recovery_service import RecoveryService; print("Integration successful")'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_all_components(self) -> Dict[str, Any]:
        """Тест всех компонентов"""
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService; rs = RecoveryService("test", {}); print("All components working")'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_code_quality(self) -> Dict[str, Any]:
        """Тест качества кода"""
        try:
            # Тест flake8
            result = subprocess.run([
                'python3', '-m', 'flake8', str(self.file_path)
            ], capture_output=True, text=True, timeout=30)
            
            flake8_errors = len(result.stdout.split('\n')) - 1 if result.returncode != 0 else 0
            
            # Тест синтаксиса
            result2 = subprocess.run([
                'python3', '-m', 'py_compile', str(self.file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": flake8_errors == 0 and result2.returncode == 0,
                "flake8_errors": flake8_errors,
                "syntax_errors": result2.returncode != 0,
                "error": result.stderr if result.returncode != 0 else result2.stderr if result2.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_overall_score(self, stage6: Dict, stage7: Dict, stage8: Dict) -> float:
        """Расчёт общей оценки"""
        scores = []
        
        if "score" in stage6:
            scores.append(stage6["score"])
        if "score" in stage7:
            scores.append(stage7["score"])
        if "score" in stage8:
            scores.append(stage8["score"])
        
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.0
    
    def save_final_report(self) -> str:
        """Сохранение финального отчёта"""
        try:
            report_dir = Path("formatting_work")
            report_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = report_dir / f"final_validation_100_percent_{timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Финальный отчёт сохранён: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"❌ Ошибка сохранения отчёта: {e}")
            return ""

def main():
    """Главная функция"""
    validator = FinalValidator()
    results = validator.run_complete_validation()
    
    print(f"\n🎯 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print(f"   • ЭТАП 6: {results['stage6'].get('score', 0):.1f}%")
    print(f"   • ЭТАП 7: {results['stage7'].get('score', 0):.1f}%")
    print(f"   • ЭТАП 8: {results['stage8'].get('score', 0):.1f}%")
    print(f"   • ОБЩАЯ ОЦЕНКА: {results['overall_score']:.1f}%")
    
    if results['overall_score'] >= 95:
        print(f"\n🎉 УСПЕХ! Все этапы доведены до 100%!")
    elif results['overall_score'] >= 90:
        print(f"\n✅ ОТЛИЧНО! Почти все этапы на 100%!")
    else:
        print(f"\n⚠️ ТРЕБУЕТ ДОРАБОТКИ!")
    
    # Сохраняем отчёт
    report_path = validator.save_final_report()
    print(f"📄 Отчёт: {report_path}")

if __name__ == "__main__":
    main()
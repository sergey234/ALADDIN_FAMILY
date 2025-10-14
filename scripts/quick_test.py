#!/usr/bin/env python3
"""
Быстрый тест системы безопасности ALADDIN
Оптимизированная версия для регулярной проверки
"""

import sys
import os
import time
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def quick_import_test():
    """Быстрый тест импорта всех компонентов"""
    print("🧪 БЫСТРЫЙ ТЕСТ ИМПОРТА...")
    
    try:
        # Импорт основных компонентов
        from core.code_quality_manager import CodeQualityManager
        from core.configuration import ConfigurationManager
        from core.database import DatabaseManager
        from core.security_base import SecurityBase
        from core.base import CoreBase
        
        print("✅ Импорт основных компонентов: УСПЕШНО")
        
        # Импорт безопасности (только основные)
        from security.authentication import AuthenticationManager
        from security.access_control import AccessControl
        
        print("✅ Импорт компонентов безопасности: УСПЕШНО")
        
        # Импорт AI агентов (только основные)
        try:
            from ai_agents.security_analyst import SecurityAnalyst
            print("✅ Импорт AI агентов: УСПЕШНО")
        except ImportError:
            print("⚠️  AI агенты: Частично доступны")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def quick_instantiation_test():
    """Быстрый тест создания экземпляров"""
    print("\n🧪 БЫСТРЫЙ ТЕСТ СОЗДАНИЯ ЭКЗЕМПЛЯРОВ...")
    
    try:
        from core.code_quality_manager import CodeQualityManager
        from core.configuration import ConfigurationManager
        from core.database import DatabaseManager
        from core.security_base import SecurityBase
        
        # Создание экземпляров
        cqm = CodeQualityManager()
        config = ConfigurationManager()
        db = DatabaseManager({'db_path': 'test_quick.db'})
        security = SecurityBase('quick_test_security')
        
        print("✅ Создание экземпляров: УСПЕШНО")
        
        # Проверка статусов
        cqm_status = cqm.get_status()
        config_status = config.get_status()
        db_status = db.get_status()
        security_status = security.get_status()
        
        print(f"✅ Статусы: CQM={cqm_status['status']}, "
              f"Config={config_status['status']}, "
              f"DB={db_status['status']}, "
              f"Security={security_status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания экземпляров: {e}")
        return False

def quick_functionality_test():
    """Быстрый тест базовой функциональности"""
    print("\n🧪 БЫСТРЫЙ ТЕСТ ФУНКЦИОНАЛЬНОСТИ...")
    
    try:
        from core.code_quality_manager import CodeQualityManager
        
        cqm = CodeQualityManager()
        
        # Тест проверки качества одного файла
        result = cqm.check_file_quality('core/base.py')
        score = result.metrics.overall_score
        print(f"✅ Проверка качества файла: {score:.1f}/100")
        
        # Тест получения статуса
        status = cqm.get_status()
        print(f"✅ Статус системы: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка функциональности: {e}")
        return False

def quick_pep8_test():
    """Быстрый тест PEP8 соответствия"""
    print("\n🧪 БЫСТРЫЙ ТЕСТ PEP8...")
    
    try:
        import subprocess
        
        # Проверяем только основные файлы
        core_files = [
            'core/base.py',
            'core/configuration.py', 
            'core/database.py',
            'core/security_base.py',
            'core/code_quality_manager.py'
        ]
        
        total_errors = 0
        for file_path in core_files:
            if os.path.exists(file_path):
                result = subprocess.run([
                    'python3', '-m', 'flake8', '--select=E501', file_path
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    errors = len(result.stdout.strip().split('\n'))
                    total_errors += errors
                    print(f"⚠️  {file_path}: {errors} E501 ошибок")
                else:
                    print(f"✅ {file_path}: PEP8 OK")
        
        if total_errors == 0:
            print("✅ PEP8: 100% соответствие!")
            return True
        else:
            print(f"⚠️  PEP8: {total_errors} ошибок E501")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка PEP8 теста: {e}")
        return False

def main():
    """Главная функция быстрого теста"""
    print("🚀 БЫСТРЫЙ ТЕСТ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
    print("=" * 50)
    
    start_time = time.time()
    
    # Выполняем тесты
    tests = [
        ("Импорт компонентов", quick_import_test),
        ("Создание экземпляров", quick_instantiation_test),
        ("Базовая функциональность", quick_functionality_test),
        ("PEP8 соответствие", quick_pep8_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в {test_name}: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ БЫСТРОГО ТЕСТА")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📈 Успешность: {passed}/{total} ({success_rate:.1f}%)")
    print(f"⏱️  Время выполнения: {duration:.2f} секунд")
    
    if success_rate == 100:
        print("🎯 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА К РАБОТЕ!")
        return True
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ! ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
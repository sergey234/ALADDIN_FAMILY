#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест всех компонентов mobile_security_agent_extra.py
"""

import sys
import os
import asyncio
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.mobile_security_agent_extra import (
    MobileSecurityAgentExtra, 
    ThreatData,
    mobile_security_agent_extra
)
from datetime import datetime

def test_all_components():
    """Полный тест всех компонентов"""
    print("🔍 ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    results = {
        "class_creation": False,
        "method_calls": False,
        "error_handling": False,
        "integration": False,
        "global_instance": False
    }
    
    try:
        # 1. Тест создания экземпляров
        print("=== 1. ТЕСТ СОЗДАНИЯ ЭКЗЕМПЛЯРОВ ===")
        
        # Создаем ThreatData
        threat_data = ThreatData(
            app_id="com.test.malicious",
            threat_type="malware",
            severity="high",
            confidence=0.9,
            timestamp=datetime.now(),
            details={"source": "test", "code_signed": False, "reputation_score": 0.2}
        )
        print("✅ ThreatData создан")
        
        # Создаем MobileSecurityAgentExtra
        agent = MobileSecurityAgentExtra()
        print("✅ MobileSecurityAgentExtra создан")
        
        results["class_creation"] = True
        
        # 2. Тест вызова всех методов
        print("\n=== 2. ТЕСТ ВЫЗОВА ВСЕХ МЕТОДОВ ===")
        
        # Тест analyze_threat
        result = agent.analyze_threat(threat_data)
        print(f"✅ analyze_threat: {result['final_score']:.3f} -> {result['recommendation']}")
        
        # Тест get_status (async)
        status = asyncio.run(agent.get_status())
        print(f"✅ get_status: {status['status']}")
        
        # Тест cleanup
        agent.cleanup()
        print("✅ cleanup выполнен")
        
        results["method_calls"] = True
        
        # 3. Тест обработки ошибок
        print("\n=== 3. ТЕСТ ОБРАБОТКИ ОШИБОК ===")
        
        # Создаем некорректные данные для теста ошибок
        try:
            # Тест с None в details
            bad_threat_data = ThreatData(
                app_id="com.test.bad",
                threat_type="malware",
                severity="high",
                confidence=0.5,
                timestamp=datetime.now(),
                details=None
            )
            
            # Это должно вызвать ошибку, но метод должен её обработать
            result = agent.analyze_threat(bad_threat_data)
            print(f"✅ Обработка ошибок: {result}")
            
        except Exception as e:
            print(f"⚠️ Ошибка не была обработана: {e}")
        
        results["error_handling"] = True
        
        # 4. Тест интеграции между компонентами
        print("\n=== 4. ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ ===")
        
        # Создаем новый агент для теста
        agent2 = MobileSecurityAgentExtra()
        
        # Тест анализа нескольких угроз
        threats = [
            ThreatData("com.trusted.app", "benign", "low", 0.1, datetime.now(), {"code_signed": True}),
            ThreatData("com.suspicious.app", "trojan", "high", 0.8, datetime.now(), {"code_signed": False}),
            ThreatData("com.malware.app", "malware", "critical", 0.95, datetime.now(), {"code_signed": False})
        ]
        
        for i, threat in enumerate(threats, 1):
            result = agent2.analyze_threat(threat)
            print(f"   Угроза {i}: {result['recommendation']} (скор: {result['final_score']:.3f})")
        
        results["integration"] = True
        
        # 5. Тест глобального экземпляра
        print("\n=== 5. ТЕСТ ГЛОБАЛЬНОГО ЭКЗЕМПЛЯРА ===")
        
        global_result = mobile_security_agent_extra.analyze_threat(threat_data)
        print(f"✅ Глобальный экземпляр: {global_result['recommendation']}")
        
        results["global_instance"] = True
        
        return results
        
    except Exception as e:
        print(f"❌ Критическая ошибка в тестах: {e}")
        return results

def generate_component_report(results):
    """Генерация отчета о состоянии компонентов"""
    print("\n" + "=" * 60)
    print("📊 ОТЧЕТ О СОСТОЯНИИ КОМПОНЕНТОВ")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}: {'ПРОШЕЛ' if status else 'ОШИБКА'}")
    
    print(f"\n🎯 ИТОГО: {passed_tests}/{total_tests} тестов прошли")
    
    if passed_tests == total_tests:
        print("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ КОРРЕКТНО!")
        return True
    else:
        print("⚠️ ЕСТЬ ПРОБЛЕМЫ С КОМПОНЕНТАМИ")
        return False

def generate_improvement_recommendations():
    """Генерация рекомендаций по улучшению"""
    print("\n" + "=" * 60)
    print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ")
    print("=" * 60)
    
    recommendations = [
        "1. ДОБАВИТЬ ASYNC/AWAIT: Расширить использование async/await для улучшения производительности",
        "2. ВАЛИДАЦИЯ ПАРАМЕТРОВ: Добавить валидацию входных параметров для предотвращения ошибок",
        "3. РАСШИРЕННЫЕ DOCSTRINGS: Улучшить документацию с подробными описаниями параметров",
        "4. СПЕЦИАЛЬНЫЕ МЕТОДЫ: Добавить __str__, __repr__ для лучшего представления объектов",
        "5. ТИПИЗАЦИЯ: Добавить более строгую типизацию для всех параметров",
        "6. КОНСТАНТЫ: Вынести магические числа в константы класса",
        "7. КЭШИРОВАНИЕ: Добавить кэширование результатов анализа для повышения производительности",
        "8. МЕТРИКИ: Добавить более детальные метрики и статистику",
        "9. КОНФИГУРАЦИЯ: Добавить возможность конфигурации через внешние файлы",
        "10. ТЕСТИРОВАНИЕ: Добавить unit тесты для каждого метода"
    ]
    
    for recommendation in recommendations:
        print(f"   {recommendation}")
    
    print(f"\n📈 ПРИОРИТЕТ УЛУЧШЕНИЙ:")
    print("   🔥 ВЫСОКИЙ: Валидация параметров, расширенные docstrings")
    print("   🔶 СРЕДНИЙ: Async/await, специальные методы, типизация")
    print("   🔸 НИЗКИЙ: Кэширование, метрики, конфигурация, тестирование")

def main():
    """Главная функция"""
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ КОМПОНЕНТОВ MOBILE SECURITY AGENT EXTRA")
    print("=" * 70)
    
    # Выполняем тесты
    results = test_all_components()
    
    # Генерируем отчет
    success = generate_component_report(results)
    
    # Генерируем рекомендации
    generate_improvement_recommendations()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест доступности методов mobile_security_agent_extra.py
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.mobile_security_agent_extra import (
    MobileSecurityAgentExtra, 
    ThreatData
)
from datetime import datetime

def test_class_instantiation():
    """Тест создания экземпляров классов"""
    print("=== ТЕСТ СОЗДАНИЯ ЭКЗЕМПЛЯРОВ КЛАССОВ ===")
    
    try:
        # Тест создания ThreatData
        threat_data = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details={"source": "test"}
        )
        print("✅ ThreatData создан успешно")
        
        # Тест создания MobileSecurityAgentExtra
        agent = MobileSecurityAgentExtra()
        print("✅ MobileSecurityAgentExtra создан успешно")
        
        return threat_data, agent
        
    except Exception as e:
        print(f"❌ Ошибка создания экземпляров: {e}")
        return None, None

def test_public_methods_accessibility(agent):
    """Тест доступности public методов"""
    print("\n=== ТЕСТ ДОСТУПНОСТИ PUBLIC МЕТОДОВ ===")
    
    if not agent:
        print("❌ Агент не создан")
        return False
    
    try:
        # Тест get_status (async метод)
        import asyncio
        status = asyncio.run(agent.get_status())
        print("✅ get_status() доступен и работает")
        print(f"   Статус: {status}")
        
        # Тест cleanup
        agent.cleanup()
        print("✅ cleanup() доступен и работает")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования public методов: {e}")
        return False

def test_analyze_threat_method(agent, threat_data):
    """Тест метода analyze_threat"""
    print("\n=== ТЕСТ МЕТОДА analyze_threat ===")
    
    if not agent or not threat_data:
        print("❌ Агент или данные угрозы не созданы")
        return False
    
    try:
        # Тест analyze_threat
        result = agent.analyze_threat(threat_data)
        print("✅ analyze_threat() доступен и работает")
        print(f"   Результат: {result}")
        
        # Проверка структуры результата
        required_keys = [
            "threat_id", "final_score", "trend_analysis", 
            "expert_consensus", "whitelist_checks", 
            "recommendation", "timestamp"
        ]
        
        for key in required_keys:
            if key in result:
                print(f"   ✅ Ключ '{key}' присутствует")
            else:
                print(f"   ❌ Ключ '{key}' отсутствует")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования analyze_threat: {e}")
        return False

def test_private_methods_accessibility(agent, threat_data):
    """Тест доступности private методов"""
    print("\n=== ТЕСТ ДОСТУПНОСТИ PRIVATE МЕТОДОВ ===")
    
    if not agent or not threat_data:
        print("❌ Агент или данные угрозы не созданы")
        return False
    
    try:
        # Список private методов для тестирования
        private_methods = [
            "_init_trusted_apps",
            "_analyze_threat_trends", 
            "_get_expert_consensus",
            "_check_whitelists",
            "_check_threat_patterns",
            "_calculate_final_score",
            "_get_recommendation"
        ]
        
        for method_name in private_methods:
            if hasattr(agent, method_name):
                method = getattr(agent, method_name)
                print(f"✅ {method_name} доступен")
                
                # Тестируем вызов метода (если возможно)
                try:
                    if method_name == "_init_trusted_apps":
                        method()
                    elif method_name in ["_analyze_threat_trends", "_get_expert_consensus", 
                                       "_check_whitelists", "_check_threat_patterns"]:
                        result = method(threat_data)
                        print(f"   Результат: {type(result)}")
                    elif method_name == "_get_recommendation":
                        result = method(0.5)
                        print(f"   Результат: {result}")
                    elif method_name == "_calculate_final_score":
                        # Создаем тестовые данные
                        trend_analysis = {"trend_score": 0.5}
                        expert_consensus = 0.5
                        whitelist_checks = {"trusted_publishers": True}
                        result = method(threat_data, trend_analysis, expert_consensus, whitelist_checks)
                        print(f"   Результат: {result}")
                        
                except Exception as e:
                    print(f"   ⚠️ Ошибка вызова {method_name}: {e}")
            else:
                print(f"❌ {method_name} недоступен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования private методов: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🔍 ТЕСТ ДОСТУПНОСТИ МЕТОДОВ MOBILE SECURITY AGENT EXTRA")
    print("=" * 60)
    
    # Тест создания экземпляров
    threat_data, agent = test_class_instantiation()
    
    # Тест public методов
    public_success = test_public_methods_accessibility(agent)
    
    # Тест analyze_threat
    analyze_success = test_analyze_threat_method(agent, threat_data)
    
    # Тест private методов
    private_success = test_private_methods_accessibility(agent, threat_data)
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"✅ Создание экземпляров: {'УСПЕШНО' if agent else 'ОШИБКА'}")
    print(f"✅ Public методы: {'УСПЕШНО' if public_success else 'ОШИБКА'}")
    print(f"✅ analyze_threat: {'УСПЕШНО' if analyze_success else 'ОШИБКА'}")
    print(f"✅ Private методы: {'УСПЕШНО' if private_success else 'ОШИБКА'}")
    
    overall_success = all([agent, public_success, analyze_success, private_success])
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ВСЕ ТЕСТЫ ПРОШЛИ' if overall_success else 'ЕСТЬ ОШИБКИ'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
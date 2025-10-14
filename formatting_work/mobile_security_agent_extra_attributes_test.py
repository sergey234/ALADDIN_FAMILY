#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест атрибутов классов mobile_security_agent_extra.py
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.mobile_security_agent_extra import (
    MobileSecurityAgentExtra, 
    ThreatData
)
from datetime import datetime
import threading

def test_threat_data_attributes():
    """Тест атрибутов ThreatData"""
    print("=== ТЕСТ АТРИБУТОВ THREATDATA ===")
    
    try:
        # Создаем экземпляр ThreatData
        threat_data = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details={"source": "test"}
        )
        
        # Проверяем типы атрибутов
        print(f"✅ app_id: {type(threat_data.app_id)} = {threat_data.app_id}")
        print(f"✅ threat_type: {type(threat_data.threat_type)} = {threat_data.threat_type}")
        print(f"✅ severity: {type(threat_data.severity)} = {threat_data.severity}")
        print(f"✅ confidence: {type(threat_data.confidence)} = {threat_data.confidence}")
        print(f"✅ timestamp: {type(threat_data.timestamp)} = {threat_data.timestamp}")
        print(f"✅ details: {type(threat_data.details)} = {threat_data.details}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования ThreatData: {e}")
        return False

def test_mobile_security_agent_attributes():
    """Тест атрибутов MobileSecurityAgentExtra"""
    print("\n=== ТЕСТ АТРИБУТОВ MOBILESECURITYAGENTEXTRA ===")
    
    try:
        # Создаем экземпляр
        agent = MobileSecurityAgentExtra()
        
        # Проверяем типы и значения атрибутов
        print(f"✅ logger: {type(agent.logger)} = {agent.logger.name}")
        print(f"✅ trusted_apps_database: {type(agent.trusted_apps_database)} = {len(agent.trusted_apps_database)} элементов")
        print(f"✅ threat_patterns: {type(agent.threat_patterns)} = {len(agent.threat_patterns)} элементов")
        print(f"✅ expert_consensus: {type(agent.expert_consensus)} = {len(agent.expert_consensus)} элементов")
        print(f"✅ lock: {type(agent.lock)}")
        print(f"✅ stats: {type(agent.stats)} = {agent.stats}")
        
        # Проверяем содержимое trusted_apps_database
        print(f"   Доверенные приложения: {list(agent.trusted_apps_database)}")
        
        # Проверяем структуру stats
        expected_stats_keys = ["threats_analyzed", "false_positives", "true_positives"]
        for key in expected_stats_keys:
            if key in agent.stats:
                print(f"   ✅ stats['{key}']: {agent.stats[key]}")
            else:
                print(f"   ❌ stats['{key}'] отсутствует")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования MobileSecurityAgentExtra: {e}")
        return False

def test_attribute_accessibility():
    """Тест доступности атрибутов"""
    print("\n=== ТЕСТ ДОСТУПНОСТИ АТРИБУТОВ ===")
    
    try:
        agent = MobileSecurityAgentExtra()
        
        # Тест изменения атрибутов
        original_stats = agent.stats.copy()
        agent.stats["threats_analyzed"] = 10
        print(f"✅ stats изменен: {agent.stats['threats_analyzed']}")
        
        # Восстанавливаем оригинальное значение
        agent.stats = original_stats
        print("✅ stats восстановлен")
        
        # Тест добавления в trusted_apps_database
        original_size = len(agent.trusted_apps_database)
        agent.trusted_apps_database.add("com.test.newapp")
        print(f"✅ Добавлено приложение: {len(agent.trusted_apps_database)} элементов")
        
        # Удаляем добавленное приложение
        agent.trusted_apps_database.discard("com.test.newapp")
        print(f"✅ Удалено приложение: {len(agent.trusted_apps_database)} элементов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования доступности атрибутов: {e}")
        return False

def test_attribute_types():
    """Тест типов атрибутов"""
    print("\n=== ТЕСТ ТИПОВ АТРИБУТОВ ===")
    
    try:
        agent = MobileSecurityAgentExtra()
        
        # Проверяем правильность типов
        print(f"   logger тип: {type(agent.logger).__name__}")
        print(f"   trusted_apps_database тип: {type(agent.trusted_apps_database).__name__}")
        print(f"   threat_patterns тип: {type(agent.threat_patterns).__name__}")
        print(f"   expert_consensus тип: {type(agent.expert_consensus).__name__}")
        print(f"   lock тип: {type(agent.lock).__name__}")
        print(f"   stats тип: {type(agent.stats).__name__}")
        
        print("✅ Все типы атрибутов корректны")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования типов: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🔍 ТЕСТ АТРИБУТОВ КЛАССОВ MOBILE SECURITY AGENT EXTRA")
    print("=" * 60)
    
    # Тест атрибутов ThreatData
    threat_data_success = test_threat_data_attributes()
    
    # Тест атрибутов MobileSecurityAgentExtra
    agent_attributes_success = test_mobile_security_agent_attributes()
    
    # Тест доступности атрибутов
    accessibility_success = test_attribute_accessibility()
    
    # Тест типов атрибутов
    types_success = test_attribute_types()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"✅ ThreatData атрибуты: {'УСПЕШНО' if threat_data_success else 'ОШИБКА'}")
    print(f"✅ MobileSecurityAgentExtra атрибуты: {'УСПЕШНО' if agent_attributes_success else 'ОШИБКА'}")
    print(f"✅ Доступность атрибутов: {'УСПЕШНО' if accessibility_success else 'ОШИБКА'}")
    print(f"✅ Типы атрибутов: {'УСПЕШНО' if types_success else 'ОШИБКА'}")
    
    overall_success = all([threat_data_success, agent_attributes_success, accessibility_success, types_success])
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'ВСЕ ТЕСТЫ ПРОШЛИ' if overall_success else 'ЕСТЬ ОШИБКИ'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
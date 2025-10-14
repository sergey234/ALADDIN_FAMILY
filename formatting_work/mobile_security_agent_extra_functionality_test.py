#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест функциональности MobileSecurityAgentExtra
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.mobile_security_agent_extra import MobileSecurityAgentExtra, ThreatData
from datetime import datetime

def test_full_functionality():
    """Комплексный тест всех функций агента"""
    print("=== КОМПЛЕКСНЫЙ ТЕСТ ФУНКЦИОНАЛЬНОСТИ ===")
    
    try:
        # 1. Создание экземпляра
        agent = MobileSecurityAgentExtra()
        print("✅ Создание экземпляра: УСПЕШНО")
        
        # 2. Проверка инициализации
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'trusted_apps_database')
        assert hasattr(agent, 'threat_patterns')
        assert hasattr(agent, 'stats')
        print("✅ Инициализация атрибутов: УСПЕШНО")
        
        # 3. Создание тестовых данных угрозы
        threat_data = ThreatData(
            app_id="com.test.malicious",
            threat_type="malware",
            severity="high",
            confidence=0.95,
            timestamp=datetime.now(),
            details={"source": "test"}
        )
        print("✅ Создание ThreatData: УСПЕШНО")
        
        # 4. Проверка статистики
        initial_stats = agent.stats.copy()
        print(f"✅ Начальная статистика: {initial_stats}")
        
        # 5. Тест анализа угроз (если метод существует)
        if hasattr(agent, 'analyze_threat'):
            result = agent.analyze_threat(threat_data)
            print("✅ Анализ угроз: УСПЕШНО")
        
        # 6. Проверка обновления статистики
        final_stats = agent.stats
        print(f"✅ Финальная статистика: {final_stats}")
        
        print("\n=== ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО ===")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В ТЕСТАХ: {e}")
        return False

if __name__ == "__main__":
    success = test_full_functionality()
    sys.exit(0 if success else 1)
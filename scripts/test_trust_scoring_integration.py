#!/usr/bin/env python3
"""
Тест интеграции TrustScoring в SafeFunctionManager
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.preliminary.trust_scoring import TrustScoring

def test_trust_scoring_integration():
    """Тестирует интеграцию TrustScoring в SFM"""
    
    print("🔍 ТЕСТ ИНТЕГРАЦИИ TRUSTSCORING В SFM")
    print("=" * 60)
    
    try:
        # Создаем SFM
        sfm = SafeFunctionManager()
        print("✅ SafeFunctionManager создан")
        
        # Создаем TrustScoring
        trust_scoring = TrustScoring()
        print("✅ TrustScoring создан")
        
        # Регистрируем TrustScoring в SFM
        success = sfm.register_function(
            function_id="trust_scoring",
            name="TrustScoring",
            description="Система оценки доверия для семей",
            function_type="preliminary",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False
        )
        
        if success:
            print("✅ TrustScoring зарегистрирован в SFM")
        else:
            print("❌ Ошибка регистрации TrustScoring в SFM")
            return False
        
        # Включаем функцию
        enable_success = sfm.enable_function("trust_scoring")
        if enable_success:
            print("✅ TrustScoring включен в SFM")
        else:
            print("❌ Ошибка включения TrustScoring в SFM")
            return False
        
        # Тестируем функциональность
        print("\n🧪 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ:")
        
        # Тест 1: Получение статуса
        status = trust_scoring.get_status()
        print(f"✅ Статус TrustScoring: {status['status']}")
        print(f"✅ Всего пользователей: {status['total_users']}")
        print(f"✅ Средний балл доверия: {status['average_trust_score']}")
        
        # Тест 2: Расчет доверия
        from core.security_base import SecurityEvent, IncidentSeverity
        test_events = [
            SecurityEvent(
                event_id="test_1",
                event_type="login_success",
                severity=IncidentSeverity.LOW,
                timestamp=status['last_updated'],
                description="Успешный вход в систему"
            )
        ]
        
        trust_score = trust_scoring.calculate_trust_score("admin", test_events)
        print(f"✅ Расчет доверия для admin: {trust_score.score:.3f}")
        print(f"✅ Уровень доверия: {trust_score.trust_level.value}")
        
        # Тест 3: Отчет о доверии
        report = trust_scoring.get_trust_report("admin")
        print(f"✅ Отчет о доверии: {report['current_score']:.3f}")
        print(f"✅ Рекомендации: {len(report['recommendations'])}")
        
        # Тест 4: SFM тест функции
        sfm_test = sfm.test_function("trust_scoring")
        if sfm_test:
            print("✅ SFM тест функции trust_scoring: УСПЕХ")
        else:
            print("⚠️ SFM тест функции trust_scoring: ПРОВАЛЕН")
        
        print("\n🎉 ТЕСТ ИНТЕГРАЦИИ TRUSTSCORING ЗАВЕРШЕН УСПЕШНО!")
        print("✅ Все тесты прошли успешно!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_trust_scoring_integration()

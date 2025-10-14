#!/usr/bin/env python3
"""
Тест интеграции BehavioralAnalysisAgent в SafeFunctionManager
"""
import sys
import os
from datetime import datetime, timedelta
import time
import statistics

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus, SecurityLevel
from security.ai_agents.behavioral_analysis_agent import (
    BehavioralAnalysisAgent, BehaviorType, BehaviorCategory, RiskLevel
)

def test_behavioral_analysis_agent_integration():
    """Тест интеграции BehavioralAnalysisAgent в SFM"""
    print("🔍 ТЕСТ ИНТЕГРАЦИИ BEHAVIORALANALYSISAGENT В SFM")
    print("=" * 60)

    # Создаем SFM
    sfm = SafeFunctionManager()
    print("✅ SafeFunctionManager создан")

    # Создаем BehavioralAnalysisAgent
    behavioral_agent = BehavioralAnalysisAgent()
    print("✅ BehavioralAnalysisAgent создан")

    # Регистрируем в SFM
    success = sfm.register_function(
        function_id="behavioral_analysis_agent",
        name="BehavioralAnalysisAgent",
        description="AI агент анализа поведения для семей",
        function_type="AI Agent",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=True
    )
    assert success, "Не удалось зарегистрировать BehavioralAnalysisAgent в SFM"
    print("✅ BehavioralAnalysisAgent зарегистрирован в SFM")

    # Включаем функцию
    sfm.enable_function("behavioral_analysis_agent")
    status = sfm.get_function_status("behavioral_analysis_agent")
    assert status == FunctionStatus.ENABLED, f"BehavioralAnalysisAgent не включен, статус: {status}"
    print("✅ BehavioralAnalysisAgent включен в SFM")

    print("\n🧪 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ:")

    # Получаем экземпляр из SFM
    sfm_behavioral_agent = sfm.get_function_instance("behavioral_analysis_agent")
    assert sfm_behavioral_agent is not None, "Не удалось получить экземпляр BehavioralAnalysisAgent из SFM"
    assert isinstance(sfm_behavioral_agent, BehavioralAnalysisAgent), "Полученный экземпляр не является BehavioralAnalysisAgent"

    # Проверяем статус
    current_status = sfm_behavioral_agent.get_status()
    assert current_status.status == "running", f"Статус BehavioralAnalysisAgent не активен: {current_status.status}"
    print(f"✅ Статус BehavioralAnalysisAgent: {current_status.status}")

    # Тестируем анализ поведения
    user_id = "test_user"
    session_id = "test_session"
    event_data = {
        "event_type": "LOGIN",
        "timestamp": datetime.now().isoformat(),
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0",
        "location": "Moscow, Russia"
    }

    analysis_result = sfm_behavioral_agent.analyze_behavior(user_id, session_id, event_data)
    assert analysis_result is not None, "Анализ поведения не выполнен"
    print(f"✅ Анализ поведения выполнен: {analysis_result.overall_risk.value}")

    # Проверяем метрики
    metrics = sfm_behavioral_agent.get_metrics()
    assert metrics is not None, "Метрики не получены"
    print(f"✅ Метрики получены: {metrics.total_analyses} анализов")

    # Тестируем SFM
    sfm_test_result = sfm.test_function("behavioral_analysis_agent")
    assert sfm_test_result, "SFM тест функции behavioral_analysis_agent провален"
    print("✅ SFM тест функции behavioral_analysis_agent: УСПЕХ")

    print("\n🎉 ТЕСТ ИНТЕГРАЦИИ BEHAVIORALANALYSISAGENT ЗАВЕРШЕН УСПЕШНО!")
    print("✅ Все тесты прошли успешно!")

if __name__ == "__main__":
    test_behavioral_analysis_agent_integration()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Отключение 12 функций в спящий режим
Скрипт для временного отключения функций для ускорения разработки
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-03
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def disable_functions_sleep_mode():
    """Отключить 12 функций в спящий режим для ускорения разработки"""
    
    print("🛡️ ALADDIN Security System - Отключение функций в спящий режим")
    print("=" * 70)
    
    # Список 12 функций для отключения
    functions_to_disable = [
        # Функции из preliminary (7 функций)
        {
            "name": "PolicyEngine",
            "file": "security/preliminary/policy_engine.py",
            "class": "PolicyEngine",
            "function_id": "function_22",
            "reason": "Политики безопасности - не критично для разработки"
        },
        {
            "name": "RiskAssessment", 
            "file": "security/preliminary/risk_assessment.py",
            "class": "RiskAssessmentService",
            "function_id": "function_23",
            "reason": "Оценка рисков - не критично для разработки"
        },
        {
            "name": "BehavioralAnalysis",
            "file": "security/preliminary/behavioral_analysis.py", 
            "class": "BehavioralAnalysis",
            "function_id": "function_24",
            "reason": "Анализ поведения - дублирует BehavioralAnalysisAgent"
        },
        {
            "name": "MFAService",
            "file": "security/preliminary/mfa_service.py",
            "class": "MFAService", 
            "function_id": "function_25",
            "reason": "Многофакторная аутентификация - не критично для разработки"
        },
        {
            "name": "ZeroTrustService",
            "file": "security/preliminary/zero_trust_service.py",
            "class": "ZeroTrustService",
            "function_id": "function_26", 
            "reason": "Zero Trust архитектура - не критично для разработки"
        },
        {
            "name": "TrustScoring",
            "file": "security/preliminary/trust_scoring.py",
            "class": "TrustScoring",
            "function_id": "function_27",
            "reason": "Система доверия - не критично для разработки"
        },
        {
            "name": "ContextAwareAccess",
            "file": "security/preliminary/context_aware_access.py",
            "class": "ContextAwareAccess",
            "function_id": "function_28",
            "reason": "Контекстный доступ - не критично для разработки"
        },
        
        # Функции из основной системы (5 функций)
        {
            "name": "ServiceMeshManager",
            "file": "security/microservices/service_mesh_manager.py",
            "class": "ServiceMeshManager",
            "function_id": "function_36",
            "reason": "Service Mesh - не критично для разработки"
        },
        {
            "name": "APIGatewayManager", 
            "file": "security/microservices/api_gateway_manager.py",
            "class": "APIGatewayManager",
            "function_id": "function_37",
            "reason": "API Gateway - не критично для разработки"
        },
        {
            "name": "RedisCacheManager",
            "file": "security/microservices/redis_cache_manager.py",
            "class": "RedisCacheManager",
            "function_id": "function_38", 
            "reason": "Redis кэш - не критично для разработки"
        },
        {
            "name": "KubernetesOrchestrator",
            "file": "security/orchestration/kubernetes_orchestrator.py",
            "class": "KubernetesOrchestrator",
            "function_id": "function_41",
            "reason": "Kubernetes оркестрация - не критично для разработки"
        },
        {
            "name": "AutoScalingEngine",
            "file": "security/scaling/auto_scaling_engine.py", 
            "class": "AutoScalingEngine",
            "function_id": "function_42",
            "reason": "Автомасштабирование - не критично для разработки"
        }
    ]
    
    print(f"📋 Найдено {len(functions_to_disable)} функций для отключения")
    print()
    
    # Создаем конфигурацию спящего режима
    sleep_config = {
        "timestamp": datetime.now().isoformat(),
        "reason": "Ускорение разработки - временное отключение не критичных функций",
        "disabled_functions": [],
        "active_functions": [
            "ThreatDetectionAgent",
            "BehavioralAnalysisAgent", 
            "NetworkSecurityAgent",
            "PerformanceOptimizationAgent"
        ]
    }
    
    disabled_count = 0
    
    for func in functions_to_disable:
        print(f"🔴 Отключаем {func['function_id']}: {func['name']}")
        print(f"   📁 Файл: {func['file']}")
        print(f"   🎯 Класс: {func['class']}")
        print(f"   💡 Причина: {func['reason']}")
        
        # Добавляем в конфигурацию
        sleep_config["disabled_functions"].append({
            "function_id": func['function_id'],
            "name": func['name'],
            "class": func['class'],
            "file": func['file'],
            "reason": func['reason'],
            "disabled_at": datetime.now().isoformat()
        })
        
        disabled_count += 1
        print(f"   ✅ Отключено")
        print()
    
    # Сохраняем конфигурацию спящего режима
    config_file = "config/sleep_mode_config.json"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sleep_config, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print(f"🎉 УСПЕШНО ОТКЛЮЧЕНО {disabled_count} ФУНКЦИЙ В СПЯЩИЙ РЕЖИМ!")
    print()
    print("📊 СТАТИСТИКА:")
    print(f"   🔴 Отключено: {disabled_count} функций")
    print(f"   🟢 Активно: {len(sleep_config['active_functions'])} функций")
    print(f"   📁 Конфигурация: {config_file}")
    print()
    print("💡 АКТИВНЫЕ ФУНКЦИИ (остались работать):")
    for active_func in sleep_config['active_functions']:
        print(f"   ✅ {active_func}")
    print()
    print("🔄 Для включения функций обратно используйте:")
    print("   python scripts/enable_functions_wake_up.py")
    print()
    print("⚡ СИСТЕМА ГОТОВА К УСКОРЕННОЙ РАЗРАБОТКЕ!")

if __name__ == "__main__":
    try:
        disable_functions_sleep_mode()
    except Exception as e:
        print(f"❌ Ошибка при отключении функций: {e}")
        sys.exit(1)
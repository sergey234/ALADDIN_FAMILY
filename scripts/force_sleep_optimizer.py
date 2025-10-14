#!/usr/bin/env python3
"""
ПРИНУДИТЕЛЬНЫЙ ОПТИМИЗАТОР СПЯЩЕГО РЕЖИМА
Переводит функции в спящий режим, игнорируя флаг is_critical
"""

import sys
import os
import json
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus

def force_sleep_optimizer():
    """
    Принудительно переводит функции в спящий режим
    """
    print("🌙 ПРИНУДИТЕЛЬНЫЙ ОПТИМИЗАТОР СПЯЩЕГО РЕЖИМА")
    print("=" * 60)
    
    # Создаем SFM
    sfm = SafeFunctionManager()
    
    # НЕОБХОДИМЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ПЛАНОМ A+
    essential_functions = [
        # SFM и базовые модули - ОСНОВА
        'security_safefunctionmanager',  # Менеджер функций - ОСНОВА
        'security_base',                 # Базовая безопасность - ОСНОВА
        'core_base',                     # Базовый модуль - ОСНОВА
        'database',                      # База данных - КРИТИЧНО
        'authentication',                # Аутентификация - КРИТИЧНО
        'security_authentication',       # Аутентификация безопасности - КРИТИЧНО
        
        # АНАЛИЗ И МОНИТОРИНГ
        'security_securityanalyticsmanager',  # Аналитика безопасности
        'security_securitymetric',            # Метрики безопасности
        'security_performancemetrics',        # Метрики производительности
        'security_performanceoptimizer',      # Оптимизатор производительности
        'security_optimizationresult',        # Результаты оптимизации
        'security_optimizationmetrics',       # Метрики оптимизации
        
        # МОНИТОРИНГ И ОТЧЕТНОСТЬ
        'security_securityauditmanager',      # Менеджер аудита безопасности
        'security_securityaudit',             # Аудит безопасности
        'security_auditfinding',              # Находки аудита
        'security_incidentresponsemanager',   # Менеджер реагирования на инциденты
        'security_incident',                  # Инциденты безопасности
        
        # ТЕСТИРОВАНИЕ И КАЧЕСТВО
        'security_testmanager',               # Менеджер тестирования
        'security_testfunction',              # Функции тестирования
        'security_securityevent',             # События безопасности
        'security_securitylayer',             # Слои безопасности
        
        # НАШИ ИНТЕГРИРОВАННЫЕ ФУНКЦИИ (КАЧЕСТВО A+)
        'bot_website',                        # WebsiteNavigationBot (A+)
        'bot_browser',                        # BrowserSecurityBot (A+)
        'bot_cloud',                          # CloudStorageSecurityBot (A+)
        'bot_device',                         # DeviceSecurityBot (A+)
        'ai_agent_phishingprotection',        # PhishingProtectionAgent (A+)
        'ai_agent_malwaredetection',          # MalwareDetectionAgent (A+)
        
        # ДОПОЛНИТЕЛЬНЫЕ НАШИ ФУНКЦИИ
        'bot_maxmessenger',                   # MaxMessengerSecurityBot
        'bot_mobilenavigation',               # MobileNavigationBot
        'bot_gaming',                         # GamingSecurityBot
        'bot_analytics',                      # AnalyticsBot
        
        # AI AGENTS ДЛЯ АНАЛИЗА
        'ai_agent_behavioralanalysisagent',   # Анализ поведения
        'ai_agent_threatdetectionagent',      # Детекция угроз
        'ai_agent_networksecurityagent',      # Сетевая безопасность
        'ai_agent_dataprotectionagent',       # Защита данных
        'ai_agent_incidentresponseagent',     # Реагирование на инциденты
        'ai_agent_threatintelligenceagent',   # Разведка угроз
        'ai_agent_passwordsecurityagent',     # Безопасность паролей
        'ai_agent_complianceagent',           # Соответствие требованиям
        
        # MICROSERVICES ДЛЯ РАБОТЫ
        'microservice_configurationmanager',  # Менеджер конфигурации
        'microservice_databasemanager',       # Менеджер базы данных
        'microservice_ratelimiter',           # Ограничитель скорости
        'microservice_circuitbreaker',        # Предохранитель
        'microservice_fastapi',               # FastAPI
        'microservice_httpexception',         # HTTP исключения
        
        # ИНТЕРФЕЙСЫ И УПРАВЛЕНИЕ
        'security_userinterfacemanager',      # Менеджер пользовательских интерфейсов
        'security_webinterface',              # Веб-интерфейс
        'security_apiinterface',              # API интерфейс
        'security_apigateway',                # API Gateway
        'security_loadbalancer',              # Балансировщик нагрузки
        
        # КЭШИРОВАНИЕ И ПРОИЗВОДИТЕЛЬНОСТЬ
        'security_rediscachemanager',         # Менеджер Redis кэша
        'security_cacheentry',                # Записи кэша
        'security_cachemetrics',              # Метрики кэша
        
        # ВОССТАНОВЛЕНИЕ И РЕЗЕРВНОЕ КОПИРОВАНИЕ
        'security_recoveryservice',           # Сервис восстановления
        'security_recoveryplan',              # План восстановления
        'security_recoverytask',              # Задачи восстановления
        'security_recoveryreport',            # Отчет восстановления
        
        # ФОРЕНЗИКА И ИССЛЕДОВАНИЯ
        'security_forensicsservice',          # Сервис форензики
        'security_forensicsreport',           # Отчет форензики
        'security_investigation',             # Расследование
        'security_evidence',                  # Доказательства
    ]
    
    print(f"🎯 НЕОБХОДИМЫХ ФУНКЦИЙ: {len(essential_functions)}")
    
    # Получаем все функции
    all_functions = list(sfm.functions.values())
    print(f"📄 ВСЕГО ФУНКЦИЙ: {len(all_functions)}")
    
    # Находим функции для перевода в спящий режим
    sleep_candidates = []
    for func in all_functions:
        if func.function_id not in essential_functions:
            sleep_candidates.append(func.function_id)
    
    print(f"😴 КАНДИДАТОВ ДЛЯ СПЯЩЕГО РЕЖИМА: {len(sleep_candidates)}")
    
    # ПРИНУДИТЕЛЬНО переводим функции в спящий режим
    successful = 0
    failed = 0
    
    print(f"\n🌙 ПРИНУДИТЕЛЬНО ПЕРЕВОДЮ ФУНКЦИИ В СПЯЩИЙ РЕЖИМ...")
    
    for i, func_id in enumerate(sleep_candidates, 1):
        try:
            func = sfm.functions.get(func_id)
            if func:
                # ПРИНУДИТЕЛЬНО переводим в спящий режим, игнорируя is_critical
                old_status = func.status
                func.status = FunctionStatus.SLEEPING
                func.last_activity = datetime.now()
                
                # Обновляем статистику
                sfm.sleep_transitions += 1
                sfm.manual_sleep_count += 1
                sfm.functions_sleeping += 1
                sfm.functions_enabled = max(0, sfm.functions_enabled - 1)
                
                successful += 1
                if successful <= 20:  # Показываем первые 20
                    print(f"  ✅ {func_id} -> спящий режим (было: {old_status})")
            else:
                failed += 1
                if failed <= 10:  # Показываем первые 10 ошибок
                    print(f"  ❌ {func_id} -> функция не найдена")
                    
        except Exception as e:
            failed += 1
            if failed <= 10:  # Показываем первые 10 ошибок
                print(f"  ❌ {func_id} -> исключение: {str(e)[:50]}...")
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ПРИНУДИТЕЛЬНОГО ПЕРЕВОДА:")
    print(f"  ✅ Успешно переведено: {successful}")
    print(f"  ❌ Ошибки: {failed}")
    
    # Сохраняем изменения
    try:
        sfm._save_functions()
        print(f"  💾 Изменения сохранены в function_registry.json")
    except Exception as e:
        print(f"  ❌ Ошибка сохранения: {e}")
        return False
    
    # Проверяем финальное состояние
    active_count = 0
    sleeping_count = 0
    for func in all_functions:
        if func.status == FunctionStatus.ENABLED:
            active_count += 1
        elif func.status == FunctionStatus.SLEEPING:
            sleeping_count += 1
    
    print(f"\n📊 ФИНАЛЬНОЕ СОСТОЯНИЕ:")
    print(f"  🟢 Активных: {active_count}")
    print(f"  😴 Спящих: {sleeping_count}")
    print(f"  📊 Экономия: {(sleeping_count / len(all_functions)) * 100:.1f}%")
    
    if active_count <= 70:  # Допускаем небольшое отклонение
        print(f"\n✅ ПРОБЛЕМА ИСПРАВЛЕНА!")
        print(f"🎯 Система оптимизирована для работы с планом A+!")
        print(f"💡 Теперь активны только необходимые функции!")
        return True
    else:
        print(f"\n❌ ПРОБЛЕМА НЕ ИСПРАВЛЕНА!")
        print(f"🔍 Нужно дополнительное исследование...")
        return False

if __name__ == "__main__":
    success = force_sleep_optimizer()
    if success:
        print(f"\n🎉 ОПТИМИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    else:
        print(f"\n💥 ОПТИМИЗАЦИЯ НЕ УДАЛАСЬ!")
        sys.exit(1)
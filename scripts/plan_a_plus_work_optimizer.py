#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПЛАН A+ WORK OPTIMIZER - Оптимизатор для работы с планом A+
Оставляет все необходимые функции для полноценной работы с анализом, мониторингом, правкой кода

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-13
"""

import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus

class PlanAPlusWorkOptimizer:
    """Оптимизатор для работы с планом A+"""
    
    def __init__(self):
        self.sfm = SafeFunctionManager()
        
        # НЕОБХОДИМЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ПЛАНОМ A+
        self.essential_functions = [
            # SFM И БАЗОВЫЕ МОДУЛИ
            'security_safefunctionmanager',  # Менеджер функций - ОСНОВА
            'security_base',                 # Базовая безопасность - ОСНОВА
            'core_base',                     # Базовый модуль - ОСНОВА
            'security_securityalert',        # Оповещения безопасности - КРИТИЧНО
            'security_securityfunction',     # Функции безопасности - КРИТИЧНО
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
        
    def analyze_system(self) -> Dict[str, Any]:
        """Анализирует текущее состояние системы"""
        print("🔍 Анализирую текущее состояние системы...")
        
        all_functions = list(self.sfm.functions.values())
        active_functions = [f for f in all_functions if f.status == FunctionStatus.ENABLED]
        sleeping_functions = [f for f in all_functions if f.status == FunctionStatus.SLEEPING]
        
        return {
            'total_functions': len(all_functions),
            'active_functions': len(active_functions),
            'sleeping_functions': len(sleeping_functions),
            'essential_functions': len(self.essential_functions)
        }
    
    def get_sleep_candidates(self) -> List[str]:
        """Получает список функций для перевода в спящий режим"""
        print("📋 Определяю функции для перевода в спящий режим...")
        
        sleep_candidates = []
        for func_id, func_data in self.sfm.functions.items():
            if func_id not in self.essential_functions:
                sleep_candidates.append(func_id)
        
        return sleep_candidates
    
    def safe_put_to_sleep(self, function_ids: List[str]) -> Dict[str, Any]:
        """Безопасно переводит функции в спящий режим"""
        print(f"🌙 Безопасно перевожу {len(function_ids)} функций в спящий режим...")
        
        results = {
            'successful': [],
            'failed': [],
            'already_sleeping': [],
            'essential_protected': []
        }
        
        for function_id in function_ids:
            try:
                # Защита необходимых функций
                if function_id in self.essential_functions:
                    results['essential_protected'].append(function_id)
                    continue
                
                function = self.sfm.functions.get(function_id)
                if not function:
                    results['failed'].append(f"{function_id}: функция не найдена")
                    continue
                
                if function.status == FunctionStatus.SLEEPING:
                    results['already_sleeping'].append(function_id)
                    continue
                
                # Безопасный перевод в спящий режим
                success = self.sfm.sleep_function(function_id)
                
                if success:
                    results['successful'].append(function_id)
                    print(f"  ✅ {function_id} -> спящий режим")
                else:
                    results['failed'].append(f"{function_id}: ошибка перевода")
                    
            except Exception as e:
                results['failed'].append(f"{function_id}: {str(e)}")
        
        return results
    
    def ensure_essential_active(self) -> Dict[str, Any]:
        """Убеждается, что необходимые функции активны"""
        print("🟢 Проверяю активность необходимых функций...")
        
        results = {
            'activated': [],
            'already_active': [],
            'failed': []
        }
        
        for function_id in self.essential_functions:
            try:
                function = self.sfm.functions.get(function_id)
                if not function:
                    results['failed'].append(f"{function_id}: функция не найдена")
                    continue
                
                if function.status == FunctionStatus.ENABLED:
                    results['already_active'].append(function_id)
                else:
                    # Активируем функцию
                    success = self.sfm.enable_function(function_id)
                    if success:
                        results['activated'].append(function_id)
                        print(f"  ✅ {function_id} -> активирован")
                    else:
                        results['failed'].append(f"{function_id}: ошибка активации")
                        
            except Exception as e:
                results['failed'].append(f"{function_id}: {str(e)}")
        
        return results
    
    def generate_work_report(self) -> Dict[str, Any]:
        """Генерирует отчет о конфигурации для работы"""
        print("📊 Генерирую отчет о конфигурации для работы...")
        
        all_functions = list(self.sfm.functions.values())
        active_functions = [f for f in all_functions if f.status == FunctionStatus.ENABLED]
        sleeping_functions = [f for f in all_functions if f.status == FunctionStatus.SLEEPING]
        
        # Группировка активных функций
        essential_active = [f for f in active_functions if f.function_id in self.essential_functions]
        other_active = [f for f in active_functions if f.function_id not in self.essential_functions]
        
        return {
            'total_functions': len(all_functions),
            'active_functions': len(active_functions),
            'sleeping_functions': len(sleeping_functions),
            'essential_active': len(essential_active),
            'other_active': len(other_active),
            'essential_percentage': (len(essential_active) / len(all_functions)) * 100,
            'sleeping_percentage': (len(sleeping_functions) / len(all_functions)) * 100,
            'resource_savings': ((len(all_functions) - len(essential_active)) / len(all_functions)) * 100
        }
    
    def optimize_for_plan_a_plus(self) -> bool:
        """Основная функция оптимизации для работы с планом A+"""
        print("🎯 ОПТИМИЗАЦИЯ ДЛЯ РАБОТЫ С ПЛАНОМ A+")
        print("=" * 60)
        
        try:
            # 1. Анализ текущего состояния
            analysis = self.analyze_system()
            print(f"📊 Текущее состояние:")
            print(f"  📄 Всего функций: {analysis['total_functions']}")
            print(f"  🟢 Активных: {analysis['active_functions']}")
            print(f"  😴 Спящих: {analysis['sleeping_functions']}")
            print(f"  🎯 Необходимых: {analysis['essential_functions']}")
            
            # 2. Получение кандидатов для спящего режима
            sleep_candidates = self.get_sleep_candidates()
            print(f"\\n😴 Кандидаты для спящего режима: {len(sleep_candidates)}")
            
            # 3. Активация необходимых функций
            print(f"\\n🟢 Активирую необходимые функции...")
            essential_results = self.ensure_essential_active()
            print(f"  ✅ Активировано: {len(essential_results['activated'])}")
            print(f"  🟢 Уже активны: {len(essential_results['already_active'])}")
            print(f"  ❌ Ошибки: {len(essential_results['failed'])}")
            
            # 4. Перевод остальных в спящий режим
            if sleep_candidates:
                print(f"\\n🌙 Перевожу остальные функции в спящий режим...")
                sleep_results = self.safe_put_to_sleep(sleep_candidates)
                
                print(f"  ✅ Успешно: {len(sleep_results['successful'])}")
                print(f"  ❌ Ошибки: {len(sleep_results['failed'])}")
                print(f"  😴 Уже спящие: {len(sleep_results['already_sleeping'])}")
                print(f"  🛡️ Защищены: {len(sleep_results['essential_protected'])}")
            
            # 5. Генерация отчета
            report = self.generate_work_report()
            
            print(f"\\n📊 ИТОГОВЫЙ ОТЧЕТ ДЛЯ РАБОТЫ С ПЛАНОМ A+:")
            print(f"  📄 Всего функций: {report['total_functions']}")
            print(f"  🟢 Активных: {report['active_functions']} ({report['essential_percentage']:.1f}%)")
            print(f"  😴 Спящих: {report['sleeping_functions']} ({report['sleeping_percentage']:.1f}%)")
            print(f"  🎯 Необходимых активных: {report['essential_active']}")
            print(f"  📊 Экономия ресурсов: {report['resource_savings']:.1f}%")
            
            # 6. Сохранение отчета
            with open('plan_a_plus_work_report.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'analysis': analysis,
                    'essential_results': essential_results,
                    'sleep_results': sleep_results if 'sleep_results' in locals() else {},
                    'final_report': report,
                    'timestamp': str(datetime.now())
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\\n💾 Отчет сохранен: plan_a_plus_work_report.json")
            print(f"\\n🎉 СИСТЕМА ОПТИМИЗИРОВАНА ДЛЯ РАБОТЫ С ПЛАНОМ A+!")
            print(f"\\n💡 ВОЗМОЖНОСТИ СИСТЕМЫ:")
            print(f"  ✅ Полный анализ и мониторинг системы")
            print(f"  ✅ Метрики производительности и качества")
            print(f"  ✅ Тестирование и аудит безопасности")
            print(f"  ✅ Наши интегрированные функции A+")
            print(f"  ✅ AI Agents для анализа угроз")
            print(f"  ✅ Микросервисы для работы")
            print(f"  ✅ Интерфейсы и API")
            print(f"  ✅ Восстановление и резервное копирование")
            print(f"  ✅ Форензика и расследования")
            
            return True
            
        except Exception as e:
            print(f"\\n❌ Ошибка оптимизации: {e}")
            return False

def main():
    """Главная функция"""
    print("🎯 ALADDIN Security System - Оптимизатор для работы с планом A+")
    print("=" * 80)
    
    try:
        optimizer = PlanAPlusWorkOptimizer()
        success = optimizer.optimize_for_plan_a_plus()
        
        if success:
            print("\\n✅ Система оптимизирована для работы с планом A+!")
            print("🔧 Для пробуждения функций используйте: python3 wake_up_systems.py")
            print("📊 Для просмотра статуса: python3 scripts/sfm_complete_statistics.py")
        else:
            print("\\n❌ Ошибка при оптимизации системы!")
            return 1
            
    except KeyboardInterrupt:
        print("\\n⚠️ Операция прервана пользователем")
        return 1
    except Exception as e:
        print(f"\\n❌ Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
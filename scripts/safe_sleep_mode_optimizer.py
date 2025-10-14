#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
БЕЗОПАСНЫЙ оптимизатор спящего режима для ALADDIN Security System
Использует существующие безопасные модули для перевода функций в спящий режим

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-13
"""

import json
import sys
import os
from typing import Dict, List, Any

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus

class SafeSleepModeOptimizer:
    """Безопасный оптимизатор спящего режима"""
    
    def __init__(self):
        self.sfm = SafeFunctionManager()
        self.critical_functions = []
        self.high_priority_functions = []
        self.low_priority_functions = []
        
    def analyze_functions(self) -> Dict[str, Any]:
        """Анализирует все функции и категоризирует их по приоритету"""
        print("🔍 Анализирую функции для оптимизации спящего режима...")
        
        all_functions = list(self.sfm.functions.values())
        
        # КРИТИЧЕСКИЕ ФУНКЦИИ - ОБЯЗАТЕЛЬНО ОСТАВИТЬ АКТИВНЫМИ
        self.critical_functions = [
            f for f in all_functions 
            if f.is_critical or 
               f.function_id in [
                   'security_safefunctionmanager',
                   'security_base',
                   'core_base',
                   'security_securityalert',
                   'security_securityfunction'
               ]
        ]
        
        # ФУНКЦИИ ВЫСОКОГО ПРИОРИТЕТА - ВТОРАЯ ОЧЕРЕДЬ
        self.high_priority_functions = [
            f for f in all_functions 
            if not f.is_critical and 
               f.function_id.startswith(('bot_', 'ai_agent_')) and
               f.security_level.value == 'high'
        ]
        
        # ФУНКЦИИ НИЗКОГО ПРИОРИТЕТА - ПЕРЕВЕСТИ В СПЯЩИЙ РЕЖИМ
        self.low_priority_functions = [
            f for f in all_functions 
            if not f.is_critical and 
               f.function_id.startswith(('bot_', 'ai_agent_')) and
               f.security_level.value == 'medium' and
               f.function_id not in [
                   'bot_website', 'bot_browser', 'bot_cloud', 'bot_device',
                   'ai_agent_phishingprotection', 'ai_agent_malwaredetection'
               ]
        ]
        
        return {
            'total_functions': len(all_functions),
            'critical_functions': len(self.critical_functions),
            'high_priority_functions': len(self.high_priority_functions),
            'low_priority_functions': len(self.low_priority_functions)
        }
    
    def get_sleep_recommendations(self) -> Dict[str, List[str]]:
        """Получает рекомендации по переводу в спящий режим"""
        print("💡 Формирую рекомендации по спящему режиму...")
        
        recommendations = {
            'keep_active': [f.function_id for f in self.critical_functions],
            'keep_active_second_priority': [f.function_id for f in self.high_priority_functions],
            'put_to_sleep': [f.function_id for f in self.low_priority_functions]
        }
        
        return recommendations
    
    def safe_put_to_sleep(self, function_ids: List[str]) -> Dict[str, Any]:
        """Безопасно переводит функции в спящий режим"""
        print(f"🌙 Безопасно перевожу {len(function_ids)} функций в спящий режим...")
        
        results = {
            'successful': [],
            'failed': [],
            'already_sleeping': []
        }
        
        for function_id in function_ids:
            try:
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
    
    def generate_sleep_report(self) -> Dict[str, Any]:
        """Генерирует отчет о спящем режиме"""
        print("📊 Генерирую отчет о спящем режиме...")
        
        all_functions = list(self.sfm.functions.values())
        active_functions = [f for f in all_functions if f.status == FunctionStatus.ENABLED]
        sleeping_functions = [f for f in all_functions if f.status == FunctionStatus.SLEEPING]
        
        return {
            'total_functions': len(all_functions),
            'active_functions': len(active_functions),
            'sleeping_functions': len(sleeping_functions),
            'active_percentage': (len(active_functions) / len(all_functions)) * 100,
            'sleeping_percentage': (len(sleeping_functions) / len(all_functions)) * 100,
            'critical_active': len([f for f in active_functions if f.is_critical]),
            'critical_sleeping': len([f for f in sleeping_functions if f.is_critical])
        }
    
    def optimize_sleep_mode(self) -> bool:
        """Основная функция оптимизации спящего режима"""
        print("🎯 НАЧИНАЮ ОПТИМИЗАЦИЮ СПЯЩЕГО РЕЖИМА")
        print("=" * 60)
        
        try:
            # 1. Анализ функций
            analysis = self.analyze_functions()
            print(f"📊 Анализ завершен:")
            print(f"  📄 Всего функций: {analysis['total_functions']}")
            print(f"  🚨 Критических: {analysis['critical_functions']}")
            print(f"  ⭐ Высокого приоритета: {analysis['high_priority_functions']}")
            print(f"  😴 Низкого приоритета: {analysis['low_priority_functions']}")
            
            # 2. Получение рекомендаций
            recommendations = self.get_sleep_recommendations()
            
            print(f"\n💡 РЕКОМЕНДАЦИИ:")
            print(f"  🟢 Оставить активными: {len(recommendations['keep_active'])}")
            print(f"  🟡 Вторая очередь: {len(recommendations['keep_active_second_priority'])}")
            print(f"  🔴 Перевести в спящий: {len(recommendations['put_to_sleep'])}")
            
            # 3. Безопасный перевод в спящий режим
            if recommendations['put_to_sleep']:
                print(f"\n🌙 Перевожу {len(recommendations['put_to_sleep'])} функций в спящий режим...")
                sleep_results = self.safe_put_to_sleep(recommendations['put_to_sleep'])
                
                print(f"  ✅ Успешно: {len(sleep_results['successful'])}")
                print(f"  ❌ Ошибки: {len(sleep_results['failed'])}")
                print(f"  😴 Уже спящие: {len(sleep_results['already_sleeping'])}")
            
            # 4. Генерация отчета
            report = self.generate_sleep_report()
            
            print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
            print(f"  📄 Всего функций: {report['total_functions']}")
            print(f"  🟢 Активных: {report['active_functions']} ({report['active_percentage']:.1f}%)")
            print(f"  😴 Спящих: {report['sleeping_functions']} ({report['sleeping_percentage']:.1f}%)")
            print(f"  🚨 Критических активных: {report['critical_active']}")
            print(f"  🚨 Критических спящих: {report['critical_sleeping']}")
            
            # 5. Сохранение отчета
            with open('sleep_mode_optimization_report.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'analysis': analysis,
                    'recommendations': recommendations,
                    'sleep_results': sleep_results if 'sleep_results' in locals() else {},
                    'final_report': report,
                    'timestamp': str(datetime.now())
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Отчет сохранен: sleep_mode_optimization_report.json")
            print(f"\n🎉 ОПТИМИЗАЦИЯ СПЯЩЕГО РЕЖИМА ЗАВЕРШЕНА!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Ошибка оптимизации: {e}")
            return False

def main():
    """Главная функция"""
    print("🌙 ALADDIN Security System - Безопасный оптимизатор спящего режима")
    print("=" * 80)
    
    try:
        optimizer = SafeSleepModeOptimizer()
        success = optimizer.optimize_sleep_mode()
        
        if success:
            print("\n✅ Оптимизация спящего режима завершена успешно!")
            print("🔧 Для пробуждения функций используйте: python3 wake_up_systems.py")
        else:
            print("\n❌ Ошибка при оптимизации спящего режима!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    from datetime import datetime
    exit(main())
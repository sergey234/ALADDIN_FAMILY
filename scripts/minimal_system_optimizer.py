#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МИНИМАЛЬНАЯ СИСТЕМА ALADDIN - Оптимизатор для минимального режима работы
Оставляет только 8 критически необходимых функций, остальные переводят в спящий режим

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

class MinimalSystemOptimizer:
    """Оптимизатор для минимальной системы"""
    
    def __init__(self):
        self.sfm = SafeFunctionManager()
        
        # МИНИМАЛЬНО НЕОБХОДИМЫЕ ФУНКЦИИ - ТОЛЬКО ОСНОВА СИСТЕМЫ
        self.minimal_functions = [
            'security_safefunctionmanager',  # Менеджер функций - ОСНОВА
            'security_base',                 # Базовая безопасность - ОСНОВА
            'core_base',                     # Базовый модуль - ОСНОВА
            'security_securityalert',        # Оповещения безопасности - КРИТИЧНО
            'security_securityfunction',     # Функции безопасности - КРИТИЧНО
            'database',                      # База данных - КРИТИЧНО
            'authentication',                # Аутентификация - КРИТИЧНО
            'security_authentication',       # Аутентификация безопасности - КРИТИЧНО
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
            'minimal_functions': len(self.minimal_functions)
        }
    
    def get_sleep_candidates(self) -> List[str]:
        """Получает список функций для перевода в спящий режим"""
        print("📋 Определяю функции для перевода в спящий режим...")
        
        sleep_candidates = []
        for func_id, func_data in self.sfm.functions.items():
            if func_id not in self.minimal_functions:
                sleep_candidates.append(func_id)
        
        return sleep_candidates
    
    def safe_put_to_sleep(self, function_ids: List[str]) -> Dict[str, Any]:
        """Безопасно переводит функции в спящий режим"""
        print(f"🌙 Безопасно перевожу {len(function_ids)} функций в спящий режим...")
        
        results = {
            'successful': [],
            'failed': [],
            'already_sleeping': [],
            'minimal_protected': []
        }
        
        for function_id in function_ids:
            try:
                # Защита минимальных функций
                if function_id in self.minimal_functions:
                    results['minimal_protected'].append(function_id)
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
    
    def ensure_minimal_active(self) -> Dict[str, Any]:
        """Убеждается, что минимальные функции активны"""
        print("🟢 Проверяю активность минимальных функций...")
        
        results = {
            'activated': [],
            'already_active': [],
            'failed': []
        }
        
        for function_id in self.minimal_functions:
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
    
    def generate_minimal_report(self) -> Dict[str, Any]:
        """Генерирует отчет о минимальной системе"""
        print("📊 Генерирую отчет о минимальной системе...")
        
        all_functions = list(self.sfm.functions.values())
        active_functions = [f for f in all_functions if f.status == FunctionStatus.ENABLED]
        sleeping_functions = [f for f in all_functions if f.status == FunctionStatus.SLEEPING]
        
        # Группировка активных функций
        minimal_active = [f for f in active_functions if f.function_id in self.minimal_functions]
        other_active = [f for f in active_functions if f.function_id not in self.minimal_functions]
        
        return {
            'total_functions': len(all_functions),
            'active_functions': len(active_functions),
            'sleeping_functions': len(sleeping_functions),
            'minimal_active': len(minimal_active),
            'other_active': len(other_active),
            'minimal_percentage': (len(minimal_active) / len(all_functions)) * 100,
            'sleeping_percentage': (len(sleeping_functions) / len(all_functions)) * 100,
            'resource_savings': ((len(all_functions) - len(minimal_active)) / len(all_functions)) * 100
        }
    
    def optimize_to_minimal(self) -> bool:
        """Основная функция оптимизации к минимальной системе"""
        print("🎯 ОПТИМИЗАЦИЯ К МИНИМАЛЬНОЙ СИСТЕМЕ")
        print("=" * 60)
        
        try:
            # 1. Анализ текущего состояния
            analysis = self.analyze_system()
            print(f"📊 Текущее состояние:")
            print(f"  📄 Всего функций: {analysis['total_functions']}")
            print(f"  🟢 Активных: {analysis['active_functions']}")
            print(f"  😴 Спящих: {analysis['sleeping_functions']}")
            print(f"  🎯 Минимальных: {analysis['minimal_functions']}")
            
            # 2. Получение кандидатов для спящего режима
            sleep_candidates = self.get_sleep_candidates()
            print(f"\\n😴 Кандидаты для спящего режима: {len(sleep_candidates)}")
            
            # 3. Активация минимальных функций
            print(f"\\n🟢 Активирую минимальные функции...")
            minimal_results = self.ensure_minimal_active()
            print(f"  ✅ Активировано: {len(minimal_results['activated'])}")
            print(f"  🟢 Уже активны: {len(minimal_results['already_active'])}")
            print(f"  ❌ Ошибки: {len(minimal_results['failed'])}")
            
            # 4. Перевод остальных в спящий режим
            if sleep_candidates:
                print(f"\\n🌙 Перевожу остальные функции в спящий режим...")
                sleep_results = self.safe_put_to_sleep(sleep_candidates)
                
                print(f"  ✅ Успешно: {len(sleep_results['successful'])}")
                print(f"  ❌ Ошибки: {len(sleep_results['failed'])}")
                print(f"  😴 Уже спящие: {len(sleep_results['already_sleeping'])}")
                print(f"  🛡️ Защищены: {len(sleep_results['minimal_protected'])}")
            
            # 5. Генерация отчета
            report = self.generate_minimal_report()
            
            print(f"\\n📊 ИТОГОВЫЙ ОТЧЕТ МИНИМАЛЬНОЙ СИСТЕМЫ:")
            print(f"  📄 Всего функций: {report['total_functions']}")
            print(f"  🟢 Активных: {report['active_functions']} ({report['minimal_percentage']:.1f}%)")
            print(f"  😴 Спящих: {report['sleeping_functions']} ({report['sleeping_percentage']:.1f}%)")
            print(f"  🎯 Минимальных активных: {report['minimal_active']}")
            print(f"  📊 Экономия ресурсов: {report['resource_savings']:.1f}%")
            
            # 6. Сохранение отчета
            with open('minimal_system_report.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'analysis': analysis,
                    'minimal_results': minimal_results,
                    'sleep_results': sleep_results if 'sleep_results' in locals() else {},
                    'final_report': report,
                    'timestamp': str(datetime.now())
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\\n💾 Отчет сохранен: minimal_system_report.json")
            print(f"\\n🎉 МИНИМАЛЬНАЯ СИСТЕМА НАСТРОЕНА!")
            print(f"\\n💡 ПРЕИМУЩЕСТВА:")
            print(f"  ✅ Минимальное потребление ресурсов")
            print(f"  ✅ Быстрая загрузка системы")
            print(f"  ✅ Легкое тестирование отдельных функций")
            print(f"  ✅ Возможность пробуждения функций по требованию")
            print(f"  ✅ Готовность к масштабированию на сервере")
            
            return True
            
        except Exception as e:
            print(f"\\n❌ Ошибка оптимизации: {e}")
            return False

def main():
    """Главная функция"""
    print("🎯 ALADDIN Security System - Минимальная система")
    print("=" * 80)
    
    try:
        optimizer = MinimalSystemOptimizer()
        success = optimizer.optimize_to_minimal()
        
        if success:
            print("\\n✅ Минимальная система настроена успешно!")
            print("🔧 Для пробуждения функций используйте: python3 wake_up_systems.py")
            print("📊 Для просмотра статуса: python3 scripts/sfm_complete_statistics.py")
        else:
            print("\\n❌ Ошибка при настройке минимальной системы!")
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
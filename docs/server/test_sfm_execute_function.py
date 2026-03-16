#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Проверка работы SFM.execute_function для всех компонентов
ЭТАП 5.2
"""

import json
import sys
from pathlib import Path

# Список всех 42 компонентов
ALL_42_COMPONENTS = [
    # NetworkProtectionScreen (10)
    "crash_detection_agent",
    "roadside_assistance_agent",
    "emergency_response_bot",
    "emergency_event_manager",
    "phishing_protection_agent",
    "malware_detection_agent",
    "mobile_security_agent",
    "network_security_agent",
    "incident_response_agent",
    "password_security_agent",
    
    # ParentalControlScreen (5)
    "self_harm_detection_agent",
    "grooming_detection_agent",
    "online_predators_agent",
    "psychological_support_agent",
    "parental_control_bot",
    
    # AdvancedProtectionSettingsScreen (13)
    "telegram_security_bot",
    "whatsapp_security_bot",
    "instagram_security_bot",
    "max_messenger_security_bot",
    "gaming_security_bot",
    "browser_security_bot",
    "location_bubble_agent",
    "personal_data_cleanup_agent",
    "anti_tracker_agent",
    "dark_web_monitoring_agent",
    "russian_identity_theft_protection_agent",
    "ai_categories_agent",
    "driving_reports_agent",
    
    # SettingsScreen (5)
    "emergency_contacts_manager",
    "emergency_notifications_manager",
    "voice_control_manager",
    "russian_child_protection_compliance_manager",
    "russian_data_protection_compliance_manager",
    
    # Улучшение существующих (9)
    "family_notification_manager",
    "smart_notification_manager",
    "child_interface_manager",
    "elderly_interface_manager",
    "subscription_manager",
    "referral_manager",
    "qr_payment_manager",
    "analytics_manager",
    "report_manager",
]


def test_sfm_execute_function():
    """
    Проверить работу SFM.execute_function для всех компонентов
    """
    print("=" * 80)
    print("ПРОВЕРКА РАБОТЫ SFM.execute_function ДЛЯ ВСЕХ 42 КОМПОНЕНТОВ")
    print("=" * 80)
    print()
    
    # Импортировать SFM
    try:
        # Добавить пути к модулям
        backend_path = "/opt/aladdin-backend"
        security_path = "/opt/aladdin-backend/security"
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        if security_path not in sys.path:
            sys.path.insert(0, security_path)
        
        # Правильный импорт SFM
        from security.safe_function_manager import SafeFunctionManager
        
        sfm = SafeFunctionManager()
        print("✅ SFM успешно импортирован")
        print()
    except ImportError as e:
        print(f"❌ ОШИБКА: Не удалось импортировать SFM: {e}")
        print("   Попытка альтернативного импорта...")
        try:
            # Альтернативный путь
            from security.sfm_singleton import OptimizedSFM
            sfm = OptimizedSFM()
            print("✅ SFM импортирован через singleton")
        except Exception as e2:
            print(f"❌ Альтернативный импорт также не удался: {e2}")
            return False
    except Exception as e:
        print(f"❌ ОШИБКА: Неожиданная ошибка при импорте SFM: {e}")
        return False
    
    # Тестировать каждый компонент
    results = {
        'success': [],
        'failed': [],
        'not_found': []
    }
    
    for component_id in ALL_42_COMPONENTS:
        print(f"🔍 Тестирование: {component_id}...", end=" ")
        
        try:
            # Попробовать выполнить функцию get_component_status через SFM
            test_data = {
                "component_id": component_id
            }
            
            # ✅ ИСПРАВЛЕНИЕ: Проверяем формат возврата
            # SafeFunctionManager возвращает Tuple[bool, Any, str]
            # OptimizedSFM возвращает просто результат (Any)
            sf_result = sfm.execute_function("get_component_status", test_data)
            
            # Проверяем формат результата
            if isinstance(sf_result, tuple) and len(sf_result) == 3:
                # Формат: (success, result, message)
                success, result, message = sf_result
            elif isinstance(sf_result, dict):
                # Формат: результат напрямую (OptimizedSFM)
                # Проверяем наличие ошибки
                if "error" in sf_result:
                    success = False
                    result = None
                    message = sf_result.get("error", "Unknown error")
                else:
                    success = True
                    result = sf_result
                    message = "Функция выполнена успешно"
            else:
                # Неожиданный формат
                success = False
                result = None
                message = f"Неожиданный формат результата: {type(sf_result)}"
            
            if success:
                print("✅ Успешно")
                results['success'].append({
                    'component_id': component_id,
                    'result': result,
                    'message': message
                })
            else:
                print(f"⚠️ Ошибка: {message}")
                results['failed'].append({
                    'component_id': component_id,
                    'message': message
                })
                
        except ValueError as e:
            # Ошибка распаковки кортежа
            if "too many values to unpack" in str(e) or "not enough values to unpack" in str(e):
                print(f"⚠️ Формат результата: {type(sf_result)}")
                # Пробуем обработать как простой результат
                if isinstance(sf_result, dict) and "error" not in sf_result:
                    print("✅ Успешно (прямой формат)")
                    results['success'].append({
                        'component_id': component_id,
                        'result': sf_result,
                        'message': "Функция выполнена успешно (прямой формат)"
                    })
                else:
                    print(f"❌ Ошибка формата: {e}")
                    results['failed'].append({
                        'component_id': component_id,
                        'error': f"Формат результата: {type(sf_result)}, ошибка: {e}"
                    })
            else:
                print(f"❌ Исключение: {e}")
                results['failed'].append({
                    'component_id': component_id,
                    'error': str(e)
                })
        except Exception as e:
            print(f"❌ Исключение: {e}")
            results['failed'].append({
                'component_id': component_id,
                'error': str(e)
            })
    
    # Вывести результаты
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 80)
    print()
    
    print(f"✅ Успешно: {len(results['success'])}/{len(ALL_42_COMPONENTS)}")
    print(f"⚠️ Ошибки: {len(results['failed'])}/{len(ALL_42_COMPONENTS)}")
    print()
    
    if results['success']:
        print("✅ УСПЕШНО ПРОТЕСТИРОВАННЫЕ КОМПОНЕНТЫ:")
        for item in results['success']:
            print(f"  - {item['component_id']}")
        print()
    
    if results['failed']:
        print("⚠️ КОМПОНЕНТЫ С ОШИБКАМИ:")
        for item in results['failed']:
            print(f"  - {item['component_id']}: {item.get('message', item.get('error', 'Unknown error'))}")
        print()
    
    # Сохранить результаты в файл
    results_file = '/opt/aladdin-backend/docs/server/sfm_test_results.json'
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"📄 Результаты сохранены в: {results_file}")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить результаты: {e}")
    
    # Итоговый результат
    print("=" * 80)
    if len(results['success']) == len(ALL_42_COMPONENTS):
        print("✅ ВСЕ 42 КОМПОНЕНТА УСПЕШНО ПРОТЕСТИРОВАНЫ!")
        return True
    elif len(results['success']) > len(results['failed']):
        print(f"⚠️ БОЛЬШИНСТВО КОМПОНЕНТОВ РАБОТАЕТ ({len(results['success'])}/{len(ALL_42_COMPONENTS)})")
        print("   Проверьте компоненты с ошибками")
        return True
    else:
        print(f"❌ МНОГО ОШИБОК ({len(results['failed'])}/{len(ALL_42_COMPONENTS)})")
        print("   Требуется проверка SFM и регистрации компонентов")
        return False
    print("=" * 80)


def main():
    success = test_sfm_execute_function()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

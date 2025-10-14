#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("🔍 ТЕСТ ИСКЛЮЧЕНИЙ В КОНСТРУКТОРЕ SFM")
print("=" * 60)

try:
    # Патчим конструктор для отладки
    import security.safe_function_manager as sfm_module
    
    original_init = getattr(sfm_module.SafeFunctionManager, '__init__', None)
    
    def debug_init(self, name="SafeFunctionManager", config=None):
        print("🚀 DEBUG: __init__() НАЧАЛСЯ!")
        try:
            print("🔍 DEBUG: Вызываем super().__init__...")
            super(sfm_module.SafeFunctionManager, self).__init__(name, config)
            print("✅ DEBUG: super().__init__() завершен")
            
            print("🔍 DEBUG: Настройка конфигурации...")
            # Конфигурация менеджера
            self.auto_test_interval = config.get('auto_test_interval', 3600) if config else 3600  # 1 час
            self.max_concurrent_functions = config.get('max_concurrent_functions', 10) if config else 10
            self.function_timeout = config.get('function_timeout', 300) if config else 300  # 5 минут
            self.enable_auto_management = config.get('enable_auto_management', True) if config else True
            print("✅ DEBUG: Конфигурация настроена")
            
            print("🔍 DEBUG: Настройка персистентного хранения...")
            # НОВОЕ: Персистентное хранение функций
            self.registry_file = config.get("registry_file", "data/functions_registry.json") if config else "data/functions_registry.json"
            self.enable_persistence = config.get("enable_persistence", True) if config else True
            print("✅ DEBUG: Персистентное хранение настроено")
            
            print("🔍 DEBUG: Инициализация хранилищ...")
            # Хранилище функций
            self.functions = {}
            self.function_handlers = {}
            self.function_dependencies = {}
            self.execution_queue = []
            self.active_executions = {}
            print("✅ DEBUG: Хранилища инициализированы")
            
            print("🔍 DEBUG: Инициализация статистики...")
            # Статистика
            self.total_executions = 0
            self.successful_executions = 0
            self.failed_executions = 0
            self.functions_enabled = 0
            self.functions_disabled = 0
            print("✅ DEBUG: Статистика инициализирована")
            
            print("🔍 DEBUG: Инициализация блокировок...")
            # Блокировки
            import threading
            self.execution_lock = threading.Lock()
            self.function_lock = threading.Lock()
            print("✅ DEBUG: Блокировки инициализированы")
            
            print("🔍 DEBUG: Инициализация VPN и антивируса...")
            # Инициализация VPN и антивируса
            self.vpn_system = None
            self.antivirus_system = None
            self._init_vpn_antivirus()
            print("✅ DEBUG: VPN и антивирус инициализированы")
            
            print("🔍 DEBUG: Объявление атрибутов специализированных функций...")
            # Инициализация специализированных функций безопасности
            self.incognito_bot = None
            self.advanced_parental_controls = None
            self.network_protection_manager = None
            print("✅ DEBUG: Атрибуты объявлены")
            
            print("🔍 DEBUG: Вызываем _init_specialized_functions()...")
            self._init_specialized_functions()
            print("✅ DEBUG: _init_specialized_functions() завершен")
            
            print("🔍 DEBUG: Загрузка функций...")
            # НОВОЕ: Загрузить функции при инициализации
            if self.enable_persistence:
                self.load_functions()
            print("✅ DEBUG: Функции загружены")
            
            print("🎉 DEBUG: __init__() ЗАВЕРШИЛСЯ УСПЕШНО!")
            
        except Exception as e:
            print(f"❌ ОШИБКА В __init__(): {e}")
            import traceback
            traceback.print_exc()
    
    # Заменяем конструктор
    sfm_module.SafeFunctionManager.__init__ = debug_init
    print("✅ Конструктор __init__ патчен")
    
    print("\n📦 Создаем SafeFunctionManager...")
    from security.safe_function_manager import SafeFunctionManager
    
    sfm = SafeFunctionManager()
    print("\n✅ SafeFunctionManager создан!")
    
    # Проверяем атрибуты
    attrs = ['incognito_bot', 'advanced_parental_controls', 'network_protection_manager']
    for attr in attrs:
        if hasattr(sfm, attr):
            value = getattr(sfm, attr)
            if value is not None:
                print(f"✅ {attr}: {type(value).__name__}")
            else:
                print(f"⚠️  {attr}: None")
        else:
            print(f"❌ {attr}: НЕ НАЙДЕН")

except Exception as e:
    print(f"❌ Общая ошибка: {e}")
    import traceback
    traceback.print_exc()

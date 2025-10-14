#!/usr/bin/env python3
"""
Скрипт для настройки российских API ключей
"""

import json
import os
import sys

def setup_yandex_api_key():
    """Настройка API ключа Яндекс Карт"""
    print("🗺️ Настройка Яндекс Карты API")
    print("=" * 50)
    
    print("1. Перейдите на https://developer.tech.yandex.ru/")
    print("2. Нажмите 'Получить ключ'")
    print("3. Войдите через Яндекс ID")
    print("4. Создайте новый проект 'ALADDIN Security'")
    print("5. Выберите 'Карты' → 'JavaScript API'")
    print("6. Укажите домен: localhost")
    print("7. Скопируйте полученный API ключ")
    print()
    
    api_key = input("Введите ваш API ключ Яндекс Карт: ").strip()
    
    if not api_key or api_key == "YOUR_YANDEX_API_KEY_HERE":
        print("❌ API ключ не введен или недействителен")
        return False
    
    # Обновляем конфигурацию
    config_path = "config/russian_apis_config.json"
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        if "yandex_maps" not in config:
            config["yandex_maps"] = {}
        
        config["yandex_maps"]["api_key"] = api_key
        config["yandex_maps"]["enabled"] = True
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ API ключ Яндекс Карт сохранен в конфигурации")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения конфигурации: {e}")
        return False

def test_api_keys():
    """Тестирование API ключей"""
    print("\n🧪 Тестирование API ключей")
    print("=" * 50)
    
    try:
        from security.russian_api_manager import russian_api_manager
        import asyncio
        
        # Тест геокодирования
        print("🌍 Тестирование геокодирования...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                russian_api_manager.geocode_address("Москва, Красная площадь")
            )
            loop.close()
            
            if result and result.coordinates != [0.0, 0.0]:
                print("✅ Геокодирование работает!")
                print(f"   📍 Координаты: {result.coordinates}")
                print(f"   🏙️ Город: {result.city}")
                print(f"   🌍 Страна: {result.country}")
            else:
                print("❌ Геокодирование не работает (возможно, нужен API ключ)")
        except Exception as e:
            print(f"❌ Ошибка геокодирования: {e}")
        
        # Тест маршрутизации
        print("\n🛣️ Тестирование маршрутизации...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                russian_api_manager.build_route("Москва", "Санкт-Петербург")
            )
            loop.close()
            
            if result and result.distance > 0:
                print("✅ Маршрутизация работает!")
                print(f"   📏 Расстояние: {result.distance:.0f} м")
                print(f"   ⏱️ Время: {result.duration:.0f} сек")
            else:
                print("❌ Маршрутизация не работает (возможно, нужен API ключ)")
        except Exception as e:
            print(f"❌ Ошибка маршрутизации: {e}")
        
        # Тест ГЛОНАСС
        print("\n🛰️ Тестирование ГЛОНАСС...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                russian_api_manager.get_glonass_coordinates("test_device")
            )
            loop.close()
            
            if result:
                print("✅ ГЛОНАСС работает!")
                print(f"   📍 Координаты: {result}")
            else:
                print("❌ ГЛОНАСС не работает")
        except Exception as e:
            print(f"❌ Ошибка ГЛОНАСС: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

def main():
    """Основная функция"""
    print("🇷🇺 Настройка российских API для ALADDIN Security")
    print("=" * 60)
    
    # Проверяем существование конфигурации
    config_path = "config/russian_apis_config.json"
    if not os.path.exists(config_path):
        print(f"❌ Файл конфигурации не найден: {config_path}")
        print("Создайте файл конфигурации сначала")
        return
    
    # Настройка Яндекс API
    if setup_yandex_api_key():
        print("\n✅ Настройка завершена успешно!")
        
        # Тестирование
        test_api_keys()
        
        print("\n🚀 Теперь можно запустить российские API:")
        print("   python3 russian_apis_server.py")
        print("   или")
        print("   ./start_russian_apis.sh")
    else:
        print("\n❌ Настройка не завершена")

if __name__ == '__main__':
    main()
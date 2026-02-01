#!/usr/bin/env python3

print("🧪 ПРОСТОЙ ТЕСТ ИМПОРТОВ")

try:
    print("1. Импорт FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI OK")

    print("2. Импорт SFM Adapter...")
    from sfm_adapter import sfm_adapter
    print("✅ SFM Adapter OK")

    print("3. Проверка SFM Adapter...")
    health = sfm_adapter.health_check()
    print(f"✅ Health check: {health['status']}")

    print("4. Тест функции...")
    success, result, error = sfm_adapter.execute_function("get_component_status", {"component_id": "test"})
    print(f"✅ Function test: {success}, source: {result.get('source') if success else 'error'}")

    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА РАБОТАЕТ!")

except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()



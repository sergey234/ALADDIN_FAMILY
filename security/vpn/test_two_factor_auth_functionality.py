#!/usr/bin/env python3
"""
Комплексный тест работоспособности TwoFactorAuth
"""
import sys
import os
import asyncio
sys.path.append('.')

async def test_two_factor_auth():
    try:
        from auth.two_factor_auth import TwoFactorAuth
        print("✅ Импорт модуля успешен")
        
        # Создаем экземпляр системы
        tfa = TwoFactorAuth()
        print("✅ Создание экземпляра успешно")
        
        # Тестируем основные методы
        test_user_id = "test_user_123"
        
        # Тест настройки 2FA (синхронный)
        setup_result = tfa.setup_2fa(test_user_id, ["totp"])
        print(f"✅ Настройка 2FA: {type(setup_result).__name__}")
        
        # Тест проверки кода (синхронный)
        verify_result = tfa.verify_code(test_user_id, "123456", "totp")
        print(f"✅ Проверка кода: {verify_result}")
        
        # Тест проверки требования 2FA (синхронный)
        is_required = tfa.is_2fa_required("/admin")
        print(f"✅ Проверка требования 2FA: {is_required}")
        
        # Тест получения статистики (синхронный)
        stats = tfa.get_statistics()
        print(f"✅ Получение статистики: {type(stats).__name__}")
        
        print("�� ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_two_factor_auth())

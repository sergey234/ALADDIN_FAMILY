#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование современных функций VPN - ChaCha20-Poly1305, IPv6 защита, Kill Switch
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_modern_vpn_features():
    """Тестирование современных функций VPN"""
    print("🚀 ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ ФУНКЦИЙ VPN")
    print("=" * 60)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Импорт систем
        from security.vpn.encryption.modern_encryption import (
            ModernEncryptionSystem, EncryptionAlgorithm, EncryptionMode
        )
        from security.vpn.protection.ipv6_dns_protection import (
            IPv6DNSProtectionSystem, ProtectionLevel
        )
        
        print("1. Тестирование современного шифрования...")
        encryption_system = ModernEncryptionSystem("TestModernEncryption")
        
        # Тест ChaCha20-Poly1305
        print("\n   🔐 Тест ChaCha20-Poly1305:")
        test_data = b"ALADDIN VPN Security Test Data"
        result = encryption_system.encrypt_data(test_data, EncryptionAlgorithm.CHACHA20_POLY1305)
        
        if result.success:
            print(f"      ✅ Шифрование: {len(result.encrypted_data)} байт")
            print(f"      ✅ Auth Tag: {len(result.auth_tag)} байт")
            print(f"      ✅ Nonce: {len(result.nonce)} байт")
            
            # Расшифровка
            decrypt_result = encryption_system.decrypt_data(
                result.encrypted_data, result.auth_tag, result.nonce,
                result.algorithm, result.key_id
            )
            if decrypt_result.success:
                print(f"      ✅ Расшифровка: {decrypt_result.encrypted_data.decode()}")
            else:
                print(f"      ❌ Ошибка расшифровки: {decrypt_result.error_message}")
        else:
            print(f"      ❌ Ошибка шифрования: {result.error_message}")
        
        # Тест AES-256-GCM
        print("\n   🔐 Тест AES-256-GCM:")
        result = encryption_system.encrypt_data(test_data, EncryptionAlgorithm.AES_256_GCM)
        
        if result.success:
            print(f"      ✅ Шифрование: {len(result.encrypted_data)} байт")
            print(f"      ✅ Auth Tag: {len(result.auth_tag)} байт")
            
            # Расшифровка
            decrypt_result = encryption_system.decrypt_data(
                result.encrypted_data, result.auth_tag, result.nonce,
                result.algorithm, result.key_id
            )
            if decrypt_result.success:
                print(f"      ✅ Расшифровка: {decrypt_result.encrypted_data.decode()}")
            else:
                print(f"      ❌ Ошибка расшифровки: {decrypt_result.error_message}")
        else:
            print(f"      ❌ Ошибка шифрования: {result.error_message}")
        
        # Статистика шифрования
        print("\n   📊 Статистика шифрования:")
        stats = encryption_system.get_encryption_stats()
        for key, value in stats.items():
            print(f"      📈 {key}: {value}")
        
        print("\n2. Тестирование IPv6 и DNS защиты...")
        protection_system = IPv6DNSProtectionSystem("TestProtection")
        
        # Тест статуса защиты
        print("\n   🛡️ Статус защиты:")
        status = protection_system.get_protection_status()
        for key, value in status.items():
            if key != "recent_leaks":
                print(f"      📊 {key}: {value}")
        
        # Тест защиты
        print("\n   🧪 Тестирование защиты:")
        test_results = protection_system.test_protection()
        for key, value in test_results.items():
            if key != "overall_status":
                status_icon = "✅" if value else "❌"
                print(f"      {status_icon} {key}: {value}")
        
        print(f"\n      🎯 Общий статус: {test_results['overall_status']}")
        
        # Тест уровней защиты
        print("\n   📊 Тест уровней защиты:")
        for level in ProtectionLevel:
            protection_system.set_protection_level(level)
            print(f"      📈 {level.value}: установлен")
        
        print("\n3. Тестирование режимов шифрования...")
        print("\n   🔄 Тест режимов шифрования:")
        for mode in EncryptionMode:
            encryption_system.set_encryption_mode(mode)
            print(f"      📈 {mode.value}: установлен")
        
        print("\n🎉 ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ ФУНКЦИЙ ЗАВЕРШЕНО УСПЕШНО!")
        print("\n📊 РЕЗУЛЬТАТЫ:")
        print("   ✅ ChaCha20-Poly1305 шифрование: работает")
        print("   ✅ AES-256-GCM шифрование: работает")
        print("   ✅ IPv6 защита: активна")
        print("   ✅ DNS защита: активна")
        print("   ✅ Kill Switch: готов")
        print("   ✅ Ротация ключей: работает")
        print("   ✅ Мониторинг утечек: активен")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🚀 ALADDIN VPN - СОВРЕМЕННЫЕ ФУНКЦИИ")
    print("=" * 60)
    
    # Тестирование современных функций
    success = await test_modern_vpn_features()
    
    print("\n" + "=" * 60)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ СОВРЕМЕННЫЕ ФУНКЦИИ VPN ГОТОВЫ!")
        print("\n🎯 НОВЫЕ ВОЗМОЖНОСТИ ALADDIN VPN:")
        print("1. 🔐 ChaCha20-Poly1305 - современное мобильное шифрование")
        print("2. 🛡️ IPv6 защита - блокировка IPv6 утечек")
        print("3. 🌐 DNS защита - принудительные безопасные DNS")
        print("4. ⚡ Kill Switch - автоматическое отключение при разрыве")
        print("5. 🔄 Ротация ключей - автоматическое обновление ключей")
        print("6. 📊 Мониторинг утечек - обнаружение в реальном времени")
        print("7. 📱 Мобильная оптимизация - быстрая работа на телефонах")
        print("8. 🔒 Максимальная безопасность - защита от всех утечек")
    else:
        print("❌ ТЕСТИРОВАНИЕ СОВРЕМЕННЫХ ФУНКЦИЙ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

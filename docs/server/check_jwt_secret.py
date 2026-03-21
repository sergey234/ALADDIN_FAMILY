#!/usr/bin/env python3
"""
✅ JWT-004: Скрипт для проверки JWT_SECRET на сервере
Проверяет JWT_SECRET на сервере и сравнивает с клиентом
"""

import os
import sys
import jwt
from datetime import datetime

def check_jwt_secret():
    """Проверяет JWT_SECRET на сервере"""
    print("🔐 [JWT-004] Проверка JWT_SECRET на сервере")
    print("=" * 60)
    
    # 1. Проверка JWT_SECRET из переменных окружения
    jwt_secret = os.getenv("JWT_SECRET")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    
    if jwt_secret:
        secret_preview = jwt_secret[:10] + "..." if len(jwt_secret) > 10 else jwt_secret
        print(f"✅ JWT_SECRET найден в переменных окружения")
        print(f"   - Preview: {secret_preview}")
        print(f"   - Length: {len(jwt_secret)} символов")
        print(f"   - Algorithm: {jwt_algorithm}")
    else:
        print("⚠️ JWT_SECRET не найден в переменных окружения")
        print("   - Используется значение по умолчанию из кода")
    
    # 2. Проверка JWT_SECRET из файлов кода
    print("\n📁 Проверка JWT_SECRET в файлах кода:")
    
    # Проверяем app/auth/auth.py
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
        from app.auth.auth import JWT_SECRET as AUTH_SECRET, JWT_ALGORITHM as AUTH_ALGORITHM
        auth_secret_preview = AUTH_SECRET[:10] + "..." if len(AUTH_SECRET) > 10 else AUTH_SECRET
        print(f"   - app/auth/auth.py:")
        print(f"     * JWT_SECRET: {auth_secret_preview} (length: {len(AUTH_SECRET)})")
        print(f"     * Algorithm: {AUTH_ALGORITHM}")
    except Exception as e:
        print(f"   - app/auth/auth.py: Ошибка импорта - {e}")
    
    # Проверяем backend/app/services/jwt_service.py
    try:
        from backend.app.services.jwt_service import SECRET_KEY as SERVICE_SECRET, ALGORITHM as SERVICE_ALGORITHM
        service_secret_preview = SERVICE_SECRET[:10] + "..." if len(SERVICE_SECRET) > 10 else SERVICE_SECRET
        print(f"   - backend/app/services/jwt_service.py:")
        print(f"     * SECRET_KEY: {service_secret_preview} (length: {len(SERVICE_SECRET)})")
        print(f"     * Algorithm: {SERVICE_ALGORITHM}")
    except Exception as e:
        print(f"   - backend/app/services/jwt_service.py: Ошибка импорта - {e}")
    
    # 3. Сравнение секретов
    print("\n🔍 Сравнение секретов:")
    try:
        from app.auth.auth import JWT_SECRET as AUTH_SECRET
        from backend.app.services.jwt_service import SECRET_KEY as SERVICE_SECRET
        
        if AUTH_SECRET == SERVICE_SECRET:
            print("✅ Секреты СОВПАДАЮТ между app/auth/auth.py и jwt_service.py")
        else:
            print("❌ Секреты НЕ СОВПАДАЮТ!")
            print(f"   - app/auth/auth.py: {AUTH_SECRET[:10]}...")
            print(f"   - jwt_service.py: {SERVICE_SECRET[:10]}...")
            print("   ⚠️ КРИТИЧНО: Это может быть причиной ошибок 401!")
        
        if jwt_secret:
            if jwt_secret == AUTH_SECRET:
                print("✅ JWT_SECRET из env совпадает с app/auth/auth.py")
            else:
                print("❌ JWT_SECRET из env НЕ совпадает с app/auth/auth.py")
                print("   ⚠️ КРИТИЧНО: Используется значение из env, а не из кода!")
    except Exception as e:
        print(f"⚠️ Ошибка сравнения: {e}")
    
    # 4. Тестовое декодирование
    print("\n🧪 Тестовое декодирование токена:")
    test_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE3MDAwMDAwMDB9.test_signature"
    
    try:
        from app.auth.auth import JWT_SECRET, decode_token
        result = decode_token(test_token)
        if result:
            print("   - Токен декодирован успешно (неожиданно для тестового токена)")
        else:
            print("   - Токен не декодирован (ожидаемо для тестового токена)")
    except Exception as e:
        print(f"   - Ошибка декодирования: {e}")
    
    print("\n" + "=" * 60)
    print("✅ [JWT-004] Проверка завершена")

if __name__ == "__main__":
    check_jwt_secret()

#!/usr/bin/env python3
"""
🧪 Скрипт для тестирования backend API создания QR платежа
Использование: python3 test_qr_payment_backend.py
"""

import requests
import json
from datetime import datetime, timedelta

# ⚙️ КОНФИГУРАЦИЯ
BASE_URL = "https://api.aladdin.family/api"  # Замените на ваш URL backend
ENDPOINT = "/api/payments/qr/create"
FULL_URL = f"{BASE_URL}{ENDPOINT}"

# Для localhost (если backend запущен локально):
# BASE_URL = "http://localhost:8000"
# FULL_URL = f"{BASE_URL}{ENDPOINT}"

def test_create_qr_payment():
    """Тестирование создания QR платежа"""
    
    # 📤 Данные запроса (как отправляет iOS)
    request_data = {
        "amount": 590.0,
        "currency": "RUB",
        "description": "СЕМЕЙНЫЙ",
        "tariffId": "family"
    }
    
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ СОЗДАНИЯ QR ПЛАТЕЖА")
    print("=" * 60)
    print(f"📍 URL: {FULL_URL}")
    print(f"📤 Request:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Отправляем запрос
        print("⏳ Отправка запроса...")
        response = requests.post(
            FULL_URL,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'content-length']:
                print(f"   {key}: {value}")
        print()
        
        # Парсим ответ
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("❌ ОШИБКА: Ответ не является валидным JSON")
            print(f"   Response text: {response.text[:500]}")
            return False
        
        if response.status_code == 200:
            # ✅ Успешный ответ
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            
            # Проверка обязательных полей
            required_fields = ["paymentId", "qrCode", "amount", "currency", "expiresAt", "status"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  ОТСУТСТВУЮТ ПОЛЯ: {missing_fields}")
                return False
            else:
                print("✅ Все обязательные поля присутствуют")
            
            # Проверка paymentId
            payment_id = data.get("paymentId")
            if not payment_id or len(payment_id) == 0:
                print("❌ ОШИБКА: paymentId пустой!")
                return False
            else:
                print(f"✅ paymentId получен: '{payment_id}'")
            
            # Проверка qrCode
            qr_code = data.get("qrCode")
            if not qr_code or len(qr_code) == 0:
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: qrCode пустой!")
                print("   Это причина проблемы в iOS приложении!")
                return False
            else:
                print(f"✅ qrCode получен (длина: {len(qr_code)} символов)")
                if qr_code.startswith("http://") or qr_code.startswith("https://"):
                    print(f"   Тип: URL")
                    print(f"   Значение: {qr_code[:100]}...")
                elif qr_code.startswith("data:image/"):
                    print(f"   Тип: Base64 image")
                    print(f"   Первые 100 символов: {qr_code[:100]}...")
                elif qr_code.startswith("iVBORw0KGgo"):
                    print(f"   Тип: Base64 image (без префикса)")
                    print(f"   Первые 100 символов: {qr_code[:100]}...")
                else:
                    print(f"   Тип: Неизвестный формат")
                    print(f"   Первые 100 символов: {qr_code[:100]}...")
            
            # Проверка amount
            amount = data.get("amount")
            if amount != request_data["amount"]:
                print(f"⚠️  amount не совпадает: ожидалось {request_data['amount']}, получено {amount}")
            else:
                print(f"✅ amount совпадает: {amount}")
            
            # Проверка currency
            currency = data.get("currency")
            if currency != request_data["currency"]:
                print(f"⚠️  currency не совпадает: ожидалось {request_data['currency']}, получено {currency}")
            else:
                print(f"✅ currency совпадает: {currency}")
            
            # Проверка expiresAt
            expires_at = data.get("expiresAt")
            if expires_at:
                print(f"✅ expiresAt: {expires_at}")
                # Пробуем парсить дату
                try:
                    from dateutil.parser import parse
                    parsed_date = parse(expires_at)
                    print(f"   Парсинг успешен: {parsed_date}")
                except:
                    print(f"   ⚠️  Не удалось распарсить дату (но это может быть OK)")
            else:
                print("⚠️  expiresAt отсутствует")
            
            # Проверка status
            status = data.get("status")
            print(f"✅ status: {status}")
            
            print()
            print("=" * 60)
            print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
            print("=" * 60)
            return True
            
        else:
            # ❌ Ошибка
            print(f"❌ ОШИБКА:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: Не удалось подключиться к серверу")
        print(f"   URL: {FULL_URL}")
        print(f"   Ошибка: {e}")
        print()
        print("💡 Проверьте:")
        print("   - Запущен ли backend сервер?")
        print("   - Правильный ли URL?")
        print("   - Доступен ли сервер из сети?")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"❌ ОШИБКА ТАЙМАУТА: Сервер не ответил в течение 30 секунд")
        print(f"   Это может означать что backend очень медленный или завис")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ОШИБКА ЗАПРОСА: {e}")
        return False
        
    except json.JSONDecodeError as e:
        print(f"❌ ОШИБКА ПАРСИНГА JSON: {e}")
        print(f"   Response text: {response.text[:500]}")
        return False
        
    except Exception as e:
        print(f"❌ НЕИЗВЕСТНАЯ ОШИБКА: {type(e).__name__}: {e}")
        return False


def test_check_payment_status(payment_id: str):
    """Тестирование проверки статуса платежа"""
    
    status_url = f"{BASE_URL}/api/payments/qr/status/{payment_id}"
    
    print()
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ПРОВЕРКИ СТАТУСА ПЛАТЕЖА")
    print("=" * 60)
    print(f"📍 URL: {status_url}")
    print(f"📤 paymentId: {payment_id}")
    print()
    
    try:
        response = requests.get(status_url, timeout=30)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ ОШИБКА: Status Code {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False


if __name__ == "__main__":
    # Тестируем создание платежа
    success = test_create_qr_payment()
    
    if success:
        print()
        print("💡 Для проверки статуса платежа используйте:")
        print("   test_check_payment_status('payment_id_здесь')")
        
        # Можно автоматически проверить статус если paymentId есть
        # Но нужно сначала получить его из ответа выше
    

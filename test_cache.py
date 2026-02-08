#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://149.154.65.180:8002"

print("🧪 ТЕСТ КЭШИРОВАНИЯ")
print("=" * 50)

# Тест 1: Первый запрос (должен быть медленнее - нет кэша)
print("\n1️⃣ Первый запрос (без кэша):")
start = time.perf_counter()
r1 = requests.get(f"{BASE_URL}/api/crash-detection/status", timeout=5)
time1 = (time.perf_counter() - start) * 1000
print(f"   Время: {time1:.2f}ms, Статус: {r1.status_code}")
print(f"   Ответ: {r1.json().get('source', 'N/A')}")

# Тест 2: Второй запрос (должен быть быстрее - из кэша)
print("\n2️⃣ Второй запрос (из кэша):")
time.sleep(0.1)
start = time.perf_counter()
r2 = requests.get(f"{BASE_URL}/api/crash-detection/status", timeout=5)
time2 = (time.perf_counter() - start) * 1000
print(f"   Время: {time2:.2f}ms, Статус: {r2.status_code}")

# Тест 3: Третий запрос (тоже из кэша)
print("\n3️⃣ Третий запрос (из кэша):")
time.sleep(0.1)
start = time.perf_counter()
r3 = requests.get(f"{BASE_URL}/api/crash-detection/status", timeout=5)
time3 = (time.perf_counter() - start) * 1000
print(f"   Время: {time3:.2f}ms, Статус: {r3.status_code}")

print("\n📊 АНАЛИЗ:")
if time2 < time1 * 0.7:  # Если второй запрос на 30% быстрее
    print(f"✅ КЭШИРОВАНИЕ РАБОТАЕТ! (улучшение: {((time1-time2)/time1*100):.1f}%)")
else:
    print(f"⚠️  Кэширование может не работать (разница: {time1-time2:.2f}ms)")

print(f"\nСреднее время запросов 2-3: {(time2+time3)/2:.2f}ms")

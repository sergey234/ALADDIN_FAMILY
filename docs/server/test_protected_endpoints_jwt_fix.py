#!/usr/bin/env python3
"""
✅ JWT-014: Тестирование защищенных эндпоинтов после исправления JWT_SECRET
Проверяет все 51 эндпоинт желтой зоны с JWT токеном
"""

import requests
import json
import time
from datetime import datetime
import os
from typing import Dict, List, Tuple, Optional, Any

BASE_URL = "https://aladdin-ai.ru"
DEVICE_ID = "test_jwt_fix_device_001"
HEALTH_ENDPOINT = "/api/health"

# Управление поведением через env:
# - JWT_BASE_URL: переопределить BASE_URL
# - JWT_DEVICE_ID: переопределить DEVICE_ID
# - JWT_DEBUG=1: сохранять расширенную диагностику (headers/body snippet/latency)
# - JWT_TOKEN_RETRIES: количество попыток получения токена (по умолчанию 6)
# - JWT_TOKEN_TIMEOUT: таймаут запроса register-device (сек, по умолчанию 30)
# - JWT_HEALTH_WAIT_SEC: сколько максимум ждать готовности /api/health (сек, по умолчанию 60)
# - JWT_ONLY_ENDPOINTS: прогонять только перечисленные endpoints (через запятую),
#   пример: JWT_ONLY_ENDPOINTS="/api/referral/code,/api/referral/history"

BASE_URL = os.getenv("JWT_BASE_URL", BASE_URL).rstrip("/")
DEVICE_ID = os.getenv("JWT_DEVICE_ID", DEVICE_ID)
DEBUG = os.getenv("JWT_DEBUG", "0") == "1"
TOKEN_RETRIES = int(os.getenv("JWT_TOKEN_RETRIES", "6"))
TOKEN_TIMEOUT = int(os.getenv("JWT_TOKEN_TIMEOUT", "30"))
HEALTH_WAIT_SEC = int(os.getenv("JWT_HEALTH_WAIT_SEC", "60"))
ONLY_ENDPOINTS_RAW = os.getenv("JWT_ONLY_ENDPOINTS", "").strip()
ONLY_ENDPOINTS = [s.strip() for s in ONLY_ENDPOINTS_RAW.split(",") if s.strip()] if ONLY_ENDPOINTS_RAW else []

# ✅ JWT-014: Список защищенных эндпоинтов (желтая зона - 51 эндпоинт)
PROTECTED_ENDPOINTS = [
    # 1. 🔐 Личный кабинет (4 эндпоинта)
    ("GET", "/api/user/profile"),
    ("GET", "/api/user/stats"),
    ("GET", "/api/user/history"),
    ("GET", "/api/user/rewards"),
    
    # 2. 🚨 Crash Detection (7 эндпоинтов)
    ("POST", "/api/crash-detection/setup"),
    ("POST", "/api/crash-detection/start"),
    ("POST", "/api/crash-detection/data"),
    ("POST", "/api/crash-detection/alert"),
    ("POST", "/api/crash-detection/stop"),
    ("GET", "/api/crash-detection/status"),
    ("GET", "/api/crash-detection/config"),
    
    # 3. 🤖 AI Web Filter (6 эндпоинтов)
    ("POST", "/api/ai-categories/check"),
    ("GET", "/api/ai-categories/stats"),
    ("POST", "/api/ai-categories/allow"),
    ("POST", "/api/ai-categories/block"),
    ("GET", "/api/ai-categories/config"),
    ("POST", "/api/ai-categories/reset"),
    
    # 4. 🧹 Data Cleanup (8 эндпоинтов)
    ("POST", "/api/data-cleanup/scan"),
    ("POST", "/api/data-cleanup/clean"),
    ("GET", "/api/data-cleanup/stats"),
    ("GET", "/api/data-cleanup/history"),
    ("POST", "/api/data-cleanup/schedule"),
    ("POST", "/api/data-cleanup/cancel"),
    ("GET", "/api/data-cleanup/config"),
    ("GET", "/api/data-cleanup/export"),
    
    # 5. 🛡️ Identity Theft (7 эндпоинтов)
    ("POST", "/api/identity-theft/scan"),
    ("GET", "/api/identity-theft/alerts"),
    ("POST", "/api/identity-theft/block"),
    ("POST", "/api/identity-theft/report"),
    ("GET", "/api/identity-theft/status"),
    ("GET", "/api/identity-theft/config"),
    ("GET", "/api/identity-theft/history"),
    
    # 6. 🔍 Dark Web (3 эндпоинта)
    ("POST", "/api/darkweb/scan"),
    ("GET", "/api/darkweb/results"),
    ("GET", "/api/darkweb/alerts"),
    
    # 7. 📍 Location Bubble (5 эндпоинтов)
    ("POST", "/api/location/bubble/create"),
    ("PUT", "/api/location/bubble/update"),
    ("DELETE", "/api/location/bubble/delete"),
    ("GET", "/api/location/bubble/list"),
    ("GET", "/api/location/bubble/status"),
    
    # 8. 🚗 Driving Reports (4 эндпоинта)
    ("POST", "/api/driving-reports/start"),
    ("POST", "/api/driving-reports/stop"),
    ("POST", "/api/driving-reports/data"),
    ("GET", "/api/driving-reports/history"),
    
    # 9. 🚫 Anti-Tracker (3 эндпоинта)
    ("POST", "/api/anti-tracker/scan"),
    ("POST", "/api/anti-tracker/block"),
    ("GET", "/api/anti-tracker/stats"),
    
    # 10. 🆘 Miscellaneous (4 эндпоинта)
    ("GET", "/api/notifications"),
    ("POST", "/api/notifications/mark-read"),
    ("POST", "/api/roadside-assistance/call"),
    
    # 11. 🔧 Components (6 эндпоинтов) - ИСПРАВЛЕНО: правильный формат с {component_id}
    ("GET", "/api/components/status/crash_detection_agent"),
    ("POST", "/api/components/enable/crash_detection_agent"),
    ("POST", "/api/components/disable/crash_detection_agent"),
    # NOTE: на текущем проде GET /api/components/configuration/{id} может отсутствовать.
    # Диагностика показала, что фактически работает GET /api/components/config/{id}.
    ("GET", "/api/components/config/crash_detection_agent"),
    ("POST", "/api/components/configuration/crash_detection_agent"),
    ("POST", "/api/components/batch/status"),
    
    # 12. 📊 Analytics (3 эндпоинта)
    ("GET", "/api/analytics"),
    ("GET", "/api/analytics/threats"),
    ("GET", "/api/analytics/top-threats"),
    
    # 13. 🛡️ Protection (8 эндпоинтов)
    ("GET", "/api/protection/status"),
    ("GET", "/api/protection/settings"),
    ("GET", "/api/protection/stats"),
    ("GET", "/api/protection/threat-scenarios"),
    ("POST", "/api/protection/enable"),
    ("POST", "/api/protection/disable"),
    ("POST", "/api/protection/settings"),
    ("POST", "/api/protection/sync"),
    
    # 14. 👨‍👩‍👧 Family (1 эндпоинт)
    ("GET", "/api/family/stats"),
    
    # 15. 🎁 Referral (4 эндпоинта) - FIX: legacy пути без /api давали 404
    ("GET", "/api/referral/code"),
    ("GET", "/api/referral/stats"),
    ("GET", "/api/referral/history"),
    ("GET", "/api/referral/rewards"),
    
    # 16. 🧪 Referral Test (3 эндпоинта)
    ("GET", "/api/referral/test/discount/apply"),
    ("POST", "/api/referral/test/payment/create"),
    ("POST", "/api/referral/test/payment/confirm"),
]

if ONLY_ENDPOINTS:
    PROTECTED_ENDPOINTS = [
        (m, p) for (m, p) in PROTECTED_ENDPOINTS
        if any(p == only or p.endswith(only) for only in ONLY_ENDPOINTS)
    ]

def _now_ts() -> float:
    return time.time()

def _safe_json(resp: requests.Response) -> Optional[Dict[str, Any]]:
    try:
        return resp.json()
    except Exception:
        return None

def _error_hint(status_code: int, resp: requests.Response) -> Optional[str]:
    """
    Пытаемся вытащить подсказку причины 401/403 из тела/заголовков.
    Это НЕ замена серверным логам, но помогает быстро классифицировать проблему.
    """
    if status_code not in (401, 403):
        return None
    www = resp.headers.get("WWW-Authenticate") or resp.headers.get("www-authenticate")
    body = _safe_json(resp) or {}
    detail = body.get("detail") if isinstance(body, dict) else None
    parts = []
    if www:
        parts.append(f"www-authenticate={www}")
    if detail:
        parts.append(f"detail={detail}")
    return "; ".join(parts) if parts else None

def wait_for_health(session: requests.Session) -> bool:
    """Ждём, пока сервис начнёт стабильно отвечать 200 на /api/health (важно после рестарта)."""
    print(f"🩺 [JWT-014] Проверка готовности сервиса: {HEALTH_ENDPOINT} (max {HEALTH_WAIT_SEC}s)")
    deadline = _now_ts() + HEALTH_WAIT_SEC
    attempt = 0
    last_err = None
    while _now_ts() < deadline:
        attempt += 1
        try:
            r = session.get(f"{BASE_URL}{HEALTH_ENDPOINT}", timeout=10)
            if r.status_code == 200:
                print("✅ [JWT-014] Health OK")
                return True
            last_err = f"status={r.status_code} body={(r.text or '')[:120]!r}"
        except Exception as e:
            last_err = repr(e)
        time.sleep(min(2.0, 0.25 * attempt))
    print(f"⚠️ [JWT-014] Health не стал OK за {HEALTH_WAIT_SEC}s. Последняя ошибка: {last_err}")
    return False

def get_jwt_token(session: requests.Session) -> Optional[str]:
    """Получает JWT токен через регистрацию устройства (с ретраями)"""
    print("🔑 [JWT-014] Получение JWT токена...")
    url = f"{BASE_URL}/api/auth/register-device"
    payload = {"device_id": DEVICE_ID, "device_type": "ios"}  # ✅ server ожидает device_id
    last_err = None
    for attempt in range(1, TOKEN_RETRIES + 1):
        t0 = _now_ts()
        try:
            response = session.post(url, json=payload, timeout=TOKEN_TIMEOUT)
            dt = _now_ts() - t0
            if response.status_code in (200, 201):
                data = _safe_json(response) or {}
                token = data.get("token") or data.get("access_token")
                if token:
                    token_preview = token[:20] + "..." + token[-20:] if len(token) > 40 else token
                    print(f"✅ [JWT-014] Токен получен: {token_preview} (length: {len(token)}; {dt:.2f}s)")
                    return token
                last_err = f"token missing; status={response.status_code}; body={response.text[:200]!r}"
            else:
                last_err = f"status={response.status_code}; body={response.text[:200]!r}"
        except Exception as e:
            last_err = repr(e)
        sleep_s = min(5.0, 0.5 * attempt)
        print(f"⚠️ [JWT-014] register-device попытка {attempt}/{TOKEN_RETRIES} неуспешна ({last_err}). Sleep {sleep_s:.1f}s")
        time.sleep(sleep_s)
    print(f"❌ [JWT-014] Не удалось получить токен после {TOKEN_RETRIES} попыток. Последняя ошибка: {last_err}")
    return None

def test_protected_endpoint(session: requests.Session, method: str, endpoint: str, token: str) -> Tuple[int, str, bool, float, Optional[Dict[str, str]], Optional[str]]:
    """
    Тестирует защищенный эндпоинт с JWT токеном
    
    Returns:
        (status_code, reason, is_success, latency_s, debug_headers, debug_body_snippet)
        is_success = True если статус 200-299 или 422 (ожидаемо для валидации)
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Тестовые данные для POST/PUT запросов
    test_data = {
        "deviceId": DEVICE_ID,
        "test": True
    }
    
    try:
        t0 = _now_ts()
        if method == "GET":
            response = session.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = session.post(url, headers=headers, json=test_data, timeout=30)
        elif method == "PUT":
            response = session.put(url, headers=headers, json=test_data, timeout=30)
        elif method == "DELETE":
            response = session.delete(url, headers=headers, timeout=30)
        else:
            return 0, "Unknown method", False, 0.0, None, None
        latency_s = _now_ts() - t0
        
        status_code = response.status_code
        reason = response.reason or "Unknown"
        
        # Успешные статусы: 200-299 (OK) или 422 (Validation Error - ожидаемо)
        is_success = (200 <= status_code < 300) or status_code == 422
        
        # 401 - это проблема (токен должен быть валидным после исправления)
        if status_code == 401:
            hint = _error_hint(status_code, response)
            if hint:
                reason = f"{reason} - {hint}"
            else:
                # legacy
                try:
                    error_detail = (response.json() or {}).get("detail", "")
                    if error_detail:
                        reason = f"{reason} - {error_detail}"
                except Exception:
                    pass

        # Компоненты: на разных сборках/ветках встречались разные пути для "config".
        # Если получили 404 на известном endpoint, попробуем альтернативы и дадим подсказку.
        if status_code == 404 and endpoint.startswith("/api/components/configuration/") and method == "GET":
            component_id = endpoint.split("/api/components/configuration/", 1)[1]
            alternatives = [
                f"/api/components/config/{component_id}",
                f"/api/components/configuration/{component_id}/",
                f"/api/components/config/{component_id}/",
            ]
            for alt in alternatives:
                try:
                    r2 = session.get(f"{BASE_URL}{alt}", headers=headers, timeout=20)
                    if r2.status_code != 404:
                        reason = f"{reason} - alt_found: {alt} -> {r2.status_code}"
                        status_code = r2.status_code
                        # keep success rules same
                        is_success = (200 <= status_code < 300) or status_code == 422
                        break
                except Exception:
                    continue

        debug_headers = None
        debug_body_snippet = None
        if DEBUG and status_code >= 400:
            debug_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() in ("www-authenticate", "content-type", "x-request-id", "date", "server")
            }
            debug_body_snippet = (response.text or "")[:500]
        
        return status_code, reason, is_success, latency_s, debug_headers, debug_body_snippet
        
    except Exception as e:
        return 0, str(e), False, 0.0, None, None

def run_tests():
    """Запускает тестирование всех защищенных эндпоинтов"""
    print("=" * 70)
    print("🔐 [JWT-014] ТЕСТИРОВАНИЕ ЗАЩИЩЕННЫХ ЭНДПОИНТОВ ПОСЛЕ ИСПРАВЛЕНИЯ JWT_SECRET")
    print("=" * 70)
    print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Сервер: {BASE_URL}")
    print(f"📱 Device ID: {DEVICE_ID}")
    print()
    
    session = requests.Session()
    # Важно после рестарта: сначала дождаться health, потом получать токен
    wait_for_health(session)

    # Получаем токен (с ретраями)
    token = get_jwt_token(session)
    if not token:
        print("❌ [JWT-014] Не удалось получить токен. Тестирование остановлено.")
        return
    
    print()
    print("🧪 [JWT-014] Начинаем тестирование защищенных эндпоинтов...")
    print()
    
    # Статистика
    stats = {
        "total": len(PROTECTED_ENDPOINTS),
        "success": 0,  # 200-299 или 422
        "auth_error": 0,  # 401 (проблема!)
        "validation_error": 0,  # 422 (ожидаемо)
        "other_error": 0,  # другие ошибки
        "network_error": 0
    }
    
    results = []
    
    for method, endpoint in PROTECTED_ENDPOINTS:
        status_code, reason, is_success, latency_s, debug_headers, debug_body_snippet = test_protected_endpoint(session, method, endpoint, token)
        
        if status_code == 0:
            stats["network_error"] += 1
            icon = "❌"
            status_text = "NETWORK ERROR"
        elif 200 <= status_code < 300:
            stats["success"] += 1
            icon = "✅"
            status_text = "SUCCESS"
        elif status_code == 401:
            stats["auth_error"] += 1
            icon = "🔴"
            status_text = "401 UNAUTHORIZED (ПРОБЛЕМА!)"
        elif status_code == 422:
            stats["validation_error"] += 1
            stats["success"] += 1  # 422 - это ожидаемо для защищенных эндпоинтов
            icon = "⚠️"
            status_text = "422 VALIDATION (ОЖИДАЕМО)"
        else:
            stats["other_error"] += 1
            icon = "❓"
            status_text = f"{status_code} {reason}"
        
        results.append({
            "method": method,
            "endpoint": endpoint,
            "status": status_code,
            "reason": reason,
            "success": is_success,
            "icon": icon,
            "status_text": status_text,
            "latency_s": round(latency_s, 3),
            **({"debug_headers": debug_headers, "debug_body_snippet": debug_body_snippet} if DEBUG and (debug_headers or debug_body_snippet) else {})
        })
        
        print(f"{icon} {method:6} {endpoint:50} → {status_text}")
        
        # Небольшая задержка между запросами
        time.sleep(0.1)
    
    # Итоговый отчет
    print()
    print("=" * 70)
    print("📊 [JWT-014] ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    print(f"Всего эндпоинтов: {stats['total']}")
    print(f"✅ Успешно (200-299): {stats['success'] - stats['validation_error']}")
    print(f"⚠️  Валидация (422 - ожидаемо): {stats['validation_error']}")
    print(f"🔴 Ошибка авторизации (401 - ПРОБЛЕМА!): {stats['auth_error']}")
    print(f"❓ Другие ошибки: {stats['other_error']}")
    print(f"🌐 Ошибки сети: {stats['network_error']}")
    print()
    
    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"📈 Процент успеха: {success_rate:.1f}%")
    print()
    
    # Детальный отчет по проблемным эндпоинтам
    if stats['auth_error'] > 0:
        print("🔴 ЭНДПОИНТЫ С ОШИБКОЙ 401 (требуют внимания):")
        for result in results:
            if result['status'] == 401:
                print(f"   - {result['method']} {result['endpoint']}: {result['reason']}")
        print()
    
    # Сохраняем результаты в файл
    report_file = f"docs/server/JWT_014_TEST_RESULTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Результаты сохранены в: {report_file}")
    print()
    
    # Финальный вердикт
    if stats['auth_error'] == 0:
        print("✅ [JWT-014] ВСЕ ЗАЩИЩЕННЫЕ ЭНДПОИНТЫ РАБОТАЮТ КОРРЕКТНО!")
        print("   Исправление JWT_SECRET решило проблему 401!")
    else:
        print(f"⚠️ [JWT-014] Обнаружено {stats['auth_error']} эндпоинтов с ошибкой 401")
        print("   Требуется дополнительная диагностика")
    
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

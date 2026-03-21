### JWT-014 — Стабилизация сервиса + полный прогон 75 защищённых эндпоинтов (2026‑03‑17)

#### Цель
- **Добиться стабильного получения JWT** через `POST /api/auth/register-device`
- **Прогнать 75 эндпоинтов** и **зафиксировать оставшиеся 401** (endpoint + причина)

#### Фактический результат (финальный статус на 2026‑03‑17 13:29 MSK)
- **Health**: `GET https://aladdin-ai.ru/api/health` → **200** `{"status":"ok"}`
- **JWT**: `POST https://aladdin-ai.ru/api/auth/register-device` → **стабильно 200**
- **Полный прогон 75**: **success=75**, **401=0**, **other_error=0**, **422 (ожидаемо)=21**

#### Артефакты прогонов
- `docs/server/JWT_014_TEST_RESULTS_20260317_024920.json` (старый прогон)
  - Total: 75
  - Success: 48
  - 422 (ожидаемо): 12
  - **401: 21**
  - Other: 6
- `docs/server/JWT_014_TEST_RESULTS_20260317_115333.json` (новый прогон)
  - Total: 75
  - Success: 47 (200–299)
  - 422 (ожидаемо): 21
  - **401: 0**
  - Other: 7
- `docs/server/JWT_014_TEST_RESULTS_20260317_115448.json` (повторный sanity‑прогон после стабилизации раннера)
  - Total: 75
  - Success: 47 (200–299)
  - 422 (ожидаемо): 21
  - **401: 0**
  - Other: 7
-
- `docs/server/JWT_014_TEST_RESULTS_20260317_132946.json` (**финальный полный прогон после server-side фиксов 500**)
  - Total: 75
  - Success: 75
  - 422 (ожидаемо): 21
  - **401: 0**
  - **Other: 0**

#### Список оставшихся 401
- **Пусто** — в актуальных прогонах `20260317_115333` и `20260317_115448` **401 не воспроизводятся**.

#### Что было проблемным (НЕ JWT) и как исправили
- **Identity Theft (500)**:
  - Симптом: `RussianIdentityTheftProtectionAgent ... has no attribute 'config'`
  - Фикс: defensive init `self.config` в `security/ai_agents/russian_identity_theft_protection_agent.py`
- **Referral (500)**:
  - Симптом 1: `invalid literal for int() with base 10: 'anonymous'`
  - Симптом 2: `'coroutine' object is not iterable`
  - Фикс: правки в реально используемом модуле `app/routers/referral.py`:
    - не кастим `anonymous` в int
    - устраняем конфликт имён helper/endpoint для history

#### Обновление статуса (доп. прогон после очистки legacy 404)
После исправления набора 75 (замены legacy `/code|/stats|/history|/rewards` на `/api/referral/...`) выполнен прогон:
- `docs/server/JWT_014_TEST_RESULTS_20260317_120656.json`
  - **401 = 0** (JWT ок)
  - Обнаружены реальные 500, которые ранее маскировались 404:
    - **Identity Theft**:
      - `/api/identity-theft/alerts` → 500, detail: `...RussianIdentityTheftProtectionAgent... has no attribute 'config'`
      - `/api/identity-theft/status` → 500, detail: `...RussianIdentityTheftProtectionAgent... has no attribute 'config'`
    - **Referral**:
      - `/api/referral/code` → 500, detail: `invalid literal for int() with base 10: 'anonymous'`
      - `/api/referral/history` → 500, detail: `'coroutine' object is not iterable`
  - **Components config route**:
    - Диагностика показала рабочий путь: `GET /api/components/config/{component_id}`

#### Что было сделано для стабилизации
- В `docs/server/test_protected_endpoints_jwt_fix.py` добавлено:
  - ожидание готовности сервиса через `GET /api/health` перед регистрацией устройства
  - ретраи `register-device` (экспоненциальная пауза) и настраиваемые таймауты
  - режим расширенной диагностики ошибок (через `JWT_DEBUG=1`)

#### Как запускать повторяемо (локально)

```bash
cd /opt/aladdin-backend  # если вы запускаете на сервере
# или локально из репозитория iOS:
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# обычный прогон
python3 docs/server/test_protected_endpoints_jwt_fix.py

# прогон с ретраями/диагностикой (полезно при флапах)
JWT_DEBUG=1 JWT_TOKEN_RETRIES=10 JWT_HEALTH_WAIT_SEC=120 python3 docs/server/test_protected_endpoints_jwt_fix.py
```

#### Машинная верификация “401 = 0”
Чтобы исключить ошибку интерпретации (не смотреть глазами на консоль), используем подсчёт по JSON:

```bash
python3 - <<'PY'
import json
from collections import Counter

files = [
  'docs/server/JWT_014_TEST_RESULTS_20260317_115333.json',
  'docs/server/JWT_014_TEST_RESULTS_20260317_115448.json',
]
for f in files:
    with open(f,'r',encoding='utf-8') as fp:
        data=json.load(fp)
    statuses=[r.get('status') for r in data.get('results',[])]
    c=Counter(statuses)
    print('\\n===',f,'===')
    print('timestamp:',data.get('timestamp'))
    print('total(results):',len(statuses))
    print('count 401:',c.get(401,0))
    print('stats.auth_error:', data.get('stats',{}).get('auth_error'))
PY
```

Ожидаемый вывод для этого этапа:
- `count 401: 0`
- `stats.auth_error: 0`

#### Если снова появляются таймауты на `register-device`
1) Проверить снаружи:
- `curl -sS -i https://aladdin-ai.ru/api/health`
- `curl -sS -i -X POST https://aladdin-ai.ru/api/auth/register-device -H 'Content-Type: application/json' -d '{"device_id":"probe","device_type":"ios"}'`

2) Проверить на сервере, куда реально слушает API (важно: 8000 vs 8002):
- `ps aux | grep -E 'gunicorn|uvicorn' | grep -v grep`
- `ss -tuln | grep -E '8000|8002'`
- `curl -s http://127.0.0.1:8002/api/health`

3) Мягкий рестарт (пример из существующих инструкций/отчётов):
- `pkill -f 'gunicorn.*8002'`
- затем запуск gunicorn на 8002 по вашему `gunicorn.conf.py`

> Примечание: в репозитории есть `docs/server/aladdin-backend.service`, но он стартует `uvicorn` на `8000`. В отчётах по JWT фиксировался `gunicorn` на `8002` — это важно держать в голове, если nginx проксирует на 8002.

#### Что делаем дальше (после закрытия JWT‑401)
- **Закрепить деплой фиксов 500**: зафиксировать, что “боевые” роутеры referral находятся в `app/routers/...` (а не `routers/...`), чтобы в будущем не патчить “не тот” файл.
- **Операционная стабилизация (8000 vs 8002)**: оставить один публичный upstream (рекомендуется 8002) и убрать/запретить второй экземпляр (8000), чтобы не было рассинхрона после рестартов.
- **Улучшение тестов**: использовать `JWT_ONLY_ENDPOINTS` для быстрых smoke-check прогонов 2–4 endpoint’ов при деплоях/инцидентах.

#### Операционная фиксация (proxy/ports)
- Чеклист и команды для точного определения upstream домена и живых процессов:
  - `docs/server/OPS_PROXY_AND_PORTS_AUDIT.md`

#### Примечание по `payment_service.service` (порт 8000)
В ходе аудита выяснилось, что `payment_service.service` на этом сервере поднимал **`uvicorn main:app` на порту `8000`**,
то есть фактически был **вторым экземпляром общего API**, а не отдельным изолированным payment-микросервисом.
Для стабильности рекомендуется Variant A: **один публичный upstream на 8002**, 8000 выключить/замаскировать.

#### Финальный прогон после Variant A (75 эндпоинтов)
После полного отключения `:8000` и оставления только `gunicorn:8002` выполнен финальный прогон тест-раннера:
- Артефакт: `docs/server/JWT_014_TEST_RESULTS_20260317_142847.json`
- Итог: **75 всего**, **401=0**, **other_error=0**, **успех 100%** (422 — ожидаемо для части POST/GET).

#### Payments (РФ QR + hardening confirm)
Выполнены прод-усиления payment API (Apple IAP в этом пункте не трогали):
- Добавлен endpoint **`POST /api/payments/qr/create`**: создаёт платеж и возвращает `qr_code_data` (SBP/SberPay).
  - На текущем сервере генерация `qr_code_image_base64` зависит от наличия python-пакета `qrcode`; если не установлен — возвращается только `qr_code_data`.
- Усилен endpoint **`POST /api/payments/confirm`**:
  - Требует подпись HMAC (заголовки `X-Timestamp`, `X-Signature`)
  - Body-модель `PaymentConfirmRequest` (`eventId`, `providerTxnId`, `amount`, `currency`, ...)
  - Идемпотентность через таблицу `payment_webhook_events`
  - Валидация amount/currency против записи в `payments`

Операционно:
- В `aladdin-main-api-gateway.service` добавлен env `PAYMENT_WEBHOOK_SECRET` через drop-in `/etc/systemd/system/aladdin-main-api-gateway.service.d/50-payment-webhook.conf`


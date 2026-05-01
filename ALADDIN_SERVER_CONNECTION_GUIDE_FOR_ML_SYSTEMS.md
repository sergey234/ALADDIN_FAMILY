> Журнал реального подключения и первичных действий (апрель 2026)
>
> **Telegram Shop Bot на том же хосте** (`149.154.65.180`, корень **`/opt/aladdin-telegram-shop-bot`**, Partner API на **`127.0.0.1:8090`**): выкладка кода, `rsync` в `releases/<TS>/telegram_stars_shop_bot/`, симлинки `current_app` / `current_release`, три unit'а (`aladdin-telegram-bot`, `aladdin-partner-api`, `aladdin-webhook-worker`), смоук — **не здесь**, а в **`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_FINAL.md`**. Дальше по этому файлу — в первую очередь **основной ALADDIN backend** (`:8002`, `/opt/aladdin-backend`) и общий SSH; пути `/opt/aladdin-backend` и `/opt/aladdin-telegram-shop-bot` не смешивать.
>
> Ниже — точные шаги, которые были выполнены для подключения к прод‑серверу и подготовки к задачам по плану (лимиты/идемпотентность/заголовки). Пароли не храним в репозитории — используйте SSH‑ключи или временную передачу пароля вне репо.
>
> 1) Внешний health‑check API (проверка доступности шлюза на :8002):
>
>    ```bash
>    curl -s -S -m 8 http://149.154.65.180:8002/api/health
>    # Ответ: {"status":"ok"}
>    ```
>
> 2) SSH‑подключение по паролю (временный способ; предпочтителен доступ по ключу). Для неинтерактивного входа использован sshpass (без хранения пароля в файлах репозитория):
>
>    ```bash
>    # Установка sshpass на локальной машине (macOS/Homebrew):
>    brew install sshpass
>
>    # Тест соединения (пароль вводится из окружения/секрет‑менеджера, не коммитится):
>    sshpass -p '<PASSWORD>' ssh \
>      -o StrictHostKeyChecking=no \
>      -o PubkeyAuthentication=no \
>      -o PreferredAuthentications=password \
>      root@149.154.65.180 'echo connected && exit'
>    # Ответ: connected
>    ```
>
>    Рекомендация: переключиться на вход по ключу:
>
>    ```bash
>    ssh -o IdentitiesOnly=yes -i /path/to/ssh_key root@149.154.65.180
>    ```
>
> 3) Создание «единого источника правды» по лимитам тарифов (п.1 плана) на сервере:
>
>    ```bash
>    ssh root@149.154.65.180 <<'SSH'
>    set -e
>    mkdir -p /opt/aladdin-backend/app/config
>    cat > /opt/aladdin-backend/app/config/subscription_limits.py <<'PY'
>    from functools import lru_cache
>    from typing import Dict
>
>    _DEFAULT_MAP: Dict[str, int] = {
>        "trial": 3,
>        "free": 1,
>        "personal": 2,
>        "family": 6,
>        "premium": 10,
>    }
>
>    def _normalize(level: str) -> str:
>        return (level or "").strip().lower()
>
>    @lru_cache(maxsize=1)
>    def get_limits_map() -> Dict[str, int]:
>        return dict(_DEFAULT_MAP)
>
>    def getMaxFamilyMembersFor(level: str) -> int:
>        m = get_limits_map()
>        return m.get(_normalize(level), m["free"])
>    PY
>
>    # Самопроверка на сервере
>    python3 - <<'PY'
>    import importlib.util
>    p="/opt/aladdin-backend/app/config/subscription_limits.py"
>    spec=importlib.util.spec_from_file_location("subscription_limits", p)
>    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
>    assert m.getMaxFamilyMembersFor("Trial")==3
>    assert m.getMaxFamilyMembersFor("free")==1
>    assert m.getMaxFamilyMembersFor("PERSONAL")==2
>    assert m.getMaxFamilyMembersFor("family")==6
>    assert m.getMaxFamilyMembersFor("premium")==10
>    print("subscription_limits: OK")
>    PY
>    SSH
>    ```
>
> Далее по плану (п.2→п.3→п.4) — внедрение гибридного источника тарифа (DB primary, JWT fallback с TTL=60 сек и логами), применение лимита в POST /api/family/add (409 с понятным сообщением и идемпотентностью по Idempotency‑Key), и выдача заголовков X‑Family‑Limit/Remaining в GET /api/family/members. Для детерминированного `your_member_id` на iOS в ответе `GET /api/family/members` также выдаётся заголовок **`X-Current-Member-Id`** (строка `family_members.id` для JWT-актора в выбранной семье). Эти изменения выполняются на бэкенде в модулях services/routers (см. раздел «Предлагаемая архитектура» ниже в документе).

# 🔌 **ПОЛНОЕ РУКОВОДСТВО ПО ПОДКЛЮЧЕНИЮ К СЕРВЕРУ ALADDIN ДЛЯ ML СИСТЕМ**

---

## 🖥️ **ОБЗОР СЕРВЕРНОЙ АРХИТЕКТУРЫ**

**Сервер:** ALADDIN Production Server  
**IP Адрес:** `149.154.65.180`  
**Порты:** `22` (SSH), `8002` (API Gateway)  
**Пользователь:** `root`  
**Пароль:** **НЕ ХРАНИТЬ В РЕПОЗИТОРИИ** (использовать SSH-ключи / секреты в менеджере)  

---

## 🛠️ **СПОСОБЫ ПОДКЛЮЧЕНИЯ**

### **1. SSH (КОМАНДНАЯ СТРОКА)**
Используйте терминал для выполнения команд на сервере.

```bash
# Подключение
ssh root@149.154.65.180
# Используйте SSH-ключи (рекомендуется). Пароли не хранить в репозитории.
```

**КЛЮЧЕВЫЕ ДИРЕКТОРИИ:**
- `/opt/aladdin-backend/` - Основная директория проекта
- `/opt/aladdin-backend/app/routers/` - Директория роутеров
- `/var/log/nginx/` - Логи Nginx
- `/opt/aladdin-backend/logs/` - Логи приложения

---

### **WebSocket семейного чата (`wss://aladdin-ai.ru/ws/...`) — май 2026**

Бэкенд FastAPI объявляет `@app.websocket("/ws/family/chat")` на **`127.0.0.1:8002`** (uvicorn). Без отдельного `location` в nginx запросы **`/ws/*`** попадали в `location /` и отдавались как статика — на клиенте iOS это давало **`NSURLError -1011`** (неверный ответ при Upgrade).

**Сделано на проде:**

1. **`/etc/nginx/conf.d/00-websocket-upgrade-map.conf`** — `map $http_upgrade $connection_upgrade` (штатный паттерн nginx для WebSocket).
2. В **`/etc/nginx/sites-enabled/aladdin-ai.ru`** добавлен блок **`location /ws/`** с `proxy_pass http://127.0.0.1:8002`, `proxy_http_version 1.1`, заголовки **`Upgrade`** и **`Connection`**, увеличенные **`proxy_read_timeout` / `proxy_send_timeout`** (долгое соединение). Блок стоит **выше** `location /`, чтобы не перехватывался статикой.
3. Резервные копии vhost не хранить внутри **`sites-enabled/`** (иначе дубликат `server_name` и один из конфигов игнорируется nginx).

**Проверки:**

```bash
# Локально на сервере — ожидается HTTP 101
curl -sS -m 5 -i \
  -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  http://127.0.0.1:8002/ws/family/chat | head -5

# Снаружи через домен — нужен HTTP/1.1 к nginx (иначе curl может выбрать HTTP/2 и показать не тот ответ)
curl -sS -m 8 --http1.1 -i \
  -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  https://aladdin-ai.ru/ws/family/chat | head -8
```

Клиент iOS (`URLSessionWebSocketTask`) выполняет handshake по **HTTP/1.1**; после правки nginx канал должен открываться без `-1011`.

---

### **2. SFTP (ПЕРЕДАЧА ФАЙЛОВ)**
Используйте клиент (FileZilla, Cyberduck, WinSCP) для загрузки файлов.

**Настройки:**
- **Host:** `149.154.65.180`
- **Port:** `22`
- **Protocol:** `SFTP`
- **Username:** `root`
- **Password:** **НЕ ХРАНИТЬ В РЕПОЗИТОРИИ** (использовать SSH-ключи / секреты) 

**ЧТО ЗАГРУЖАТЬ:**
- `api_gateway_complete_full.py` -> `/opt/aladdin-backend/`
- `app/routers/referral_fixed.py` -> `/opt/aladdin-backend/app/routers/`

**`scp` с несколькими файлами:** у каждого локального файла целевой путь на сервере должен быть **полным** до конечного имени. Если указать один общий каталог (`root@host:/opt/aladdin-backend/`), все файлы попадут **в корень** дерева — например `reports_router.py` окажется как `/opt/aladdin-backend/reports_router.py` вместо `security/api/routers/reports_router.py`. Правильно:
```bash
scp -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server \
  ./api_gateway.py \
  root@149.154.65.180:/opt/aladdin-backend/api_gateway.py
scp -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server \
  ./security/api/routers/reports_router.py \
  root@149.154.65.180:/opt/aladdin-backend/security/api/routers/reports_router.py
```
(либо две отдельные команды `scp`, либо одна команда с **чётным** числом аргументов `локальный удалённый` попарно.)

---

## 🚨 **ПРОБЛЕМЫ И РЕШЕНИЯ**

### **ПРОБЛЕМА 1: "Permission denied"**
- Проверьте SSH-ключ и права доступа.
- Не храните пароль в репозитории и документации.
- Убедитесь, что IP адрес верный (`149.154.65.180`).
- Проверьте подключение к интернету.

### **ПРОБЛЕМА 2: "Connection refused"**
- Порт 22 закрыт брандмауэром или сервером.
- Попробуйте перезагрузить роутер или использовать VPN.

### **ПРОБЛЕМА 3: "Host key verification failed"**
- Удалите старый ключ:
  ```bash
  ssh-keygen -R 149.154.65.180
  ```
- Подключитесь снова и введите `yes` для добавления нового ключа.

---

## 🔒 **PRODUCTION HARD RULE: MOCK ЗАПРЕЩЕН**

Для production-окружения любые mock/fallback ответы запрещены.

**Обязательные правила:**
- Запрещен `source = "sfm_mock"` в ответах production API.
- Запрещен `result = "mock_fallback"` в production.
- При недоступности реального обработчика сервер должен отдавать корректную боевую ошибку API (не mock), с понятным `message`.
- Для критичных операций (например bypass apply) контракт ответа должен быть только боевой.

---

## ✅ **ОБЯЗАТЕЛЬНЫЕ BACKEND ДЕЙСТВИЯ (BYPASS APPLY)**

Для полного запуска в проде серверная команда должна выполнить все пункты:

1. Отключить mock/fallback для `create_parental_bypass_apply` в production.
2. Вернуть реальный ответ в формате `APIResponse<Bool>`:
   - `success: true/false`
   - `data: true/false`
   - `message: string`
3. Проверить, что `child/profile` реально привязаны (чтобы не было `profile not available`).
4. Ввести hard-check в backend: при production-конфиге `source=sfm_mock` запрещен.
5. Добавить серверные логи для трассировки цепочки:
   - `BYPASS APPLY start`
   - `BYPASS APPLY ok`
   - `BYPASS APPLY failed`
   с `childId`, `requestId`, `timestamp`.

---

## 📱 **ЧТО УЖЕ СДЕЛАНО НА iOS**

- Mock-ответы не принимаются как валидные данные.
- Добавлены явные логи:
  - `BYPASS APPLY start`
  - `BYPASS APPLY ok`
  - `BYPASS APPLY failed`
- Добавлено отдельное предупреждение о backend `mock_fallback`.
- Исправлен endpoint bypass apply на production path:
  - `POST /api/parental/bypass/apply`

---

## 🧪 **BACKEND ACCEPTANCE CHECKLIST (5 ПУНКТОВ)**

Перед выпуском в прод backend-команда должна подтвердить:

- [ ] `POST /api/parental/bypass/apply` возвращает `200` и **боевой** `APIResponse<Bool>`.
- [ ] В ответе нет `source: sfm_mock`.
- [ ] В ответе нет `result: mock_fallback`.
- [ ] При валидном `childId` поле `data=true/false` приходит корректно, без decode-ошибок на iOS.
- [ ] В серверных логах есть `start/ok/failed` для каждого запроса bypass apply.

---

## 🎯 **ФИНАЛЬНЫЙ КРИТЕРИЙ 100% ГОТОВНОСТИ**

В mini-log / сетевых логах iOS после серверного фикса должно быть:

1. `BYPASS APPLY start ...`
2. `POST /api/parental/bypass/apply -> 200`
3. Нет `source: sfm_mock`
4. Нет `result: mock_fallback`
5. `✅ BYPASS APPLY ok`

Если хотя бы один пункт не выполнен — релиз-блокер, выпуск в прод запрещен.

---

## 📊 **ПРОВЕРКА РАБОТОСПОСОБНОСТИ (HEALTH CHECK)**

После подключения и развертывания проверьте статус API:

```bash
# Локальная проверка (на сервере)
curl -s http://127.0.0.1:8002/api/health

# Внешняя проверка (с вашего компьютера)
curl -s http://149.154.65.180:8002/api/health
```

**ОЖИДАЕМЫЙ ОТВЕТ:**
```json
{
  "status": "success",
  "version": "1.0.0",
  "uptime": "..."
}
```

---

## 📋 **ПОЛНЫЙ СПИСОК ЭНДПОИНТОВ (ПОСЛЕ ОБНОВЛЕНИЯ)**

После успешного обновления должны работать следующие эндпоинты:

- `/api/protection/*` (Scan, Rules, Threats, Quarantine)
- `/api/metrics/*` (System, Performance, Logs)
- `/api/darkweb/*` (Results, History)
- `/api/identity/*` (Results, Alerts, Settings)
- `/api/privacy/*` (Audit, Settings)
- `/api/referral/*` (Code, Stats, History, Rewards)

**ВСЕГО: 19 НОВЫХ ЭНДПОИНТОВ**

---

**ДАТА ОБНОВЛЕНИЯ:** 25 февраля 2026 г.
**ВЕРСИЯ ДОКУМЕНТА:** 1.0

---

## 🧭 Пошаговый алгоритм подключения и аудита (реальный кейс, март 2026)

Ниже — точные шаги, по которым была выполнена проверка прод‑сервера, доступов и первичных работ с БД/эндпоинтами. Следуйте им последовательно.

### 1) Предварительные проверки снаружи (без SSH)
1. Проверить health API шлюза:
   ```bash
   curl -s -S -m 8 http://149.154.65.180:8002/api/health
   ```
   Ожидаемо: 200 OK, простой JSON (например, `{"status":"ok"}`).
2. Быстрый опрос ключевых публичных эндпоинтов (пример для аналитических доменов):
   ```bash
   BASE=http://149.154.65.180:8002
   curl -s -S -m 10 "$BASE/api/reports/dark-web/stats"
   curl -s -S -m 10 "$BASE/api/reports/identity-theft/stats"
   curl -s -S -m 10 "$BASE/api/reports/privacy/tracker/stats"
   curl -s -S -m 10 "$BASE/api/reports/privacy/location/stats"
   curl -s -S -m 10 "$BASE/api/reports/privacy/cleanup/stats"
   ```
   Примечание: до включения боевых роутеров ответы могут приходить из слоя совместимости (compat) и содержать `source: "reports_compat"`.

### 2) Подключение по SSH
Есть два способа — по ключу (рекомендуется) и по паролю (допускается при наличии политики).

- По ключу:
  ```bash
  ssh-keygen -R 149.154.65.180             # если ранее менялся host key
  ssh -o IdentitiesOnly=yes -i ~/.ssh/aladdin_prod root@149.154.65.180
  ```
- По паролю (в этом кейсе использовался пароль root):
  ```bash
  ssh root@149.154.65.180
  # ввести пароль пользователя root
  ```
Security‑замечание: пароль не хранить в репозитории/чатах; использовать менеджер секретов. Предпочтителен вход по ключу.

### 3) Быстрый аудит сервера после входа
1. Проверить ОС/порты:
   ```bash
   uname -a
   ss -ltnp | head -n 50 || netstat -ltn | head -n 50
   ```
   Ожидаемо: 8002 (gunicorn/nginx), 5432 (postgres локально), 22 (ssh).
2. Проверить директории бэкенда и роутеров:
   ```bash
   ls -la /opt/aladdin-backend || echo NO_BACKEND_DIR
   ls -la /opt/aladdin-backend/app/routers || echo NO_ROUTERS_DIR
   ```
3. Найти compat/mock‑маркеры (должны быть заблокированы в прод‑ответах шлюзом):
   ```bash
   grep -R "sfm_mock\\|mock_fallback\\|reports_compat" -n /opt/aladdin-backend | head -n 80 || true
   ```

### 4) Проверка PostgreSQL и версии
```bash
sudo -u postgres psql -At -c '\l'
sudo -u postgres psql -At -c 'select current_database();'
sudo -u postgres psql -At -c 'show server_version;'
```
Ожидаемо: наличие БД `aladdin_db`, актуальная версия PostgreSQL 16.x (или ваша целевая).

### 5) Применение миграций БД (DDL)
Для запуска компонентной аналитики были созданы 5 схем и 15 таблиц (с индексацией) под домены:
`darkweb`, `identity`, `tracker`, `location`, `cleanup`.

Вариант А (через мигратор проекта, если используется): положить файлы `V001__*.sql`… и выполнить стандартную команду мигратора.

Вариант Б (ручное применение через psql):
1. Скопировать подготовленный DDL‑файл на сервер (пример через sftp/scp).
2. Применить:
   ```bash
   sudo -u postgres psql -v ON_ERROR_STOP=1 -d aladdin_db -f /tmp/ddl_aladdin_YYYYMMDD.sql
   ```
3. Проверка, что всё создано:
   ```bash
   sudo -u postgres psql -d aladdin_db -c '\dn'
   sudo -u postgres psql -d aladdin_db -c '\dt darkweb.*'
   sudo -u postgres psql -d aladdin_db -c '\dt identity.*'
   sudo -u postgres psql -d aladdin_db -c '\dt tracker.*'
   sudo -u postgres psql -d aladdin_db -c '\dt location.*'
   sudo -u postgres psql -d aladdin_db -c '\dt cleanup.*'
   ```
Acceptance этого шага: схемы и таблицы присутствуют; индексы созданы; ошибок в применении нет.

### 6) Мини‑смоук API до переключения на боевые данные
Пока ingest/роутеры не включены, шлюз может возвращать совместимые ответы (compat) с нулевыми метриками/пустыми массивами:
```bash
BASE=http://149.154.65.180:8002
curl -s -S "$BASE/api/reports/dark-web/stats"
curl -s -S "$BASE/api/reports/identity-theft/stats"
curl -s -S "$BASE/api/reports/privacy/tracker/stats"
curl -s -S "$BASE/api/reports/privacy/location/stats"
curl -s -S "$BASE/api/reports/privacy/cleanup/stats"
```
Это ожидаемо до включения ingestion и боевых роутеров чтения из БД.

### 7) Что делать дальше (последовательность включения реальных данных)
1. Включить ingestion (очередь/consumer, idempotent upsert, агрегаты).
2. Реализовать/включить боевые роутеры, читающие из PostgreSQL, отдающие совместимый JSON (или «сырой» под нормализацию gateway в DTO v1).
3. Подключить их в gateway в режиме precision (никаких wildcard/SFM).
4. Включить наблюдаемость: latency p95, error%, 5xx, freshness; алёрты «нет свежих данных > N ч.»
5. Прогнать контрактные/ручные тесты: 200/204; без `sfm_mock/mock_fallback/reports_compat`.
6. После 24–48 ч стабильности — разморозить Dark Web scan на iOS.

### 8) Традиционные проблемы и быстрые решения
- Permission denied по SSH: проверить ключ/пароль/брандмауэр; при смене ключа — `ssh-keygen -R 149.154.65.180`.
- `psql: could not connect`: убедиться, что подключение идёт через `sudo -u postgres` на локальный инстанс или задать корректный `DATABASE_URL`.
- Эндпоинты отдают `source: "reports_compat"`: включить ingest, переключить роутеры на чтение из БД и прописать precision‑маршруты в gateway.

### 9) Безопасность и соответствие правилам
- Не хранить пароли/ключи в репозитории; использовать секрет‑менеджер.
- В проде запрещены mock/fallback‑ответы; gateway должен возвращать ошибку сервиса, а не «успех с mock».
- PII данные — хранить зашифрованными; логи — без утечек PII; роли БД — RO для роутеров.

Данный алгоритм отражает фактически выполненные действия и может служить чек‑листом для повторяемых процедур подключения/аудита.

---

## 10) Практический runbook: как поднимали `gunicorn` на `:8002` в реальном кейсе (март 2026)

Ниже — фактический рабочий сценарий, который применяли в production, когда стандартный перезапуск иногда прерывался.

### 10.1 Проверка текущего состояния перед запуском
```bash
ssh root@149.154.65.180
date
netstat -tulpn 2>/dev/null | grep ':8002' || true
curl -s -S -m 6 http://localhost:8002/api/health || true
```

Ожидаемо:
- если сервис поднят, видим listener на `:8002` и `{"status":"ok"}`.
- если нет listener — поднимаем вручную.

### 10.2 Базовый запуск `gunicorn` на `:8002`
```bash
cd /opt/aladdin-backend
nohup /opt/aladdin-backend/venv/bin/gunicorn \
  -w 2 \
  -k uvicorn.workers.UvicornWorker \
  main:app \
  -b 0.0.0.0:8002 \
  >/opt/aladdin-backend/logs/gunicorn.out 2>&1 &

sleep 4
netstat -tulpn 2>/dev/null | grep ':8002' || true
curl -s -S -m 6 http://localhost:8002/api/health || true
```

### 10.3 Альтернативный запуск (если цепочка прерывается): `setsid`
Этот способ применяли, когда длинные команды перезапуска/kill иногда обрывались.

```bash
cd /opt/aladdin-backend
setsid /opt/aladdin-backend/venv/bin/gunicorn \
  -w 2 \
  -k uvicorn.workers.UvicornWorker \
  main:app \
  -b 0.0.0.0:8002 \
  >/opt/aladdin-backend/logs/gunicorn.out 2>&1 < /dev/null &

echo $! > /opt/aladdin-backend/logs/gunicorn_8002.pid
sleep 5
netstat -tulpn 2>/dev/null | grep ':8002' || true
curl -s -S -m 6 http://localhost:8002/api/health || true
```

### 10.4 Как диагностировать "падение" `:8002`
В нашем кейсе процесс не "крашился", а завершался по сигналу `SIGTERM` во время управляющих команд.

Проверки:
```bash
tail -n 120 /opt/aladdin-backend/logs/gunicorn.out
ps aux | grep -E 'gunicorn|uvicorn' | grep -v grep
systemctl status --no-pager aladdin-backend.service
```

Если в логах `Handling signal: term`, это controlled shutdown (не boot-crash).

### 10.5 Проверка, что нужные маршруты реально подхватились
После перезапуска обязательно проверяем OpenAPI:

```bash
curl -s -S -m 12 http://localhost:8002/openapi.json -o /tmp/openapi_now.json
python3 - <<'PY'
import json
j=json.load(open('/tmp/openapi_now.json','r',encoding='utf-8'))
paths=j.get('paths',{})
for p in [
 '/api/reports/identity-theft/allow',
 '/api/reports/identity-theft/block',
 '/api/reports/privacy/tracker/whitelist',
 '/api/reports/privacy/location/allow',
 '/api/reports/privacy/cleanup/start',
 '/api/reports/dark-web/scan/start',
]:
    print(p, sorted(paths.get(p, {}).keys()))
PY
```

Ожидаемо: для перечисленных путей есть `['get', 'post']`.

### 10.6 Важно по PostgreSQL правам для write-path
Если POST возвращает `500`, проверяйте `gunicorn.out`.  
В нашем кейсе причины были:
- `permission denied for table tracker_blocks`
- `permission denied for table cleanup_records`

Рабочий фикс:
```bash
sudo -u postgres psql -d aladdin_db -c "
GRANT USAGE ON SCHEMA darkweb, identity, tracker, location, cleanup TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE darkweb.darkweb_leaks TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE identity.identity_attempts TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE tracker.tracker_blocks TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE location.location_requests TO aladdin_user;
GRANT SELECT, INSERT, UPDATE ON TABLE cleanup.cleanup_records TO aladdin_user;
"
```

### 10.7 Что получилось по факту (валидировано)
- `:8002` стабильно поднимается и отвечает `api/health`.
- write-endpoints работают через реальные POST-вызовы (без mock fallback).
- `aladdin_analytics_freshness_seconds` обновляется по доменам после replay.
- `AladdinNoFreshDataByDomain` перестал быть активным после replay по 5 доменам.

Это эталонный runbook для других ML-систем: сначала сеть/процесс, затем OpenAPI-контракт, затем DB-права, затем replay и финальная проверка alerts.

---

## 11) Автоматизация: единый скрипт подключения и настройки сервера

Для ускорения повторяемых действий добавлен сценарий:

- Путь: `scripts/aladdin_server_connect_and_setup.sh`
- Использование:

```bash
chmod +x scripts/aladdin_server_connect_and_setup.sh
./scripts/aladdin_server_connect_and_setup.sh root 149.154.65.180 8002 /path/to/ssh_key
```

Что делает скрипт:
- выполняет аудит сервера (порты/директории);
- выравнивает `/opt/aladdin-backend` до `origin/master` c backup-веткой и `clean -fdX`;
- создаёт/обновляет `venv` и устанавливает зависимости (`fastapi`, `gunicorn`, `psycopg2-binary`, `asyncpg`, `PyJWT`, и др.);
- создаёт/включает systemd-юнит `aladdin-backend.service` на `:8002` c `DISABLE_SFM_MOCK=1` и `PYTHONPATH`;
- перезапускает сервис и проверяет:
  - `api/health` локально и снаружи,
  - отсутствие mock‑маркеров на `/api/auth/register-device`,
  - блокировку wildcard на критичных префиксах (`/api/auth/unknown` → 404),
  - наличие `/api/auth/register-device` в OpenAPI,
  - доступность `/api/reports/privacy/tracker/stats`.

Скрипт служит быстрым «подключить и проверить», соответствуя правилам no‑mock и precision‑роутинга.

---

## 12) P0: Выкат согласования семьи (`GET /api/family/members`)

После обновления `app/routers/family.py` в репозитории **обязательно** задеплойте файл на сервер, который реально обслуживает `:8002` (см. разделы 10–11).

**Автоматизация (SSH без интерактива):** на рабочей машине используйте выделенный ключ, например `~/.ssh/aladdin_server`, с `ssh -i … -o BatchMode=yes -o IdentitiesOnly=yes` (содержимое ключа и пароли в репозиторий не класть).

**Чеклист:**

1. Скопировать актуальный `app/routers/family.py` в дерево деплоя (`/opt/aladdin-backend/...` — путь по вашему окружению).
2. Перезапустить backend (gunicorn/systemd из раздела 10).
3. Проверить OpenAPI: у `GET /api/family/members` есть query `familyId` (optional).
4. С валидным токеном выполнить:
   - `GET .../api/family/members` — в ответе заголовки **`X-Resolved-Family-Id`** и **`X-Current-Member-Id`** (id членства текущего пользователя в этой семье; клиент сохраняет его как `your_member_id`).
   - Проверка вручную: `curl -sI -H "Authorization: Bearer <ACCESS>" 'https://<HOST>/api/family/members?familyId=<FAM>' | grep -i current`
   - `GET .../api/family/members?familyId=<НЕВЕРНЫЙ_ID>` — ожидается **409** (не смешивать контексты).
5. Метрики в логах: см. `docs/FAMILY_OPS_DASHBOARD.md`.

**Продуктовое правило «одна активная семья»:** `docs/FAMILY_MEMBERSHIP_PRODUCT.md`.

**Геймификация, OpenAPI и iOS (важно):**

1. **Импорт роутера:** в `main.py` геймификация подключается только если `from security.api.routers.gamification_router import router` выполняется без ошибки. Если в venv **нет** зависимостей из `backend/requirements.txt` (типичный случай — отсутствует **`python-jose`**, ошибка `No module named 'jose'`), флаг `gamification_router_available` остаётся `false`, и **весь** префикс `/api/gamification/*` пропадает из OpenAPI.

2. **Синхронизация venv с репозиторием (рекомендуется на каждый выкат):**
   ```bash
   cd /opt/aladdin-backend
   ./venv/bin/pip install -r backend/requirements.txt
   ./venv/bin/python3 -m py_compile main.py
   systemctl restart aladdin-backend.service
   ```
   Файл на проде: `backend/requirements.txt` (должен совпадать с репозиторием `mobile_apps/ALADDIN_iOS/backend/requirements.txt`). Так venv не «обедняется» относительно кода.

3. **Паритет файла роутера с репозиторием:** на проде могла лежать **урезанная** версия `security/api/routers/gamification_router.py` (например, только SFM/`GET` для `/balance`). iOS для начисления/списания вызывает **`POST /api/gamification/balance`** (`AppConfig.gamificationBalanceAdd` / `Subtract`). В OpenAPI у `/api/gamification/balance` должны быть **`get` и `post`**; у `rewards/claim`, `rewards/give`, `rewards/purchase`, `tournaments/join`, `tournaments/leave` — **`post`** там, где в каноническом роутере объявлен `post`. После выката полного файла из репозитория перезапустите сервис и проверьте методы в `openapi.json` (скриптом или `tools/release_openapi_drift_and_ios_sync.py`).

4. **Быстрая проверка снаружи (после рестарта):**  
   `curl -s -S -m 20 http://149.154.65.180:8002/openapi.json` → в `paths["/api/gamification/balance"]` есть и `get`, и `post`; всего путей с `/api/gamification` — **26**.

---

## 13) Выкат антивирусного скана файла (`POST /api/antivirus/scan`)

Контракт совпадает с iOS (`MalwareFileScanAPIRequest` / `MalwareFileScanAPIResponse`): тело JSON в **snake_case** (`file_data` base64, `file_name`, `file_size`, опционально `file_hash`); ответ — `clean`, `threats_found`, `recommendations`, `scan_time`, `confidence`. Роутер: `app/routers/antivirus.py`; подключение в `main.py` (флаги `antivirus_router_available` + `app.include_router(antivirus.router)`).

**Чеклист (как на проде, апрель 2026):**

1. **Снаружи:** `curl -s -S -m 8 http://149.154.65.180:8002/api/health` → `200`, JSON со `status`.
2. **Бэкап на сервере:** `cp -a /opt/aladdin-backend/main.py /opt/aladdin-backend/main.py.bak_<timestamp>` (и при замене целого `main.py` — обязателен).
3. **Файлы:** скопировать `app/routers/antivirus.py` → `/opt/aladdin-backend/app/routers/antivirus.py`; в `main.py` добавить импорт/`include_router` для `antivirus` (если ещё нет — см. репозиторий `mobile_apps/ALADDIN_iOS`).
4. **Синтаксис:** `cd /opt/aladdin-backend && ./venv/bin/python3 -m py_compile app/routers/antivirus.py main.py`
5. **Перезапуск:** `systemctl restart aladdin-backend.service` → `systemctl is-active aladdin-backend.service` → `active`.
6. **Проверки:**
   - локально на сервере: `curl -s -S -m 8 http://127.0.0.1:8002/api/health`
   - снаружи: тот же `curl` на `:8002`
   - OpenAPI: `curl -s -S -m 12 http://149.154.65.180:8002/openapi.json` — в `paths` должен быть ключ **`/api/antivirus/scan`** с методом `post`.
   - смоук POST (минимальный чистый файл, 1 байт):  
     `curl -s -S -m 12 -X POST http://149.154.65.180:8002/api/antivirus/scan -H "Content-Type: application/json" -d '{"file_data":"QQ==","file_name":"t.txt","file_size":1}'` → **200**, в теле `"clean":true` (или сработавший тест EICAR в `threats_found`).

**Лимит:** декодированное тело не более **25 MiB** (как на iOS); иначе **413**.

**Журнал:** успешный выкат зафиксирован при живом `systemd`-юните `aladdin-backend.service` и появлении маршрута в OpenAPI на `:8002`.

---

## 14) Угрозы и карантин (`/api/malware/*`, `/api/protection/*`) — контракт с iOS

Клиент (`APIService.getUserThreatsAsync`, `quarantineFileAsync`) ожидает:

- **`GET /api/malware/threats`** (опционально `?status=`) — JSON-объект **`ThreatsListResponse`**: поля `threats`, `total`, `active`, `quarantined`, `resolved` (не «сырой» массив).
- **`POST /api/malware/quarantine/action`** — тело **`{ "threatId", "action", "filePath"? }`** (camelCase), ответ **`{ "success", "message"?, "threat"? }`**. Допустимо оставить легаси **`GET`** на том же пути для совместимости; в OpenAPI должны быть **`get` и `post`**.
- Аналогично для префикса **`/api/protection/threats`** и **`/api/protection/quarantine/action`**, если клиент или альтернативные экраны используют эти URL.

**Источник правды на сервере:** PostgreSQL, таблица **`user_malware_threats`** (см. `app/database/migrations/create_user_malware_threats.sql`). При первом обращении таблица также создаётся из кода (`ensure_user_malware_threats_table`). Для прод-деплоя предпочтительно один раз применить миграцию на хосте с `DATABASE_URL`:  
`python3 app/database/migrations/apply_user_malware_threats_migration.py`

**Запись при скане:** `POST /api/antivirus/scan` при валидном JWT сохраняет найденные сигнатуры в **`user_malware_threats`** (роутер `app/routers/antivirus.py`, логика `app/services/user_malware_threats.py`). Содержимое файла не пишется; в БД допускаются только метаданные (имя/размер/путь как строка, опциональный **`file_hash`** от клиента). Сессия PostgreSQL открывается **только** если есть и JWT, и найденные угрозы (чистый скан без записи не требует БД). Без JWT ответ скана прежний, строки в БД не пишутся.

**Автопроверка (без пароля):** с хоста разработки при живом API:  
`ALADDIN_API_BASE=http://149.154.65.180:8002 python3 tools/smoke_malware_threats_persist.py` — ожидается `OK`: реальные вызовы к прод-шлюзу, запись в PostgreSQL, затем **`POST /api/malware/quarantine/action`** и проверка **`GET /api/malware/threats?status=quarantined`** (строка `eicar-test` в статусе `quarantined`).

**Отчёты 5 доменов + driving + ai-categories (план ML):**  
`ALADDIN_API_BASE=http://149.154.65.180:8002 python3 tools/smoke_reports_five_domains.py` — **OK**, если все `GET /api/reports/*/stats` и пять list‑эндпоинтов вернули **200** и в теле нет `sfm_mock` / `mock_fallback` / `reports_compat`.

**Связка с карантином на устройстве:** iOS при помещении в карантин передаёт **`threatId`**, совпадающий с id угрозы со скана (например `eicar-test`), см. `QuarantineManager.quarantineFile(..., stableThreatId:)` и `AntivirusManager.quarantineThreat`.

Роутеры: `app/routers/misc_other_compat.py`, `app/routers/antivirus.py`. После правок:  
`python3 -m py_compile app/routers/misc_other_compat.py app/routers/antivirus.py app/services/user_malware_threats.py app/auth/auth.py`, выкат каталога **`app/services/`** и перечисленных файлов в `/opt/aladdin-backend/`, **`systemctl restart aladdin-backend.service`**, прогон `tools/release_openapi_drift_and_ios_sync.py`.

# Handoff для ML: Postgres (p3-11) + Parent LLM (p3-16)

> **Назначение:** передать другой ML-системе **только две** ops-задачи. Canary и Sleep **не входят** в этот handoff.  
> **Обновлено:** 2026-06-02  
> **Рабочая папка (обязательно):**  
> `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

---

## 0. Первое сообщение для новой ML (скопировать целиком)

```text
Ты — backend + iOS ops для ALADDIN Wellness.

Рабочай ТОЛЬКО в:
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

Прочитай:
1) docs/WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md (этот файл)
2) docs/WELLNESS_POSTGRES_MIGRATION.md
3) security/services/ai_platform/wellness_parent_playbook.py

Сделай по порядку:
A) Parent LLM — фазы A→B на VPS, PO checklist, verify
B) Postgres — установка PG на VPS, миграция, dual-write, cutover

Сервер: root@149.154.65.180, backend /opt/aladdin-backend, SSH key ~/.ssh/aladdin_server
Prod URL: https://aladdin-ai.ru

iOS фаза C (use_llm в API) уже в коде — нужен App Store / TestFlight билд после флага на prod.

Не трогай: WELLNESS_CANARY_PERCENT (оставить 100), Sleep audio. Rive = только 3× `Resources/Companion/*.riv` ([RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md)).
Пароли не коммитить. После каждого шага — verify_wellness_prod.sh.
```

---

## 1. Что уже сделано в репозитории (не переделывать)

| Компонент | Файл | Статус |
|-----------|------|--------|
| Parent LLM + Hermes | `wellness_parent_playbook.py` | ✅ `FEATURE_WELLNESS_PARENT_LLM` gate |
| API endpoint | `GET /api/wellness/parent/playbook?use_llm=&topic=&teen_mood=` | ✅ `wellness_router.py` |
| iOS запрос с LLM | `WellnessAPIService.fetchParentPlaybook(useLlm: true)` | ✅ |
| Hub загрузка | `WellnessHubScreen.loadFamilyThemesIfParent()` | ✅ `useLlm: true` |
| Postgres schema | `wellness_pg_schema.sql` | ✅ |
| Dual-write hooks | `wellness_store_dual.py`, `companion_store.py` | ✅ checkins + settings |
| Migration script | `scripts/migrate_wellness_sqlite_to_pg.py` | ✅ |
| Docker bootstrap (локально) | `scripts/setup_wellness_postgres_docker.sh` | ✅ VPS **без Docker** — apt |
| Deploy | `scripts/deploy_wellness_p1.sh` | ✅ включает новые файлы |
| Tests | `Tests/test_wellness_canary_pg.py` | ✅ |

**Prod .env сейчас (типично):**

```env
FEATURE_WELLNESS_PARENT_LLM=0
WELLNESS_PG_DSN=          # не задан
WELLNESS_PG_DUAL_WRITE=0
WELLNESS_PG_READ=0
WELLNESS_CANARY_PERCENT=100
```

---

## 2. Задача A — Parent LLM (p3-16)

### 2.1 Зачем

Родитель видит карточку **«Как поговорить»** на Wellness Hub. Без LLM — фиксированные фразы из `wellness_i18n/playbook_v1.json`. С LLM — Hermes добавляет **2–3 короткие фразы** под `topic` / `teen_mood`. **Чат ребёнка не читается.**

### 2.2 Два предохранителя

| Уровень | Переменная / параметр | Сейчас prod |
|---------|----------------------|-------------|
| Сервер | `FEATURE_WELLNESS_PARENT_LLM=1` | **0** |
| Запрос | `use_llm=true` | iOS шлёт после билда; curl — вручную |

Оба должны быть **1/true**, иначе только JSON.

### 2.3 Фаза A — тест на prod (без App Store)

#### A1 — SSH и .env

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
cd /opt/aladdin-backend
nano .env   # или vi
```

Добавить или изменить:

```env
FEATURE_WELLNESS_PARENT_LLM=1
```

#### A2 — Restart

```bash
systemctl restart aladdin-backend.service
systemctl status aladdin-backend.service --no-pager
```

#### A3 — JWT родителя

**Нужен JWT с `age_band=parent` или `senior`**, не child/teen.

Вариант 1 — register-device (как verify script):

```bash
DEVICE_ID="parent-llm-test-$(date +%s)"
RESP=$(curl -sS -X POST "https://aladdin-ai.ru/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"${DEVICE_ID}\",\"deviceType\":\"ios\"}")
# Если API возвращает child — использовать mint на сервере (вариант 2)
```

Вариант 2 — mint на VPS (надёжно для parent):

```bash
cd /opt/aladdin-backend
PYTHONPATH=. ./venv/bin/python3 <<'PY'
import os, time, jwt
from dotenv import load_dotenv
load_dotenv(".env")
secret = os.environ["JWT_SECRET"]
now = int(time.time())
payload = {
    "user_id": 901803,
    "sub": "901803",
    "type": "access",
    "age_band": "parent",
    "subscription_level": "premium",
    "iat": now,
    "exp": now + 3600,
}
print(jwt.encode(payload, secret, algorithm=os.getenv("JWT_ALGORITHM", "HS256")))
PY
```

Сохранить токен в `PARENT_TOKEN=...`

#### A4 — Curl проверка

```bash
curl -sS "https://aladdin-ai.ru/api/wellness/parent/playbook?locale=ru&use_llm=true&topic=school&teen_mood=sad" \
  -H "Authorization: Bearer ${PARENT_TOKEN}" | python3 -m json.tool
```

**Ожидание:**

- `phrases` — массив, ≥4 элементов
- Первые 1–3 с `"id": "llm_1"` … если Hermes OK
- `"llm_used": true` — если LLM сработал
- `"llm_used": false` — Hermes недоступен, но JSON-фразы есть (это OK для отката)

Повторить `locale=en`.

#### A5 — PO checklist (15–20 мин)

| # | Проверка | Pass |
|---|----------|------|
| 1 | Нет «терапия», «лечим», «диагноз» | ☐ |
| 2 | Нет «назначим психолога» / «замена психолога» | ☐ |
| 3 | Нет «прочитал чат» / «вижу переписку» | ☐ |
| 4 | Фразы короткие (1–2 предложения) | ☐ |
| 5 | ru и en осмысленны | ☐ |
| 6 | При `llm_used: false` — UI всё равно с фразами из JSON | ☐ |

**Записать в:** `docs/WELLNESS_CLINICAL_REVIEW.md` (строка Parent LLM PO review + дата) или отдельный комментарий PO.

**Если checklist FAIL** → сразу откат (раздел 2.6), не переходить к фазе B.

### 2.4 Фаза B — оставить на prod

После ✅ A5:

- `FEATURE_WELLNESS_PARENT_LLM=1` **остаётся** в `.env`
- `systemctl restart aladdin-backend.service`
- `./scripts/verify_wellness_prod.sh https://aladdin-ai.ru` — **14/14**

### 2.5 Фаза C — iOS (код готов, нужен релиз)

| Шаг | Действие | Кто |
|-----|----------|-----|
| C1 | Код уже: `fetchParentPlaybook(useLlm: true)` | ✅ dev |
| C2 | Xcode Archive → TestFlight | PO/dev |
| C3 | Родительский аккаunt → Hub → карточка «Как поговорить» | PO QA |
| C4 | App Store submit | PO |

**QA на устройстве:** при `FEATURE_WELLNESS_PARENT_LLM=1` и новом билде — в ответе API `llm_used: true` (можно проверить proxy/логи).

### 2.6 Откат Parent LLM

```bash
# /opt/aladdin-backend/.env
FEATURE_WELLNESS_PARENT_LLM=0
systemctl restart aladdin-backend.service
```

Пользователи снова только JSON. iOS с `use_llm=true` не сломается — сервер игнорирует LLM.

---

## 3. Задача B — Postgres (p3-11)

### 3.1 Зачем

SQLite (`companion_store.db`) — один файл, сложнее масштабировать и бэкапить при росте. Postgres — отдельная БД, dual-write → безопасный переход.

### 3.2 Архитектура после cutover

```
Запись:  iOS → API → companion_store (SQLite) ──mirror──► Postgres (если DUAL_WRITE=1)
Чтение:  SQLite (по умолчанию) ИЛИ Postgres (если PG_READ=1)
```

### 3.3 Предусловия

- SSH root@149.154.65.180
- ~2 GB свободного места
- Бэкап SQLite **обязателен**
- **Не** ставить `WELLNESS_PG_READ=1` в первый день

### 3.4 Шаг B1 — установка PostgreSQL (VPS без Docker)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180

apt update
apt install -y postgresql postgresql-contrib

# Сильный пароль — сгенерировать локально, НЕ коммитить
export WELLNESS_DB_PASS='REPLACE_WITH_STRONG_PASSWORD'

sudo -u postgres psql -c "CREATE USER wellness WITH PASSWORD '${WELLNESS_DB_PASS}';"
sudo -u postgres psql -c "CREATE DATABASE wellness OWNER wellness;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE wellness TO wellness;"

# Проверка
sudo -u postgres psql -d wellness -c "SELECT 1;"
```

### 3.5 Шаг B2 — .env на backend

```bash
cd /opt/aladdin-backend
nano .env
```

Добавить (подставить реальный пароль):

```env
WELLNESS_PG_DSN=postgresql://wellness:REPLACE_WITH_STRONG_PASSWORD@127.0.0.1:5432/wellness
WELLNESS_PG_DUAL_WRITE=0
WELLNESS_PG_READ=0
```

### 3.6 Шаг B3 — psycopg2 + схема + миграция

```bash
cd /opt/aladdin-backend
./venv/bin/pip install psycopg2-binary

# Бэкап
cp -a data/companion_store.db "data/companion_store.pre_pg_$(date +%Y%m%d).bak"
# или путь где лежит db — проверить: find /opt/aladdin-backend -name companion_store.db

# Dry-run
PYTHONPATH=. ./venv/bin/python3 scripts/migrate_wellness_sqlite_to_pg.py --dry-run

# Реальная миграция
PYTHONPATH=. ./venv/bin/python3 scripts/migrate_wellness_sqlite_to_pg.py
```

**Ожидание dry-run:** счётчики строк по таблицам без ошибок.

### 3.7 Шаг B4 — dual-write (7 дней)

```env
WELLNESS_PG_DUAL_WRITE=1
WELLNESS_PG_READ=0
```

```bash
systemctl restart aladdin-backend.service
```

**Проверка:**

```bash
curl -sS "https://aladdin-ai.ru/api/wellness/store/backend" \
  -H "Authorization: Bearer ${TEEN_OR_PARENT_TOKEN}" | python3 -m json.tool
```

Ожидание:

```json
{
  "backend": "postgres",
  "configured": true,
  "reachable": true,
  "dual_write": true,
  "read_postgres": false
}
```

**Smoke:**

```bash
cd /opt/aladdin-backend && PYTHONPATH=. ./venv/bin/python3 scripts/vps_smoke_wellness.py
```

Сделать test check-in → убедиться, что строка появилась в Postgres:

```bash
sudo -u postgres psql -d wellness -c "SELECT user_id, day FROM wellness_checkins ORDER BY created_at DESC LIMIT 3;"
```

### 3.8 Шаг B5 — cutover read (не раньше чем через 7 дней)

После недели без инцидентов:

```env
WELLNESS_PG_READ=1
```

```bash
systemctl restart aladdin-backend.service
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
```

`store/backend` → `"read_postgres": true`.

### 3.9 Откат Postgres

| Ситуация | Действие |
|----------|----------|
| Dual-write ломает запись | `WELLNESS_PG_DUAL_WRITE=0`, restart |
| Read PG плохие данные | `WELLNESS_PG_READ=0`, restart (читаем SQLite) |
| Полный откат | Удалить `WELLNESS_PG_DSN` из `.env`, restart; SQLite backup на месте |

---

## 4. Порядок выполнения (рекомендация)

| День | Задача | Критерий готовности |
|------|--------|---------------------|
| 1 | Parent LLM A4 + A5 | PO checklist ✅, curl `llm_used` понятен |
| 1 | Parent LLM B | `FEATURE_WELLNESS_PARENT_LLM=1`, verify 14/14 |
| 2 | Postgres B1–B4 | migrate OK, dual_write=1, smoke OK |
| 2–9 | Мониторинг PG | Нет роста 5xx, checkins в PG |
| 10 | Postgres B5 | `PG_READ=1`, verify OK |
| 3+ | iOS TestFlight | Hub playbook с LLM фразами |

**Parent LLM можно делать параллельно с Postgres B1–B3**, но не менять `.env` хаотично — один restart за раз, записать что меняли.

---

## 5. Команды verify (после каждого блока)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
```

На VPS:

```bash
cd /opt/aladdin-backend && PYTHONPATH=. ./venv/bin/python3 scripts/vps_smoke_wellness.py
```

---

## 6. Файлы — карта

| Тема | Путь |
|------|------|
| Parent LLM logic | `security/services/ai_platform/wellness_parent_playbook.py` |
| i18n phrases | `security/services/ai_platform/wellness_i18n/playbook_v1.json` |
| Router | `security/api/routers/wellness_router.py` → `parent_playbook` |
| Feature flag | `security/services/ai_platform/feature_flags.py` |
| iOS API | `Core/Services/WellnessAPIService.swift` |
| iOS Hub | `Screens/WellnessHubScreen.swift` |
| PG store | `security/services/ai_platform/wellness_store_postgres.py` |
| PG dual-write | `security/services/ai_platform/wellness_store_dual.py` |
| PG schema SQL | `security/services/ai_platform/wellness_pg_schema.sql` |
| Migrate | `scripts/migrate_wellness_sqlite_to_pg.py` |
| Deploy | `scripts/deploy_wellness_p1.sh` |
| Server guide | `docs/ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` |

---

## 7. Частые ошибки

| Ошибка | Решение |
|--------|---------|
| `parent_only` 403 | JWT должен быть `age_band=parent` |
| `llm_used: false` всегда | Hermes/OpenRouter ключи; `hermes_available()` на VPS |
| `FEATURE_WELLNESS_PARENT_LLM=1` но нет LLM фраз | Нет `use_llm=true` в запросе |
| Postgres `reachable: false` | DSN, пароль, `systemctl status postgresql` |
| migrate пустой | Путь к `companion_store.db` |
| После PG_READ пропали checkins | Откат `PG_READ=0`, проверить dual-write логи |

---

## 8. Критерии «задача закрыта»

### Parent LLM

- [ ] `FEATURE_WELLNESS_PARENT_LLM=1` на prod
- [ ] PO checklist задокументирован
- [ ] curl ru/en с `llm_used: true` (или осознанный fallback с PO OK)
- [ ] verify_wellness_prod 14/14
- [ ] TestFlight билд с новым iOS (опционально до App Store)

### Postgres

- [ ] PostgreSQL установлен, `wellness` DB создана
- [ ] migrate без `--dry-run` выполнен
- [ ] 7+ дней `DUAL_WRITE=1` без инцидентов
- [ ] `PG_READ=1`, `store/backend` OK
- [ ] verify + smoke OK

---

*Handoff для ML · p3-11 + p3-16 only · 2026-06-02*

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

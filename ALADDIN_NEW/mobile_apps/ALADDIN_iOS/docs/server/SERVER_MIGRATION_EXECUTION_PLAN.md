# 🧭 SERVER MIGRATION EXECUTION PLAN (root@149.154.65.180)

Документ предназначен для любой ML‑системы, которая будет выполнять перенос и развёртывание серверной части ALADDIN. Здесь собраны структура каталогов, чеклист действий и команды (через `expect`), чтобы процесс можно было повторить без потерь.

---

## 0. Целевая структура на сервере

Подтверждена по `COMPLETE_SERVER_MIGRATION_PLAN.md`, `FINAL_MIGRATION_GUIDE.md` и `OPTIMIZED_SERVER_MIGRATION_LIST.md` — всё должно лежать в `/opt/aladdin-backend/`:

```
/opt/aladdin-backend/
├── security/
│   ├── safe_function_manager.py
│   ├── ai_agents/               (76 файлов)
│   ├── bots/                    (30 файлов)
│   ├── managers/                (24 файла)
│   ├── microservices/           (17 файлов)
│   ├── active/                  (7 файлов)
│   ├── family/                  (18 файлов)
│   ├── antivirus/               (7 файлов)
│   ├── vpn/                     (~20 критичных серверных файлов)
│   ├── compliance/, core/, orchestration/ и т.д.
│   └── критичные security‑модули (`access_control.py`, `zero_trust_manager.py`, …)
├── scripts/
│   └── sfm_structure_validator.py
├── data/
│   └── sfm/
│       └── function_registry.json
├── requirements.txt
└── venvs/
    └── main_env/                (виртуальное окружение Python)
```

> **Важно:** переносим только оптимизированный набор (~220 файлов + `function_registry.json` + `requirements.txt`). Документация, тесты, `analyze_*`, `fix_*`, backup файлы остаются локально.

---

## 1. Подготовка на локальной машине (Mac)

1. **Бэкап**  
   ```bash
   cd /Users/sergejhlystov/ALADDIN_NEW
   tar -czf ../backup_before_migration_$(date +%Y%m%d_%H%M%S).tar.gz \
       --exclude='*.pyc' --exclude='__pycache__' --exclude='*.log' \
       security/ scripts/ data/ requirements.txt
   ```

2. **Зафиксировать статистику/контрольные суммы**  
   ```bash
   find security -name "*.py" -type f | wc -l                 # ожидаем 558
   find security/ai_agents -name "*.py" -type f | wc -l       # 76
   find security/bots -name "*.py" -type f | wc -l            # 30
   find security/managers -name "*.py" -type f | wc -l        # 24
   md5 security/safe_function_manager.py
   md5 scripts/sfm_structure_validator.py
   md5 requirements.txt
   ```

3. **Проверить содержимое архива**  
   ```bash
   gzip -t ../backup_before_migration_*.tar.gz
   tar -tzf ../backup_before_migration_*.tar.gz | head
   ```

---

## 2. Создание инфраструктуры на сервере (через сетевое окно + `expect`)

> Все ssh/scp команды выполняются в отдельном «сетевом» терминале, где установлен `expect`.

1. **Создать каталоги**  
   ```bash
   expect -c "
   set timeout 120
   set password \"Sergio675\"
   spawn ssh root@149.154.65.180 \"mkdir -p /opt/aladdin-backend/security \
     /opt/aladdin-backend/scripts /opt/aladdin-backend/data/sfm /opt/aladdin-backend/venvs\"
   expect {
     \"yes/no\" { send \"yes\\r\"; exp_continue }
     \"password:\" { send \"$password\\r\" }
   }
   expect eof
   "
   ```

2. **Проверить**  
   ```bash
   expect -c "
   set timeout 60
   set password \"Sergio675\"
   spawn ssh root@149.154.65.180 \"ls -la /opt/aladdin-backend\"
   expect \"password:\" { send \"$password\\r\" }
   expect eof
   "
   ```

3. **Создать виртуальное окружение**  
   ```bash
   expect -c "
   set timeout 60
   set password \"Sergio675\"
   spawn ssh root@149.154.65.180 \"python3 -m venv /opt/aladdin-backend/venvs/main_env\"
   expect \"password:\" { send \"$password\\r\" }
   expect eof
   "
   ```

---

## 3. Перенос файлов блоками (каждый блок = копировать → проверить ДО/ПОСЛЕ)

### Общий шаблон копирования
```bash
expect -c "
set timeout 180
set password \"Sergio675\"
spawn rsync -avz --progress /Users/sergejhlystov/ALADDIN_NEW/<локальный путь>/ \
    root@149.154.65.180:/opt/aladdin-backend/<серверный путь>/
expect \"password:\" { send \"$password\\r\" }
expect eof
"
```

### Блоки:
1. **SFM + валидатор + requirements**  
   - ДО: `md5` локальных файлов.  
   - Копировать `security/safe_function_manager.py`, `scripts/sfm_structure_validator.py`, `requirements.txt`.  
   - ПОСЛЕ: `md5sum` на сервере + `python3 -m compileall` + тест валидатора.

2. **AI Agents (76 файлов)**  
   - ДО: `find security/ai_agents -name "*.py" | wc -l`.  
   - Копия целой папки.  
   - ПОСЛЕ: подсчитать файлы на сервере, `python3 -m compileall /opt/aladdin-backend/security/ai_agents`.

3. **Bots (30 файлов)**  
4. **Managers (24 файла)**  
5. **Microservices (17 файлов)**  
6. **Active + Family modules (7 + 18 файлов)**  
7. **VPN + Antivirus + Compliance + Core**  
8. **Критичные security‑модули (~20 файлов)**  
9. **`data/sfm/function_registry.json`**  

> Для каждого блока:  
> - Перед копированием — зафиксировать количество файлов/контрольные суммы.  
> - После копирования — повторить подсчёт/`md5sum` и запустить короткий smoke‑тест (`python3 -m compileall`, запуск соответствующего менеджера и т.д.).

### Установка зависимостей

```bash
expect -c "
set timeout 300
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"source /opt/aladdin-backend/venvs/main_env/bin/activate && pip install -r /opt/aladdin-backend/requirements.txt\"
expect \"password:\" { send \"$password\\r\" }
expect eof
"
```

---

## 4. Серверные настройки (Этап 3 плана)

- Firewall (`ufw` или iptables) — открыть 22/80/443, закрыть лишнее.
- SSL (certbot или вручную).  
- PostgreSQL: `apt install postgresql`, создать `aladdin_db`/`aladdin_user`.  
- Nginx: разместить конфиг `/etc/nginx/sites-available/aladdin.conf`, включить, `nginx -t`, `systemctl reload nginx`.  
- API Gateway: убедиться, что `security/microservices/api_gateway.py` работает (env vars, systemd unit).  
- Logging & monitoring: `monitor_manager.py`, `performance_optimization_agent.py`, `journalctl`.  
- Rate limiting, резервное копирование, systemd сервисы (`systemctl enable --now <service>`).

---

## 5. Тестирование и релиз

1. **Функциональные тесты (Этап 4)**  
   - API endpoints (curl/Postman).  
   - 138 функций защиты, тарифы, семейные сценарии.  
   - Нагрузочные тесты, безопасность, перформанс.  
   - Исправить найденные баги и повторить проверку.

2. **App Store (Этап 5)**  
   - Code signing, архив, выгрузка в App Store Connect.  
   - Метаданные, Privacy Policy, скриншоты.  
   - Отправка на ревью, обработка замечаний, релиз.

---

## 6. Sleep Mode интеграция

- Убедиться, что 9 мобильных функций (`mobile_security_agent`, `mobile_navigation_bot`, `voice_control_manager`, …) имеют `mode: "sleep"` и `trigger: "client_active"` в `/opt/aladdin-backend/data/sfm/function_registry.json`.
- API `/sfm/function-status` (в `api_gateway.py`) принимает POST от iOS и управляет `SleepModeManager`.
- Проверить файлы `sleep_state_<function>.json` и метрики `monitor_manager.py`.
- При необходимости использовать `scripts/put_function_to_sleep.py` (на сервере) для ручного управления.

---

## 7. TODO / Чеклист

| ID    | Шаг | Статус |
|-------|------|--------|
| plan1 | Подготовка/бэкап + контрольные суммы | ✅ |
| plan2 | Перенос SFM + валидатор + requirements (до/после проверки) | ⏳ |
| plan3 | Перенос AI Agents (76) (до/после) | ⏳ |
| plan4 | Перенос Bots (30) (до/после) | ⏳ |
| plan5 | Перенос Managers (24) (до/после) | ⏳ |
| plan6 | Перенос Microservices (17) (до/после) | ⏳ |
| plan7 | Перенос Active & Family (до/после) | ⏳ |
| plan8 | Перенос VPN + Antivirus + Compliance + Core (до/после) | ⏳ |
| plan9 | Перенос критичных security файлов (до/после) | ⏳ |
| plan10| Перенос function_registry.json (до/после) | ⏳ |
| plan11| Серверные настройки (firewall/SSL/DB/Nginx/…) | ⏳ |
| plan12| Тестирование + App Store | ⏳ |

Каждый пункт включает **фиксирование состояния до**, **копирование**, **проверки после** и соответствующие smoke-тесты.

---

Таким образом, любая ML‑система, следуя этому документу, сможет повторить перенос и развёртывание без риска потерять файлы или нарушить структуру. Если требуется выполнить конкретную команду, используйте `expect` из этого же документа либо шаблоны из `docs/server/QUICK_REFERENCE.md`. 
# 📦 Server Migration Execution Plan (для ML системы)

Документ описывает полный процесс переноса проекта ALADDIN на сервер `root@149.154.65.180`, включая структуру каталогов, последовательность действий и команды, которые должна выполнять другая ML система.

---

## 1. Целевая структура на сервере

Структура подтверждена — именно так всё должно лежать на сервере после переноса:

```
/opt/aladdin-backend/
├── security/
│   ├── safe_function_manager.py
│   ├── ai_agents/               (76 файлов)
│   ├── bots/                    (30 файлов)
│   ├── managers/                (24 файла)
│   ├── microservices/           (17 файлов)
│   ├── active/                  (7 файлов)
│   ├── family/                  (18 файлов)
│   ├── antivirus/               (7 файлов)
│   ├── vpn/                     (~20 критичных файлов)
│   └── критичные модули security/ (access_control.py, zero_trust_manager.py и т.д.)
├── scripts/
│   └── sfm_structure_validator.py
├── data/
│   └── sfm/
│       └── function_registry.json
├── requirements.txt
└── venvs/
    └── main_env/                (виртуальное окружение)
```

---

## 2. Подготовка на локальной машине (Mac)

1. **Бэкап**:
   ```bash
   tar -czf ../backup_before_migration_$(date +%Y%m%d_%H%M%S).tar.gz \
       --exclude='*.pyc' --exclude='__pycache__' --exclude='*.log' \
       security/ scripts/ data/ requirements.txt
   ```
2. **Статистика и проверки**:
   ```bash
   find security -name "*.py" -type f | wc -l          # 558
   find security/ai_agents -name "*.py" -type f | wc -l # 76
   find security/bots -name "*.py" -type f | wc -l      # 30
   find security/managers -name "*.py" -type f | wc -l  # 24
   md5 security/safe_function_manager.py
   md5 scripts/sfm_structure_validator.py
   md5 requirements.txt
   ```
   Сохраняем эти значения для сравнения после копирования на сервер.

---

## 3. Работа на сервере (через `expect`)

Во всех командах используем:
- Сервер: `root@149.154.65.180`
- Пароль: `Sergio675`

### 3.1 Создание базовой структуры

```bash
expect -c "
set timeout 120
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \
  \"mkdir -p /opt/aladdin-backend/security \
           /opt/aladdin-backend/scripts \
           /opt/aladdin-backend/data/sfm \
           /opt/aladdin-backend/venvs\"
expect {
    \"yes/no\" { send \"yes\\r\"; exp_continue }
    \"password:\" { send \"$password\\r\" }
}
expect eof
"
```

### 3.2 Создание виртуального окружения

```bash
expect -c "
set timeout 120
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"python3 -m venv /opt/aladdin-backend/venvs/main_env\"
expect \"password:\" { send \"$password\\r\" }
expect eof
"
```

---

## 4. Перенос файлов блоками (rsync + проверки)

Шаблон команды:
```bash
expect -c "
set timeout 180
set password \"Sergio675\"
spawn rsync -avz --progress <локальный_путь>/ root@149.154.65.180:<серверный_путь>/
expect \"password:\" { send \"$password\\r\" }
expect eof
"
```

Для каждого блока:
1. На Mac фиксируем контрольные суммы/количество файлов.
2. Копируем через rsync.
3. На сервере проверяем `md5sum`/`find ... | wc -l`.
4. Запускаем быстрый `python3 -m compileall <каталог>` или соответствующий smoke-тест.

### Блоки
1. **SFM + валидатор + requirements**
2. **AI Agents (76 файлов)**
3. **Bots (30 файлов)**
4. **Managers (24 файла)**
5. **Microservices (17 файлов)**
6. **Active + Family**
7. **VPN + Antivirus + Compliance + Core**
8. **Критичные файлы security/**
9. **`data/sfm/function_registry.json`**

---

## 5. Установка зависимостей

```bash
expect -c "
set timeout 300
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \
  \"source /opt/aladdin-backend/venvs/main_env/bin/activate && \
    pip install -r /opt/aladdin-backend/requirements.txt\"
expect \"password:\" { send \"$password\\r\" }
expect eof
"
```

---

## 6. Настройки серверной инфраструктуры

Выполняем шаги из `COMPLETE_SERVER_MIGRATION_PLAN.md`:  
- Firewall (`ufw`/iptables).  
- SSL (certbot/сертификаты).  
- PostgreSQL (создать пользователя, базу).  
- Nginx (конфиг, `systemctl reload nginx`).  
- API Gateway (проверить службу, systemd unit).  
- Monitoring/logging/rate limiting.  
- Резервное копирование, systemd-сервисы.

---

## 7. Тестирование

1. API endpoints (`curl`, Postman, pytest).  
2. 138 функций защиты и тарифы.  
3. Нагрузочное тестирование.  
4. Тесты безопасности (сканы, firewall, SSL).  
5. Убедиться, что `scripts/sfm_structure_validator.py` проходит без ошибок.

---

## 8. App Store шаги

Согласно плану: code signing, архив, загрузка в App Store Connect, метаданные, скриншоты, Privacy Policy, Terms, ревью, релиз.

---

## 9. Sleep Mode интеграция

1. Проверить, что 9 мобильных функций (`mobile_security_agent` и т.д.) имеют `mode: "sleep"` в `/opt/aladdin-backend/data/sfm/function_registry.json`.  
2. Убедиться, что API `/sfm/function-status` (в `security/microservices/api_gateway.py`) принимает сигналы от клиента.  
3. Проверить `sleep_state_<function>.json` и записи в мониторинге (`monitor_manager.py`, `performance_optimization_agent.py`).

---

## 10. TODO чеклист (для трекинга)

- [ ] Подготовка/бэкап + контрольные суммы  
- [ ] Перенос SFM + валидатор + requirements (до/после проверка)  
- [ ] Перенос AI Agents (до/после)  
- [ ] Перенос Bots (до/после)  
- [ ] Перенос Managers (до/после)  
- [ ] Перенос Microservices (до/после)  
- [ ] Перенос Active & Family (до/после)  
- [ ] Перенос VPN + Antivirus + Compliance + Core (до/после)  
- [ ] Перенос критичных security файлов (до/после)  
- [ ] Перенос function_registry.json (до/после)  
- [ ] Серверные настройки (firewall, SSL, БД, Nginx, systemd)  
- [ ] Тестирование и App Store шаги  
- [ ] Sleep Mode проверка

---

## Примечания

- Все сетевые команды (ssh/scp/expect) выполняются в отдельном “сетевом” терминале.  
- В локальном терминале работаем только с кодом и документацией.  
- Пароль `Sergio675` использовать только внутри `expect`, не коммитить в репозиторий.  
- После каждого блока строго сверяем контрольные суммы и запускаем короткие тесты.  
- Структура `/opt/aladdin-backend/` из раздела 1 является эталоном — отклонения не допускаются.



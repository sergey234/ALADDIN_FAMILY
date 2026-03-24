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

# 🔌 **ПОЛНОЕ РУКОВОДСТВО ПО ПОДКЛЮЧЕНИЮ К СЕРВЕРУ ALADDIN ДЛЯ ML СИСТЕМ**

---

## 🖥️ **ОБЗОР СЕРВЕРНОЙ АРХИТЕКТУРЫ**

**Сервер:** ALADDIN Production Server  
**IP Адрес:** `149.154.65.180`  
**Порты:** `22` (SSH), `8002` (API Gateway)  
**Пользователь:** `root`  
**Пароль:** `Sergio675`  

---

## 🛠️ **СПОСОБЫ ПОДКЛЮЧЕНИЯ**

### **1. SSH (КОМАНДНАЯ СТРОКА)**
Используйте терминал для выполнения команд на сервере.

```bash
# Подключение
ssh root@149.154.65.180
# Введите пароль: Sergio675
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
- **Password:** `Sergio675`

**ЧТО ЗАГРУЖАТЬ:**
- `api_gateway_complete_full.py` -> `/opt/aladdin-backend/`
- `app/routers/referral_fixed.py` -> `/opt/aladdin-backend/app/routers/`

---

## 🚨 **ПРОБЛЕМЫ И РЕШЕНИЯ**

### **ПРОБЛЕМА 1: "Permission denied"**
- Проверьте правильность пароля (`Sergio675` - первая буква заглавная).
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

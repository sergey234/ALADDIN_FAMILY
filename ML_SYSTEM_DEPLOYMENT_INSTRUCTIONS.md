# 📤 **ИНСТРУКЦИИ ДЛЯ ML СИСТЕМЫ: РАЗВЕРТЫВАНИЕ ОБНОВЛЕНИЙ НА СЕРВЕРЕ ALADDIN**

## 🎯 **ЦЕЛЬ ЗАДАЧИ:**
Отправить обновленные файлы API Gateway на сервер ALADDIN для устранения 404 ошибок и добавления новых эндпоинтов.

---

## 📋 **КРИТИЧЕСКИ ВАЖНЫЕ ФАЙЛЫ ДЛЯ ОТПРАВКИ:**

### **1. ОСНОВНОЙ ФАЙЛ API GATEWAY:**
```
ЛОКАЛЬНЫЙ ПУТЬ: /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/api_gateway_complete_full.py
УДАЛЕННЫЙ ПУТЬ: /opt/aladdin-backend/api_gateway_complete_full.py
РАЗМЕР: 104,598 байт
СОДЕРЖИТ: 
- 19 НОВЫХ ЭНДПОИНТОВ (Protection, Metrics, Darkweb, Identity, Privacy)
- 10+ ПОДКЛЮЧЕННЫХ РОУТЕРОВ
```

### **2. ИСПРАВЛЕННЫЙ РОУТЕР REFERRAL:**
```
ЛОКАЛЬНЫЙ ПУТЬ: /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/app/routers/referral_fixed.py
УДАЛЕННЫЙ ПУТЬ: /opt/aladdin-backend/app/routers/referral_fixed.py
РАЗМЕР: 17,072 байт
СОДЕРЖИТ: 
- 4 эндпоинта: /code, /stats, /history, /rewards
- Интеграция с PostgreSQL
```

---

## 🔌 **ПАРАМЕТРЫ ПОДКЛЮЧЕНИЯ:**
- **IP:** `149.154.65.180`
- **User:** `root`
- **Password:** `Sergio675`
- **Protocol:** `SSH/SFTP`

---

## 🚀 **АЛГОРИТМ РАЗВЕРТЫВАНИЯ (РУЧНОЙ РЕЖИМ):**

### **ШАГ 1: ОТПРАВКА ФАЙЛОВ**
Выполните эти команды в терминале на вашем Mac (в папке проекта):

```bash
# 1. Отправка API Gateway
scp -o StrictHostKeyChecking=no api_gateway_complete_full.py root@149.154.65.180:/opt/aladdin-backend/

# 2. Отправка Referral Router
scp -o StrictHostKeyChecking=no app/routers/referral_fixed.py root@149.154.65.180:/opt/aladdin-backend/app/routers/
```
*При запросе пароля введите: `Sergio675`*

---

### **ШАГ 2: НАСТРОЙКА НА СЕРВЕРЕ**
Подключитесь к серверу и выполните команды:

```bash
# 1. Подключение
ssh root@149.154.65.180
# Пароль: Sergio675

# 2. Переход в папку
cd /opt/aladdin-backend

# 3. Резервная копия текущего файла
cp api_gateway.py api_gateway.backup.$(date +%Y%m%d_%H%M%S)

# 4. Замена файла
cp api_gateway_complete_full.py api_gateway.py
chmod +x api_gateway.py

# 5. Проверка синтаксиса (ВАЖНО!)
python3 -m py_compile api_gateway.py

# 6. Если ошибок нет - перезапуск сервиса
systemctl restart aladdin-main-api-gateway

# 7. Ожидание запуска
sleep 15
```

---

### **ШАГ 3: ТЕСТИРОВАНИЕ**
Проверьте работу системы прямо на сервере:

```bash
# Health check
curl -s http://127.0.0.1:8002/api/health

# Проверка новых эндпоинтов
curl -s http://127.0.0.1:8002/api/protection/scan
curl -s http://127.0.0.1:8002/api/metrics/system
curl -s http://127.0.0.1:8002/api/referral/stats
```

---

## 📊 **ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:**
- ✅ **Ошибки 404** должны снизиться с 117 до 50-70.
- ✅ **Новые эндпоинты** (Protection, Metrics, Darkweb) должны возвращать статус `success`.
- ✅ **Приложение** должно начать корректно отображать данные.

---

## 🚨 **ДЕЙСТВИЯ ПРИ СБОЯХ:**

**ЕСЛИ СЕРВЕР НЕ ЗАПУСКАЕТСЯ:**
1. Посмотрите логи: `journalctl -u aladdin-main-api-gateway -n 50`
2. Откатите изменения:
   ```bash
   cp api_gateway.backup.* api_gateway.py
   systemctl restart aladdin-main-api-gateway
   ```

**ЕСЛИ ПАРОЛЬ НЕ ПОДХОДИТ:**
Убедитесь, что вводите `Sergio675` (с большой буквы S).

---

**ДАТА СОЗДАНИЯ ИНСТРУКЦИИ:** 25 февраля 2026 г.
**СТАТУС:** ГОТОВА К ИСПОЛНЕНИЮ

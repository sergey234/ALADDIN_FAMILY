# 🚀 ИНСТРУКЦИЯ ПО ЗАПУСКУ ДИАГНОСТИКИ ВСЕХ 331 ENDPOINT'А

**Дата:** 2026-02-11  
**Цель:** Пошаговая инструкция для запуска полной диагностики всех endpoint'ов

---

## ✅ ПОДГОТОВКА

### **1. Проверка инструментов**

Убедитесь, что установлены:
- `curl` - для HTTP запросов
- `jq` - для работы с JSON
- `sshpass` - для SSH подключения без пароля
- `bash` - версия 4.0+

**Проверка:**
```bash
curl --version
jq --version
sshpass -V
bash --version
```

**Установка (если нужно):**
```bash
# macOS
brew install jq sshpass

# Linux
sudo apt-get install jq sshpass curl
```

---

### **2. Настройка доступа к серверу**

**Параметры сервера:**
- IP: `149.154.65.180`
- Порт: `8002`
- Пользователь: `root`
- Пароль: `Sergio675`
- Путь: `/opt/aladdin-backend`

**Проверка подключения:**
```bash
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 "echo 'Connection OK'"
```

**Ожидаемый результат:** `Connection OK`

---

### **3. Подготовка файлов**

Убедитесь, что созданы:
- ✅ `diagnose_all_endpoints.sh` - скрипт диагностики
- ✅ `all_331_endpoints_list.json` - список всех endpoint'ов
- ✅ `ENDPOINTS_DIAGNOSIS_PLAN.md` - план диагностики

**Проверка:**
```bash
ls -la diagnose_all_endpoints.sh
ls -la all_331_endpoints_list.json
ls -la ENDPOINTS_DIAGNOSIS_PLAN.md
```

---

## 🚀 ЗАПУСК ДИАГНОСТИКИ

### **Шаг 1: Запуск базовой диагностики**

**Команда:**
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./diagnose_all_endpoints.sh
```

**Что делает скрипт:**
1. Подключается к серверу
2. Проверяет каждый endpoint из списка
3. Создает отчеты в папке `endpoints_diagnosis_YYYYMMDD_HHMMSS/`

**Время выполнения:** 2-3 часа для всех 331 endpoint'а

---

### **Шаг 2: Проверка результатов**

**После завершения скрипта:**

1. **Проверьте созданную папку:**
```bash
ls -la endpoints_diagnosis_*/
```

2. **Откройте сводный отчет:**
```bash
cat endpoints_diagnosis_*/summary_report.md
```

3. **Откройте детальный отчет:**
```bash
cat endpoints_diagnosis_*/detailed_report.md
```

4. **Проверьте JSON отчет:**
```bash
cat endpoints_diagnosis_*/diagnosis_report.json | jq '.'
```

---

## 📊 АНАЛИЗ РЕЗУЛЬТАТОВ

### **Что искать в отчете:**

#### **1. Критичные проблемы:**
- ❌ Endpoint'ы, которые не работают (404)
- ❌ Endpoint'ы, которые не существуют
- ❌ Endpoint'ы без FastAPI декораторов

#### **2. Требующие внимания:**
- ⚠️ Endpoint'ы, требующие авторизацию (401/403)
- ⚠️ Endpoint'ы с ошибками валидации (422)
- ⚠️ Endpoint'ы, не видимые в OpenAPI

#### **3. Работающие:**
- ✅ Endpoint'ы, возвращающие 200/201
- ✅ Endpoint'ы, правильно подключенные
- ✅ Endpoint'ы, видимые в OpenAPI

---

## 🔍 РУЧНАЯ ПРОВЕРКА КРИТИЧНЫХ ENDPOINT'ОВ

### **1. POST /api/family/create**

**Проверка функции:**
```bash
sshpass -p 'Sergio675' ssh root@149.154.65.180 \
  "cd /opt/aladdin-backend && grep -r 'def create_family' security/ app/"
```

**Проверка endpoint'а:**
```bash
sshpass -p 'Sergio675' ssh root@149.154.65.180 \
  "cd /opt/aladdin-backend && grep -r '@router.post.*create' app/routers/"
```

**Проверка HTTP:**
```bash
curl -X POST "http://149.154.65.180:8002/api/family/create" \
  -H "Content-Type: application/json" \
  -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V", "device_type": "iOS"}' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Ожидаемый результат:**
- Функция: ✅ Найдена
- Endpoint: ❌ Не найден
- HTTP: ❌ 404 Not Found

---

### **2. POST /api/auth/login-by-recovery-code**

**Проверка endpoint'а:**
```bash
sshpass -p 'Sergio675' ssh root@149.154.65.180 \
  "cd /opt/aladdin-backend && grep -r 'login-by-recovery-code' app/routers/"
```

**Проверка HTTP:**
```bash
curl -X POST "http://149.154.65.180:8002/api/auth/login-by-recovery-code" \
  -H "Content-Type: application/json" \
  -d '{"family_id": "FAM_TEST", "recovery_code": "TEST"}' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Ожидаемый результат:**
- Endpoint: ❌ Не найден
- HTTP: ❌ 404 Not Found

---

## 📋 СЛЕДУЮЩИЕ ШАГИ

После завершения диагностики:

1. **Создать приоритетный список исправлений:**
   - Критичные endpoint'ы (2 штуки)
   - Важные endpoint'ы (40+ штук)
   - Остальные endpoint'ы (289+ штук)

2. **Начать исправление:**
   - Сначала критичные
   - Потом важные
   - Потом остальные

3. **Повторное тестирование:**
   - После каждого исправления
   - Полное тестирование перед продакшном

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### **Проблема 1: Не удается подключиться к серверу**

**Решение:**
```bash
# Проверьте доступность сервера
ping 149.154.65.180

# Проверьте SSH доступ
ssh root@149.154.65.180

# Проверьте пароль
sshpass -p 'Sergio675' ssh root@149.154.65.180 "echo 'OK'"
```

---

### **Проблема 2: Скрипт работает медленно**

**Решение:**
- Запустите диагностику только для критичных endpoint'ов
- Используйте параллельные запросы (если возможно)
- Разбейте на несколько запусков

---

### **Проблема 3: Некоторые endpoint'ы требуют авторизацию**

**Решение:**
1. Создайте тестовую семью
2. Получите recovery code
3. Авторизуйтесь
4. Используйте токен для запросов

**Пример:**
```bash
# 1. Создать семью (если endpoint работает)
FAMILY_RESPONSE=$(curl -X POST "http://149.154.65.180:8002/api/family/create" \
  -H "Content-Type: application/json" \
  -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V", "device_type": "iOS"}')

# 2. Получить токен (если endpoint работает)
TOKEN=$(curl -X POST "http://149.154.65.180:8002/api/auth/login-by-recovery-code" \
  -H "Content-Type: application/json" \
  -d '{"family_id": "...", "recovery_code": "..."}' \
  | jq -r '.access_token')

# 3. Использовать токен
curl -X GET "http://149.154.65.180:8002/api/family/stats" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 📊 МЕТРИКИ УСПЕХА

### **Диагностика считается успешной, если:**
- ✅ Все 331 endpoint проверен
- ✅ Для каждого endpoint'а есть статус
- ✅ Выявлены все проблемы
- ✅ Создан план исправлений
- ✅ Определены приоритеты

---

**Последнее обновление:** 2026-02-11  
**Статус:** 🚀 **ГОТОВ К ЗАПУСКУ**

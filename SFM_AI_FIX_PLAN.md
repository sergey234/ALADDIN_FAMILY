# 🚨 **КРИТИЧЕСКИЙ ПЛАН ИСПРАВЛЕНИЯ SFM ADAPTER & AI ASSISTANT**

## 📊 **СОСТОЯНИЕ ПРОБЛЕМЫ (АКТУАЛЬНО НА 2026-03-03)**

### **❌ ТЕКУЩИЕ ПРОБЛЕМЫ:**

1. **AI Assistant отвечает всегда одинаково** - "Привет! Я AI помощник ALADDIN..."
2. **SFM Adapter не может подключиться** к `127.0.0.1:8003`
3. **Сервер работает в MOCK режиме** вместо реального AI
4. **SFM HTTP API не запущен** на сервере

### **✅ ЧТО УЖЕ ИСПРАВЛЕНО:**

1. **JSON парсинг** - исправлен timestamp тип (String вместо Date)
2. **Локальная обработка** - добавлены умные fallback ответы
3. **Импорт SFM Adapter** - исправлены пути импорта
4. **Определение контекста** - улучшена логика категоризации сообщений

---

## 🏗️ **АРХИТЕКТУРА СИСТЕМЫ**

### **🔗 Цепочка вызовов AI Assistant:**

```
МОБИЛЬНОЕ ПРИЛОЖЕНИЕ (iOS)
    ↓ HTTP POST /api/ai/assistant/chat
API GATEWAY (порт 8002)
    ↓ FastAPI ai_assistant_router.py
SFM ADAPTER (sfm_adapter.py)
    ↓ HTTP POST http://127.0.0.1:8003/api/execute
SFM HTTP API (порт 8003)
    ↓ SafeFunctionManager (SFM Core)
ИИ ОБРАБОТКА СООБЩЕНИЙ ✅
```

### **🎯 Критическая точка отказа:**
**SFM HTTP API (порт 8003) НЕ ЗАПУЩЕН → Все запросы падают в MOCK**

---

## 🔧 **ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ**

### **ЭТАП 1: ДИАГНОСТИКА СЕРВЕРА** 🚨

#### **1.1 Подключение к серверу**
```bash
# Сервер: 149.154.65.180
# Пользователь: root
# Пароль: Sergio675

ssh root@149.154.65.180
```

#### **1.2 Проверка запущенных процессов**
```bash
# Проверить все Python процессы
ps aux | grep python

# Проверить занятые порты
netstat -tlnp | grep -E ':800[0-9]'

# Проверить SFM процессы
ps aux | grep sfm
```

#### **1.3 Проверка SFM HTTP API**
```bash
# Проверить порт 8003
curl -s http://127.0.0.1:8003/api/health

# Если не отвечает - SFM не запущен!
```

### **ЭТАП 2: ЗАПУСК SFM HTTP API** 🔥

#### **2.1 Переход в директорию проекта**
```bash
cd /opt/aladdin-backend
```

#### **2.2 Проверка наличия файлов**
```bash
# Проверить наличие SFM файлов
ls -la start_sfm_core_http.py
ls -la security/safe_function_manager.py
ls -la sfm_adapter.py
```

#### **2.3 Установка зависимостей**
```bash
# Установить aiohttp если не установлен
pip install aiohttp

# Проверить Python зависимости
python3 -c "import aiohttp; print('✅ aiohttp OK')"
python3 -c "from security.safe_function_manager import SafeFunctionManager; print('✅ SFM OK')"
```

#### **2.4 Запуск SFM HTTP API**
```bash
# Запустить в фоне
python3 start_sfm_core_http.py &

# Проверить что запустился
sleep 3
curl -s http://127.0.0.1:8003/api/health
```

#### **2.5 Тестирование SFM API**
```bash
# Health check
curl http://127.0.0.1:8003/api/health

# Список функций
curl http://127.0.0.1:8003/api/functions

# Тест AI функции
curl -X POST http://127.0.0.1:8003/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "function": "ai_assistant_chat",
    "params": {
      "message": "Привет, как дела?",
      "context": "general"
    }
  }'
```

### **ЭТАП 3: ПЕРЕЗАПУСК API GATEWAY** 🔄

#### **3.1 Проверка статуса API Gateway**
```bash
# Проверить запущен ли API Gateway
systemctl status aladdin-api-gateway

# Или найти процесс
ps aux | grep api_gateway
```

#### **3.2 Перезапуск сервиса**
```bash
# Перезапустить API Gateway
systemctl restart aladdin-api-gateway

# Или если запущен вручную - убить и запустить
pkill -f api_gateway
cd /opt/aladdin-backend
python3 api_gateway_complete_full.py &
```

#### **3.3 Проверка работы API Gateway**
```bash
# Тест health check
curl -s http://127.0.0.1:8002/api/health

# Тест AI endpoint (должен использовать SFM)
curl -X POST http://127.0.0.1:8002/api/ai/assistant/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Расскажи о защите",
    "context": "general"
  }'
```

### **ЭТАП 4: ТЕСТИРОВАНИЕ С МОБИЛЬНОГО ПРИЛОЖЕНИЯ** 📱

#### **4.1 Тестирование API извне**
```bash
# Тест с внешнего IP
curl -X POST http://149.154.65.180:8002/api/ai/assistant/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Какие угрозы ты видишь?",
    "context": "general"
  }'
```

#### **4.2 Проверка в мобильном приложении**
- Открыть AI Assistant в приложении
- Отправить разные сообщения
- Проверить что ответы разные и релевантные

---

## 🔍 **ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ**

### **ПРОБЛЕМА 1: SFM не импортируется**
```bash
# Проверить пути
ls -la /opt/aladdin-backend/security/
python3 -c "import sys; print(sys.path)"

# Исправить пути в start_sfm_core_http.py
backend_path = "/opt/aladdin-backend"
security_path = "/opt/aladdin-backend/security"
```

### **ПРОБЛЕМА 2: Порт 8003 занят**
```bash
# Найти процесс на порту 8003
lsof -i :8003

# Убить процесс
kill -9 PID_NUMBER

# Запустить SFM снова
python3 start_sfm_core_http.py &
```

### **ПРОБЛЕМА 3: SFM возвращает ошибки**
```bash
# Проверить логи SFM
tail -f /opt/aladdin-backend/logs/sfm.log

# Проверить конфигурацию
python3 -c "from security.safe_function_manager import SafeFunctionManager; sfm = SafeFunctionManager(); print(f'Functions: {len(sfm.functions)}')"
```

### **ПРОБЛЕМА 4: API Gateway не видит SFM**
```bash
# Проверить переменную SFM_ADAPTER_AVAILABLE
grep "SFM_ADAPTER_AVAILABLE" /opt/aladdin-backend/api_gateway_complete_full.py

# Перезапустить с логированием
python3 api_gateway_complete_full.py --log-level DEBUG
```

---

## 📋 **ЧЕКЛИСТ ГОТОВНОСТИ К ПРОДАКШЕНУ**

### **✅ ДОЛЖНО БЫТЬ ВЫПОЛНЕНО:**

- [ ] **SFM HTTP API запущен** на порту 8003
- [ ] **API Gateway перезапущен** и видит SFM
- [ ] **AI Assistant отвечает по-разному** на разные вопросы
- [ ] **Контекст определяется корректно**
- [ ] **JWT авторизация работает**
- [ ] **Rate limiting настроен**

### **🧪 ТЕСТОВЫЕ СЦЕНАРИИ:**

1. **Общий вопрос:** "Привет" → Умный ответ
2. **Защита:** "Статус защиты" → Детальная информация
3. **Угрозы:** "Какие угрозы?" → Анализ угроз
4. **Рекомендации:** "Что посоветуешь?" → Персональные советы

---

## 🎯 **КРИТИЧЕСКИЕ ФАЙЛЫ ДЛЯ ПРОВЕРКИ**

### **На сервере `/opt/aladdin-backend/`:**
- `start_sfm_core_http.py` - SFM HTTP API сервер
- `security/safe_function_manager.py` - Ядро SFM
- `api_gateway_complete_full.py` - API Gateway
- `ai_assistant_router.py` - AI роутер

### **На клиенте (уже исправлено):**
- `APIModels.swift` - ChatMessageResponse с timestamp: String?
- `AIAssistantScreen.swift` - Умная обработка контекстов
- `AIAssistantViewModel.swift` - timestampDate computed property

---

## 🚀 **ФИНАЛЬНЫЙ РЕЗУЛЬТАТ**

### **ПОСЛЕ ИСПРАВЛЕНИЯ:**
✅ **AI Assistant работает с настоящим ИИ**  
✅ **Умные ответы на основе контекста**  
✅ **Разные ответы на разные вопросы**  
✅ **Полная интеграция SFM**  
✅ **Продакшен готовность**  

### **ВРЕМЯ НА ИСПРАВЛЕНИЕ:** 30-60 минут
### **КРИТИЧНОСТЬ:** 🚨 **БЛОКИРУЮЩАЯ ДЛЯ ПРОДАКШЕНА**

---

## 📞 **КОНТАКТЫ ДЛЯ ПОМОЩИ**

Если возникнут проблемы:
1. **Проверить логи:** `tail -f /opt/aladdin-backend/logs/*.log`
2. **Тестировать по шагам** из этого плана
3. **Сообщить о конкретной ошибке**

**SFM - сердце AI системы ALADDIN!** 🔥

---

*Создано: 2026-03-03 | Версия: 1.0 | Статус: ГОТОВ К ИСПОЛНЕНИЮ*
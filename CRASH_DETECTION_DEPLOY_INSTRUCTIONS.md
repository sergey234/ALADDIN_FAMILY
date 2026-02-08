# 🚨 CRASH DETECTION DEPLOY - РУЧНЫЕ ИНСТРУКЦИИ

## 📊 ТЕКУЩИЙ СТАТУС
- ✅ **Файлы загружены** на сервер
- ✅ **Синтаксис проверен** (Python OK)
- ✅ **Сервер работает** (порт 8002 активен)
- ❌ **API недоступен** (404 ошибка - роутер не зарегистрирован)

## 🔧 РУЧНЫЕ ШАГИ НА СЕРВЕРЕ

### ШАГ 1: Подключение к серверу
```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

### ШАГ 2: Проверка файлов
```bash
cd /opt/aladdin-backend

# Проверить загруженные файлы
ls -la security/api/routers/crash_detection_router.py
ls -la security/ai_agents/crash_detection_agent.py

# Проверить синтаксис
python3 -m py_compile security/api/routers/crash_detection_router.py
python3 -m py_compile security/ai_agents/crash_detection_agent.py
```

### ШАГ 3: Поиск API Gateway файла
```bash
# Найти основной API файл
find . -name "*api_gateway*" -type f

# Проверить какой файл используется сервером
ps aux | grep uvicorn | grep -v grep
```

### ШАГ 4: Регистрация роутера
```bash
# Отредактировать основной API файл (обычно api_gateway_complete_full.py)
nano api_gateway_complete_full.py

# Найти секцию импортов и добавить:
from security.api.routers.crash_detection_router import router as crash_detection_router

# Найти секцию регистрации роутеров и добавить:
app.include_router(crash_detection_router)

# Сохранить файл (Ctrl+O, Enter, Ctrl+X)
```

### ШАГ 5: Перезапуск сервера
```bash
# Остановить текущий сервер
SERVER_PID=$(ps aux | grep "uvicorn.*api_gateway" | grep -v grep | awk '{print $2}')
kill $SERVER_PID
sleep 3

# Запустить сервер
python3 -m uvicorn api_gateway_complete_full:app --host 0.0.0.0 --port 8002 --reload &
sleep 5

# Проверить запуск
curl -s http://127.0.0.1:8002/api/health
```

### ШАГ 6: Тестирование Crash Detection API
```bash
# Тест 1: Статус
curl -s http://127.0.0.1:8002/api/crash-detection/status | jq '.'

# Тест 2: Настройка
curl -X POST http://127.0.0.1:8002/api/crash-detection/setup \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6173, "radius": 500}' | jq '.'

# Тест 3: Запуск мониторинга
curl -X POST http://127.0.0.1:8002/api/crash-detection/start | jq '.'

# Тест 4: Симуляция аварии
curl -X POST http://127.0.0.1:8002/api/crash-detection/data \
  -H "Content-Type: application/json" \
  -d '{
    "accelerometer": {"x": 35.5, "y": -8.2, "z": 4.1},
    "gyroscope": {"x": 2.1, "y": 1.8, "z": -1.2},
    "speed": 65.5,
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timestamp": 1707234567.123
  }' | jq '.'

# Тест 5: Аварийный алерт
curl -X POST http://127.0.0.1:8002/api/crash-detection/alert \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6173, "severity": "high"}' | jq '.'

# Тест 6: Остановка мониторинга
curl -X POST http://127.0.0.1:8002/api/crash-detection/stop | jq '.'
```

## 📱 ТЕСТИРОВАНИЕ МОБИЛЬНОГО ПРИЛОЖЕНИЯ

После успешного деплоя на сервере:

1. **Запустите мобильное приложение**
2. **Перейдите в Network Protection экран**
3. **Включите Crash Detection**
4. **Нажмите "🚨 ТЕСТ: Симулировать аварию"**
5. **Проверьте появление модального окна**

## 🆘 НЕИСПРАВНОСТИ И РЕШЕНИЯ

### Проблема: "No such file or directory"
```bash
# Проверить правильный путь
find /opt/aladdin-backend -name "*api_gateway*" -type f
ls -la /opt/aladdin-backend/
```

### Проблема: Синтаксическая ошибка
```bash
# Проверить синтаксис
python3 -c "import ast; ast.parse(open('api_gateway_complete_full.py').read())"
python3 -m py_compile api_gateway_complete_full.py
```

### Проблема: Роутер не регистрируется
```bash
# Проверить импорт
python3 -c "from security.api.routers.crash_detection_router import router; print('Import OK')"

# Проверить что роутер добавлен
grep -n "crash_detection_router" api_gateway_complete_full.py
```

### Проблема: Сервер не запускается
```bash
# Проверить логи
tail -f /opt/aladdin-backend/logs/api.log

# Проверить порт
netstat -tlnp | grep 8002

# Проверить процессы
ps aux | grep uvicorn
```

## 🎯 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После выполнения всех шагов:

### ✅ Серверные тесты
```bash
# Все эндпоинты должны возвращать HTTP 200
curl http://149.154.65.180:8002/api/crash-detection/status  # 200 OK
curl -X POST http://149.154.65.180:8002/api/crash-detection/setup -H "Content-Type: application/json" -d '{"latitude": 55.7558, "longitude": 37.6173, "radius": 500}'  # 200 OK
```

### ✅ Мобильные тесты
- Модальное окно аварии появляется
- Обратный отсчет работает
- Кнопки "Отменить" и "Вызвать 112" функционируют
- API запросы отправляются на сервер

### ✅ Логи сервера
```
INFO - REQUEST: POST http://149.154.65.180:8002/api/crash-detection/setup
INFO - RESPONSE: 200 - Time: 0.05s
INFO - 🚨 CRASH ALERT RECEIVED: Severity high at (55.7558, 37.6173)
```

## 📞 ПОДДЕРЖКА

Если возникнут проблемы:
1. **Проверьте логи сервера**: `tail -f /opt/aladdin-backend/logs/api.log`
2. **Проверьте синтаксис**: `python3 -m py_compile api_gateway_complete_full.py`
3. **Проверьте импорт**: `python3 -c "from security.api.routers.crash_detection_router import router"`
4. **Проверьте порт**: `netstat -tlnp | grep 8002`

**🚨 CRASH DETECTION ГОТОВ К АКТИВАЦИИ! Выполните шаги на сервере и экстренная помощь ALADDIN заработает!**
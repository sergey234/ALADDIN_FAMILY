# 📋 РУЧНЫЕ КОМАНДЫ ДЛЯ ЭТАПА 1: РАЗВЕРТЫВАНИЕ SFM HTTP API

## 🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА

### ШАГ 1: КОПИРОВАНИЕ ФАЙЛА НА СЕРВЕР
```bash
# На вашем Маке (локально):
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
scp start_sfm_core_http.py root@149.154.65.180:/opt/aladdin-backend/
```

### ШАГ 2: ПОДКЛЮЧЕНИЕ К СЕРВЕРУ
```bash
# Подключитесь к серверу:
ssh root@149.154.65.180
# Пароль: Sergio675
```

### ШАГ 3: НАСТРОЙКА НА СЕРВЕРЕ
```bash
# Перейдите в директорию проекта:
cd /opt/aladdin-backend

# Сделайте файл исполняемым:
chmod +x start_sfm_core_http.py

# Обновите systemd сервис:
cat > /etc/systemd/system/aladdin-sfm-core.service << 'EOF'
[Unit]
Description=ALADDIN SFM HTTP API Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/aladdin-backend
ExecStart=/opt/aladdin-backend/venvs/main_env/bin/python3 /opt/aladdin-backend/start_sfm_core_http.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=aladdin-sfm-http-api

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузите systemd:
systemctl daemon-reload

# Остановите старый сервис:
systemctl stop aladdin-sfm-core

# Запустите новый сервис:
systemctl start aladdin-sfm-core

# Подождите 5 секунд:
sleep 5
```

### ШАГ 4: ТЕСТИРОВАНИЕ
```bash
# Проверьте статус сервиса:
systemctl status aladdin-sfm-core --no-pager

# Проверьте health check:
curl -s http://127.0.0.1:8003/api/health

# Протестируйте функцию:
curl -s -X POST http://127.0.0.1:8003/api/execute \
  -H "Content-Type: application/json" \
  -d '{"function": "get_phishing_sensitivity", "params": {}}'

# Проверьте список функций:
curl -s http://127.0.0.1:8003/api/functions

# Проверьте логи:
journalctl -u aladdin-sfm-core -n 10
```

### ШАГ 5: ПРОВЕРКА РЕЗУЛЬТАТА

#### ✅ УСПЕШНЫЙ РЕЗУЛЬТАТ:
```json
// Health check:
{
  "status": "healthy",
  "service": "sfm-http-api",
  "functions_count": 1065,
  "timestamp": "2026-02-03T..."
}

// Function call:
{
  "success": true,
  "result": {...},
  "timestamp": "2026-02-03T...",
  "source": "real_sfm",
  "function": "get_phishing_sensitivity"
}

// Service status:
● aladdin-sfm-core.service - ALADDIN SFM HTTP API Service
     Loaded: loaded (/etc/systemd/system/aladdin-sfm-core.service; enabled; preset: enabled)
     Active: active (running) since ...
```

### ШАГ 6: ПОДТВЕРЖДЕНИЕ ГОТОВНОСТИ К ЭТАПУ 2
После успешного выполнения всех команд:
- SFM HTTP API слушает порт 8003
- Возвращает real_sfm данные
- Сервис работает стабильно

**ТОЛЬКО ТОГДА ПЕРЕХОДИМ К ЭТАПУ 2!** 🎯

---

## 📋 ЧТО ДЕЛАТЬ ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК:

### 🔍 ДИАГНОСТИКА ПРОБЛЕМ:

```bash
# Проверить логи сервиса:
journalctl -u aladdin-sfm-core -f

# Проверить что порт слушает:
ss -tlnp | grep :8003

# Проверить что файл существует:
ls -la /opt/aladdin-backend/start_sfm_core_http.py

# Проверить синтаксис Python:
python3 -m py_compile /opt/aladdin-backend/start_sfm_core_http.py

# Запустить вручную для отладки:
/opt/aladdin-backend/venvs/main_env/bin/python3 /opt/aladdin-backend/start_sfm_core_http.py
```

### 🚨 ЧАСТЫЕ ПРОБЛЕМЫ:

1. **"Module not found"** → Проверить пути импорта в файле
2. **"Permission denied"** → Проверить права на файл
3. **"Port already in use"** → Проверить что старый сервис остановлен
4. **"Connection refused"** → Проверить что сервис запущен

### 🔄 ВОССТАНОВЛЕНИЕ:
```bash
# Остановить и перезапустить:
systemctl stop aladdin-sfm-core
systemctl start aladdin-sfm-core

# Или перезагрузить сервер:
reboot
```

---

## 🎯 КРИТЕРИИ ГОТОВНОСТИ К ЭТАПУ 2:

- ✅ HTTP API отвечает на порту 8003
- ✅ Health check возвращает status: "healthy"
- ✅ Function call возвращает source: "real_sfm"
- ✅ Сервис активен (active running)
- ✅ Нет ошибок в логах

**ТОЛЬКО ПОСЛЕ ВЫПОЛНЕНИЯ ЭТИХ КРИТЕРИЕВ ПЕРЕХОДИМ К ЭТАПУ 2!** 🚀
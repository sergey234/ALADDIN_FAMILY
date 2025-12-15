# 🔧 ИСПРАВЛЕНИЕ ОШИБКИ 502

## ❌ ПРОБЛЕМА
После нажатия "Активировать" в приложении появляется ошибка **502 Bad Gateway**.

## 🔍 ПРИЧИНА
Ошибка 502 означает, что **Nginx не может подключиться к payment_service** на порту 8000. Это происходит потому, что:
1. Payment_service не запущен
2. Payment_service запущен, но не отвечает
3. Payment_service запущен, но есть ошибки в коде

## ✅ РЕШЕНИЕ

### Шаг 1: Проверить статус payment_service
```bash
ssh root@149.154.65.180 "ps aux | grep uvicorn"
```

### Шаг 2: Запустить payment_service
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 &"
```

### Шаг 3: Проверить, что сервис работает
```bash
ssh root@149.154.65.180 "curl http://localhost:8000/"
```

Должен вернуть: `{"service": "Aladdin Payment Service", ...}`

### Шаг 4: Проверить endpoint активации
```bash
curl -X POST 'https://aladdin-ai.ru/api/subscription/activation/verify' \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: PUBLIC_CLIENT_KEY' \
  -d '{"code": "ALDN-D6W9-IUXN-QGJZ", "familyId": "test", "deviceId": "test"}'
```

## 🔄 АВТОМАТИЧЕСКИЙ ЗАПУСК

Чтобы payment_service запускался автоматически при перезагрузке сервера, создайте systemd service:

```bash
# Создать файл /etc/systemd/system/payment_service.service
cat > /etc/systemd/system/payment_service.service << 'EOF'
[Unit]
Description=Aladdin Payment Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aladdin-backend
Environment="PATH=/opt/aladdin-backend/venv/bin"
ExecStart=/opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Включить и запустить
systemctl daemon-reload
systemctl enable payment_service
systemctl start payment_service
```

## 📋 ПРОВЕРКА

После запуска payment_service:
1. ✅ Проверьте статус: `systemctl status payment_service`
2. ✅ Проверьте логи: `tail -f /tmp/payment_service.log`
3. ✅ Протестируйте endpoint: `curl http://localhost:8000/`
4. ✅ Попробуйте активировать код в приложении

## ⚠️ ЕСЛИ ВСЕ ЕЩЕ НЕ РАБОТАЕТ

1. Проверьте логи payment_service:
   ```bash
   ssh root@149.154.65.180 "tail -50 /tmp/payment_service.log"
   ```

2. Проверьте, что порт 8000 слушает:
   ```bash
   ssh root@149.154.65.180 "netstat -tlnp | grep 8000"
   ```

3. Проверьте конфигурацию Nginx:
   ```bash
   ssh root@149.154.65.180 "grep -A 5 'location /api' /etc/nginx/sites-enabled/aladdin-ai.ru"
   ```



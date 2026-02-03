#!/bin/bash
# РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА

echo "🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА"

# 1. Копируем HTTP API файл на сервер
echo "1️⃣ ЗАГРУЗКА HTTP API ФАЙЛА:"
scp start_sfm_core_http.py root@149.154.65.180:/opt/aladdin-backend/
ssh root@149.154.65.180 "chmod +x /opt/aladdin-backend/start_sfm_core_http.py"
echo "✅ HTTP API файл загружен"

# 2. Обновляем systemd сервис
echo ""
echo "2️⃣ ОБНОВЛЕНИЕ SYSTEMD СЕРВИСА:"
ssh root@149.154.65.180 "cat > /etc/systemd/system/aladdin-sfm-core.service << 'EOF'
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
EOF"

ssh root@149.154.65.180 "systemctl daemon-reload"
echo "✅ Systemd сервис обновлен"

# 3. Запускаем сервис
echo ""
echo "3️⃣ ЗАПУСК SFM HTTP API СЕРВИСА:"
ssh root@149.154.65.180 "systemctl stop aladdin-sfm-core"
ssh root@149.154.65.180 "systemctl start aladdin-sfm-core"
echo "⏳ Ожидание запуска..."
sleep 3

# 4. Тестируем
echo ""
echo "4️⃣ ТЕСТИРОВАНИЕ HTTP API:"
HEALTH=$(ssh root@149.154.65.180 "curl -s http://127.0.0.1:8003/api/health")
echo "Health check: $HEALTH"

echo ""
echo "Function test:"
ssh root@149.154.65.180 "curl -s -X POST http://127.0.0.1:8003/api/execute -H 'Content-Type: application/json' -d '{\"function\": \"get_phishing_sensitivity\", \"params\": {}}'"

echo ""
echo "Service status:"
ssh root@149.154.65.180 "systemctl status aladdin-sfm-core --no-pager | head -3"

echo ""
echo "🎯 ЭТАП 1 ЗАВЕРШЕН!"
echo "✅ SFM HTTP API сервис запущен на порту 8003"
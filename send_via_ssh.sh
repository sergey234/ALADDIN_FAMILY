#!/bin/bash
echo "📤 Отправляю файл через SSH + base64..."

# Кодируем файл в base64 и отправляем
cat api_gateway_complete_full.py | base64 | sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 "
cd /opt/aladdin-backend
echo 'Распаковываю файл...'
cat | base64 -d > api_gateway_complete_full_new.py
echo '✅ Файл получен!'

# Создаем backup
cp api_gateway_complete_full.py api_gateway_complete_full.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo 'Backup создан'

# Заменяем файл
mv api_gateway_complete_full_new.py api_gateway_complete_full.py
chmod +x api_gateway_complete_full.py
echo '✅ Файл обновлен!'

# Перезапускаем сервис
systemctl restart aladdin-main-api-gateway 2>/dev/npi/health && echo '✅ API работает!' || echo '❌ API не отвечает'
"

echo "🎉 ГОТОВО! Проверьте работу API на сервере."

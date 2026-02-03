#!/bin/bash
# 🚀 ЗАПУСК ПРОВЕРКИ ФУНКЦИЙ НА СЕРВЕРЕ
# Выполняет полную диагностику исправленных функций 1-4/93

echo "🚀 ЗАПУСК ПРОВЕРКИ ФУНКЦИЙ 1-4/93 НА СЕРВЕРЕ"
echo "=" * 60

# Загружаем скрипт проверки на сервер
echo "📤 Загрузка скрипта проверки на сервер..."
sshpass -p 'Sergio675' scp -o StrictHostKeyChecking=no check_server_functions_1_4.sh root@149.154.65.180:/tmp/

# Делаем исполняемым и запускаем
echo "▶️  Запуск проверки на сервере..."
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 "chmod +x /tmp/check_server_functions_1_4.sh && /tmp/check_server_functions_1_4.sh"

echo ""
echo "🎉 ПРОВЕРКА ЗАВЕРШЕНА!"
echo "Если все ✅ - функции работают правильно на сервере"
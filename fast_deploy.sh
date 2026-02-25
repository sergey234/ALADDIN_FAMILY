#!/bin/bash
echo "🚀 Быстрая отправка API Gateway на сервер..."

# Сжимаем файл
echo "📦 Сжимаю файл..."
gzip -f api_gateway_complete_full.py

# Отправляем с оптимизированными параметрами
echo "📤 Отправляю на сервер..."
scp -o Compression=yes -o Cipher=aes128-ctr -q api_gateway_complete_full.py.gz root@149.154.65.180:/opt/aladdin-backend/

if [ $? -eq 0 ]; then
    echo "✅ Файл отправлен успешно!"
    
    # Распаковываем на сервере
    echo "📦 Распаковываю на сервере..."
    ssh root@149.154.65.180 "cd /opt/aladdin-backend && gunzip -f api_gateway_complete_full.py.gz && chmod +x api_gateway_complete_full.py"
    
    if [ $? -eq 0 ]; then
     пускается вручную'"
        echo "🎉 ГОТОВО!"
    else
        echo "❌ Ошибка распаковки на сервере"
    fi
else
    echo "❌ Ошибка отправки файла"
fi

# Очищаем локальный сжатый файл
rm -f api_gateway_complete_full.py.gz

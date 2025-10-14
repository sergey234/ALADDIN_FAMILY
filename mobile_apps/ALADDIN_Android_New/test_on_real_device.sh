#!/bin/bash

echo "📱 ТЕСТИРОВАНИЕ НА РЕАЛЬНОМ УСТРОЙСТВЕ"
echo "====================================="

# Переходим в папку проекта
cd "/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"

echo "📁 Текущая директория: $(pwd)"

# Настраиваем Java и Android
source setup_java_env.sh

echo ""
echo "📱 Проверка подключенных устройств..."
adb devices

echo ""
echo "📋 ИНСТРУКЦИИ ДЛЯ ПОДКЛЮЧЕНИЯ УСТРОЙСТВА:"
echo "1. Включите режим разработчика на Android:"
echo "   Настройки → О телефоне → Номер сборки (нажать 7 раз)"
echo ""
echo "2. Включите USB отладку:"
echo "   Настройки → Для разработчиков → USB отладка"
echo ""
echo "3. Подключите устройство через USB"
echo ""
echo "4. Разрешите отладку на устройстве (появится запрос)"

echo ""
read -p "Нажмите Enter когда устройство подключено..."

echo ""
echo "📱 Проверка подключенных устройств..."
if adb devices | grep -q "device$"; then
    echo "✅ Устройство подключено!"
    
    echo ""
    echo "🔨 Создание debug APK для тестирования..."
    ./gradlew assembleDebug
    
    if [ $? -eq 0 ]; then
        echo "✅ Debug APK создан!"
        
        APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
        
        echo ""
        echo "📥 Установка APK на устройство..."
        adb install -r "$APK_PATH"
        
        if [ $? -eq 0 ]; then
            echo "✅ APK установлен на устройство!"
            
            echo ""
            echo "🚀 Запуск приложения..."
            adb shell am start -n family.aladdin.android/.MainActivity
            
            echo ""
            echo "🎉 ПРИЛОЖЕНИЕ ЗАПУЩЕНО НА УСТРОЙСТВЕ!"
            echo ""
            echo "📱 Теперь можете:"
            echo "• Тестировать все функции"
            echo "• Проверять UI на реальном экране"
            echo "• Тестировать производительность"
            echo "• Проверять работу всех 326 функций"
            echo ""
            echo "🔧 Для внесения изменений:"
            echo "1. Внесите правки в Android Studio"
            echo "2. Запустите этот скрипт снова"
            echo "3. Или используйте: ./quick_install.sh"
            
        else
            echo "❌ Ошибка установки APK"
        fi
    else
        echo "❌ Ошибка создания APK"
    fi
else
    echo "❌ Устройство не подключено"
    echo ""
    echo "💡 Убедитесь что:"
    echo "• USB отладка включена"
    echo "• Устройство подключено через USB"
    echo "• Разрешен доступ для отладки"
    echo ""
    echo "🔄 Попробуйте еще раз:"
    echo "   adb devices"
fi

echo ""
echo "📱 Готово! Теперь можете тестировать приложение на реальном устройстве!"


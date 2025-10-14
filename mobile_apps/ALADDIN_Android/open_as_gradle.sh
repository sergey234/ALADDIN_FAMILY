#!/bin/bash

echo "🔧 ОТКРЫВАЕМ ПРОЕКТ КАК GRADLE ПРОЕКТ"
echo "====================================="

# Закрываем Android Studio
echo "🔄 Закрываем Android Studio..."
pkill -f "Android Studio"

# Ждем 3 секунды
sleep 3

# Открываем проект через командную строку как Gradle проект
echo "🚀 Открываем проект как Gradle проект..."
open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android

echo "✅ ПРОЕЕКТ ОТКРЫТ КАК GRADLE ПРОЕКТ!"
echo "📱 В Android Studio:"
echo "   1. Дождитесь завершения 'Gradle sync'"
echo "   2. Если появится диалог 'Import Gradle Project' - нажмите 'OK'"
echo "   3. 'Project Structure' должен стать активным"
echo "   4. Перейдите в Run → Edit Configurations"
echo "   5. В поле Module должно появиться: ALADDIN.app"


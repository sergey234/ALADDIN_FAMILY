#!/bin/bash

echo "🔐 СОЗДАНИЕ КЛЮЧА ПОДПИСИ ДЛЯ ПУБЛИКАЦИИ"
echo "======================================="

# Переходим в папку проекта
cd "/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"

echo "📁 Текущая директория: $(pwd)"

# Проверяем наличие Java
if ! command -v keytool &> /dev/null; then
    echo "❌ keytool не найден. Настраиваем Java..."
    export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
    export PATH="$JAVA_HOME/bin:$PATH"
fi

echo "✅ Java настроена: $(java -version 2>&1 | head -1)"

# Создаем keystore
KEYSTORE_NAME="aladdin-release-key.keystore"
ALIAS_NAME="aladdin"

echo ""
echo "🔑 Создание keystore для подписи APK..."
echo "Введите данные для сертификата:"

# Создаем keystore с автоматическими данными
keytool -genkey -v \
    -keystore "$KEYSTORE_NAME" \
    -alias "$ALIAS_NAME" \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass "aladdin2024!" \
    -keypass "aladdin2024!" \
    -dname "CN=ALADDIN Family Security, OU=Development, O=ALADDIN, L=Moscow, S=Moscow, C=RU"

if [ $? -eq 0 ]; then
    echo "✅ Keystore создан успешно!"
    echo ""
    echo "📋 ИНФОРМАЦИЯ О КЛЮЧЕ:"
    echo "   Keystore: $KEYSTORE_NAME"
    echo "   Alias: $ALIAS_NAME"
    echo "   Password: aladdin2024!"
    echo "   Срок действия: 10000 дней (~27 лет)"
    echo ""
    echo "⚠️  ВАЖНО: Сохраните пароль в безопасном месте!"
    echo "   Без него вы не сможете обновлять приложение!"
    echo ""
    
    # Создаем файл с информацией о ключе
    cat > keystore_info.txt << EOF
# 🔐 ИНФОРМАЦИЯ О КЛЮЧЕ ПОДПИСИ ALADDIN

## Основная информация:
- Keystore файл: $KEYSTORE_NAME
- Alias: $ALIAS_NAME
- Пароль: aladdin2024!
- Алгоритм: RSA 2048
- Срок действия: 10000 дней

## Для Android Studio:
1. Build → Generate Signed Bundle/APK
2. Choose existing keystore
3. Путь: $(pwd)/$KEYSTORE_NAME
4. Alias: $ALIAS_NAME
5. Пароли: aladdin2024!

## Безопасность:
⚠️  НЕ ТЕРЯЙТЕ ЭТОТ ФАЙЛ И ПАРОЛЬ!
⚠️  Без них невозможно обновлять приложение в Google Play!

Создано: $(date)
EOF
    
    echo "📄 Информация сохранена в: keystore_info.txt"
    
    # Показываем содержимое keystore
    echo ""
    echo "🔍 Проверка keystore:"
    keytool -list -v -keystore "$KEYSTORE_NAME" -storepass "aladdin2024!"
    
else
    echo "❌ Ошибка создания keystore"
    exit 1
fi

echo ""
echo "🎉 ГОТОВО! Теперь можно создавать release APK!"
echo ""
echo "📱 Следующие шаги:"
echo "1. Откройте Android Studio"
echo "2. Build → Generate Signed Bundle/APK"
echo "3. Выберите созданный keystore"
echo "4. Создайте AAB файл для Google Play"

#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ ВСЕХ ОШИБОК С HINT АРГУМЕНТАМИ"

# Найти все файлы с ошибками hint
echo "📁 Поиск файлов с ошибками..."

# Исправить все файлы с .accessibilityLabel(label:, hint:)
find . -name "*.swift" -exec grep -l "\.accessibilityLabel(" {} \; | while read file; do
    echo "🔧 Исправляю: $file"
    
    # Заменить .accessibilityLabel(label: X, hint: Y) на .accessibilityLabel(X) и .accessibilityHint(Y)
    sed -i '' 's/\.accessibilityLabel([[:space:]]*label:[[:space:]]*\([^,]*\),[[:space:]]*hint:[[:space:]]*\([^)]*\))/\.accessibilityLabel(\1)\
        \.accessibilityHint(\2)/g' "$file"
done

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "🧪 Проверяю результат..."

# Проверить результат
xcodebuild build -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 12' 2>&1 | grep "extra argument 'hint'" | wc -l




#!/bin/bash

echo "🔧 Обновляю все GitHub Actions workflow файлы..."

# Обновляем actions/upload-artifact@v3 на v4
find .github/workflows/ -name "*.yml" -o -name "*.yaml" | xargs sed -i '' 's/actions\/upload-artifact@v3/actions\/upload-artifact@v4/g'

# Обновляем actions/cache@v3 на v4
find .github/workflows/ -name "*.yml" -o -name "*.yaml" | xargs sed -i '' 's/actions\/cache@v3/actions\/cache@v4/g'

# Обновляем actions/checkout@v3 на v4
find .github/workflows/ -name "*.yml" -o -name "*.yaml" | xargs sed -i '' 's/actions\/checkout@v3/actions\/checkout@v4/g'

# Обновляем actions/setup-python@v4 на v5
find .github/workflows/ -name "*.yml" -o -name "*.yaml" | xargs sed -i '' 's/actions\/setup-python@v4/actions\/setup-python@v5/g'

echo "✅ Все workflow файлы обновлены!"
echo "📋 Проверяю результат..."

# Показываем что изменилось
echo "🔍 Найденные устаревшие действия:"
grep -r "actions/upload-artifact@v3\|actions/cache@v3\|actions/checkout@v3" .github/workflows/ || echo "✅ Все действия обновлены!"

echo "🎉 Готово! Теперь можно коммитить и пушить."

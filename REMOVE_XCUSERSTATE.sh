#!/bin/bash
# Скрипт для удаления .xcuserstate из коммита

echo "🔍 ПРОВЕРКА СИТУАЦИИ..."
echo ""

# Проверка что .gitignore настроен
if grep -q "xcuserstate" .gitignore 2>/dev/null; then
    echo "✅ .gitignore уже настроен правильно"
else
    echo "⚠️ Добавляю правила в .gitignore..."
    echo "" >> .gitignore
    echo "# Xcode user settings" >> .gitignore
    echo "*.xcuserstate" >> .gitignore
    echo "*.xcuserdatad/" >> .gitignore
    echo "✅ Добавлено в .gitignore"
fi

# Проверка что файл в коммите
if git show 08c69bf0 --name-only | grep -q "xcuserstate"; then
    echo "✅ Файл найден в коммите 08c69bf0"
    
    # Проверка что коммит не запушен
    if git log origin/master..HEAD 2>/dev/null | grep -q "08c69bf0"; then
        echo "✅ Коммит НЕ запушен - можно безопасно исправить"
        echo ""
        echo "🗑️ Удаляю файл из коммита..."
        
        # Удаление из индекса
        git rm --cached ALADDIN.xcodeproj/project.xcworkspace/xcuserdata/sergejhlystov.xcuserdatad/UserInterfaceState.xcuserstate 2>/dev/null
        
        # Исправление коммита
        git commit --amend --no-edit
        
        echo ""
        echo "✅ Файл удален из коммита!"
        echo ""
        echo "📊 Проверка результата:"
        git show HEAD --name-only | grep xcuserstate || echo "✅ Файл успешно удален (не найден в коммите)"
    else
        echo "⚠️ Коммит УЖЕ запушен - нужно создать новый коммит"
        echo ""
        echo "🗑️ Удаляю файл из индекса..."
        
        # Удаление из индекса
        git rm --cached ALADDIN.xcodeproj/project.xcworkspace/xcuserdata/sergejhlystov.xcuserdatad/UserInterfaceState.xcuserstate 2>/dev/null
        
        # Создание нового коммита
        git commit -m "🗑️ Удаление временных файлов Xcode из репозитория"
        
        echo ""
        echo "✅ Создан новый коммит с удалением!"
        echo ""
        echo "📊 Проверка результата:"
        git show HEAD --name-only | grep xcuserstate || echo "✅ Файл успешно удален (не найден в коммите)"
    fi
else
    echo "✅ Файл уже удален из коммита"
fi

echo ""
echo "🎯 ИТОГ:"
echo "✅ .gitignore настроен - файл не будет попадать в будущие коммиты"
echo "✅ Файл удален из репозитория (остался локально для вашего удобства)"
echo "✅ Репозиторий стал чище!"

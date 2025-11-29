#!/bin/bash
# 🔍 Скрипт проверки конфликтов файлов для iOS проекта
# Использование: ./check_file_conflicts.sh <SCREEN_NAME>

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    print_status $RED "❌ Ошибка: Не указано имя экрана"
    echo "Использование: $0 <SCREEN_NAME>"
    echo "Пример: $0 VPNScreen"
    exit 1
fi

SCREEN_NAME=$1
PROJECT_FILE="ALADDIN.xcodeproj/project.pbxproj"

print_status $BLUE "🔍 Проверка конфликтов для ${SCREEN_NAME}..."

# Проверка 1: Существование project.pbxproj
if [ ! -f "$PROJECT_FILE" ]; then
    print_status $RED "❌ Ошибка: Файл $PROJECT_FILE не найден"
    exit 1
fi

# Проверка 2: Существующие файлы
print_status $YELLOW "📁 Проверка существующих файлов..."
existing_files=$(find . -name "*${SCREEN_NAME}*" -type f 2>/dev/null || true)
if [ -n "$existing_files" ]; then
    print_status $YELLOW "Найдены файлы:"
    echo "$existing_files"
else
    print_status $GREEN "✅ Файлы с именем ${SCREEN_NAME} не найдены"
fi

# Проверка 3: Конфликты в project.pbxproj
print_status $YELLOW "📋 Проверка конфликтов в project.pbxproj..."
conflicts=$(grep -n "${SCREEN_NAME}" "$PROJECT_FILE" 2>/dev/null || true)
if [ -n "$conflicts" ]; then
    print_status $YELLOW "Найдены упоминания в project.pbxproj:"
    echo "$conflicts"
else
    print_status $GREEN "✅ Упоминания ${SCREEN_NAME} в project.pbxproj не найдены"
fi

# Проверка 4: Дублирование
print_status $YELLOW "🔄 Проверка дублирования..."
count=$(grep -c "${SCREEN_NAME}" "$PROJECT_FILE" 2>/dev/null || echo "0")
count=$(echo "$count" | tr -d '\n' | tr -d ' ')
if [ "$count" -gt 2 ]; then
    print_status $RED "⚠️  Обнаружено дублирование: $count упоминаний"
    print_status $YELLOW "Рекомендация: Проверить и удалить дублирующие записи"
elif [ "$count" -eq 2 ]; then
    print_status $GREEN "✅ Нормальное количество упоминаний: $count (PBXFileReference + PBXBuildFile)"
else
    print_status $YELLOW "ℹ️  Количество упоминаний: $count"
fi

# Проверка 5: Пути
print_status $YELLOW "🛤️  Проверка путей..."
paths=$(grep -o "path = \"[^\"]*${SCREEN_NAME}[^\"]*\"" "$PROJECT_FILE" 2>/dev/null || true)
if [ -n "$paths" ]; then
    print_status $YELLOW "Найденные пути:"
    echo "$paths"
    
    # Проверка на дублирование путей
    if echo "$paths" | grep -q "Screens/Screens/"; then
        print_status $RED "❌ Обнаружено дублирование путей (Screens/Screens/)"
        print_status $YELLOW "Рекомендация: Исправить пути в project.pbxproj"
    else
        print_status $GREEN "✅ Пути корректны"
    fi
else
    print_status $GREEN "✅ Пути не найдены (файл не добавлен в проект)"
fi

# Проверка 6: ID файла
print_status $YELLOW "🆔 Проверка уникальности ID..."
file_ids=$(grep -o "A[0-9A-F]\{10\}.*${SCREEN_NAME}" "$PROJECT_FILE" 2>/dev/null || true)
if [ -n "$file_ids" ]; then
    print_status $YELLOW "Найденные ID:"
    echo "$file_ids"
    
    # Проверка уникальности ID
    duplicate_ids=$(grep -o "A[0-9A-F]\{10\}" "$PROJECT_FILE" | sort | uniq -d 2>/dev/null || true)
    if [ -n "$duplicate_ids" ]; then
        print_status $RED "❌ Обнаружены дублирующие ID:"
        echo "$duplicate_ids"
    else
        print_status $GREEN "✅ ID уникальны"
    fi
else
    print_status $GREEN "✅ ID не найдены (файл не добавлен в проект)"
fi

# Проверка 7: Компиляция (если файл добавлен)
if [ "$count" -ge 2 ]; then
    print_status $YELLOW "🔨 Проверка компиляции..."
    if command -v xcodebuild >/dev/null 2>&1; then
        build_output=$(xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build 2>&1 || true)
        if echo "$build_output" | grep -q "error.*${SCREEN_NAME}"; then
            print_status $RED "❌ Ошибки компиляции для ${SCREEN_NAME}:"
            echo "$build_output" | grep -i "error.*${SCREEN_NAME}"
        else
            print_status $GREEN "✅ Компиляция прошла успешно"
        fi
    else
        print_status $YELLOW "⚠️  xcodebuild не найден, пропуск проверки компиляции"
    fi
fi

# Итоговый отчет
print_status $BLUE "📊 ИТОГОВЫЙ ОТЧЕТ:"
echo "=================="

if [ "$count" -eq 0 ]; then
    print_status $GREEN "✅ Файл ${SCREEN_NAME} готов к добавлению в проект"
    print_status $YELLOW "💡 Следующие шаги:"
    echo "   1. Добавить файл в PBXFileReference"
    echo "   2. Добавить файл в PBXBuildFile"
    echo "   3. Добавить файл в соответствующую группу"
    echo "   4. Добавить файл в PBXSourcesBuildPhase"
elif [ "$count" -eq 2 ]; then
    print_status $GREEN "✅ Файл ${SCREEN_NAME} корректно добавлен в проект"
elif [ "$count" -gt 2 ]; then
    print_status $RED "❌ Обнаружены проблемы с файлом ${SCREEN_NAME}"
    print_status $YELLOW "💡 Рекомендации:"
    echo "   1. Проверить дублирующие записи в project.pbxproj"
    echo "   2. Удалить лишние упоминания"
    echo "   3. Пересобрать проект"
fi

print_status $BLUE "🏁 Проверка завершена"

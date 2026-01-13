#!/bin/bash

# Скрипт для проверки хардкода в Swift файлах
# Ищет строки, которые могут быть хардкодом вместо локализации

echo "🔍 ПРОВЕРКА ХАРДКОДА В SWIFT ФАЙЛАХ"
echo "===================================="

# Цвета для вывода
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Паттерны для поиска хардкода
PATTERNS=(
    'Text\(".*[А-Яа-яЁё].*"\)'  # Текст с русскими буквами
    'title:.*"[А-Яа-яЁё]'        # Заголовки с русскими буквами
    'subtitle:.*"[А-Яа-яЁё]'    # Подзаголовки с русскими буквами
    '\.localized\(".*[A-Za-z].*"\)'  # Возможные ошибки в ключах
)

# Исключения (файлы, которые не проверяем)
EXCLUDE=(
    "Localizable.strings"
    "*.backup*"
    "*.bak"
    "*_BACKUP*"
    "*_Old*"
    "check_hardcode.sh"
)

# Счетчики
TOTAL_FILES=0
FILES_WITH_ISSUES=0
TOTAL_ISSUES=0

# Функция для проверки файла
check_file() {
    local file=$1
    local has_issues=false
    local issues=0
    
    for pattern in "${PATTERNS[@]}"; do
        # Игнорируем строки с комментариями и локализацией
        local matches=$(grep -nE "$pattern" "$file" 2>/dev/null | \
            grep -v "//.*localized" | \
            grep -v "localizationManager.localized" | \
            grep -v "\.localized\(" | \
            grep -v "accessibilityLabel" | \
            grep -v "accessibilityHint" | \
            grep -v "accessibilityValue" | \
            wc -l | tr -d ' ')
        
        if [ "$matches" -gt 0 ]; then
            if [ "$has_issues" = false ]; then
                echo -e "\n${YELLOW}⚠️  $file${NC}"
                has_issues=true
                ((FILES_WITH_ISSUES++))
            fi
            
            echo -e "  ${RED}Найдено $matches совпадений для паттерна: $pattern${NC}"
            grep -nE "$pattern" "$file" 2>/dev/null | \
                grep -v "//.*localized" | \
                grep -v "localizationManager.localized" | \
                grep -v "\.localized\(" | \
                grep -v "accessibilityLabel" | \
                grep -v "accessibilityHint" | \
                grep -v "accessibilityValue" | \
                head -5 | \
                sed 's/^/    /'
            
            ((TOTAL_ISSUES+=matches))
            ((issues+=matches))
        fi
    done
    
    if [ "$has_issues" = false ]; then
        echo -e "${GREEN}✅ $file${NC}"
    fi
}

# Поиск всех Swift файлов
echo "📁 Поиск Swift файлов..."
find . -name "*.swift" -type f | while read -r file; do
    # Проверяем, не в исключениях ли файл
    skip=false
    for exclude in "${EXCLUDE[@]}"; do
        if [[ "$file" == *"$exclude"* ]]; then
            skip=true
            break
        fi
    done
    
    if [ "$skip" = false ]; then
        ((TOTAL_FILES++))
        check_file "$file"
    fi
done

# Итоговая статистика
echo ""
echo "===================================="
echo "📊 ИТОГОВАЯ СТАТИСТИКА:"
echo "  Всего файлов проверено: $TOTAL_FILES"
echo "  Файлов с проблемами: $FILES_WITH_ISSUES"
echo "  Всего проблем: $TOTAL_ISSUES"
echo ""

if [ "$TOTAL_ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✅ Хардкод не найден! Все строки локализованы.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Найдено $TOTAL_ISSUES потенциальных проблем с хардкодом.${NC}"
    echo -e "${YELLOW}   Проверьте файлы выше и замените хардкод на LocalizationManager.shared.localized()${NC}"
    exit 1
fi


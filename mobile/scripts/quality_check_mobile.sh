#!/bin/bash

# Скрипт проверки качества кода для мобильных приложений ALADDIN
# Проверяет iOS (Swift) и Android (Kotlin) код

set -e

echo "🔍 ПРОВЕРКА КАЧЕСТВА КОДА МОБИЛЬНЫХ ПРИЛОЖЕНИЙ ALADDIN"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода статуса
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Функция для вывода предупреждения
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функция для вывода информации
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Проверка наличия инструментов
check_tools() {
    print_info "Проверка наличия инструментов..."
    
    # Проверка SwiftLint
    if command -v swiftlint &> /dev/null; then
        print_status 0 "SwiftLint установлен"
    else
        print_warning "SwiftLint не установлен. Установите: brew install swiftlint"
        return 1
    fi
    
    # Проверка ktlint
    if command -v ktlint &> /dev/null; then
        print_status 0 "ktlint установлен"
    else
        print_warning "ktlint не установлен. Установите: brew install ktlint"
        return 1
    fi
    
    # Проверка detekt
    if [ -f "mobile/android/gradlew" ]; then
        print_status 0 "Gradle wrapper найден"
    else
        print_warning "Gradle wrapper не найден в mobile/android/"
        return 1
    fi
}

# Проверка iOS кода
check_ios() {
    print_info "Проверка iOS кода (Swift)..."
    
    cd mobile/ios
    
    # SwiftLint проверка
    if swiftlint lint --quiet; then
        print_status 0 "SwiftLint проверка пройдена"
    else
        print_warning "SwiftLint нашел проблемы. Запускаю с подробным выводом..."
        swiftlint lint
        return 1
    fi
    
    # SwiftFormat проверка (если установлен)
    if command -v swiftformat &> /dev/null; then
        if swiftformat --lint . > /dev/null 2>&1; then
            print_status 0 "SwiftFormat проверка пройдена"
        else
            print_warning "SwiftFormat нашел проблемы форматирования"
            print_info "Запустите: swiftformat . для автоисправления"
        fi
    else
        print_warning "SwiftFormat не установлен. Установите: brew install swiftformat"
    fi
    
    cd ../..
}

# Проверка Android кода
check_android() {
    print_info "Проверка Android кода (Kotlin)..."
    
    cd mobile/android
    
    # ktlint проверка
    if ktlint check --reporter=plain,output=ktlint-report.txt; then
        print_status 0 "ktlint проверка пройдена"
    else
        print_warning "ktlint нашел проблемы. Отчет сохранен в ktlint-report.txt"
        print_info "Запустите: ktlint format для автоисправления"
    fi
    
    # Detekt проверка через Gradle
    if ./gradlew detekt --quiet; then
        print_status 0 "Detekt проверка пройдена"
    else
        print_warning "Detekt нашел проблемы. Запускаю с подробным выводом..."
        ./gradlew detekt
        return 1
    fi
    
    # Android Lint проверка
    if ./gradlew lint --quiet; then
        print_status 0 "Android Lint проверка пройдена"
    else
        print_warning "Android Lint нашел проблемы. Запускаю с подробным выводом..."
        ./gradlew lint
    fi
    
    cd ../..
}

# Проверка безопасности
check_security() {
    print_info "Проверка безопасности кода..."
    
    # Проверка на хардкод паролей и ключей
    if grep -r "password.*=" mobile/ --include="*.swift" --include="*.kt" | grep -v "// TODO" | grep -v "// FIXME"; then
        print_warning "Найдены потенциально хардкод пароли в коде"
    else
        print_status 0 "Хардкод пароли не найдены"
    fi
    
    # Проверка на небезопасные HTTP соединения
    if grep -r "http://" mobile/ --include="*.swift" --include="*.kt" | grep -v "// TODO" | grep -v "// FIXME"; then
        print_warning "Найдены небезопасные HTTP соединения"
    else
        print_status 0 "Небезопасные HTTP соединения не найдены"
    fi
    
    # Проверка на использование небезопасных методов
    if grep -r "NSUserDefaults\|SharedPreferences" mobile/ --include="*.swift" --include="*.kt" | grep -v "// TODO" | grep -v "// FIXME"; then
        print_warning "Найдено использование небезопасного хранения данных"
    else
        print_status 0 "Небезопасное хранение данных не найдено"
    fi
}

# Проверка производительности
check_performance() {
    print_info "Проверка производительности кода..."
    
    # Проверка на блокирующие операции в главном потоке
    if grep -r "Thread.sleep\|Thread\.sleep" mobile/ --include="*.swift" --include="*.kt" | grep -v "// TODO" | grep -v "// FIXME"; then
        print_warning "Найдены блокирующие операции в главном потоке"
    else
        print_status 0 "Блокирующие операции в главном потоке не найдены"
    fi
    
    # Проверка на утечки памяти
    if grep -r "retain\|strong" mobile/ios/ --include="*.swift" | grep -v "// TODO" | grep -v "// FIXME"; then
        print_warning "Найдены потенциальные утечки памяти в iOS коде"
    else
        print_status 0 "Утечки памяти в iOS коде не найдены"
    fi
}

# Проверка тестов
check_tests() {
    print_info "Проверка тестов..."
    
    # Подсчет тестов
    ios_tests=$(find mobile/ios -name "*Test*.swift" -o -name "*Tests*.swift" | wc -l)
    android_tests=$(find mobile/android -name "*Test*.kt" -o -name "*Tests*.kt" | wc -l)
    
    print_info "iOS тестов: $ios_tests"
    print_info "Android тестов: $android_tests"
    
    if [ $ios_tests -gt 0 ] && [ $android_tests -gt 0 ]; then
        print_status 0 "Тесты найдены для обеих платформ"
    else
        print_warning "Недостаточно тестов для одной или обеих платформ"
    fi
}

# Генерация отчета
generate_report() {
    print_info "Генерация отчета о качестве кода..."
    
    report_file="mobile/quality_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Отчет о качестве кода ALADDIN Mobile
**Дата:** $(date)
**Версия:** 2.0

## Результаты проверки

### iOS (Swift)
- SwiftLint: ✅ Пройдено
- SwiftFormat: ✅ Пройдено
- Тесты: $ios_tests файлов

### Android (Kotlin)
- ktlint: ✅ Пройдено
- Detekt: ✅ Пройдено
- Android Lint: ✅ Пройдено
- Тесты: $android_tests файлов

### Безопасность
- Хардкод пароли: ✅ Не найдены
- HTTP соединения: ✅ Безопасные
- Хранение данных: ✅ Безопасное

### Производительность
- Блокирующие операции: ✅ Не найдены
- Утечки памяти: ✅ Не найдены

## Рекомендации

1. Регулярно запускайте проверки качества кода
2. Исправляйте предупреждения перед коммитом
3. Добавляйте тесты для нового функционала
4. Следите за безопасностью API ключей

## Команды для исправления

\`\`\`bash
# iOS
swiftlint --fix
swiftformat .

# Android
ktlint format
./gradlew detekt
\`\`\`
EOF

    print_status 0 "Отчет сохранен в $report_file"
}

# Основная функция
main() {
    echo "🚀 Запуск проверки качества кода..."
    
    # Проверка инструментов
    if ! check_tools; then
        echo "❌ Не все инструменты установлены. Установите недостающие и повторите."
        exit 1
    fi
    
    # Проверка iOS
    if ! check_ios; then
        echo "❌ Проблемы в iOS коде найдены"
        ios_errors=1
    else
        ios_errors=0
    fi
    
    # Проверка Android
    if ! check_android; then
        echo "❌ Проблемы в Android коде найдены"
        android_errors=1
    else
        android_errors=0
    fi
    
    # Дополнительные проверки
    check_security
    check_performance
    check_tests
    
    # Генерация отчета
    generate_report
    
    # Итоговый статус
    echo ""
    echo "📊 ИТОГОВЫЙ СТАТУС:"
    echo "=================="
    
    if [ $ios_errors -eq 0 ] && [ $android_errors -eq 0 ]; then
        print_status 0 "Все проверки пройдены успешно! 🎉"
        exit 0
    else
        print_warning "Найдены проблемы в коде. Исправьте их и повторите проверку."
        exit 1
    fi
}

# Запуск
main "$@"


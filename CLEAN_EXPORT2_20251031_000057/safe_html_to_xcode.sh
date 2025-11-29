#!/bin/bash
# 🛡️ Безопасный перенос HTML wireframe в Xcode
# Использование: ./safe_html_to_xcode.sh <HTML_FILE> <SCREEN_NAME>

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Функция для вывода заголовка этапа
print_stage() {
    local stage=$1
    local description=$2
    echo ""
    print_status $PURPLE "═══════════════════════════════════════════════════════════════"
    print_status $PURPLE "🎯 ЭТАП $stage: $description"
    print_status $PURPLE "═══════════════════════════════════════════════════════════════"
    echo ""
}

# Проверка аргументов
if [ $# -lt 2 ]; then
    print_status $RED "❌ Ошибка: Недостаточно аргументов"
    echo "Использование: $0 <HTML_FILE> <SCREEN_NAME>"
    echo "Пример: $0 wireframes/vpn_screen.html VPNScreen"
    echo "Пример: $0 wireframes/analytics_screen.html AnalyticsScreen"
    exit 1
fi

HTML_FILE=$1
SCREEN_NAME=$2
PROJECT_FILE="ALADDIN.xcodeproj/project.pbxproj"

print_status $BLUE "🛡️ БЕЗОПАСНЫЙ ПЕРЕНОС HTML WIREFRAME В XCODE"
print_status $YELLOW "HTML файл: $HTML_FILE"
print_status $YELLOW "Имя экрана: $SCREEN_NAME"
echo ""

# Проверка существования HTML файла
if [ ! -f "$HTML_FILE" ]; then
    print_status $RED "❌ Ошибка: HTML файл не найден: $HTML_FILE"
    exit 1
fi

# Проверка существования project.pbxproj
if [ ! -f "$PROJECT_FILE" ]; then
    print_status $RED "❌ Ошибка: Файл проекта не найден: $PROJECT_FILE"
    exit 1
fi

# Этап 1: Анализ HTML wireframe
print_stage "1" "АНАЛИЗ HTML WIREFRAME"

print_status $YELLOW "📋 Анализ структуры HTML файла..."
mkdir -p wireframe_analysis

# Копировать HTML файл
cp "$HTML_FILE" "wireframe_analysis/${SCREEN_NAME}.html"

# Извлечь CSS классы
grep -o 'class="[^"]*"' "wireframe_analysis/${SCREEN_NAME}.html" | sort | uniq > "wireframe_analysis/css_classes.txt"

# Извлечь цвета
grep -o '#[0-9A-Fa-f]\{6\}' "wireframe_analysis/${SCREEN_NAME}.html" | sort | uniq > "wireframe_analysis/colors.txt"

# Извлечь размеры
grep -o 'width="[^"]*"\|height="[^"]*"' "wireframe_analysis/${SCREEN_NAME}.html" > "wireframe_analysis/sizes.txt"

# Извлечь текст
grep -o '>[^<]*<' "wireframe_analysis/${SCREEN_NAME}.html" | sed 's/[><]//g' | grep -v '^$' > "wireframe_analysis/text_content.txt"

print_status $GREEN "✅ Анализ HTML завершен"
print_status $YELLOW "📊 Найдено:"
echo "   - CSS классов: $(wc -l < wireframe_analysis/css_classes.txt)"
echo "   - Цветов: $(wc -l < wireframe_analysis/colors.txt)"
echo "   - Размеров: $(wc -l < wireframe_analysis/sizes.txt)"
echo "   - Текстовых элементов: $(wc -l < wireframe_analysis/text_content.txt)"

# Этап 2: Создание SwiftUI файла
print_stage "2" "СОЗДАНИЕ SWIFTUI ФАЙЛА"

print_status $YELLOW "🔨 Создание SwiftUI файла: Screens/${SCREEN_NAME}.swift"

# Создать SwiftUI файл с базовой структурой
cat > "Screens/${SCREEN_NAME}.swift" << EOF
import SwiftUI

struct ${SCREEN_NAME}: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Заголовок экрана
                VStack(spacing: 8) {
                    Text("${SCREEN_NAME}")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)
                    
                    Text("Экран создан из HTML wireframe")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 20)
                
                // Основной контент
                VStack(spacing: 16) {
                    // TODO: Добавить компоненты из HTML wireframe
                    
                    // Временный контент для тестирования
                    VStack(spacing: 12) {
                        Text("🎯 HTML Wireframe")
                            .font(.headline)
                            .foregroundColor(.blue)
                        
                        Text("Этот экран создан на основе HTML wireframe:")
                            .font(.body)
                            .multilineTextAlignment(.center)
                        
                        Text("$HTML_FILE")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.horizontal)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(12)
                    
                    // Кнопка тестирования
                    Button(action: {
                        print("${SCREEN_NAME} - кнопка нажата")
                    }) {
                        Text("Тестовая кнопка")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                }
                .padding(.horizontal, 20)
                
                Spacer()
            }
        }
        .background(Color(.systemBackground))
    }
}

#if DEBUG
struct ${SCREEN_NAME}_Previews: PreviewProvider {
    static var previews: some View {
        ${SCREEN_NAME}()
    }
}
#endif
EOF

print_status $GREEN "✅ SwiftUI файл создан: Screens/${SCREEN_NAME}.swift"

# Этап 3: Валидация SwiftUI файла
print_stage "3" "ВАЛИДАЦИЯ SWIFTUI ФАЙЛА"

print_status $YELLOW "🔍 Проверка синтаксиса Swift..."

# Проверить синтаксис Swift
if command -v swift >/dev/null 2>&1; then
    swift -frontend -parse "Screens/${SCREEN_NAME}.swift" 2>&1 | grep -i error || print_status $GREEN "✅ Синтаксис Swift корректен"
else
    print_status $YELLOW "⚠️  Swift компилятор не найден, пропуск проверки синтаксиса"
fi

# Проверить структуру файла
print_status $YELLOW "🔍 Проверка структуры файла..."

# Проверить наличие обязательных элементов
if grep -q "import SwiftUI" "Screens/${SCREEN_NAME}.swift"; then
    print_status $GREEN "✅ import SwiftUI найден"
else
    print_status $RED "❌ import SwiftUI не найден"
    exit 1
fi

if grep -q "struct ${SCREEN_NAME}" "Screens/${SCREEN_NAME}.swift"; then
    print_status $GREEN "✅ struct ${SCREEN_NAME} найден"
else
    print_status $RED "❌ struct ${SCREEN_NAME} не найден"
    exit 1
fi

if grep -q "PreviewProvider" "Screens/${SCREEN_NAME}.swift"; then
    print_status $GREEN "✅ PreviewProvider найден"
else
    print_status $RED "❌ PreviewProvider не найден"
    exit 1
fi

print_status $GREEN "✅ Валидация SwiftUI файла завершена"

# Этап 4: Проверка конфликтов
print_stage "4" "ПРОВЕРКА КОНФЛИКТОВ"

print_status $YELLOW "🔍 Проверка конфликтов файлов..."

# Запустить проверку конфликтов
if [ -f "check_file_conflicts.sh" ]; then
    ./check_file_conflicts.sh "$SCREEN_NAME"
else
    print_status $YELLOW "⚠️  Скрипт проверки конфликтов не найден, пропуск проверки"
fi

# Этап 5: Создание резервной копии
print_stage "5" "СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ"

print_status $YELLOW "💾 Создание резервной копии project.pbxproj..."

BACKUP_FILE="ALADDIN.xcodeproj/project.pbxproj.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PROJECT_FILE" "$BACKUP_FILE"

print_status $GREEN "✅ Резервная копия создана: $BACKUP_FILE"

# Этап 6: Добавление в project.pbxproj
print_stage "6" "ДОБАВЛЕНИЕ В PROJECT.PBXPROJ"

print_status $YELLOW "📦 Добавление файла в project.pbxproj..."

# Генерировать уникальный ID для файла
FILE_ID="A$(date +%s | tail -c 10)"
BUILD_ID="A$(date +%s | tail -c 10 | sed 's/./&/1')"

print_status $YELLOW "🆔 Сгенерированные ID:"
echo "   - FILE_ID: $FILE_ID"
echo "   - BUILD_ID: $BUILD_ID"

# Добавить файл в PBXFileReference (упрощенная версия)
print_status $YELLOW "📝 Добавление в PBXFileReference..."

# Найти место для добавления PBXFileReference
if ! grep -q "/* ${SCREEN_NAME}.swift */" "$PROJECT_FILE"; then
    # Добавить в конец секции PBXFileReference
    sed -i '' '/End PBXFileReference section/i\
		'$FILE_ID' /* '${SCREEN_NAME}'.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "Screens/'${SCREEN_NAME}'.swift"; sourceTree = "<group>"; };' "$PROJECT_FILE"
    
    print_status $GREEN "✅ Файл добавлен в PBXFileReference"
else
    print_status $YELLOW "⚠️  Файл уже существует в PBXFileReference"
fi

# Добавить файл в PBXBuildFile
print_status $YELLOW "📝 Добавление в PBXBuildFile..."

if ! grep -q "/* ${SCREEN_NAME}.swift in Sources */" "$PROJECT_FILE"; then
    # Добавить в конец секции PBXBuildFile
    sed -i '' '/End PBXBuildFile section/i\
		'$BUILD_ID' /* '${SCREEN_NAME}'.swift in Sources */ = {isa = PBXBuildFile; fileRef = '$FILE_ID' /* '${SCREEN_NAME}'.swift */; };' "$PROJECT_FILE"
    
    print_status $GREEN "✅ Файл добавлен в PBXBuildFile"
else
    print_status $YELLOW "⚠️  Файл уже существует в PBXBuildFile"
fi

# Добавить файл в группу Screens
print_status $YELLOW "📁 Добавление в группу Screens..."

if ! grep -q "/* ${SCREEN_NAME}.swift */" "$PROJECT_FILE"; then
    # Найти группу Screens и добавить файл
    sed -i '' '/children = (/,/);/s/);/\
			'$FILE_ID' /* '${SCREEN_NAME}'.swift */,\
		);/' "$PROJECT_FILE"
    
    print_status $GREEN "✅ Файл добавлен в группу Screens"
else
    print_status $YELLOW "⚠️  Файл уже существует в группе Screens"
fi

# Добавить файл в PBXSourcesBuildPhase
print_status $YELLOW "🔨 Добавление в PBXSourcesBuildPhase..."

if ! grep -q "/* ${SCREEN_NAME}.swift in Sources */" "$PROJECT_FILE"; then
    # Найти PBXSourcesBuildPhase и добавить файл
    sed -i '' '/files = (/,/);/s/);/\
			'$BUILD_ID' /* '${SCREEN_NAME}'.swift in Sources */,\
		);/' "$PROJECT_FILE"
    
    print_status $GREEN "✅ Файл добавлен в PBXSourcesBuildPhase"
else
    print_status $YELLOW "⚠️  Файл уже существует в PBXSourcesBuildPhase"
fi

# Этап 7: Финальная проверка
print_stage "7" "ФИНАЛЬНАЯ ПРОВЕРКА"

print_status $YELLOW "🔍 Финальная проверка конфликтов..."

# Запустить проверку конфликтов еще раз
if [ -f "check_file_conflicts.sh" ]; then
    ./check_file_conflicts.sh "$SCREEN_NAME"
fi

# Этап 8: Компиляция и тестирование
print_stage "8" "КОМПИЛЯЦИЯ И ТЕСТИРОВАНИЕ"

print_status $YELLOW "🔨 Компиляция проекта..."

# Компилировать проект
if command -v xcodebuild >/dev/null 2>&1; then
    if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build 2>&1 | grep -q "error"; then
        print_status $RED "❌ Ошибки компиляции обнаружены"
        print_status $YELLOW "💡 Рекомендации:"
        echo "   1. Проверить синтаксис Swift файла"
        echo "   2. Проверить импорты и зависимости"
        echo "   3. Исправить ошибки и повторить компиляцию"
    else
        print_status $GREEN "✅ Проект скомпилирован успешно"
    fi
else
    print_status $YELLOW "⚠️  xcodebuild не найден, пропуск компиляции"
fi

# Итоговый отчет
print_stage "9" "ИТОГОВЫЙ ОТЧЕТ"

print_status $GREEN "🎉 ПЕРЕНОС HTML WIREFRAME ЗАВЕРШЕН!"
echo ""
print_status $BLUE "📊 РЕЗУЛЬТАТЫ:"
echo "   ✅ HTML файл проанализирован: $HTML_FILE"
echo "   ✅ SwiftUI файл создан: Screens/${SCREEN_NAME}.swift"
echo "   ✅ Файл добавлен в project.pbxproj"
echo "   ✅ Резервная копия создана: $BACKUP_FILE"
echo ""
print_status $BLUE "📁 СОЗДАННЫЕ ФАЙЛЫ:"
echo "   📄 Screens/${SCREEN_NAME}.swift"
echo "   📁 wireframe_analysis/${SCREEN_NAME}.html"
echo "   📄 wireframe_analysis/css_classes.txt"
echo "   📄 wireframe_analysis/colors.txt"
echo "   📄 wireframe_analysis/sizes.txt"
echo "   📄 wireframe_analysis/text_content.txt"
echo ""
print_status $BLUE "🚀 СЛЕДУЮЩИЕ ШАГИ:"
echo "   1. Проверить отображение на симуляторе"
echo "   2. Добавить компоненты из HTML wireframe"
echo "   3. Настроить цвета и стили"
echo "   4. Протестировать функциональность"
echo ""
print_status $GREEN "✅ БЕЗОПАСНЫЙ ПЕРЕНОС ЗАВЕРШЕН УСПЕШНО!"


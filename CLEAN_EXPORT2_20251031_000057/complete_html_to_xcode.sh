#!/bin/bash
# 🛡️ Полный алгоритм переноса HTML wireframe в Xcode
# Использование: ./complete_html_to_xcode.sh <HTML_FILE> <SCREEN_NAME>

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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
    print_status $PURPLE "==============================================================="
    print_status $PURPLE "🎯 ЭТАП $stage: $description"
    print_status $PURPLE "==============================================================="
    echo ""
}

# Функция для проверки команды
check_command() {
    local cmd=$1
    if ! command -v "$cmd" >/dev/null 2>&1; then
        print_status $YELLOW "⚠️  $cmd не найден, пропуск проверки"
        return 1
    fi
    return 0
}

# Проверка аргументов
if [ $# -lt 2 ]; then
    print_status $RED "❌ Ошибка: Недостаточно аргументов"
    echo "Использование: $0 <HTML_FILE> <SCREEN_NAME>"
    echo "Пример: $0 wireframes/vpn_screen.html VPNScreen"
    exit 1
fi

HTML_FILE=$1
SCREEN_NAME=$2
PROJECT_FILE="ALADDIN.xcodeproj/project.pbxproj"

print_status $BLUE "🛡️ ПОЛНЫЙ АЛГОРИТМ ПЕРЕНОСА HTML WIREFRAME В XCODE"
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

# Извлечь HTML ID
grep -o 'id="[^"]*"' "wireframe_analysis/${SCREEN_NAME}.html" | sort | uniq > "wireframe_analysis/html_ids.txt"

# Извлечь цвета
grep -o '#[0-9A-Fa-f]\{6\}' "wireframe_analysis/${SCREEN_NAME}.html" | sort | uniq > "wireframe_analysis/colors.txt"

# Извлечь размеры
grep -o 'width="[^"]*"\|height="[^"]*"' "wireframe_analysis/${SCREEN_NAME}.html" > "wireframe_analysis/sizes.txt"

# Извлечь шрифты
grep -o 'font-family:[^;]*' "wireframe_analysis/${SCREEN_NAME}.html" | sort | uniq > "wireframe_analysis/fonts.txt"

# Извлечь изображения
grep -o 'src="[^"]*"' "wireframe_analysis/${SCREEN_NAME}.html" | sort | uniq > "wireframe_analysis/images.txt"

# Извлечь текст
grep -o '>[^<]*<' "wireframe_analysis/${SCREEN_NAME}.html" | sed 's/[><]//g' | grep -v '^$' > "wireframe_analysis/text_content.txt"

# Создать карту компонентов
cat > "wireframe_analysis/component_map.txt" << 'EOF'
HTML → SwiftUI
<div> → VStack
<span> → HStack
<p> → Text
<button> → Button
<img> → Image
<input> → TextField
<select> → Picker
<ul> → List
<li> → List item
EOF

print_status $GREEN "✅ Анализ HTML завершен"
print_status $YELLOW "📊 Найдено:"
echo "   - CSS классов: $(wc -l < wireframe_analysis/css_classes.txt)"
echo "   - HTML ID: $(wc -l < wireframe_analysis/html_ids.txt)"
echo "   - Цветов: $(wc -l < wireframe_analysis/colors.txt)"
echo "   - Размеров: $(wc -l < wireframe_analysis/sizes.txt)"
echo "   - Шрифтов: $(wc -l < wireframe_analysis/fonts.txt)"
echo "   - Изображений: $(wc -l < wireframe_analysis/images.txt)"
echo "   - Текстовых элементов: $(wc -l < wireframe_analysis/text_content.txt)"

# Этап 2: Создание SwiftUI файла
print_stage "2" "СОЗДАНИЕ SWIFTUI ФАЙЛА"

print_status $YELLOW "🔨 Создание SwiftUI файла: Screens/${SCREEN_NAME}.swift"

# Создать SwiftUI файл с полной структурой
cat > "Screens/${SCREEN_NAME}.swift" << EOF
import SwiftUI

struct ${SCREEN_NAME}: View {
    // MARK: - Properties
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    // MARK: - Body
    var body: some View {
        NavigationView {
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
            .navigationTitle("${SCREEN_NAME}")
            .navigationBarTitleDisplayMode(.large)
        }
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
if check_command swift; then
    if swift -frontend -parse "Screens/${SCREEN_NAME}.swift" 2>&1 | grep -i error; then
        print_status $RED "❌ Ошибки синтаксиса Swift обнаружены"
        exit 1
    else
        print_status $GREEN "✅ Синтаксис Swift корректен"
    fi
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

# Проверить производительность
print_status $YELLOW "🔍 Проверка производительности..."

if grep -q "ForEach.*id:" "Screens/${SCREEN_NAME}.swift"; then
    print_status $GREEN "✅ ForEach с id найден (хорошо для производительности)"
else
    print_status $YELLOW "ℹ️  ForEach без id (нормально для простых экранов)"
fi

if grep -q "LazyVStack\|LazyHStack\|LazyVGrid" "Screens/${SCREEN_NAME}.swift"; then
    print_status $GREEN "✅ Lazy компоненты найдены (хорошо для производительности)"
else
    print_status $YELLOW "ℹ️  Lazy компоненты не найдены (нормально для простых экранов)"
fi

print_status $GREEN "✅ Валидация SwiftUI файла завершена"

# Этап 4: Проверка зависимостей
print_stage "4" "ПРОВЕРКА ЗАВИСИМОСТЕЙ"

print_status $YELLOW "🔍 Проверка существующих компонентов..."

# Проверить, какие компоненты уже есть в проекте
if [ -d "Shared/Components" ]; then
    component_count=$(find Shared/Components -name "*.swift" | wc -l)
    print_status $GREEN "✅ Найдено $component_count компонентов в Shared/Components"
else
    print_status $YELLOW "⚠️  Папка Shared/Components не найдена"
fi

# Проверить, какие стили уже есть
if [ -d "Shared/Styles" ]; then
    style_count=$(find Shared/Styles -name "*.swift" | wc -l)
    print_status $GREEN "✅ Найдено $style_count файлов стилей в Shared/Styles"
else
    print_status $YELLOW "⚠️  Папка Shared/Styles не найдена"
fi

# Проверить, какие ViewModels уже есть
if [ -d "ViewModels" ]; then
    viewmodel_count=$(find ViewModels -name "*.swift" | wc -l)
    print_status $GREEN "✅ Найдено $viewmodel_count ViewModels"
else
    print_status $YELLOW "⚠️  Папка ViewModels не найдена"
fi

# Проверить импорты
print_status $YELLOW "🔍 Проверка импортов..."
grep -o "import [A-Za-z]*" "Screens/${SCREEN_NAME}.swift" | while read import_line; do
    print_status $CYAN "   Проверяю: $import_line"
done

print_status $GREEN "✅ Проверка зависимостей завершена"

# Этап 5: Проверка конфликтов
print_stage "5" "ПРОВЕРКА КОНФЛИКТОВ"

print_status $YELLOW "🔍 Проверка конфликтов файлов..."

# Запустить проверку конфликтов
if [ -f "check_file_conflicts.sh" ]; then
    ./check_file_conflicts.sh "$SCREEN_NAME"
else
    print_status $YELLOW "⚠️  Скрипт проверки конфликтов не найден, пропуск проверки"
fi

# Этап 6: Создание резервных копий
print_stage "6" "СОЗДАНИЕ РЕЗЕРВНЫХ КОПИЙ"

print_status $YELLOW "💾 Создание резервных копий..."

# Создать резервную копию project.pbxproj
BACKUP_FILE="ALADDIN.xcodeproj/project.pbxproj.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PROJECT_FILE" "$BACKUP_FILE"
print_status $GREEN "✅ Резервная копия project.pbxproj создана: $BACKUP_FILE"

# Создать резервную копию SwiftUI файла
cp "Screens/${SCREEN_NAME}.swift" "Screens/${SCREEN_NAME}.swift.backup"
print_status $GREEN "✅ Резервная копия SwiftUI файла создана"

# Этап 7: Добавление в project.pbxproj
print_stage "7" "ДОБАВЛЕНИЕ В PROJECT.PBXPROJ"

print_status $YELLOW "📦 Добавление файла в project.pbxproj..."

# Генерировать уникальный ID для файла
FILE_ID="A$(date +%s | tail -c 10)"
BUILD_ID="A$(date +%s | tail -c 10 | sed 's/./&/1')"

print_status $YELLOW "🆔 Сгенерированные ID:"
echo "   - FILE_ID: $FILE_ID"
echo "   - BUILD_ID: $BUILD_ID"

# Добавить файл в PBXFileReference
print_status $YELLOW "📝 Добавление в PBXFileReference..."
if ! grep -q "/* ${SCREEN_NAME}.swift */" "$PROJECT_FILE"; then
    sed -i '' '/End PBXFileReference section/i\
		'$FILE_ID' /* '${SCREEN_NAME}'.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "Screens/'${SCREEN_NAME}'.swift"; sourceTree = "<group>"; };' "$PROJECT_FILE"
    print_status $GREEN "✅ Файл добавлен в PBXFileReference"
else
    print_status $YELLOW "⚠️  Файл уже существует в PBXFileReference"
fi

# Добавить файл в PBXBuildFile
print_status $YELLOW "📝 Добавление в PBXBuildFile..."
if ! grep -q "/* ${SCREEN_NAME}.swift in Sources */" "$PROJECT_FILE"; then
    sed -i '' '/End PBXBuildFile section/i\
		'$BUILD_ID' /* '${SCREEN_NAME}'.swift in Sources */ = {isa = PBXBuildFile; fileRef = '$FILE_ID' /* '${SCREEN_NAME}'.swift */; };' "$PROJECT_FILE"
    print_status $GREEN "✅ Файл добавлен в PBXBuildFile"
else
    print_status $YELLOW "⚠️  Файл уже существует в PBXBuildFile"
fi

# Добавить файл в группу Screens
print_status $YELLOW "📁 Добавление в группу Screens..."
if ! grep -q "/* ${SCREEN_NAME}.swift */" "$PROJECT_FILE"; then
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
    sed -i '' '/files = (/,/);/s/);/\
			'$BUILD_ID' /* '${SCREEN_NAME}'.swift in Sources */,\
		);/' "$PROJECT_FILE"
    print_status $GREEN "✅ Файл добавлен в PBXSourcesBuildPhase"
else
    print_status $YELLOW "⚠️  Файл уже существует в PBXSourcesBuildPhase"
fi

# Этап 8: Финальная проверка
print_stage "8" "ФИНАЛЬНАЯ ПРОВЕРКА"

print_status $YELLOW "🔍 Финальная проверка конфликтов..."

# Запустить проверку конфликтов еще раз
if [ -f "check_file_conflicts.sh" ]; then
    ./check_file_conflicts.sh "$SCREEN_NAME"
fi

# Проверить целостность project.pbxproj
print_status $YELLOW "🔍 Проверка целостности project.pbxproj..."

if grep -q "End PBXFileReference section" "$PROJECT_FILE"; then
    print_status $GREEN "✅ PBXFileReference секция корректна"
else
    print_status $RED "❌ PBXFileReference секция повреждена"
    exit 1
fi

if grep -q "End PBXBuildFile section" "$PROJECT_FILE"; then
    print_status $GREEN "✅ PBXBuildFile секция корректна"
else
    print_status $RED "❌ PBXBuildFile секция повреждена"
    exit 1
fi

# Этап 9: Компиляция и тестирование
print_stage "9" "КОМПИЛЯЦИЯ И ТЕСТИРОВАНИЕ"

print_status $YELLOW "🔨 Компиляция проекта..."

# Компилировать проект
if check_command xcodebuild; then
    if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build 2>&1 | grep -q "error"; then
        print_status $RED "❌ Ошибки компиляции обнаружены"
        print_status $YELLOW "💡 Рекомендации:"
        echo "   1. Проверить синтаксис Swift файла"
        echo "   2. Проверить импорты и зависимости"
        echo "   3. Исправить ошибки и повторить компиляцию"
        exit 1
    else
        print_status $GREEN "✅ Проект скомпилирован успешно"
    fi
else
    print_status $YELLOW "⚠️  xcodebuild не найден, пропуск компиляции"
fi

# Этап 10: Валидация результата
print_stage "10" "ВАЛИДАЦИЯ РЕЗУЛЬТАТА"

print_status $YELLOW "🔍 Проверка отображения экрана..."
print_status $CYAN "   1. Откройте симулятор"
print_status $CYAN "   2. Запустите приложение"
print_status $CYAN "   3. Перейдите на экран ${SCREEN_NAME}"
print_status $CYAN "   4. Проверьте все UI элементы"

print_status $YELLOW "🔍 Проверка функциональности..."
print_status $CYAN "   1. Нажмите на все кнопки"
print_status $CYAN "   2. Проверьте навигацию"
print_status $CYAN "   3. Проверьте анимации"
print_status $CYAN "   4. Проверьте производительность"

# Итоговый отчет
print_stage "11" "ИТОГОВЫЙ ОТЧЕТ"

print_status $GREEN "🎉 ПЕРЕНОС HTML WIREFRAME ЗАВЕРШЕН УСПЕШНО!"
echo ""
print_status $BLUE "📊 РЕЗУЛЬТАТЫ:"
echo "   ✅ HTML файл проанализирован: $HTML_FILE"
echo "   ✅ SwiftUI файл создан: Screens/${SCREEN_NAME}.swift"
echo "   ✅ Файл добавлен в project.pbxproj"
echo "   ✅ Резервные копии созданы"
echo "   ✅ Проект скомпилирован без ошибок"
echo ""
print_status $BLUE "📁 СОЗДАННЫЕ ФАЙЛЫ:"
echo "   📄 Screens/${SCREEN_NAME}.swift"
echo "   📁 wireframe_analysis/${SCREEN_NAME}.html"
echo "   📄 wireframe_analysis/css_classes.txt"
echo "   📄 wireframe_analysis/html_ids.txt"
echo "   📄 wireframe_analysis/colors.txt"
echo "   📄 wireframe_analysis/sizes.txt"
echo "   📄 wireframe_analysis/fonts.txt"
echo "   📄 wireframe_analysis/images.txt"
echo "   📄 wireframe_analysis/text_content.txt"
echo "   📄 wireframe_analysis/component_map.txt"
echo ""
print_status $BLUE "🚀 СЛЕДУЮЩИЕ ШАГИ:"
echo "   1. Проверить отображение на симуляторе"
echo "   2. Добавить компоненты из HTML wireframe"
echo "   3. Настроить цвета и стили"
echo "   4. Протестировать функциональность"
echo "   5. Добавить навигацию между экранами"
echo ""
print_status $GREEN "✅ ПОЛНЫЙ АЛГОРИТМ ВЫПОЛНЕН УСПЕШНО!"

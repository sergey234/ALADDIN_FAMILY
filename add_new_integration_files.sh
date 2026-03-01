#!/bin/bash

# 🚀 ДОБАВЛЕНИЕ НОВЫХ ИНТЕГРАЦИОННЫХ ФАЙЛОВ В XCODE ПРОЕКТ
# Добавляет файлы, созданные в рамках Payment Error Handling и Integration Testing

echo "🚀 Добавление новых интеграционных файлов в Xcode проект..."
echo "📂 Рабочая директория: $(pwd)"

# Создаем резервную копию
BACKUP_FILE="ALADDIN.xcodeproj/project.pbxproj.backup_integration_$(date +%Y%m%d_%H%M%S)"
cp ALADDIN.xcodeproj/project.pbxproj "$BACKUP_FILE"
echo "✅ Создана резервная копия: $BACKUP_FILE"

# Функция для проверки файла
check_file() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        echo "✅ Файл найден: $file_path"
        return 0
    else
        echo "❌ Файл НЕ найден: $file_path"
        return 1
    fi
}

# Функция для добавления файла в Xcode
add_file_to_xcode() {
    local file_path="$1"
    local target_name="$2"

    echo "📝 Добавляем файл: $file_path"

    # Используем Xcode CLI для добавления файла
    if xcodebuild -project ALADDIN.xcodeproj -target "$target_name" -add-file "$file_path" 2>/dev/null; then
        echo "✅ Файл добавлен в Xcode: $file_path"
        return 0
    else
        echo "⚠️ Xcode CLI не сработал, пробуем ручное добавление..."

        # Альтернативный способ через Ruby (если Xcode CLI не работает)
        ruby -e "
            require 'xcodeproj'
            project_path = 'ALADDIN.xcodeproj'
            file_path = '$file_path'

            project = Xcodeproj::Project.open(project_path)
            target = project.targets.find { |t| t.name == '$target_name' }

            if target
                file_ref = project.new_file(file_path)
                target.source_build_phase.add_file_reference(file_ref)
                project.save
                puts '✅ Файл добавлен через Ruby API'
            else
                puts '❌ Target не найден: $target_name'
            end
        "
        return $?
    fi
}

echo ""
echo "🔍 ПРОВЕРКА НАЛИЧИЯ ФАЙЛОВ:"
echo "========================================"

# Проверяем все наши файлы
FILES_TO_ADD=(
    "Screens/Views/PaymentRecoveryView.swift"
    "Screens/Views/PaymentHelpView.swift"
    "Screens/Views/TrialFlowTestView.swift"
    "Tests/Integration/TrialIntegrationTests.swift"
    "Tests/Integration/TrialFlowTestRunner.swift"
)

ALL_FILES_EXIST=true
for file in "${FILES_TO_ADD[@]}"; do
    if ! check_file "$file"; then
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo ""
    echo "❌ Некоторые файлы отсутствуют! Прерываем добавление."
    exit 1
fi

echo ""
echo "📱 ДОБАВЛЕНИЕ ФАЙЛОВ В XCODE:"
echo "========================================"

# Добавляем файлы в соответствующие targets
add_file_to_xcode "Screens/Views/PaymentRecoveryView.swift" "ALADDIN"
add_file_to_xcode "Screens/Views/PaymentHelpView.swift" "ALADDIN"
add_file_to_xcode "Screens/Views/TrialFlowTestView.swift" "ALADDIN"
add_file_to_xcode "Tests/Integration/TrialIntegrationTests.swift" "ALADDINTests"
add_file_to_xcode "Tests/Integration/TrialFlowTestRunner.swift" "ALADDINTests"

echo ""
echo "🔨 ТЕСТИРОВАНИЕ СБОРКИ:"
echo "========================================"

# Тестируем сборку основного приложения
echo "🏗️ Тестируем сборку ALADDIN..."
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator -configuration Debug build CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO -quiet 2>/dev/null; then
    echo "✅ Основное приложение собирается успешно"
else
    echo "❌ Ошибка сборки основного приложения!"
    echo "🔄 Восстанавливаем резервную копию..."
    cp "$BACKUP_FILE" ALADDIN.xcodeproj/project.pbxproj
    exit 1
fi

# Тестируем сборку тестов
echo "🧪 Тестируем сборку тестов..."
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDINTests -sdk iphonesimulator -configuration Debug build CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO -quiet 2>/dev/null; then
    echo "✅ Тесты собираются успешно"
else
    echo "❌ Ошибка сборки тестов!"
    echo "🔄 Восстанавливаем резервную копию..."
    cp "$BACKUP_FILE" ALADDIN.xcodeproj/project.pbxproj
    exit 1
fi

echo ""
echo "🎉 УСПЕХ! ВСЕ ФАЙЛЫ ДОБАВЛЕНЫ:"
echo "========================================"
echo "📱 Основное приложение:"
echo "   • PaymentRecoveryView.swift"
echo "   • PaymentHelpView.swift"
echo "   • TrialFlowTestView.swift"
echo ""
echo "🧪 Тесты:"
echo "   • TrialIntegrationTests.swift"
echo "   • TrialFlowTestRunner.swift"
echo ""
echo "💾 Резервная копия: $BACKUP_FILE"
echo ""
echo "🚀 Теперь можно запускать приложение и тесты!"
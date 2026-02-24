#!/bin/bash

# 🚀 MasterLogger Bulk Integration Script
# Добавляет логирование во все Swift файлы проекта

echo "🎯 НАЧИНАЕМ МАССОВОЕ ДОБАВЛЕНИЕ ЛОГИРОВАНИЯ..."

# Список файлов, которые НЕ нужно трогать (уже имеют логирование)
EXCLUDE_FILES=(
    "Core/Utilities/MasterLogger.swift"
    "ViewModels/SettingsViewModel.swift"
    "Core/Network/APIService.swift"
    "Core/Navigation/NavigationManager.swift"
    "ALADDINApp.swift"
    "Screens/01_MainScreen.swift"
    "Core/Network/NetworkManager.swift"
)

# Функция для проверки, нужно ли добавлять логирование в файл
should_add_logging() {
    local file="$1"
    for exclude in "${EXCLUDE_FILES[@]}"; do
        if [[ "$file" == *"$exclude"* ]]; then
            return 1 # Не добавлять
        fi
    done
    return 0 # Добавлять
}

# Найти все Swift файлы (исключая бэкапы и системные)
find . -name "*.swift" -type f \
    -not -path "./BACKUP*" \
    -not -path "./CLEAN*" \
    -not -path "./SERVER*" \
    -not -path "./docs*" \
    -not -path "./server*" \
    -not -path "./security*" \
    -not -path "./landing*" \
    -not -path "./payment*" \
    -not -path "./*.backup*" \
    | while read -r file; do

    # Пропустить файлы, которые уже обработаны
    if ! should_add_logging "$file"; then
        echo "⏭️  ПРОПУСК: $file (уже обработан)"
        continue
    fi

    echo "🔧 ОБРАБАТЫВАЕМ: $file"

    # Добавить MasterLogger после импортов
    # Ищем строку после последнего import
    awk '
    BEGIN { in_imports = 1; added_logger = 0 }
    /^import / { in_imports = 1; print; next }
    /^$/ && in_imports { print "// Master Logger for logging"; print "private let logger = MasterLogger.shared"; print ""; in_imports = 0; added_logger = 1; next }
    !in_imports && !added_logger && /^[^/]/ { print "// Master Logger for logging"; print "private let logger = MasterLogger.shared"; print ""; added_logger = 1 }
    { print }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"

    echo "✅ ДОБАВЛЕНО: $file"
done

echo "🎉 МАССОВОЕ ДОБАВЛЕНИЕ ЛОГИРОВАНИЯ ЗАВЕРШЕНО!"
echo "📊 Проверьте файлы и добавьте специфическое логирование для каждого компонента"
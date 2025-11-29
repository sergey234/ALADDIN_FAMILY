# ALADDIN iOS - Команды для исправления ошибок

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Перейти в директорию проекта
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

### 2. Создать резервную копию
```bash
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_$(date +%Y%m%d_%H%M%S)
```

## 🔍 ДИАГНОСТИКА ПРОБЛЕМЫ

### Проверить текущие ошибки
```bash
echo "🔍 ТЕКУЩИЕ ОШИБКИ:" && xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "(error:|warning:)" | head -10
```

### Найти записи с ALADDIN/ в project.pbxproj
```bash
echo "🔍 ПОИСК ЗАПИСЕЙ С ALADDIN/:" && grep -n "ALADDIN/" ALADDIN.xcodeproj/project.pbxproj
```

### Найти записи с полными путями
```bash
echo "🔍 ПОИСК ПОЛНЫХ ПУТЕЙ:" && grep -n "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN/" ALADDIN.xcodeproj/project.pbxproj
```

### Проверить структуру файлов
```bash
echo "📁 СТРУКТУРА ФАЙЛОВ:" && echo "ViewModels: $(ls ViewModels/ | wc -l)" && echo "Core: $(find Core/ -name '*.swift' | wc -l)" && echo "Root Swift: $(ls *.swift | wc -l)"
```

## 🔧 ИСПРАВЛЕНИЕ ОШИБОК

### Исправить пути к ViewModels
```bash
echo "🔧 ИСПРАВЛЯЕМ ПУТИ К VIEWMODELS:" && sed -i '' 's|ALADDIN/ViewModels/|ViewModels/|g' ALADDIN.xcodeproj/project.pbxproj
```

### Исправить пути к Core модулям
```bash
echo "🔧 ИСПРАВЛЯЕМ ПУТИ К CORE:" && sed -i '' 's|ALADDIN/Core/|Core/|g' ALADDIN.xcodeproj/project.pbxproj
```

### Исправить пути к основным файлам
```bash
echo "🔧 ИСПРАВЛЯЕМ ОСНОВНЫЕ ФАЙЛЫ:" && sed -i '' 's|ALADDIN/ALADDINApp.swift|ALADDINApp.swift|g' ALADDIN.xcodeproj/project.pbxproj && sed -i '' 's|ALADDIN/ContentView.swift|ContentView.swift|g' ALADDIN.xcodeproj/project.pbxproj
```

### Исправить полные пути
```bash
echo "🔧 ИСПРАВЛЯЕМ ПОЛНЫЕ ПУТИ:" && sed -i '' 's|/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN/|/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/|g' ALADDIN.xcodeproj/project.pbxproj
```

## 🧹 ОЧИСТКА КЭША

### Удалить DerivedData
```bash
echo "🧹 УДАЛЯЕМ DERIVEDDATA:" && rm -rf DerivedData && rm -rf ~/Library/Developer/Xcode/DerivedData/ALADDIN-* 2>/dev/null || echo "DerivedData очищен"
```

### Очистить кэш Xcode
```bash
echo "🧹 ОЧИЩАЕМ КЭШ XCODE:" && rm -rf ~/Library/Caches/com.apple.dt.Xcode 2>/dev/null || echo "Кэш Xcode очищен"
```

### Перезапустить Xcode
```bash
echo "🔄 ПЕРЕЗАПУСКАЕМ XCODE:" && killall Xcode 2>/dev/null || echo "Xcode не запущен"
```

## 🧪 ТЕСТИРОВАНИЕ

### Собрать проект
```bash
echo "🧪 ТЕСТИРУЕМ СБОРКУ:" && xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "(error:|warning:|BUILD SUCCEEDED|BUILD FAILED)" | head -10
```

### Проверить ошибки
```bash
echo "🔍 ПРОВЕРЯЕМ ОШИБКИ:" && xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "(error:|warning:)" | head -20
```

### Запустить приложение
```bash
echo "🚀 ЗАПУСКАЕМ ПРИЛОЖЕНИЕ:" && xcrun simctl boot "iPhone 13" 2>/dev/null || echo "Симулятор уже запущен" && xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' -derivedDataPath ./DerivedData build
```

## 📊 ПРОВЕРКА РЕЗУЛЬТАТА

### Подсчитать ошибки
```bash
echo "📊 ПОДСЧЕТ ОШИБОК:" && xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -c "error:"
```

### Проверить успешность сборки
```bash
echo "📊 ПРОВЕРКА СБОРКИ:" && xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "BUILD SUCCEEDED|BUILD FAILED"
```

## 🎯 ПОЛНЫЙ АЛГОРИТМ ИСПРАВЛЕНИЯ

```bash
#!/bin/bash
# Полный алгоритм исправления ошибок ALADDIN iOS

echo "🚀 НАЧИНАЕМ ИСПРАВЛЕНИЕ ОШИБОК ALADDIN iOS"

# 1. Создать резервную копию
echo "📦 Создаем резервную копию..."
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_$(date +%Y%m%d_%H%M%S)

# 2. Диагностика
echo "🔍 Диагностика проблем..."
echo "Текущие ошибки:"
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "(error:|warning:)" | head -5

# 3. Исправление путей
echo "🔧 Исправляем пути..."
sed -i '' 's|ALADDIN/ViewModels/|ViewModels/|g' ALADDIN.xcodeproj/project.pbxproj
sed -i '' 's|ALADDIN/Core/|Core/|g' ALADDIN.xcodeproj/project.pbxproj
sed -i '' 's|ALADDIN/ALADDINApp.swift|ALADDINApp.swift|g' ALADDIN.xcodeproj/project.pbxproj
sed -i '' 's|ALADDIN/ContentView.swift|ContentView.swift|g' ALADDIN.xcodeproj/project.pbxproj
sed -i '' 's|/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN/|/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/|g' ALADDIN.xcodeproj/project.pbxproj

# 4. Очистка кэша
echo "🧹 Очищаем кэш..."
rm -rf DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/ALADDIN-* 2>/dev/null
rm -rf ~/Library/Caches/com.apple.dt.Xcode 2>/dev/null

# 5. Тестирование
echo "🧪 Тестируем сборку..."
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "(error:|warning:|BUILD SUCCEEDED|BUILD FAILED)" | head -10

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
```

## 🚨 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Всегда создавайте резервную копию** перед изменениями
2. **Проверяйте результат** после каждого этапа
3. **Не удаляйте файлы проекта** - только исправляйте пути
4. **Очищайте кэш** после изменений в project.pbxproj
5. **Тестируйте сборку** после каждого исправления

---
**Используйте эти команды последовательно для исправления всех 28 ошибок путей к файлам.**

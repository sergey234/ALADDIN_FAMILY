# 🔍 АЛГОРИТМ ПРОВЕРКИ КОНФЛИКТОВ ФАЙЛОВ

## 🎯 ЦЕЛЬ
Предотвратить конфликты файлов при добавлении новых экранов в project.pbxproj

## 📋 УНИВЕРСАЛЬНЫЙ АЛГОРИТМ (для любого экрана)

### Шаг 1: Подготовка к проверке
```bash
# Перейти в директорию проекта
cd /path/to/project

# Создать резервную копию project.pbxproj
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup
```

### Шаг 2: Проверка существующих файлов
```bash
# Заменить [SCREEN_NAME] на имя файла (например, VPNScreen)
SCREEN_NAME="VPNScreen"

# Найти все файлы с похожими именами
find . -name "*${SCREEN_NAME}*" -type f

# Проверить существование целевого файла
ls -la Screens/${SCREEN_NAME}.swift
```

### Шаг 3: Проверка конфликтов в project.pbxproj
```bash
# Проверить все упоминания файла в project.pbxproj
grep -n "${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj

# Проверить дублирование
grep -c "${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj
```

### Шаг 4: Проверка соответствия PBXFileReference и PBXBuildFile
```bash
# Найти PBXFileReference для файла
grep -A 1 -B 1 "PBXFileReference.*${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj

# Найти PBXBuildFile для файла
grep -A 1 -B 1 "PBXBuildFile.*${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj

# Проверить соответствие имен
grep -o "${SCREEN_NAME}[^\"]*" ALADDIN.xcodeproj/project.pbxproj | sort | uniq
```

### Шаг 5: Проверка путей
```bash
# Проверить корректность путей
grep -o "path = \"[^\"]*${SCREEN_NAME}[^\"]*\"" ALADDIN.xcodeproj/project.pbxproj

# Проверить отсутствие дублирования путей
grep -o "Screens/Screens/" ALADDIN.xcodeproj/project.pbxproj
```

### Шаг 6: Проверка уникальности ID
```bash
# Найти ID файла
grep -o "A[0-9A-F]\{10\}.*${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj

# Проверить уникальность ID
grep -o "A[0-9A-F]\{10\}" ALADDIN.xcodeproj/project.pbxproj | sort | uniq -d
```

## 🚨 ТИПИЧНЫЕ КОНФЛИКТЫ И РЕШЕНИЯ

### Конфликт 1: Несоответствие имен файлов
**Проблема:**
```
PBXFileReference: "Screens/FamilyScreen.swift"
PBXBuildFile: "02_FamilyScreen.swift"
```

**Решение:**
```bash
# Исправить PBXFileReference
sed -i 's/"Screens\/FamilyScreen\.swift"/"Screens\/02_FamilyScreen.swift"/g' ALADDIN.xcodeproj/project.pbxproj
```

### Конфликт 2: Дублирование путей
**Проблема:**
```
path = "Screens/Screens/FileName.swift"
```

**Решение:**
```bash
# Исправить дублирование
sed -i 's/Screens\/Screens\//Screens\//g' ALADDIN.xcodeproj/project.pbxproj
```

### Конфликт 3: Дублирование файлов
**Проблема:**
```
A3000064 /* 02_FamilyScreen.swift */ = {isa = PBXFileReference; ...};
A3000065 /* 02_FamilyScreen.swift */ = {isa = PBXFileReference; ...};
```

**Решение:**
```bash
# Удалить дублирующую запись
# Найти и удалить вторую запись вручную
```

### Конфликт 4: Неправильные пути к ресурсам
**Проблема:**
```
path = "ALADDIN/Info.plist"
path = "ALADDIN/Preview Content/Preview Assets.xcassets"
```

**Решение:**
```bash
# Исправить пути
sed -i 's/ALADDIN\/Info\.plist/Info.plist/g' ALADDIN.xcodeproj/project.pbxproj
sed -i 's/ALADDIN\/Preview Content/Preview Content/g' ALADDIN.xcodeproj/project.pbxproj
```

## 🔧 КОМАНДЫ ДЛЯ АВТОМАТИЧЕСКОЙ ПРОВЕРКИ

### Создать скрипт проверки
```bash
#!/bin/bash
# check_file_conflicts.sh

SCREEN_NAME=$1
if [ -z "$SCREEN_NAME" ]; then
    echo "Usage: $0 <SCREEN_NAME>"
    exit 1
fi

echo "🔍 Проверка конфликтов для ${SCREEN_NAME}..."

# Проверка 1: Существующие файлы
echo "📁 Проверка существующих файлов..."
find . -name "*${SCREEN_NAME}*" -type f

# Проверка 2: Конфликты в project.pbxproj
echo "📋 Проверка конфликтов в project.pbxproj..."
grep -n "${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj

# Проверка 3: Дублирование
echo "🔄 Проверка дублирования..."
count=$(grep -c "${SCREEN_NAME}" ALADDIN.xcodeproj/project.pbxproj)
if [ $count -gt 2 ]; then
    echo "⚠️  Обнаружено дублирование: $count упоминаний"
else
    echo "✅ Дублирование не обнаружено"
fi

# Проверка 4: Пути
echo "🛤️  Проверка путей..."
grep -o "path = \"[^\"]*${SCREEN_NAME}[^\"]*\"" ALADDIN.xcodeproj/project.pbxproj

echo "✅ Проверка завершена"
```

### Использование скрипта
```bash
# Сделать скрипт исполняемым
chmod +x check_file_conflicts.sh

# Проверить конкретный экран
./check_file_conflicts.sh VPNScreen
./check_file_conflicts.sh AnalyticsScreen
./check_file_conflicts.sh SettingsScreen
```

## 📊 ЧЕКЛИСТ ПРОВЕРКИ

- [ ] Резервная копия project.pbxproj создана
- [ ] Файл экрана существует
- [ ] Нет дублирующих файлов с похожими именами
- [ ] PBXFileReference и PBXBuildFile ссылаются на один файл
- [ ] Пути в project.pbxproj корректны
- [ ] Нет дублирования путей (Screens/Screens/)
- [ ] ID файла уникален
- [ ] Проект компилируется без ошибок
- [ ] Приложение запускается на симуляторе

## 🎯 РЕЗУЛЬТАТ

После выполнения всех проверок:
- ✅ Конфликты файлов устранены
- ✅ project.pbxproj корректен
- ✅ Проект компилируется
- ✅ Приложение работает

---
*Создано: 18 октября 2024*
*Версия: 1.0*
*Применимо к любому экрану iOS приложения*


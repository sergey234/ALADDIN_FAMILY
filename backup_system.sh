#!/bin/bash
# backup_system.sh - Полный бэкап системы ALADDIN

echo "🔄 Создание полного бэкапа системы ALADDIN..."

# Создание директории для бэкапа
BACKUP_DIR="ALADDIN_BACKUP_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Создана директория бэкапа: $BACKUP_DIR"

# Копирование основных файлов
echo "📋 Копирование основных файлов..."
cp -r core/ "$BACKUP_DIR/"
cp -r security/ "$BACKUP_DIR/"
cp -r scripts/ "$BACKUP_DIR/"
cp -r config/ "$BACKUP_DIR/"
cp -r tests/ "$BACKUP_DIR/"

# Копирование API файлов
echo "🔧 Копирование API файлов..."
cp dashboard_server.py "$BACKUP_DIR/"
cp elasticsearch_api.py "$BACKUP_DIR/"
cp alerts_api.py "$BACKUP_DIR/"
cp enhanced_elasticsearch_simulator.py "$BACKUP_DIR/"

# Копирование HTML файлов
echo "🌐 Копирование HTML файлов..."
cp dashboard_with_search.html "$BACKUP_DIR/"
cp search_interface.html "$BACKUP_DIR/"

# Копирование скриптов управления
echo "⚙️ Копирование скриптов управления..."
cp start_aladdin.sh "$BACKUP_DIR/"
cp stop_aladdin.sh "$BACKUP_DIR/"
cp status_aladdin.sh "$BACKUP_DIR/"

# Копирование базы данных
echo "🗄️ Копирование базы данных..."
if [ -f "aladdin_logs.db" ]; then
    cp aladdin_logs.db "$BACKUP_DIR/"
    echo "✅ База данных скопирована"
else
    echo "⚠️ База данных не найдена"
fi

# Копирование конфигурационных файлов
echo "⚙️ Копирование конфигурационных файлов..."
cp *.json "$BACKUP_DIR/" 2>/dev/null || true
cp *.txt "$BACKUP_DIR/" 2>/dev/null || true
cp *.md "$BACKUP_DIR/" 2>/dev/null || true

# Создание манифеста бэкапа
echo "📝 Создание манифеста бэкапа..."
cat > "$BACKUP_DIR/BACKUP_MANIFEST.json" << EOF
{
    "backup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_type": "full_system_backup",
    "system_version": "ALADDIN v2.0",
    "components": [
        "core",
        "security", 
        "scripts",
        "config",
        "tests",
        "dashboard_server",
        "elasticsearch_api",
        "alerts_api",
        "enhanced_elasticsearch_simulator",
        "management_scripts"
    ],
    "database_files": [
        "aladdin_logs.db"
    ],
    "backup_size": "$(du -sh "$BACKUP_DIR" | cut -f1)",
    "file_count": "$(find "$BACKUP_DIR" -type f | wc -l)"
}
EOF

# Проверка целостности бэкапа
echo "🔍 Проверка целостности бэкапа..."
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)

echo "📊 Статистика бэкапа:"
echo "   Размер: $BACKUP_SIZE"
echo "   Файлов: $FILE_COUNT"
echo "   Директория: $BACKUP_DIR"

# Проверка критических файлов
echo "✅ Проверка критических файлов..."
CRITICAL_FILES=(
    "dashboard_server.py"
    "elasticsearch_api.py" 
    "alerts_api.py"
    "enhanced_elasticsearch_simulator.py"
    "start_aladdin.sh"
    "stop_aladdin.sh"
    "status_aladdin.sh"
)

MISSING_FILES=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - ОТСУТСТВУЕТ!"
        ((MISSING_FILES++))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "🎉 Бэкап создан успешно!"
    echo "📁 Расположение: $BACKUP_DIR"
    echo "🔄 Для восстановления: cp -r $BACKUP_DIR/* ."
else
    echo "⚠️ Внимание: $MISSING_FILES критических файлов отсутствуют!"
fi

echo "✅ Бэкап завершен!"
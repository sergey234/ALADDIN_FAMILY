# 🚨 SFM Recovery Guide - Руководство по восстановлению

## Проблема
Другие чаты не видят созданные SFM скрипты в директориях.

## ✅ Решение

### 1. Универсальный скрипт (рекомендуется)
```bash
cd /Users/sergejhlystov/ALADDIN_NEW
python3 sfm_stats_universal.py
```

### 2. Быстрая проверка через shell скрипт
```bash
cd /Users/sergejhlystov/ALADDIN_NEW
./sfm_status.sh
```

### 3. Восстановление из резервной копии
```bash
cd /Users/sergejhlystov/ALADDIN_NEW
cp sfm_tools_backup/* scripts/
```

## 📁 Расположение файлов

### Основные файлы:
- `sfm_stats_universal.py` - Универсальный анализатор (работает везде)
- `sfm_status.sh` - Shell скрипт для быстрого доступа
- `sfm_tools_backup/` - Резервные копии всех скриптов

### В директории scripts/:
- `sfm_analyzer.py` - Полнофункциональный анализатор
- `sfm_quick_stats.py` - Быстрая статистика
- `sfm_status` - Алиас для быстрого доступа

## 🔧 Восстановление скриптов

Если файлы пропали, выполните:

```bash
# 1. Перейдите в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW

# 2. Восстановите из резервной копии
cp sfm_tools_backup/sfm_analyzer.py scripts/
cp sfm_tools_backup/sfm_quick_stats.py scripts/
cp sfm_tools_backup/sfm_status scripts/
cp sfm_tools_backup/README_SFM.md scripts/
cp sfm_tools_backup/SFM_ANALYZER_GUIDE.md docs/

# 3. Сделайте исполняемыми
chmod +x scripts/sfm_status
chmod +x sfm_status.sh
```

## 🚀 Быстрый тест

```bash
# Тест универсального скрипта
python3 sfm_stats_universal.py

# Тест shell скрипта
./sfm_status.sh

# Тест из scripts/
python3 scripts/sfm_quick_stats.py
```

## 📊 Ожидаемый результат

```
📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM
==================================================
Версия реестра: 2.0
Обновлено: 2025-09-19T11:15:09.574333
Файл: /Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json

Параметр                Значение        Процент
--------------------------------------------------
Всего функций           330             100.0%
Активные                22              6.7%
Спящие                  289             87.6%
Работающие              19              5.8%
Критические             262             79.4%
```

## 🎯 Рекомендации

1. **Используйте универсальный скрипт** - он работает из любой директории
2. **Сохраняйте резервные копии** - они находятся в `sfm_tools_backup/`
3. **Проверяйте права доступа** - используйте `chmod +x` для исполняемых файлов
4. **Тестируйте после восстановления** - убедитесь, что все работает

## 🔍 Диагностика проблем

### Файл реестра не найден:
```bash
find /Users/sergejhlystov -name "function_registry.json" -type f
```

### Скрипты не исполняются:
```bash
chmod +x sfm_status.sh
chmod +x scripts/sfm_status
```

### Ошибки Python:
```bash
python3 -c "import json; print('Python работает')"
```

---
**Создано:** 2025-09-19  
**Версия:** 1.0  
**Статус:** Готово к использованию
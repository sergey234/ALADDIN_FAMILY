# 📊 SFM Analyzer - Руководство по использованию

## Описание

SFM Analyzer - это набор инструментов для анализа реестра функций SFM (System Function Manager). Позволяет получать актуальную статистику по функциям в системе безопасности ALADDIN.

## 🚀 Быстрый старт

### 1. Быстрая статистика (рекомендуется)
```bash
cd /Users/sergejhlystov/ALADDIN_NEW
python3 scripts/sfm_quick_stats.py
```

### 2. Через алиас (еще быстрее)
```bash
cd /Users/sergejhlystov/ALADDIN_NEW
./scripts/sfm_status
```

## 📋 Доступные скрипты

### 1. `sfm_quick_stats.py` - Быстрая статистика
**Назначение:** Получение основной статистики SFM одной командой

**Использование:**
```bash
python3 scripts/sfm_quick_stats.py
```

**Вывод:**
- Общее количество функций
- Количество активных функций
- Количество спящих функций  
- Количество работающих функций
- Количество критических функций
- Проценты для каждого показателя

### 2. `sfm_analyzer.py` - Полнофункциональный анализатор
**Назначение:** Детальный анализ реестра функций с различными опциями

**Основные команды:**

#### Базовая статистика
```bash
python3 scripts/sfm_analyzer.py
```

#### Детальная статистика
```bash
python3 scripts/sfm_analyzer.py --detailed
# или
python3 scripts/sfm_analyzer.py -d
```

#### Функции по статусу
```bash
# Показать все активные функции
python3 scripts/sfm_analyzer.py --status active

# Показать все спящие функции
python3 scripts/sfm_analyzer.py --status sleeping

# Показать все работающие функции
python3 scripts/sfm_analyzer.py --status running
```

#### Экспорт в CSV
```bash
python3 scripts/sfm_analyzer.py --export csv
# или
python3 scripts/sfm_analyzer.py -e csv
```

#### Указать другой файл реестра
```bash
python3 scripts/sfm_analyzer.py --registry path/to/other/registry.json
```

### 3. `sfm_status` - Алиас для быстрого доступа
**Назначение:** Максимально быстрое получение статистики

**Использование:**
```bash
./scripts/sfm_status
```

## 📊 Примеры вывода

### Базовая статистика
```
📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM
========================================
Обновлено: 2025-09-19T11:15:09.574333

Параметр                Значение        Процент
----------------------------------------
Всего функций           330             100.0%
Активные                22              6.7%
Спящие                  289             87.6%
Работающие              19              5.8%
Критические             262             79.4%
```

### Детальная статистика
```
📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM
==================================================
Версия реестра: 2.0
Последнее обновление: 2025-09-19T11:15:09.574333

Параметр                Значение        Процент
--------------------------------------------------
Всего функций           330             100.0%
Активные                22              6.7%
Спящие                  289             87.6%
Работающие              19              5.8%

==================================================
📈 ДЕТАЛЬНАЯ СТАТИСТИКА
==================================================

🔴 Критические функции: 262 (79.4%)
🔄 Автоматически включаемые: 6 (1.8%)
🚨 Экстренное пробуждение: 261 (79.1%)

📋 Топ-5 типов функций:
  unknown: 208 (63.0%)
  manager: 24 (7.3%)
  ai_agent: 23 (7.0%)
  bot: 20 (6.1%)
  security: 19 (5.8%)

🛡️ Уровни безопасности:
  medium: 290 (87.9%)
  high: 34 (10.3%)
  critical: 5 (1.5%)
  low: 1 (0.3%)
```

## 🔧 Настройка и кастомизация

### Изменение пути к реестру
По умолчанию скрипты ищут реестр по пути `data/sfm/function_registry.json`. 
Чтобы использовать другой файл:

```bash
python3 scripts/sfm_analyzer.py --registry /path/to/your/registry.json
```

### Создание собственного алиаса
Добавьте в ваш `.bashrc` или `.zshrc`:

```bash
alias sfm-stats="cd /Users/sergejhlystov/ALADDIN_NEW && python3 scripts/sfm_quick_stats.py"
alias sfm-detail="cd /Users/sergejhlystov/ALADDIN_NEW && python3 scripts/sfm_analyzer.py --detailed"
alias sfm-active="cd /Users/sergejhlystov/ALADDIN_NEW && python3 scripts/sfm_analyzer.py --status active"
```

## 📈 Автоматизация

### Получение статистики в скриптах
```python
import sys
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')
from scripts.sfm_analyzer import SFMAnalyzer

# Создаем анализатор
analyzer = SFMAnalyzer()

# Получаем быструю статистику
stats = analyzer.get_quick_stats()
print(f"Активных функций: {stats['active']}")

# Получаем детальную статистику
detailed_stats = analyzer.get_detailed_stats()
print(f"Критических функций: {detailed_stats['critical_functions']}")
```

### Мониторинг изменений
```bash
# Запуск каждые 5 минут
watch -n 300 "cd /Users/sergejhlystov/ALADDIN_NEW && python3 scripts/sfm_quick_stats.py"
```

## 🚨 Устранение неполадок

### Ошибка "Файл реестра не найден"
```bash
# Проверьте путь к файлу
ls -la data/sfm/function_registry.json

# Если файл не существует, проверьте правильность пути
find . -name "function_registry.json" -type f
```

### Ошибка "Ошибка парсинга JSON"
```bash
# Проверьте корректность JSON файла
python3 -m json.tool data/sfm/function_registry.json > /dev/null
```

### Ошибка "Permission denied" для алиаса
```bash
# Сделайте скрипт исполняемым
chmod +x scripts/sfm_status
```

## 📝 Логи и отладка

### Включение отладочного режима
```bash
# Добавьте в начало скрипта для отладки
export PYTHONPATH="/Users/sergejhlystov/ALADDIN_NEW:$PYTHONPATH"
python3 -u scripts/sfm_analyzer.py --detailed
```

## 🎯 Рекомендации по использованию

1. **Для ежедневного мониторинга:** используйте `sfm_quick_stats.py`
2. **Для детального анализа:** используйте `sfm_analyzer.py --detailed`
3. **Для поиска конкретных функций:** используйте `--status`
4. **Для отчетов:** используйте `--export csv`
5. **Для автоматизации:** импортируйте класс `SFMAnalyzer`

## 📞 Поддержка

При возникновении проблем:
1. Проверьте путь к файлу реестра
2. Убедитесь в корректности JSON
3. Проверьте права доступа к файлам
4. Обратитесь к логам системы

---

**Создано:** 2025-09-19  
**Версия:** 1.0  
**Автор:** ALADDIN Security System
# 📋 ОТЧЕТ #23: export_manager.py

**Дата анализа:** 2025-09-16T00:06:45.620728
**Категория:** OTHER
**Статус:** ❌ 93 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 93
- **Тип файла:** OTHER
- **Путь к файлу:** `export_manager.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 61 ошибок - Пробелы в пустых строках
- **E501:** 22 ошибок - Длинные строки (>79 символов)
- **F401:** 6 ошибок - Неиспользуемые импорты
- **E402:** 3 ошибок - Импорты не в начале файла
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
export_manager.py:18:1: F401 'dataclasses.asdict' imported but unused
export_manager.py:19:1: F401 'io' imported but unused
export_manager.py:24:1: E402 module level import not at top of file
export_manager.py:25:1: E402 module level import not at top of file
export_manager.py:26:1: F401 'elasticsearch_simulator.ElasticsearchSimulator' imported but unused
export_manager.py:26:1: E402 module level import not at top of file
export_manager.py:29:5: F401 'reportlab.lib.pagesizes.letter' imported but unused
export_manager.py:31:5: F401 'reportlab.lib.units.inch' imported but unused
export_manager.py:32:80: E501 line too long (90 > 79 characters)
export_manager.py:34:5: F401 'reportlab.lib.enums.TA_LEFT' imported but unused
export_manager.py:43:1: W293 blank line contains whitespace
export_manager.py:50:1: W293 blank line contains whitespace
export_manager.py:56:1: W293 blank line contains whitespace
export_manager.py:57:80: E501 line too long (91 > 79 characters)
export_manager.py:63:1: W29
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:45.620902  
**Функция #23**

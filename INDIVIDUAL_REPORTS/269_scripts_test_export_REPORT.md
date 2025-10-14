# 📋 ОТЧЕТ #269: scripts/test_export.py

**Дата анализа:** 2025-09-16T00:08:29.421991
**Категория:** SCRIPT
**Статус:** ❌ 47 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 47
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/test_export.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 30 ошибок - Пробелы в пустых строках
- **E501:** 12 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E402:** 2 ошибок - Импорты не в начале файла
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/test_export.py:13:1: F401 'json' imported but unused
scripts/test_export.py:22:1: E402 module level import not at top of file
scripts/test_export.py:23:1: F401 'elasticsearch_simulator.ElasticsearchSimulator' imported but unused
scripts/test_export.py:23:1: E402 module level import not at top of file
scripts/test_export.py:32:1: W293 blank line contains whitespace
scripts/test_export.py:35:1: W293 blank line contains whitespace
scripts/test_export.py:51:80: E501 line too long (91 > 79 characters)
scripts/test_export.py:59:80: E501 line too long (92 > 79 characters)
scripts/test_export.py:63:1: W293 blank line contains whitespace
scripts/test_export.py:68:1: W293 blank line contains whitespace
scripts/test_export.py:72:1: W293 blank line contains whitespace
scripts/test_export.py:79:1: W293 blank line contains whitespace
scripts/test_export.py:84:80: E501 line too long (103 > 79 characters)
scripts/test_export.py:88:80: E501 line too long (80 > 79 characters)
scripts/test_export
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:29.422100  
**Функция #269**

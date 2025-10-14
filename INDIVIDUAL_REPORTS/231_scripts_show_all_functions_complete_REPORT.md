# 📋 ОТЧЕТ #231: scripts/show_all_functions_complete.py

**Дата анализа:** 2025-09-16T00:08:13.364851
**Категория:** SCRIPT
**Статус:** ❌ 99 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 99
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/show_all_functions_complete.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W291:** 65 ошибок - Пробелы в конце строки
- **W293:** 21 ошибок - Пробелы в пустых строках
- **E501:** 8 ошибок - Длинные строки (>79 символов)
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/show_all_functions_complete.py:9:1: F401 'os' imported but unused
scripts/show_all_functions_complete.py:15:1: E302 expected 2 blank lines, found 1
scripts/show_all_functions_complete.py:21:1: W293 blank line contains whitespace
scripts/show_all_functions_complete.py:26:32: W291 trailing whitespace
scripts/show_all_functions_complete.py:35:35: W291 trailing whitespace
scripts/show_all_functions_complete.py:44:36: W291 trailing whitespace
scripts/show_all_functions_complete.py:53:32: W291 trailing whitespace
scripts/show_all_functions_complete.py:62:37: W291 trailing whitespace
scripts/show_all_functions_complete.py:71:37: W291 trailing whitespace
scripts/show_all_functions_complete.py:80:38: W291 trailing whitespace
scripts/show_all_functions_complete.py:88:1: W293 blank line contains whitespace
scripts/show_all_functions_complete.py:93:46: W291 trailing whitespace
scripts/show_all_functions_complete.py:102:40: W291 trailing whitespace
scripts/show_all_functions_complete.py:111
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:13.365086  
**Функция #231**

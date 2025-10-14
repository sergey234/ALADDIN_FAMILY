# 📋 ОТЧЕТ #2: analyze_all_files.py

**Дата анализа:** 2025-09-16T00:06:37.609071
**Категория:** OTHER
**Статус:** ❌ 33 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 33
- **Тип файла:** OTHER
- **Путь к файлу:** `analyze_all_files.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 17 ошибок - Пробелы в пустых строках
- **E501:** 6 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E302:** 2 ошибок - Недостаточно пустых строк
- **W291:** 2 ошибок - Пробелы в конце строки
- **F541:** 2 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
analyze_all_files.py:7:1: F401 'sys' imported but unused
analyze_all_files.py:9:1: F401 'pathlib.Path' imported but unused
analyze_all_files.py:11:1: E302 expected 2 blank lines, found 1
analyze_all_files.py:16:39: W291 trailing whitespace
analyze_all_files.py:19:80: E501 line too long (82 > 79 characters)
analyze_all_files.py:20:1: W293 blank line contains whitespace
analyze_all_files.py:28:1: W293 blank line contains whitespace
analyze_all_files.py:33:1: W293 blank line contains whitespace
analyze_all_files.py:45:1: W293 blank line contains whitespace
analyze_all_files.py:52:1: W293 blank line contains whitespace
analyze_all_files.py:61:1: E302 expected 2 blank lines, found 1
analyze_all_files.py:65:1: W293 blank line contains whitespace
analyze_all_files.py:70:1: W293 blank line contains whitespace
analyze_all_files.py:71:58: W291 trailing whitespace
analyze_all_files.py:72:80: E501 line too long (92 > 79 characters)
analyze_all_files.py:73:1: W293 blank line contains whitespace
ana
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:37.609306  
**Функция #2**

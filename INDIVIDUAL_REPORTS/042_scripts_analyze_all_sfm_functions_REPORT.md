# 📋 ОТЧЕТ #42: scripts/analyze_all_sfm_functions.py

**Дата анализа:** 2025-09-16T00:06:52.870913
**Категория:** SCRIPT
**Статус:** ❌ 39 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 39
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/analyze_all_sfm_functions.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 13 ошибок - Пробелы в пустых строках
- **W291:** 10 ошибок - Пробелы в конце строки
- **F541:** 10 ошибок - f-строки без плейсхолдеров
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **E302:** 2 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/analyze_all_sfm_functions.py:11:80: E501 line too long (82 > 79 characters)
scripts/analyze_all_sfm_functions.py:13:1: E302 expected 2 blank lines, found 1
scripts/analyze_all_sfm_functions.py:18:80: E501 line too long (82 > 79 characters)
scripts/analyze_all_sfm_functions.py:38:1: E302 expected 2 blank lines, found 1
scripts/analyze_all_sfm_functions.py:43:1: W293 blank line contains whitespace
scripts/analyze_all_sfm_functions.py:54:33: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:62:40: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:70:63: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:78:32: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:90:36: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:98:63: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:111:42: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:120:32: W291 trailing whitespace
scripts/analyze_all_sfm_functions.py:12
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:52.871070  
**Функция #42**

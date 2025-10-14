# 📋 ОТЧЕТ #299: scripts/test_singapore_direct.py

**Дата анализа:** 2025-09-16T00:08:40.809078
**Категория:** SCRIPT
**Статус:** ❌ 22 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 22
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/test_singapore_direct.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 15 ошибок - Пробелы в пустых строках
- **E501:** 3 ошибок - Длинные строки (>79 символов)
- **E302:** 2 ошибок - Недостаточно пустых строк
- **E402:** 1 ошибок - Импорты не в начале файла
- **W291:** 1 ошибок - Пробелы в конце строки

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк

### 📝 Детальный вывод flake8:

```
scripts/test_singapore_direct.py:17:1: E402 module level import not at top of file
scripts/test_singapore_direct.py:17:80: E501 line too long (80 > 79 characters)
scripts/test_singapore_direct.py:23:1: E302 expected 2 blank lines, found 1
scripts/test_singapore_direct.py:27:1: W293 blank line contains whitespace
scripts/test_singapore_direct.py:33:1: W293 blank line contains whitespace
scripts/test_singapore_direct.py:38:1: W293 blank line contains whitespace
scripts/test_singapore_direct.py:44:1: W293 blank line contains whitespace
scripts/test_singapore_direct.py:48:1: W293 blank line contains whitespace
scripts/test_singapore_direct.py:51:23: W291 trailing whitespace
scripts/test_singapore_direct.py:55:1: W293 blank line contains whitespace
scripts/test_singapore_direct.py:59:80: E501 line too long (83 > 79 characters)
scripts/test_singapore_direct.py:60:80: E501 line too long (88 > 79 characters)
scripts/test_singapore_direct.py:61:1: W293 blank line contains whitespace
scripts/tes
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:40.809199  
**Функция #299**

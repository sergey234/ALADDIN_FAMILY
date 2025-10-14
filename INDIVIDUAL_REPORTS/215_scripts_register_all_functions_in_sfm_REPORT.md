# 📋 ОТЧЕТ #215: scripts/register_all_functions_in_sfm.py

**Дата анализа:** 2025-09-16T00:08:07.031190
**Категория:** SCRIPT
**Статус:** ❌ 35 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 35
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/register_all_functions_in_sfm.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 21 ошибок - Пробелы в пустых строках
- **E501:** 5 ошибок - Длинные строки (>79 символов)
- **F541:** 4 ошибок - f-строки без плейсхолдеров
- **E402:** 1 ошибок - Импорты не в начале файла
- **E302:** 1 ошибок - Недостаточно пустых строк
- **W291:** 1 ошибок - Пробелы в конце строки
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/register_all_functions_in_sfm.py:10:80: E501 line too long (82 > 79 characters)
scripts/register_all_functions_in_sfm.py:12:1: E402 module level import not at top of file
scripts/register_all_functions_in_sfm.py:12:80: E501 line too long (93 > 79 characters)
scripts/register_all_functions_in_sfm.py:14:1: E302 expected 2 blank lines, found 1
scripts/register_all_functions_in_sfm.py:19:1: W293 blank line contains whitespace
scripts/register_all_functions_in_sfm.py:23:1: W293 blank line contains whitespace
scripts/register_all_functions_in_sfm.py:38:34: W291 trailing whitespace
scripts/register_all_functions_in_sfm.py:63:1: W293 blank line contains whitespace
scripts/register_all_functions_in_sfm.py:110:1: W293 blank line contains whitespace
scripts/register_all_functions_in_sfm.py:139:1: W293 blank line contains whitespace
scripts/register_all_functions_in_sfm.py:150:1: W293 blank line contains whitespace
scripts/register_all_functions_in_sfm.py:179:1: W293 blank line contains wh
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:07.031353  
**Функция #215**

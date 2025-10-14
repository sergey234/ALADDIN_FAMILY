# 📋 ОТЧЕТ #294: scripts/test_sfm_debug.py

**Дата анализа:** 2025-09-16T00:08:38.813649
**Категория:** SCRIPT
**Статус:** ❌ 8 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 8
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/test_sfm_debug.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E501:** 3 ошибок - Длинные строки (>79 символов)
- **W293:** 2 ошибок - Пробелы в пустых строках
- **E402:** 1 ошибок - Импорты не в начале файла
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках

### 📝 Детальный вывод flake8:

```
scripts/test_sfm_debug.py:11:1: E402 module level import not at top of file
scripts/test_sfm_debug.py:13:80: E501 line too long (104 > 79 characters)
scripts/test_sfm_debug.py:15:1: E302 expected 2 blank lines, found 1
scripts/test_sfm_debug.py:28:1: E305 expected 2 blank lines after class or function definition, found 1
scripts/test_sfm_debug.py:29:80: E501 line too long (87 > 79 characters)
scripts/test_sfm_debug.py:39:1: W293 blank line contains whitespace
scripts/test_sfm_debug.py:41:80: E501 line too long (89 > 79 characters)
scripts/test_sfm_debug.py:48:1: W293 blank line contains whitespace
1     E302 expected 2 blank lines, found 1
1     E305 expected 2 blank lines after class or function definition, found 1
1     E402 module level import not at top of file
3     E501 line too long (104 > 79 characters)
2     W293 blank line contains whitespace

```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:38.813746  
**Функция #294**

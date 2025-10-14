# 📋 ОТЧЕТ #56: scripts/check_all_preliminary_functions.py

**Дата анализа:** 2025-09-16T00:06:57.542498
**Категория:** SCRIPT
**Статус:** ❌ 22 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 22
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/check_all_preliminary_functions.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 8 ошибок - Пробелы в пустых строках
- **E501:** 6 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E402:** 2 ошибок - Импорты не в начале файла
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E701:** 1 ошибок - Ошибка E701
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/check_all_preliminary_functions.py:8:1: F401 'typing.Dict' imported but unused
scripts/check_all_preliminary_functions.py:8:1: F401 'typing.Any' imported but unused
scripts/check_all_preliminary_functions.py:10:80: E501 line too long (82 > 79 characters)
scripts/check_all_preliminary_functions.py:12:1: E402 module level import not at top of file
scripts/check_all_preliminary_functions.py:13:1: E402 module level import not at top of file
scripts/check_all_preliminary_functions.py:15:1: E302 expected 2 blank lines, found 1
scripts/check_all_preliminary_functions.py:18:1: W293 blank line contains whitespace
scripts/check_all_preliminary_functions.py:21:1: W293 blank line contains whitespace
scripts/check_all_preliminary_functions.py:23:1: W293 blank line contains whitespace
scripts/check_all_preliminary_functions.py:25:80: E501 line too long (98 > 79 characters)
scripts/check_all_preliminary_functions.py:26:80: E501 line too long (81 > 79 characters)
scripts/check_all_preliminary_
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:57.542621  
**Функция #56**

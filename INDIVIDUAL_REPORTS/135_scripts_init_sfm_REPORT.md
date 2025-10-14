# 📋 ОТЧЕТ #135: scripts/init_sfm.py

**Дата анализа:** 2025-09-16T00:07:24.928448
**Категория:** SCRIPT
**Статус:** ❌ 28 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 28
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/init_sfm.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 15 ошибок - Пробелы в пустых строках
- **E501:** 4 ошибок - Длинные строки (>79 символов)
- **F541:** 3 ошибок - f-строки без плейсхолдеров
- **E402:** 2 ошибок - Импорты не в начале файла
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/init_sfm.py:8:1: F401 'os' imported but unused
scripts/init_sfm.py:11:1: E402 module level import not at top of file
scripts/init_sfm.py:12:1: E402 module level import not at top of file
scripts/init_sfm.py:14:1: E302 expected 2 blank lines, found 1
scripts/init_sfm.py:19:1: W293 blank line contains whitespace
scripts/init_sfm.py:24:1: W293 blank line contains whitespace
scripts/init_sfm.py:28:1: W293 blank line contains whitespace
scripts/init_sfm.py:34:1: W293 blank line contains whitespace
scripts/init_sfm.py:38:1: W293 blank line contains whitespace
scripts/init_sfm.py:42:1: W293 blank line contains whitespace
scripts/init_sfm.py:43:15: F541 f-string is missing placeholders
scripts/init_sfm.py:45:1: W293 blank line contains whitespace
scripts/init_sfm.py:47:15: F541 f-string is missing placeholders
scripts/init_sfm.py:49:1: W293 blank line contains whitespace
scripts/init_sfm.py:57:1: W293 blank line contains whitespace
scripts/init_sfm.py:59:80: E501 line too long (94 > 79
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:24.928591  
**Функция #135**

# 📋 ОТЧЕТ #225: scripts/setup_russian_apis.py

**Дата анализа:** 2025-09-16T00:08:10.989035
**Категория:** SCRIPT
**Статус:** ❌ 32 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 32
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/setup_russian_apis.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 25 ошибок - Пробелы в пустых строках
- **E302:** 3 ошибок - Недостаточно пустых строк
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E501:** 1 ошибок - Длинные строки (>79 символов)
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/setup_russian_apis.py:8:1: F401 'sys' imported but unused
scripts/setup_russian_apis.py:10:1: E302 expected 2 blank lines, found 1
scripts/setup_russian_apis.py:14:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:23:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:25:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:29:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:32:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:39:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:42:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:45:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:48:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:51:1: W293 blank line contains whitespace
scripts/setup_russian_apis.py:56:1: E302 expected 2 blank lines, found 1
scripts/setup_russian_apis.py:60:1: W293 blank line contains whitesp
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:10.989275  
**Функция #225**

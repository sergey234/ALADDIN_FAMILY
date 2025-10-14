# 📋 ОТЧЕТ #91: scripts/deep_test_managers.py

**Дата анализа:** 2025-09-16T00:07:09.764643
**Категория:** SCRIPT
**Статус:** ❌ 161 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 161
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/deep_test_managers.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 84 ошибок - Пробелы в пустых строках
- **E501:** 33 ошибок - Длинные строки (>79 символов)
- **F541:** 18 ошибок - f-строки без плейсхолдеров
- **E302:** 8 ошибок - Недостаточно пустых строк
- **F841:** 7 ошибок - Неиспользуемые переменные
- **F401:** 6 ошибок - Неиспользуемые импорты
- **E261:** 2 ошибок - Ошибка E261
- **W291:** 1 ошибок - Пробелы в конце строки
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F841:** Удалить неиспользуемые переменные
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/deep_test_managers.py:18:1: F401 'asyncio' imported but unused
scripts/deep_test_managers.py:20:1: F401 'pandas as pd' imported but unused
scripts/deep_test_managers.py:21:1: F401 'datetime.timedelta' imported but unused
scripts/deep_test_managers.py:22:1: F401 'typing.Dict' imported but unused
scripts/deep_test_managers.py:22:1: F401 'typing.Any' imported but unused
scripts/deep_test_managers.py:22:1: F401 'typing.List' imported but unused
scripts/deep_test_managers.py:27:1: E302 expected 2 blank lines, found 1
scripts/deep_test_managers.py:31:1: W293 blank line contains whitespace
scripts/deep_test_managers.py:34:1: W293 blank line contains whitespace
scripts/deep_test_managers.py:44:1: W293 blank line contains whitespace
scripts/deep_test_managers.py:54:1: W293 blank line contains whitespace
scripts/deep_test_managers.py:64:1: W293 blank line contains whitespace
scripts/deep_test_managers.py:74:1: W293 blank line contains whitespace
scripts/deep_test_managers.py:84:1: W293 b
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:09.764849  
**Функция #91**

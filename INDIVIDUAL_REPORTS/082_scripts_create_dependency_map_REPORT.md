# 📋 ОТЧЕТ #82: scripts/create_dependency_map.py

**Дата анализа:** 2025-09-16T00:07:06.929467
**Категория:** SCRIPT
**Статус:** ❌ 118 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 118
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/create_dependency_map.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 75 ошибок - Пробелы в пустых строках
- **E501:** 33 ошибок - Длинные строки (>79 символов)
- **F401:** 3 ошибок - Неиспользуемые импорты
- **E302:** 2 ошибок - Недостаточно пустых строк
- **F541:** 2 ошибок - f-строки без плейсхолдеров
- **W291:** 1 ошибок - Пробелы в конце строки
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
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/create_dependency_map.py:10:1: F401 'ast' imported but unused
scripts/create_dependency_map.py:13:1: F401 'pathlib.Path' imported but unused
scripts/create_dependency_map.py:14:1: F401 'typing.Set' imported but unused
scripts/create_dependency_map.py:20:1: E302 expected 2 blank lines, found 1
scripts/create_dependency_map.py:22:1: W293 blank line contains whitespace
scripts/create_dependency_map.py:35:1: W293 blank line contains whitespace
scripts/create_dependency_map.py:39:80: E501 line too long (85 > 79 characters)
scripts/create_dependency_map.py:44:1: W293 blank line contains whitespace
scripts/create_dependency_map.py:48:1: W293 blank line contains whitespace
scripts/create_dependency_map.py:49:80: E501 line too long (89 > 79 characters)
scripts/create_dependency_map.py:52:1: W293 blank line contains whitespace
scripts/create_dependency_map.py:55:1: W293 blank line contains whitespace
scripts/create_dependency_map.py:57:1: W293 blank line contains whitespace
scripts/creat
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:06.929696  
**Функция #82**

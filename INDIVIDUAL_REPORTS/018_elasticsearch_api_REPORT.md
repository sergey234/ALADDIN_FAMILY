# 📋 ОТЧЕТ #18: elasticsearch_api.py

**Дата анализа:** 2025-09-16T00:06:43.709224
**Категория:** OTHER
**Статус:** ❌ 50 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 50
- **Тип файла:** OTHER
- **Путь к файлу:** `elasticsearch_api.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 27 ошибок - Пробелы в пустых строках
- **E302:** 11 ошибок - Недостаточно пустых строк
- **F401:** 7 ошибок - Неиспользуемые импорты
- **E501:** 3 ошибок - Длинные строки (>79 символов)
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
elasticsearch_api.py:12:1: F401 'json' imported but unused
elasticsearch_api.py:13:1: F401 'time' imported but unused
elasticsearch_api.py:14:1: F401 'datetime.timedelta' imported but unused
elasticsearch_api.py:15:1: F401 'typing.Dict' imported but unused
elasticsearch_api.py:15:1: F401 'typing.List' imported but unused
elasticsearch_api.py:15:1: F401 'typing.Any' imported but unused
elasticsearch_api.py:15:1: F401 'typing.Optional' imported but unused
elasticsearch_api.py:27:1: E302 expected 2 blank lines, found 1
elasticsearch_api.py:46:1: E302 expected 2 blank lines, found 1
elasticsearch_api.py:57:80: E501 line too long (86 > 79 characters)
elasticsearch_api.py:58:1: W293 blank line contains whitespace
elasticsearch_api.py:66:1: W293 blank line contains whitespace
elasticsearch_api.py:77:1: W293 blank line contains whitespace
elasticsearch_api.py:79:1: W293 blank line contains whitespace
elasticsearch_api.py:87:1: E302 expected 2 blank lines, found 1
elasticsearch_api.py:93:1: W29
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:43.709349  
**Функция #18**

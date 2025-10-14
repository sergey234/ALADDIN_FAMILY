# 📋 ОТЧЕТ #28: monitoring_api_server.py

**Дата анализа:** 2025-09-16T00:06:47.404707
**Категория:** OTHER
**Статус:** ❌ 50 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 50
- **Тип файла:** OTHER
- **Путь к файлу:** `monitoring_api_server.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 27 ошибок - Пробелы в пустых строках
- **E501:** 10 ошибок - Длинные строки (>79 символов)
- **E302:** 10 ошибок - Недостаточно пустых строк
- **F401:** 1 ошибок - Неиспользуемые импорты
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
monitoring_api_server.py:9:80: E501 line too long (119 > 79 characters)
monitoring_api_server.py:12:1: F401 'json' imported but unused
monitoring_api_server.py:18:1: E302 expected 2 blank lines, found 1
monitoring_api_server.py:33:1: E302 expected 2 blank lines, found 1
monitoring_api_server.py:39:1: W293 blank line contains whitespace
monitoring_api_server.py:41:1: W293 blank line contains whitespace
monitoring_api_server.py:42:80: E501 line too long (87 > 79 characters)
monitoring_api_server.py:48:1: W293 blank line contains whitespace
monitoring_api_server.py:53:1: E302 expected 2 blank lines, found 1
monitoring_api_server.py:59:1: W293 blank line contains whitespace
monitoring_api_server.py:62:1: W293 blank line contains whitespace
monitoring_api_server.py:64:1: W293 blank line contains whitespace
monitoring_api_server.py:65:80: E501 line too long (83 > 79 characters)
monitoring_api_server.py:71:1: W293 blank line contains whitespace
monitoring_api_server.py:76:1: E302 expected 2 b
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:47.404930  
**Функция #28**

# 📋 ОТЧЕТ #186: scripts/put_incident_response_to_sleep.py

**Дата анализа:** 2025-09-16T00:07:57.031768
**Категория:** SCRIPT
**Статус:** ❌ 33 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 33
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/put_incident_response_to_sleep.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 19 ошибок - Пробелы в пустых строках
- **E501:** 11 ошибок - Длинные строки (>79 символов)
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
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
scripts/put_incident_response_to_sleep.py:8:1: F401 'sys' imported but unused
scripts/put_incident_response_to_sleep.py:13:1: E302 expected 2 blank lines, found 1
scripts/put_incident_response_to_sleep.py:17:1: W293 blank line contains whitespace
scripts/put_incident_response_to_sleep.py:24:1: W293 blank line contains whitespace
scripts/put_incident_response_to_sleep.py:26:1: W293 blank line contains whitespace
scripts/put_incident_response_to_sleep.py:30:1: W293 blank line contains whitespace
scripts/put_incident_response_to_sleep.py:36:80: E501 line too long (83 > 79 characters)
scripts/put_incident_response_to_sleep.py:41:1: W293 blank line contains whitespace
scripts/put_incident_response_to_sleep.py:42:80: E501 line too long (89 > 79 characters)
scripts/put_incident_response_to_sleep.py:43:80: E501 line too long (91 > 79 characters)
scripts/put_incident_response_to_sleep.py:44:1: W293 blank line contains whitespace
scripts/put_incident_response_to_sleep.py:48:1: W293 blank line co
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:57.032001  
**Функция #186**

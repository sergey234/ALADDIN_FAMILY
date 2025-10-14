# 📋 ОТЧЕТ #173: scripts/put_api_gateway_to_sleep.py

**Дата анализа:** 2025-09-16T00:07:51.642345
**Категория:** SCRIPT
**Статус:** ❌ 25 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 25
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/put_api_gateway_to_sleep.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 15 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/put_api_gateway_to_sleep.py:16:1: E302 expected 2 blank lines, found 1
scripts/put_api_gateway_to_sleep.py:20:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:24:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:30:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:33:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:39:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:72:80: E501 line too long (83 > 79 characters)
scripts/put_api_gateway_to_sleep.py:74:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:77:80: E501 line too long (80 > 79 characters)
scripts/put_api_gateway_to_sleep.py:78:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:81:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:83:1: W293 blank line contains whitespace
scripts/put_api_gateway_to_sleep.py:86:80: E501 line 
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:51.642563  
**Функция #173**

# 📋 ОТЧЕТ #196: scripts/put_smart_notification_to_sleep.py

**Дата анализа:** 2025-09-16T00:08:00.486783
**Категория:** SCRIPT
**Статус:** ❌ 46 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 46
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/put_smart_notification_to_sleep.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 29 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **F541:** 7 ошибок - f-строки без плейсхолдеров
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/put_smart_notification_to_sleep.py:17:1: E302 expected 2 blank lines, found 1
scripts/put_smart_notification_to_sleep.py:21:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:27:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:29:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:33:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:37:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:41:80: E501 line too long (99 > 79 characters)
scripts/put_smart_notification_to_sleep.py:42:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:43:11: F541 f-string is missing placeholders
scripts/put_smart_notification_to_sleep.py:47:1: W293 blank line contains whitespace
scripts/put_smart_notification_to_sleep.py:55:80: E501 line too long (95 > 79 characters)
scripts/put_smart_notification_to_sleep.py:56:80: E
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:00.486898  
**Функция #196**

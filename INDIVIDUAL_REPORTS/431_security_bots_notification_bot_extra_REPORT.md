# 📋 ОТЧЕТ #431: security/bots/notification_bot_extra.py

**Дата анализа:** 2025-09-16T00:09:45.500897
**Категория:** BOT
**Статус:** ❌ 39 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 39
- **Тип файла:** BOT
- **Путь к файлу:** `security/bots/notification_bot_extra.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 23 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **F401:** 4 ошибок - Неиспользуемые импорты
- **E302:** 3 ошибок - Недостаточно пустых строк
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
security/bots/notification_bot_extra.py:7:1: F401 'asyncio' imported but unused
security/bots/notification_bot_extra.py:9:1: F401 'time' imported but unused
security/bots/notification_bot_extra.py:11:1: F401 'typing.List' imported but unused
security/bots/notification_bot_extra.py:11:1: F401 'typing.Optional' imported but unused
security/bots/notification_bot_extra.py:14:1: E302 expected 2 blank lines, found 1
security/bots/notification_bot_extra.py:24:1: E302 expected 2 blank lines, found 1
security/bots/notification_bot_extra.py:33:1: W293 blank line contains whitespace
security/bots/notification_bot_extra.py:38:1: E302 expected 2 blank lines, found 1
security/bots/notification_bot_extra.py:40:1: W293 blank line contains whitespace
security/bots/notification_bot_extra.py:51:1: W293 blank line contains whitespace
security/bots/notification_bot_extra.py:58:80: E501 line too long (81 > 79 characters)
security/bots/notification_bot_extra.py:72:1: W293 blank line contains whitespace
secur
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:09:45.501011  
**Функция #431**

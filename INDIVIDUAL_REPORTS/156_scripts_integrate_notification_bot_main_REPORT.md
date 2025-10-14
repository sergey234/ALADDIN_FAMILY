# 📋 ОТЧЕТ #156: scripts/integrate_notification_bot_main.py

**Дата анализа:** 2025-09-16T00:07:40.409397
**Категория:** SCRIPT
**Статус:** ❌ 41 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 41
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/integrate_notification_bot_main.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 29 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **E402:** 3 ошибок - Импорты не в начале файла
- **F401:** 1 ошибок - Неиспользуемые импорты
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/integrate_notification_bot_main.py:9:1: F401 'os' imported but unused
scripts/integrate_notification_bot_main.py:18:1: E402 module level import not at top of file
scripts/integrate_notification_bot_main.py:18:80: E501 line too long (129 > 79 characters)
scripts/integrate_notification_bot_main.py:19:1: E402 module level import not at top of file
scripts/integrate_notification_bot_main.py:20:1: E402 module level import not at top of file
scripts/integrate_notification_bot_main.py:31:1: W293 blank line contains whitespace
scripts/integrate_notification_bot_main.py:34:1: W293 blank line contains whitespace
scripts/integrate_notification_bot_main.py:46:1: W293 blank line contains whitespace
scripts/integrate_notification_bot_main.py:51:1: W293 blank line contains whitespace
scripts/integrate_notification_bot_main.py:56:1: W293 blank line contains whitespace
scripts/integrate_notification_bot_main.py:59:1: W293 blank line contains whitespace
scripts/integrate_notification_bot_main.py
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:40.410513  
**Функция #156**

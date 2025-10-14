# 📋 ОТЧЕТ #319: scripts/wake_up_sleep_manager.py

**Дата анализа:** 2025-09-16T00:08:51.757511
**Категория:** SCRIPT
**Статус:** ❌ 18 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 18
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/wake_up_sleep_manager.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 12 ошибок - Пробелы в пустых строках
- **F541:** 2 ошибок - f-строки без плейсхолдеров
- **E302:** 1 ошибок - Недостаточно пустых строк
- **W291:** 1 ошибок - Пробелы в конце строки
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/wake_up_sleep_manager.py:14:1: E302 expected 2 blank lines, found 1
scripts/wake_up_sleep_manager.py:16:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:19:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:22:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:26:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:29:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:31:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:35:34: W291 trailing whitespace
scripts/wake_up_sleep_manager.py:41:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:42:11: F541 f-string is missing placeholders
scripts/wake_up_sleep_manager.py:43:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:54:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.py:59:1: W293 blank line contains whitespace
scripts/wake_up_sleep_manager.p
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:51.757711  
**Функция #319**

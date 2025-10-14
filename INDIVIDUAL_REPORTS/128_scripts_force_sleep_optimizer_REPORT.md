# 📋 ОТЧЕТ #128: scripts/force_sleep_optimizer.py

**Дата анализа:** 2025-09-16T00:07:22.014412
**Категория:** SCRIPT
**Статус:** ❌ 49 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 49
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/force_sleep_optimizer.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 28 ошибок - Пробелы в пустых строках
- **F541:** 11 ошибок - f-строки без плейсхолдеров
- **E501:** 4 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E402:** 1 ошибок - Импорты не в начале файла
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/force_sleep_optimizer.py:9:1: F401 'json' imported but unused
scripts/force_sleep_optimizer.py:10:1: F401 'time' imported but unused
scripts/force_sleep_optimizer.py:16:1: E402 module level import not at top of file
scripts/force_sleep_optimizer.py:18:1: E302 expected 2 blank lines, found 1
scripts/force_sleep_optimizer.py:24:1: W293 blank line contains whitespace
scripts/force_sleep_optimizer.py:27:1: W293 blank line contains whitespace
scripts/force_sleep_optimizer.py:36:80: E501 line too long (81 > 79 characters)
scripts/force_sleep_optimizer.py:37:1: W293 blank line contains whitespace
scripts/force_sleep_optimizer.py:45:1: W293 blank line contains whitespace
scripts/force_sleep_optimizer.py:50:80: E501 line too long (82 > 79 characters)
scripts/force_sleep_optimizer.py:52:1: W293 blank line contains whitespace
scripts/force_sleep_optimizer.py:58:1: W293 blank line contains whitespace
scripts/force_sleep_optimizer.py:66:1: W293 blank line contains whitespace
scripts/force_s
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:22.014537  
**Функция #128**

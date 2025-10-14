# 📋 ОТЧЕТ #162: scripts/minimal_active_only.py

**Дата анализа:** 2025-09-16T00:07:45.182383
**Категория:** SCRIPT
**Статус:** ❌ 36 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 36
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/minimal_active_only.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 25 ошибок - Пробелы в пустых строках
- **W291:** 5 ошибок - Пробелы в конце строки
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **E302:** 1 ошибок - Недостаточно пустых строк
- **F541:** 1 ошибок - f-строки без плейсхолдеров
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
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/minimal_active_only.py:18:1: E302 expected 2 blank lines, found 1
scripts/minimal_active_only.py:20:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:23:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:26:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:30:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:33:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:36:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:38:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:41:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:44:54: W291 trailing whitespace
scripts/minimal_active_only.py:49:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:57:1: W293 blank line contains whitespace
scripts/minimal_active_only.py:61:52: W291 trailing whitespace
scripts/minimal_active_only.py:62:70: W291 trailing whitespace
scripts
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:45.182537  
**Функция #162**

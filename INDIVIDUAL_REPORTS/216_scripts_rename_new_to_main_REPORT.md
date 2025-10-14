# 📋 ОТЧЕТ #216: scripts/rename_new_to_main.py

**Дата анализа:** 2025-09-16T00:08:07.535563
**Категория:** SCRIPT
**Статус:** ❌ 24 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 24
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/rename_new_to_main.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 10 ошибок - Пробелы в пустых строках
- **E501:** 10 ошибок - Длинные строки (>79 символов)
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
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/rename_new_to_main.py:12:1: E302 expected 2 blank lines, found 1
scripts/rename_new_to_main.py:17:1: W293 blank line contains whitespace
scripts/rename_new_to_main.py:20:80: E501 line too long (99 > 79 characters)
scripts/rename_new_to_main.py:21:80: E501 line too long (99 > 79 characters)
scripts/rename_new_to_main.py:22:80: E501 line too long (95 > 79 characters)
scripts/rename_new_to_main.py:23:80: E501 line too long (93 > 79 characters)
scripts/rename_new_to_main.py:24:80: E501 line too long (91 > 79 characters)
scripts/rename_new_to_main.py:25:80: E501 line too long (95 > 79 characters)
scripts/rename_new_to_main.py:26:80: E501 line too long (107 > 79 characters)
scripts/rename_new_to_main.py:27:80: E501 line too long (95 > 79 characters)
scripts/rename_new_to_main.py:28:80: E501 line too long (110 > 79 characters)
scripts/rename_new_to_main.py:30:1: W293 blank line contains whitespace
scripts/rename_new_to_main.py:32:80: E501 line too long (83 > 79 characters)
scripts/ren
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:07.535696  
**Функция #216**

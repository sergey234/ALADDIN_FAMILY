# 📋 ОТЧЕТ #134: scripts/individual_reports_generator.py

**Дата анализа:** 2025-09-16T00:07:24.101834
**Категория:** SCRIPT
**Статус:** ❌ 96 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 96
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/individual_reports_generator.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 44 ошибок - Пробелы в пустых строках
- **E501:** 29 ошибок - Длинные строки (>79 символов)
- **F541:** 10 ошибок - f-строки без плейсхолдеров
- **E302:** 9 ошибок - Недостаточно пустых строк
- **W291:** 1 ошибок - Пробелы в конце строки
- **E722:** 1 ошибок - Ошибка E722
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W291:** Удалить пробелы в конце строк
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/individual_reports_generator.py:15:1: E302 expected 2 blank lines, found 1
scripts/individual_reports_generator.py:19:39: W291 trailing whitespace
scripts/individual_reports_generator.py:23:1: W293 blank line contains whitespace
scripts/individual_reports_generator.py:25:5: E722 do not use bare 'except'
scripts/individual_reports_generator.py:28:1: E302 expected 2 blank lines, found 1
scripts/individual_reports_generator.py:32:1: W293 blank line contains whitespace
scripts/individual_reports_generator.py:41:1: W293 blank line contains whitespace
scripts/individual_reports_generator.py:44:1: E302 expected 2 blank lines, found 1
scripts/individual_reports_generator.py:47:1: W293 blank line contains whitespace
scripts/individual_reports_generator.py:69:1: E302 expected 2 blank lines, found 1
scripts/individual_reports_generator.py:85:80: E501 line too long (80 > 79 characters)
scripts/individual_reports_generator.py:89:1: E302 expected 2 blank lines, found 1
scripts/individual_rep
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:24.102026  
**Функция #134**

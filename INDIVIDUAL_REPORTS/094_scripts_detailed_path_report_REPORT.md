# 📋 ОТЧЕТ #94: scripts/detailed_path_report.py

**Дата анализа:** 2025-09-16T00:07:10.818638
**Категория:** SCRIPT
**Статус:** ❌ 39 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 39
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/detailed_path_report.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 27 ошибок - Пробелы в пустых строках
- **E501:** 5 ошибок - Длинные строки (>79 символов)
- **F541:** 4 ошибок - f-строки без плейсхолдеров
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
scripts/detailed_path_report.py:15:1: E302 expected 2 blank lines, found 1
scripts/detailed_path_report.py:17:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:20:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:23:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:27:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:30:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:32:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:36:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:41:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:51:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:56:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:57:11: F541 f-string is missing placeholders
scripts/detailed_path_report.py:62:1: W293 blank line contains whitespace
scripts/detailed_path_report.py:67
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:10.818747  
**Функция #94**

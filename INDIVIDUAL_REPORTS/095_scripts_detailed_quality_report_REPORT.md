# 📋 ОТЧЕТ #95: scripts/detailed_quality_report.py

**Дата анализа:** 2025-09-16T00:07:11.145961
**Категория:** SCRIPT
**Статус:** ❌ 41 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 41
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/detailed_quality_report.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 28 ошибок - Пробелы в пустых строках
- **E501:** 6 ошибок - Длинные строки (>79 символов)
- **W291:** 3 ошибок - Пробелы в конце строки
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/detailed_quality_report.py:8:1: F401 'sys' imported but unused
scripts/detailed_quality_report.py:12:1: E302 expected 2 blank lines, found 1
scripts/detailed_quality_report.py:18:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:22:24: W291 trailing whitespace
scripts/detailed_quality_report.py:32:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:36:25: W291 trailing whitespace
scripts/detailed_quality_report.py:41:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:43:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:46:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:51:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:54:80: E501 line too long (100 > 79 characters)
scripts/detailed_quality_report.py:59:1: W293 blank line contains whitespace
scripts/detailed_quality_report.py:66:1: W293 blank line contains whitespace
scripts/detailed_q
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:11.146084  
**Функция #95**

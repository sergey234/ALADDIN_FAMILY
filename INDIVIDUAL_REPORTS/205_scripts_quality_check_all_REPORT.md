# 📋 ОТЧЕТ #205: scripts/quality_check_all.py

**Дата анализа:** 2025-09-16T00:08:03.427787
**Категория:** SCRIPT
**Статус:** ❌ 21 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 21
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/quality_check_all.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 13 ошибок - Пробелы в пустых строках
- **E501:** 3 ошибок - Длинные строки (>79 символов)
- **W291:** 2 ошибок - Пробелы в конце строки
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
scripts/quality_check_all.py:7:1: F401 'sys' imported but unused
scripts/quality_check_all.py:11:1: E302 expected 2 blank lines, found 1
scripts/quality_check_all.py:13:1: W293 blank line contains whitespace
scripts/quality_check_all.py:22:34: W291 trailing whitespace
scripts/quality_check_all.py:28:63: W291 trailing whitespace
scripts/quality_check_all.py:47:1: W293 blank line contains whitespace
scripts/quality_check_all.py:52:1: W293 blank line contains whitespace
scripts/quality_check_all.py:55:1: W293 blank line contains whitespace
scripts/quality_check_all.py:60:1: W293 blank line contains whitespace
scripts/quality_check_all.py:64:80: E501 line too long (85 > 79 characters)
scripts/quality_check_all.py:65:80: E501 line too long (86 > 79 characters)
scripts/quality_check_all.py:67:1: W293 blank line contains whitespace
scripts/quality_check_all.py:80:1: W293 blank line contains whitespace
scripts/quality_check_all.py:95:1: W293 blank line contains whitespace
scripts/quality_check
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:03.427918  
**Функция #205**

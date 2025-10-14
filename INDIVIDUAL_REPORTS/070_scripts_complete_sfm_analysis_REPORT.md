# 📋 ОТЧЕТ #70: scripts/complete_sfm_analysis.py

**Дата анализа:** 2025-09-16T00:07:02.393996
**Категория:** SCRIPT
**Статус:** ❌ 39 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 39
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/complete_sfm_analysis.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 19 ошибок - Пробелы в пустых строках
- **E501:** 8 ошибок - Длинные строки (>79 символов)
- **E302:** 4 ошибок - Недостаточно пустых строк
- **F541:** 2 ошибок - f-строки без плейсхолдеров
- **F401:** 1 ошибок - Неиспользуемые импорты
- **W291:** 1 ошибок - Пробелы в конце строки
- **E713:** 1 ошибок - Ошибка E713
- **E129:** 1 ошибок - Визуальные отступы
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями
- **E129:** Исправить визуальные отступы

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/complete_sfm_analysis.py:9:1: F401 're' imported but unused
scripts/complete_sfm_analysis.py:12:80: E501 line too long (82 > 79 characters)
scripts/complete_sfm_analysis.py:14:1: E302 expected 2 blank lines, found 1
scripts/complete_sfm_analysis.py:19:1: W293 blank line contains whitespace
scripts/complete_sfm_analysis.py:22:80: E501 line too long (82 > 79 characters)
scripts/complete_sfm_analysis.py:44:1: E302 expected 2 blank lines, found 1
scripts/complete_sfm_analysis.py:77:1: E302 expected 2 blank lines, found 1
scripts/complete_sfm_analysis.py:88:1: E302 expected 2 blank lines, found 1
scripts/complete_sfm_analysis.py:93:1: W293 blank line contains whitespace
scripts/complete_sfm_analysis.py:99:1: W293 blank line contains whitespace
scripts/complete_sfm_analysis.py:101:1: W293 blank line contains whitespace
scripts/complete_sfm_analysis.py:105:26: W291 trailing whitespace
scripts/complete_sfm_analysis.py:108:13: E713 test for membership should be 'not in'
scripts/complete
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:02.394126  
**Функция #70**

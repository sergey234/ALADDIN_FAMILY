# 📋 ОТЧЕТ #230: scripts/sfm_conflict_analyzer.py

**Дата анализа:** 2025-09-16T00:08:12.968812
**Категория:** SCRIPT
**Статус:** ❌ 121 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 121
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/sfm_conflict_analyzer.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 99 ошибок - Пробелы в пустых строках
- **E501:** 15 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E302:** 2 ошибок - Недостаточно пустых строк
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/sfm_conflict_analyzer.py:16:1: F401 'typing.Set' imported but unused
scripts/sfm_conflict_analyzer.py:16:1: F401 'typing.Tuple' imported but unused
scripts/sfm_conflict_analyzer.py:24:1: E302 expected 2 blank lines, found 1
scripts/sfm_conflict_analyzer.py:26:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:34:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:38:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:41:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:44:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:46:80: E501 line too long (83 > 79 characters)
scripts/sfm_conflict_analyzer.py:47:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:50:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:53:1: W293 blank line contains whitespace
scripts/sfm_conflict_analyzer.py:56:1: W293 blank line contains whitespace
scripts/sfm_c
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:12.968923  
**Функция #230**

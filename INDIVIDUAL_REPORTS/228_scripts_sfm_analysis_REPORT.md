# 📋 ОТЧЕТ #228: scripts/sfm_analysis.py

**Дата анализа:** 2025-09-16T00:08:12.169463
**Категория:** SCRIPT
**Статус:** ❌ 54 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 54
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/sfm_analysis.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 22 ошибок - Пробелы в пустых строках
- **E501:** 10 ошибок - Длинные строки (>79 символов)
- **F541:** 9 ошибок - f-строки без плейсхолдеров
- **E402:** 4 ошибок - Импорты не в начале файла
- **F401:** 3 ошибок - Неиспользуемые импорты
- **E302:** 3 ошибок - Недостаточно пустых строк
- **E305:** 2 ошибок - Ожидается 2 пустые строки после определения класса или функции
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
scripts/sfm_analysis.py:8:1: F401 'os' imported but unused
scripts/sfm_analysis.py:11:1: E402 module level import not at top of file
scripts/sfm_analysis.py:14:1: E402 module level import not at top of file
scripts/sfm_analysis.py:16:1: E302 expected 2 blank lines, found 1
scripts/sfm_analysis.py:21:1: E302 expected 2 blank lines, found 1
scripts/sfm_analysis.py:26:1: F401 'json' imported but unused
scripts/sfm_analysis.py:26:1: E305 expected 2 blank lines after class or function definition, found 0
scripts/sfm_analysis.py:26:1: E402 module level import not at top of file
scripts/sfm_analysis.py:27:1: F401 'datetime.datetime' imported but unused
scripts/sfm_analysis.py:27:1: E402 module level import not at top of file
scripts/sfm_analysis.py:29:1: E302 expected 2 blank lines, found 1
scripts/sfm_analysis.py:34:1: W293 blank line contains whitespace
scripts/sfm_analysis.py:38:1: W293 blank line contains whitespace
scripts/sfm_analysis.py:41:1: W293 blank line contains whitespace
scripts
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:12.169577  
**Функция #228**

# 📋 ОТЧЕТ #233: scripts/show_all_sfm_functions_final.py

**Дата анализа:** 2025-09-16T00:08:14.072242
**Категория:** SCRIPT
**Статус:** ❌ 71 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 71
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/show_all_sfm_functions_final.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E501:** 28 ошибок - Длинные строки (>79 символов)
- **W293:** 24 ошибок - Пробелы в пустых строках
- **F541:** 15 ошибок - f-строки без плейсхолдеров
- **E302:** 2 ошибок - Недостаточно пустых строк
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
scripts/show_all_sfm_functions_final.py:20:1: E302 expected 2 blank lines, found 1
scripts/show_all_sfm_functions_final.py:24:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions_final.py:28:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions_final.py:32:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions_final.py:35:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions_final.py:36:15: F541 f-string is missing placeholders
scripts/show_all_sfm_functions_final.py:38:80: E501 line too long (81 > 79 characters)
scripts/show_all_sfm_functions_final.py:39:15: F541 f-string is missing placeholders
scripts/show_all_sfm_functions_final.py:40:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions_final.py:47:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions_final.py:54:80: E501 line too long (93 > 79 characters)
scripts/show_all_sfm_functions_final.py:59:1: W293 blank line contains whitespace
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:14.072357  
**Функция #233**

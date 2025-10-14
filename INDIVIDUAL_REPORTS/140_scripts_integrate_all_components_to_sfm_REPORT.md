# 📋 ОТЧЕТ #140: scripts/integrate_all_components_to_sfm.py

**Дата анализа:** 2025-09-16T00:07:28.681058
**Категория:** SCRIPT
**Статус:** ❌ 31 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 31
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/integrate_all_components_to_sfm.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 13 ошибок - Пробелы в пустых строках
- **F541:** 5 ошибок - f-строки без плейсхолдеров
- **W291:** 4 ошибок - Пробелы в конце строки
- **E402:** 3 ошибок - Импорты не в начале файла
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/integrate_all_components_to_sfm.py:13:1: F401 'os' imported but unused
scripts/integrate_all_components_to_sfm.py:16:1: E402 module level import not at top of file
scripts/integrate_all_components_to_sfm.py:17:1: E402 module level import not at top of file
scripts/integrate_all_components_to_sfm.py:18:1: E402 module level import not at top of file
scripts/integrate_all_components_to_sfm.py:21:80: E501 line too long (91 > 79 characters)
scripts/integrate_all_components_to_sfm.py:23:1: E302 expected 2 blank lines, found 1
scripts/integrate_all_components_to_sfm.py:29:1: W293 blank line contains whitespace
scripts/integrate_all_components_to_sfm.py:34:1: W293 blank line contains whitespace
scripts/integrate_all_components_to_sfm.py:48:44: W291 trailing whitespace
scripts/integrate_all_components_to_sfm.py:58:64: W291 trailing whitespace
scripts/integrate_all_components_to_sfm.py:68:42: W291 trailing whitespace
scripts/integrate_all_components_to_sfm.py:88:49: W291 trailing whitesp
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:28.681260  
**Функция #140**

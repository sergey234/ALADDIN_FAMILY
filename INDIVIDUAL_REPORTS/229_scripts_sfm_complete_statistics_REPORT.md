# 📋 ОТЧЕТ #229: scripts/sfm_complete_statistics.py

**Дата анализа:** 2025-09-16T00:08:12.545506
**Категория:** SCRIPT
**Статус:** ❌ 122 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 122
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/sfm_complete_statistics.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E501:** 73 ошибок - Длинные строки (>79 символов)
- **W293:** 41 ошибок - Пробелы в пустых строках
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **W291:** 1 ошибок - Пробелы в конце строки
- **E741:** 1 ошибок - Ошибка E741
- **E122:** 1 ошибок - Ошибка E122
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
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/sfm_complete_statistics.py:8:1: F401 'sys' imported but unused
scripts/sfm_complete_statistics.py:12:1: E302 expected 2 blank lines, found 1
scripts/sfm_complete_statistics.py:18:1: W293 blank line contains whitespace
scripts/sfm_complete_statistics.py:22:80: E501 line too long (108 > 79 characters)
scripts/sfm_complete_statistics.py:23:80: E501 line too long (127 > 79 characters)
scripts/sfm_complete_statistics.py:24:80: E501 line too long (116 > 79 characters)
scripts/sfm_complete_statistics.py:25:80: E501 line too long (131 > 79 characters)
scripts/sfm_complete_statistics.py:26:80: E501 line too long (126 > 79 characters)
scripts/sfm_complete_statistics.py:27:80: E501 line too long (130 > 79 characters)
scripts/sfm_complete_statistics.py:28:1: W293 blank line contains whitespace
scripts/sfm_complete_statistics.py:30:80: E501 line too long (145 > 79 characters)
scripts/sfm_complete_statistics.py:31:80: E501 line too long (142 > 79 characters)
scripts/sfm_complete_statistics.p
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:12.545816  
**Функция #229**

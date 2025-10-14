# 📋 ОТЧЕТ #176: scripts/put_ci_pipeline_to_sleep.py

**Дата анализа:** 2025-09-16T00:07:53.136872
**Категория:** SCRIPT
**Статус:** ❌ 28 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 28
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/put_ci_pipeline_to_sleep.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 18 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/put_ci_pipeline_to_sleep.py:19:1: E302 expected 2 blank lines, found 1
scripts/put_ci_pipeline_to_sleep.py:21:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:24:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:31:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:35:80: E501 line too long (82 > 79 characters)
scripts/put_ci_pipeline_to_sleep.py:40:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:48:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:55:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:62:1: W293 blank line contains whitespace
scripts/put_ci_pipeline_to_sleep.py:74:80: E501 line too long (87 > 79 characters)
scripts/put_ci_pipeline_to_sleep.py:84:80: E501 line too long (88 > 79 characters)
scripts/put_ci_pipeline_to_sleep.py:86:80: E501 line too long (86 > 79 characters)
scripts/put_ci_pipeline_to_sleep.py:89:80: 
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:53.137042  
**Функция #176**

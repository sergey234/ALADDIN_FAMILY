# 📋 ОТЧЕТ #560: test_export_simple.py

**Дата анализа:** 2025-09-16T00:10:46.602381
**Категория:** OTHER
**Статус:** ❌ 18 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 18
- **Тип файла:** OTHER
- **Путь к файлу:** `test_export_simple.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 13 ошибок - Пробелы в пустых строках
- **E501:** 2 ошибок - Длинные строки (>79 символов)
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
test_export_simple.py:13:1: E302 expected 2 blank lines, found 1
test_export_simple.py:15:1: W293 blank line contains whitespace
test_export_simple.py:20:1: W293 blank line contains whitespace
test_export_simple.py:24:1: W293 blank line contains whitespace
test_export_simple.py:30:1: W293 blank line contains whitespace
test_export_simple.py:33:80: E501 line too long (87 > 79 characters)
test_export_simple.py:34:1: W293 blank line contains whitespace
test_export_simple.py:43:1: W293 blank line contains whitespace
test_export_simple.py:47:1: W293 blank line contains whitespace
test_export_simple.py:50:1: W293 blank line contains whitespace
test_export_simple.py:56:1: W293 blank line contains whitespace
test_export_simple.py:59:1: W293 blank line contains whitespace
test_export_simple.py:63:1: W293 blank line contains whitespace
test_export_simple.py:66:1: W293 blank line contains whitespace
test_export_simple.py:75:80: E501 line too long (93 > 79 characters)
test_export_simple.py:77:1: W
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:10:46.602545  
**Функция #560**

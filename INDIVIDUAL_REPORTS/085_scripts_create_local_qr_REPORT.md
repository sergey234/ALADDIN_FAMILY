# 📋 ОТЧЕТ #85: scripts/create_local_qr.py

**Дата анализа:** 2025-09-16T00:07:07.834179
**Категория:** SCRIPT
**Статус:** ❌ 37 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 37
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/create_local_qr.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 23 ошибок - Пробелы в пустых строках
- **F541:** 5 ошибок - f-строки без плейсхолдеров
- **E302:** 4 ошибок - Недостаточно пустых строк
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E722:** 1 ошибок - Ошибка E722
- **E501:** 1 ошибок - Длинные строки (>79 символов)
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
scripts/create_local_qr.py:9:1: F401 'sys' imported but unused
scripts/create_local_qr.py:10:1: F401 'os' imported but unused
scripts/create_local_qr.py:13:1: E302 expected 2 blank lines, found 1
scripts/create_local_qr.py:22:5: E722 do not use bare 'except'
scripts/create_local_qr.py:25:1: E302 expected 2 blank lines, found 1
scripts/create_local_qr.py:29:1: W293 blank line contains whitespace
scripts/create_local_qr.py:32:1: W293 blank line contains whitespace
scripts/create_local_qr.py:36:9: F541 f-string is missing placeholders
scripts/create_local_qr.py:37:9: F541 f-string is missing placeholders
scripts/create_local_qr.py:40:1: W293 blank line contains whitespace
scripts/create_local_qr.py:43:1: W293 blank line contains whitespace
scripts/create_local_qr.py:51:1: W293 blank line contains whitespace
scripts/create_local_qr.py:54:1: W293 blank line contains whitespace
scripts/create_local_qr.py:57:1: W293 blank line contains whitespace
scripts/create_local_qr.py:59:80: E501 line to
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:07.834315  
**Функция #85**

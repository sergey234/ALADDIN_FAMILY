# 📋 ОТЧЕТ #83: scripts/create_file_qr.py

**Дата анализа:** 2025-09-16T00:07:07.228623
**Категория:** SCRIPT
**Статус:** ❌ 23 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 23
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/create_file_qr.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 14 ошибок - Пробелы в пустых строках
- **E302:** 3 ошибок - Недостаточно пустых строк
- **F401:** 2 ошибок - Неиспользуемые импорты
- **F541:** 2 ошибок - f-строки без плейсхолдеров
- **E722:** 1 ошибок - Ошибка E722
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках

### 📝 Детальный вывод flake8:

```
scripts/create_file_qr.py:9:1: F401 'sys' imported but unused
scripts/create_file_qr.py:10:1: F401 'os' imported but unused
scripts/create_file_qr.py:13:1: E302 expected 2 blank lines, found 1
scripts/create_file_qr.py:22:5: E722 do not use bare 'except'
scripts/create_file_qr.py:25:1: E302 expected 2 blank lines, found 1
scripts/create_file_qr.py:29:1: W293 blank line contains whitespace
scripts/create_file_qr.py:32:1: W293 blank line contains whitespace
scripts/create_file_qr.py:34:16: F541 f-string is missing placeholders
scripts/create_file_qr.py:35:1: W293 blank line contains whitespace
scripts/create_file_qr.py:38:1: W293 blank line contains whitespace
scripts/create_file_qr.py:46:1: W293 blank line contains whitespace
scripts/create_file_qr.py:49:1: W293 blank line contains whitespace
scripts/create_file_qr.py:52:1: W293 blank line contains whitespace
scripts/create_file_qr.py:56:1: W293 blank line contains whitespace
scripts/create_file_qr.py:58:11: F541 f-string is missing pla
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:07.228739  
**Функция #83**

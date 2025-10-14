# 📋 ОТЧЕТ #25: final_system_report.py

**Дата анализа:** 2025-09-16T00:06:46.325120
**Категория:** OTHER
**Статус:** ❌ 33 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 33
- **Тип файла:** OTHER
- **Путь к файлу:** `final_system_report.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E501:** 12 ошибок - Длинные строки (>79 символов)
- **W293:** 9 ошибок - Пробелы в пустых строках
- **F541:** 7 ошибок - f-строки без плейсхолдеров
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **F841:** 1 ошибок - Неиспользуемые переменные
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные
- **F841:** Удалить неиспользуемые переменные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
final_system_report.py:9:1: F401 'sys' imported but unused
final_system_report.py:10:1: F401 'collections.defaultdict' imported but unused
final_system_report.py:12:1: E302 expected 2 blank lines, found 1
final_system_report.py:15:1: W293 blank line contains whitespace
final_system_report.py:23:11: F541 f-string is missing placeholders
final_system_report.py:42:1: W293 blank line contains whitespace
final_system_report.py:45:1: W293 blank line contains whitespace
final_system_report.py:51:1: W293 blank line contains whitespace
final_system_report.py:54:80: E501 line too long (85 > 79 characters)
final_system_report.py:57:1: W293 blank line contains whitespace
final_system_report.py:63:1: W293 blank line contains whitespace
final_system_report.py:65:80: E501 line too long (83 > 79 characters)
final_system_report.py:69:80: E501 line too long (96 > 79 characters)
final_system_report.py:71:1: W293 blank line contains whitespace
final_system_report.py:80:1: W293 blank line contains whitespa
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:46.325245  
**Функция #25**

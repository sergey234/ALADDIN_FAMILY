# 📋 ОТЧЕТ #47: scripts/analyze_sleep_mode_risks.py

**Дата анализа:** 2025-09-16T00:06:54.497894
**Категория:** SCRIPT
**Статус:** ❌ 92 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 92
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/analyze_sleep_mode_risks.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 39 ошибок - Пробелы в пустых строках
- **E501:** 27 ошибок - Длинные строки (>79 символов)
- **E302:** 7 ошибок - Недостаточно пустых строк
- **W291:** 4 ошибок - Пробелы в конце строки
- **E128:** 4 ошибок - Неправильные отступы
- **F541:** 4 ошибок - f-строки без плейсхолдеров
- **F401:** 3 ошибок - Неиспользуемые импорты
- **F841:** 1 ошибок - Неиспользуемые переменные
- **E722:** 1 ошибок - Ошибка E722
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F841:** Удалить неиспользуемые переменные
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/analyze_sleep_mode_risks.py:9:1: F401 'os' imported but unused
scripts/analyze_sleep_mode_risks.py:12:1: F401 'typing.Set' imported but unused
scripts/analyze_sleep_mode_risks.py:12:1: F401 'typing.Tuple' imported but unused
scripts/analyze_sleep_mode_risks.py:15:1: E302 expected 2 blank lines, found 1
scripts/analyze_sleep_mode_risks.py:18:80: E501 line too long (81 > 79 characters)
scripts/analyze_sleep_mode_risks.py:24:1: E302 expected 2 blank lines, found 1
scripts/analyze_sleep_mode_risks.py:27:1: W293 blank line contains whitespace
scripts/analyze_sleep_mode_risks.py:31:1: W293 blank line contains whitespace
scripts/analyze_sleep_mode_risks.py:37:1: W293 blank line contains whitespace
scripts/analyze_sleep_mode_risks.py:39:5: F841 local variable 'critical_paths' is assigned to but never used
scripts/analyze_sleep_mode_risks.py:41:1: W293 blank line contains whitespace
scripts/analyze_sleep_mode_risks.py:53:1: W293 blank line contains whitespace
scripts/analyze_sleep_mode_
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:54.498058  
**Функция #47**

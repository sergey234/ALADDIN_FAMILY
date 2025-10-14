# 📋 ОТЧЕТ #177: scripts/put_compliance_to_sleep.py

**Дата анализа:** 2025-09-16T00:07:53.534153
**Категория:** SCRIPT
**Статус:** ❌ 28 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 28
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/put_compliance_to_sleep.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 17 ошибок - Пробелы в пустых строках
- **E302:** 4 ошибок - Недостаточно пустых строк
- **W291:** 3 ошибок - Пробелы в конце строки
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк

### 📝 Детальный вывод flake8:

```
scripts/put_compliance_to_sleep.py:5:80: E501 line too long (83 > 79 characters)
scripts/put_compliance_to_sleep.py:16:1: F401 'datetime' imported but unused
scripts/put_compliance_to_sleep.py:22:1: E302 expected 2 blank lines, found 1
scripts/put_compliance_to_sleep.py:25:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep.py:28:59: W291 trailing whitespace
scripts/put_compliance_to_sleep.py:31:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep.py:39:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep.py:42:1: E302 expected 2 blank lines, found 1
scripts/put_compliance_to_sleep.py:45:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep.py:51:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep.py:57:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep.py:59:80: E501 line too long (86 > 79 characters)
scripts/put_compliance_to_sleep.py:64:1: E302 expected 2 blank lines, found
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:53.534271  
**Функция #177**

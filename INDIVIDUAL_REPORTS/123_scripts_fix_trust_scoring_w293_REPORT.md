# 📋 ОТЧЕТ #123: scripts/fix_trust_scoring_w293.py

**Дата анализа:** 2025-09-16T00:07:20.387141
**Категория:** SCRIPT
**Статус:** ❌ 11 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 11
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/fix_trust_scoring_w293.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 8 ошибок - Пробелы в пустых строках
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках

### 📝 Детальный вывод flake8:

```
scripts/fix_trust_scoring_w293.py:6:1: F401 're' imported but unused
scripts/fix_trust_scoring_w293.py:8:1: E302 expected 2 blank lines, found 1
scripts/fix_trust_scoring_w293.py:10:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:12:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:17:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:22:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:29:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:32:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:36:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:39:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_w293.py:44:1: E305 expected 2 blank lines after class or function definition, found 1
1     E302 expected 2 blank lines, found 1
1     E305 expected 2 blank lines after class or function definition, found 1
1     F401 're
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:20.387248  
**Функция #123**

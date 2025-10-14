# 📋 ОТЧЕТ #122: scripts/fix_trust_scoring_new.py

**Дата анализа:** 2025-09-16T00:07:20.094436
**Категория:** SCRIPT
**Статус:** ❌ 14 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 14
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/fix_trust_scoring_new.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 10 ошибок - Пробелы в пустых строках
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E501:** 1 ошибок - Длинные строки (>79 символов)
- **W291:** 1 ошибок - Пробелы в конце строки
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк

### 📝 Детальный вывод flake8:

```
scripts/fix_trust_scoring_new.py:6:1: E302 expected 2 blank lines, found 1
scripts/fix_trust_scoring_new.py:8:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:10:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:15:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:20:80: E501 line too long (94 > 79 characters)
scripts/fix_trust_scoring_new.py:21:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:26:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:28:65: W291 trailing whitespace
scripts/fix_trust_scoring_new.py:30:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:34:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:38:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:42:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.py:45:1: W293 blank line contains whitespace
scripts/fix_trust_scoring_new.p
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:20.094548  
**Функция #122**

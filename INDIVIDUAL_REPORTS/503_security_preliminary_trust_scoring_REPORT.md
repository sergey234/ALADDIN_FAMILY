# 📋 ОТЧЕТ #503: security/preliminary/trust_scoring.py

**Дата анализа:** 2025-09-16T00:10:21.854389
**Категория:** SECURITY
**Статус:** ❌ 9 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 9
- **Тип файла:** SECURITY
- **Путь к файлу:** `security/preliminary/trust_scoring.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E302:** 5 ошибок - Недостаточно пустых строк
- **E501:** 3 ошибок - Длинные строки (>79 символов)
- **E128:** 1 ошибок - Неправильные отступы

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
security/preliminary/trust_scoring.py:20:1: E302 expected 2 blank lines, found 1
security/preliminary/trust_scoring.py:28:1: E302 expected 2 blank lines, found 1
security/preliminary/trust_scoring.py:41:1: E302 expected 2 blank lines, found 1
security/preliminary/trust_scoring.py:53:1: E302 expected 2 blank lines, found 1
security/preliminary/trust_scoring.py:63:1: E302 expected 2 blank lines, found 1
security/preliminary/trust_scoring.py:196:26: E128 continuation line under-indented for visual indent
security/preliminary/trust_scoring.py:251:80: E501 line too long (81 > 79 characters)
security/preliminary/trust_scoring.py:254:80: E501 line too long (86 > 79 characters)
security/preliminary/trust_scoring.py:417:80: E501 line too long (80 > 79 characters)
1     E128 continuation line under-indented for visual indent
5     E302 expected 2 blank lines, found 1
3     E501 line too long (81 > 79 characters)

```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:10:21.854489  
**Функция #503**

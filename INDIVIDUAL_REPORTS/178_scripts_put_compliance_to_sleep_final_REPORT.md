# 📋 ОТЧЕТ #178: scripts/put_compliance_to_sleep_final.py

**Дата анализа:** 2025-09-16T00:07:53.894445
**Категория:** SCRIPT
**Статус:** ❌ 18 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 18
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/put_compliance_to_sleep_final.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 9 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E712:** 1 ошибок - Ошибка E712

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
scripts/put_compliance_to_sleep_final.py:15:1: E302 expected 2 blank lines, found 1
scripts/put_compliance_to_sleep_final.py:19:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep_final.py:22:80: E501 line too long (82 > 79 characters)
scripts/put_compliance_to_sleep_final.py:34:80: E501 line too long (83 > 79 characters)
scripts/put_compliance_to_sleep_final.py:35:80: E501 line too long (96 > 79 characters)
scripts/put_compliance_to_sleep_final.py:40:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep_final.py:42:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep_final.py:50:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep_final.py:53:80: E501 line too long (83 > 79 characters)
scripts/put_compliance_to_sleep_final.py:54:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep_final.py:94:1: W293 blank line contains whitespace
scripts/put_compliance_to_sleep_final.py:98:1: W293 blank line con
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:53.894561  
**Функция #178**

# 📋 ОТЧЕТ #323: security/access_control.py

**Дата анализа:** 2025-09-16T00:08:55.493953
**Категория:** SECURITY
**Статус:** ❌ 37 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 37
- **Тип файла:** SECURITY
- **Путь к файлу:** `security/access_control.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E501:** 33 ошибок - Длинные строки (>79 символов)
- **F821:** 3 ошибок - Неопределенное имя
- **W293:** 1 ошибок - Пробелы в пустых строках

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F821:** Определить неопределенные переменные

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках

### 📝 Детальный вывод flake8:

```
security/access_control.py:72:80: E501 line too long (80 > 79 characters)
security/access_control.py:114:80: E501 line too long (83 > 79 characters)
security/access_control.py:117:80: E501 line too long (91 > 79 characters)
security/access_control.py:127:80: E501 line too long (93 > 79 characters)
security/access_control.py:131:80: E501 line too long (88 > 79 characters)
security/access_control.py:132:80: E501 line too long (100 > 79 characters)
security/access_control.py:133:80: E501 line too long (95 > 79 characters)
security/access_control.py:134:80: E501 line too long (94 > 79 characters)
security/access_control.py:156:80: E501 line too long (84 > 79 characters)
security/access_control.py:170:80: E501 line too long (95 > 79 characters)
security/access_control.py:174:80: E501 line too long (93 > 79 characters)
security/access_control.py:328:80: E501 line too long (81 > 79 characters)
security/access_control.py:339:80: E501 line too long (101 > 79 characters)
security/access_control.
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:55.494078  
**Функция #323**

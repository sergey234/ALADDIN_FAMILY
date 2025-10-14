# 📋 ОТЧЕТ #171: scripts/push_notifications.py

**Дата анализа:** 2025-09-16T00:07:50.567959
**Категория:** SCRIPT
**Статус:** ❌ 57 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 57
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/push_notifications.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 33 ошибок - Пробелы в пустых строках
- **E501:** 18 ошибок - Длинные строки (>79 символов)
- **F401:** 4 ошибок - Неиспользуемые импорты
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/push_notifications.py:8:1: F401 'os' imported but unused
scripts/push_notifications.py:11:1: F401 'subprocess' imported but unused
scripts/push_notifications.py:14:1: F401 'getpass' imported but unused
scripts/push_notifications.py:15:1: F401 'platform' imported but unused
scripts/push_notifications.py:41:1: W293 blank line contains whitespace
scripts/push_notifications.py:104:1: W293 blank line contains whitespace
scripts/push_notifications.py:105:80: E501 line too long (87 > 79 characters)
scripts/push_notifications.py:107:1: W293 blank line contains whitespace
scripts/push_notifications.py:110:1: W293 blank line contains whitespace
scripts/push_notifications.py:117:1: W293 blank line contains whitespace
scripts/push_notifications.py:122:80: E501 line too long (107 > 79 characters)
scripts/push_notifications.py:128:80: E501 line too long (94 > 79 characters)
scripts/push_notifications.py:134:80: E501 line too long (89 > 79 characters)
scripts/push_notifications.py:168:80: E50
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:50.568106  
**Функция #171**

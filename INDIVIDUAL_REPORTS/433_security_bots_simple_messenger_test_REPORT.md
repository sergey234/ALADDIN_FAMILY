# 📋 ОТЧЕТ #433: security/bots/simple_messenger_test.py

**Дата анализа:** 2025-09-16T00:09:46.355238
**Категория:** BOT
**Статус:** ❌ 103 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 103
- **Тип файла:** BOT
- **Путь к файлу:** `security/bots/simple_messenger_test.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 74 ошибок - Пробелы в пустых строках
- **E501:** 18 ошибок - Длинные строки (>79 символов)
- **F401:** 4 ошибок - Неиспользуемые импорты
- **F841:** 4 ошибок - Неиспользуемые переменные
- **W291:** 1 ошибок - Пробелы в конце строки
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F841:** Удалить неиспользуемые переменные
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
security/bots/simple_messenger_test.py:11:1: F401 'time' imported but unused
security/bots/simple_messenger_test.py:13:1: F401 'typing.Dict' imported but unused
security/bots/simple_messenger_test.py:13:1: F401 'typing.List' imported but unused
security/bots/simple_messenger_test.py:13:1: F401 'typing.Any' imported but unused
security/bots/simple_messenger_test.py:22:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:27:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:31:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:34:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:43:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:52:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:61:1: W293 blank line contains whitespace
security/bots/simple_messenger_test.py:70:1: W293 blank line contains whitespace
security/bots/simple_mes
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:09:46.355427  
**Функция #433**

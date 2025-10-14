# 📋 ОТЧЕТ #434: security/bots/sleep_mode_manager.py

**Дата анализа:** 2025-09-16T00:09:46.747075
**Категория:** BOT
**Статус:** ❌ 92 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 92
- **Тип файла:** BOT
- **Путь к файлу:** `security/bots/sleep_mode_manager.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 63 ошибок - Пробелы в пустых строках
- **E501:** 25 ошибок - Длинные строки (>79 символов)
- **F401:** 3 ошибок - Неиспользуемые импорты
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
security/bots/sleep_mode_manager.py:11:1: F401 'time' imported but unused
security/bots/sleep_mode_manager.py:13:1: F401 'typing.List' imported but unused
security/bots/sleep_mode_manager.py:13:1: F401 'typing.Optional' imported but unused
security/bots/sleep_mode_manager.py:23:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:29:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:46:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:58:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:66:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:76:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:77:80: E501 line too long (85 > 79 characters)
security/bots/sleep_mode_manager.py:79:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:83:1: W293 blank line contains whitespace
security/bots/sleep_mode_manager.py:84:80: E501 line 
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:09:46.747255  
**Функция #434**

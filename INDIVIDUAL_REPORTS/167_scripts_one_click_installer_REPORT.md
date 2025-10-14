# 📋 ОТЧЕТ #167: scripts/one_click_installer.py

**Дата анализа:** 2025-09-16T00:07:48.455143
**Категория:** SCRIPT
**Статус:** ❌ 62 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 62
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/one_click_installer.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 49 ошибок - Пробелы в пустых строках
- **E501:** 6 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **W291:** 2 ошибок - Пробелы в конце строки
- **E128:** 2 ошибок - Неправильные отступы
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/one_click_installer.py:12:1: F401 'shutil' imported but unused
scripts/one_click_installer.py:15:1: F401 'getpass' imported but unused
scripts/one_click_installer.py:41:1: W293 blank line contains whitespace
scripts/one_click_installer.py:46:1: W293 blank line contains whitespace
scripts/one_click_installer.py:48:1: W293 blank line contains whitespace
scripts/one_click_installer.py:55:80: E501 line too long (86 > 79 characters)
scripts/one_click_installer.py:56:1: W293 blank line contains whitespace
scripts/one_click_installer.py:68:1: W293 blank line contains whitespace
scripts/one_click_installer.py:75:1: W293 blank line contains whitespace
scripts/one_click_installer.py:79:78: W291 trailing whitespace
scripts/one_click_installer.py:80:30: E128 continuation line under-indented for visual indent
scripts/one_click_installer.py:90:1: W293 blank line contains whitespace
scripts/one_click_installer.py:100:1: W293 blank line contains whitespace
scripts/one_click_installer.py:110:1:
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:48.455460  
**Функция #167**

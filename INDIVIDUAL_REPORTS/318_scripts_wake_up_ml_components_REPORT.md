# 📋 ОТЧЕТ #318: scripts/wake_up_ml_components.py

**Дата анализа:** 2025-09-16T00:08:51.138372
**Категория:** SCRIPT
**Статус:** ❌ 32 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 32
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/wake_up_ml_components.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 19 ошибок - Пробелы в пустых строках
- **W291:** 5 ошибок - Пробелы в конце строки
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **F401:** 1 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **E129:** 1 ошибок - Визуальные отступы
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями
- **E129:** Исправить визуальные отступы

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/wake_up_ml_components.py:13:1: F401 'typing.Set' imported but unused
scripts/wake_up_ml_components.py:15:1: E302 expected 2 blank lines, found 1
scripts/wake_up_ml_components.py:17:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:20:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:23:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:27:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:30:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:33:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:35:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:41:1: W293 blank line contains whitespace
scripts/wake_up_ml_components.py:44:72: W291 trailing whitespace
scripts/wake_up_ml_components.py:45:5: E129 visually indented line with same indent as next logical line
scripts/wake_up_ml_components.py:47:1: W293 blank line contains whitespace
sc
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:51.138617  
**Функция #318**

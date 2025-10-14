# 📋 ОТЧЕТ #88: scripts/create_vpn_qr.py

**Дата анализа:** 2025-09-16T00:07:08.736684
**Категория:** SCRIPT
**Статус:** ❌ 40 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 40
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/create_vpn_qr.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 25 ошибок - Пробелы в пустых строках
- **E302:** 4 ошибок - Недостаточно пустых строк
- **F541:** 3 ошибок - f-строки без плейсхолдеров
- **F401:** 2 ошибок - Неиспользуемые импорты
- **F841:** 2 ошибок - Неиспользуемые переменные
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **E722:** 1 ошибок - Ошибка E722
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные
- **F841:** Удалить неиспользуемые переменные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
scripts/create_vpn_qr.py:9:1: F401 'sys' imported but unused
scripts/create_vpn_qr.py:10:1: F401 'os' imported but unused
scripts/create_vpn_qr.py:13:1: E302 expected 2 blank lines, found 1
scripts/create_vpn_qr.py:22:5: E722 do not use bare 'except'
scripts/create_vpn_qr.py:25:1: E302 expected 2 blank lines, found 1
scripts/create_vpn_qr.py:29:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:33:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:36:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:39:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:47:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:50:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:53:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:57:1: W293 blank line contains whitespace
scripts/create_vpn_qr.py:59:11: F541 f-string is missing placeholders
scripts/create_vpn_qr.py:60:1: W293 blank line contains whitespace
scripts/
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:08.736812  
**Функция #88**

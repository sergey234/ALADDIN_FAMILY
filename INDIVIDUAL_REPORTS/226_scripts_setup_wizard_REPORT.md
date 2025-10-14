# 📋 ОТЧЕТ #226: scripts/setup_wizard.py

**Дата анализа:** 2025-09-16T00:08:11.419905
**Категория:** SCRIPT
**Статус:** ❌ 8 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 8
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/setup_wizard.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **F541:** 6 ошибок - f-строки без плейсхолдеров
- **F401:** 2 ошибок - Неиспользуемые импорты

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

### 📝 Детальный вывод flake8:

```
scripts/setup_wizard.py:8:1: F401 'os' imported but unused
scripts/setup_wizard.py:12:1: F401 'datetime.datetime' imported but unused
scripts/setup_wizard.py:123:15: F541 f-string is missing placeholders
scripts/setup_wizard.py:200:15: F541 f-string is missing placeholders
scripts/setup_wizard.py:275:15: F541 f-string is missing placeholders
scripts/setup_wizard.py:339:15: F541 f-string is missing placeholders
scripts/setup_wizard.py:384:15: F541 f-string is missing placeholders
scripts/setup_wizard.py:428:15: F541 f-string is missing placeholders
2     F401 'os' imported but unused
6     F541 f-string is missing placeholders

```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:11.420008  
**Функция #226**

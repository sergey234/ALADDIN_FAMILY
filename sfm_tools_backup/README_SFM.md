# 🚀 SFM Analyzer - Быстрый доступ

## ⚡ Мгновенная статистика
```bash
cd /Users/sergejhlystov/ALADDIN_NEW
python3 scripts/sfm_quick_stats.py
```

## 📊 Детальный анализ
```bash
python3 scripts/sfm_analyzer.py --detailed
```

## 🔍 Функции по статусу
```bash
# Активные функции
python3 scripts/sfm_analyzer.py --status active

# Спящие функции  
python3 scripts/sfm_analyzer.py --status sleeping

# Работающие функции
python3 scripts/sfm_analyzer.py --status running
```

## 📁 Экспорт в CSV
```bash
python3 scripts/sfm_analyzer.py --export csv
```

## 🎯 Что это дает?

**Актуальная статистика SFM:**
- Всего функций: 330 (100%)
- Активные: 22 (6.7%)
- Спящие: 289 (87.6%)
- Работающие: 19 (5.8%)
- Критические: 262 (79.4%)

**Полная документация:** `docs/SFM_ANALYZER_GUIDE.md`
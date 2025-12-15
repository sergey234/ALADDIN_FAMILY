# ✅ ШАБЛОН ПРОВЕРКИ FLAKE8 ПЕРЕД РЕГИСТРАЦИЕЙ В SFM

**ВАЖНО:** Этот шаблон должен применяться для ВСЕХ новых функций перед регистрацией в SFM!

---

## 🔍 ШАГИ ПРОВЕРКИ FLAKE8

### 1. Запуск flake8 на все созданные Python файлы

```bash
# Для каждого созданного файла агента:
python3 -m flake8 security/ai_agents/[имя_агента].py \
    --max-line-length=120 \
    --ignore=E501,W503,E203,W293,W391

# Если есть дополнительные файлы (интерфейсы, утилиты):
python3 -m flake8 security/ai_agents/[дополнительный_файл].py \
    --max-line-length=120 \
    --ignore=E501,W503,E203,W293,W391
```

### 2. Проверка компиляции Python

```bash
python3 -m py_compile security/ai_agents/[имя_агента].py
python3 -m py_compile security/ai_agents/[дополнительный_файл].py
```

### 3. Проверка импортов

```bash
python3 -c "from security.ai_agents.[имя_агента] import [ИмяКлассаАгента]"
```

### 4. Исправление найденных ошибок

**Критичные ошибки (обязательно исправить):**
- **F-errors** (F401, F541, F841 и т.д.) - синтаксис, неиспользуемые импорты/переменные
- **E-errors** (E128, E501 и т.д.) - стиль кода, отступы (кроме игнорируемых)

**Менее критичные (можно игнорировать, но лучше исправить):**
- **W-errors** - предупреждения (W293, W391 обычно игнорируются)

---

## ✅ КРИТЕРИИ УСПЕШНОЙ ПРОВЕРКИ

1. ✅ flake8 возвращает **0 ошибок** (или только игнорируемые W-errors)
2. ✅ Все файлы успешно компилируются через `py_compile`
3. ✅ Все импорты работают корректно

---

## 🚫 ЗАПРЕЩЕНО

❌ **НЕ РЕГИСТРИРОВАТЬ В SFM** если:
- Есть любые F-errors
- Есть любые E-errors (кроме явно игнорируемых)
- Файлы не компилируются
- Импорты не работают

---

## 📝 ПРИМЕР ДЛЯ DARK WEB MONITORING

```bash
# 1. Проверка flake8
python3 -m flake8 security/ai_agents/dark_web_monitoring_agent.py \
    --max-line-length=120 --ignore=E501,W503,E203,W293,W391

python3 -m flake8 security/ai_agents/threat_monitoring_interface.py \
    --max-line-length=120 --ignore=E501,W503,E203,W293,W391

# 2. Проверка компиляции
python3 -m py_compile security/ai_agents/dark_web_monitoring_agent.py
python3 -m py_compile security/ai_agents/threat_monitoring_interface.py

# 3. Проверка импортов
python3 -c "from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent"
python3 -c "from security.ai_agents.threat_monitoring_interface import ThreatEventBus"

# 4. ✅ Если все успешно - можно регистрировать в SFM!
```

---

**Дата создания:** 9 декабря 2025  
**Применимо для:** Все 12 новых функций

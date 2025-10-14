# 📋 ОТЧЕТ #386: security/ai_agents/notification_bot.py

**Дата анализа:** 2025-09-16T00:09:25.203446
**Категория:** AI_AGENT
**Статус:** ❌ 14 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 14
- **Тип файла:** AI_AGENT
- **Путь к файлу:** `security/ai_agents/notification_bot.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **F401:** 14 ошибок - Неиспользуемые импорты

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

### 📝 Детальный вывод flake8:

```
security/ai_agents/notification_bot.py:20:1: F401 'asyncio' imported but unused
security/ai_agents/notification_bot.py:21:1: F401 'hashlib' imported but unused
security/ai_agents/notification_bot.py:23:1: F401 'logging' imported but unused
security/ai_agents/notification_bot.py:24:1: F401 'math' imported but unused
security/ai_agents/notification_bot.py:26:1: F401 're' imported but unused
security/ai_agents/notification_bot.py:33:1: F401 'typing.Callable' imported but unused
security/ai_agents/notification_bot.py:33:1: F401 'typing.Protocol' imported but unused
security/ai_agents/notification_bot.py:33:1: F401 'typing.Set' imported but unused
security/ai_agents/notification_bot.py:33:1: F401 'typing.Union' imported but unused
security/ai_agents/notification_bot.py:46:1: F401 'requests' imported but unused
security/ai_agents/notification_bot.py:50:1: F401 'sklearn.metrics.pairwise.cosine_similarity' imported but unused
security/ai_agents/notification_bot.py:54:1: F401 'core.security_bas
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:09:25.203625  
**Функция #386**

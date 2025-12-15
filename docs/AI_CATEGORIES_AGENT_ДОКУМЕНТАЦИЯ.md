# 🤖 AI Categories Agent - Документация

**Дата создания:** 11 декабря 2025  
**Версия:** 1.0.0  
**Статус:** ✅ Backend готов (100% - готов к деплою)

---

## 📋 ОБЗОР

AI Categories Agent - это агент для родительского контроля AI-сайтов и приложений. Позволяет родителям блокировать или ограничивать доступ детей к различным AI-сервисам с настройками по времени и возрасту.

---

## 🎯 ФУНКЦИОНАЛЬНОСТЬ

### Основные возможности:

1. **Блокировка/разрешение AI-сайтов** - родители могут заблокировать или разрешить доступ к конкретным AI-сервисам
2. **Ограничения по времени** - блокировка в определенное время суток и дни недели
3. **Ограничения по возрасту** - автоматическая блокировка для детей младше определенного возраста
4. **Уведомления родителям** - автоматические уведомления о попытках доступа к заблокированным сайтам
5. **История доступа** - отслеживание всех попыток доступа к AI-сайтам

---

## 📱 ПОДДЕРЖИВАЕМЫЕ AI-СЕРВИСЫ (9 сервисов)

### 🇷🇺 Российские сервисы (5):

1. **Алиса AI** (Яндекс)
   - ID: `alice`
   - Домен: `yandex.ru/alice`
   - Категория: Текстовый AI
   - Возраст: 6+ (безопасна для детей)
   - Бесплатный

2. **YandexGPT** (Яндекс)
   - ID: `yandexgpt`
   - Домен: `yandex.ru/gpt`
   - Категория: Текстовый AI
   - Возраст: 13+
   - Бесплатный
   - Популярность: 60% предпочтений в России

3. **GigaChat** (Сбербанк)
   - ID: `gigachat`
   - Домен: `gigachat.ru`
   - Категория: Текстовый AI
   - Возраст: 13+
   - Бесплатный
   - Популярность: 4% пользователей в России

4. **Kandinsky** (Яндекс)
   - ID: `kandinsky`
   - Домен: `kandinsky.ai`
   - Категория: Генерация изображений
   - Возраст: 13+
   - Бесплатный

5. **Шедеврум**
   - ID: `shedevrum`
   - Домен: `shedevrum.ai`
   - Категория: Генерация изображений
   - Возраст: 13+
   - Бесплатный

### 🌍 Международные сервисы (4):

1. **ChatGPT** (OpenAI)
   - ID: `chatgpt`
   - Домен: `chat.openai.com`
   - Категория: Текстовый AI
   - Возраст: 13+
   - Платный
   - Популярность: 3.5% пользователей в России

2. **DeepSeek**
   - ID: `deepseek`
   - Домен: `deepseek.com`
   - Категория: Текстовый AI
   - Возраст: 13+
   - Бесплатный
   - Популярность: 9.4% пользователей в России

3. **Claude** (Anthropic)
   - ID: `claude`
   - Домен: `claude.ai`
   - Категория: Текстовый AI
   - Возраст: 13+
   - Платный

4. **Google Gemini**
   - ID: `gemini`
   - Домен: `gemini.google.com`
   - Категория: Текстовый AI
   - Возраст: 13+
   - Бесплатный

---

## 🔧 API ENDPOINTS

### 1. Получить список всех AI-сайтов
```
GET /api/ai-categories/sites
```
**Ответ:**
```json
{
  "status": "success",
  "sites": [
    {
      "id": "alice",
      "name": "Алиса AI",
      "domain": "yandex.ru/alice",
      "category": "text_generation",
      "age_restriction": 6,
      "is_free": true
    },
    ...
  ],
  "total": 9
}
```

### 2. Заблокировать AI-сайты
```
POST /api/ai-categories/block
```
**Тело запроса:**
```json
{
  "user_id": "user123",
  "site_ids": ["chatgpt", "midjourney"],
  "time_restriction": {
    "start_time": "09:00",
    "end_time": "18:00",
    "days_of_week": [0, 1, 2, 3, 4],
    "enabled": true
  }
}
```

### 3. Разрешить доступ к AI-сайтам
```
POST /api/ai-categories/allow
```
**Тело запроса:**
```json
{
  "user_id": "user123",
  "site_ids": ["alice", "yandexgpt"]
}
```

### 4. Проверить доступ к AI-сайту
```
POST /api/ai-categories/check
```
**Тело запроса:**
```json
{
  "user_id": "user123",
  "site_id": "chatgpt",
  "user_age": 15
}
```
**Ответ:**
```json
{
  "allowed": false,
  "blocked": true,
  "reason": "blocked",
  "message": "Сайт ChatGPT заблокирован"
}
```

### 5. Получить статус всех AI-сайтов
```
GET /api/ai-categories/status?user_id=user123
```
**Ответ:**
```json
{
  "user_id": "user123",
  "sites": [
    {
      "site_id": "chatgpt",
      "is_blocked": true,
      "is_allowed": false,
      "access_count": 0,
      "blocked_count": 5
    },
    ...
  ],
  "total_sites": 9,
  "blocked_count": 3,
  "allowed_count": 6
}
```

### 6. Получить историю попыток доступа
```
GET /api/ai-categories/history?user_id=user123&limit=50
```

### 7. Установить ограничение по возрасту
```
POST /api/ai-categories/age-restriction
```
**Тело запроса:**
```json
{
  "user_id": "user123",
  "site_id": "chatgpt",
  "age_restriction": {
    "min_age": 16,
    "require_parental_approval": true,
    "block_completely": false
  }
}
```

### 8. Health check
```
GET /api/ai-categories/health
```

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
security/
├── ai_agents/
│   └── ai_categories_agent.py          # Основной агент (≈800 строк)
└── api/
    └── routers/
        └── ai_categories_router.py      # API router (≈400 строк)
```

---

## 🔍 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Блокировка ChatGPT для ребенка
```python
from security.ai_agents.ai_categories_agent import AICategoriesAgent

agent = AICategoriesAgent()

# Блокируем ChatGPT
result = agent.block_sites(
    user_id="child123",
    site_ids=["chatgpt"]
)
# Результат: {"status": "success", "blocked": ["chatgpt"], ...}
```

### Пример 2: Ограничение по времени
```python
from security.ai_agents.ai_categories_agent import TimeRestriction

# Разрешаем доступ только с 9:00 до 18:00 в будние дни
time_restriction = TimeRestriction(
    start_time="09:00",
    end_time="18:00",
    days_of_week=[0, 1, 2, 3, 4],  # Пн-Пт
    enabled=True
)

result = agent.block_sites(
    user_id="child123",
    site_ids=["chatgpt", "gigachat"],
    time_restriction=time_restriction
)
```

### Пример 3: Проверка доступа
```python
# Проверяем доступ 15-летнего ребенка к ChatGPT
result = agent.check_access(
    user_id="child123",
    site_id="chatgpt",
    user_age=15
)

if result["blocked"]:
    print(f"Доступ заблокирован: {result['message']}")
```

---

## ✅ ПРОВЕРКИ

- [x] Код компилируется без ошибок
- [x] Flake8 проверка пройдена (0 ошибок)
- [x] Все импорты работают
- [x] API router создан и проверен
- [x] Регистрация в SFM (`function_registry_entry_ai_categories.json` создан)
- [x] JSON валидирован
- [x] Unit-тесты созданы (`test_ai_categories_agent.py`)
- [x] Интеграционные тесты созданы (`test_ai_categories_api_endpoints.py`)

---

## 📊 СТАТИСТИКА

- **Всего AI-сайтов:** 9
- **Российских:** 5 (56%)
- **Международных:** 4 (44%)
- **Текстовых AI:** 7
- **Генерация изображений:** 2
- **Бесплатных:** 8
- **Платных:** 1 (ChatGPT)

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. ✅ **Регистрация в SFM** - `function_registry_entry_ai_categories.json` создан
2. ✅ **Unit-тесты** - `test_ai_categories_agent.py` создан (15+ тестов)
3. ✅ **Интеграционные тесты** - `test_ai_categories_api_endpoints.py` создан (20+ тестов)
4. ✅ **Деплой** - скрипты деплоя созданы, готов к деплою на `/opt/aladdin-backend/`

---

**Последнее обновление:** 11 декабря 2025

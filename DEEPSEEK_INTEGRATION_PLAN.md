# 🚀 ДЕТАЛЬНЫЙ ПЛАН ИНТЕГРАЦИИ DEEPSEEK В AI ASSISTANT

**Дата:** 2026-03-12  
**Версия:** BUILD 115+  
**Статус:** 📋 ПОШАГОВЫЙ ПЛАН

---

## 🎯 ЦЕЛЬ

Интегрировать DeepSeek API в AI Assistant для получения умных, персонализированных ответов вместо одинаковых mock ответов.

---

## 📋 ЭТАПЫ РЕАЛИЗАЦИИ

### 🔴 ФАЗА 1: Получение API ключа и настройка (30 минут)

#### 1.1. Получить API ключ DeepSeek:

1. Зарегистрироваться на https://platform.deepseek.com
2. Создать API ключ
3. Сохранить ключ в переменных окружения

#### 1.2. Добавить в конфигурацию сервера:

```bash
# В .env файл сервера
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_ENABLED=true
```

---

### 🟡 ФАЗА 2: Создание DeepSeek Client на сервере (2-3 часа)

#### 2.1. Создать `app/security/ai/deepseek_client.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API Client
Интеграция DeepSeek AI для генерации умных ответов
"""

import os
import httpx
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Клиент для работы с DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.enabled = bool(self.api_key)
        self.model = "deepseek-chat"
        self.timeout = 30.0
        
        if not self.enabled:
            logger.warning("⚠️ DeepSeek API key not found, DeepSeek disabled")
    
    async def chat(
        self,
        message: str,
        context: str = "general",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Отправка сообщения в DeepSeek
        
        Args:
            message: Сообщение пользователя
            context: Контекст разговора
            conversation_history: История диалога
            system_prompt: Системный промпт (опционально)
        
        Returns:
            Ответ от DeepSeek или None при ошибке
        """
        if not self.enabled:
            return None
        
        try:
            # Формируем сообщения
            messages = self._build_messages(
                message=message,
                context=context,
                history=conversation_history or [],
                system_prompt=system_prompt
            )
            
            # Формируем запрос
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            # Отправляем запрос
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        logger.info(f"✅ DeepSeek response received ({len(content)} chars)")
                        return {
                            "response": content,
                            "confidence": 0.95,
                            "model": "deepseek-chat",
                            "usage": result.get("usage", {})
                        }
                else:
                    logger.error(f"❌ DeepSeek API error: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("❌ DeepSeek API timeout")
            return None
        except Exception as e:
            logger.error(f"❌ DeepSeek API exception: {e}")
            return None
    
    def _build_messages(
        self,
        message: str,
        context: str,
        history: List[Dict[str, str]],
        system_prompt: Optional[str]
    ) -> List[Dict[str, str]]:
        """Построение списка сообщений для DeepSeek"""
        messages = []
        
        # Системный промпт
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": self._build_system_prompt(context)
            })
        
        # История диалога (последние 10 сообщений)
        for hist_msg in history[-10:]:
            messages.append({
                "role": hist_msg.get("role", "user"),
                "content": hist_msg.get("content", "")
            })
        
        # Текущее сообщение
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def _build_system_prompt(self, context: str) -> str:
        """Построение системного промпта на основе контекста"""
        base_prompt = """Ты - AI помощник ALADDIN, система безопасности для семей.
Твоя задача - помогать пользователям с вопросами безопасности, защиты семьи и детей.

Правила:
- Отвечай на русском языке
- Будь дружелюбным и понятным
- Используй эмодзи для лучшего восприятия (но не переборщи)
- Давай конкретные советы
- Если не знаешь ответа - честно скажи
- Будь кратким, но информативным
"""
        
        context_prompts = {
            "protection_status": base_prompt + """
- Расскажи о статусе защиты на основе реальных данных
- Объясни, что означает текущий уровень защиты
- Дай рекомендации по улучшению
""",
            "threat_analysis": base_prompt + """
- Проанализируй угрозы и дай рекомендации
- Объясни уровень опасности
- Предложи конкретные действия
""",
            "recommendations": base_prompt + """
- Дай персональные рекомендации по безопасности
- Учитывай текущую ситуацию пользователя
- Предложи конкретные шаги
""",
            "help": base_prompt + """
- Помоги пользователю разобраться с функциями
- Объясни простым языком
- Предложи следующие шаги
""",
            "psychological_support": base_prompt + """
- Окажи психологическую поддержку
- Будь эмпатичным и понимающим
- Не давай медицинских советов
- При кризисе направь к специалисту
""",
            "crisis": base_prompt + """
- КРИЗИСНАЯ СИТУАЦИЯ!
- Окажи немедленную поддержку
- Дай контакты кризисной службы: 8-800-2000-122
- Успокой пользователя
- Направь к специалисту
""",
            "stats": base_prompt + """
- Расскажи о статистике безопасности
- Объясни цифры простым языком
- Дай рекомендации на основе статистики
""",
            "general": base_prompt
        }
        
        return context_prompts.get(context, base_prompt)

# Singleton instance
deepseek_client = DeepSeekClient()
```

---

### 🟢 ФАЗА 3: Интеграция в AI Assistant Router (2-3 часа)

#### 3.1. Модифицировать `security/api/routers/ai_assistant_router.py`:

```python
# Добавить импорт
from app.security.ai.deepseek_client import deepseek_client

# Модифицировать ai_assistant_chat endpoint
@router.post("/chat", response_model=ChatMessageResponse)
async def ai_assistant_chat(
    request: ChatMessageRequest,
    user: dict = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    AI помощник - обработка сообщений пользователя
    Теперь с поддержкой DeepSeek!
    """
    # Проверяем rate limit
    user_id = user["user_id"] or "anonymous"
    subscription_level = user["subscription_level"]
    
    if not check_rate_limit(user_id, subscription_level):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {subscription_level} subscription."
        )
    
    try:
        # ✅ ПРИОРИТЕТ 1: Попробовать DeepSeek API
        if deepseek_client.enabled:
            logger.info(f"🤖 Attempting DeepSeek API call for context: {request.context}")
            
            # Получаем историю диалога (можно добавить позже)
            conversation_history = []  # TODO: Получить из БД
            
            deepseek_response = await deepseek_client.chat(
                message=request.message,
                context=request.context,
                conversation_history=conversation_history
            )
            
            if deepseek_response:
                logger.info("✅ Using DeepSeek API response")
                
                # Сохраняем в историю (можно добавить позже)
                # await save_message(user_id, "user", request.message, request.context)
                # await save_message(user_id, "assistant", deepseek_response["response"], request.context)
                
                return ChatMessageResponse(
                    response=deepseek_response["response"],
                    confidence=deepseek_response.get("confidence", 0.95),
                    suggestions=[],
                    follow_up_questions=[],
                    timestamp=datetime.now()
                )
            else:
                logger.warning("⚠️ DeepSeek API failed, trying fallback")
        
        # ✅ ПРИОРИТЕТ 2: Попробовать SFM Adapter
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "message": request.message,
                "context": request.context,
                "user_id": request.user_id or "guest",
                "timestamp": request.timestamp.isoformat() if request.timestamp else datetime.now().isoformat()
            }
            success, result, message = sfm_adapter.execute_function("ai_assistant_chat", data)
            
            if success:
                logger.info("✅ Using SFM Adapter response")
                return ChatMessageResponse(
                    response=result.get("response", _get_fallback_response(request.context)["response"]),
                    confidence=result.get("confidence", 0.95),
                    suggestions=result.get("suggestions", []),
                    follow_up_questions=result.get("follow_up_questions", []),
                    timestamp=datetime.now()
                )
        
        # ✅ ПРИОРИТЕТ 3: Fallback mock response
        logger.warning("⚠️ Using fallback mock response")
        fallback = _get_fallback_response(request.context)
        return ChatMessageResponse(**fallback)
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        fallback = _get_fallback_response(request.context)
        return ChatMessageResponse(**fallback)
```

---

### 🔵 ФАЗА 4: Добавить историю диалога (опционально, 1 день)

#### 4.1. Создать таблицу в БД:

```python
# В database/models.py
class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    context = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
```

#### 4.2. Функции для работы с историей:

```python
async def get_conversation_history(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[Dict[str, str]]:
    """Получение истории диалога"""
    history = db.query(ConversationHistory)\
        .filter(ConversationHistory.user_id == user_id)\
        .order_by(ConversationHistory.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return [
        {"role": h.role, "content": h.content}
        for h in reversed(history)
    ]

async def save_message(
    user_id: str,
    role: str,
    content: str,
    context: str,
    db: Session = Depends(get_db)
):
    """Сохранение сообщения"""
    history = ConversationHistory(
        user_id=user_id,
        role=role,
        content=content,
        context=context,
        timestamp=datetime.now()
    )
    db.add(history)
    db.commit()
```

---

## 🎯 ПРИОРИТЕТЫ ОБРАБОТКИ

### Идеальная архитектура:

```
1. Локальная обработка (простые вопросы)
   ↓ (если не обработано)
2. DeepSeek API (умные ответы)
   ↓ (если DeepSeek недоступен)
3. Psychological Support Agent (психологические вопросы)
   ↓ (если не психологический контекст)
4. SFM Adapter (существующие агенты)
   ↓ (если SFM недоступен)
5. Fallback Mock (последний резерв)
```

---

## 💰 СТОИМОСТЬ И ЛИМИТЫ

### Цены DeepSeek:

- **Вход:** ~$0.001 за 1K токенов
- **Выход:** ~$0.002 за 1K токенов
- **Средний запрос:** ~500 токенов = **~$0.0005**

### Лимиты для пользователей:

```python
# В ai_assistant_router.py
def check_deepseek_rate_limit(user_id: str, subscription_level: str) -> bool:
    """Проверка лимитов для DeepSeek"""
    limits = {
        "free": 10,      # 10 запросов в день
        "trial": 50,     # 50 запросов в день
        "premium": 1000  # 1000 запросов в день
    }
    
    limit = limits.get(subscription_level, 10)
    # Проверка использования
    # ...
    return True
```

---

## 📊 ПРЕИМУЩЕСТВА DEEPSEEK

### ✅ Что получим:

1. **Умные ответы**
   - Разные ответы на разные вопросы
   - Понимание контекста
   - Естественные диалоги

2. **Поддержка диалога**
   - Помнит предыдущие сообщения
   - Контекстный разговор
   - Персонализация

3. **Низкая стоимость**
   - В 10-100 раз дешевле GPT-4
   - Доступно для всех пользователей

4. **Поддержка русского**
   - Отлично работает на русском
   - Понимает контекст

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **API Ключ:**
   - Хранить в переменных окружения
   - Не коммитить в репозиторий
   - Ротация ключей

2. **Стоимость:**
   - Мониторить использование
   - Установить лимиты
   - Кэшировать частые запросы

3. **Приватность:**
   - DeepSeek может хранить данные
   - Для приватных данных использовать локальную обработку

4. **Fallback:**
   - Всегда иметь fallback
   - Не зависеть только от DeepSeek

---

## 📋 TODO ЛИСТ

### Фаза 1: Настройка
- [ ] Получить API ключ DeepSeek
- [ ] Добавить в переменные окружения
- [ ] Протестировать подключение

### Фаза 2: DeepSeek Client
- [ ] Создать `deepseek_client.py`
- [ ] Реализовать метод `chat()`
- [ ] Добавить системные промпты
- [ ] Протестировать базовые запросы

### Фаза 3: Интеграция
- [ ] Модифицировать `ai_assistant_router.py`
- [ ] Добавить приоритет DeepSeek
- [ ] Добавить логирование
- [ ] Протестировать интеграцию

### Фаза 4: История диалога (опционально)
- [ ] Создать таблицу в БД
- [ ] Сохранение сообщений
- [ ] Передача истории в DeepSeek

### Фаза 5: Тестирование
- [ ] Тест разных типов вопросов
- [ ] Тест на русском языке
- [ ] Тест fallback логики
- [ ] Тест лимитов

---

**Статус:** ✅ **ПЛАН ГОТОВ К РЕАЛИЗАЦИИ**

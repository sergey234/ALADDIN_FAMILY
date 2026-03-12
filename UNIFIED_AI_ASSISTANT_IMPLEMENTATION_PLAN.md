# 🚀 ДЕТАЛЬНЫЙ ПЛАН ОБЪЕДИНЕНИЯ AI АССИСТЕНТОВ

**Дата:** 2026-03-12  
**Версия:** BUILD 115+  
**Статус:** 📋 ПОЛНЫЙ ПЛАН РЕАЛИЗАЦИИ

---

## 🎯 ЦЕЛЬ

Создать единую систему AI Assistant с возможностью выбора провайдера:
- **DeepSeek** - умные ответы через API
- **Гибридный агент** - локальная обработка + Psychological Support Agent
- **Автоматический выбор** - умная маршрутизация

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

### Компоненты:

```
┌─────────────────────────────────────────────────────────────┐
│                    МОБИЛЬНОЕ ПРИЛОЖЕНИЕ                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AIAssistantScreen                                    │  │
│  │  - UI для выбора провайдера                           │  │
│  │  - Определение контекста                              │  │
│  │  - Отображение метрик                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AIProviderManager (НОВЫЙ)                           │  │
│  │  - Управление провайдерами                             │  │
│  │  - Выбор провайдера                                    │  │
│  │  - Умная маршрутизация                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  APIService                                           │  │
│  │  - sendMessageToAI(provider:)                         │  │
│  │  - Методы для каждого провайдера                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      СЕРВЕР (Backend)                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ai_assistant_router.py                               │  │
│  │  - Маршрутизация запросов                              │  │
│  │  - Выбор провайдера                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AI Provider Router (НОВЫЙ)                           │  │
│  │  - Локальная обработка                                 │  │
│  │  - DeepSeek Client                                     │  │
│  │  - Psychological Support Agent                         │  │
│  │  - SFM Adapter                                         │  │
│  │  - Fallback Mock                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Metrics Collector (НОВЫЙ)                           │  │
│  │  - Сбор метрик                                         │  │
│  │  - Анализ производительности                           │  │
│  │  - Сохранение в БД                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 ЭТАПЫ РЕАЛИЗАЦИИ

### 🔴 ФАЗА 1: Создание AI Provider Manager (2-3 дня)

#### 1.1. Создать `Core/AI/AIProviderManager.swift`:

```swift
import Foundation

/// Тип AI провайдера
enum AIProvider: String, Codable, CaseIterable {
    case automatic = "automatic"           // Автоматический выбор
    case deepseek = "deepseek"             // DeepSeek API
    case hybrid = "hybrid"                 // Гибридный (локальный + Psychological)
    case local = "local"                   // Только локальная обработка
    case psychological = "psychological"   // Только Psychological Support Agent
    
    var displayName: String {
        switch self {
        case .automatic: return "Автоматический"
        case .deepseek: return "DeepSeek (Умный)"
        case .hybrid: return "Гибридный"
        case .local: return "Быстрый (Локальный)"
        case .psychological: return "Психолог"
        }
    }
    
    var description: String {
        switch self {
        case .automatic:
            return "Система автоматически выберет лучший AI для вашего вопроса"
        case .deepseek:
            return "Умные ответы с пониманием контекста и диалога"
        case .hybrid:
            return "Комбинация быстрой локальной обработки и психологической поддержки"
        case .local:
            return "Мгновенные ответы на основе локальных данных"
        case .psychological:
            return "Психологическая поддержка для всех возрастных групп"
        }
    }
    
    var icon: String {
        switch self {
        case .automatic: return "🤖"
        case .deepseek: return "🧠"
        case .hybrid: return "⚡"
        case .local: return "🚀"
        case .psychological: return "💚"
        }
    }
}

/// Менеджер AI провайдеров
class AIProviderManager {
    static let shared = AIProviderManager()
    
    @Published var selectedProvider: AIProvider = .automatic
    @Published var metrics: AIProviderMetrics = AIProviderMetrics()
    
    private let userDefaults = UserDefaults.standard
    private let providerKey = "selected_ai_provider"
    
    private init() {
        loadSelectedProvider()
    }
    
    /// Загрузка выбранного провайдера из UserDefaults
    private func loadSelectedProvider() {
        if let savedProvider = userDefaults.string(forKey: providerKey),
           let provider = AIProvider(rawValue: savedProvider) {
            selectedProvider = provider
        }
    }
    
    /// Сохранение выбранного провайдера
    func setProvider(_ provider: AIProvider) {
        selectedProvider = provider
        userDefaults.set(provider.rawValue, forKey: providerKey)
        logger.business("🤖 AI Provider changed to: \(provider.displayName)")
    }
    
    /// Автоматический выбор провайдера на основе контекста
    func selectProviderForContext(_ context: String, message: String) -> AIProvider {
        // Если пользователь выбрал конкретный провайдер - используем его
        if selectedProvider != .automatic {
            return selectedProvider
        }
        
        // Умная маршрутизация
        let lowerMessage = message.lowercased()
        
        // Психологические вопросы → Psychological Support Agent
        let psychologicalKeywords = [
            "грустно", "печально", "плохо", "депрессия", "тревожно",
            "волнуюсь", "боюсь", "страшно", "одиноко", "помощь",
            "поддержка", "психолог", "sad", "anxious", "lonely",
            "depression", "stress", "help", "support"
        ]
        
        for keyword in psychologicalKeywords {
            if lowerMessage.contains(keyword) {
                return .psychological
            }
        }
        
        // Кризисные ситуации → Psychological Support Agent
        let crisisKeywords = [
            "суицид", "убить себя", "не хочу жить", "конец",
            "suicide", "kill myself", "don't want to live"
        ]
        
        for keyword in crisisKeywords {
            if lowerMessage.contains(keyword) {
                return .psychological
            }
        }
        
        // Простые вопросы → Локальная обработка
        let simpleContexts = ["protection_status", "stats", "help"]
        if simpleContexts.contains(context) {
            return .local
        }
        
        // Сложные вопросы → DeepSeek
        return .deepseek
    }
    
    /// Обновление метрик
    func updateMetrics(provider: AIProvider, responseTime: TimeInterval, success: Bool) {
        metrics.update(provider: provider, responseTime: responseTime, success: success)
    }
}

/// Метрики провайдеров
struct AIProviderMetrics {
    var deepseekMetrics = ProviderMetrics()
    var hybridMetrics = ProviderMetrics()
    var localMetrics = ProviderMetrics()
    var psychologicalMetrics = ProviderMetrics()
    
    struct ProviderMetrics {
        var totalRequests: Int = 0
        var successfulRequests: Int = 0
        var averageResponseTime: TimeInterval = 0
        var totalResponseTime: TimeInterval = 0
        
        var successRate: Double {
            guard totalRequests > 0 else { return 0 }
            return Double(successfulRequests) / Double(totalRequests) * 100
        }
    }
    
    mutating func update(provider: AIProvider, responseTime: TimeInterval, success: Bool) {
        var metrics: ProviderMetrics
        
        switch provider {
        case .deepseek:
            metrics = deepseekMetrics
        case .hybrid:
            metrics = hybridMetrics
        case .local:
            metrics = localMetrics
        case .psychological:
            metrics = psychologicalMetrics
        case .automatic:
            return // Не обновляем метрики для автоматического выбора
        }
        
        metrics.totalRequests += 1
        if success {
            metrics.successfulRequests += 1
        }
        metrics.totalResponseTime += responseTime
        metrics.averageResponseTime = metrics.totalResponseTime / Double(metrics.totalRequests)
        
        switch provider {
        case .deepseek:
            deepseekMetrics = metrics
        case .hybrid:
            hybridMetrics = metrics
        case .local:
            localMetrics = metrics
        case .psychological:
            psychologicalMetrics = metrics
        case .automatic:
            break
        }
    }
}
```

---

#### 1.2. Модифицировать `Screens/06_AIAssistantScreen.swift`:

```swift
// Добавить состояние для выбора провайдера
@StateObject private var providerManager = AIProviderManager.shared
@State private var showProviderSelector = false

// Добавить UI для выбора провайдера
private var providerSelectorView: some View {
    VStack(alignment: .leading, spacing: 12) {
        Text("Выберите AI провайдера")
            .font(.headline)
            .padding(.bottom, 8)
        
        ForEach(AIProvider.allCases, id: \.self) { provider in
            ProviderRow(
                provider: provider,
                isSelected: providerManager.selectedProvider == provider,
                metrics: getMetrics(for: provider)
            ) {
                providerManager.setProvider(provider)
                showProviderSelector = false
            }
        }
        
        // Показать метрики
        if !providerManager.metrics.deepseekMetrics.totalRequests == 0 {
            MetricsView(metrics: providerManager.metrics)
        }
    }
    .padding()
}

// Модифицировать sendMessage
private func sendMessage() {
    let context = determineMessageContext(messageText)
    
    // Автоматический выбор провайдера
    let provider = providerManager.selectProviderForContext(context, message: messageText)
    
    logger.business("🤖 Using AI Provider: \(provider.displayName)")
    
    let startTime = Date()
    
    // Отправка в зависимости от провайдера
    switch provider {
    case .automatic, .deepseek:
        sendToDeepSeek(message: messageText, context: context)
    case .hybrid:
        sendToHybrid(message: messageText, context: context)
    case .local:
        sendLocal(message: messageText, context: context)
    case .psychological:
        sendToPsychological(message: messageText, context: context)
    }
    
    // Обновление метрик
    let responseTime = Date().timeIntervalSince(startTime)
    providerManager.updateMetrics(provider: provider, responseTime: responseTime, success: true)
}

// Добавить методы для каждого провайдера
private func sendToDeepSeek(message: String, context: String) {
    // Вызов DeepSeek API
    apiService.sendMessageToDeepSeek(message: message, context: context) { result in
        // Обработка ответа
    }
}

private func sendToHybrid(message: String, context: String) {
    // Сначала локальная обработка
    if let localResponse = processLocally(message: message, context: context) {
        // Если локальная обработка дала ответ - используем его
        addMessage(localResponse)
    } else {
        // Иначе отправляем в Psychological Support Agent
        sendToPsychological(message: message, context: context)
    }
}

private func sendLocal(message: String, context: String) {
    // Локальная обработка
    if let response = processLocally(message: message, context: context) {
        addMessage(response)
    } else {
        // Fallback на DeepSeek
        sendToDeepSeek(message: message, context: context)
    }
}

private func sendToPsychological(message: String, context: String) {
    // Вызов Psychological Support Agent
    apiService.requestPsychologicalSupport(message: message, context: context) { result in
        // Обработка ответа
    }
}
```

---

### 🟡 ФАЗА 2: Создание серверного AI Provider Router (2-3 дня)

#### 2.1. Создать `app/security/ai/ai_provider_router.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Provider Router
Маршрутизация запросов к разным AI провайдерам
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.security.ai.deepseek_client import deepseek_client
from app.security.ai_agents.psychological_support_agent import PsychologicalSupportAgent
from app.security.ai.local_processor import LocalAIProcessor

logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    """Типы AI провайдеров"""
    AUTOMATIC = "automatic"
    DEEPSEEK = "deepseek"
    HYBRID = "hybrid"
    LOCAL = "local"
    PSYCHOLOGICAL = "psychological"

class AIProviderRouter:
    """Роутер для маршрутизации запросов к AI провайдерам"""
    
    def __init__(self):
        self.deepseek_client = deepseek_client
        self.psychological_agent = PsychologicalSupportAgent()
        self.local_processor = LocalAIProcessor()
        self.metrics_collector = MetricsCollector()
    
    async def route_request(
        self,
        message: str,
        context: str,
        provider: str = "automatic",
        user_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Маршрутизация запроса к нужному провайдеру
        
        Args:
            message: Сообщение пользователя
            context: Контекст разговора
            provider: Выбранный провайдер
            user_id: ID пользователя
            conversation_history: История диалога
        
        Returns:
            Ответ от выбранного провайдера
        """
        start_time = datetime.now()
        
        # Автоматический выбор провайдера
        if provider == "automatic":
            provider = self._select_provider_automatically(message, context)
        
        try:
            # Маршрутизация
            if provider == "deepseek":
                response = await self._route_to_deepseek(
                    message, context, conversation_history
                )
            elif provider == "hybrid":
                response = await self._route_to_hybrid(
                    message, context, user_id, conversation_history
                )
            elif provider == "local":
                response = await self._route_to_local(message, context, user_id)
            elif provider == "psychological":
                response = await self._route_to_psychological(
                    message, context, user_id
                )
            else:
                # Fallback на DeepSeek
                response = await self._route_to_deepseek(
                    message, context, conversation_history
                )
            
            # Обновление метрик
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics_collector.record(
                provider=provider,
                response_time=response_time,
                success=True,
                user_id=user_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error routing to {provider}: {e}")
            
            # Fallback на другой провайдер
            return await self._fallback_route(message, context, provider)
    
    def _select_provider_automatically(self, message: str, context: str) -> str:
        """Автоматический выбор провайдера на основе контекста"""
        lower_message = message.lower()
        
        # Психологические вопросы
        psychological_keywords = [
            "грустно", "печально", "плохо", "депрессия", "тревожно",
            "волнуюсь", "боюсь", "страшно", "одиноко", "помощь",
            "поддержка", "психолог"
        ]
        
        if any(keyword in lower_message for keyword in psychological_keywords):
            return "psychological"
        
        # Кризисные ситуации
        crisis_keywords = ["суицид", "убить себя", "не хочу жить"]
        if any(keyword in lower_message for keyword in crisis_keywords):
            return "psychological"
        
        # Простые вопросы → локальная обработка
        simple_contexts = ["protection_status", "stats", "help"]
        if context in simple_contexts:
            return "local"
        
        # Сложные вопросы → DeepSeek
        return "deepseek"
    
    async def _route_to_deepseek(
        self,
        message: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """Маршрутизация к DeepSeek"""
        logger.info("🤖 Routing to DeepSeek")
        
        response = await self.deepseek_client.chat(
            message=message,
            context=context,
            conversation_history=conversation_history
        )
        
        if response:
            return {
                "response": response["response"],
                "confidence": response.get("confidence", 0.95),
                "provider": "deepseek",
                "suggestions": [],
                "follow_up_questions": []
            }
        
        # Fallback
        return await self._fallback_route(message, context, "deepseek")
    
    async def _route_to_hybrid(
        self,
        message: str,
        context: str,
        user_id: Optional[str],
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """Маршрутизация к гибридному агенту"""
        logger.info("⚡ Routing to Hybrid Agent")
        
        # Сначала локальная обработка
        local_response = self.local_processor.process(message, context, user_id)
        
        if local_response and local_response.get("success"):
            return {
                "response": local_response["response"],
                "confidence": local_response.get("confidence", 0.9),
                "provider": "hybrid_local",
                "suggestions": local_response.get("suggestions", []),
                "follow_up_questions": []
            }
        
        # Если локальная обработка не дала ответа - используем DeepSeek
        return await self._route_to_deepseek(message, context, conversation_history)
    
    async def _route_to_local(
        self,
        message: str,
        context: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Маршрутизация к локальной обработке"""
        logger.info("🚀 Routing to Local Processor")
        
        response = self.local_processor.process(message, context, user_id)
        
        if response and response.get("success"):
            return {
                "response": response["response"],
                "confidence": response.get("confidence", 0.9),
                "provider": "local",
                "suggestions": response.get("suggestions", []),
                "follow_up_questions": []
            }
        
        # Fallback на DeepSeek
        return await self._route_to_deepseek(message, context, None)
    
    async def _route_to_psychological(
        self,
        message: str,
        context: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Маршрутизация к Psychological Support Agent"""
        logger.info("💚 Routing to Psychological Support Agent")
        
        # Определяем возрастную группу
        age_group = self._determine_age_group(user_id)
        
        # Вызываем Psychological Support Agent
        support_response = self.psychological_agent.provide_emotional_support(
            user_id=user_id or "guest",
            message=message,
            age_group=age_group
        )
        
        return {
            "response": support_response.get("message", "Я здесь, чтобы поддержать вас."),
            "confidence": support_response.get("confidence", 0.95),
            "provider": "psychological",
            "suggestions": support_response.get("recommendations", []),
            "follow_up_questions": support_response.get("follow_up_questions", [])
        }
    
    async def _fallback_route(
        self,
        message: str,
        context: str,
        failed_provider: str
    ) -> Dict[str, Any]:
        """Fallback маршрутизация при ошибке"""
        logger.warning(f"⚠️ Fallback from {failed_provider}")
        
        # Пробуем другие провайдеры по порядку
        fallback_order = ["local", "deepseek", "psychological"]
        
        for provider in fallback_order:
            if provider == failed_provider:
                continue
            
            try:
                if provider == "local":
                    return await self._route_to_local(message, context, None)
                elif provider == "deepseek":
                    return await self._route_to_deepseek(message, context, None)
                elif provider == "psychological":
                    return await self._route_to_psychological(message, context, None)
            except Exception as e:
                logger.error(f"❌ Fallback to {provider} also failed: {e}")
                continue
        
        # Последний резерв - mock ответ
        return {
            "response": "Извините, произошла ошибка. Попробуйте позже.",
            "confidence": 0.0,
            "provider": "fallback",
            "suggestions": [],
            "follow_up_questions": []
        }
    
    def _determine_age_group(self, user_id: Optional[str]) -> Optional[str]:
        """Определение возрастной группы пользователя"""
        # TODO: Получить из профиля пользователя
        return None

class MetricsCollector:
    """Сборщик метрик для AI провайдеров"""
    
    def __init__(self):
        self.metrics = {}
    
    def record(
        self,
        provider: str,
        response_time: float,
        success: bool,
        user_id: Optional[str] = None
    ):
        """Запись метрики"""
        if provider not in self.metrics:
            self.metrics[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0.0,
                "average_response_time": 0.0
            }
        
        metrics = self.metrics[provider]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
        
        metrics["total_response_time"] += response_time
        metrics["average_response_time"] = (
            metrics["total_response_time"] / metrics["total_requests"]
        )
        
        logger.info(
            f"📊 Metrics for {provider}: "
            f"success_rate={metrics['successful_requests']/metrics['total_requests']*100:.1f}%, "
            f"avg_time={metrics['average_response_time']:.2f}s"
        )

# Singleton instance
ai_provider_router = AIProviderRouter()
```

---

#### 2.2. Модифицировать `security/api/routers/ai_assistant_router.py`:

```python
# Добавить импорт
from app.security.ai.ai_provider_router import ai_provider_router, AIProvider

# Модифицировать ai_assistant_chat endpoint
@router.post("/chat", response_model=ChatMessageResponse)
async def ai_assistant_chat(
    request: ChatMessageRequest,
    user: dict = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    AI помощник - обработка сообщений пользователя
    Теперь с поддержкой выбора провайдера!
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
        # Получаем выбранный провайдер из запроса (или "automatic" по умолчанию)
        provider = request.provider if hasattr(request, "provider") else "automatic"
        
        # Получаем историю диалога (можно добавить позже)
        conversation_history = []  # TODO: Получить из БД
        
        # Маршрутизация через AI Provider Router
        response = await ai_provider_router.route_request(
            message=request.message,
            context=request.context,
            provider=provider,
            user_id=user_id,
            conversation_history=conversation_history
        )
        
        return ChatMessageResponse(
            response=response["response"],
            confidence=response.get("confidence", 0.95),
            suggestions=response.get("suggestions", []),
            follow_up_questions=response.get("follow_up_questions", []),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        fallback = _get_fallback_response(request.context)
        return ChatMessageResponse(**fallback)
```

---

### 🟢 ФАЗА 3: Добавление локальной обработки (2-3 дня)

#### 3.1. Создать `app/security/ai/local_processor.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local AI Processor
Локальная обработка простых вопросов без запросов к серверу
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LocalAIProcessor:
    """Локальный процессор для простых вопросов"""
    
    def process(
        self,
        message: str,
        context: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Обработка сообщения локально
        
        Returns:
            Ответ или None, если не может обработать локально
        """
        # Обработка по контексту
        if context == "protection_status":
            return self._process_protection_status(user_id)
        elif context == "stats":
            return self._process_stats(user_id)
        elif context == "help":
            return self._process_help(message)
        
        # Если контекст не поддерживается - возвращаем None
        return None
    
    def _process_protection_status(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Обработка вопроса о статусе защиты"""
        # TODO: Получить реальные данные о статусе защиты
        # Пока возвращаем базовый ответ
        
        return {
            "success": True,
            "response": "Ваша защита ALADDIN активна! Все функции безопасности работают корректно.",
            "confidence": 0.9,
            "suggestions": [
                "Проверить статус защиты",
                "Посмотреть статистику",
                "Настроить параметры"
            ]
        }
    
    def _process_stats(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Обработка вопроса о статистике"""
        # TODO: Получить реальные данные статистики
        
        return {
            "success": True,
            "response": "За последнюю неделю обнаружено 12 угроз, все заблокированы.",
            "confidence": 0.9,
            "suggestions": [
                "Посмотреть детальную статистику",
                "Настроить уведомления"
            ]
        }
    
    def _process_help(self, message: str) -> Dict[str, Any]:
        """Обработка вопроса о помощи"""
        # TODO: Интеграция с FAQ из SupportScreen
        
        return {
            "success": True,
            "response": "Я могу помочь вам с вопросами безопасности, защиты семьи и настройками ALADDIN.",
            "confidence": 0.8,
            "suggestions": [
                "Как настроить защиту?",
                "Как добавить члена семьи?",
                "Как проверить угрозы?"
            ]
        }
```

---

### 🔵 ФАЗА 4: UI для выбора провайдера (1-2 дня)

#### 4.1. Создать `Screens/Components/ProviderSelectorView.swift`:

```swift
import SwiftUI

struct ProviderSelectorView: View {
    @ObservedObject var providerManager: AIProviderManager
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            List {
                Section(header: Text("Выберите AI провайдера")) {
                    ForEach(AIProvider.allCases, id: \.self) { provider in
                        ProviderRow(
                            provider: provider,
                            isSelected: providerManager.selectedProvider == provider,
                            metrics: getMetrics(for: provider)
                        ) {
                            providerManager.setProvider(provider)
                            isPresented = false
                        }
                    }
                }
                
                Section(header: Text("Метрики производительности")) {
                    MetricsView(metrics: providerManager.metrics)
                }
            }
            .navigationTitle("AI Провайдеры")
            .navigationBarItems(trailing: Button("Готово") {
                isPresented = false
            })
        }
    }
    
    private func getMetrics(for provider: AIProvider) -> AIProviderMetrics.ProviderMetrics {
        switch provider {
        case .deepseek:
            return providerManager.metrics.deepseekMetrics
        case .hybrid:
            return providerManager.metrics.hybridMetrics
        case .local:
            return providerManager.metrics.localMetrics
        case .psychological:
            return providerManager.metrics.psychologicalMetrics
        case .automatic:
            return AIProviderMetrics.ProviderMetrics()
        }
    }
}

struct ProviderRow: View {
    let provider: AIProvider
    let isSelected: Bool
    let metrics: AIProviderMetrics.ProviderMetrics
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Text(provider.icon)
                    .font(.title2)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(provider.displayName)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(provider.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                    
                    if metrics.totalRequests > 0 {
                        HStack(spacing: 8) {
                            Label("\(metrics.totalRequests)", systemImage: "number")
                            Label("\(Int(metrics.successRate))%", systemImage: "checkmark.circle")
                            Label("\(String(format: "%.1f", metrics.averageResponseTime))s", systemImage: "clock")
                        }
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.blue)
                }
            }
            .padding(.vertical, 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct MetricsView: View {
    let metrics: AIProviderMetrics
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Общая статистика")
                .font(.headline)
            
            MetricRow(
                name: "DeepSeek",
                requests: metrics.deepseekMetrics.totalRequests,
                successRate: metrics.deepseekMetrics.successRate,
                avgTime: metrics.deepseekMetrics.averageResponseTime
            )
            
            MetricRow(
                name: "Гибридный",
                requests: metrics.hybridMetrics.totalRequests,
                successRate: metrics.hybridMetrics.successRate,
                avgTime: metrics.hybridMetrics.averageResponseTime
            )
            
            MetricRow(
                name: "Локальный",
                requests: metrics.localMetrics.totalRequests,
                successRate: metrics.localMetrics.successRate,
                avgTime: metrics.localMetrics.averageResponseTime
            )
            
            MetricRow(
                name: "Психолог",
                requests: metrics.psychologicalMetrics.totalRequests,
                successRate: metrics.psychologicalMetrics.successRate,
                avgTime: metrics.psychologicalMetrics.averageResponseTime
            )
        }
    }
}

struct MetricRow: View {
    let name: String
    let requests: Int
    let successRate: Double
    let avgTime: TimeInterval
    
    var body: some View {
        HStack {
            Text(name)
                .font(.subheadline)
            
            Spacer()
            
            Text("\(requests) запросов")
            Text("\(Int(successRate))% успех")
            Text("\(String(format: "%.1f", avgTime))s")
        }
        .font(.caption)
        .foregroundColor(.secondary)
    }
}
```

---

### 🟣 ФАЗА 5: Метрики и аналитика (1 день)

#### 5.1. Создать таблицу метрик в БД:

```python
# В database/models.py
class AIProviderMetrics(Base):
    __tablename__ = "ai_provider_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    provider = Column(String)
    response_time = Column(Float)
    success = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.now)
```

#### 5.2. Endpoint для получения метрик:

```python
@router.get("/metrics", response_model=ProviderMetricsResponse)
async def get_provider_metrics(
    user: dict = Depends(get_current_user)
) -> ProviderMetricsResponse:
    """Получение метрик провайдеров для пользователя"""
    # TODO: Получить из БД
    return ProviderMetricsResponse(
        deepseek=metrics.deepseek,
        hybrid=metrics.hybrid,
        local=metrics.local,
        psychological=metrics.psychological
    )
```

---

## 📊 МЕТРИКИ УСПЕХА

### Ключевые метрики:

1. **Скорость ответа:**
   - Локальная обработка: < 100ms ✅
   - DeepSeek: 1-3 секунды ✅
   - Psychological Support Agent: 2-5 секунд ✅
   - Цель: < 3 секунды для 95% запросов

2. **Качество ответов:**
   - % персонализированных ответов
   - % релевантных ответов
   - Цель: > 80% персонализированных ответов

3. **Использование:**
   - Количество вопросов в день
   - Распределение по провайдерам
   - Цель: > 10 вопросов в день на пользователя

4. **Надежность:**
   - % успешных запросов
   - Время отклика
   - Цель: > 99% успешных запросов

---

## 📋 TODO ЛИСТ

### Фаза 1: AI Provider Manager
- [ ] Создать `AIProviderManager.swift`
- [ ] Добавить выбор провайдера
- [ ] Реализовать умную маршрутизацию
- [ ] Добавить метрики

### Фаза 2: Серверный Router
- [ ] Создать `ai_provider_router.py`
- [ ] Интегрировать все провайдеры
- [ ] Добавить fallback логику
- [ ] Модифицировать `ai_assistant_router.py`

### Фаза 3: Локальная обработка
- [ ] Создать `local_processor.py`
- [ ] Реализовать обработку простых вопросов
- [ ] Интегрировать с реальными данными

### Фаза 4: UI
- [ ] Создать `ProviderSelectorView.swift`
- [ ] Добавить выбор провайдера в `AIAssistantScreen`
- [ ] Показать метрики
- [ ] Добавить визуальные индикаторы

### Фаза 5: Метрики
- [ ] Создать таблицу в БД
- [ ] Endpoint для метрик
- [ ] Дашборд для пользователя

---

**Статус:** ✅ **ПЛАН ГОТОВ К РЕАЛИЗАЦИИ**

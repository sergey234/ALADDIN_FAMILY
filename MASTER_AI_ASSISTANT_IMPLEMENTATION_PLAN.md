# 🚀 ГЛАВНЫЙ ПЛАН РЕАЛИЗАЦИИ AI ASSISTANT - ПОЛНАЯ ИНТЕГРАЦИЯ

**Дата:** 2026-03-12  
**Версия:** BUILD 115+  
**Статус:** 📋 СВОДНЫЙ ПЛАН ВСЕХ КОМПОНЕНТОВ

---

## 📋 СОДЕРЖАНИЕ

1. [Обзор системы](#обзор-системы)
2. [Архитектура](#архитектура)
3. [Компоненты](#компоненты)
4. [План реализации](#план-реализации)
5. [Интеграция компонентов](#интеграция-компонентов)
6. [Метрики и аналитика](#метрики-и-аналитика)
7. [TODO лист](#todo-лист)

---

## 🎯 ОБЗОР СИСТЕМЫ

### Цель проекта

Создать единую систему AI Assistant, объединяющую:
- ✅ **DeepSeek** - умные ответы через API
- ✅ **Гибридный агент** - локальная обработка + Psychological Support Agent
- ✅ **Локальная обработка** - быстрые ответы на основе реальных данных
- ✅ **Psychological Support Agent** - психологическая поддержка
- ✅ **FAQ интеграция** - использование Help & Support раздела
- ✅ **Выбор провайдера** - пользователь может выбирать AI провайдера
- ✅ **Умная маршрутизация** - автоматический выбор лучшего провайдера

---

## 🏗️ АРХИТЕКТУРА

### Полная архитектура системы:

```
┌─────────────────────────────────────────────────────────────────┐
│              МОБИЛЬНОЕ ПРИЛОЖЕНИЕ (iOS)                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AIAssistantScreen                                       │  │
│  │  - Чат интерфейс                                         │  │
│  │  - Выбор провайдера (UI)                                 │  │
│  │  - Определение контекста                                 │  │
│  │  - Отображение метрик                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AIProviderManager                                       │  │
│  │  - Управление провайдерами                               │  │
│  │  - Выбор провайдера                                      │  │
│  │  - Умная маршрутизация                                   │  │
│  │  - Метрики                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FAQManager                                              │  │
│  │  - Единая база FAQ                                       │  │
│  │  - Поиск по FAQ                                          │  │
│  │  - Использование в AI Assistant                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AILocalResponseHelper                                   │  │
│  │  - Локальная обработка простых вопросов                  │  │
│  │  - Использование FAQ                                     │  │
│  │  - Использование реальных данных                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  APIService                                              │  │
│  │  - sendMessageToAI(provider:)                            │  │
│  │  - sendMessageToDeepSeek()                               │  │
│  │  - requestPsychologicalSupport()                         │  │
│  │  - Методы для каждого провайдера                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      СЕРВЕР (Backend)                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ai_assistant_router.py                                 │  │
│  │  - Маршрутизация запросов                                │  │
│  │  - Выбор провайдера                                      │  │
│  │  - Обработка запросов                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AI Provider Router                                      │  │
│  │  - Маршрутизация к провайдерам                           │  │
│  │  - Приоритеты обработки                                  │  │
│  │  - Fallback логика                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ПРИОРИТЕТЫ ОБРАБОТКИ:                                   │  │
│  │                                                           │  │
│  │  1. Локальная обработка                                  │  │
│  │     (простые вопросы + FAQ)                              │  │
│  │                                                           │  │
│  │  2. DeepSeek API                                         │  │
│  │     (умные ответы)                                        │  │
│  │                                                           │  │
│  │  3. Psychological Support Agent                          │  │
│  │     (психологические вопросы)                            │  │
│  │                                                           │  │
│  │  4. SFM Adapter                                          │  │
│  │     (существующие агенты)                                 │  │
│  │                                                           │  │
│  │  5. Fallback Mock                                        │  │
│  │     (последний резерв)                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Провайдеры:                                             │  │
│  │                                                           │  │
│  │  • LocalAIProcessor                                       │  │
│  │    - Обработка простых вопросов                          │  │
│  │    - Использование FAQ                                    │  │
│  │    - Использование реальных данных                        │  │
│  │                                                           │  │
│  │  • DeepSeekClient                                        │  │
│  │    - OpenAI-совместимый API                              │  │
│  │    - Умные ответы с контекстом                            │  │
│  │    - Поддержка диалога                                    │  │
│  │                                                           │  │
│  │  • PsychologicalSupportAgent                             │  │
│  │    - Психологическая поддержка                            │  │
│  │    - Детский психолог                                    │  │
│  │    - Кризисная поддержка                                  │  │
│  │                                                           │  │
│  │  • MetricsCollector                                      │  │
│  │    - Сбор метрик                                          │  │
│  │    - Анализ производительности                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 КОМПОНЕНТЫ

### 1. AI Provider Manager

**Файл:** `Core/AI/AIProviderManager.swift`

**Функции:**
- Управление выбором провайдера
- Умная маршрутизация на основе контекста
- Сбор метрик производительности
- Сохранение предпочтений пользователя

**Типы провайдеров:**
- `automatic` - автоматический выбор
- `deepseek` - DeepSeek API
- `hybrid` - гибридный (локальный + Psychological)
- `local` - только локальная обработка
- `psychological` - только Psychological Support Agent

---

### 2. FAQ Manager

**Файл:** `Core/Managers/FAQManager.swift`

**Функции:**
- Единая база FAQ для SupportScreen и AI Assistant
- Поиск по FAQ на основе запроса пользователя
- Форматирование FAQ для ответов AI Assistant
- Категоризация FAQ

**Интеграция:**
- Используется в `SupportScreen` для отображения FAQ
- Используется в `AIAssistantScreen` для локальной обработки "help"
- Используется в `LocalAIProcessor` на сервере

---

### 3. AI Local Response Helper

**Файл:** `Screens/06_AIAssistantScreen.swift` (внутренняя структура)

**Функции:**
- Локальная обработка простых вопросов
- Использование реальных данных пользователя
- Использование FAQ для ответов
- Форматирование ответов

**Контексты обработки:**
- `protection_status` - статус защиты
- `stats` - статистика
- `threat_analysis` - анализ угроз
- `help` - помощь (использует FAQ)
- `family_info` - информация о семье

---

### 4. DeepSeek Client

**Файл:** `app/security/ai/deepseek_client.py` (сервер)

**Функции:**
- Вызов DeepSeek API
- Формирование системных промптов
- Поддержка истории диалога
- Обработка ошибок и fallback

**Конфигурация:**
- API ключ из переменных окружения
- Модель: `deepseek-chat`
- Temperature: 0.7
- Max tokens: 1000

---

### 5. Psychological Support Agent

**Файл:** `app/security/ai_agents/psychological_support_agent.py` (сервер)

**Функции:**
- Психологическая поддержка для всех возрастных групп
- Детский психолог (3-17 лет)
- Кризисная поддержка
- Анализ эмоций

**Интеграция:**
- Вызывается через SFM Adapter
- Используется для психологических вопросов
- Автоматически определяется по ключевым словам

---

### 6. Local AI Processor

**Файл:** `app/security/ai/local_processor.py` (сервер)

**Функции:**
- Локальная обработка простых вопросов
- Использование FAQ из базы данных
- Использование реальных данных пользователя
- Быстрые ответы без запросов к внешним API

**Контексты:**
- `help` - поиск по FAQ
- `protection_status` - статус защиты
- `stats` - статистика

---

### 7. AI Provider Router

**Файл:** `app/security/ai/ai_provider_router.py` (сервер)

**Функции:**
- Маршрутизация запросов к нужному провайдеру
- Автоматический выбор провайдера
- Fallback логика
- Сбор метрик

**Приоритеты:**
1. Локальная обработка (FAQ + реальные данные)
2. DeepSeek API
3. Psychological Support Agent
4. SFM Adapter
5. Fallback Mock

---

## 📋 ПЛАН РЕАЛИЗАЦИИ

### 🔴 ЭТАП 1: Базовая инфраструктура (3-4 дня)

#### 1.1. Создать FAQManager (1 день)

**Файл:** `Core/Managers/FAQManager.swift`

```swift
import Foundation

class FAQManager {
    static let shared = FAQManager()
    
    struct FAQItem: Identifiable, Codable {
        let id: String
        let icon: String
        let question: String
        let answer: String
        let category: String
        let keywords: [String]
    }
    
    func getAllFAQItems() -> [FAQItem] {
        // Загрузка всех FAQ элементов
    }
    
    func searchFAQ(query: String, limit: Int = 3) -> [FAQItem] {
        // Поиск по FAQ
    }
    
    func formatFAQForAI(_ faqItems: [FAQItem]) -> String {
        // Форматирование для AI Assistant
    }
}
```

**Задачи:**
- [ ] Создать структуру FAQItem
- [ ] Реализовать getAllFAQItems()
- [ ] Реализовать searchFAQ()
- [ ] Реализовать formatFAQForAI()
- [ ] Добавить локализацию

---

#### 1.2. Создать AIProviderManager (1 день)

**Файл:** `Core/AI/AIProviderManager.swift`

```swift
import Foundation

enum AIProvider: String, Codable, CaseIterable {
    case automatic = "automatic"
    case deepseek = "deepseek"
    case hybrid = "hybrid"
    case local = "local"
    case psychological = "psychological"
    
    var displayName: String { /* ... */ }
    var description: String { /* ... */ }
    var icon: String { /* ... */ }
}

class AIProviderManager {
    static let shared = AIProviderManager()
    
    @Published var selectedProvider: AIProvider = .automatic
    @Published var metrics: AIProviderMetrics = AIProviderMetrics()
    
    func selectProviderForContext(_ context: String, message: String) -> AIProvider {
        // Умная маршрутизация
    }
    
    func updateMetrics(provider: AIProvider, responseTime: TimeInterval, success: Bool) {
        // Обновление метрик
    }
}
```

**Задачи:**
- [ ] Создать enum AIProvider
- [ ] Реализовать AIProviderManager
- [ ] Реализовать умную маршрутизацию
- [ ] Реализовать сбор метрик
- [ ] Сохранение предпочтений в UserDefaults

---

#### 1.3. Интегрировать FAQManager в SupportScreen (1 день)

**Файл:** `Screens/13_SupportScreen.swift`

```swift
// Заменить локальную структуру FAQItem на FAQManager.FAQItem
@State private var faqItems: [FAQManager.FAQItem] = []

private func initializeFAQItems() {
    faqItems = FAQManager.shared.getAllFAQItems()
}
```

**Задачи:**
- [ ] Заменить локальную структуру FAQItem
- [ ] Использовать FAQManager.shared
- [ ] Протестировать отображение FAQ

---

#### 1.4. Создать AILocalResponseHelper (1 день)

**Файл:** `Screens/06_AIAssistantScreen.swift` (внутренняя структура)

```swift
private struct AILocalResponseHelper {
    let localizationManager: LocalizationManager
    let apiService: APIService
    let faqManager: FAQManager
    
    func getLocalResponse(context: String, message: String) -> String? {
        switch context {
        case "protection_status":
            return getProtectionStatusResponse()
        case "stats":
            return getStatsResponse()
        case "threat_analysis":
            return getThreatAnalysisResponse()
        case "help":
            return getHelpResponse(message: message)
        case "family_info":
            return getFamilyInfoResponse()
        default:
            return nil
        }
    }
    
    func getHelpResponse(message: String) -> String? {
        // Поиск по FAQ
        let relevantFAQ = faqManager.searchFAQ(query: message, limit: 3)
        if !relevantFAQ.isEmpty {
            return faqManager.formatFAQForAI(relevantFAQ)
        }
        return nil
    }
    
    // ... другие методы
}
```

**Задачи:**
- [ ] Создать структуру AILocalResponseHelper
- [ ] Реализовать getLocalResponse()
- [ ] Реализовать getHelpResponse() с использованием FAQ
- [ ] Реализовать другие методы получения данных

---

### 🟡 ЭТАП 2: Интеграция в AI Assistant (3-4 дня)

#### 2.1. Модифицировать AIAssistantScreen (2 дня)

**Файл:** `Screens/06_AIAssistantScreen.swift`

**Изменения:**

1. Добавить выбор провайдера:
```swift
@StateObject private var providerManager = AIProviderManager.shared
@State private var showProviderSelector = false
```

2. Модифицировать sendMessage():
```swift
private func sendMessage() {
    let context = determineMessageContext(messageText)
    
    // Автоматический выбор провайдера
    let provider = providerManager.selectProviderForContext(context, message: messageText)
    
    logger.business("🤖 Using AI Provider: \(provider.displayName)")
    
    let startTime = Date()
    
    // Сначала проверяем локальную обработку
    let localHelper = AILocalResponseHelper(
        localizationManager: localizationManager,
        apiService: apiService,
        faqManager: FAQManager.shared
    )
    
    if let localResponse = localHelper.getLocalResponse(context: context, message: messageText) {
        // Используем локальный ответ
        addMessage(localResponse)
        let responseTime = Date().timeIntervalSince(startTime)
        providerManager.updateMetrics(provider: .local, responseTime: responseTime, success: true)
        return
    }
    
    // Отправка в зависимости от провайдера
    switch provider {
    case .automatic, .deepseek:
        sendToDeepSeek(message: messageText, context: context)
    case .hybrid:
        sendToHybrid(message: messageText, context: context)
    case .local:
        // Уже обработано локально выше
        break
    case .psychological:
        sendToPsychological(message: messageText, context: context)
    }
    
    // Обновление метрик
    let responseTime = Date().timeIntervalSince(startTime)
    providerManager.updateMetrics(provider: provider, responseTime: responseTime, success: true)
}
```

3. Добавить методы для каждого провайдера:
```swift
private func sendToDeepSeek(message: String, context: String) {
    apiService.sendMessageToDeepSeek(message: message, context: context) { result in
        // Обработка ответа
    }
}

private func sendToHybrid(message: String, context: String) {
    // Сначала локальная обработка
    if let localResponse = processLocally(message: message, context: context) {
        addMessage(localResponse)
    } else {
        // Иначе отправляем в Psychological Support Agent
        sendToPsychological(message: message, context: context)
    }
}

private func sendToPsychological(message: String, context: String) {
    apiService.requestPsychologicalSupport(message: message, context: context) { result in
        // Обработка ответа
    }
}
```

**Задачи:**
- [ ] Добавить AIProviderManager
- [ ] Модифицировать sendMessage()
- [ ] Добавить методы для каждого провайдера
- [ ] Добавить UI для выбора провайдера
- [ ] Добавить отображение метрик

---

#### 2.2. Создать UI для выбора провайдера (1 день)

**Файл:** `Screens/Components/ProviderSelectorView.swift`

```swift
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
        }
    }
}
```

**Задачи:**
- [ ] Создать ProviderSelectorView
- [ ] Создать ProviderRow
- [ ] Создать MetricsView
- [ ] Интегрировать в AIAssistantScreen

---

#### 2.3. Добавить методы в APIService (1 день)

**Файл:** `Core/Network/APIService.swift`

```swift
// MARK: - DeepSeek API
func sendMessageToDeepSeek(
    message: String,
    context: String,
    completion: @escaping (Result<ChatMessageResponse, Error>) -> Void
) {
    // Вызов DeepSeek API
}

// MARK: - Psychological Support API
func requestPsychologicalSupport(
    message: String,
    context: String,
    completion: @escaping (Result<PsychologicalSupportResponse, Error>) -> Void
) {
    // Вызов Psychological Support Agent
}
```

**Задачи:**
- [ ] Добавить sendMessageToDeepSeek()
- [ ] Добавить requestPsychologicalSupport()
- [ ] Добавить другие методы провайдеров
- [ ] Добавить endpoints в AppConfig

---

### 🟢 ЭТАП 3: Серверная реализация (4-5 дней)

#### 3.1. Создать DeepSeek Client (1 день)

**Файл:** `app/security/ai/deepseek_client.py`

```python
class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.enabled = bool(self.api_key)
    
    async def chat(
        self,
        message: str,
        context: str = "general",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        # Вызов DeepSeek API
        pass
```

**Задачи:**
- [ ] Создать DeepSeekClient
- [ ] Реализовать метод chat()
- [ ] Добавить системные промпты
- [ ] Добавить обработку ошибок

---

#### 3.2. Создать Local AI Processor (1 день)

**Файл:** `app/security/ai/local_processor.py`

```python
class LocalAIProcessor:
    def __init__(self):
        self.faq_database = self._load_faq_database()
    
    def process(
        self,
        message: str,
        context: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if context == "help":
            return self._process_help(message)
        elif context == "protection_status":
            return self._process_protection_status(user_id)
        # ...
    
    def _process_help(self, message: str) -> Dict[str, Any]:
        # Поиск по FAQ
        relevant_faq = self._search_faq(message, limit=3)
        # Форматирование ответа
        pass
```

**Задачи:**
- [ ] Создать LocalAIProcessor
- [ ] Реализовать поиск по FAQ
- [ ] Реализовать обработку простых вопросов
- [ ] Интегрировать с БД FAQ

---

#### 3.3. Создать AI Provider Router (2 дня)

**Файл:** `app/security/ai/ai_provider_router.py`

```python
class AIProviderRouter:
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
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Маршрутизация к нужному провайдеру
        pass
```

**Задачи:**
- [ ] Создать AIProviderRouter
- [ ] Реализовать route_request()
- [ ] Реализовать автоматический выбор провайдера
- [ ] Реализовать fallback логику
- [ ] Добавить сбор метрик

---

#### 3.4. Модифицировать ai_assistant_router.py (1 день)

**Файл:** `security/api/routers/ai_assistant_router.py`

```python
from app.security.ai.ai_provider_router import ai_provider_router

@router.post("/chat", response_model=ChatMessageResponse)
async def ai_assistant_chat(
    request: ChatMessageRequest,
    user: dict = Depends(get_current_user)
) -> ChatMessageResponse:
    # Получаем выбранный провайдер
    provider = request.provider if hasattr(request, "provider") else "automatic"
    
    # Маршрутизация через AI Provider Router
    response = await ai_provider_router.route_request(
        message=request.message,
        context=request.context,
        provider=provider,
        user_id=user["user_id"]
    )
    
    return ChatMessageResponse(**response)
```

**Задачи:**
- [ ] Импортировать ai_provider_router
- [ ] Модифицировать ai_assistant_chat endpoint
- [ ] Добавить поддержку выбора провайдера
- [ ] Протестировать интеграцию

---

### 🔵 ЭТАП 4: Интеграция Psychological Support Agent (2-3 дня)

#### 4.1. Создать endpoints для Psychological Support (1 день)

**Файл:** `security/api/routers/ai_assistant_router.py`

```python
@router.post("/psychological_support", response_model=ChatMessageResponse)
async def psychological_support(
    request: ChatMessageRequest,
    age_group: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
) -> ChatMessageResponse:
    # Вызов Psychological Support Agent
    pass

@router.post("/analyze_emotions", response_model=EmotionalAnalysisResponse)
async def analyze_emotions(
    request: ChatMessageRequest,
    user: dict = Depends(get_current_user)
) -> EmotionalAnalysisResponse:
    # Анализ эмоций
    pass

@router.post("/crisis_support", response_model=CrisisSupportResponse)
async def crisis_support(
    request: CrisisSupportRequest,
    user: dict = Depends(get_current_user)
) -> CrisisSupportResponse:
    # Кризисная поддержка
    pass
```

**Задачи:**
- [ ] Создать endpoint для психологической поддержки
- [ ] Создать endpoint для анализа эмоций
- [ ] Создать endpoint для кризисной поддержки
- [ ] Добавить модели запросов/ответов

---

#### 4.2. Интегрировать в AI Assistant (1 день)

**Файл:** `Screens/06_AIAssistantScreen.swift`

```swift
// Модифицировать determineMessageContext для определения психологических вопросов
private func determineMessageContext(_ message: String) -> String {
    let lowerMessage = message.lowercased()
    
    // Проверка на психологические вопросы (ПЕРВЫМ!)
    let psychologicalKeywords = [
        "грустно", "печально", "плохо", "депрессия", "тревожно",
        "волнуюсь", "боюсь", "страшно", "одиноко", "помощь",
        "поддержка", "психолог"
    ]
    
    for keyword in psychologicalKeywords {
        if lowerMessage.contains(keyword) {
            return "psychological_support"
        }
    }
    
    // Остальные проверки...
}
```

**Задачи:**
- [ ] Модифицировать determineMessageContext()
- [ ] Добавить определение кризисных ситуаций
- [ ] Интегрировать вызовы Psychological Support Agent

---

### 🟣 ЭТАП 5: Локализация и тестирование (2-3 дня)

#### 5.1. Добавить локализацию (1 день)

**Файл:** `Core/Localization/LocalizationManager.swift`

**Ключи для добавления:**
- FAQ вопросы и ответы
- AI Provider названия и описания
- Метрики и аналитика
- Сообщения об ошибках

**Задачи:**
- [ ] Добавить ключи для FAQ
- [ ] Добавить ключи для AI Provider
- [ ] Добавить ключи для метрик
- [ ] Протестировать на русском и английском

---

#### 5.2. Тестирование (1-2 дня)

**Тесты:**
- [ ] Тест локальной обработки с FAQ
- [ ] Тест DeepSeek API
- [ ] Тест Psychological Support Agent
- [ ] Тест умной маршрутизации
- [ ] Тест fallback логики
- [ ] Тест метрик

---

## 🔗 ИНТЕГРАЦИЯ КОМПОНЕНТОВ

### Взаимодействие компонентов:

```
1. Пользователь задает вопрос
   ↓
2. AIAssistantScreen определяет контекст
   ↓
3. AIProviderManager выбирает провайдера
   ↓
4. Проверка локальной обработки:
   - Если простой вопрос → AILocalResponseHelper
   - Если "help" → FAQManager.searchFAQ()
   - Если есть локальный ответ → возврат
   ↓
5. Если нет локального ответа → отправка на сервер
   ↓
6. AI Provider Router маршрутизирует запрос:
   - Локальная обработка (если не обработано на клиенте)
   - DeepSeek API
   - Psychological Support Agent
   - SFM Adapter
   - Fallback Mock
   ↓
7. Ответ возвращается пользователю
   ↓
8. Метрики обновляются
```

---

## 📊 МЕТРИКИ И АНАЛИТИКА

### Ключевые метрики:

1. **Скорость ответа:**
   - Локальная обработка: < 100ms
   - DeepSeek: 1-3 секунды
   - Psychological Support Agent: 2-5 секунд
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

5. **Удовлетворенность:**
   - Рейтинг ответов (👍/👎)
   - Повторные обращения
   - Цель: > 4.5/5 звезд

---

## 📋 TODO ЛИСТ

### ЭТАП 1: Базовая инфраструктура
- [ ] Создать FAQManager.swift
- [ ] Создать AIProviderManager.swift
- [ ] Интегрировать FAQManager в SupportScreen
- [ ] Создать AILocalResponseHelper

### ЭТАП 2: Интеграция в AI Assistant
- [ ] Модифицировать AIAssistantScreen.swift
- [ ] Создать ProviderSelectorView.swift
- [ ] Добавить методы в APIService.swift
- [ ] Добавить endpoints в AppConfig.swift

### ЭТАП 3: Серверная реализация
- [ ] Создать deepseek_client.py
- [ ] Создать local_processor.py
- [ ] Создать ai_provider_router.py
- [ ] Модифицировать ai_assistant_router.py

### ЭТАП 4: Psychological Support Agent
- [ ] Создать endpoints для Psychological Support
- [ ] Интегрировать в AI Assistant
- [ ] Добавить определение кризисных ситуаций

### ЭТАП 5: Локализация и тестирование
- [ ] Добавить локализацию
- [ ] Тестирование всех компонентов
- [ ] Оптимизация производительности

---

## ✅ РЕЗУЛЬТАТ

### После реализации получим:

1. **Единая система AI Assistant:**
   - Выбор провайдера пользователем
   - Автоматическая маршрутизация
   - Интеграция всех компонентов

2. **Все функции:**
   - DeepSeek для умных ответов
   - Локальная обработка для быстрых ответов
   - FAQ интеграция для помощи
   - Psychological Support Agent для психологических вопросов

3. **Лучший UX:**
   - Простой выбор провайдера
   - Показ метрик
   - Визуальные индикаторы
   - Быстрые ответы

4. **Надежность:**
   - Многоуровневый fallback
   - Всегда есть ответ
   - Мониторинг производительности

---

**Статус:** ✅ **СВОДНЫЙ ПЛАН ГОТОВ К РЕАЛИЗАЦИИ**

**Время реализации:** 14-19 дней

**Приоритет:** 🔴 ВЫСОКИЙ

# 🚀 ПЛАН ПОДКЛЮЧЕНИЯ PSYCHOLOGICAL SUPPORT AGENT К МОБИЛЬНОМУ ПРИЛОЖЕНИЮ

**Дата:** 2026-03-12  
**Версия:** BUILD 115+  
**Статус:** 📋 ПЛАН ГОТОВ К РЕАЛИЗАЦИИ

---

## 🎯 ЦЕЛЬ

Подключить **Psychological Support Agent** (Супер AI Асистент) к мобильному приложению iOS, объединив его с существующим AI Assistant для создания полноценного Супер AI Асистента.

---

## 📋 ЭТАПЫ РЕАЛИЗАЦИИ

### 🔴 ФАЗА 1: Создание API Endpoints (1-2 дня)

#### 1.1. Добавить endpoints в `security/api/routers/ai_assistant_router.py`

**Новые endpoints:**

```python
# 1. Психологическая поддержка
@router.post("/psychological_support", response_model=ChatMessageResponse)
async def psychological_support(
    request: ChatMessageRequest,
    age_group: Optional[str] = Query(None, description="Возрастная группа"),
    user: dict = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    Психологическая поддержка через AI
    
    Args:
        request: Запрос с сообщением пользователя
        age_group: Возрастная группа (child_3_6, child_7_12, teen_13_17, adult_18_65, elderly_65_plus)
    
    Returns:
        Ответ психологической поддержки
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "message": request.message,
                "user_id": user["user_id"],
                "age_group": age_group,
                "timestamp": request.timestamp.isoformat() if request.timestamp else datetime.now().isoformat()
            }
            success, result, message = sfm_adapter.execute_function("psychological_support", data)
            
            if success:
                return ChatMessageResponse(
                    response=result.get("message", "Я здесь, чтобы поддержать вас."),
                    confidence=result.get("confidence", 0.95),
                    suggestions=result.get("recommendations", []),
                    follow_up_questions=result.get("follow_up_questions", []),
                    timestamp=datetime.now()
                )
        
        # Fallback
        return ChatMessageResponse(
            response="Я здесь, чтобы поддержать вас. Расскажите, что вас беспокоит?",
            confidence=0.9,
            suggestions=["Попробуйте дыхательные упражнения", "Свяжитесь с близкими"],
            follow_up_questions=["Как вы себя чувствуете?", "Что вас беспокоит?"],
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Ошибка психологической поддержки: {e}")
        return ChatMessageResponse(
            response="Извините, произошла ошибка. Попробуйте позже.",
            confidence=0.0,
            timestamp=datetime.now()
        )

# 2. Анализ эмоций
@router.post("/analyze_emotions", response_model=EmotionalAnalysisResponse)
async def analyze_emotions(
    request: ChatMessageRequest,
    user: dict = Depends(get_current_user)
) -> EmotionalAnalysisResponse:
    """
    Анализ эмоционального состояния пользователя
    
    Returns:
        Результат анализа эмоций
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "text_input": request.message,
                "user_id": user["user_id"]
            }
            success, result, message = sfm_adapter.execute_function("analyze_emotional_state", data)
            
            if success:
                return EmotionalAnalysisResponse(
                    dominant_emotion=result.get("dominant_emotion", "calm"),
                    confidence=result.get("confidence", 0.0),
                    risk_level=result.get("risk_level", "low"),
                    recommendations=result.get("recommendations", [])
                )
        
        # Fallback
        return EmotionalAnalysisResponse(
            dominant_emotion="calm",
            confidence=0.0,
            risk_level="low",
            recommendations=[]
        )
    except Exception as e:
        logger.error(f"Ошибка анализа эмоций: {e}")
        return EmotionalAnalysisResponse(
            dominant_emotion="unknown",
            confidence=0.0,
            risk_level="unknown",
            recommendations=[]
        )

# 3. Кризисная поддержка
@router.post("/crisis_support", response_model=CrisisSupportResponse)
async def crisis_support(
    request: CrisisSupportRequest,
    user: dict = Depends(get_current_user)
) -> CrisisSupportResponse:
    """
    Экстренная кризисная психологическая поддержка
    
    Args:
        request: Запрос с типом кризиса
    
    Returns:
        Кризисная поддержка и действия
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "user_id": user["user_id"],
                "crisis_type": request.crisis_type
            }
            success, result, message = sfm_adapter.execute_function("emergency_support", data)
            
            if success:
                return CrisisSupportResponse(
                    message=result.get("message", "Помощь уже в пути."),
                    crisis_type=result.get("crisis_type", request.crisis_type),
                    immediate_actions=result.get("immediate_actions", []),
                    timestamp=datetime.now()
                )
        
        # Fallback
        return CrisisSupportResponse(
            message="Сейчас с вами свяжется специалист. Вы не одни.",
            crisis_type=request.crisis_type,
            immediate_actions=["Связаться с кризисной службой", "Уведомить семью"],
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Ошибка кризисной поддержки: {e}")
        return CrisisSupportResponse(
            message="Ошибка. Немедленно обратитесь к специалисту.",
            crisis_type=request.crisis_type,
            immediate_actions=["Позвоните 112", "Обратитесь к психологу"],
            timestamp=datetime.now()
        )

# 4. Психологический профиль
@router.get("/psychological_profile", response_model=PsychologicalProfileResponse)
async def get_psychological_profile(
    user: dict = Depends(get_current_user)
) -> PsychologicalProfileResponse:
    """
    Получение психологического профиля пользователя
    
    Returns:
        Психологический профиль и рекомендации
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"user_id": user["user_id"]}
            success, result, message = sfm_adapter.execute_function("get_user_psychological_profile", data)
            
            if success:
                return PsychologicalProfileResponse(
                    user_id=result.get("user_id", user["user_id"]),
                    emotional_trends=result.get("emotional_trends", {}),
                    recent_sessions=result.get("recent_sessions", []),
                    recommendations=result.get("recommendations", [])
                )
        
        # Fallback
        return PsychologicalProfileResponse(
            user_id=user["user_id"],
            emotional_trends={"trend": "stable", "confidence": 0.0},
            recent_sessions=[],
            recommendations=[]
        )
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {e}")
        return PsychologicalProfileResponse(
            user_id=user["user_id"],
            emotional_trends={"trend": "unknown", "confidence": 0.0},
            recent_sessions=[],
            recommendations=[]
        )
```

**Новые модели:**

```python
class CrisisSupportRequest(BaseModel):
    crisis_type: str = Field(..., description="Тип кризиса (suicidal_ideation, severe_depression, anxiety_attack)")

class CrisisSupportResponse(BaseModel):
    message: str
    crisis_type: str
    immediate_actions: List[str]
    timestamp: datetime

class EmotionalAnalysisResponse(BaseModel):
    dominant_emotion: str
    confidence: float
    risk_level: str
    recommendations: List[str]

class PsychologicalProfileResponse(BaseModel):
    user_id: str
    emotional_trends: Dict[str, Any]
    recent_sessions: List[Dict[str, Any]]
    recommendations: List[str]
```

---

### 🟡 ФАЗА 2: Регистрация функций в SFM (1 день)

#### 2.1. Зарегистрировать функции Psychological Support Agent в SFM:

```python
# В SFM Registry добавить:
{
    "function_name": "psychological_support",
    "agent": "PsychologicalSupportAgent",
    "method": "provide_emotional_support",
    "description": "Психологическая поддержка пользователя"
},
{
    "function_name": "analyze_emotional_state",
    "agent": "PsychologicalSupportAgent",
    "method": "analyze_emotional_state",
    "description": "Анализ эмоционального состояния"
},
{
    "function_name": "emergency_support",
    "agent": "PsychologicalSupportAgent",
    "method": "emergency_support",
    "description": "Экстренная кризисная поддержка"
},
{
    "function_name": "get_user_psychological_profile",
    "agent": "PsychologicalSupportAgent",
    "method": "get_user_psychological_profile",
    "description": "Получение психологического профиля"
}
```

---

### 🟢 ФАЗА 3: Интеграция в мобильное приложение (2-3 дня)

#### 3.1. Добавить модели в `Core/Models/APIModels.swift`:

```swift
// Психологическая поддержка
struct PsychologicalSupportResponse: Codable {
    let message: String
    let supportType: String
    let sessionId: String
    let timestamp: Date
}

// Анализ эмоций
struct EmotionalAnalysisResponse: Codable {
    let dominantEmotion: String
    let confidence: Double
    let riskLevel: String
    let recommendations: [String]
    let emotionalScores: [String: Int]?
}

// Кризисная поддержка
struct CrisisSupportResponse: Codable {
    let message: String
    let crisisType: String
    let immediateActions: [String]
    let timestamp: Date
}

// Психологический профиль
struct PsychologicalProfileResponse: Codable {
    let userId: String
    let emotionalTrends: EmotionalTrends
    let recentSessions: [SupportSession]
    let recommendations: [String]
}

struct EmotionalTrends: Codable {
    let trend: String // "positive", "negative", "stable"
    let positiveRatio: Double
    let negativeRatio: Double
    let confidence: Double
}

struct SupportSession: Codable {
    let sessionId: String
    let ageGroup: String
    let emotionalState: String
    let supportType: String
    let message: String
    let timestamp: Date
}

// Возрастные группы
enum AgeGroup: String, Codable {
    case child_3_6 = "child_3_6"
    case child_7_12 = "child_7_12"
    case teen_13_17 = "teen_13_17"
    case adult_18_65 = "adult_18_65"
    case elderly_65_plus = "elderly_65_plus"
}
```

---

#### 3.2. Добавить методы в `Core/Network/APIService.swift`:

```swift
// MARK: - Psychological Support API

/// Запрос психологической поддержки
func requestPsychologicalSupport(
    message: String,
    ageGroup: AgeGroup?,
    completion: @escaping (Result<PsychologicalSupportResponse, Error>) -> Void
) {
    struct Request: Codable {
        let message: String
        let context: String = "psychological_support"
        let ageGroup: String?
        let userId: String?
        let timestamp: Date
    }
    
    let request = Request(
        message: message,
        ageGroup: ageGroup?.rawValue,
        userId: AppConfig.authToken ?? "guest",
        timestamp: Date()
    )
    
    networkManager.post(
        endpoint: AppConfig.Endpoint.aiAssistantPsychologicalSupport,
        body: request,
        completion: completion
    )
}

/// Анализ эмоционального состояния
func analyzeEmotionalState(
    message: String,
    completion: @escaping (Result<EmotionalAnalysisResponse, Error>) -> Void
) {
    struct Request: Codable {
        let message: String
        let context: String = "emotional_analysis"
        let userId: String?
        let timestamp: Date
    }
    
    let request = Request(
        message: message,
        userId: AppConfig.authToken ?? "guest",
        timestamp: Date()
    )
    
    networkManager.post(
        endpoint: AppConfig.Endpoint.aiAssistantAnalyzeEmotions,
        body: request,
        completion: completion
    )
}

/// Кризисная поддержка
func requestCrisisSupport(
    crisisType: String,
    completion: @escaping (Result<CrisisSupportResponse, Error>) -> Void
) {
    struct Request: Codable {
        let crisisType: String
    }
    
    let request = Request(crisisType: crisisType)
    
    networkManager.post(
        endpoint: AppConfig.Endpoint.aiAssistantCrisisSupport,
        body: request,
        completion: completion
    )
}

/// Получение психологического профиля
func getPsychologicalProfile(
    completion: @escaping (Result<PsychologicalProfileResponse, Error>) -> Void
) {
    networkManager.get(
        endpoint: AppConfig.Endpoint.aiAssistantPsychologicalProfile,
        completion: completion
    )
}
```

---

#### 3.3. Добавить endpoints в `Core/Config/AppConfig.swift`:

```swift
// AI Assistant Psychological Support
static let aiAssistantPsychologicalSupport = "/api/ai/assistant/psychological_support"
static let aiAssistantAnalyzeEmotions = "/api/ai/assistant/analyze_emotions"
static let aiAssistantCrisisSupport = "/api/ai/assistant/crisis_support"
static let aiAssistantPsychologicalProfile = "/api/ai/assistant/psychological_profile"
```

---

#### 3.4. Модифицировать `Screens/06_AIAssistantScreen.swift`:

```swift
// Добавить состояние для возрастной группы
@State private var selectedAgeGroup: AgeGroup? = nil

// Модифицировать determineMessageContext
private func determineMessageContext(_ message: String) -> String {
    let lowerMessage = message.lowercased()
    
    // Проверка на психологические вопросы (ПЕРВЫМ!)
    let psychologicalKeywords = [
        "грустно", "печально", "плохо", "ужасно", "депрессия",
        "тревожно", "волнуюсь", "боюсь", "страшно", "паника",
        "злой", "злюсь", "бешенство", "ярость", "ненавижу",
        "стресс", "устал", "напряжение", "давление", "перегрузка",
        "одиноко", "один", "никого", "пустота", "изоляция",
        "помощь", "поддержка", "психолог", "психологическая",
        "sad", "anxious", "angry", "stressed", "lonely",
        "depression", "stress", "help", "support", "psychologist"
    ]
    
    for keyword in psychologicalKeywords {
        if lowerMessage.contains(keyword) {
            return "psychological_support"
        }
    }
    
    // Проверка на кризис
    let crisisKeywords = [
        "суицид", "убить себя", "не хочу жить", "конец",
        "suicide", "kill myself", "don't want to live", "end"
    ]
    
    for keyword in crisisKeywords {
        if lowerMessage.contains(keyword) {
            return "crisis"
        }
    }
    
    // Остальные проверки (существующий код)
    // ...
}

// Модифицировать sendRegularMessage
private func sendRegularMessage(_ message: String, context: String) {
    logger.business("🤖 AI Assistant: Sending message (context: \(context))")
    
    // Если психологический контекст → Psychological Support Agent
    if context == "psychological_support" {
        sendPsychologicalSupportMessage(message)
        return
    }
    
    // Если кризис → немедленная кризисная поддержка
    if context == "crisis" {
        sendCrisisSupportMessage(message)
        return
    }
    
    // Иначе → обычный AI Assistant
    logger.network("🤖 AI Assistant: Making API call to AI service")
    apiService.sendMessageToAI(message: message, context: context) { [self] result in
        // Существующая логика
    }
}

// Новый метод для психологической поддержки
private func sendPsychologicalSupportMessage(_ message: String) {
    logger.business("🧠 AI Assistant: Sending psychological support request")
    
    // Определить возрастную группу
    let ageGroup = determineUserAgeGroup() // Из UserProfile или FamilyMember
    
    isLoading = true
    
    apiService.requestPsychologicalSupport(
        message: message,
        ageGroup: ageGroup
    ) { [self] result in
        DispatchQueue.main.async {
            isLoading = false
            
            switch result {
            case .success(let response):
                logger.business("✅ AI Assistant: Received psychological support response")
                
                let aiResponse = ChatMessage(
                    text: response.message,
                    isUser: false,
                    time: currentTime()
                )
                
                messages.append(aiResponse)
                saveMessages()
                
                // Опционально: анализ эмоций
                analyzeEmotionsIfNeeded(message)
                
            case .failure(let error):
                logger.error("❌ AI Assistant: Failed to get psychological support", error: error)
                
                let errorResponse = ChatMessage(
                    text: "Извините, не удалось получить поддержку. Попробуйте позже или обратитесь к специалисту.",
                    isUser: false,
                    time: currentTime()
                )
                messages.append(errorResponse)
                saveMessages()
            }
        }
    }
}

// Новый метод для кризисной поддержки
private func sendCrisisSupportMessage(_ message: String) {
    logger.business("🚨 AI Assistant: Sending CRISIS support request")
    
    isLoading = true
    
    // Определить тип кризиса
    let crisisType = determineCrisisType(message)
    
    apiService.requestCrisisSupport(crisisType: crisisType) { [self] result in
        DispatchQueue.main.async {
            isLoading = false
            
            switch result {
            case .success(let response):
                logger.business("✅ AI Assistant: Received crisis support response")
                
                // Показать кризисное сообщение
                let crisisResponse = ChatMessage(
                    text: response.message,
                    isUser: false,
                    time: currentTime()
                )
                messages.append(crisisResponse)
                
                // Показать немедленные действия
                if !response.immediateActions.isEmpty {
                    let actionsText = "Немедленные действия:\n" + response.immediateActions.map { "• \($0)" }.joined(separator: "\n")
                    let actionsResponse = ChatMessage(
                        text: actionsText,
                        isUser: false,
                        time: currentTime()
                    )
                    messages.append(actionsResponse)
                }
                
                saveMessages()
                
                // Показать алерт с контактами кризисной службы
                showCrisisAlert()
                
            case .failure(let error):
                logger.error("❌ AI Assistant: Failed to get crisis support", error: error)
                
                // В случае ошибки показать контакты кризисной службы
                let emergencyResponse = ChatMessage(
                    text: "Немедленно обратитесь за помощью:\n• Телефон доверия: 8-800-2000-122\n• Экстренная служба: 112\n• Вы не одни, помощь доступна!",
                    isUser: false,
                    time: currentTime()
                )
                messages.append(emergencyResponse)
                saveMessages()
                
                showCrisisAlert()
            }
        }
    }
}

// Вспомогательные методы
private func determineUserAgeGroup() -> AgeGroup? {
    // Получить возраст из UserProfile или FamilyMember
    // Если не найден → вернуть nil (будет использована дефолтная группа)
    return nil
}

private func determineCrisisType(_ message: String) -> String {
    let lowerMessage = message.lowercased()
    
    if lowerMessage.contains("суицид") || lowerMessage.contains("убить себя") || lowerMessage.contains("suicide") {
        return "suicidal_ideation"
    } else if lowerMessage.contains("депрессия") || lowerMessage.contains("depression") {
        return "severe_depression"
    } else if lowerMessage.contains("тревога") || lowerMessage.contains("паника") || lowerMessage.contains("anxiety") {
        return "anxiety_attack"
    }
    
    return "general_crisis"
}

private func analyzeEmotionsIfNeeded(_ message: String) {
    // Опционально: автоматически анализировать эмоции
    apiService.analyzeEmotionalState(message: message) { result in
        switch result {
        case .success(let analysis):
            logger.business("🧠 AI Assistant: Emotional analysis - \(analysis.dominantEmotion), risk: \(analysis.riskLevel)")
            
            // Если высокий риск → предложить кризисную поддержку
            if analysis.riskLevel == "high" || analysis.riskLevel == "critical" {
                DispatchQueue.main.async {
                    let riskResponse = ChatMessage(
                        text: "Я заметил, что вам может быть нужна дополнительная поддержка. Хотите поговорить с психологом?",
                        isUser: false,
                        time: currentTime()
                    )
                    messages.append(riskResponse)
                    saveMessages()
                }
            }
        case .failure:
            // Игнорируем ошибки анализа
            break
        }
    }
}

private func showCrisisAlert() {
    // Показать алерт с контактами кризисной службы
    // Можно использовать Alert или отдельный экран
}
```

---

#### 3.5. Добавить быстрые действия для психологической поддержки:

```swift
// В QuickActionType enum
enum QuickActionType {
    case protectionStatus
    case analyzeThreats
    case securityTips
    case help
    case familySetup
    case reportIncident
    case psychologicalSupport  // НОВОЕ
    case crisisSupport         // НОВОЕ
    case emotionalAnalysis     // НОВОЕ
}

// В QuickActionsView
private let actions = [
    QuickAction(type: .protectionStatus, icon: "🛡️", title: "Статус защиты"),
    QuickAction(type: .analyzeThreats, icon: "🔍", title: "Анализ угроз"),
    QuickAction(type: .securityTips, icon: "💡", title: "Советы"),
    QuickAction(type: .help, icon: "❓", title: "Помощь"),
    QuickAction(type: .familySetup, icon: "👨‍👩‍👧‍👦", title: "Семья"),
    QuickAction(type: .reportIncident, icon: "🚨", title: "Инцидент"),
    QuickAction(type: .psychologicalSupport, icon: "🧠", title: "Поддержка"),  // НОВОЕ
    QuickAction(type: .crisisSupport, icon: "🚨", title: "Кризис"),            // НОВОЕ
    QuickAction(type: .emotionalAnalysis, icon: "😊", title: "Эмоции")           // НОВОЕ
]

// В handleQuickAction
case .psychologicalSupport:
    message = "Мне нужна психологическая поддержка"
case .crisisSupport:
    message = "Мне нужна экстренная помощь"
case .emotionalAnalysis:
    message = "Проанализируй мое эмоциональное состояние"
```

---

### 🔵 ФАЗА 4: Тестирование (1 день)

#### 4.1. Тесты:

1. **Психологическая поддержка:**
   - Отправить сообщение с психологическими ключевыми словами
   - Проверить, что вызывается Psychological Support Agent
   - Проверить ответ с учетом возрастной группы

2. **Кризисная поддержка:**
   - Отправить сообщение с кризисными ключевыми словами
   - Проверить немедленную реакцию
   - Проверить показ контактов кризисной службы

3. **Анализ эмоций:**
   - Отправить сообщение для анализа эмоций
   - Проверить определение доминирующей эмоции
   - Проверить уровень риска

4. **Психологический профиль:**
   - Запросить профиль пользователя
   - Проверить эмоциональные тренды
   - Проверить рекомендации

---

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### ✅ После подключения:

1. **Супер AI Асистент:**
   - ✅ Психолог для всех возрастных групп
   - ✅ Детский психолог (3-17 лет)
   - ✅ Кризисная поддержка
   - ✅ Анализ эмоций

2. **Улучшенный UX:**
   - ✅ Автоматическое определение психологических вопросов
   - ✅ Быстрые действия для психологической поддержки
   - ✅ Кризисные алерты

3. **Персонализация:**
   - ✅ Поддержка адаптируется под возраст
   - ✅ Учет эмоционального состояния
   - ✅ Персонализированные рекомендации

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Кризисная поддержка:**
   - Всегда показывать контакты кризисной службы
   - Немедленно реагировать на кризисные ситуации
   - Уведомлять семью при критических ситуациях

2. **Конфиденциальность:**
   - Все психологические данные должны быть защищены
   - Соблюдать медицинскую конфиденциальность
   - Не сохранять кризисные данные без согласия

3. **Локализация:**
   - Все сообщения психологической поддержки должны быть локализованы
   - Контакты кризисной службы должны быть для конкретной страны

---

## 📋 TODO ЛИСТ

### Фаза 1: API Endpoints
- [ ] Добавить endpoints в `ai_assistant_router.py`
- [ ] Создать модели для запросов/ответов
- [ ] Протестировать endpoints

### Фаза 2: SFM Регистрация
- [ ] Зарегистрировать функции в SFM Registry
- [ ] Протестировать вызовы через SFM

### Фаза 3: Мобильное приложение
- [ ] Добавить модели в `APIModels.swift`
- [ ] Добавить методы в `APIService.swift`
- [ ] Добавить endpoints в `AppConfig.swift`
- [ ] Модифицировать `AIAssistantScreen.swift`
- [ ] Добавить быстрые действия
- [ ] Добавить определение возрастной группы

### Фаза 4: Тестирование
- [ ] Тест психологической поддержки
- [ ] Тест кризисной поддержки
- [ ] Тест анализа эмоций
- [ ] Тест психологического профиля

---

**Статус:** ✅ **ПЛАН ГОТОВ К РЕАЛИЗАЦИИ**

# 🔗 КОНКРЕТНЫЕ ТОЧКИ ИНТЕГРАЦИИ: iOS ↔️ Сервер для 100% защиты

**Дата:** 30 октября 2025

---

## 📊 ОБЗОР

**Нужно создать 27 интеграций для 19 угроз**

**Распределение:**
- 🔴 **API Endpoints**: 10 интеграций (iOS → Server)
- 🟡 **Real-time Notifications**: 8 интеграций (Server → iOS)
- 🟢 **ML Models**: 5 интеграций (Server)
- 🔵 **Enhanced Modules**: 4 интеграции (Server)

---

## 🔴 ГРУППА 1: API ENDPOINTS (10 интеграций)

### **1.1 Mobile Malware Scanner API**

**Угрозы:** Вирусы, Ransomware, Поддельные приложения

**iOS файл:** `Core/Mobile/MobileMalwareScanner.swift`

**Backend файл:** `security/ai_agents/mobile_security_agent.py`

**API Endpoint:**
```python
POST /api/mobile/scan-apps
{
    "device_id": "abc123",
    "apps": [
        {"name": "App1", "package": "com.app1"},
        {"name": "App2", "package": "com.app2"}
    ]
}

Response:
{
    "status": "success",
    "threats_detected": [
        {"app": "App1", "threat": "Trojan", "severity": "high"}
    ]
}
```

**Что делает:**
- iOS отправляет список приложений на сервер
- Сервер проверяет через MobileSecurityAgent
- Возврат списка угроз
- iOS блокирует опасные приложения

**Файлы для изменения:**
```
iOS:
  - Core/Mobile/MobileMalwareScanner.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/mobile.py (НОВЫЙ)
  - security/ai_agents/mobile_security_agent.py (уже есть)
```

**Время:** 2-3 дня

---

### **1.2 Fraud Detection API - Звонки**

**Угрозы:** Телефонное мошенничество, Vishing

**iOS файл:** `Core/Fraud/FraudDetectionModule.swift`

**Backend файл:** `security/ai_agents/anti_fraud_master_ai.py`

**API Endpoint:**
```python
POST /api/fraud/analyze-call
{
    "phone_number": "+79991234567",
    "user_id": "user123",
    "call_time": "2025-10-30T12:00:00Z"
}

Response:
{
    "status": "success",
    "is_fraud": true,
    "confidence": 0.95,
    "threat_type": "Phone Fraud",
    "recommendation": "Block this call"
}
```

**Что делает:**
- iOS перехватывает входящий звонок
- Отправляет номер на сервер
- Сервер проверяет через AntiFraudMasterAI
- Возврат "это мошенник" или "безопасно"
- iOS блокирует звонок или предупреждает

**Файлы для изменения:**
```
iOS:
  - Core/Fraud/FraudDetectionModule.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/fraud.py (НОВЫЙ)
  - security/ai_agents/anti_fraud_master_ai.py (уже есть)
```

**Время:** 2-3 дня

---

### **1.3 Fraud Detection API - SMS**

**Угрозы:** SMS-мошенничество, Smishing

**iOS файл:** `Core/Fraud/FraudDetectionModule.swift`

**Backend файл:** `security/ai_agents/phishing_protection_agent.py`

**API Endpoint:**
```python
POST /api/fraud/analyze-sms
{
    "message": "Вы выиграли 1 млн рублей!",
    "sender": "+79991234567",
    "user_id": "user123"
}

Response:
{
    "status": "success",
    "is_fraud": true,
    "confidence": 0.98,
    "threat_type": "Smishing",
    "recommendation": "Delete this SMS"
}
```

**Что делает:**
- iOS перехватывает входящее SMS
- Отправляет текст на сервер
- Сервер проверяет через PhishingProtectionAgent
- Возврат "это мошенничество" или "безопасно"
- iOS блокирует SMS или предупреждает

**Файлы для изменения:**
```
iOS:
  - Core/Fraud/FraudDetectionModule.swift (уже создан выше)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/fraud.py (добавить в существующий)
  - security/ai_agents/phishing_protection_agent.py (уже есть)
```

**Время:** 1-2 дня

---

### **1.4 Deepfake Detection API**

**Угрозы:** Deepfake видео, Поддельные голоса

**iOS файл:** `Core/Deepfake/DeepfakeDetectionModule.swift`

**Backend файл:** `security/ai_agents/deepfake_protection_system.py`

**API Endpoint:**
```python
POST /api/deepfake/analyze-video
{
    "video_file": "base64_encoded_video",
    "user_id": "user123"
}

Response:
{
    "status": "success",
    "is_deepfake": true,
    "confidence": 0.92,
    "recommendation": "This video is fake"
}
```

**Что делает:**
- iOS загружает видео
- Отправляет на сервер
- Сервер проверяет через DeepfakeProtectionSystem
- Возврат "фейк" или "настоящее"
- iOS предупреждает пользователя

**Файлы для изменения:**
```
iOS:
  - Core/Deepfake/DeepfakeDetectionModule.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/deepfake.py (НОВЫЙ)
  - security/ai_agents/deepfake_protection_system.py (уже есть)
```

**Время:** 3-5 дней

---

### **1.5 Behavioral Analysis API**

**Угрозы:** Cyberstalking, Online manipulation, Social engineering

**iOS файл:** `Core/Behavioral/BehavioralAnalysisModule.swift`

**Backend файл:** `security/ai_agents/behavioral_analysis_agent.py`

**API Endpoint:**
```python
POST /api/behavioral/analyze-activity
{
    "user_id": "user123",
    "activities": [
        {"type": "login", "location": "unknown"},
        {"type": "message", "to": "stranger123"}
    ]
}

Response:
{
    "status": "success",
    "risk_score": 0.75,
    "threats_detected": [
        {"type": "Cyberstalking", "severity": "high"}
    ],
    "recommendation": "Block this user"
}
```

**Что делает:**
- iOS собирает активность пользователя
- Отправляет на сервер
- Сервер анализирует через BehavioralAnalysisAgent
- Возврат risk score и угроз
- iOS предупреждает или блокирует

**Файлы для изменения:**
```
iOS:
  - Core/Behavioral/BehavioralAnalysisModule.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/behavioral.py (НОВЫЙ)
  - security/ai_agents/behavioral_analysis_agent.py (уже есть)
```

**Время:** 3-5 дней

---

### **1.6 Cyberbullying Detection API**

**Угрозы:** Кибербуллинг, Digital harassment

**iOS файл:** `Core/Social/CyberbullyingDetector.swift`

**Backend файлы:** `security/bots/parental_control_bot.py`, `security/bots/whatsapp_security_bot.py`

**API Endpoint:**
```python
POST /api/social/analyze-message
{
    "message": "You are stupid!",
    "sender": "bully123",
    "receiver": "child123"
}

Response:
{
    "status": "success",
    "is_bullying": true,
    "severity": "medium",
    "recommendation": "Block this user"
}
```

**Что делает:**
- iOS отправляет сообщения на сервер
- Сервер проверяет через ParentalControlBot
- Возврат "это буллинг" или "безопасно"
- iOS блокирует пользователя или предупреждает

**Файлы для изменения:**
```
iOS:
  - Core/Social/CyberbullyingDetector.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/social.py (НОВЫЙ)
  - security/bots/parental_control_bot.py (добавить метод)
```

**Время:** 2-3 дня

---

### **1.7 Online Predators Detection API**

**Угрозы:** Опасные знакомства, Online predators, Grooming

**iOS файл:** `Core/ChildProtection/PredatorDetectionModule.swift`

**Backend файл:** `security/bots/parental_control_bot.py`

**API Endpoint:**
```python
POST /api/child/predator-check
{
    "child_id": "child123",
    "contact_id": "stranger123",
    "messages": ["Hi, how old are you?"]
}

Response:
{
    "status": "success",
    "is_predator": true,
    "confidence": 0.88,
    "recommendation": "Block immediately"
}
```

**Что делает:**
- iOS отправляет контакты и сообщения на сервер
- Сервер анализирует через ParentalControlBot + ML
- Возврат "это хищник" или "безопасно"
- iOS блокирует контакт и предупреждает родителей

**Файлы для изменения:**
```
iOS:
  - Core/ChildProtection/PredatorDetectionModule.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/child.py (НОВЫЙ)
  - security/bots/parental_control_bot.py (добавить метод)
```

**Время:** 3-5 дней

---

### **1.8 Content Analysis API**

**Угрозы:** Фейковые новости, Поддельные документы

**iOS файл:** `Core/Content/ContentSafetyModule.swift`

**Backend файл:** `security/ai_agents/content_analyzer_enhanced.py`

**API Endpoint:**
```python
POST /api/content/analyze-news
{
    "article": "Breaking news:...",
    "source": "news.com"
}

Response:
{
    "status": "success",
    "is_fake": true,
    "confidence": 0.85,
    "recommendation": "Do not trust this source"
}
```

**Что делает:**
- iOS отправляет новость на сервер
- Сервер проверяет через ContentAnalyzerEnhanced
- Возврат "фейк" или "настоящее"
- iOS предупреждает пользователя

**Файлы для изменения:**
```
iOS:
  - Core/Content/ContentSafetyModule.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/content.py (НОВЫЙ)
  - security/ai_agents/content_analyzer_enhanced.py (добавить метод)
```

**Время:** 2-3 дня

---

### **1.9 Metadata Protection API**

**Угрозы:** Утечки метаданных, EXIF data leaks

**iOS файл:** `Core/Data/MetadataProtector.swift`

**Backend файл:** `security/ai_agents/data_protection_agent.py`

**API Endpoint:**
```python
POST /api/data/protect-metadata
{
    "image_file": "base64_encoded_image",
    "strip_location": true
}

Response:
{
    "status": "success",
    "cleaned_image": "base64_encoded_image",
    "removed_data": ["location", "timestamp"]
}
```

**Что делает:**
- iOS загружает фото
- Отправляет на сервер для очистки
- Сервер удаляет метаданные через DataProtectionAgent
- Возврат очищенного изображения
- iOS сохраняет безопасное фото

**Файлы для изменения:**
```
iOS:
  - Core/Data/MetadataProtector.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/data.py (НОВЫЙ)
  - security/ai_agents/data_protection_agent.py (добавить метод)
```

**Время:** 2-3 дня

---

### **1.10 Privacy Settings API**

**Угрозы:** Tracking cookies, Нарушение приватности

**iOS файл:** `Core/Browser/PrivacyManager.swift`

**Backend файл:** `security/bots/browser_security_bot.py`

**API Endpoint:**
```python
POST /api/browser/protect-privacy
{
    "url": "https://site.com",
    "remove_trackers": true
}

Response:
{
    "status": "success",
    "safe_url": "https://site.com?no_trackers=true",
    "blocked_trackers": 15
}
```

**Что делает:**
- iOS отправляет URL на сервер
- Сервер удаляет трекеры через BrowserSecurityBot
- Возврат безопасной ссылки
- iOS открывает защищённый сайт

**Файлы для изменения:**
```
iOS:
  - Core/Browser/PrivacyManager.swift (НОВЫЙ)
  - Core/Network/APIService.swift (добавить метод)
  
Backend:
  - api/routes/browser.py (НОВЫЙ)
  - security/bots/browser_security_bot.py (добавить метод)
```

**Время:** 2-3 дня

---

## 🟡 ГРУППА 2: REAL-TIME NOTIFICATIONS (8 интеграций)

### **2.1 Threat Detection Notifications**

**Угрозы:** Все угрозы (real-time)

**iOS файл:** `Core/Notifications/ThreatNotificationManager.swift`

**Backend файл:** `security/ai_agents/threat_detection_agent.py`

**Механизм:**
```swift
// iOS
class ThreatNotificationManager {
    func subscribeToThreats() {
        // WebSocket подключение
        websocket.on("threat_detected") { data in
            // Показываем уведомление
        }
    }
}
```

**Что делает:**
- Сервер отправляет уведомление при обнаружении угрозы
- iOS получает и показывает уведомление
- Пользователь видит "Обнаружена угроза: ..."
- Пользователь может заблокировать

**Файлы для изменения:**
```
iOS:
  - Core/Notifications/ThreatNotificationManager.swift (НОВЫЙ)
  - Info.plist (добавить права на уведомления)
  
Backend:
  - websocket/handlers/threats.py (НОВЫЙ)
  - security/ai_agents/threat_detection_agent.py (добавить WebSocket emit)
```

**Время:** 1-2 дня

---

### **2.2 Fraud Alert Notifications**

**Угрозы:** Мошенничество (все типы)

**iOS файл:** `Core/Notifications/FraudNotificationManager.swift`

**Backend файл:** `security/ai_agents/anti_fraud_master_ai.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

### **2.3 Child Safety Notifications**

**Угрозы:** Детские угрозы

**iOS файл:** `Core/Notifications/ChildSafetyNotificationManager.swift`

**Backend файл:** `security/bots/parental_control_bot.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

### **2.4 Network Attack Notifications**

**Угрозы:** Сетевые атаки

**iOS файл:** `Core/Notifications/NetworkNotificationManager.swift`

**Backend файл:** `security/bots/network_security_bot.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

### **2.5 Deepfake Alert Notifications**

**Угрозы:** Deepfake

**iOS файл:** `Core/Notifications/DeepfakeNotificationManager.swift`

**Backend файл:** `security/ai_agents/deepfake_protection_system.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

### **2.6 Behavioral Anomaly Notifications**

**Угрозы:** Anomalies, Cyberstalking

**iOS файл:** `Core/Notifications/BehavioralNotificationManager.swift`

**Backend файл:** `security/ai_agents/behavioral_analysis_agent.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

### **2.7 Malware Block Notifications**

**Угрозы:** Malware

**iOS файл:** `Core/Notifications/MalwareNotificationManager.swift`

**Backend файл:** `security/ai_agents/malware_detection_agent.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

### **2.8 Emergency Notifications**

**Угрозы:** Критические угрозы

**iOS файл:** `Core/Notifications/EmergencyNotificationManager.swift`

**Backend файл:** `security/bots/emergency_response_bot.py`

**Механизм:** Аналогично выше (WebSocket)

**Время:** 1 день

---

## 🟢 ГРУППА 3: ML MODELS (5 интеграций)

### **3.1 Self-Harm Detection Model**

**Угроза:** Self-harm content

**Backend файл:** `security/ai_agents/parental_control_bot.py`

**ML модель:**
```python
# Обучить BERT модель
from transformers import BertForSequenceClassification

model = BertForSequenceClassification.from_pretrained('bert-base')
# Обучить на датасете self-harm content
# Интегрировать в ParentalControlBot
```

**Что делает:**
- Анализирует текст контента
- Обнаруживает опасные слова/фразы
- Блокирует контент автоматически

**Время:** 1-2 недели

---

### **3.2 Online Predator Detection Model**

**Угроза:** Online predators

**Backend файл:** `security/bots/parental_control_bot.py`

**ML модель:**
```python
# CNN + RNN модель
model = Sequential([
    Embedding(input_dim, embedding_dim),
    Conv1D(128, 5),
    LSTM(64),
    Dense(1, activation='sigmoid')
])
# Обучить на датасете predator messages
```

**Время:** 1-2 недели

---

### **3.3 Grooming Detection Model**

**Угроза:** Grooming атаки

**Backend файл:** `security/bots/parental_control_bot.py`

**ML модель:**
```python
# Transformer модель
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained('rubert')
# Обучить на датасете grooming conversations
```

**Время:** 1-2 недели

---

### **3.4 Fake News Detection Model**

**Угроза:** Фейковые новости

**Backend файл:** `security/ai_agents/content_analyzer_enhanced.py`

**ML модель:**
```python
# BERT модель для fake news
model = BertForSequenceClassification.from_pretrained('bert-base')
# Обучить на датасете fake news
```

**Время:** 1-2 недели

---

### **3.5 Document Verification Model**

**Угроза:** Поддельные документы

**Backend файл:** `security/ai_agents/content_analyzer_enhanced.py`

**ML модель:**
```python
# Computer Vision модель
model = tf.keras.Sequential([
    Conv2D(32, 3, activation='relu'),
    MaxPooling2D(),
    Conv2D(64, 3, activation='relu'),
    Dense(1, activation='sigmoid')
])
# Обучить на датасете documents
```

**Время:** 1-2 недели

---

## 🔵 ГРУППА 4: ENHANCED MODULES (4 интеграции)

### **4.1 SIM Swapping Detection**

**Угроза:** SIM swapping

**iOS файл:** `Core/Mobile/SIMMonitoringModule.swift`

**Backend файл:** `security/ai_agents/mobile_security_agent.py`

**Что делает:**
- iOS мониторит изменения SIM карты
- Отправляет уведомление на сервер
- Сервер анализирует через MobileSecurityAgent
- Предупреждение пользователя

**Время:** 2-3 дня

---

### **4.2 Fake Banking Apps Detection**

**Угроза:** Fake mobile banking apps

**iOS файл:** `Core/Mobile/BankingAppScanner.swift`

**Backend файлы:** `security/ai_agents/mobile_security_agent.py`, `security/ai_agents/anti_fraud_master_ai.py`

**Что делает:**
- iOS сканирует банковские приложения
- Проверяет через MobileSecurityAgent + AntiFraudMasterAI
- Блокирует поддельные приложения

**Время:** 2-3 дня

---

### **4.3 Gaslighting Detection**

**Угроза:** Gaslighting в сети

**iOS файл:** `Core/Psychological/GaslightingDetector.swift`

**Backend файл:** `security/ai_agents/psychological_support_agent.py`

**Что делает:**
- Анализирует сообщения на газлайтинг
- Предупреждает пользователя

**Время:** 2-3 дня

---

### **4.4 Online Manipulation Detection**

**Угроза:** Online manipulation

**iOS файл:** `Core/Social/ManipulationDetector.swift`

**Backend файл:** `security/ai_agents/behavioral_analysis_agent.py`

**Что делает:**
- Анализирует поведение на манипуляции
- Предупреждает пользователя

**Время:** 2-3 дня

---

## 📊 СВОДНАЯ ТАБЛИЦА

| # | Интеграция | Группа | Время | Приоритет |
|---|------------|--------|-------|-----------|
| 1 | Mobile Malware Scanner API | 🔴 API | 2-3 дня | 🔴 |
| 2 | Fraud Detection - Calls API | 🔴 API | 2-3 дня | 🔴 |
| 3 | Fraud Detection - SMS API | 🔴 API | 1-2 дня | 🔴 |
| 4 | Deepfake Detection API | 🔴 API | 3-5 дней | 🟡 |
| 5 | Behavioral Analysis API | 🔴 API | 3-5 дней | 🟡 |
| 6 | Cyberbullying Detection API | 🔴 API | 2-3 дня | 🟡 |
| 7 | Predator Detection API | 🔴 API | 3-5 дней | 🟡 |
| 8 | Content Analysis API | 🔴 API | 2-3 дня | 🟡 |
| 9 | Metadata Protection API | 🔴 API | 2-3 дня | 🟡 |
| 10 | Privacy Settings API | 🔴 API | 2-3 дня | 🟡 |
| 11-18 | Real-time Notifications (8 штук) | 🟡 Notifications | 8-16 дней | 🟡 |
| 19 | Self-Harm Detection ML | 🟢 ML | 1-2 недели | 🟡 |
| 20 | Predator Detection ML | 🟢 ML | 1-2 недели | 🟡 |
| 21 | Grooming Detection ML | 🟢 ML | 1-2 недели | 🟡 |
| 22 | Fake News Detection ML | 🟢 ML | 1-2 недели | 🟡 |
| 23 | Document Verification ML | 🟢 ML | 1-2 недели | 🟡 |
| 24 | SIM Swapping Detection | 🔵 Enhanced | 2-3 дня | 🟡 |
| 25 | Fake Banking Apps | 🔵 Enhanced | 2-3 дня | 🟡 |
| 26 | Gaslighting Detection | 🔵 Enhanced | 2-3 дня | 🟡 |
| 27 | Online Manipulation Detection | 🔵 Enhanced | 2-3 дня | 🟡 |

---

## ⏱️ ВРЕМЯ ВЫПОЛНЕНИЯ

**API Endpoints:** 20-30 дней  
**Real-time Notifications:** 8-16 дней  
**ML Models:** 5-10 недель  
**Enhanced Modules:** 8-12 дней  

**ИТОГО:** 4-6 недель (при параллельной разработке)

---

## 💰 СТОИМОСТЬ

**API Endpoints:** $40,000 - $60,000  
**Real-time Notifications:** $20,000 - $30,000  
**ML Models:** $60,000 - $90,000  
**Enhanced Modules:** $15,000 - $25,000  

**ИТОГО:** $135,000 - $205,000

---

## ✅ КРИТЕРИИ УСПЕХА

После реализации всех 27 интеграций:
- ✅ 100 угроз покрыто (100%)
- ✅ Real-time защита работает
- ✅ ML модели обучены
- ✅ API endpoints работают
- ✅ Уведомления приходят мгновенно

---

## 🎯 ПРИОРИТЕТЫ

**Критично (немедленно):**
1. Mobile Malware Scanner API
2. Fraud Detection API
3. Real-time Notifications

**Важно (1-2 недели):**
4-10. Остальные API endpoints

**Можно позже (2-4 недели):**
11-27. ML Models и Enhanced Modules

---

## 📍 КОНКРЕТНЫЕ ФАЙЛЫ ДЛЯ ИЗМЕНЕНИЯ

**iOS:**
```
Core/Mobile/MobileMalwareScanner.swift (НОВЫЙ)
Core/Fraud/FraudDetectionModule.swift (НОВЫЙ)
Core/Deepfake/DeepfakeDetectionModule.swift (НОВЫЙ)
Core/Behavioral/BehavioralAnalysisModule.swift (НОВЫЙ)
Core/Social/CyberbullyingDetector.swift (НОВЫЙ)
Core/ChildProtection/PredatorDetectionModule.swift (НОВЫЙ)
Core/Content/ContentSafetyModule.swift (НОВЫЙ)
Core/Data/MetadataProtector.swift (НОВЫЙ)
Core/Browser/PrivacyManager.swift (НОВЫЙ)
Core/Notifications/ThreatNotificationManager.swift (НОВЫЙ)
Core/Network/APIService.swift (ДОПОЛНИТЬ 10 методов)
```

**Backend:**
```
api/routes/mobile.py (НОВЫЙ)
api/routes/fraud.py (НОВЫЙ)
api/routes/deepfake.py (НОВЫЙ)
api/routes/behavioral.py (НОВЫЙ)
api/routes/social.py (НОВЫЙ)
api/routes/child.py (НОВЫЙ)
api/routes/content.py (НОВЫЙ)
api/routes/data.py (НОВЫЙ)
api/routes/browser.py (НОВЫЙ)
websocket/handlers/threats.py (НОВЫЙ)
security/bots/parental_control_bot.py (ДОПОЛНИТЬ методы)
security/ai_agents/content_analyzer_enhanced.py (ДОПОЛНИТЬ методы)
ml_models/self_harm_detector.py (НОВЫЙ)
ml_models/predator_detector.py (НОВЫЙ)
ml_models/grooming_detector.py (НОВЫЙ)
ml_models/fake_news_detector.py (НОВЫЙ)
ml_models/document_verifier.py (НОВЫЙ)
```

---

## ✅ ВЫВОД

**Для 100% защиты нужно создать 27 конкретных интеграций**

**Локации:**
- 10 API endpoints (iOS → Server)
- 8 WebSocket уведомлений (Server → iOS)
- 5 ML моделей (Server)
- 4 расширенных модуля (iOS + Server)

**Время:** 4-6 недель  
**Стоимость:** $135K - $205K

**Результат:** 100% покрытие 100 угроз!



# 📱 ПЛАН ИНТЕГРАЦИИ НОВЫХ ФУНКЦИЙ В iOS ПРИЛОЖЕНИЕ

**Дата создания:** 9 декабря 2025  
**Статус:** ✅ Готов к реализации  
**Цель:** Детальный план интеграции всех 11 новых функций безопасности в существующее iOS приложение ALADDIN

---

## 📋 СОДЕРЖАНИЕ

1. [Анализ существующей структуры](#анализ-существующей-структуры)
2. [План интеграции по функциям](#план-интеграции-по-функциям)
3. [Общие изменения](#общие-изменения)
4. [Порядок реализации](#порядок-реализации)
5. [Чеклист интеграции](#чеклист-интеграции)

---

## 🔍 АНАЛИЗ СУЩЕСТВУЮЩЕЙ СТРУКТУРЫ

### Текущая архитектура iOS приложения

**Основные файлы:**
- `Core/Config/AppConfig.swift` - Endpoints конфигурация
- `Core/Network/APIService.swift` - API методы
- `Core/Models/APIModels.swift` - Модели данных
- `Core/Navigation/NavigationManager.swift` - Навигация между экранами
- `Screens/*.swift` - UI экраны

**Существующие экраны:** 33+ экранов уже реализованы

**Паттерн создания экранов:**
1. Создать Screen.swift файл в папке `Screens/`
2. Добавить case в `NavigationManager.ALADDINScreen`
3. Добавить отображение в `NavigationManager.getView()`
4. Добавить endpoint в `AppConfig.Endpoint`
5. Добавить методы в `APIService.swift`
6. Добавить модели в `APIModels.swift`

---

## 📋 ПЛАН ИНТЕГРАЦИИ ПО ФУНКЦИЯМ

### ✅ ФАЗА 1: КРИТИЧНЫЕ ФУНКЦИИ (29-32 дня)

---

#### 1. 🌐 DARK WEB МОНИТОРИНГ (8-9 дней)

**Что нужно добавить в iOS:**

##### 1.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // ... существующие endpoints
    
    // Dark Web Monitoring
    static let darkWebCheck = "/darkweb/check"
    static let darkWebStartMonitoring = "/darkweb/start-monitoring"
    static let darkWebBreaches = "/darkweb/breaches"
    static let darkWebStatus = "/darkweb/status"
    static let darkWebStopMonitoring = "/darkweb/stop-monitoring"
}
```

##### 1.2 APIModels.swift - Модели данных
```swift
// MARK: - Dark Web Monitoring Models

struct DarkWebCheckRequest: Codable {
    let email: String
    let phone: String?
}

struct DarkWebCheckResponse: Codable {
    let userId: String
    let breachesFound: Int
    let breaches: [DarkWebBreach]
    let checkedAt: String
}

struct DarkWebBreach: Codable, Identifiable {
    let id: String
    let email: String
    let breachName: String
    let count: Int
    let detectedAt: String
    let severity: String // "low", "medium", "high", "critical"
    let description: String?
    let affectedData: [String]? // ["Email", "Passwords", "Phone"]
    let breachDate: String?
    let addedDate: String?
}

struct DarkWebStartMonitoringRequest: Codable {
    let email: String
    let phone: String?
    let intervalHours: Int // 24 по умолчанию
}

struct DarkWebStatusResponse: Codable {
    let isMonitoring: Bool
    let email: String?
    let phone: String?
    let lastCheck: String?
    let nextCheck: String?
    let totalBreaches: Int
    let newBreaches: Int
}

struct DarkWebBreachesResponse: Codable {
    let breaches: [DarkWebBreach]
    let total: Int
}
```

##### 1.3 APIService.swift - API методы
```swift
// MARK: - Dark Web Monitoring API

func checkDarkWeb(email: String, phone: String?, completion: @escaping (Result<DarkWebCheckResponse, Error>) -> Void) {
    let request = DarkWebCheckRequest(email: email, phone: phone)
    networkManager.post(endpoint: AppConfig.Endpoint.darkWebCheck, body: request, completion: completion)
}

func startDarkWebMonitoring(email: String, phone: String?, intervalHours: Int = 24, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = DarkWebStartMonitoringRequest(email: email, phone: phone, intervalHours: intervalHours)
    networkManager.post(endpoint: AppConfig.Endpoint.darkWebStartMonitoring, body: request, completion: completion)
}

func stopDarkWebMonitoring(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct EmptyBody: Codable {}
    networkManager.post(endpoint: AppConfig.Endpoint.darkWebStopMonitoring, body: EmptyBody(), completion: completion)
}

func getDarkWebBreaches(completion: @escaping (Result<DarkWebBreachesResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.darkWebBreaches, completion: completion)
}

func getDarkWebStatus(completion: @escaping (Result<DarkWebStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.darkWebStatus, completion: completion)
}
```

##### 1.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    // ... существующие экраны
    
    case darkWebMonitoring = "27_DarkWebMonitoringScreen"
    
    var displayName: String {
        switch self {
        // ... существующие
        case .darkWebMonitoring: return "Мониторинг Dark Web"
        }
    }
    
    var icon: String {
        switch self {
        // ... существующие
        case .darkWebMonitoring: return "eye.slash.fill"
        }
    }
}
```

##### 1.5 Screens/27_DarkWebMonitoringScreen.swift - UI экран
```swift
import SwiftUI

struct DarkWebMonitoringScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var viewModel = DarkWebMonitoringViewModel()
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: "Dark Web Мониторинг",
                    subtitle: "Проверка утечек данных",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Статус мониторинга
                        monitoringStatusCard
                        
                        // Список утечек
                        if !viewModel.breaches.isEmpty {
                            breachesListSection
                        }
                        
                        // Кнопка запуска проверки
                        checkButtonSection
                        
                        // Настройки мониторинга
                        settingsSection
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            viewModel.loadStatus()
            viewModel.loadBreaches()
        }
    }
    
    // ... UI компоненты
}

// ViewModel для DarkWebMonitoringScreen
@MainActor
class DarkWebMonitoringViewModel: ObservableObject {
    @Published var isMonitoring = false
    @Published var status: DarkWebStatusResponse?
    @Published var breaches: [DarkWebBreach] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    
    func loadStatus() {
        isLoading = true
        apiService.getDarkWebStatus { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let status):
                    self?.status = status
                    self?.isMonitoring = status.isMonitoring
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    func loadBreaches() {
        apiService.getDarkWebBreaches { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    self?.breaches = response.breaches
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    func startMonitoring(email: String, phone: String?, intervalHours: Int = 24) {
        isLoading = true
        apiService.startDarkWebMonitoring(email: email, phone: phone, intervalHours: intervalHours) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success:
                    self?.loadStatus()
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    func checkNow(email: String, phone: String?) {
        isLoading = true
        apiService.checkDarkWeb(email: email, phone: phone) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let response):
                    self?.breaches = response.breaches
                    self?.loadStatus()
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                }
            }
        }
    }
}
```

##### 1.6 Интеграция в навигацию
- Добавить кнопку/карточку на главном экране (MainScreen)
- Добавить в меню настроек (SettingsScreen)
- Возможно добавить в ThreatProtectionScreen

**Итого изменений:**
- ✅ 4 новых endpoint в AppConfig
- ✅ 6 новых моделей в APIModels
- ✅ 5 новых методов в APIService
- ✅ 1 новый экран (DarkWebMonitoringScreen + ViewModel)
- ✅ 1 новый case в NavigationManager

---

#### 2. 🆔 IDENTITY THEFT PROTECTION ДЛЯ РОССИИ (18 дней)

**Что нужно добавить в iOS:**

##### 2.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Identity Theft Protection
    static let identityTheftMonitorSNILS = "/identity-theft/monitor-snils"
    static let identityTheftMonitorCredit = "/identity-theft/monitor-credit"
    static let identityTheftCheck = "/identity-theft/check"
    static let identityTheftAlerts = "/identity-theft/alerts"
    static let identityTheftStatus = "/identity-theft/status"
    static let identityTheftConsent = "/identity-theft/consent"
    static let identityTheftRevokeConsent = "/identity-theft/revoke-consent"
}
```

##### 2.2 APIModels.swift - Модели данных
```swift
// MARK: - Identity Theft Protection Models

struct IdentityTheftMonitorSNILSRequest: Codable {
    let snils: String
    let consent: Bool // Согласие на обработку данных (152-ФЗ)
}

struct IdentityTheftMonitorCreditRequest: Codable {
    let consent: Bool
}

struct IdentityTheftCheckResponse: Codable {
    let userId: String
    let riskScore: Int // 0-100
    let riskLevel: String // "low", "medium", "high", "critical"
    let alertsCount: Int
    let lastCheck: String
    let snilsMonitoring: Bool
    let creditMonitoring: Bool
}

struct IdentityTheftAlert: Codable, Identifiable {
    let id: String
    let type: String // "snils", "credit", "fraud"
    let severity: String // "low", "medium", "high", "critical"
    let title: String
    let message: String
    let detectedAt: String
    let riskScore: Int
}

struct IdentityTheftAlertsResponse: Codable {
    let alerts: [IdentityTheftAlert]
    let total: Int
    let unread: Int
}

struct IdentityTheftStatusResponse: Codable {
    let isMonitoring: Bool
    let snilsMonitoring: Bool
    let creditMonitoring: Bool
    let fraudDatabaseCheck: Bool
    let lastCheck: String?
    let riskScore: Int
    let riskLevel: String
    let totalAlerts: Int
}

struct IdentityTheftConsentRequest: Codable {
    let snils: Bool
    let passport: Bool
    let creditReport: Bool
    let consentDate: String
}

struct IdentityTheftConsentResponse: Codable {
    let success: Bool
    let consents: IdentityTheftConsents
}

struct IdentityTheftConsents: Codable {
    let snils: Bool
    let passport: Bool
    let creditReport: Bool
    let consentDate: String
}
```

##### 2.3 APIService.swift - API методы
```swift
// MARK: - Identity Theft Protection API

func monitorSNILS(snils: String, consent: Bool, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = IdentityTheftMonitorSNILSRequest(snils: snils, consent: consent)
    networkManager.post(endpoint: AppConfig.Endpoint.identityTheftMonitorSNILS, body: request, completion: completion)
}

func monitorCreditReport(consent: Bool, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = IdentityTheftMonitorCreditRequest(consent: consent)
    networkManager.post(endpoint: AppConfig.Endpoint.identityTheftMonitorCredit, body: request, completion: completion)
}

func checkIdentityTheft(completion: @escaping (Result<IdentityTheftCheckResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.identityTheftCheck, completion: completion)
}

func getIdentityTheftAlerts(completion: @escaping (Result<IdentityTheftAlertsResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.identityTheftAlerts, completion: completion)
}

func getIdentityTheftStatus(completion: @escaping (Result<IdentityTheftStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.identityTheftStatus, completion: completion)
}

func giveConsent(consents: IdentityTheftConsentRequest, completion: @escaping (Result<IdentityTheftConsentResponse, Error>) -> Void) {
    networkManager.post(endpoint: AppConfig.Endpoint.identityTheftConsent, body: consents, completion: completion)
}

func revokeConsent(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct EmptyBody: Codable {}
    networkManager.post(endpoint: AppConfig.Endpoint.identityTheftRevokeConsent, body: EmptyBody(), completion: completion)
}
```

##### 2.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case identityTheftProtection = "28_IdentityTheftProtectionScreen"
    case identityTheftConsent = "29_IdentityTheftConsentScreen"
    
    var displayName: String {
        case .identityTheftProtection: return "Защита от кражи личности"
        case .identityTheftConsent: return "Согласие на обработку данных"
    }
    
    var icon: String {
        case .identityTheftProtection: return "person.badge.shield.checkmark.fill"
        case .identityTheftConsent: return "doc.text.fill"
    }
}
```

##### 2.5 Screens/28_IdentityTheftProtectionScreen.swift - UI экран
- Статус мониторинга СНИЛС
- Статус мониторинга кредитного отчета
- Оценка риска (risk score)
- Список алертов
- Настройки мониторинга
- Кнопка для согласия на обработку данных

##### 2.6 Screens/29_IdentityTheftConsentScreen.swift - Экран согласия (152-ФЗ)
- Согласие на СНИЛС
- Согласие на паспортные данные
- Согласие на кредитный отчет
- Информация о правах пользователя
- Возможность отзыва согласия

**Итого изменений:**
- ✅ 7 новых endpoints в AppConfig
- ✅ 9 новых моделей в APIModels
- ✅ 7 новых методов в APIService
- ✅ 2 новых экрана (IdentityTheftProtectionScreen + ConsentScreen)
- ✅ 2 новых case в NavigationManager

---

#### 3. 🔐 ИНТЕГРАЦИЯ МЕНЕДЖЕРА ПАРОЛЕЙ В iOS (3-5 дней)

**Что нужно добавить в iOS:**

##### 3.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Password Manager
    static let passwordGenerate = "/password/generate"
    static let passwordSave = "/password/save"
    static let passwordGet = "/password/get"
    static let passwordCheck = "/password/check"
    static let passwordDelete = "/password/delete"
    static let passwordUpdate = "/password/update"
}
```

##### 3.2 APIModels.swift - Модели данных
```swift
// MARK: - Password Manager Models

struct PasswordGenerateRequest: Codable {
    let length: Int // 12-64
    let includeSymbols: Bool
    let includeNumbers: Bool
    let includeUppercase: Bool
    let includeLowercase: Bool
}

struct PasswordGenerateResponse: Codable {
    let password: String
    let strength: String // "weak", "medium", "strong", "very_strong"
    let score: Int // 0-100
}

struct PasswordEntry: Codable, Identifiable {
    let id: String
    let service: String
    let username: String
    let password: String
    let url: String?
    let notes: String?
    let createdAt: String
    let updatedAt: String
}

struct PasswordSaveRequest: Codable {
    let service: String
    let username: String
    let password: String
    let url: String?
    let notes: String?
}

struct PasswordGetResponse: Codable {
    let passwords: [PasswordEntry]
    let total: Int
}

struct PasswordCheckRequest: Codable {
    let password: String
}

struct PasswordCheckResponse: Codable {
    let strength: String
    let score: Int // 0-100
    let suggestions: [String]
    let isInBreachDatabase: Bool
    let breachCount: Int?
}
```

##### 3.3 APIService.swift - API методы
```swift
// MARK: - Password Manager API

func generatePassword(length: Int, includeSymbols: Bool, includeNumbers: Bool, includeUppercase: Bool, includeLowercase: Bool, completion: @escaping (Result<PasswordGenerateResponse, Error>) -> Void) {
    let request = PasswordGenerateRequest(length: length, includeSymbols: includeSymbols, includeNumbers: includeNumbers, includeUppercase: includeUppercase, includeLowercase: includeLowercase)
    networkManager.post(endpoint: AppConfig.Endpoint.passwordGenerate, body: request, completion: completion)
}

func savePassword(service: String, username: String, password: String, url: String?, notes: String?, completion: @escaping (Result<APIResponse<PasswordEntry>, Error>) -> Void) {
    let request = PasswordSaveRequest(service: service, username: username, password: password, url: url, notes: notes)
    networkManager.post(endpoint: AppConfig.Endpoint.passwordSave, body: request, completion: completion)
}

func getPasswords(completion: @escaping (Result<PasswordGetResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.passwordGet, completion: completion)
}

func checkPasswordStrength(password: String, completion: @escaping (Result<PasswordCheckResponse, Error>) -> Void) {
    let request = PasswordCheckRequest(password: password)
    networkManager.post(endpoint: AppConfig.Endpoint.passwordCheck, body: request, completion: completion)
}

func deletePassword(passwordId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    networkManager.delete(endpoint: "\(AppConfig.Endpoint.passwordDelete)/\(passwordId)", body: nil as EmptyBody?, completion: completion)
}

func updatePassword(passwordId: String, service: String?, username: String?, password: String?, url: String?, notes: String?, completion: @escaping (Result<APIResponse<PasswordEntry>, Error>) -> Void) {
    struct UpdatePasswordRequest: Codable {
        let service: String?
        let username: String?
        let password: String?
        let url: String?
        let notes: String?
    }
    let request = UpdatePasswordRequest(service: service, username: username, password: password, url: url, notes: notes)
    networkManager.put(endpoint: "\(AppConfig.Endpoint.passwordUpdate)/\(passwordId)", body: request, completion: completion)
}
```

##### 3.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case passwordManager = "30_PasswordManagerScreen"
    
    var displayName: String {
        case .passwordManager: return "Менеджер паролей"
    }
    
    var icon: String {
        case .passwordManager: return "key.fill"
    }
}
```

##### 3.5 Screens/30_PasswordManagerScreen.swift - UI экран
- Генератор паролей
- Список сохраненных паролей
- Проверка силы пароля
- Настройки менеджера паролей
- Поиск паролей

**Итого изменений:**
- ✅ 6 новых endpoints в AppConfig
- ✅ 7 новых моделей в APIModels
- ✅ 6 новых методов в APIService
- ✅ 1 новый экран (PasswordManagerScreen)
- ✅ 1 новый case в NavigationManager

---

### ✅ ФАЗА 2: НОВЫЕ КРИТИЧНЫЕ ФУНКЦИИ (17-22 дня)

---

#### 4. 🤖 AI CATEGORIES (5-7 дней)

**Что нужно добавить в iOS:**

##### 4.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // AI Categories
    static let aiCategoriesBlock = "/ai-categories/block"
    static let aiCategoriesAllow = "/ai-categories/allow"
    static let aiCategoriesStatus = "/ai-categories/status"
    static let aiCategoriesSettings = "/ai-categories/settings"
}
```

##### 4.2 APIModels.swift - Модели данных
```swift
// MARK: - AI Categories Models

struct AISite: Codable, Identifiable {
    let id: String
    let name: String
    let url: String
    let icon: String
    let description: String
    let category: String // "chat", "image", "video", "code"
}

struct AICategoriesBlockRequest: Codable {
    let siteIds: [String]
    let userId: String?
    let timeRestrictions: TimeRestrictions?
}

struct AICategoriesAllowRequest: Codable {
    let siteIds: [String]
    let userId: String?
}

struct TimeRestrictions: Codable {
    let startTime: String? // "HH:mm"
    let endTime: String? // "HH:mm"
    let daysOfWeek: [Int]? // 0-6 (Sunday-Saturday)
}

struct AICategoriesStatusResponse: Codable {
    let sites: [AISiteStatus]
    let totalBlocked: Int
    let totalAllowed: Int
}

struct AISiteStatus: Codable, Identifiable {
    let id: String
    let site: AISite
    let isBlocked: Bool
    let timeRestrictions: TimeRestrictions?
    let blockedForUsers: [String]? // User IDs
}

struct AICategoriesSettings: Codable {
    let defaultBlock: Bool
    let requireParentApproval: Bool
    let sendNotifications: Bool
    let ageRestrictions: AgeRestrictions?
}

struct AgeRestrictions: Codable {
    let minAge: Int
    let requireParentApproval: Bool
}
```

##### 4.3 APIService.swift - API методы
```swift
// MARK: - AI Categories API

func blockAISites(siteIds: [String], userId: String?, timeRestrictions: TimeRestrictions?, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = AICategoriesBlockRequest(siteIds: siteIds, userId: userId, timeRestrictions: timeRestrictions)
    networkManager.post(endpoint: AppConfig.Endpoint.aiCategoriesBlock, body: request, completion: completion)
}

func allowAISites(siteIds: [String], userId: String?, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = AICategoriesAllowRequest(siteIds: siteIds, userId: userId)
    networkManager.post(endpoint: AppConfig.Endpoint.aiCategoriesAllow, body: request, completion: completion)
}

func getAICategoriesStatus(completion: @escaping (Result<AICategoriesStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.aiCategoriesStatus, completion: completion)
}

func getAICategoriesSettings(completion: @escaping (Result<AICategoriesSettings, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.aiCategoriesSettings, completion: completion)
}
```

##### 4.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case aiCategories = "31_AICategoriesScreen"
    
    var displayName: String {
        case .aiCategories: return "AI Категории"
    }
    
    var icon: String {
        case .aiCategories: return "brain.head.profile"
    }
}
```

##### 4.5 Screens/31_AICategoriesScreen.swift - UI экран
- Список AI-сайтов (ChatGPT, Midjourney, DALL-E, Claude, Gemini)
- Настройки блокировки/разрешения
- Настройки по времени
- Настройки по возрасту
- Уведомления родителям

**Итого изменений:**
- ✅ 4 новых endpoints в AppConfig
- ✅ 8 новых моделей в APIModels
- ✅ 4 новых методов в APIService
- ✅ 1 новый экран (AICategoriesScreen)
- ✅ 1 новый case в NavigationManager

---

#### 5. 📱 РАСШИРЕННЫЙ SOCIAL MEDIA MONITORING (2-3 дня)

**Статус:** ⚠️ Частично (Instagram, Twitter/X, TikTok, VK, Telegram, WhatsApp, MAX есть)

**Что нужно добавить:**
- Обновить существующие модели для поддержки MAX и Одноклассники
- Проверить iOS интеграцию (скорее всего ничего не нужно, так как используется общий endpoint)

**Итого изменений:**
- ✅ Минимальные изменения (если нужно обновить UI)
- ✅ Возможно обновление списка платформ в UI

---

#### 6. 🚗 CRASH DETECTION (10-12 дней)

**Что нужно добавить в iOS:**

##### 6.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Crash Detection
    static let crashDetectionStart = "/crash-detection/start"
    static let crashDetectionStop = "/crash-detection/stop"
    static let crashDetectionStatus = "/crash-detection/status"
    static let crashDetectionEmergencyCall = "/crash-detection/emergency-call"
    static let crashDetectionCancelEmergencyCall = "/crash-detection/cancel-emergency-call"
}
```

##### 6.2 APIModels.swift - Модели данных
```swift
// MARK: - Crash Detection Models

struct CrashDetectionStartRequest: Codable {
    let sensitivity: String // "low", "medium", "high"
}

struct CrashDetectionStatusResponse: Codable {
    let isActive: Bool
    let sensitivity: String
    let lastDetection: String?
    let emergencyContacts: [EmergencyContact]
}

struct EmergencyContact: Codable, Identifiable {
    let id: String
    let name: String
    let phone: String
    let relationship: String?
}

struct CrashDetectionData: Codable {
    let accelerometerX: Double
    let accelerometerY: Double
    let accelerometerZ: Double
    let gyroscopeX: Double
    let gyroscopeY: Double
    let gyroscopeZ: Double
    let timestamp: String
    let location: LocationData?
}

struct LocationData: Codable {
    let latitude: Double
    let longitude: Double
    let accuracy: Double
}

struct CrashDetectionAlert: Codable {
    let detectedAt: String
    let gForce: Double
    let location: LocationData?
    let emergencyCallInitiated: Bool
    let countdownSeconds: Int
}
```

##### 6.3 APIService.swift - API методы
```swift
// MARK: - Crash Detection API

func startCrashDetection(sensitivity: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = CrashDetectionStartRequest(sensitivity: sensitivity)
    networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionStart, body: request, completion: completion)
}

func stopCrashDetection(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct EmptyBody: Codable {}
    networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionStop, body: EmptyBody(), completion: completion)
}

func getCrashDetectionStatus(completion: @escaping (Result<CrashDetectionStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.crashDetectionStatus, completion: completion)
}

func sendCrashDetectionData(_ data: CrashDetectionData, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    networkManager.post(endpoint: "/crash-detection/data", body: data, completion: completion)
}

func initiateEmergencyCall(location: LocationData, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct EmergencyCallRequest: Codable {
        let location: LocationData
    }
    let request = EmergencyCallRequest(location: location)
    networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionEmergencyCall, body: request, completion: completion)
}

func cancelEmergencyCall(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct EmptyBody: Codable {}
    networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionCancelEmergencyCall, body: EmptyBody(), completion: completion)
}
```

##### 6.4 Core/CrashDetection/CrashDetectionManager.swift - Новый менеджер
```swift
import CoreMotion
import CoreLocation

@MainActor
class CrashDetectionManager: NSObject, ObservableObject {
    @Published var isMonitoring = false
    @Published var crashDetected = false
    @Published var countdownSeconds = 10
    @Published var currentLocation: CLLocation?
    
    private let motionManager = CMMotionManager()
    private let locationManager = CLLocationManager()
    private let apiService = APIService.shared
    
    // Пороги G-сил
    private var gForceThreshold: Double {
        switch UserDefaults.standard.string(forKey: "crashDetectionSensitivity") ?? "medium" {
        case "low": return 5.0
        case "medium": return 4.0
        case "high": return 3.0
        default: return 4.0
        }
    }
    
    func startMonitoring() {
        guard motionManager.isAccelerometerAvailable else {
            print("❌ Акселерометр недоступен")
            return
        }
        
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
        
        motionManager.accelerometerUpdateInterval = 0.1
        motionManager.gyroUpdateInterval = 0.1
        
        motionManager.startAccelerometerUpdates(to: .main) { [weak self] data, error in
            guard let self = self, let data = data else { return }
            self.processAccelerometerData(data)
        }
        
        motionManager.startGyroUpdates(to: .main) { [weak self] data, error in
            guard let self = self, let data = data else { return }
            self.processGyroscopeData(data)
        }
        
        isMonitoring = true
    }
    
    private func processAccelerometerData(_ data: CMAccelerometerData) {
        let gForce = sqrt(data.acceleration.x * data.acceleration.x +
                         data.acceleration.y * data.acceleration.y +
                         data.acceleration.z * data.acceleration.z)
        
        if gForce > gForceThreshold {
            detectCrash()
        }
    }
    
    private func processGyroscopeData(_ data: CMGyroData) {
        // Дополнительная обработка данных гироскопа
    }
    
    private func detectCrash() {
        guard !crashDetected else { return }
        crashDetected = true
        
        // Отправка данных на сервер
        sendCrashDataToServer()
        
        // Обратный отсчет перед вызовом помощи
        startCountdown()
    }
    
    private func startCountdown() {
        countdownSeconds = 10
        Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] timer in
            guard let self = self else {
                timer.invalidate()
                return
            }
            
            self.countdownSeconds -= 1
            
            if self.countdownSeconds <= 0 {
                timer.invalidate()
                self.callEmergency()
            }
        }
    }
    
    private func callEmergency() {
        guard let location = currentLocation else { return }
        
        let locationData = LocationData(
            latitude: location.coordinate.latitude,
            longitude: location.coordinate.longitude,
            accuracy: location.horizontalAccuracy
        )
        
        apiService.initiateEmergencyCall(location: locationData) { result in
            switch result {
            case .success:
                // Открыть экран с подтверждением
                break
            case .failure(let error):
                print("❌ Ошибка вызова помощи: \(error)")
            }
        }
    }
    
    private func sendCrashDataToServer() {
        guard let location = currentLocation else { return }
        
        let data = CrashDetectionData(
            accelerometerX: 0, // Получить из motionManager
            accelerometerY: 0,
            accelerometerZ: 0,
            gyroscopeX: 0,
            gyroscopeY: 0,
            gyroscopeZ: 0,
            timestamp: ISO8601DateFormatter().string(from: Date()),
            location: LocationData(
                latitude: location.coordinate.latitude,
                longitude: location.coordinate.longitude,
                accuracy: location.horizontalAccuracy
            )
        )
        
        apiService.sendCrashDetectionData(data) { result in
            switch result {
            case .success:
                print("✅ Данные об аварии отправлены")
            case .failure(let error):
                print("❌ Ошибка отправки данных: \(error)")
            }
        }
    }
}

extension CrashDetectionManager: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        currentLocation = locations.last
    }
}
```

##### 6.5 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case crashDetection = "32_CrashDetectionScreen"
    
    var displayName: String {
        case .crashDetection: return "Обнаружение аварий"
    }
    
    var icon: String {
        case .crashDetection: return "car.fill"
    }
}
```

##### 6.6 Screens/32_CrashDetectionScreen.swift - UI экран
- Статус мониторинга
- Настройки чувствительности
- Экстренные контакты
- Обратный отсчет при обнаружении аварии
- Кнопка отмены экстренного вызова

**Итого изменений:**
- ✅ 5 новых endpoints в AppConfig
- ✅ 6 новых моделей в APIModels
- ✅ 6 новых методов в APIService
- ✅ 1 новый менеджер (CrashDetectionManager)
- ✅ 1 новый экран (CrashDetectionScreen)
- ✅ 1 новый case в NavigationManager
- ✅ Интеграция с CoreMotion и CoreLocation

---

### ✅ ФАЗА 3: ВАЖНЫЕ ФУНКЦИИ (36-46 дней)

---

#### 7. 📊 DRIVING REPORTS (8-10 дней)

**Что нужно добавить в iOS:**

##### 7.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Driving Reports
    static let drivingReportsGenerate = "/driving-reports/generate"
    static let drivingReportsReport = "/driving-reports/report"
    static let drivingReportsWeekly = "/driving-reports/weekly"
    static let drivingReportsSettings = "/driving-reports/settings"
}
```

##### 7.2 APIModels.swift - Модели данных
```swift
// MARK: - Driving Reports Models

struct DrivingReport: Codable, Identifiable {
    let id: String
    let userId: String
    let startDate: String
    let endDate: String
    let totalDistance: Double // км
    let averageSpeed: Double // км/ч
    let maxSpeed: Double // км/ч
    let phoneUsageMinutes: Int
    let hardBrakingCount: Int
    let speedingCount: Int
    let safetyScore: Int // 0-100
    let safetyLevel: String // "excellent", "good", "fair", "poor"
}

struct DrivingReportsGenerateRequest: Codable {
    let startDate: String
    let endDate: String
}

struct DrivingReportsWeeklyResponse: Codable {
    let weekStartDate: String
    let weekEndDate: String
    let report: DrivingReport
    let dailyReports: [DailyDrivingReport]
}

struct DailyDrivingReport: Codable, Identifiable {
    let id: String
    let date: String
    let distance: Double
    let averageSpeed: Double
    let violations: Int
    let safetyScore: Int
}
```

##### 7.3 APIService.swift - API методы
```swift
// MARK: - Driving Reports API

func generateDrivingReport(startDate: String, endDate: String, completion: @escaping (Result<APIResponse<DrivingReport>, Error>) -> Void) {
    let request = DrivingReportsGenerateRequest(startDate: startDate, endDate: endDate)
    networkManager.post(endpoint: AppConfig.Endpoint.drivingReportsGenerate, body: request, completion: completion)
}

func getDrivingReport(reportId: String, completion: @escaping (Result<DrivingReport, Error>) -> Void) {
    networkManager.get(endpoint: "\(AppConfig.Endpoint.drivingReportsReport)/\(reportId)", completion: completion)
}

func getWeeklyDrivingReport(completion: @escaping (Result<DrivingReportsWeeklyResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.drivingReportsWeekly, completion: completion)
}
```

##### 7.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case drivingReports = "33_DrivingReportsScreen"
    
    var displayName: String {
        case .drivingReports: return "Отчеты о вождении"
    }
    
    var icon: String {
        case .drivingReports: return "chart.line.uptrend.xyaxis"
    }
}
```

##### 7.5 Screens/33_DrivingReportsScreen.swift - UI экран
- Еженедельный отчет
- Графики скорости
- Статистика нарушений
- Оценка безопасности вождения
- Детальные отчеты по дням

**Итого изменений:**
- ✅ 4 новых endpoints в AppConfig
- ✅ 4 новых моделей в APIModels
- ✅ 3 новых методов в APIService
- ✅ 1 новый экран (DrivingReportsScreen)
- ✅ 1 новый case в NavigationManager

---

#### 8. 🗑️ PERSONAL DATA CLEANUP (10-12 дней)

**Что нужно добавить в iOS:**

##### 8.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Personal Data Cleanup
    static let dataCleanupScan = "/data-cleanup/scan"
    static let dataCleanupRemove = "/data-cleanup/remove"
    static let dataCleanupStatus = "/data-cleanup/status"
    static let dataCleanupReport = "/data-cleanup/report"
}
```

##### 8.2 APIModels.swift - Модели данных
```swift
// MARK: - Personal Data Cleanup Models

struct BrokerSite: Codable, Identifiable {
    let id: String
    let name: String
    let url: String
    let foundData: [String] // ["Email", "Phone", "Address"]
    let removalStatus: String // "not_started", "in_progress", "completed", "failed"
    let removalRequestId: String?
}

struct DataCleanupScanResponse: Codable {
    let sites: [BrokerSite]
    let totalSites: Int
    let sitesWithData: Int
}

struct DataCleanupRemoveRequest: Codable {
    let siteIds: [String]
}

struct DataCleanupStatusResponse: Codable {
    let inProgress: Int
    let completed: Int
    let failed: Int
    let total: Int
    let sites: [BrokerSite]
}

struct DataCleanupReport: Codable {
    let totalScans: Int
    let totalRemovals: Int
    let successfulRemovals: Int
    let failedRemovals: Int
    let lastScanDate: String?
}
```

##### 8.3 APIService.swift - API методы
```swift
// MARK: - Personal Data Cleanup API

func scanBrokerSites(completion: @escaping (Result<DataCleanupScanResponse, Error>) -> Void) {
    struct EmptyBody: Codable {}
    networkManager.post(endpoint: AppConfig.Endpoint.dataCleanupScan, body: EmptyBody(), completion: completion)
}

func removeDataFromBrokerSites(siteIds: [String], completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    let request = DataCleanupRemoveRequest(siteIds: siteIds)
    networkManager.post(endpoint: AppConfig.Endpoint.dataCleanupRemove, body: request, completion: completion)
}

func getDataCleanupStatus(completion: @escaping (Result<DataCleanupStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.dataCleanupStatus, completion: completion)
}

func getDataCleanupReport(completion: @escaping (Result<DataCleanupReport, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.dataCleanupReport, completion: completion)
}
```

##### 8.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case personalDataCleanup = "34_PersonalDataCleanupScreen"
    
    var displayName: String {
        case .personalDataCleanup: return "Очистка персональных данных"
    }
    
    var icon: String {
        case .personalDataCleanup: return "trash.fill"
    }
}
```

##### 8.5 Screens/34_PersonalDataCleanupScreen.swift - UI экран
- Список найденных сайтов
- Кнопка запуска сканирования
- Кнопка запуска удаления
- Отчет о процессе удаления
- Статус удаления для каждого сайта

**Итого изменений:**
- ✅ 4 новых endpoints в AppConfig
- ✅ 5 новых моделей в APIModels
- ✅ 4 новых методов в APIService
- ✅ 1 новый экран (PersonalDataCleanupScreen)
- ✅ 1 новый case в NavigationManager

---

#### 9. 🛡️ ANTI-TRACKER (5-7 дней)

**Что нужно добавить в iOS:**

##### 9.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Anti-Tracker
    static let antiTrackerBlock = "/anti-tracker/block"
    static let antiTrackerStatus = "/anti-tracker/status"
    static let antiTrackerStats = "/anti-tracker/stats"
    static let antiTrackerSettings = "/anti-tracker/settings"
}
```

##### 9.2 APIModels.swift - Модели данных
```swift
// MARK: - Anti-Tracker Models

struct Tracker: Codable, Identifiable {
    let id: String
    let name: String
    let domain: String
    let category: String // "advertising", "analytics", "social", "other"
    let isBlocked: Bool
}

struct AntiTrackerStatsResponse: Codable {
    let totalTrackersBlocked: Int
    let trackersBlockedToday: Int
    let adsBlocked: Int
    let adsBlockedToday: Int
    let dataSavedMB: Double
    let timeSavedMinutes: Int
    let topBlockedTrackers: [Tracker]
}

struct AntiTrackerStatusResponse: Codable {
    let isEnabled: Bool
    let isIntegratedWithVPN: Bool
    let blockedTrackers: [Tracker]
    let totalBlocked: Int
}

struct AntiTrackerSettings: Codable {
    let blockAds: Bool
    let blockAnalytics: Bool
    let blockSocialTrackers: Bool
    let whitelistDomains: [String]
}
```

##### 9.3 APIService.swift - API методы
```swift
// MARK: - Anti-Tracker API

func blockTrackers(trackerIds: [String]?, enable: Bool, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct BlockTrackersRequest: Codable {
        let trackerIds: [String]?
        let enable: Bool
    }
    let request = BlockTrackersRequest(trackerIds: trackerIds, enable: enable)
    networkManager.post(endpoint: AppConfig.Endpoint.antiTrackerBlock, body: request, completion: completion)
}

func getAntiTrackerStatus(completion: @escaping (Result<AntiTrackerStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.antiTrackerStatus, completion: completion)
}

func getAntiTrackerStats(completion: @escaping (Result<AntiTrackerStatsResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.antiTrackerStats, completion: completion)
}

func getAntiTrackerSettings(completion: @escaping (Result<AntiTrackerSettings, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.antiTrackerSettings, completion: completion)
}

func updateAntiTrackerSettings(_ settings: AntiTrackerSettings, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    networkManager.post(endpoint: AppConfig.Endpoint.antiTrackerSettings, body: settings, completion: completion)
}
```

##### 9.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case antiTracker = "35_AntiTrackerScreen"
    
    var displayName: String {
        case .antiTracker: return "Анти-трекер"
    }
    
    var icon: String {
        case .antiTracker: return "eye.slash.fill"
    }
}
```

##### 9.5 Screens/35_AntiTrackerScreen.swift - UI экран
- Статистика заблокированных трекеров
- Настройки блокировки
- Интеграция с VPN
- Список заблокированных трекеров

**Итого изменений:**
- ✅ 4 новых endpoints в AppConfig
- ✅ 4 новых моделей в APIModels
- ✅ 5 новых методов в APIService
- ✅ 1 новый экран (AntiTrackerScreen)
- ✅ 1 новый case в NavigationManager
- ✅ Интеграция с VPN модулем

---

#### 10. 🚑 ROADSIDE ASSISTANCE (10-12 дней)

**Что нужно добавить в iOS:**

##### 10.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Roadside Assistance
    static let roadsideAssistanceCall = "/roadside-assistance/call"
    static let roadsideAssistanceStatus = "/roadside-assistance/status"
    static let roadsideAssistanceCancel = "/roadside-assistance/cancel"
    static let roadsideAssistanceHistory = "/roadside-assistance/history"
}
```

##### 10.2 APIModels.swift - Модели данных
```swift
// MARK: - Roadside Assistance Models

enum ProblemType: String, Codable, CaseIterable {
    case flatTire = "flat_tire"
    case batteryDead = "battery_dead"
    case keysLocked = "keys_locked"
    case outOfGas = "out_of_gas"
    case engineWontStart = "engine_wont_start"
    case towing = "towing"
    case other = "other"
    
    var displayName: String {
        switch self {
        case .flatTire: return "Прокол колеса"
        case .batteryDead: return "Разрядился аккумулятор"
        case .keysLocked: return "Ключи в машине"
        case .outOfGas: return "Закончился бензин"
        case .engineWontStart: return "Не заводится"
        case .towing: return "Буксировка"
        case .other: return "Другое"
        }
    }
}

struct RoadsideAssistanceCallRequest: Codable {
    let problemType: ProblemType
    let location: LocationData
    let description: String?
    let vehicleInfo: VehicleInfo?
}

struct VehicleInfo: Codable {
    let make: String?
    let model: String?
    let year: Int?
    let color: String?
    let licensePlate: String?
}

struct RoadsideAssistanceStatusResponse: Codable {
    let requestId: String
    let status: String // "pending", "assigned", "in_transit", "arrived", "completed", "cancelled"
    let estimatedArrival: String?
    let providerName: String?
    let providerPhone: String?
    let location: LocationData?
}

struct RoadsideAssistanceHistoryItem: Codable, Identifiable {
    let id: String
    let problemType: ProblemType
    let status: String
    let requestedAt: String
    let completedAt: String?
    let providerName: String?
}
```

##### 10.3 APIService.swift - API методы
```swift
// MARK: - Roadside Assistance API

func callRoadsideAssistance(problemType: ProblemType, location: LocationData, description: String?, vehicleInfo: VehicleInfo?, completion: @escaping (Result<APIResponse<RoadsideAssistanceStatusResponse>, Error>) -> Void) {
    let request = RoadsideAssistanceCallRequest(problemType: problemType, location: location, description: description, vehicleInfo: vehicleInfo)
    networkManager.post(endpoint: AppConfig.Endpoint.roadsideAssistanceCall, body: request, completion: completion)
}

func getRoadsideAssistanceStatus(requestId: String, completion: @escaping (Result<RoadsideAssistanceStatusResponse, Error>) -> Void) {
    networkManager.get(endpoint: "\(AppConfig.Endpoint.roadsideAssistanceStatus)/\(requestId)", completion: completion)
}

func cancelRoadsideAssistance(requestId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    struct EmptyBody: Codable {}
    networkManager.post(endpoint: "\(AppConfig.Endpoint.roadsideAssistanceCancel)/\(requestId)", body: EmptyBody(), completion: completion)
}

func getRoadsideAssistanceHistory(completion: @escaping (Result<[RoadsideAssistanceHistoryItem], Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.roadsideAssistanceHistory, completion: completion)
}
```

##### 10.4 NavigationManager.swift - Новый экран
```swift
enum ALADDINScreen: String, CaseIterable {
    case roadsideAssistance = "36_RoadsideAssistanceScreen"
    
    var displayName: String {
        case .roadsideAssistance: return "Помощь на дороге"
    }
    
    var icon: String {
        case .roadsideAssistance: return "car.2.fill"
    }
}
```

##### 10.5 Screens/36_RoadsideAssistanceScreen.swift - UI экран
- Кнопка вызова помощи
- Выбор типа проблемы
- Отслеживание статуса помощи
- История вызовов
- Автоматическое определение местоположения

**Итого изменений:**
- ✅ 4 новых endpoints в AppConfig
- ✅ 5 новых моделей в APIModels
- ✅ 4 новых методов в APIService
- ✅ 1 новый экран (RoadsideAssistanceScreen)
- ✅ 1 новый case в NavigationManager
- ✅ Интеграция с CoreLocation

---

#### 11. 💭 BUBBLES FEATURE (3-5 дней)

**Что нужно добавить в iOS:**

##### 11.1 AppConfig.swift - Endpoints
```swift
enum Endpoint {
    // Bubbles (Approximate Location)
    static let locationBubble = "/location/bubble"
    static let locationBubbleSettings = "/location/bubble/settings"
}
```

##### 11.2 APIModels.swift - Модели данных
```swift
// MARK: - Bubbles (Location) Models

enum BubbleRadius: String, Codable, CaseIterable {
    case small = "100" // 100м
    case medium = "500" // 500м
    case large = "1000" // 1км
    
    var displayName: String {
        switch self {
        case .small: return "100 м"
        case .medium: return "500 м"
        case .large: return "1 км"
        }
    }
    
    var meters: Double {
        switch self {
        case .small: return 100
        case .medium: return 500
        case .large: return 1000
        }
    }
}

struct BubbleLocationRequest: Codable {
    let userId: String
    let radius: BubbleRadius
}

struct BubbleLocationResponse: Codable {
    let userId: String
    let approximateLocation: LocationData
    let radius: BubbleRadius
    let centerLocation: LocationData // Точное местоположение (не передается пользователю)
}

struct BubbleSettings: Codable {
    let userId: String?
    let radius: BubbleRadius
    let enabledForTime: TimeRestrictions?
    let enabled: Bool
}
```

##### 11.3 APIService.swift - API методы
```swift
// MARK: - Bubbles (Location) API

func getBubbleLocation(userId: String, radius: BubbleRadius, completion: @escaping (Result<BubbleLocationResponse, Error>) -> Void) {
    let request = BubbleLocationRequest(userId: userId, radius: radius)
    networkManager.post(endpoint: AppConfig.Endpoint.locationBubble, body: request, completion: completion)
}

func getBubbleSettings(userId: String?, completion: @escaping (Result<BubbleSettings, Error>) -> Void) {
    let query = userId != nil ? "?userId=\(userId!)" : ""
    networkManager.get(endpoint: "\(AppConfig.Endpoint.locationBubbleSettings)\(query)", completion: completion)
}

func updateBubbleSettings(_ settings: BubbleSettings, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    networkManager.post(endpoint: AppConfig.Endpoint.locationBubbleSettings, body: settings, completion: completion)
}
```

##### 11.4 Обновление существующего экрана геолокации
- Обновить FamilyScreen или существующий экран геолокации
- Добавить настройки пузыря (радиус, время)
- Отображать приблизительное местоположение вместо точного

**Итого изменений:**
- ✅ 2 новых endpoints в AppConfig
- ✅ 3 новых моделей в APIModels
- ✅ 3 новых методов в APIService
- ✅ Обновление существующего экрана геолокации
- ✅ Нет нового экрана (расширение существующего)

---

## 📊 ОБЩИЕ ИЗМЕНЕНИЯ

### Сводная таблица изменений

| Функция | Endpoints | Модели | Методы API | Экраны | Менеджеры | Особенности |
|---------|-----------|--------|------------|--------|-----------|-------------|
| Dark Web | 5 | 6 | 5 | 1 | - | - |
| Identity Theft | 7 | 9 | 7 | 2 | - | Согласие 152-ФЗ |
| Password Manager | 6 | 7 | 6 | 1 | - | - |
| AI Categories | 4 | 8 | 4 | 1 | - | - |
| Social Media | 0 | 0 | 0 | 0 | - | Расширение существующего |
| Crash Detection | 5 | 6 | 6 | 1 | 1 | CoreMotion + CoreLocation |
| Driving Reports | 4 | 4 | 3 | 1 | - | - |
| Data Cleanup | 4 | 5 | 4 | 1 | - | - |
| Anti-Tracker | 4 | 4 | 5 | 1 | - | Интеграция с VPN |
| Roadside Assistance | 4 | 5 | 4 | 1 | - | CoreLocation |
| Bubbles | 2 | 3 | 3 | 0 | - | Расширение геолокации |

**Итого:**
- ✅ **46 новых endpoints** в AppConfig
- ✅ **57 новых моделей** в APIModels
- ✅ **47 новых методов** в APIService
- ✅ **10 новых экранов** (11 функций, но Bubbles расширяет существующий)
- ✅ **1 новый менеджер** (CrashDetectionManager)
- ✅ **11 новых case** в NavigationManager

---

## 🎯 ПОРЯДОК РЕАЛИЗАЦИИ

### Рекомендуемый порядок (по фазам):

#### ФАЗА 1 (Критичные функции):
1. ✅ Dark Web мониторинг
2. ✅ Identity Theft Protection
3. ✅ Интеграция менеджера паролей

#### ФАЗА 2 (Новые критичные функции):
4. ✅ AI Categories
5. ✅ Расширенный Social Media Monitoring
6. ✅ Crash Detection

#### ФАЗА 3 (Важные функции):
7. ✅ Driving Reports
8. ✅ Personal Data Cleanup
9. ✅ Anti-Tracker
10. ✅ Roadside Assistance
11. ✅ Bubbles Feature

---

## ✅ ЧЕКЛИСТ ИНТЕГРАЦИИ

### Для каждой функции:

#### 1. AppConfig.swift
- [ ] Добавить endpoints в enum `Endpoint`
- [ ] Проверить соответствие с серверными endpoints

#### 2. APIModels.swift
- [ ] Создать Request модели
- [ ] Создать Response модели
- [ ] Добавить Codable conformance
- [ ] Добавить Identifiable для списков
- [ ] Добавить комментарии MARK

#### 3. APIService.swift
- [ ] Добавить методы в соответствующую MARK секцию
- [ ] Реализовать обработку ошибок
- [ ] Использовать правильные HTTP методы (GET/POST/PUT/DELETE)
- [ ] Передавать правильные параметры

#### 4. NavigationManager.swift
- [ ] Добавить case в enum `ALADDINScreen`
- [ ] Добавить displayName
- [ ] Добавить icon
- [ ] Обновить getView() если нужно

#### 5. Screen.swift
- [ ] Создать файл экрана в папке Screens/
- [ ] Использовать паттерн существующих экранов
- [ ] Добавить ALADDINNavigationBar
- [ ] Добавить ViewModel (если нужен)
- [ ] Реализовать UI компоненты
- [ ] Добавить обработку ошибок
- [ ] Добавить loading состояния

#### 6. Интеграция
- [ ] Добавить навигацию к экрану (кнопка/карточка)
- [ ] Проверить работу навигации
- [ ] Тестирование API запросов
- [ ] Тестирование UI

#### 7. Особые случаи
- [ ] Crash Detection: CoreMotion + CoreLocation интеграция
- [ ] Identity Theft: Экран согласия 152-ФЗ
- [ ] Anti-Tracker: Интеграция с VPN модулем
- [ ] Bubbles: Обновление существующего экрана геолокации

---

## 📝 ПРИМЕЧАНИЯ

### Важные моменты:

1. **Паттерны кода:**
   - Все экраны должны использовать `ALADDINNavigationBar`
   - Все экраны должны использовать `LinearGradient.backgroundGradient`
   - Все экраны должны иметь `@Environment(\.dismiss)` для навигации назад
   - ViewModels должны быть `@MainActor` для UI обновлений

2. **Обработка ошибок:**
   - Все API методы должны обрабатывать ошибки
   - Показывать пользователю понятные сообщения об ошибках
   - Логировать ошибки для отладки

3. **Состояния загрузки:**
   - Показывать индикаторы загрузки при запросах
   - Блокировать повторные запросы во время загрузки

4. **Локализация:**
   - Все тексты должны быть локализованы через `LocalizationManager`
   - Использовать ключи локализации вместо хардкода

5. **Тестирование:**
   - Тестировать все API методы
   - Тестировать навигацию
   - Тестировать UI взаимодействия

---

**Дата создания:** 9 декабря 2025  
**Статус:** ✅ Готов к реализации  
**Автор:** AI Assistant для ALADDIN Project

---

**Удачи в реализации! 🚀**

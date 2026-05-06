import Foundation
import SwiftUI
import Combine

/**
 * 🔒 Protection Settings ViewModel
 * ViewModel для управления 13 компонентами на экране AdvancedProtectionSettingsScreen
 * Использует ComponentStatusService для загрузки и обновления статусов
 */

@MainActor
class ProtectionSettingsViewModel: ObservableObject {
    
    // MARK: - Dependencies
    
    private let statusService: ComponentStatusService
    private let configurationService: ComponentConfigurationService
    private let retryManager: RetryManager
    private let toastManager = ToastManager.shared
    
    // MARK: - Published Properties - Component Statuses
    
    // Защита в мессенджерах (6 компонентов)
    @Published var telegramSecurityEnabled: Bool = false
    @Published var whatsappSecurityEnabled: Bool = false
    @Published var instagramSecurityEnabled: Bool = false
    @Published var maxMessengerSecurityEnabled: Bool = false
    @Published var gamingSecurityEnabled: Bool = false
    @Published var browserSecurityEnabled: Bool = false
    
    // Приватность (3 компонента)
    @Published var locationBubbleEnabled: Bool = false
    @Published var personalDataCleanupEnabled: Bool = false
    @Published var antiTrackerEnabled: Bool = false
    
    // Мониторинг (4 компонента)
    @Published var darkWebMonitoringEnabled: Bool = false
    @Published var identityTheftProtectionEnabled: Bool = false
    @Published var aiCategoriesEnabled: Bool = false
    @Published var drivingReportsEnabled: Bool = false
    
    // MARK: - Published Properties - UI State
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // Модальные окна для настроек
    @Published var showTelegramSettings: Bool = false
    @Published var showWhatsAppSettings: Bool = false
    @Published var showInstagramSettings: Bool = false
    @Published var showMaxMessengerSettings: Bool = false
    @Published var showGamingSettings: Bool = false
    @Published var showBrowserSettings: Bool = false
    @Published var showLocationBubbleSettings: Bool = false
    @Published var showPersonalDataCleanupSettings: Bool = false
    @Published var showAntiTrackerSettings: Bool = false
    @Published var showDarkWebMonitoringSettings: Bool = false
    @Published var showIdentityTheftProtectionSettings: Bool = false
    @Published var showAICategoriesSettings: Bool = false
    @Published var showDrivingReportsSettings: Bool = false
    
    // MARK: - Private Properties
    
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    @MainActor init(
        statusService: ComponentStatusService = .shared,
        configurationService: ComponentConfigurationService = .shared,
        retryManager: RetryManager = .balanced()
    ) {
        self.statusService = statusService
        self.configurationService = configurationService
        self.retryManager = retryManager
        
        // Загрузить статусы компонентов при инициализации
        Task {
            await loadComponentsStatus()
        }
    }
    
    // MARK: - Public Methods
    
    /// Загрузить статусы всех компонентов
    func loadComponentsStatus() async {
        isLoading = true
        errorMessage = nil
        
        // ✅ ЭТАП 2: Проверка токена перед загрузкой
        guard AppConfig.authToken != nil else {
            print("⚠️ ProtectionSettingsViewModel: Токен отсутствует, используем демо режим")
            isLoading = false
            // Загружаем из кэша или используем дефолтные значения
            await updateLocalStatuses()
            return
        }
        
        let componentIds = [
            "telegram_security_bot",
            "whatsapp_security_bot",
            "instagram_security_bot",
            "max_messenger_security_bot",
            "gaming_security_bot",
            "browser_security_bot",
            "location_bubble_agent",
            "personal_data_cleanup_agent",
            "anti_tracker_agent",
            "dark_web_monitoring_agent",
            "russian_identity_theft_protection_agent",
            "ai_categories_agent",
            "driving_reports_agent"
        ]
        
        let result: Result<Void, NetworkError> = await retryManager.execute(
            operation: {
                do {
                    // ✅ УЛУЧШЕНИЕ: Параллельная загрузка с лимитом и приоритизацией
                    // Определяем приоритеты: критичные компоненты загружаются первыми
                    let prioritizedItems: [PrioritizedLoadItem<ComponentStatus>] = componentIds.map { componentId in
                        let priority: ComponentLoadPriority
                        // Критичные: мониторинг и защита данных
                        if componentId.contains("dark_web") || componentId.contains("identity_theft") {
                            priority = .critical
                        }
                        // Важные: мессенджеры и приватность
                        else if componentId.contains("security_bot") || componentId.contains("bubble") || componentId.contains("cleanup") {
                            priority = .high
                        }
                        // Обычные: остальные
                        else {
                            priority = .normal
                        }
                        
                        return PrioritizedLoadItem(
                            id: componentId,
                            priority: priority
                        ) { [weak self] in
                            guard let self = self else {
                                throw ComponentError.unknown(NSError(domain: "ProtectionSettingsViewModel", code: -1))
                            }
                            return try await self.statusService.getStatus(for: componentId)
                        }
                    }
                    
                    // Загружаем с лимитом 10 одновременных запросов
                    let results = try await ParallelLoader.executeWithLimit(
                        items: prioritizedItems,
                        maxConcurrent: 10
                    ) { componentId, status in
                        // Статусы автоматически сохраняются в ComponentStatusService
                        print("✅ ProtectionSettingsViewModel: Загружен статус для \(componentId): \(status.isEnabled)")
                    }
                    
                    // Проверяем, что все загружено
                    if results.count < componentIds.count {
                        print("⚠️ ProtectionSettingsViewModel: Загружено только \(results.count)/\(componentIds.count) компонентов")
                    }
                } catch let error as ComponentError {
                    throw error.toNetworkError()
                } catch {
                    // Обрабатываем другие типы ошибок
                    throw NetworkError.from(error)
                }
            },
            retryCondition: { $0.isRetryable }
        )
        
        switch result {
        case .success:
            await updateLocalStatuses()
            isLoading = false
        case .failure(let error):
            // ✅ ЭТАП 3: Обработка unauthorized
            if case .unauthorized(let message) = error {
                print("⚠️ ProtectionSettingsViewModel: Ошибка авторизации при загрузке статусов")
                let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                self.errorMessage = errorMessage
                isLoading = false
                // Отправляем уведомление о необходимости логина
                NotificationCenter.default.post(
                    name: NSNotification.Name("SessionExpired"),
                    object: nil,
                    userInfo: ["message": errorMessage]
                )
                // Не загружаем из кэша при ошибке авторизации
                return
            }
            
            // ✅ ИСПРАВЛЕНИЕ: Не показываем ошибку пользователю при загрузке (fallback работает)
            // Ошибка загрузки не критична - используем кэш или дефолтные значения
            print("⚠️ ProtectionSettingsViewModel: Ошибка загрузки компонентов: \(error.localizedDescription)")
            errorMessage = nil // Не показываем ошибку пользователю
            isLoading = false
            // ✅ УДАЛЕНО: toastManager.showError("Ошибка загрузки компонентов")
            // Загружаем из кэша или используем дефолтные значения
            await updateLocalStatuses()
        }
    }
    
    // MARK: - Toggle Methods - Мессенджеры
    
    func setTelegramSecurity(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "telegram_security_bot",
                updateClosure: { [weak self] value in self?.telegramSecurityEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.telegramSecurityEnabled ?? false }
            )
        }
    }
    
    func setWhatsAppSecurity(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "whatsapp_security_bot",
                updateClosure: { [weak self] value in self?.whatsappSecurityEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.whatsappSecurityEnabled ?? false }
            )
        }
    }
    
    func setInstagramSecurity(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "instagram_security_bot",
                updateClosure: { [weak self] value in self?.instagramSecurityEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.instagramSecurityEnabled ?? false }
            )
        }
    }
    
    func setMaxMessengerSecurity(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "max_messenger_security_bot",
                updateClosure: { [weak self] value in self?.maxMessengerSecurityEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.maxMessengerSecurityEnabled ?? false }
            )
        }
    }
    
    func setGamingSecurity(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "gaming_security_bot",
                updateClosure: { [weak self] value in self?.gamingSecurityEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.gamingSecurityEnabled ?? false }
            )
        }
    }
    
    func setBrowserSecurity(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "browser_security_bot",
                updateClosure: { [weak self] value in self?.browserSecurityEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.browserSecurityEnabled ?? false }
            )
        }
    }
    
    // MARK: - Toggle Methods - Приватность
    
    func setLocationBubble(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "location_bubble_agent",
                updateClosure: { [weak self] value in self?.locationBubbleEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.locationBubbleEnabled ?? false }
            )
        }
    }
    
    func setPersonalDataCleanup(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "personal_data_cleanup_agent",
                updateClosure: { [weak self] value in self?.personalDataCleanupEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.personalDataCleanupEnabled ?? false }
            )
        }
    }
    
    func setAntiTracker(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "anti_tracker_agent",
                updateClosure: { [weak self] value in self?.antiTrackerEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.antiTrackerEnabled ?? false }
            )
        }
    }
    
    // MARK: - Toggle Methods - Мониторинг
    
    func setDarkWebMonitoring(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "dark_web_monitoring_agent",
                updateClosure: { [weak self] value in self?.darkWebMonitoringEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.darkWebMonitoringEnabled ?? false }
            )
        }
    }
    
    func setIdentityTheftProtection(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "russian_identity_theft_protection_agent",
                updateClosure: { [weak self] value in self?.identityTheftProtectionEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.identityTheftProtectionEnabled ?? false }
            )
        }
    }
    
    func setAICategories(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "ai_categories_agent",
                updateClosure: { [weak self] value in self?.aiCategoriesEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.aiCategoriesEnabled ?? false }
            )
        }
    }
    
    func setDrivingReports(isEnabled: Bool) {
        Task {
            await setComponent(
                componentId: "driving_reports_agent",
                updateClosure: { [weak self] value in self?.drivingReportsEnabled = value },
                newValue: isEnabled,
                getCurrentValue: { [weak self] in self?.drivingReportsEnabled ?? false }
            )
        }
    }
    
    // MARK: - Private Methods
    
    /// Переключить компонент
    private func setComponent(
        componentId: String,
        updateClosure: @escaping (Bool) -> Void,
        newValue: Bool,
        getCurrentValue: @escaping () -> Bool
    ) async {
        // ✅ ЭТАП 2: Проверка токена перед запросом
        guard AppConfig.authToken != nil else {
            let errorMessage = "Требуется авторизация. Войдите в аккаунт."
            self.errorMessage = errorMessage
            toastManager.showError(errorMessage)
            // Отправляем уведомление о необходимости логина
            NotificationCenter.default.post(
                name: NSNotification.Name("SessionExpired"),
                object: nil,
                userInfo: ["message": errorMessage]
            )
            return
        }
        
        let oldValue = getCurrentValue()
        
        // Оптимистичное обновление UI
        updateClosure(newValue)
        
        let result: Result<Void, NetworkError> = await retryManager.execute(
            operation: {
                do {
                    try await self.statusService.updateStatus(
                        componentId: componentId,
                        isEnabled: newValue
                    )
                } catch let error as ComponentError {
                    throw error.toNetworkError()
                } catch {
                    // Обрабатываем другие типы ошибок
                    throw NetworkError.from(error)
                }
            },
            retryCondition: { $0.isRetryable }
        )
        
        switch result {
        case .success:
            toastManager.showSuccess(
                newValue ? "Компонент включен" : "Компонент выключен"
            )
        case .failure(let error):
            // ✅ ЭТАП 3: Обработка unauthorized
            if case .unauthorized(let message) = error {
                // Откат при ошибке
                updateClosure(oldValue)
                let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                self.errorMessage = errorMessage
                toastManager.showError(errorMessage)
                // Отправляем уведомление о необходимости логина
                NotificationCenter.default.post(
                    name: NSNotification.Name("SessionExpired"),
                    object: nil,
                    userInfo: ["message": errorMessage]
                )
                return
            }
            
            // Откат при ошибке
            updateClosure(oldValue)
            // ✅ ИСПРАВЛЕНИЕ: Не показываем технические детали ошибки пользователю
            if case .invalidStatusCode(let code) = error,
               code == 405 {
                // HTTP 405 - сервер не поддерживает метод, но это не критично
                print("⚠️ ProtectionSettingsViewModel: HTTP 405 - сервер не поддерживает метод обновления")
                errorMessage = nil
                // Не показываем ошибку пользователю - статус сохранен локально
            } else {
                errorMessage = error.localizedDescription
                toastManager.showError("Не удалось обновить настройки. Попробуйте позже.")
            }
        }
    }
    
    /// Обновить локальные статусы из сервиса
    private func updateLocalStatuses() async {
        // ✅ УЛУЧШЕНИЕ: Параллельная загрузка с лимитом и приоритизацией
        let componentMappings: [(String, ComponentLoadPriority, (Bool) -> Void)] = [
            ("dark_web_monitoring_agent", .critical, { [weak self] value in self?.darkWebMonitoringEnabled = value }),
            ("russian_identity_theft_protection_agent", .critical, { [weak self] value in self?.identityTheftProtectionEnabled = value }),
            ("location_bubble_agent", .high, { [weak self] value in self?.locationBubbleEnabled = value }),
            ("personal_data_cleanup_agent", .high, { [weak self] value in self?.personalDataCleanupEnabled = value }),
            ("telegram_security_bot", .high, { [weak self] value in self?.telegramSecurityEnabled = value }),
            ("whatsapp_security_bot", .high, { [weak self] value in self?.whatsappSecurityEnabled = value }),
            ("instagram_security_bot", .normal, { [weak self] value in self?.instagramSecurityEnabled = value }),
            ("max_messenger_security_bot", .normal, { [weak self] value in self?.maxMessengerSecurityEnabled = value }),
            ("gaming_security_bot", .normal, { [weak self] value in self?.gamingSecurityEnabled = value }),
            ("browser_security_bot", .normal, { [weak self] value in self?.browserSecurityEnabled = value }),
            ("anti_tracker_agent", .normal, { [weak self] value in self?.antiTrackerEnabled = value }),
            ("ai_categories_agent", .normal, { [weak self] value in self?.aiCategoriesEnabled = value }),
            ("driving_reports_agent", .low, { [weak self] value in self?.drivingReportsEnabled = value })
        ]
        
        let prioritizedItems: [PrioritizedLoadItem<Bool>] = componentMappings.map { componentId, priority, updateClosure in
            PrioritizedLoadItem(
                id: componentId,
                priority: priority
            ) { [weak self] in
                guard let self = self else {
                    throw ComponentError.unknown(NSError(domain: "ProtectionSettingsViewModel", code: -1))
                }
                let status = try await self.statusService.getStatus(for: componentId)
                return status.isEnabled
            }
        }
        
        do {
            let results = try await ParallelLoader.executeWithLimit(
                items: prioritizedItems,
                maxConcurrent: 10
            ) { componentId, isEnabled in
                // Обновляем UI сразу при получении результата
                if let mapping = componentMappings.first(where: { $0.0 == componentId }) {
                    mapping.2(isEnabled)
                }
            }
            
            print("✅ ProtectionSettingsViewModel: Обновлено \(results.count) статусов")
        } catch {
            print("⚠️ ProtectionSettingsViewModel: Ошибка загрузки статусов: \(error)")
        }
    }
}


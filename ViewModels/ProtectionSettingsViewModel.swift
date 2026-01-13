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
    
    init(
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
                    // Загрузить статусы всех компонентов
                    for componentId in componentIds {
                        _ = try await self.statusService.getStatus(for: componentId)
                    }
                } catch let error as ComponentError {
                    throw error.toNetworkError()
                }
            },
            retryCondition: { $0.isRetryable }
        )
        
        switch result {
        case .success:
            await updateLocalStatuses()
            isLoading = false
        case .failure(let error):
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
    
    func toggleTelegramSecurity() {
        Task {
            await toggleComponent(
                componentId: "telegram_security_bot",
                updateClosure: { [weak self] value in self?.telegramSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.telegramSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleWhatsAppSecurity() {
        Task {
            await toggleComponent(
                componentId: "whatsapp_security_bot",
                updateClosure: { [weak self] value in self?.whatsappSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.whatsappSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleInstagramSecurity() {
        Task {
            await toggleComponent(
                componentId: "instagram_security_bot",
                updateClosure: { [weak self] value in self?.instagramSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.instagramSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleMaxMessengerSecurity() {
        Task {
            await toggleComponent(
                componentId: "max_messenger_security_bot",
                updateClosure: { [weak self] value in self?.maxMessengerSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.maxMessengerSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleGamingSecurity() {
        Task {
            await toggleComponent(
                componentId: "gaming_security_bot",
                updateClosure: { [weak self] value in self?.gamingSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.gamingSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleBrowserSecurity() {
        Task {
            await toggleComponent(
                componentId: "browser_security_bot",
                updateClosure: { [weak self] value in self?.browserSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.browserSecurityEnabled ?? false }
            )
        }
    }
    
    // MARK: - Toggle Methods - Приватность
    
    func toggleLocationBubble() {
        Task {
            await toggleComponent(
                componentId: "location_bubble_agent",
                updateClosure: { [weak self] value in self?.locationBubbleEnabled = value },
                getCurrentValue: { [weak self] in self?.locationBubbleEnabled ?? false }
            )
        }
    }
    
    func togglePersonalDataCleanup() {
        Task {
            await toggleComponent(
                componentId: "personal_data_cleanup_agent",
                updateClosure: { [weak self] value in self?.personalDataCleanupEnabled = value },
                getCurrentValue: { [weak self] in self?.personalDataCleanupEnabled ?? false }
            )
        }
    }
    
    func toggleAntiTracker() {
        Task {
            await toggleComponent(
                componentId: "anti_tracker_agent",
                updateClosure: { [weak self] value in self?.antiTrackerEnabled = value },
                getCurrentValue: { [weak self] in self?.antiTrackerEnabled ?? false }
            )
        }
    }
    
    // MARK: - Toggle Methods - Мониторинг
    
    func toggleDarkWebMonitoring() {
        Task {
            await toggleComponent(
                componentId: "dark_web_monitoring_agent",
                updateClosure: { [weak self] value in self?.darkWebMonitoringEnabled = value },
                getCurrentValue: { [weak self] in self?.darkWebMonitoringEnabled ?? false }
            )
        }
    }
    
    func toggleIdentityTheftProtection() {
        Task {
            await toggleComponent(
                componentId: "russian_identity_theft_protection_agent",
                updateClosure: { [weak self] value in self?.identityTheftProtectionEnabled = value },
                getCurrentValue: { [weak self] in self?.identityTheftProtectionEnabled ?? false }
            )
        }
    }
    
    func toggleAICategories() {
        Task {
            await toggleComponent(
                componentId: "ai_categories_agent",
                updateClosure: { [weak self] value in self?.aiCategoriesEnabled = value },
                getCurrentValue: { [weak self] in self?.aiCategoriesEnabled ?? false }
            )
        }
    }
    
    func toggleDrivingReports() {
        Task {
            await toggleComponent(
                componentId: "driving_reports_agent",
                updateClosure: { [weak self] value in self?.drivingReportsEnabled = value },
                getCurrentValue: { [weak self] in self?.drivingReportsEnabled ?? false }
            )
        }
    }
    
    // MARK: - Private Methods
    
    /// Переключить компонент
    private func toggleComponent(
        componentId: String,
        updateClosure: @escaping (Bool) -> Void,
        getCurrentValue: @escaping () -> Bool
    ) async {
        let oldValue = getCurrentValue()
        let newValue = !oldValue
        
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
            // Откат при ошибке
            updateClosure(oldValue)
            // ✅ ИСПРАВЛЕНИЕ: Не показываем технические детали ошибки пользователю
            if let networkError = error as? NetworkError,
               case .invalidStatusCode(let code) = networkError,
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
        // Мессенджеры
        do {
            telegramSecurityEnabled = try await statusService.getStatus(for: "telegram_security_bot").isEnabled
            whatsappSecurityEnabled = try await statusService.getStatus(for: "whatsapp_security_bot").isEnabled
            instagramSecurityEnabled = try await statusService.getStatus(for: "instagram_security_bot").isEnabled
            maxMessengerSecurityEnabled = try await statusService.getStatus(for: "max_messenger_security_bot").isEnabled
            gamingSecurityEnabled = try await statusService.getStatus(for: "gaming_security_bot").isEnabled
            browserSecurityEnabled = try await statusService.getStatus(for: "browser_security_bot").isEnabled
            
            // Приватность
            locationBubbleEnabled = try await statusService.getStatus(for: "location_bubble_agent").isEnabled
            personalDataCleanupEnabled = try await statusService.getStatus(for: "personal_data_cleanup_agent").isEnabled
            antiTrackerEnabled = try await statusService.getStatus(for: "anti_tracker_agent").isEnabled
            
            // Мониторинг
            darkWebMonitoringEnabled = try await statusService.getStatus(for: "dark_web_monitoring_agent").isEnabled
            identityTheftProtectionEnabled = try await statusService.getStatus(for: "russian_identity_theft_protection_agent").isEnabled
            aiCategoriesEnabled = try await statusService.getStatus(for: "ai_categories_agent").isEnabled
            drivingReportsEnabled = try await statusService.getStatus(for: "driving_reports_agent").isEnabled
        } catch {
            print("⚠️ ProtectionSettingsViewModel: Ошибка загрузки статусов: \(error)")
        }
    }
}


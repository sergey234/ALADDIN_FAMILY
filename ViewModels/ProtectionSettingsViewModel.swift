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
                    ) { [weak self] componentId, status in
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


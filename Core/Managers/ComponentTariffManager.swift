import Foundation
import Combine

/**
 * 🎯 Component Tariff Manager
 * Управление доступом к 42 компонентам по тарифам
 * FAMILY: 21 компонент, PREMIUM: все 42 компонента
 * User preferences: возможность отключения компонентов пользователем
 */

@MainActor
class ComponentTariffManager: ObservableObject {
    static let shared = ComponentTariffManager()

    // MARK: - Dependencies
    private let componentStatusService: ComponentStatusService
    private let userDefaults: UserDefaults

    // MARK: - Published Properties
    @Published var userDisabledComponents: Set<String> = []

    // MARK: - Private Properties
    private let userDisabledComponentsKey = "user_disabled_components"
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Initialization
    init(
        componentStatusService: ComponentStatusService = ComponentStatusService.shared,
        userDefaults: UserDefaults = .standard
    ) {
        self.componentStatusService = componentStatusService
        self.userDefaults = userDefaults

        // Загружаем пользовательские настройки отключения
        loadUserDisabledComponents()
    }

    // MARK: - Public Methods

    /// Активировать компоненты для тарифа (с учетом user preferences)
    func enableComponentsForTariff(_ tariffType: TariffType) async throws {
        let componentsToActivate = getAvailableComponents(for: tariffType)

        print("🎯 ComponentTariffManager: Активация \(componentsToActivate.count) компонентов для \(tariffType.rawValue)")

        // Активируем каждый компонент (если пользователь не отключил его)
        for componentId in componentsToActivate {
            try await enableComponentIfAllowed(componentId)
        }

        print("✅ ComponentTariffManager: Активировано \(componentsToActivate.count) компонентов")
    }

    /// Проверить, доступен ли компонент для тарифа
    func isComponentAvailable(_ componentId: String, for tariffType: TariffType) -> Bool {
        let availableComponents = getAvailableComponents(for: tariffType)
        return availableComponents.contains(componentId)
    }

    /// Проверить, может ли пользователь использовать компонент
    func canUseComponent(_ componentId: String, for tariffType: TariffType) -> Bool {
        // Уровень 1: Тариф дает доступ?
        let hasTariffAccess = isComponentAvailable(componentId, for: tariffType)

        // Уровень 2: Пользователь не отключил?
        let isUserEnabled = !userDisabledComponents.contains(componentId)

        return hasTariffAccess && isUserEnabled
    }

    /// Пользователь отключил компонент
    func disableComponentByUser(_ componentId: String) async throws {
        // Добавляем в список отключенных пользователем
        userDisabledComponents.insert(componentId)
        saveUserDisabledComponents()

        // Отключаем компонент
        try await componentStatusService.updateStatus(
            componentId: componentId,
            isEnabled: false
        )

        print("🚫 ComponentTariffManager: Компонент \(componentId) отключен пользователем")
    }

    /// Пользователь включил компонент
    func enableComponentByUser(_ componentId: String) async throws {
        // Убираем из списка отключенных
        userDisabledComponents.remove(componentId)
        saveUserDisabledComponents()

        // Включаем компонент
        try await componentStatusService.updateStatus(
            componentId: componentId,
            isEnabled: true
        )

        print("✅ ComponentTariffManager: Компонент \(componentId) включен пользователем")
    }

    /// Получить все доступные компоненты для тарифа
    func getAvailableComponents(for tariffType: TariffType) -> [String] {
        switch tariffType {
        case .trial, .free, .personal:
            // TRIAL, FREE и PERSONAL не получают компонентов
            return []

        case .family:
            // FAMILY получает 21 компонент
            return getFamilyComponents()

        case .premium:
            // PREMIUM получает ВСЕ компоненты (42)
            return getFamilyComponents() + getPremiumOnlyComponents()
        }
    }

    // MARK: - Private Methods

    /// Активировать компонент, если пользователь не отключил его
    private func enableComponentIfAllowed(_ componentId: String) async throws {
        // Проверяем, не отключил ли пользователь этот компонент
        guard !userDisabledComponents.contains(componentId) else {
            print("⚠️ ComponentTariffManager: Компонент \(componentId) пропущен (отключен пользователем)")
            return
        }

        // Проверяем, не активирован ли уже
        let currentStatus = componentStatusService.getComponentEnabledStatus(componentId: componentId)
        guard !currentStatus else {
            print("⚠️ ComponentTariffManager: Компонент \(componentId) уже активирован")
            return
        }

        // Активируем компонент
        try await componentStatusService.updateStatus(
            componentId: componentId,
            isEnabled: true
        )

        print("✅ ComponentTariffManager: Компонент \(componentId) активирован")
    }

    /// Получить компоненты FAMILY тарифа
    private func getFamilyComponents() -> [String] {
        return [
            // Сетевая защита (4)
            "phishing_protection_agent",
            "malware_detection_agent",
            "mobile_security_agent",
            "network_security_agent",

            // Родительский контроль (5)
            "self_harm_detection_agent",
            "grooming_detection_agent",
            "online_predators_agent",
            "psychological_support_agent",
            "parental_control_bot",

            // Мессенджеры (6)
            "telegram_security_bot",
            "whatsapp_security_bot",
            "instagram_security_bot",
            "max_messenger_security_bot",
            "gaming_security_bot",
            "browser_security_bot",

            // Приватность (1)
            "location_bubble_agent",

            // Регуляторные (2)
            "russian_child_protection_compliance_manager",
            "russian_data_protection_compliance_manager",

            // Интерфейсы (3)
            "family_notification_manager",
            "child_interface_manager",
            "elderly_interface_manager"
        ]
    }

    /// Получить компоненты только для PREMIUM
    private func getPremiumOnlyComponents() -> [String] {
        return [
            // Экстренная помощь (6)
            "crash_detection_agent",
            "roadside_assistance_agent",
            "emergency_response_bot",
            "emergency_event_manager",
            "incident_response_agent",
            "password_security_agent",

            // Расширенная приватность (3)
            "personal_data_cleanup_agent",
            "anti_tracker_agent",
            "dark_web_monitoring_agent",

            // Мониторинг (4)
            "russian_identity_theft_protection_agent",
            "ai_categories_agent",
            "driving_reports_agent",

            // Менеджеры (8)
            "emergency_contacts_manager",
            "emergency_notifications_manager",
            "voice_control_manager",
            "smart_notification_manager"
        ]
    }

    /// Загрузить список отключенных пользователем компонентов
    private func loadUserDisabledComponents() {
        if let savedComponents = userDefaults.array(forKey: userDisabledComponentsKey) as? [String] {
            userDisabledComponents = Set(savedComponents)
        }
    }

    /// Сохранить список отключенных пользователем компонентов
    private func saveUserDisabledComponents() {
        userDefaults.set(Array(userDisabledComponents), forKey: userDisabledComponentsKey)
    }
}
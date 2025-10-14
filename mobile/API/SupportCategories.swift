import Foundation

// MARK: - Support Categories Enum для iOS
public enum SupportCategory: String, CaseIterable, Codable {
    // Основные категории
    case general = "general"
    case security = "security"
    case family = "family"
    case settings = "settings"
    case help = "help"
    
    // Технические категории
    case technical = "technical"
    case installation = "installation"
    case configuration = "configuration"
    case troubleshooting = "troubleshooting"
    case performance = "performance"
    
    // Безопасность
    case parentalControl = "parental_control"
    case childProtection = "child_protection"
    case elderlyProtection = "elderly_protection"
    case deviceSecurity = "device_security"
    case networkSecurity = "network_security"
    case dataProtection = "data_protection"
    
    // VPN и сеть
    case vpn = "vpn"
    case network = "network"
    case connectivity = "connectivity"
    case firewall = "firewall"
    
    // Платежи и подписки
    case payments = "payments"
    case subscription = "subscription"
    case billing = "billing"
    case refunds = "refunds"
    
    // Кризисные ситуации
    case crisis = "crisis"
    case emergency = "emergency"
    case psychological = "psychological"
    case childSafety = "child_safety"
    case cyberbullying = "cyberbullying"
    
    // Дополнительные
    case feedback = "feedback"
    case suggestions = "suggestions"
    case complaints = "complaints"
    case other = "other"
    
    // MARK: - Computed Properties
    public var displayName: String {
        switch self {
        case .general:
            return "Общие вопросы"
        case .security:
            return "Безопасность"
        case .family:
            return "Семья"
        case .settings:
            return "Настройки"
        case .help:
            return "Помощь"
        case .technical:
            return "Техническая поддержка"
        case .installation:
            return "Установка"
        case .configuration:
            return "Конфигурация"
        case .troubleshooting:
            return "Устранение неполадок"
        case .performance:
            return "Производительность"
        case .parentalControl:
            return "Родительский контроль"
        case .childProtection:
            return "Защита детей"
        case .elderlyProtection:
            return "Защита пожилых"
        case .deviceSecurity:
            return "Безопасность устройства"
        case .networkSecurity:
            return "Сетевая безопасность"
        case .dataProtection:
            return "Защита данных"
        case .vpn:
            return "VPN"
        case .network:
            return "Сеть"
        case .connectivity:
            return "Подключение"
        case .firewall:
            return "Файрвол"
        case .payments:
            return "Платежи"
        case .subscription:
            return "Подписка"
        case .billing:
            return "Биллинг"
        case .refunds:
            return "Возвраты"
        case .crisis:
            return "Кризисная ситуация"
        case .emergency:
            return "Экстренная помощь"
        case .psychological:
            return "Психологическая поддержка"
        case .childSafety:
            return "Безопасность детей"
        case .cyberbullying:
            return "Кибербуллинг"
        case .feedback:
            return "Обратная связь"
        case .suggestions:
            return "Предложения"
        case .complaints:
            return "Жалобы"
        case .other:
            return "Другое"
        }
    }
    
    public var description: String {
        switch self {
        case .general:
            return "Общие вопросы и информация"
        case .security:
            return "Вопросы безопасности и защиты"
        case .family:
            return "Семейные настройки и профили"
        case .settings:
            return "Настройки приложения"
        case .help:
            return "Справка и инструкции"
        case .technical:
            return "Технические проблемы и решения"
        case .installation:
            return "Установка и обновления"
        case .configuration:
            return "Настройка параметров"
        case .troubleshooting:
            return "Диагностика и исправление ошибок"
        case .performance:
            return "Оптимизация производительности"
        case .parentalControl:
            return "Настройка родительского контроля"
        case .childProtection:
            return "Защита детей в интернете"
        case .elderlyProtection:
            return "Защита пожилых пользователей"
        case .deviceSecurity:
            return "Безопасность мобильного устройства"
        case .networkSecurity:
            return "Защита сетевого соединения"
        case .dataProtection:
            return "Защита персональных данных"
        case .vpn:
            return "Настройка и использование VPN"
        case .network:
            return "Сетевые подключения"
        case .connectivity:
            return "Проблемы с подключением"
        case .firewall:
            return "Настройка файрвола"
        case .payments:
            return "Платежи и транзакции"
        case .subscription:
            return "Управление подпиской"
        case .billing:
            return "Счета и оплата"
        case .refunds:
            return "Возврат средств"
        case .crisis:
            return "Кризисные ситуации и экстренная помощь"
        case .emergency:
            return "Экстренная поддержка"
        case .psychological:
            return "Психологическая помощь"
        case .childSafety:
            return "Экстренная помощь по безопасности детей"
        case .cyberbullying:
            return "Помощь при кибербуллинге"
        case .feedback:
            return "Отзывы и предложения"
        case .suggestions:
            return "Предложения по улучшению"
        case .complaints:
            return "Жалобы и проблемы"
        case .other:
            return "Другие вопросы"
        }
    }
    
    public var priority: SupportPriority {
        switch self {
        case .crisis, .emergency, .childSafety, .cyberbullying:
            return .critical
        case .psychological, .technical, .troubleshooting:
            return .high
        case .security, .parentalControl, .childProtection, .elderlyProtection:
            return .high
        case .vpn, .network, .connectivity, .deviceSecurity:
            return .medium
        case .payments, .subscription, .billing:
            return .medium
        case .settings, .configuration, .performance:
            return .medium
        case .general, .help, .feedback, .suggestions:
            return .low
        case .other, .complaints:
            return .low
        }
    }
    
    public var icon: String {
        switch self {
        case .general:
            return "questionmark.circle"
        case .security:
            return "shield.checkered"
        case .family:
            return "person.3"
        case .settings:
            return "gear"
        case .help:
            return "questionmark.circle.fill"
        case .technical:
            return "wrench.and.screwdriver"
        case .installation:
            return "arrow.down.circle"
        case .configuration:
            return "slider.horizontal.3"
        case .troubleshooting:
            return "stethoscope"
        case .performance:
            return "speedometer"
        case .parentalControl:
            return "person.crop.circle.badge.checkmark"
        case .childProtection:
            return "figure.child"
        case .elderlyProtection:
            return "figure.walk"
        case .deviceSecurity:
            return "iphone"
        case .networkSecurity:
            return "network"
        case .dataProtection:
            return "lock.shield"
        case .vpn:
            return "network"
        case .network:
            return "wifi"
        case .connectivity:
            return "antenna.radiowaves.left.and.right"
        case .firewall:
            return "shield.lefthalf.filled"
        case .payments:
            return "creditcard"
        case .subscription:
            return "repeat"
        case .billing:
            return "doc.text"
        case .refunds:
            return "arrow.uturn.backward"
        case .crisis:
            return "exclamationmark.triangle.fill"
        case .emergency:
            return "phone.fill"
        case .psychological:
            return "heart.fill"
        case .childSafety:
            return "figure.child.circle.fill"
        case .cyberbullying:
            return "person.crop.circle.badge.exclamationmark"
        case .feedback:
            return "bubble.left.and.bubble.right"
        case .suggestions:
            return "lightbulb"
        case .complaints:
            return "exclamationmark.bubble"
        case .other:
            return "ellipsis.circle"
        }
    }
    
    public var color: String {
        switch self {
        case .crisis, .emergency, .childSafety, .cyberbullying:
            return "error"
        case .psychological, .technical, .troubleshooting:
            return "warning"
        case .security, .parentalControl, .childProtection, .elderlyProtection:
            return "accent"
        case .vpn, .network, .connectivity, .deviceSecurity:
            return "primary"
        case .payments, .subscription, .billing:
            return "secondary"
        case .settings, .configuration, .performance:
            return "info"
        case .general, .help, .feedback, .suggestions:
            return "success"
        case .other, .complaints:
            return "text"
        }
    }
}

// MARK: - Support Priority Enum
public enum SupportPriority: String, CaseIterable, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
    
    public var displayName: String {
        switch self {
        case .low:
            return "Низкий"
        case .medium:
            return "Средний"
        case .high:
            return "Высокий"
        case .critical:
            return "Критический"
        }
    }
    
    public var description: String {
        switch self {
        case .low:
            return "Обычный вопрос, не требует срочного решения"
        case .medium:
            return "Важный вопрос, требует внимания"
        case .high:
            return "Срочный вопрос, требует быстрого решения"
        case .critical:
            return "Критическая ситуация, требует немедленного решения"
        }
    }
    
    public var responseTime: TimeInterval {
        switch self {
        case .low:
            return 24 * 60 * 60 // 24 часа
        case .medium:
            return 4 * 60 * 60 // 4 часа
        case .high:
            return 1 * 60 * 60 // 1 час
        case .critical:
            return 15 * 60 // 15 минут
        }
    }
    
    public var color: String {
        switch self {
        case .low:
            return "success"
        case .medium:
            return "info"
        case .high:
            return "warning"
        case .critical:
            return "error"
        }
    }
}

// MARK: - Crisis Type Enum
public enum CrisisType: String, CaseIterable, Codable {
    case childSafety = "child_safety"
    case cyberbullying = "cyberbullying"
    case psychological = "psychological"
    case emergency = "emergency"
    case security = "security"
    case other = "other"
    
    public var displayName: String {
        switch self {
        case .childSafety:
            return "Безопасность детей"
        case .cyberbullying:
            return "Кибербуллинг"
        case .psychological:
            return "Психологическая помощь"
        case .emergency:
            return "Экстренная ситуация"
        case .security:
            return "Безопасность"
        case .other:
            return "Другое"
        }
    }
    
    public var description: String {
        switch self {
        case .childSafety:
            return "Критическая ситуация с безопасностью ребенка"
        case .cyberbullying:
            return "Случай кибербуллинга или травли"
        case .psychological:
            return "Психологическая кризисная ситуация"
        case .emergency:
            return "Экстренная ситуация, требующая немедленного вмешательства"
        case .security:
            return "Критическая угроза безопасности"
        case .other:
            return "Другая кризисная ситуация"
        }
    }
    
    public var urgencyLevel: Int {
        switch self {
        case .childSafety, .emergency:
            return 1
        case .cyberbullying, .security:
            return 2
        case .psychological:
            return 3
        case .other:
            return 4
        }
    }
}


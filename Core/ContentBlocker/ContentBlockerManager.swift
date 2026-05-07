import Foundation
import SafariServices

/**
 * 🔒 Content Blocker Manager
 * Управление блокировкой контента в Safari через Content Blocker Extension
 * Использует SFContentBlockerManager для активации/деактивации
 */

@MainActor
class ContentBlockerManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = ContentBlockerManager()
    
    // MARK: - Published Properties
    
    @Published var isEnabled: Bool = false
    @Published var status: ContentBlockerStatus = .disabled
    @Published var blockedSitesCount: Int = 0
    @Published var activeCategories: [ContentBlockerCategory] = []
    
    // MARK: - Constants
    
    private let extensionIdentifier = "family.aladdin.ios.ContentBlocker"
    private let appGroupIdentifier = "group.com.aladdin.family"
    private let rulesKey = "contentBlockerRules"
    
    // MARK: - Private Properties
    
    private var userDefaults: UserDefaults? {
        UserDefaults(suiteName: appGroupIdentifier)
    }
    
    // MARK: - Initialization
    
    private init() {
        loadStatus()
    }
    
    // MARK: - Status Management
    
    /**
     * Загрузить статус блокировки
     */
    private func loadStatus() {
        Task {
            await checkBlockingStatus()
        }
    }
    
    /**
     * Проверить статус блокировки
     */
    func checkBlockingStatus() async {
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            SFContentBlockerManager.getStateOfContentBlocker(withIdentifier: extensionIdentifier) { state, error in
                Task { @MainActor in
                    if let error = error {
                        if self.isExtensionMissingError(error) {
                            self.status = .extensionMissing
                            self.isEnabled = false
                        } else {
                            self.status = .error(error.localizedDescription)
                            self.isEnabled = false
                        }
                    } else if let state = state {
                        if state.isEnabled {
                            self.status = .enabled
                            self.isEnabled = true
                        } else {
                            self.status = .needsActivation
                            self.isEnabled = false
                        }
                        
                        // Загрузить количество заблокированных сайтов
                        self.blockedSitesCount = self.getBlockedSitesCount()
                    } else {
                        self.status = .disabled
                        self.isEnabled = false
                    }
                    continuation.resume()
                }
            }
        }
    }
    
    // MARK: - Rules Management
    
    /**
     * Включить блокировку контента
     */
    func enableContentBlocker(categories: [ContentBlockerCategory]) async throws {
        // Создать правила из категорий
        let rules = createRules(from: categories)
        
        // Сохранить правила в App Group
        saveRules(rules)
        
        // Сохранить активные категории
        await MainActor.run {
            self.activeCategories = categories
            UserDefaults.standard.set(categories.map { $0.rawValue }, forKey: "contentBlockerActiveCategories")
        }
        
        // Проверить статус
        await checkBlockingStatus()
        
        // Если блокировка не активирована, показать инструкцию
        if case .needsActivation = status {
            throw ContentBlockerError.needsActivation
        }
        if case .extensionMissing = status {
            throw ContentBlockerError.extensionMissing
        }
    }
    
    /**
     * Выключить блокировку контента
     */
    func disableContentBlocker() async {
        // Очистить правила
        clearRules()
        
        // Очистить активные категории
        await MainActor.run {
            self.activeCategories = []
            UserDefaults.standard.removeObject(forKey: "contentBlockerActiveCategories")
        }
        
        // Обновить статус
        await checkBlockingStatus()
    }
    
    /**
     * Обновить правила блокировки
     */
    func updateRules(categories: [ContentBlockerCategory]) async throws {
        try await enableContentBlocker(categories: categories)
    }
    
    /**
     * Создать правила из категорий
     */
    private func createRules(from categories: [ContentBlockerCategory]) -> [ContentBlockerRule] {
        var rules: [ContentBlockerRule] = []
        
        for category in categories {
            let domains = category.blockedDomains
            
            for domain in domains {
                let trigger = Trigger(
                    urlFilter: domain,
                    ifDomain: nil,
                    unlessDomain: nil,
                    resourceType: nil,
                    loadType: nil,
                    ifTopUrl: nil
                )
                
                let action = Action(type: "block", selector: nil)
                
                let rule = ContentBlockerRule(trigger: trigger, action: action)
                rules.append(rule)
            }
        }
        
        return rules
    }
    
    /**
     * Сохранить правила в App Group
     */
    private func saveRules(_ rules: [ContentBlockerRule]) {
        guard let userDefaults = userDefaults else {
            print("❌ ContentBlockerManager: Не удалось получить UserDefaults для App Group")
            return
        }
        
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(rules)
            userDefaults.set(data, forKey: rulesKey)
            userDefaults.synchronize()
            
            print("✅ ContentBlockerManager: Правила сохранены (\(rules.count) правил)")
        } catch {
            print("❌ ContentBlockerManager: Ошибка сохранения правил: \(error)")
        }
    }
    
    /**
     * Очистить правила
     */
    private func clearRules() {
        guard let userDefaults = userDefaults else {
            return
        }
        
        userDefaults.removeObject(forKey: rulesKey)
        userDefaults.synchronize()
        
        print("✅ ContentBlockerManager: Правила очищены")
    }
    
    /**
     * Загрузить правила из App Group
     */
    func loadRules() -> [ContentBlockerRule] {
        guard let userDefaults = userDefaults,
              let data = userDefaults.data(forKey: rulesKey) else {
            return []
        }
        
        do {
            let decoder = JSONDecoder()
            let rules = try decoder.decode([ContentBlockerRule].self, from: data)
            return rules
        } catch {
            print("❌ ContentBlockerManager: Ошибка загрузки правил: \(error)")
            return []
        }
    }
    
    /**
     * Получить количество заблокированных сайтов
     */
    private func getBlockedSitesCount() -> Int {
        let rules = loadRules()
        return rules.count
    }
    
    /**
     * Открыть настройки iOS для активации блокировки
     * ⚠️ ВАЖНО: iOS не поддерживает прямой deep link к Safari → Content Blockers
     * 
     * Решение:
     * 1. Открываем общие настройки приложения (UIApplication.openSettingsURLString)
     * 2. Пользователь должен вручную перейти: Настройки → Safari → Content Blockers → ALADDIN
     * 
     * Альтернатива (не работает в продакшн):
     * - App-Prefs:root=Safari&path=Content_Blockers (требует приватный API, отклоняется App Store)
     */
    func openSettings() {
        // Открываем настройки приложения
        // Пользователь увидит инструкцию в alert и сможет перейти в Safari → Content Blockers
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url, options: [:], completionHandler: nil)
        }
    }

    private func isExtensionMissingError(_ error: Error) -> Bool {
        let nsError = error as NSError
        if nsError.domain == "SFErrorDomain" && nsError.code == 1 {
            return true
        }
        let text = nsError.localizedDescription.lowercased()
        return text.contains("no extension found") || text.contains("extension") && text.contains("not found")
    }
    
    /**
     * Загрузить активные категории
     */
    func loadActiveCategories() {
        if let categoriesData = UserDefaults.standard.array(forKey: "contentBlockerActiveCategories") as? [String] {
            activeCategories = categoriesData.compactMap { ContentBlockerCategory(rawValue: $0) }
        }
    }
}

// MARK: - Content Blocker Error

enum ContentBlockerError: LocalizedError {
    case needsActivation
    case extensionMissing
    case rulesCreationFailed
    case saveFailed
    
    var errorDescription: String? {
        switch self {
        case .needsActivation:
            return "Необходимо включить блокировку контента в Настройках iOS → Safari → Content Blockers"
        case .extensionMissing:
            return "Расширение Safari Content Blocker отсутствует в текущей сборке приложения"
        case .rulesCreationFailed:
            return "Не удалось создать правила блокировки"
        case .saveFailed:
            return "Не удалось сохранить правила блокировки"
        }
    }
}


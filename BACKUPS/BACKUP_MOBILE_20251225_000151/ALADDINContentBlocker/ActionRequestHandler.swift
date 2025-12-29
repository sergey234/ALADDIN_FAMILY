import Foundation
import SafariServices

/**
 * 🔒 Action Request Handler
 * Content Blocker Extension для Safari
 * Загружает правила блокировки из App Group и возвращает их Safari
 */

class ActionRequestHandler: NSObject, NSExtensionRequestHandling {
    
    // MARK: - Constants
    
    private let appGroupIdentifier = "group.com.aladdin.family"
    private let rulesKey = "contentBlockerRules"
    
    // MARK: - Extension Request Handling
    
    func beginRequest(with context: NSExtensionContext) {
        // Загрузить правила из App Group
        let rules = loadRules()
        
        // Преобразовать в JSON и сохранить во временный файл
        guard let jsonURL = createJSONFile(from: rules) else {
            context.completeRequest(returningItems: nil, completionHandler: nil)
            return
        }
        
        // Создать attachment для Safari с URL файла
        let attachment = NSItemProvider(contentsOf: jsonURL)
        let item = NSExtensionItem()
        item.attachments = [attachment].compactMap { $0 }
        
        // Вернуть правила Safari
        context.completeRequest(returningItems: [item], completionHandler: nil)
    }
    
    // MARK: - Rules Loading
    
    /**
     * Загрузить правила из App Group
     */
    private func loadRules() -> [ContentBlockerRule] {
        guard let userDefaults = UserDefaults(suiteName: appGroupIdentifier),
              let data = userDefaults.data(forKey: rulesKey) else {
            print("⚠️ ActionRequestHandler: Правила не найдены в App Group")
            return getDefaultRules()
        }
        
        do {
            let decoder = JSONDecoder()
            let rules = try decoder.decode([ContentBlockerRule].self, from: data)
            print("✅ ActionRequestHandler: Загружено \(rules.count) правил")
            return rules
        } catch {
            print("❌ ActionRequestHandler: Ошибка загрузки правил: \(error)")
            return getDefaultRules()
        }
    }
    
    /**
     * Получить правила по умолчанию (если нет сохраненных)
     */
    private func getDefaultRules() -> [ContentBlockerRule] {
        // Базовые правила для блокировки опасного контента
        return [
            ContentBlockerRule(
                trigger: Trigger(
                    urlFilter: ".*porn.*",
                    ifDomain: nil,
                    unlessDomain: nil,
                    resourceType: nil,
                    loadType: nil,
                    ifTopUrl: nil
                ),
                action: Action(type: "block", selector: nil)
            ),
            ContentBlockerRule(
                trigger: Trigger(
                    urlFilter: ".*xxx.*",
                    ifDomain: nil,
                    unlessDomain: nil,
                    resourceType: nil,
                    loadType: nil,
                    ifTopUrl: nil
                ),
                action: Action(type: "block", selector: nil)
            )
        ]
    }
    
    // MARK: - JSON Creation
    
    /**
     * Создать JSON файл из правил
     */
    private func createJSONFile(from rules: [ContentBlockerRule]) -> URL? {
        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = .prettyPrinted
            let jsonData = try encoder.encode(rules)
            
            // Сохранить во временный файл
            let tempURL = FileManager.default.temporaryDirectory
                .appendingPathComponent("blockerList.json")
            
            try jsonData.write(to: tempURL)
            
            print("✅ ActionRequestHandler: JSON файл создан: \(tempURL.path)")
            return tempURL
        } catch {
            print("❌ ActionRequestHandler: Ошибка создания JSON файла: \(error)")
            return nil
        }
    }
}

// MARK: - Content Blocker Rule (для Extension)

struct ContentBlockerRule: Codable {
    let trigger: Trigger
    let action: Action
}

struct Trigger: Codable {
    let urlFilter: String
    let ifDomain: [String]?
    let unlessDomain: [String]?
    let resourceType: [String]?
    let loadType: [String]?
    let ifTopUrl: [String]?
    
    enum CodingKeys: String, CodingKey {
        case urlFilter = "url-filter"
        case ifDomain = "if-domain"
        case unlessDomain = "unless-domain"
        case resourceType = "resource-type"
        case loadType = "load-type"
        case ifTopUrl = "if-top-url"
    }
}

struct Action: Codable {
    let type: String
    let selector: String?
}


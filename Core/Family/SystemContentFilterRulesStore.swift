import Foundation
import NetworkExtension

/// WAVE3 F2 — parental domain rules in App Group for NE Content Filter (not VPN).
enum SystemContentFilterRulesStore {
    static let appGroupId = "group.ai.aladdin"
    static let rulesFileName = "content_filter_rules.json"

    struct RulesPayload: Codable {
        var blockedHosts: [String]
        var updatedAt: TimeInterval
    }

    static func saveBlockedHosts(_ hosts: [String]) {
        guard AppStoreBuildPolicy.allowsSystemContentFilter else { return }
        let cleaned = hosts
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
            .filter { !$0.isEmpty }
        let payload = RulesPayload(blockedHosts: Array(Set(cleaned)).sorted(), updatedAt: Date().timeIntervalSince1970)
        guard let data = try? JSONEncoder().encode(payload) else { return }
        guard let url = containerURL()?.appendingPathComponent(rulesFileName) else { return }
        try? data.write(to: url, options: .atomic)
        reloadFilterConfiguration()
    }

    static func loadBlockedHosts() -> [String] {
        guard let url = containerURL()?.appendingPathComponent(rulesFileName),
              let data = try? Data(contentsOf: url),
              let payload = try? JSONDecoder().decode(RulesPayload.self, from: data) else {
            return []
        }
        return payload.blockedHosts
    }

    private static func containerURL() -> URL? {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupId)
    }

    /// Ask the system to reload the content filter provider configuration.
    static func reloadFilterConfiguration() {
        guard AppStoreBuildPolicy.allowsSystemContentFilter else { return }
        NEFilterManager.shared().loadFromPreferences { error in
            if let error {
                print("⚠️ SystemContentFilterRulesStore load: \(error.localizedDescription)")
            }
            let manager = NEFilterManager.shared()
            if manager.providerConfiguration == nil {
                let config = NEFilterProviderConfiguration()
                config.filterBrowsers = true
                config.filterSockets = true
                config.username = "ALADDIN Family"
                config.organization = "ALADDIN"
                manager.providerConfiguration = config
            }
            manager.isEnabled = true
            manager.saveToPreferences { saveError in
                if let saveError {
                    print("⚠️ SystemContentFilterRulesStore save: \(saveError.localizedDescription)")
                } else {
                    print("✅ SystemContentFilterRulesStore: filter prefs saved")
                }
            }
        }
    }
}

import Foundation
import NetworkExtension

/// WAVE3 F2/F3 — parental domain rules in App Group for NE Content Filter.
enum SystemContentFilterRulesStore {
    static let appGroupId = "group.ai.aladdin"
    static let rulesFileName = "content_filter_rules.json"
    static let optedInDefaultsKey = "system_content_filter_opted_in"

    struct RulesPayload: Codable {
        var blockedHosts: [String]
        var updatedAt: TimeInterval
    }

    static var isOptedIn: Bool {
        get { UserDefaults.standard.bool(forKey: optedInDefaultsKey) }
        set { UserDefaults.standard.set(newValue, forKey: optedInDefaultsKey) }
    }

    static func saveBlockedHosts(_ hosts: [String]) {
        guard AppStoreBuildPolicy.allowsSystemContentFilter else { return }
        let cleaned = hosts
            .map { normalizeHostToken($0) }
            .filter { !$0.isEmpty }
        let payload = RulesPayload(blockedHosts: Array(Set(cleaned)).sorted(), updatedAt: Date().timeIntervalSince1970)
        guard let data = try? JSONEncoder().encode(payload) else { return }
        guard let url = containerURL()?.appendingPathComponent(rulesFileName) else { return }
        try? data.write(to: url, options: .atomic)
    }

    static func loadBlockedHosts() -> [String] {
        guard let url = containerURL()?.appendingPathComponent(rulesFileName),
              let data = try? Data(contentsOf: url),
              let payload = try? JSONDecoder().decode(RulesPayload.self, from: data) else {
            return []
        }
        return payload.blockedHosts
    }

    /// Sync Safari category patterns + custom parental sites into App Group rules.
    static func syncHostsFromContentCategories(_ categories: [ContentBlockerCategory]) {
        var hosts: [String] = []
        for category in categories {
            for pattern in category.blockedDomains {
                hosts.append(normalizeHostToken(pattern))
            }
        }
        if let custom = UserDefaults.standard.array(forKey: "parental_blocked_websites") as? [String] {
            hosts.append(contentsOf: custom.map { normalizeHostToken($0) })
        }
        saveBlockedHosts(hosts)
    }

    /// Human copy for the toggle — never show `IPC failed` / XPC jargon.
    static func userFacingStatus(for error: Error, localization: LocalizationManager) -> String {
        if isSimulatorOrMissingFilterHost(error) {
            return localization.localized("system_filter_toggle_error_simulator")
        }
        return String(
            format: localization.localized("system_filter_toggle_error_fmt"),
            error.localizedDescription
        )
    }

    /// Enable system filter (shows iOS permission UI when supported).
    static func setEnabled(_ enabled: Bool, categories: [ContentBlockerCategory], completion: @escaping (Result<Void, Error>) -> Void) {
        guard AppStoreBuildPolicy.allowsSystemContentFilter else {
            completion(.failure(StoreError.featureDisabled))
            return
        }
        #if targetEnvironment(simulator)
        if enabled {
            completion(.failure(StoreError.simulatorUnavailable))
            return
        }
        isOptedIn = false
        completion(.success(()))
        return
        #endif
        if enabled {
            syncHostsFromContentCategories(categories)
        }
        NEFilterManager.shared().loadFromPreferences { error in
            if let error {
                completion(.failure(error))
                return
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
            manager.isEnabled = enabled
            manager.saveToPreferences { saveError in
                if let saveError {
                    completion(.failure(saveError))
                    return
                }
                isOptedIn = enabled
                completion(.success(()))
            }
        }
    }

    private static func containerURL() -> URL? {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupId)
    }

    /// `.*facebook.*` → `facebook`; `https://evil.com/path` → `evil.com`
    private static func normalizeHostToken(_ raw: String) -> String {
        var s = raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        s = s.replacingOccurrences(of: ".*", with: "")
        if let url = URL(string: s), let host = url.host, !host.isEmpty {
            return host
        }
        if s.hasPrefix("http://") || s.hasPrefix("https://") {
            if let url = URL(string: s), let host = url.host { return host }
        }
        while s.hasPrefix(".") { s.removeFirst() }
        while s.hasSuffix(".") { s.removeLast() }
        return s
    }

    private static func isSimulatorOrMissingFilterHost(_ error: Error) -> Bool {
        if let store = error as? StoreError, store == .simulatorUnavailable { return true }
        let ns = error as NSError
        if ns.domain == "NEFilterErrorDomain" || ns.domain == "NEConfigurationErrorDomain" {
            return true
        }
        let desc = error.localizedDescription.lowercased()
        return desc.contains("ipc") || desc.contains("connection invalid")
    }

    enum StoreError: LocalizedError, Equatable {
        case featureDisabled
        case simulatorUnavailable
        var errorDescription: String? {
            switch self {
            case .featureDisabled: return "System content filter is not enabled for this build"
            case .simulatorUnavailable: return "System content filter is unavailable in Simulator"
            }
        }
    }
}

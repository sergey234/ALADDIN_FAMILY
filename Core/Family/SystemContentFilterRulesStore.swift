import Foundation
import NetworkExtension

/// WAVE3 F2/F3 — parental domain rules in App Group for NE Content Filter.
enum SystemContentFilterRulesStore {
    static let appGroupId = "group.ai.aladdin"
    static let rulesFileName = "content_filter_rules.json"
    static let optedInDefaultsKey = "system_content_filter_opted_in"
    /// Must match `ALADDINContentFilter` PRODUCT_BUNDLE_IDENTIFIER.
    static let filterDataProviderBundleId = "ai.aladdin.ContentFilter"

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
        if let store = error as? StoreError, store == .simulatorUnavailable {
            return localization.localized("system_filter_toggle_error_simulator")
        }
        if let store = error as? StoreError, store == .featureDisabled {
            return localization.localized("system_filter_toggle_error_disabled")
        }
        if isPermissionDenied(error) {
            return localization.localized("system_filter_toggle_error_permission")
        }
        if isNetworkExtensionConfigurationError(error) {
            return localization.localized("system_filter_toggle_error_extension")
        }
        return String(
            format: localization.localized("system_filter_toggle_error_fmt"),
            error.localizedDescription
        )
    }

    /// Enable system filter (shows iOS permission UI when supported).
    /// Not available in Simulator — Apple does not load NEFilter providers there.
    static func setEnabled(_ enabled: Bool, categories: [ContentBlockerCategory], completion: @escaping (Result<Void, Error>) -> Void) {
        VisualLogger.shared.log(
            "➡️ SYSTEM_FILTER setEnabled=\(enabled) allows=\(AppStoreBuildPolicy.allowsSystemContentFilter)",
            level: .info,
            category: "CONTENT_FILTER"
        )
        guard AppStoreBuildPolicy.allowsSystemContentFilter else {
            VisualLogger.shared.log("❌ SYSTEM_FILTER featureDisabled", level: .error, category: "CONTENT_FILTER")
            completion(.failure(StoreError.featureDisabled))
            return
        }
        #if targetEnvironment(simulator)
        VisualLogger.shared.log(
            "⚠️ SYSTEM_FILTER simulator — NEFilterManager not supported",
            level: .warning,
            category: "CONTENT_FILTER"
        )
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
                VisualLogger.shared.log(
                    "❌ SYSTEM_FILTER loadFromPreferences: \(Self.errorDigest(error))",
                    level: .error,
                    category: "CONTENT_FILTER"
                )
                completion(.failure(error))
                return
            }
            let manager = NEFilterManager.shared()
            let config = manager.providerConfiguration ?? NEFilterProviderConfiguration()
            config.filterBrowsers = true
            config.filterSockets = true
            config.username = "ALADDIN Family"
            config.organization = "ALADDIN"
            // Without an explicit provider bundle id, iOS often fails save / never prompts Allow.
            config.filterDataProviderBundleIdentifier = filterDataProviderBundleId
            manager.providerConfiguration = config
            manager.localizedDescription = "ALADDIN Safe Sites"
            manager.isEnabled = enabled
            manager.saveToPreferences { saveError in
                if let saveError {
                    VisualLogger.shared.log(
                        "❌ SYSTEM_FILTER saveToPreferences: \(Self.errorDigest(saveError))",
                        level: .error,
                        category: "CONTENT_FILTER"
                    )
                    completion(.failure(saveError))
                    return
                }
                VisualLogger.shared.log(
                    "✅ SYSTEM_FILTER save ok enabled=\(enabled) hosts=\(loadBlockedHosts().count)",
                    level: .success,
                    category: "CONTENT_FILTER"
                )
                isOptedIn = enabled
                completion(.success(()))
            }
        }
    }

    private static func errorDigest(_ error: Error) -> String {
        let ns = error as NSError
        return "domain=\(ns.domain) code=\(ns.code) desc=\(ns.localizedDescription)"
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

    private static func isNetworkExtensionConfigurationError(_ error: Error) -> Bool {
        let ns = error as NSError
        if ns.domain == "NEFilterErrorDomain" || ns.domain == "NEConfigurationErrorDomain" {
            return true
        }
        let desc = error.localizedDescription.lowercased()
        return desc.contains("ipc") || desc.contains("connection invalid")
    }

    private static func isPermissionDenied(_ error: Error) -> Bool {
        let ns = error as NSError
        if ns.code == 5 || ns.code == 10 || ns.code == 13 { return true }
        let desc = error.localizedDescription.lowercased()
        return desc.contains("denied")
            || desc.contains("permission")
            || desc.contains("not allowed")
            || desc.contains("user")
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

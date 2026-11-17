import Foundation
import StoreKit

/// China mainland App Store compliance gate (E2EE Family Chat + AIGC / Companion / AI Assistant).
///
/// Apple App Store Connect «Оценка безопасности» / AIGC declarations apply to apps
/// **offered on the mainland China storefront**. We detect that storefront (`CHN`)
/// and hide regulated surfaces there so the honest ASC answer is **No**.
///
/// - Mainland only: `CHN`. Hong Kong (`HKG`), Macau (`MAC`), Taiwan (`TWN`) are **not** gated.
/// - RU / EU / US storefronts: features stay on.
/// - Launch args (DEBUG / UITest): `-ForceChinaMainlandCompliance` / `-ForceNonChinaMainlandCompliance`.
enum ChinaMainlandCompliance {
    /// ISO 3166-1 alpha-3 for mainland China App Store.
    static let mainlandChinaStorefrontCode = "CHN"

    /// Unit-test override. `nil` = use storefront / launch args.
    static var testingOverrideIsMainlandChina: Bool?

    private static let cacheLock = NSLock()
    private static var cachedStorefrontCountryCode: String?

    /// True when the App Store storefront is mainland China (or forced in tests).
    static var isMainlandChinaAppStore: Bool {
        if let testingOverrideIsMainlandChina {
            return testingOverrideIsMainlandChina
        }
        let args = ProcessInfo.processInfo.arguments
        if args.contains("-ForceChinaMainlandCompliance") { return true }
        if args.contains("-ForceNonChinaMainlandCompliance") { return false }
        guard let code = resolvedStorefrontCountryCode() else {
            // No storefront yet (cold start / Simulator): do **not** restrict — RU/dev stay open.
            return false
        }
        return code.uppercased() == mainlandChinaStorefrontCode
    }

    /// Family Chat (E2EE IM) + Companion/AIGC + AI Assistant must be off when true.
    static var restrictsEncryptedChatAndAIGC: Bool {
        isMainlandChinaAppStore
    }

    /// Sync read of StoreKit storefront (alpha-3), with cache.
    static func resolvedStorefrontCountryCode() -> String? {
        cacheLock.lock()
        defer { cacheLock.unlock() }
        if let cachedStorefrontCountryCode, !cachedStorefrontCountryCode.isEmpty {
            return cachedStorefrontCountryCode
        }
        if let code = SKPaymentQueue.default().storefront?.countryCode, !code.isEmpty {
            cachedStorefrontCountryCode = code
            return code
        }
        return nil
    }

    /// Refresh cache from StoreKit 2 (call once at launch).
    @MainActor
    static func refreshStorefrontFromAppStore() async {
        if let storefront = await Storefront.current {
            cacheLock.lock()
            cachedStorefrontCountryCode = storefront.countryCode
            cacheLock.unlock()
        }
    }

    /// Reset cache + test override (unit tests).
    static func resetForTesting() {
        testingOverrideIsMainlandChina = nil
        cacheLock.lock()
        cachedStorefrontCountryCode = nil
        cacheLock.unlock()
    }
}

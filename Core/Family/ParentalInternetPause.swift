import Foundation
import ManagedSettings

/// F5 — пауза: щит приложений/сайтов на телефоне ребёнка, держится после закрытия ALADDIN.
/// Именованный ManagedSettingsStore (iOS 16+, как bedtime), отдельно от дневных лимитов.
/// На iOS 15 — дефолтный store.
enum ParentalInternetPause {
    static let storeNameRaw = "aladdin.pause"
    private static let pausedKey = "aladdin.internet_paused"
    private static let pausedAtKey = "aladdin.internet_paused_at"

    private static var store: ManagedSettingsStore {
        if #available(iOS 16.0, *) {
            return ManagedSettingsStore(named: ManagedSettingsStore.Name(storeNameRaw))
        }
        return ManagedSettingsStore()
    }

    private static var defaults: UserDefaults {
        UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
    }

    static var isPausedLocally: Bool {
        defaults.bool(forKey: pausedKey)
    }

    /// Применить или снять щит на **этом** устройстве (телефон ребёнка).
    static func applyLocalState(paused: Bool) {
        defaults.set(paused, forKey: pausedKey)
        if paused {
            guard AppStoreBuildPolicy.allowsSystemFamilyControls else {
                print("ℹ️ ParentalInternetPause: FC gated — flag saved, shield skipped")
                return
            }
            store.shield.applicationCategories = .all()
            defaults.set(Date().timeIntervalSince1970, forKey: pausedAtKey)
            print("⏸️ ParentalInternetPause: shields ON (persists after app exit)")
        } else {
            store.shield.applicationCategories = nil
            store.shield.applications = nil
            store.shield.webDomains = nil
            print("▶️ ParentalInternetPause: shields OFF")
        }
        UserDefaults.standard.set(paused, forKey: "parental_internet_paused")
    }
}

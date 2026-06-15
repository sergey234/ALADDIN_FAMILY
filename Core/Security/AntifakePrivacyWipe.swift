import Foundation

/// N-03 — remove all local antifake artifacts on account delete.
enum AntifakePrivacyWipe {
    static func wipeAllLocalData() {
        AntifakeLastCallContext.clearOnAccountDelete()
        AntifakeCheckHistoryStore.clear()
        AntifakeSharePayloadStore.clear()
        AntifakeCallDirectoryStore.clearForAccountDelete()

        let keys = [
            AppConfig.UserDefaultsKeys.pendingAntifakePostCallCheck,
            AppConfig.UserDefaultsKeys.antifakePostCallReminderEnabled,
            AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt,
        ]
        for key in keys {
            UserDefaults.standard.removeObject(forKey: key)
        }
    }
}

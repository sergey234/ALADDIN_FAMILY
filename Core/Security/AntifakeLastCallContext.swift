import Foundation

/// E-07: remember last caller metadata for post-call call-check prefill.
enum AntifakeLastCallContext {
    private static let callerKey = AppConfig.UserDefaultsKeys.antifakeLastCallerId
    private static let displayNameKey = AppConfig.UserDefaultsKeys.antifakeLastDisplayName

    static func save(callerId: String, displayName: String) {
        let cid = callerId.trimmingCharacters(in: .whitespacesAndNewlines)
        let name = displayName.trimmingCharacters(in: .whitespacesAndNewlines)
        if !cid.isEmpty {
            UserDefaults.standard.set(cid, forKey: callerKey)
        }
        if !name.isEmpty {
            UserDefaults.standard.set(name, forKey: displayNameKey)
        }
    }

    static func consumePrefill() -> (callerId: String, displayName: String)? {
        let cid = UserDefaults.standard.string(forKey: callerKey)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let name = UserDefaults.standard.string(forKey: displayNameKey)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        guard !cid.isEmpty || !name.isEmpty else { return nil }
        UserDefaults.standard.removeObject(forKey: callerKey)
        UserDefaults.standard.removeObject(forKey: displayNameKey)
        return (cid, name)
    }

    @MainActor
    static func applyPrefillIfNeeded(to viewModel: AntifakeMediaCheckViewModel) {
        guard viewModel.mediaKind == .call,
              viewModel.callerId.isEmpty,
              let prefill = consumePrefill() else { return }
        if viewModel.callerId.isEmpty, !prefill.callerId.isEmpty {
            viewModel.callerId = prefill.callerId
        }
        if viewModel.displayName.isEmpty, !prefill.displayName.isEmpty {
            viewModel.displayName = prefill.displayName
        }
    }

    static func clearOnAccountDelete() {
        UserDefaults.standard.removeObject(forKey: callerKey)
        UserDefaults.standard.removeObject(forKey: displayNameKey)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.antifakeMediaUploadConsentGiven)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
    }
}

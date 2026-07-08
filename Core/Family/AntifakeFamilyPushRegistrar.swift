import Foundation

/// fws-03: register parent APNs token so `maybe_notify_parents_likely_fake` can deliver alerts.
@MainActor
final class AntifakeFamilyPushRegistrar {
    static let shared = AntifakeFamilyPushRegistrar()

    private let lastSyncKey = "antifake_family_push_token_last_hex"

    private init() {}

    func syncTokenIfNeeded(force: Bool = false) async {
        guard AppConfig.authToken != nil else { return }
        guard let token = NotificationManager.shared.deviceToken,
              !token.isEmpty else { return }

        let previous = UserDefaults.standard.string(forKey: lastSyncKey) ?? ""
        if !force, previous == token { return }

        let result: Result<AntifakeFamilyPushTokenResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.antifakeRegisterFamilyPushToken(token) { continuation.resume(returning: $0) }
        }
        if case .success = result {
            UserDefaults.standard.set(token, forKey: lastSyncKey)
        }
    }
}

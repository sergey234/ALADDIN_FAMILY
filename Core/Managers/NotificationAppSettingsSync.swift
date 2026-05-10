import Foundation
import UIKit

/// Синхронизация тумблеров «Push / Звук» на экране настроек с `GET/POST /api/settings/notifications*`.
/// Локальный источник правды остаётся `NotificationManager`; сервер — для кросс‑устройства и серверной логики push.
@MainActor
final class NotificationAppSettingsSync {
    static let shared = NotificationAppSettingsSync()

    private var debouncedPushWorkItem: DispatchWorkItem?
    private var becomeActiveObserver: NSObjectProtocol?

    private init() {
        becomeActiveObserver = NotificationCenter.default.addObserver(
            forName: UIApplication.didBecomeActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { @MainActor in
                self?.retryPendingSyncIfNeeded()
            }
        }
    }

    deinit {
        if let o = becomeActiveObserver {
            NotificationCenter.default.removeObserver(o)
        }
    }

    /// Тот же идентификатор, что и для подписки/дашборда: `deviceId` из JWT (`SubscriptionManager.currentToken`).
    func settingsUserId() -> String {
        let t = SubscriptionManager.shared.currentToken?.deviceId.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !t.isEmpty { return t }
        return UIDevice.current.identifierForVendor?.uuidString ?? ""
    }

    func deviceIdForRequestBody() -> String {
        UIDevice.current.identifierForVendor?.uuidString ?? settingsUserId()
    }

    private func storedRemoteVersion() -> Int? {
        let k = AppConfig.UserDefaultsKeys.notificationAppSettingsRemoteVersion
        guard UserDefaults.standard.object(forKey: k) != nil else { return nil }
        return UserDefaults.standard.integer(forKey: k)
    }

    private func setStoredRemoteVersion(_ v: Int) {
        UserDefaults.standard.set(v, forKey: AppConfig.UserDefaultsKeys.notificationAppSettingsRemoteVersion)
    }

    /// Вызывать после изменения локальных тумблеров (debounce внутри).
    func schedulePushAfterLocalChange() {
        debouncedPushWorkItem?.cancel()
        let work = DispatchWorkItem { [weak self] in
            self?.pushCurrentLocalToServer()
        }
        debouncedPushWorkItem = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4, execute: work)
    }

    /// Pull с сервера при открытии настроек; серверный ответ имеет приоритет над локальными `@Published` для двух тумблеров.
    func pullFromServer(into viewModel: SettingsViewModel) {
        guard KeychainManager.shared.loadString(forKey: .authToken) != nil else { return }
        let uid = settingsUserId()
        guard !uid.isEmpty else { return }

        APIService.shared.getNotificationSettingsApp(userId: uid) { result in
            Task { @MainActor in
                switch result {
                case .success(let r):
                    viewModel.applyRemoteNotificationAppSettings(
                        masterEnabled: r.enabled,
                        pushEnabled: r.pushEnabled,
                        soundEnabled: r.soundEnabled
                    )
                    self.setStoredRemoteVersion(r.version)
                    UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.notificationAppSettingsSyncPending)
                case .failure:
                    break
                }
            }
        }
    }

    func retryPendingSyncIfNeeded() {
        guard UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.notificationAppSettingsSyncPending) else { return }
        guard KeychainManager.shared.loadString(forKey: .authToken) != nil else { return }
        pushCurrentLocalToServer()
    }

    private func pushCurrentLocalToServer() {
        guard KeychainManager.shared.loadString(forKey: .authToken) != nil else { return }
        let uid = settingsUserId()
        guard !uid.isEmpty else { return }

        let local = NotificationManager.shared.notificationSettings
        let master = local.securityEnabled || local.soundEnabled
        APIService.shared.updateNotificationSettingsApp(
            userId: uid,
            enabled: master,
            pushEnabled: local.securityEnabled,
            soundEnabled: local.soundEnabled,
            emailEnabled: nil,
            deviceId: deviceIdForRequestBody(),
            version: storedRemoteVersion()
        ) { result in
            Task { @MainActor in
                switch result {
                case .success(let r):
                    self.setStoredRemoteVersion(r.version)
                    UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.notificationAppSettingsSyncPending)
                case .failure:
                    UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.notificationAppSettingsSyncPending)
                }
            }
        }
    }
}

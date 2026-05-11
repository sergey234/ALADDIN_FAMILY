import Foundation
import NetworkExtension
import Combine
import CryptoKit

/**
 * 🌐 DNS Protection Manager (План 2026)
 * Управление системным DoH (DNS-over-HTTPS) профилем
 * Использует NEDNSSettingsManager для защиты трафика без VPN
 */
@MainActor
class DNSProtectionManager: ObservableObject {

    /// Домен NSError для ошибок `NEDNSSettingsManager` (в Swift-обёртке символ `NEConfigurationErrorDomain` не всегда доступен).
    private static let neConfigurationErrorDomain = "NEConfigurationErrorDomain"

    /// Параметр `childId` для `/dns-config`: UUID или серверный идентификатор вида `MEM_…` (см. прод-логи). Произвольный текст (имя) не передаём.
    static func dnsConfigQueryChildId(from raw: String) -> String? {
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !t.isEmpty else { return nil }
        if UUID(uuidString: t) != nil { return t }
        let upper = t.uppercased()
        guard upper.hasPrefix("MEM_") else { return nil }
        let rest = String(t.dropFirst(4))
        guard rest.count >= 8 else { return nil }
        guard rest.range(of: "^[0-9a-fA-F]+$", options: .regularExpression) != nil else { return nil }
        return t
    }
    
    static let shared = DNSProtectionManager()
    
    @Published var isEnabled: Bool = false
    @Published var isLoading: Bool = false
    @Published var lastError: String?

    private var lastEnableRequestAt: Date?
    private var dnsSaveRetryUsed = false
    
    private let dnsSettingsManager = NEDNSSettingsManager.shared()
    
    private init() {
        loadStatus()
    }
    
    /// Загрузить текущий статус профиля DNS
    func loadStatus() {
        dnsSettingsManager.loadFromPreferences { [weak self] error in
            DispatchQueue.main.async {
                if let error = error {
                    print("⚠️ DNS Manager: Failed to load preferences: \(error.localizedDescription)")
                    return
                }
                self?.isEnabled = self?.dnsSettingsManager.dnsSettings != nil
                print("🌐 DNS Manager: Status loaded (Enabled: \(self?.isEnabled ?? false))")
                self?.postNetworkLayerIndicatorsChanged(trackAnalytics: false, source: "status_load")
            }
        }
    }
    
    /// Активировать DoH защиту
    func enableProtection(childId: String? = nil) {
        guard !isLoading else {
            print("⏭️ DNS Manager: enableProtection ignored (already in progress)")
            return
        }
        let now = Date()
        if let t = lastEnableRequestAt, now.timeIntervalSince(t) < 1.2 {
            print("⏭️ DNS Manager: enableProtection throttled (<1.2s)")
            return
        }
        lastEnableRequestAt = now
        dnsSaveRetryUsed = false
        isLoading = true
        lastError = nil
        
        // 1. Получаем конфигурацию с бэкенда
        APIService.shared.getDNSConfig(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let config):
                    self?.setupDNSProfile(config: config, childId: childId)
                case .failure(let error):
                    self?.isLoading = false
                    self?.lastError = "Ошибка получения конфига: \(error.localizedDescription)"
                    print("❌ DNS Manager: API error: \(error.localizedDescription)")
                }
            }
        }
    }
    
    /// Отключить DoH защиту
    func disableProtection() {
        isLoading = true
        dnsSettingsManager.loadFromPreferences { [weak self] error in
            if let error = error {
                self?.handleError(error)
                return
            }
            
            self?.dnsSettingsManager.removeFromPreferences { error in
                DispatchQueue.main.async {
                    self?.isLoading = false
                    if let error = error {
                        self?.lastError = error.localizedDescription
                    } else {
                        self?.isEnabled = false
                        self?.lastError = nil
                        print("✅ DNS Manager: Profile removed")
                        self?.postNetworkLayerIndicatorsChanged(trackAnalytics: true, source: "doh_profile_removed")
                    }
                }
            }
        }
    }
    
    // MARK: - Private Methods
    
    private func setupDNSProfile(config: DNSConfigResponse, childId: String?) {
        dnsSettingsManager.loadFromPreferences { [weak self] error in
            if let error = error {
                self?.handleError(error)
                return
            }
            
            let dohSettings = NEDNSOverHTTPSSettings()
            dohSettings.serverURL = URL(string: config.dohUrl)
            
            // Настраиваем системный DNS
            self?.dnsSettingsManager.dnsSettings = dohSettings
            self?.dnsSettingsManager.localizedDescription = config.serverName
            
            // Сохраняем и активируем
            self?.dnsSettingsManager.saveToPreferences { error in
                DispatchQueue.main.async {
                    if let error = error {
                        let ns = error as NSError
                        // Code 11 «IPC failed»: сбой связи с nehelper / NetworkExtension (часто временный, симулятор, гонки UI).
                        if ns.domain == Self.neConfigurationErrorDomain, ns.code == 11,
                           let strong = self, !strong.dnsSaveRetryUsed {
                            strong.dnsSaveRetryUsed = true
                            print("🔁 DNS Manager: IPC failed — one retry after delay")
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.85) {
                                strong.setupDNSProfile(config: config, childId: childId)
                            }
                            return
                        }
                        self?.isLoading = false
                        self?.lastError = "Не удалось сохранить профиль iOS: \(error.localizedDescription)"
                        print("❌ DNS Manager: Save error: \(error.localizedDescription)")
                    } else {
                        self?.isLoading = false
                        self?.isEnabled = true
                        self?.lastError = nil
                        print("✅ DNS Manager: DoH Profile active (\(config.dohUrl))")
                        self?.postDnsMonitoringIngest(config: config, childId: childId)
                        self?.postNetworkLayerIndicatorsChanged(trackAnalytics: true, source: "doh_profile_saved")
                    }
                }
            }
        }
    }

    /// pc-05: агрегат в `parental_monitoring_events` (хэш DoH URL, без полного URL в явном виде).
    private func postDnsMonitoringIngest(config: DNSConfigResponse, childId: String?) {
        let digest = SHA256.hash(data: Data(config.dohUrl.utf8))
        let hashHex = digest.map { String(format: "%02x", $0) }.joined()
        var payload: [String: Any] = [
            "doh_url_sha256": hashHex,
            "blocking_enabled": config.blockingEnabled,
            "server_name": config.serverName,
            "site": config.serverName
        ]
        if let childId, !childId.isEmpty {
            payload["child_id"] = childId
        }
        let event = ParentalMonitoringEventInDTO(kind: "dns", payload: payload)
        APIService.shared.postParentalMonitoringEvents(events: [event]) { _ in }
    }
    
    private func handleError(_ error: Error) {
        DispatchQueue.main.async {
            self.isLoading = false
            self.lastError = error.localizedDescription
            print("❌ DNS Manager: Error: \(error.localizedDescription)")
        }
    }

    /// int-9: отдельная аналитика/индикаторы для Smart DNS, не смешивать с Safari CB и счётчиком угроз.
    private func postNetworkLayerIndicatorsChanged(trackAnalytics: Bool, source: String) {
        if trackAnalytics {
            MetricsService.shared.trackUserAction(
                action: "network_protection_smart_dns_state",
                parameters: [
                    "layer": "smart_dns",
                    "active": isEnabled,
                    "source": source
                ]
            )
        }
        NotificationCenter.default.post(name: Notification.Name.networkLayerIndicatorsRefresh, object: nil)
    }
}

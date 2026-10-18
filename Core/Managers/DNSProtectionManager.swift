import Foundation
import os
#if canImport(NetworkExtension)
import NetworkExtension
#endif
import Combine
import CryptoKit

/**
 * 🌐 DNS Protection Manager (План 2026)
 * Управление системным DoH (DNS-over-HTTPS) профилем
 * Использует NEDNSSettingsManager для защиты трафика без VPN
 */
@MainActor
class DNSProtectionManager: ObservableObject {
    private enum DNSLogLevel {
        case debug
        case info
        case warning
        case error
    }

    enum RuntimeState: Equatable {
        case unsupportedBuild
        case simulatorPreview
        case inactive
        case savingProfile
        case needsSystemEnable
        case active
        case failedUserReadable(String)

        var localizationKey: String {
            switch self {
            case .unsupportedBuild:
                return "bypass_smart_dns_status_unavailable"
            case .simulatorPreview:
                return "bypass_smart_dns_status_simulator_preview"
            case .inactive:
                return "bypass_smart_dns_status_inactive"
            case .savingProfile:
                return "bypass_smart_dns_status_saving"
            case .needsSystemEnable:
                return "bypass_smart_dns_status_needs_settings"
            case .active:
                return "bypass_smart_dns_status_active"
            case .failedUserReadable:
                return "bypass_smart_dns_status_failed"
            }
        }
    }

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
    private static let dnsLog = Logger(
        subsystem: Bundle.main.bundleIdentifier ?? "ALADDIN",
        category: "SmartDNS"
    )
    
    @Published var isEnabled: Bool = false
    @Published var isLoading: Bool = false
    @Published var lastError: String?
    @Published private(set) var runtimeState: RuntimeState = .inactive

    private var lastEnableRequestAt: Date?
    private var dnsSaveRetryUsed = false
    private var lastStatusLoadAt: Date?
    private var statusLoadInFlight = false
    private let simulatorPreviewKey = "smart_dns_simulator_preview_enabled_v1"
    
    private let statusLoadMinInterval: TimeInterval = 2.0
    
    private let dnsSettingsManager = NEDNSSettingsManager.shared()
    
    private init() {
        logDNS("manager_init")
        loadStatus(force: true)
    }
    
    /// Загрузить текущий статус профиля DNS (throttled; без notification loop).
    func loadStatus(force: Bool = false) {
        guard AppStoreBuildPolicy.allowsSmartDNS else {
            isEnabled = false
            isLoading = false
            lastError = nil
            runtimeState = .unsupportedBuild
            logDNS("status unsupported_build", level: .warning)
            return
        }
        #if targetEnvironment(simulator)
        isEnabled = UserDefaults.standard.bool(forKey: simulatorPreviewKey)
        isLoading = false
        lastError = nil
        runtimeState = .simulatorPreview
        logDNS("status simulator_preview stored=\(isEnabled)", level: .debug)
        return
        #else
        if statusLoadInFlight { return }
        let now = Date()
        if !force, let last = lastStatusLoadAt, now.timeIntervalSince(last) < statusLoadMinInterval {
            return
        }
        statusLoadInFlight = true
        lastStatusLoadAt = now

        dnsSettingsManager.loadFromPreferences { [weak self] error in
            DispatchQueue.main.async {
                guard let self else { return }
                self.statusLoadInFlight = false
                if let error = error {
                    #if DEBUG
                    print("⚠️ DNS Manager: Failed to load preferences: \(error.localizedDescription)")
                    #endif
                    self.logDNS("status load_failed reason=\(self.safeErrorSummary(error))", level: .error)
                    self.runtimeState = .failedUserReadable("bypass_smart_dns_reason_generic")
                    return
                }
                let hasProfile = self.dnsSettingsManager.dnsSettings != nil
                let profileActive = hasProfile && self.dnsSettingsManager.isEnabled
                let newEnabled = hasProfile
                let changed = newEnabled != self.isEnabled
                self.isEnabled = newEnabled
                self.runtimeState = profileActive ? .active : (hasProfile ? .needsSystemEnable : .inactive)
                #if DEBUG
                if changed || force {
                    print("🌐 DNS Manager: Status loaded (Enabled: \(newEnabled))")
                }
                #endif
                if changed || force {
                    self.logDNS(
                        "status loaded has_profile=\(hasProfile) ios_enabled=\(self.dnsSettingsManager.isEnabled) runtime=\(self.runtimeState.logLabel)",
                        level: .info
                    )
                }
                if changed {
                    self.postNetworkLayerIndicatorsChanged(trackAnalytics: false, source: "status_load")
                }
            }
        }
        #endif
    }
    
    /// Активировать DoH защиту
    func enableProtection(childId: String? = nil) {
        guard AppStoreBuildPolicy.allowsSmartDNS else {
            isEnabled = false
            isLoading = false
            lastError = nil
            runtimeState = .unsupportedBuild
            logDNS("enable ignored unsupported_build", level: .warning)
            return
        }
        #if targetEnvironment(simulator)
        isEnabled = true
        isLoading = false
        lastError = nil
        runtimeState = .simulatorPreview
        UserDefaults.standard.set(true, forKey: simulatorPreviewKey)
        logDNS("enable simulator_preview_on", level: .info)
        postNetworkLayerIndicatorsChanged(trackAnalytics: false, source: "simulator_preview_enabled")
        return
        #else
        guard !isLoading else {
            logDNS("enable ignored already_in_progress", level: .debug)
            return
        }
        let now = Date()
        if let t = lastEnableRequestAt, now.timeIntervalSince(t) < 1.2 {
            logDNS("enable throttled", level: .debug)
            return
        }
        lastEnableRequestAt = now
        dnsSaveRetryUsed = false
        isLoading = true
        lastError = nil
        runtimeState = .savingProfile
        logDNS("enable requested scope=\(childId == nil ? "family" : "child")", level: .info)
        
        // 1. Получаем конфигурацию с бэкенда
        APIService.shared.getDNSConfig(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let config):
                    self?.logDNS("config loaded blocking=\(config.blockingEnabled) server_name_present=\(!config.serverName.isEmpty)", level: .info)
                    self?.setupDNSProfile(config: config, childId: childId)
                case .failure(let error):
                    self?.isLoading = false
                    self?.lastError = "Ошибка получения конфига: \(error.localizedDescription)"
                    self?.runtimeState = .failedUserReadable("bypass_smart_dns_reason_no_config")
                    self?.logDNS("config failed reason=\(self?.safeErrorSummary(error) ?? "unknown")", level: .error)
                }
            }
        }
        #endif
    }
    
    /// Отключить DoH защиту
    func disableProtection() {
        #if targetEnvironment(simulator)
        isEnabled = false
        isLoading = false
        lastError = nil
        runtimeState = .simulatorPreview
        UserDefaults.standard.set(false, forKey: simulatorPreviewKey)
        logDNS("disable simulator_preview_off", level: .info)
        postNetworkLayerIndicatorsChanged(trackAnalytics: false, source: "simulator_preview_disabled")
        return
        #else
        isLoading = true
        logDNS("disable requested", level: .info)
        dnsSettingsManager.loadFromPreferences { [weak self] error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.logDNS("disable load_failed reason=\(self?.safeErrorSummary(error) ?? "unknown")", level: .error)
                    self?.handleError(error)
                    return
                }
                
                self?.dnsSettingsManager.removeFromPreferences { error in
                    DispatchQueue.main.async {
                        self?.isLoading = false
                        if let error = error {
                            self?.lastError = error.localizedDescription
                            self?.runtimeState = .failedUserReadable("bypass_smart_dns_reason_generic")
                            self?.logDNS("disable remove_failed reason=\(self?.safeErrorSummary(error) ?? "unknown")", level: .error)
                        } else {
                            self?.isEnabled = false
                            self?.lastError = nil
                            self?.runtimeState = .inactive
                            self?.logDNS("disable profile_removed", level: .info)
                            self?.postNetworkLayerIndicatorsChanged(trackAnalytics: true, source: "doh_profile_removed")
                        }
                    }
                }
            }
        }
        #endif
    }
    
    // MARK: - Private Methods
    
    private func setupDNSProfile(config: DNSConfigResponse, childId: String?) {
        logDNS("profile setup_load_preferences scope=\(childId == nil ? "family" : "child")", level: .debug)
        dnsSettingsManager.loadFromPreferences { [weak self] error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.logDNS("profile setup_load_failed reason=\(self?.safeErrorSummary(error) ?? "unknown")", level: .error)
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
                            // Code 11: NetworkExtension preference service rejected the save; retry once.
                            if ns.domain == Self.neConfigurationErrorDomain, ns.code == 11,
                               let strong = self, !strong.dnsSaveRetryUsed {
                                strong.dnsSaveRetryUsed = true
                                strong.logDNS("profile save_retry reason=neconfiguration_11", level: .warning)
                                DispatchQueue.main.asyncAfter(deadline: .now() + 0.85) {
                                    strong.setupDNSProfile(config: config, childId: childId)
                                }
                                return
                            }
                            self?.isLoading = false
                            self?.lastError = "Не удалось сохранить профиль iOS: \(error.localizedDescription)"
                            self?.runtimeState = .failedUserReadable("bypass_smart_dns_reason_ios_save")
                            self?.logDNS("profile save_failed reason=\(self?.safeErrorSummary(error) ?? "unknown")", level: .error)
                        } else {
                            self?.isLoading = false
                            self?.isEnabled = false
                            self?.lastError = nil
                            self?.runtimeState = .needsSystemEnable
                            self?.logDNS("profile saved needs_ios_settings blocking=\(config.blockingEnabled)", level: .info)
                            self?.postDnsMonitoringIngest(config: config, childId: childId)
                            self?.postNetworkLayerIndicatorsChanged(trackAnalytics: true, source: "doh_profile_saved")
                        }
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
        logDNS("monitoring ingest queued hash_prefix=\(String(hashHex.prefix(8)))", level: .debug)
        APIService.shared.postParentalMonitoringEvents(events: [event]) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self?.logDNS("monitoring ingest ok", level: .debug)
                case .failure(let error):
                    self?.logDNS("monitoring ingest failed reason=\(self?.safeErrorSummary(error) ?? "unknown")", level: .warning)
                }
            }
        }
    }
    
    private func handleError(_ error: Error) {
        isLoading = false
        lastError = error.localizedDescription
        runtimeState = .failedUserReadable("bypass_smart_dns_reason_generic")
        logDNS("error handled reason=\(safeErrorSummary(error))", level: .error)
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
        logDNS("indicator_refresh posted source=\(source) analytics=\(trackAnalytics)", level: .debug)
    }

    private func logDNS(_ message: String, level: DNSLogLevel = .info) {
        #if DEBUG
        print("🌐 SmartDNS: \(message)")
        #endif

        switch level {
        case .debug:
            Self.dnsLog.debug("\(message, privacy: .public)")
        case .info:
            Self.dnsLog.info("\(message, privacy: .public)")
        case .warning:
            Self.dnsLog.warning("\(message, privacy: .public)")
        case .error:
            Self.dnsLog.error("\(message, privacy: .public)")
        }
    }

    private func safeErrorSummary(_ error: Error) -> String {
        let ns = error as NSError
        return "\(ns.domain)#\(ns.code)"
    }
}

private extension DNSProtectionManager.RuntimeState {
    var logLabel: String {
        switch self {
        case .unsupportedBuild:
            return "unsupported_build"
        case .simulatorPreview:
            return "simulator_preview"
        case .inactive:
            return "inactive"
        case .savingProfile:
            return "saving_profile"
        case .needsSystemEnable:
            return "needs_system_enable"
        case .active:
            return "active"
        case .failedUserReadable:
            return "failed"
        }
    }
}

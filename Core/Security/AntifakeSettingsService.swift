import Foundation

/// fws-06 — voice fraud threshold sync with `/api/antifake/settings`.
@MainActor
final class AntifakeSettingsService: ObservableObject {
    static let shared = AntifakeSettingsService()

    @Published private(set) var thresholdPercent: Int = 72
    @Published private(set) var minThresholdPercent: Int = 50
    @Published private(set) var maxThresholdPercent: Int = 95
    @Published private(set) var isLoading = false
    @Published private(set) var lastErrorKey: String?

    private init() {
        let cached = UserDefaults.standard.integer(forKey: AppConfig.UserDefaultsKeys.antifakeVoiceFraudThresholdPercent)
        if cached >= minThresholdPercent, cached <= maxThresholdPercent {
            thresholdPercent = cached
        }
    }

    func refresh() async {
        isLoading = true
        defer { isLoading = false }
        let result: Result<AntifakeSettingsResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getAntifakeSettings { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            apply(payload)
            lastErrorKey = nil
        case .failure:
            lastErrorKey = "antifake_voice_fraud_threshold_save_error"
        }
    }

    func updateThreshold(_ percent: Int) async -> Bool {
        let clamped = clamp(percent)
        thresholdPercent = clamped
        cacheLocally(clamped)
        let result: Result<AntifakeSettingsResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.putAntifakeSettings(thresholdPercent: clamped) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            apply(payload)
            lastErrorKey = nil
            return true
        case .failure:
            lastErrorKey = "antifake_voice_fraud_threshold_save_error"
            return false
        }
    }

    func presetMild() -> Int { 60 }
    func presetBalanced() -> Int { 72 }
    func presetStrict() -> Int { 85 }

    private func apply(_ payload: AntifakeSettingsResponse) {
        minThresholdPercent = payload.minThresholdPercent
        maxThresholdPercent = payload.maxThresholdPercent
        thresholdPercent = clamp(payload.voiceFraudThresholdPercent)
        cacheLocally(thresholdPercent)
    }

    private func clamp(_ value: Int) -> Int {
        max(minThresholdPercent, min(maxThresholdPercent, value))
    }

    private func cacheLocally(_ value: Int) {
        UserDefaults.standard.set(value, forKey: AppConfig.UserDefaultsKeys.antifakeVoiceFraudThresholdPercent)
    }
}

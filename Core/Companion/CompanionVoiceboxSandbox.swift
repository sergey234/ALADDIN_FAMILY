import Foundation

/// P8 sandbox gate for Companion voice (Voicebox-inspired).
/// Brand STT/TTS only; no shop/VPN side effects. Controlled by feature flags.
enum CompanionVoiceboxSandbox {
    enum VoiceMode: String, Equatable {
        case sttOnly
        case brandTTS
    }

    enum GateResult: Equatable {
        case allowed(VoiceMode)
        case denied(reason: String)
    }

    static func evaluate(
        mode: VoiceMode,
        sandboxFlag: Bool = CompanionVoiceboxFeatureFlags.sandboxEnabled
    ) -> GateResult {
        guard sandboxFlag || CompanionVoiceboxFeatureFlags.prodEnabled else {
            return .denied(reason: "voicebox_flag_off")
        }
        switch mode {
        case .sttOnly, .brandTTS:
            return .allowed(mode)
        }
    }

    // MARK: - Hybrid (legacy Companion voice + Voicebox gate)

    /// Existing Companion STT/TTS (AVSpeech / neuro) — always available when flags are off.
    static var isLegacyCompanionVoiceEnabled: Bool { true }

    /// Experimental Voicebox path (sandbox or prod flag).
    static var isExperimentalVoiceboxPathEnabled: Bool {
        CompanionVoiceboxFeatureFlags.sandboxEnabled || CompanionVoiceboxFeatureFlags.prodEnabled
    }

    /// Allow brand TTS/STT.
    /// Flags OFF → legacy path (true). Flags ON → through `evaluate(.brandTTS)`.
    static func allowBrandSpeech() -> Bool {
        guard isExperimentalVoiceboxPathEnabled else {
            return isLegacyCompanionVoiceEnabled
        }
        switch evaluate(mode: .brandTTS) {
        case .allowed:
            return true
        case .denied:
            return false
        }
    }
}

import Foundation

/// P8 Voicebox / Companion voice path flags.
/// Defaults OFF — enable only after policy `docs/P8_VOICEBOX_POLICY.md` and QA.
enum CompanionVoiceboxFeatureFlags {
    private static let defaults = UserDefaults.standard

    private static func resolved(_ key: String, prodDefault: Bool) -> Bool {
        guard defaults.object(forKey: key) != nil else { return prodDefault }
        return defaults.bool(forKey: key)
    }

    /// Sandbox Companion voice path (brand TTS/STT only).
    /// Debug try: Xcode Scheme → Arguments Passed On Launch → `-voiceboxSandbox`
    static var sandboxEnabled: Bool {
        #if DEBUG
        if ProcessInfo.processInfo.arguments.contains("-voiceboxSandbox") {
            return true
        }
        #endif
        return resolved("companion.voiceboxSandboxEnabled", prodDefault: false)
    }

    /// Production Companion voice path — keep false until explicit QA sign-off.
    /// Never auto-on via launch args (prod requires deliberate UserDefaults / remote flag).
    static var prodEnabled: Bool {
        resolved("companion.voiceboxProdEnabled", prodDefault: false)
    }

    /// Kill switch: both off.
    static func disableAll() {
        defaults.set(false, forKey: "companion.voiceboxSandboxEnabled")
        defaults.set(false, forKey: "companion.voiceboxProdEnabled")
    }
}

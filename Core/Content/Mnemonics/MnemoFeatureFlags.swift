import Foundation

/// B14 optional v3 features. Prod preset **4–22 v1** (2026-06-06):
/// ON by default: memoryHeroAvatars, teenExamHacksCopy, advancedNumberPegs, storiesRecallHook
/// OFF by default: familyMemoryChallenge (enable after QA), companionVoiceReminder (wave 2)
/// Explicit UserDefaults value always overrides prod default.
enum MnemoFeatureFlags {
    private static let defaults = UserDefaults.standard

    private static func resolved(_ key: String, prodDefault: Bool) -> Bool {
        guard defaults.object(forKey: key) != nil else { return prodDefault }
        return defaults.bool(forKey: key)
    }

    static var memoryHeroAvatars: Bool {
        resolved("mnemo.memoryHeroAvatars", prodDefault: true)
    }

    static var teenExamHacksCopy: Bool {
        resolved("mnemo.teenExamHacksCopy", prodDefault: true)
    }

    static var familyMemoryChallenge: Bool {
        resolved("mnemo.familyMemoryChallenge", prodDefault: false)
    }

    static var companionVoiceReminder: Bool {
        resolved("mnemo.companionVoiceReminder", prodDefault: false)
    }

    static var storiesRecallHook: Bool {
        resolved("mnemo.storiesRecallHook", prodDefault: true)
    }

    static var advancedNumberPegs: Bool {
        resolved("mnemo.advancedNumberPegs", prodDefault: true)
    }
}

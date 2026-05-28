import Foundation

/// HERO-3-15: пресеты речи (зеркало BE `companion_characters` + `normalize_personality_preset`).
enum CompanionPersonalityPresets {
    static let allPresets = ["friendly", "calm", "playful", "mentor", "witty"]

    static func presetsForUI(ageBand: String?) -> [String] {
        if ageBand == "child" {
            return allPresets.filter { $0 != "witty" }
        }
        return allPresets
    }

    static func defaultPreset(characterId: String, ageBand: String = "parent") -> String {
        if ageBand == "senior", characterId == "aladdin" { return "calm" }
        switch characterId {
        case "unicorn": return "playful"
        case "aladdin": return "mentor"
        case "genie": return ageBand == "child" ? "playful" : "witty"
        default: return "friendly"
        }
    }

    static func normalize(_ preset: String, characterId: String, ageBand: String) -> String {
        let p = preset.trimmingCharacters(in: .whitespacesAndNewlines)
        if p == "witty", ageBand == "child" || characterId == "unicorn" {
            return "playful"
        }
        return allPresets.contains(p) ? p : "friendly"
    }

    /// Для TTS и UI чата: семейный preset с учётом героя и возраста.
    static func effective(stored: String, characterId: String, ageBand: String) -> String {
        normalize(stored, characterId: characterId, ageBand: ageBand)
    }
}

/// UX Sprint 1: профиль пользователя для упрощённого mic и overlay.
enum CompanionUserContext {
    static var isChildProfile: Bool {
        UserDefaults.standard.string(forKey: "current_user_role") == "child"
    }

    static var companionAgeBand: String {
        isChildProfile ? "child" : "parent"
    }
}

enum CompanionDisplayNames {
    static func heroName(characterId: String, localizationManager: LocalizationManager) -> String {
        switch characterId {
        case "aladdin": return localizationManager.localized("companion_hero_aladdin")
        case "genie": return localizationManager.localized("companion_hero_genie")
        default: return localizationManager.localized("companion_hero_unicorn")
        }
    }

    static func voiceErrorMessage(code: String, localizationManager: LocalizationManager) -> String {
        switch code {
        case "transcript_required":
            return localizationManager.localized("companion_voice_error_transcript_required")
        case "companion_unavailable", "voice_error":
            return localizationManager.localized("companion_voice_error_unavailable")
        case "voice_limit", "4429":
            return localizationManager.localized("companion_voice_error_limit")
        case "connection_lost":
            return localizationManager.localized("companion_voice_error_connection")
        default:
            return localizationManager.localized("companion_voice_error_unavailable")
        }
    }
}

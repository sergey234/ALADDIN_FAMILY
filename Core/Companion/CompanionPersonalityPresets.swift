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

    /// P2-14 — set when opening companion from Main «60+» card.
    static var isSeniorEntry: Bool {
        UserDefaults.standard.bool(forKey: "companion_senior_entry")
    }

    static var companionAgeBand: String {
        WellnessAgeBandResolver.localExpectedBand()
    }
}

/// Wellness Hub: age_band с сервера + выравнивание по роли в приложении.
enum WellnessAgeBandResolver {
    static func localExpectedBand() -> String {
        if CompanionUserContext.isChildProfile { return "child" }
        if CompanionUserContext.isSeniorEntry { return "senior" }
        let role = (UserDefaults.standard.string(forKey: "current_user_role") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        switch role {
        case "child", "kid", "ребенок", "ребёнок":
            return "child"
        case "teen", "teenager", "подросток":
            return "teen"
        case "elderly", "senior", "пожилой", "люди 60+":
            return "senior"
        case "parent", "guardian", "родитель":
            return "parent"
        default:
            return "parent"
        }
    }

    static var isAdultFamilyAccount: Bool {
        let band = localExpectedBand()
        return band == "parent" || band == "senior"
    }

    /// Сервер вернул child/teen, а локально взрослый аккаунт — показываем 4 направления.
    static func shouldOverrideServerChildBand(_ serverBand: String) -> Bool {
        isAdultFamilyAccount && (serverBand == "child" || serverBand == "teen")
    }

    static func pillarsForDisplay(
        serverPillars: [String],
        serverAgeBand: String
    ) -> (ageBand: String, pillars: [WellnessPillar]) {
        let band = shouldOverrideServerChildBand(serverAgeBand)
            ? localExpectedBand()
            : serverAgeBand
        let allowed = Set(serverPillars)
        var list = WellnessPillar.allowed(for: band).filter { allowed.contains($0.rawValue) }
        if list.isEmpty && isAdultFamilyAccount {
            list = WellnessPillar.allowed(for: localExpectedBand())
        }
        return (band, list)
    }
}

/// hero-x-50…51 — local + family settings for companion persona layers.
enum CompanionSettings {
    private static let vedicWisdomKey = "companion_vedic_wisdom_enabled_v1"

    /// Child profiles never receive wisdom snippets (hero-x-51).
    static func defaultVedicWisdomEnabled(ageBand: String) -> Bool {
        ageBand != "child"
    }

    static func cachedVedicWisdomEnabled(ageBand: String) -> Bool {
        if ageBand == "child" { return false }
        guard UserDefaults.standard.object(forKey: vedicWisdomKey) != nil else {
            return defaultVedicWisdomEnabled(ageBand: ageBand)
        }
        return UserDefaults.standard.bool(forKey: vedicWisdomKey)
    }

    static func setCachedVedicWisdomEnabled(_ enabled: Bool, ageBand: String) {
        let value = ageBand == "child" ? false : enabled
        UserDefaults.standard.set(value, forKey: vedicWisdomKey)
    }

    static func humorHintKey(for characterId: String) -> String {
        "companion_humor_hint_\(characterId)"
    }

    private static let teenHumorKey = "companion_teen_humor_preference_v1"

    static func cachedTeenHumorPreference() -> String {
        let raw = UserDefaults.standard.string(forKey: teenHumorKey) ?? "normal"
        return raw == "less" ? "less" : "normal"
    }

    static func setCachedTeenHumorPreference(_ value: String) {
        UserDefaults.standard.set(value == "less" ? "less" : "normal", forKey: teenHumorKey)
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

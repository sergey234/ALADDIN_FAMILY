import Foundation

/// fws-h01 — default hero by age_band + wellness context; respects explicit user pick.
enum CompanionHeroEntryPoint: Equatable {
    case hub
    case conversation
    case windDown
    case exam
    case reflective
    case seniorQuick
}

enum CompanionHeroRouter {
    static let userOverrideKey = "companion_hero_user_override_v1"
    static let selectedCharacterKey = "companion_selected_character_id"
    static let allHeroIDs = ["unicorn", "aladdin", "genie"]

    static var userOverride: Bool {
        UserDefaults.standard.bool(forKey: userOverrideKey)
    }

    static func markUserOverride(characterId: String) {
        let id = normalized(characterId)
        UserDefaults.standard.set(true, forKey: userOverrideKey)
        UserDefaults.standard.set(id, forKey: selectedCharacterKey)
    }

    static func clearUserOverride() {
        UserDefaults.standard.set(false, forKey: userOverrideKey)
    }

    static func resolve(
        ageBand: String? = nil,
        entryPoint: CompanionHeroEntryPoint = .conversation,
        wellnessPillar: String? = nil,
        storedCharacterId: String? = nil,
        userOverride override: Bool? = nil,
        allowedCharacterIds: [String]? = nil
    ) -> String {
        let band = (ageBand ?? WellnessAgeBandResolver.localExpectedBand())
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        let hasOverride = override ?? userOverride
        let stored = normalized(storedCharacterId ?? UserDefaults.standard.string(forKey: selectedCharacterKey))
        let allowed = allowedSet(allowedCharacterIds)

        if hasOverride, allowed.contains(stored) {
            return stored
        }

        let pillar = (wellnessPillar ?? inferredWellnessPillar())
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        var pick = defaultHero(band: band, entryPoint: entryPoint, pillar: pillar)

        if !allowed.contains(pick) {
            pick = fallbackHero(from: allowed, band: band)
        }
        return pick
    }

    /// Applies routed default to `companion_selected_character_id` when the user has not picked a hero.
    @discardableResult
    static func applyDefaultIfNeeded(
        entryPoint: CompanionHeroEntryPoint = .conversation,
        wellnessPillar: String? = nil,
        allowedCharacterIds: [String]? = nil
    ) -> String {
        if userOverride {
            return normalized(UserDefaults.standard.string(forKey: selectedCharacterKey))
        }
        let pick = resolve(
            entryPoint: entryPoint,
            wellnessPillar: wellnessPillar,
            allowedCharacterIds: allowedCharacterIds
        )
        UserDefaults.standard.set(pick, forKey: selectedCharacterKey)
        return pick
    }

    static func entryPointForCurrentLaunch() -> CompanionHeroEntryPoint {
        if UserDefaults.standard.bool(forKey: "companion_senior_entry") {
            return .seniorQuick
        }
        let pillar = inferredWellnessPillar()
        if !pillar.isEmpty {
            switch pillar {
            case "wind_down", "sleep", "sleep_story":
                return .windDown
            case "exam", "exam_countdown":
                return .exam
            case "jung", "humanistic", "reflective":
                return .reflective
            default:
                break
            }
        }
        return .conversation
    }

    // MARK: - Private

    private static func normalized(_ raw: String?) -> String {
        let id = (raw ?? "unicorn").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return allHeroIDs.contains(id) ? id : "unicorn"
    }

    private static func allowedSet(_ ids: [String]?) -> Set<String> {
        let source = ids?.map { $0.lowercased() } ?? allHeroIDs
        let filtered = source.filter { allHeroIDs.contains($0) }
        return Set(filtered.isEmpty ? allHeroIDs : filtered)
    }

    private static func inferredWellnessPillar() -> String {
        WellnessSessionStore.activePillar
            ?? WellnessSessionStore.exercisePillar
            ?? ""
    }

    private static func defaultHero(
        band: String,
        entryPoint: CompanionHeroEntryPoint,
        pillar: String
    ) -> String {
        if entryPoint == .seniorQuick || band == "senior" {
            return "aladdin"
        }
        if entryPoint == .exam || pillar == "exam" || pillar == "exam_countdown" {
            return "aladdin"
        }
        if shouldRouteGenie(band: band, entryPoint: entryPoint, pillar: pillar) {
            return "genie"
        }
        switch band {
        case "child":
            return "unicorn"
        case "teen":
            return "aladdin"
        case "parent":
            return "aladdin"
        default:
            return "unicorn"
        }
    }

    private static func shouldRouteGenie(
        band: String,
        entryPoint: CompanionHeroEntryPoint,
        pillar: String
    ) -> Bool {
        guard band != "child" else { return false }
        if entryPoint == .windDown {
            return true
        }
        if entryPoint == .reflective {
            return true
        }
        switch pillar {
        case "wind_down", "sleep", "sleep_story", "jung", "humanistic", "reflective":
            return true
        default:
            return false
        }
    }

    private static func fallbackHero(from allowed: Set<String>, band: String) -> String {
        let preference: [String]
        switch band {
        case "child":
            preference = ["unicorn", "aladdin", "genie"]
        case "teen", "parent", "senior":
            preference = ["aladdin", "genie", "unicorn"]
        default:
            preference = allHeroIDs
        }
        for id in preference where allowed.contains(id) {
            return id
        }
        return allowed.sorted().first ?? "unicorn"
    }
}

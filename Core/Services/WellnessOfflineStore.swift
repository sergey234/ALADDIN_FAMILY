import Foundation

/// p2-23 — локальный кэш wellness (pillars, recap, check-in draft) при офлайне.
enum WellnessOfflineStore {
    private static let pillarsKey = "wellness_offline_pillars_v1"
    private static let recapKey = "wellness_offline_recap_v1"
    private static let checkinDraftKey = "wellness_offline_checkin_draft_v1"
    private static let consentKey = "wellness_offline_consent_v1"
    private static let allianceKey = "wellness_offline_alliance_v1"

    static func savePillars(_ response: WellnessPillarsResponse) {
        guard let data = try? JSONEncoder().encode(response) else { return }
        UserDefaults.standard.set(data, forKey: pillarsKey)
    }

    static func loadPillars() -> WellnessPillarsResponse? {
        guard let data = UserDefaults.standard.data(forKey: pillarsKey),
              let decoded = try? JSONDecoder().decode(WellnessPillarsResponse.self, from: data) else {
            return nil
        }
        return decoded
    }

    static func saveRecap(_ recap: WellnessSessionRecapResponse) {
        guard let data = try? JSONEncoder().encode(recap) else { return }
        UserDefaults.standard.set(data, forKey: recapKey)
    }

    static func loadRecap() -> WellnessSessionRecapResponse? {
        guard let data = UserDefaults.standard.data(forKey: recapKey),
              let decoded = try? JSONDecoder().decode(WellnessSessionRecapResponse.self, from: data) else {
            return nil
        }
        return decoded
    }

    static func saveCheckinDraft(_ draft: WellnessCheckinDraft) {
        let enc = JSONEncoder()
        enc.dateEncodingStrategy = .iso8601
        guard let data = try? enc.encode(draft) else { return }
        UserDefaults.standard.set(data, forKey: checkinDraftKey)
    }

    static func loadCheckinDraft() -> WellnessCheckinDraft? {
        guard let data = UserDefaults.standard.data(forKey: checkinDraftKey) else { return nil }
        let dec = JSONDecoder()
        dec.dateDecodingStrategy = .iso8601
        return try? dec.decode(WellnessCheckinDraft.self, from: data)
    }

    static func setConsentCached(_ accepted: Bool) {
        UserDefaults.standard.set(accepted, forKey: consentKey)
    }

    static func consentCached() -> Bool {
        UserDefaults.standard.bool(forKey: consentKey)
    }

    static func saveAlliance(score: Int, heroEmotion: String) {
        let payload = ["score": score, "hero_emotion": heroEmotion] as [String: Any]
        UserDefaults.standard.set(payload, forKey: allianceKey)
    }

    static func loadAlliance() -> (score: Int, heroEmotion: String)? {
        guard let dict = UserDefaults.standard.dictionary(forKey: allianceKey),
              let score = dict["score"] as? Int,
              let emotion = dict["hero_emotion"] as? String else {
            return nil
        }
        return (score, emotion)
    }

    /// UI smoke (`-UITestWellnessNavSmoke`): hub без сети.
    static func seedNavSmokeFixtures() {
        savePillars(
            WellnessPillarsResponse(
                pillars: ["humanistic", "behavioral", "cognitive", "jung"],
                ageBand: "teen"
            )
        )
        setConsentCached(true)
    }
}

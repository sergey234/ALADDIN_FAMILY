import Foundation

/// HTTP-клиент Wellness API (`/api/wellness/*`, JWT).
@MainActor
final class WellnessAPIService {
    static let shared = WellnessAPIService()
    private let network: NetworkManager

    private init() {
        network = APIService.shared.networkManager
    }

    func fetchPillars() async throws -> WellnessPillarsResponse {
        try await get(AppConfig.Endpoint.wellnessPillars)
    }

    func fetchConsent() async throws -> WellnessConsentResponse {
        try await get(AppConfig.Endpoint.wellnessConsent)
    }

    func postConsent(accepted: Bool, psychologicalSupportEnabled: Bool? = nil) async throws -> WellnessConsentResponse {
        let body = WellnessConsentRequestBody(
            wellnessAccepted: accepted,
            psychologicalSupportEnabled: psychologicalSupportEnabled
        )
        return try await post(AppConfig.Endpoint.wellnessConsent, body: body)
    }

    func fetchSettings() async throws -> WellnessSettingsResponse {
        try await get(AppConfig.Endpoint.wellnessSettings)
    }

    func setParentShareAggregate(_ enabled: Bool) async throws -> WellnessSettingsResponse {
        struct Resp: Codable {
            let ok: Bool
            let settings: WellnessSettingsDTO
            let parentShareAggregate: Bool

            enum CodingKeys: String, CodingKey {
                case ok
                case settings
                case parentShareAggregate = "parent_share_aggregate"
            }
        }
        let r: Resp = try await post(
            AppConfig.Endpoint.wellnessParentShare,
            body: WellnessParentShareBody(parentShareAggregate: enabled)
        )
        return WellnessSettingsResponse(
            settings: r.settings,
            ageBand: "teen",
            canEditParentShare: true
        )
    }

    func setSessionPillar(_ pillar: String) async throws -> WellnessSessionPillarResponse {
        try await post(
            AppConfig.Endpoint.wellnessSessionPillar,
            body: WellnessPillarSelectBody(pillar: pillar)
        )
    }

    func postCheckin(mood: String, sleepHours: Double?, stressLevel: Int?) async throws -> WellnessCheckinResponse {
        try await post(
            AppConfig.Endpoint.wellnessCheckin,
            body: WellnessCheckinRequestBody(
                mood: mood,
                sleepHours: sleepHours,
                stressLevel: stressLevel,
                energyLevel: nil
            )
        )
    }

    func fetchJournal(days: Int = 7) async throws -> WellnessJournalResponse {
        try await get("\(AppConfig.Endpoint.wellnessJournal)?days=\(days)")
    }

    func fetchTriggers() async throws -> WellnessTriggersResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get("\(AppConfig.Endpoint.wellnessTriggersStatus)?locale=\(loc)")
    }

    func dismissIdleNudge() async throws {
        struct Resp: Codable { let ok: Bool }
        let _: Resp = try await post(AppConfig.Endpoint.wellnessNudgeIdleDismiss, body: EmptyBody())
    }

    private struct EmptyBody: Encodable {}

    func fetchPhqLiteSchema() async throws -> WellnessPhqLiteSchemaResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await get("\(AppConfig.Endpoint.wellnessPhqLiteSchema)?locale=\(loc)")
    }

    func submitPhqLite(answers: [Int]) async throws -> WellnessPhqSubmitResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await post(
            "\(AppConfig.Endpoint.wellnessPhqLiteSubmit)?locale=\(loc)",
            body: WellnessPhqSubmitBody(answers: answers)
        )
    }

    func fetchPhq9Schema() async throws -> WellnessPhqLiteSchemaResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await get("\(AppConfig.Endpoint.wellnessPhq9Schema)?locale=\(loc)")
    }

    func submitPhq9(answers: [Int]) async throws -> WellnessPhqSubmitResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await post(
            "\(AppConfig.Endpoint.wellnessPhq9Submit)?locale=\(loc)",
            body: WellnessPhqSubmitBody(answers: answers)
        )
    }

    func fetchGad7Schema() async throws -> WellnessPhqLiteSchemaResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await get("\(AppConfig.Endpoint.wellnessGad7Schema)?locale=\(loc)")
    }

    func submitGad7(answers: [Int]) async throws -> WellnessPhqSubmitResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await post(
            "\(AppConfig.Endpoint.wellnessGad7Submit)?locale=\(loc)",
            body: WellnessPhqSubmitBody(answers: answers)
        )
    }

    func fetchEscalation(message: String = "", phqLiteScore: Int? = nil) async throws -> WellnessEscalationResponse {
        var path = AppConfig.Endpoint.wellnessEscalationLevel
        var query: [String] = []
        if !message.isEmpty,
           let encoded = message.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) {
            query.append("message=\(encoded)")
        }
        if let phqLiteScore {
            query.append("phq_lite_score=\(phqLiteScore)")
        }
        if !query.isEmpty {
            path += "?" + query.joined(separator: "&")
        }
        return try await get(path)
    }

    func fetchReferral(level: String = "L2") async throws -> WellnessReferralResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        let path = "\(AppConfig.Endpoint.wellnessReferral)?locale=\(loc)&level=\(level)"
        return try await get(path)
    }

    func postOutcome(pillar: String, helpful: Int, note: String? = nil) async throws -> WellnessOutcomePostResponse {
        try await post(
            AppConfig.Endpoint.wellnessOutcomes,
            body: WellnessOutcomeRequestBody(pillar: pillar, helpful: helpful, note: note)
        )
    }

    func fetchSessionRecap() async throws -> WellnessSessionRecapResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get("\(AppConfig.Endpoint.wellnessSessionRecap)?locale=\(loc)")
    }

    /// p3-01 — Wellness Loop Engine (triggers → escalation → pillar → agents).
    func fetchSessionLoop(
        message: String = "",
        requestedPillar: String? = nil
    ) async throws -> WellnessSessionLoopResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        var query = ["locale=\(loc)"]
        if !message.isEmpty,
           let encoded = message.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) {
            query.append("message=\(encoded)")
        }
        if let requestedPillar, !requestedPillar.isEmpty,
           let encoded = requestedPillar.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) {
            query.append("requested_pillar=\(encoded)")
        }
        let path = "\(AppConfig.Endpoint.wellnessSessionLoop)?" + query.joined(separator: "&")
        return try await get(path)
    }

    func dismissOutcomePrompt() async throws {
        struct Resp: Codable { let ok: Bool }
        let _: Resp = try await post(AppConfig.Endpoint.wellnessOutcomesDismissPrompt, body: EmptyBody())
    }

    func fetchTraumaCheck(message: String) async throws -> WellnessTraumaCheckResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        let encoded = message.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        return try await get(
            "\(AppConfig.Endpoint.wellnessTraumaCheck)?locale=\(loc)&message=\(encoded)"
        )
    }

    func fetchHubCopy() async throws -> WellnessHubCopyResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get("\(AppConfig.Endpoint.wellnessHubCopy)?locale=\(loc)")
    }

    func fetchStreaks() async throws -> WellnessStreaksPayload {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        let r: WellnessStreaksResponse = try await get("\(AppConfig.Endpoint.wellnessStreaks)?locale=\(loc)")
        return r.streaks
    }

    func fetchWeeklyMeaning() async throws -> WellnessWeeklyMeaningResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get("\(AppConfig.Endpoint.wellnessWeeklyMeaning)?locale=\(loc)")
    }

    func dismissWeeklyMeaning() async throws {
        struct Resp: Codable { let ok: Bool }
        let _: Resp = try await post(AppConfig.Endpoint.wellnessWeeklyMeaningDismiss, body: EmptyBody())
    }

    func fetchFamilyThemes(teenUserId: String) async throws -> WellnessFamilyThemesResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        let encoded = teenUserId.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? teenUserId
        return try await get(
            "\(AppConfig.Endpoint.wellnessFamilyThemes)?teen_user_id=\(encoded)&locale=\(loc)"
        )
    }

    /// p3-16 — parent talk scripts; `useLlm` requires `FEATURE_WELLNESS_PARENT_LLM=1` on server.
    func fetchParentPlaybook(
        topic: String? = nil,
        teenMood: String? = nil,
        useLlm: Bool = true
    ) async throws -> WellnessParentPlaybookResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        var parts = ["locale=\(loc)"]
        if useLlm { parts.append("use_llm=true") }
        if let topic, !topic.isEmpty {
            let enc = topic.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? topic
            parts.append("topic=\(enc)")
        }
        if let teenMood, !teenMood.isEmpty {
            let enc = teenMood.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? teenMood
            parts.append("teen_mood=\(enc)")
        }
        let query = parts.joined(separator: "&")
        return try await get("\(AppConfig.Endpoint.wellnessParentPlaybook)?\(query)")
    }

    func fetchTogetherSession(durationSec: Int = 180) async throws -> WellnessTogetherSession {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        struct Resp: Codable {
            let ok: Bool
            let session: WellnessTogetherSession
        }
        let r: Resp = try await get(
            "\(AppConfig.Endpoint.wellnessTogetherSession)?locale=\(loc)&duration_sec=\(durationSec)"
        )
        return r.session
    }

    func fetchAlliance() async throws -> WellnessAllianceDTO {
        struct Resp: Codable {
            let ok: Bool
            let alliance: WellnessAllianceDTO
        }
        let r: Resp = try await get(AppConfig.Endpoint.wellnessAlliance)
        return r.alliance
    }

    func fetchReflectiveModes() async throws -> WellnessReflectiveModesResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get("\(AppConfig.Endpoint.wellnessReflectiveModes)?locale=\(loc)")
    }

    func fetchMbiLiteSchema() async throws -> WellnessPhqLiteSchemaResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await get("\(AppConfig.Endpoint.wellnessMbiLiteSchema)?locale=\(loc)")
    }

    func submitMbiLite(answers: [Int]) async throws -> WellnessPhqSubmitResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2)
        return try await post(
            "\(AppConfig.Endpoint.wellnessMbiLiteSubmit)?locale=\(loc)",
            body: WellnessPhqSubmitBody(answers: answers)
        )
    }

    func fetchExerciseCatalog(pillar: String) async throws -> WellnessExerciseCatalogResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get(
            "\(AppConfig.Endpoint.wellnessExercisesCatalog)?pillar=\(pillar)&locale=\(loc)"
        )
    }

    func fetchActiveExercise() async throws -> WellnessExerciseActiveResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await get("\(AppConfig.Endpoint.wellnessExercisesActive)?locale=\(loc)")
    }

    func startExercise(pillar: String, exerciseId: String) async throws -> WellnessExerciseStartResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await post(
            "\(AppConfig.Endpoint.wellnessExercisesStart)?locale=\(loc)",
            body: WellnessExerciseStartBody(pillar: pillar, exerciseId: exerciseId)
        )
    }

    func advanceExercise(id: Int, answer: String?) async throws -> WellnessExerciseStartResponse {
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        return try await post(
            "\(AppConfig.Endpoint.wellnessExerciseStep(id))?locale=\(loc)",
            body: WellnessExerciseStepBody(answer: answer)
        )
    }

    func fetchTimeline(days: Int = 14) async throws -> WellnessTimelineResponse {
        try await get("\(AppConfig.Endpoint.wellnessTimeline)?days=\(days)")
    }

    func postDream(text: String, moodTag: String?) async throws {
        struct Resp: Codable { let ok: Bool }
        let _: Resp = try await post(
            AppConfig.Endpoint.wellnessDreams,
            body: WellnessDreamBody(dreamText: text, moodTag: moodTag)
        )
    }

    func fetchDreams() async throws -> WellnessDreamsResponse {
        try await get(AppConfig.Endpoint.wellnessDreams)
    }

    func fetchPremiumEligibility() async throws -> WellnessPremiumEligibilityResponse {
        try await get(AppConfig.Endpoint.wellnessPremiumEligibility)
    }

    func fetchPdfLabels() async throws -> [String: String] {
        struct Resp: Codable {
            let ok: Bool
            let title: String?
            let disclaimer: String?
            let sectionCheckins: String?
            let sectionOutcomes: String?

            enum CodingKeys: String, CodingKey {
                case ok, title, disclaimer
                case sectionCheckins = "section_checkins"
                case sectionOutcomes = "section_outcomes"
            }
        }
        let loc = LocalizationManager.shared.aiResponseLanguageCode.prefix(2).lowercased()
        let r: Resp = try await get("\(AppConfig.Endpoint.wellnessExportPdfLabels)?locale=\(loc)")
        var map: [String: String] = [:]
        if let title = r.title { map["title"] = title }
        if let disclaimer = r.disclaimer { map["disclaimer"] = disclaimer }
        if let s = r.sectionCheckins { map["section_checkins"] = s }
        if let s = r.sectionOutcomes { map["section_outcomes"] = s }
        return map
    }

    func saveValuesCard(valueIds: [String], note: String?) async throws {
        struct Body: Encodable {
            let valueIds: [String]
            let note: String?
            enum CodingKeys: String, CodingKey {
                case valueIds = "value_ids"
                case note
            }
        }
        struct Resp: Codable { let ok: Bool }
        let _: Resp = try await post(
            AppConfig.Endpoint.wellnessValuesCard,
            body: Body(valueIds: Array(valueIds.prefix(2)), note: note)
        )
    }

    private func get<T: Decodable>(_ endpoint: String) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            network.get(endpoint: endpoint, requiresAuth: true) { (result: Result<T, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    private func post<T: Decodable, B: Encodable>(_ endpoint: String, body: B) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            network.post(endpoint: endpoint, body: body, requiresAuth: true) { (result: Result<T, Error>) in
                continuation.resume(with: result)
            }
        }
    }
}

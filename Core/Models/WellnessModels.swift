import Foundation

// MARK: - API DTOs (/api/wellness/*)

struct WellnessPillarsResponse: Codable {
    let pillars: [String]
    let ageBand: String

    enum CodingKeys: String, CodingKey {
        case pillars
        case ageBand = "age_band"
    }
}

struct WellnessPillarSelectBody: Encodable {
    let pillar: String
}

struct WellnessSessionPillarResponse: Codable {
    let ok: Bool
    let settings: WellnessSettingsDTO?
}

struct WellnessSettingsDTO: Codable {
    let userId: String?
    let primaryPillar: String?
    let escalationLevel: String?
    let parentShareAggregate: Int?

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case primaryPillar = "primary_pillar"
        case escalationLevel = "escalation_level"
        case parentShareAggregate = "parent_share_aggregate"
    }
}

struct WellnessSettingsResponse: Codable {
    let settings: WellnessSettingsDTO
    let ageBand: String
    let canEditParentShare: Bool

    enum CodingKeys: String, CodingKey {
        case settings
        case ageBand = "age_band"
        case canEditParentShare = "can_edit_parent_share"
    }
}

struct WellnessConsentResponse: Codable {
    let wellnessAccepted: Bool?
    let wellnessAcceptedAt: String?
    let wellnessDisclaimerVersion: String?
    let psychologicalSupportEnabled: Bool?
    let ageBand: String?
    let hasAccess: Bool?
    let canSetParentToggle: Bool?

    enum CodingKeys: String, CodingKey {
        case wellnessAccepted = "wellness_accepted"
        case wellnessAcceptedAt = "wellness_accepted_at"
        case wellnessDisclaimerVersion = "wellness_disclaimer_version"
        case psychologicalSupportEnabled = "psychological_support_enabled"
        case ageBand = "age_band"
        case hasAccess = "has_access"
        case canSetParentToggle = "can_set_parent_toggle"
    }
}

struct WellnessConsentRequestBody: Encodable {
    let wellnessAccepted: Bool
    let psychologicalSupportEnabled: Bool?

    enum CodingKeys: String, CodingKey {
        case wellnessAccepted = "wellness_accepted"
        case psychologicalSupportEnabled = "psychological_support_enabled"
    }
}

struct WellnessCheckinRequestBody: Encodable {
    let mood: String
    let sleepHours: Double?
    let stressLevel: Int?
    let energyLevel: Int?

    enum CodingKeys: String, CodingKey {
        case mood
        case sleepHours = "sleep_hours"
        case stressLevel = "stress_level"
        case energyLevel = "energy_level"
    }
}

struct WellnessCheckinResponse: Codable {
    let ok: Bool
    let checkin: WellnessCheckinDTO?
}

struct WellnessCheckinDTO: Codable {
    let moodEmoji: String?
    let moodScore: Int?
    let sleepHours: Double?
    let stressLevel: Int?
    let day: String?

    enum CodingKeys: String, CodingKey {
        case moodEmoji = "mood_emoji"
        case moodScore = "mood_score"
        case sleepHours = "sleep_hours"
        case stressLevel = "stress_level"
        case day
    }
}

struct WellnessJournalResponse: Codable {
    let days: Int
    let entries: [WellnessCheckinDTO]
}

struct WellnessTriggersResponse: Codable {
    let lowMoodStreakDays: Int
    let suggestPhqLite: Bool
    let suggestCheckin: Bool
    let reason: String?
    let idleDays: Int?
    let showIdleNudge: Bool?
    let nudgeType: String?
    let nudgeTitle: String?
    let nudgeBody: String?
    let nudgeAction: String?

    enum CodingKeys: String, CodingKey {
        case lowMoodStreakDays = "low_mood_streak_days"
        case suggestPhqLite = "suggest_phq_lite"
        case suggestCheckin = "suggest_checkin"
        case reason
        case idleDays = "idle_days"
        case showIdleNudge = "show_idle_nudge"
        case nudgeType = "nudge_type"
        case nudgeTitle = "title"
        case nudgeBody = "body"
        case nudgeAction = "action"
    }
}

struct WellnessPhqLiteSchemaResponse: Codable {
    let assessmentType: String
    let disclaimer: String
    let questions: [WellnessPhqQuestion]
    let answerOptions: [WellnessPhqAnswerOption]
    let maxScore: Int

    enum CodingKeys: String, CodingKey {
        case assessmentType = "assessment_type"
        case disclaimer
        case questions
        case answerOptions = "answer_options"
        case maxScore = "max_score"
    }
}

struct WellnessPhqQuestion: Codable, Identifiable {
    let id: String
    let text: String
}

struct WellnessPhqAnswerOption: Codable, Identifiable {
    var id: Int { value }
    let value: Int
    let labelKey: String

    enum CodingKeys: String, CodingKey {
        case value
        case labelKey = "label_key"
    }
}

struct WellnessPhqSubmitBody: Encodable {
    let answers: [Int]
}

struct WellnessPhqSubmitResponse: Codable {
    let ok: Bool
    let score: Int
    let severity: String
    let suggestProfessional: Bool
    let disclaimer: String
    let escalationLevel: String?
    let crisisFlag: Bool?

    enum CodingKeys: String, CodingKey {
        case ok
        case score
        case severity
        case suggestProfessional = "suggest_professional"
        case disclaimer
        case escalationLevel = "escalation_level"
        case crisisFlag = "crisis_flag"
    }
}

struct WellnessParentShareBody: Encodable {
    let parentShareAggregate: Bool

    enum CodingKeys: String, CodingKey {
        case parentShareAggregate = "parent_share_aggregate"
    }
}

struct WellnessEscalationResponse: Codable {
    let level: String
    let reason: String?
    let actions: [String]?
    let trauma: WellnessTraumaCheckResponse?
    let alliance: WellnessAllianceDTO?
}

/// p3-01 — snapshot from `GET /api/wellness/session/loop`.
struct WellnessLoopSnapshotDTO: Codable {
    let phase: String
    let primaryPillar: String?
    let escalationLevel: String
    let escalationReason: String?
    let escalationActions: [String]?
    let agentsActive: [String]
    let suggestPhqLite: Bool
    let guardOk: Bool
    let guardReason: String?
    let fatigueMessage: String?

    enum CodingKeys: String, CodingKey {
        case phase
        case primaryPillar = "primary_pillar"
        case escalationLevel = "escalation_level"
        case escalationReason = "escalation_reason"
        case escalationActions = "escalation_actions"
        case agentsActive = "agents_active"
        case suggestPhqLite = "suggest_phq_lite"
        case guardOk = "guard_ok"
        case guardReason = "guard_reason"
        case fatigueMessage = "fatigue_message"
    }
}

struct WellnessSessionLoopResponse: Codable {
    let ok: Bool
    let orchestratorEnabled: Bool
    let loop: WellnessLoopSnapshotDTO

    enum CodingKeys: String, CodingKey {
        case ok
        case orchestratorEnabled = "orchestrator_enabled"
        case loop
    }
}

struct WellnessAllianceDTO: Codable {
    let allianceScore: Int
    let heroEmotion: String
    let trustBand: String?

    enum CodingKeys: String, CodingKey {
        case allianceScore = "alliance_score"
        case heroEmotion = "hero_emotion"
        case trustBand = "trust_band"
    }
}

struct WellnessTraumaCheckResponse: Codable {
    let triggered: Bool
    let level: String?
    let reason: String?
    let message: String?
    let blockJungDeep: Bool?
    let redirectPillar: String?
    let showReferral: Bool?
    let specialistNote: String?
    let referral: WellnessReferralResponse?

    enum CodingKeys: String, CodingKey {
        case triggered
        case level
        case reason
        case message
        case blockJungDeep = "block_jung_deep"
        case redirectPillar = "redirect_pillar"
        case showReferral = "show_referral"
        case specialistNote = "specialist_note"
        case referral
    }
}

struct WellnessReferralLine: Codable, Identifiable {
    let id: String
    let label: String
    let phone: String
    let labelKey: String?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case phone
        case labelKey = "label_key"
    }
}

struct WellnessReferralResponse: Codable {
    let level: String
    let locale: String
    let disclaimer: String
    let lines: [WellnessReferralLine]
}

struct WellnessOutcomeRequestBody: Encodable {
    let pillar: String
    let helpful: Int
    let note: String?

    enum CodingKeys: String, CodingKey {
        case pillar
        case helpful
        case note
    }
}

struct WellnessOutcomePostResponse: Codable {
    let ok: Bool
    let outcome: WellnessOutcomeDTO?
}

struct WellnessOutcomeDTO: Codable {
    let id: Int
    let pillar: String
    let helpful: Int
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case pillar
        case helpful
        case createdAt = "created_at"
    }
}

// MARK: - UI

enum WellnessPillar: String, CaseIterable, Identifiable {
    case cognitive
    case behavioral
    case humanistic
    case jung

    var id: String { rawValue }

    var titleKey: String { "wellness_pillar_\(rawValue)_title" }
    var subtitleKey: String { "wellness_pillar_\(rawValue)_subtitle" }

    static func allowed(for ageBand: String) -> [WellnessPillar] {
        let band = ageBand.lowercased()
        if band == "child" {
            return [.humanistic, .behavioral]
        }
        return WellnessPillar.allCases
    }
}

struct WellnessCheckinDraft: Codable, Equatable {
    var mood: String
    var sleepHours: Double
    var stressLevel: Int
    var savedAt: Date

    static let moods = ["great", "ok", "sad", "anxious", "tired"]
}

struct WellnessExerciseCatalogItem: Codable, Identifiable {
    let exerciseId: String
    let pillar: String
    let totalSteps: Int
    let title: String?
    let introHint: String?

    var id: String { exerciseId }

    enum CodingKeys: String, CodingKey {
        case exerciseId = "exercise_id"
        case pillar
        case totalSteps = "total_steps"
        case title
        case introHint = "intro_hint"
    }
}

struct WellnessExerciseCatalogResponse: Codable {
    let pillar: String
    let exercises: [WellnessExerciseCatalogItem]
}

struct WellnessExerciseSessionDTO: Codable {
    let id: Int
    let pillar: String
    let exerciseId: String
    let stepIndex: Int
    let stepTotal: Int
    let hint: String
    let completed: Bool

    enum CodingKeys: String, CodingKey {
        case id, pillar, hint, completed
        case exerciseId = "exercise_id"
        case stepIndex = "step_index"
        case stepTotal = "step_total"
    }
}

struct WellnessExerciseStartBody: Encodable {
    let pillar: String
    let exerciseId: String

    enum CodingKeys: String, CodingKey {
        case pillar
        case exerciseId = "exercise_id"
    }
}

struct WellnessExerciseStepBody: Encodable {
    let answer: String?
}

struct WellnessExerciseStartResponse: Codable {
    let ok: Bool
    let session: WellnessExerciseSessionDTO
}

struct WellnessExerciseActiveResponse: Codable {
    let active: WellnessExerciseSessionDTO?
}

struct WellnessTimelineCheckin: Codable, Identifiable {
    let day: String
    let moodEmoji: String?
    let moodScore: Int?
    let stressLevel: Int?

    var id: String { day }

    enum CodingKeys: String, CodingKey {
        case day
        case moodEmoji = "mood_emoji"
        case moodScore = "mood_score"
        case stressLevel = "stress_level"
    }
}

struct WellnessTimelineExercise: Codable, Identifiable {
    let id: Int
    let pillar: String
    let exerciseType: String
    let completed: Int

    enum CodingKeys: String, CodingKey {
        case id, pillar, completed
        case exerciseType = "exercise_type"
    }
}

struct WellnessTimelineResponse: Codable {
    let days: Int
    let checkins: [WellnessTimelineCheckin]
    let exercises: [WellnessTimelineExercise]
}

struct WellnessDreamEntry: Codable, Identifiable {
    let id: Int
    let dreamText: String
    let moodTag: String?
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case dreamText = "dream_text"
        case moodTag = "mood_tag"
        case createdAt = "created_at"
    }
}

struct WellnessDreamsResponse: Codable {
    let dreams: [WellnessDreamEntry]
}

struct WellnessDreamBody: Encodable {
    let dreamText: String
    let moodTag: String?

    enum CodingKeys: String, CodingKey {
        case dreamText = "dream_text"
        case moodTag = "mood_tag"
    }
}

struct WellnessOutcomeReminderDTO: Codable {
    let alertType: String?
    let severity: String?
    let title: String?
    let body: String?
    let action: String?
    let pillar: String?

    enum CodingKeys: String, CodingKey {
        case alertType = "alert_type"
        case severity
        case title
        case body
        case action
        case pillar
    }
}

struct WellnessPillarFatigueDTO: Codable {
    let fatigued: Bool?
    let streakPillar: String?
    let streakCount: Int?
    let threshold: Int?
    let suggestedPillar: String?
    let message: String?

    enum CodingKeys: String, CodingKey {
        case fatigued
        case streakPillar = "streak_pillar"
        case streakCount = "streak_count"
        case threshold
        case suggestedPillar = "suggested_pillar"
        case message
    }
}

struct WellnessSessionRecapResponse: Codable {
    let suggestedPillar: String?
    let message: String?
    let continuityMessage: String?
    let outcomeDue: Bool?
    let outcomeReminder: WellnessOutcomeReminderDTO?
    let pillarFatigue: WellnessPillarFatigueDTO?

    enum CodingKeys: String, CodingKey {
        case suggestedPillar = "suggested_pillar"
        case message
        case continuityMessage = "continuity_message"
        case outcomeDue = "outcome_due"
        case outcomeReminder = "outcome_reminder"
        case pillarFatigue = "pillar_fatigue"
    }
}

struct WellnessReflectiveModeItem: Codable, Identifiable {
    let id: String
    let label: String
    let hint: String
    let labelKey: String?
    let hintKey: String?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case hint
        case labelKey = "label_key"
        case hintKey = "hint_key"
    }
}

struct WellnessReflectiveModesResponse: Codable {
    let modes: [WellnessReflectiveModeItem]
}

struct WellnessHubCopyCard: Codable {
    let pillar: String
    let titleKey: String
    let subtitleKey: String

    enum CodingKeys: String, CodingKey {
        case pillar
        case titleKey = "title_key"
        case subtitleKey = "subtitle_key"
    }
}

struct WellnessHubCopyResponse: Codable {
    let variant: String
    let locale: String
    let pillars: [WellnessHubCopyCard]
}

struct WellnessStreaksPayload: Codable {
    let checkinStreak: Int
    let message: String
    let badges: [WellnessBadgeItem]
    let nextThresholdDays: Int?

    enum CodingKeys: String, CodingKey {
        case checkinStreak = "checkin_streak"
        case message
        case badges
        case nextThresholdDays = "next_threshold_days"
    }
}

struct WellnessBadgeItem: Codable, Identifiable {
    let badgeId: String
    let thresholdDays: Int
    let earned: Bool
    let labelKey: String

    var id: String { badgeId }

    enum CodingKeys: String, CodingKey {
        case badgeId = "badge_id"
        case thresholdDays = "threshold_days"
        case earned
        case labelKey = "label_key"
    }
}

struct WellnessStreaksResponse: Codable {
    let ok: Bool
    let streaks: WellnessStreaksPayload
}

struct WellnessWeeklyMeaningResponse: Codable {
    let ok: Bool
    let show: Bool
    let title: String
    let body: String
    let prompt: String
    let suggestedPillar: String
    let durationMinutes: Int

    enum CodingKeys: String, CodingKey {
        case ok
        case show
        case title
        case body
        case prompt
        case suggestedPillar = "suggested_pillar"
        case durationMinutes = "duration_minutes"
    }
}

struct WellnessFamilyThemeItem: Codable, Identifiable {
    let id: String
    let label: String
    let labelKey: String?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case labelKey = "label_key"
    }
}

struct WellnessFamilyAggregate: Codable {
    let daysWithCheckin: Int?
    let avgMoodScore: Double?
    let lowMoodStreakDays: Int?
    let escalationHint: String?
    let message: String?
    let moodTrendLabel: String?

    enum CodingKeys: String, CodingKey {
        case daysWithCheckin = "days_with_checkin"
        case avgMoodScore = "avg_mood_score"
        case lowMoodStreakDays = "low_mood_streak_days"
        case escalationHint = "escalation_hint"
        case message
        case moodTrendLabel = "mood_trend_label"
    }
}

struct WellnessFamilyThemesResponse: Codable {
    let ok: Bool?
    let shared: Bool
    let reason: String?
    let aggregate: WellnessFamilyAggregate?
    let themes: [WellnessFamilyThemeItem]
    let themesDisclaimer: String?

    enum CodingKeys: String, CodingKey {
        case ok
        case shared
        case reason
        case aggregate
        case themes
        case themesDisclaimer = "themes_disclaimer"
    }
}

struct WellnessParentPlaybookPhrase: Codable, Identifiable {
    let id: String
    let text: String
}

struct WellnessParentPlaybookResponse: Codable {
    let ok: Bool?
    let titleKey: String
    let subtitleKey: String
    let phrases: [WellnessParentPlaybookPhrase]
    let llmUsed: Bool?

    enum CodingKeys: String, CodingKey {
        case ok
        case titleKey = "title_key"
        case subtitleKey = "subtitle_key"
        case phrases
        case llmUsed = "llm_used"
    }
}

struct WellnessPremiumEligibilityResponse: Codable {
    let ok: Bool?
    let allowed: Bool?
    let eligible: Bool?
    let reason: String?
    let messageKey: String?
    let subscriptionActive: Bool?

    enum CodingKeys: String, CodingKey {
        case ok, allowed, eligible, reason
        case messageKey = "message_key"
        case subscriptionActive = "subscription_active"
    }

    var isPremiumAllowed: Bool {
        allowed ?? eligible ?? false
    }
}

/// p18-13 — Widget Extension l10n keys (p3-18).
enum WellnessWidgetL10n {
    static let titleKey = "wellness_widget_title"
    static let tapKey = "wellness_widget_tap"
}

/// p18-13 — PDF export string keys (p3-19).
enum WellnessProgressPDFL10n {
    static let titleKey = "wellness_pdf_title"
    static let disclaimerKey = "wellness_pdf_disclaimer"
    static let sectionCheckinsKey = "wellness_pdf_section_checkins"
    static let sectionAssessmentsKey = "wellness_pdf_section_assessments"
    static let sectionOutcomesKey = "wellness_pdf_section_outcomes"
    static let sectionInsightsKey = "wellness_pdf_section_insights"
    static let generatedKey = "wellness_pdf_generated"
    static let shareKey = "wellness_pdf_share"
    static let clinicianTitleKey = "wellness_pdf_clinician_title"
    static let exportSettingsKey = "wellness_settings_export"
}

/// p18-14 — resolve `wellness_*` with `_child` / `_teen` suffix by age band.
enum WellnessAgeL10n {
    static func text(
        _ manager: LocalizationManager,
        key baseKey: String,
        ageBand: String
    ) -> String {
        let band = ageBand.lowercased()
        if band == "child" {
            let childKey = "\(baseKey)_child"
            let value = manager.localized(childKey)
            if value != childKey { return value }
        } else if band == "teen" {
            let teenKey = "\(baseKey)_teen"
            let value = manager.localized(teenKey)
            if value != teenKey { return value }
        }
        return manager.localized(baseKey)
    }
}

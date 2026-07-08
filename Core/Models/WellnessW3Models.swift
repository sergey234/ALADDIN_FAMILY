import Foundation

// MARK: - fws-14 / fws-17 / fws-24 W3 wellness DTOs

struct WellnessSocialGoalsBlock: Codable, Equatable {
    let show: Bool
    let goalKey: String?
    let cta: String?
    let playbookSteps: [String]?
    let reason: String?
    let cooldownHours: Int?

    enum CodingKeys: String, CodingKey {
        case show
        case goalKey = "goal_key"
        case cta
        case playbookSteps = "playbook_steps"
        case reason
        case cooldownHours = "cooldown_hours"
    }
}

struct WellnessCheckinWithSocialResponse: Codable {
    let ok: Bool
    let checkin: WellnessCheckinDTO?
    let socialGoals: WellnessSocialGoalsBlock?

    enum CodingKeys: String, CodingKey {
        case ok
        case checkin
        case socialGoals = "social_goals"
    }
}

struct WellnessExamPlanDTO: Codable, Equatable {
    let examAt: String?
    let title: String?
    let parentDigest: Bool?
    let secondsUntil: Int?
    let phase: String?
    let suggestBreathing: Bool?
    let suggestOneThing: Bool?

    enum CodingKeys: String, CodingKey {
        case examAt = "exam_at"
        case title
        case parentDigest = "parent_digest"
        case secondsUntil = "seconds_until"
        case phase
        case suggestBreathing = "suggest_breathing"
        case suggestOneThing = "suggest_one_thing"
    }
}

struct WellnessExamPlanResponse: Codable {
    let ok: Bool
    let configured: Bool?
    let plan: WellnessExamPlanDTO?
}

struct WellnessExamPlanSaveBody: Encodable {
    let examAt: String
    let title: String?
    let parentDigest: Bool

    enum CodingKeys: String, CodingKey {
        case examAt = "exam_at"
        case title
        case parentDigest = "parent_digest"
    }
}

struct WellnessPsychLibraryMethod: Codable, Identifiable, Equatable {
    let id: String
    let titleKey: String
    let subtitleKey: String
    let heroId: String
    let pillar: String
    let exerciseId: String?
    let route: String

    enum CodingKeys: String, CodingKey {
        case id
        case titleKey = "title_key"
        case subtitleKey = "subtitle_key"
        case heroId = "hero_id"
        case pillar
        case exerciseId = "exercise_id"
        case route
    }
}

struct WellnessPsychLibraryResponse: Codable {
    let ok: Bool
    let version: String?
    let disclaimerKey: String?
    let methods: [WellnessPsychLibraryMethod]

    enum CodingKeys: String, CodingKey {
        case ok
        case version
        case disclaimerKey = "disclaimer_key"
        case methods
    }
}

struct WellnessHabitPlanDTO: Codable, Identifiable, Equatable {
    let id: Int
    let ifThen: String
    let streak: Int?
    let active: Bool?

    enum CodingKeys: String, CodingKey {
        case id
        case ifThen = "if_then"
        case streak
        case active
    }
}

struct WellnessHabitsListResponse: Codable {
    let habits: [WellnessHabitPlanDTO]
}

struct WellnessHabitCreateBody: Encodable {
    let ifThen: String

    enum CodingKeys: String, CodingKey {
        case ifThen = "if_then"
    }
}

struct WellnessSocialNudgeDismissBody: Encodable {
    let goalKey: String

    enum CodingKeys: String, CodingKey {
        case goalKey = "goal_key"
    }
}

struct WellnessSleepStoryDTO: Codable, Identifiable, Equatable {
    let id: String
    let title: String
    let durationMin: Int?
    let audioUrl: String?

    enum CodingKeys: String, CodingKey {
        case id, title
        case durationMin = "duration_min"
        case audioUrl = "audio_url"
    }
}

struct WellnessSleepStoriesResponse: Codable {
    let ok: Bool
    let stories: [WellnessSleepStoryDTO]
}

// MARK: - fws-10/12/16 W4 + W0

struct WellnessStudentModeBody: Encodable {
    let enabled: Bool
}

struct WellnessStudentModeResponse: Codable {
    let ok: Bool
    let studentMode: Bool?
    let ageBand: String?
    let pillars: [String]?

    enum CodingKeys: String, CodingKey {
        case ok
        case studentMode = "student_mode"
        case ageBand = "age_band"
        case pillars
    }
}

struct WellnessDetoxChallengeDTO: Codable, Equatable {
    let active: Bool
    let startedAt: String?
    let daysCompleted: Int
    let daysTotal: Int
    let completedDays: [String]
    let finished: Bool

    enum CodingKeys: String, CodingKey {
        case active
        case startedAt = "started_at"
        case daysCompleted = "days_completed"
        case daysTotal = "days_total"
        case completedDays = "completed_days"
        case finished
    }
}

struct WellnessDetoxWeeklyDTO: Codable, Equatable {
    let weeklyCheckins: Int?
    let messageKey: String?

    enum CodingKeys: String, CodingKey {
        case weeklyCheckins = "weekly_checkins"
        case messageKey = "message_key"
    }
}

struct WellnessDetoxChallengeResponse: Codable {
    let ok: Bool?
    let challenge: WellnessDetoxChallengeDTO?
    let weekly: WellnessDetoxWeeklyDTO?
}

struct WellnessDetoxDayBody: Encodable {
    let underLimit: Bool
    let day: String?

    enum CodingKeys: String, CodingKey {
        case underLimit = "under_limit"
        case day
    }
}

struct WellnessTeenAggregateDTO: Codable, Equatable {
    let shared: Bool?
    let lowMoodStreakDays: Int?
    let detoxDaysCompleted: Int?
    let detoxFinished: Bool?

    enum CodingKeys: String, CodingKey {
        case shared
        case lowMoodStreakDays = "low_mood_streak_days"
        case detoxDaysCompleted = "detox_days_completed"
        case detoxFinished = "detox_finished"
    }
}

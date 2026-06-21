import Foundation

// MARK: - Companion API models (P0)

struct CompanionCharacterDTO: Codable, Identifiable, Equatable {
    let id: String
    let displayName: String
    let tagline: String
    let available: Bool
    let minSubscription: String

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case tagline
        case available
        case minSubscription = "min_subscription"
    }
}

struct CompanionCharactersResponse: Codable {
    let characters: [CompanionCharacterDTO]
}

struct CompanionLifeDomainDTO: Codable, Identifiable, Equatable {
    let id: String
    let label: String
    let starterPrompt: String
    let ageBands: [String]

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case starterPrompt = "starter_prompt"
        case ageBands = "age_bands"
    }
}

struct CompanionLifeDomainsResponse: Codable {
    let domains: [CompanionLifeDomainDTO]
}

struct CompanionAnalyticsEventBody: Encodable {
    let event: String
    let characterId: String?
    let sessionId: String?
    let extra: [String: String]?

    enum CodingKeys: String, CodingKey {
        case event
        case characterId = "character_id"
        case sessionId = "session_id"
        case extra
    }
}

struct CompanionAnalyticsEventResponse: Decodable {
    let recorded: Bool
    let event: String
}

struct CompanionUsageSnapshot: Codable, Equatable {
    let messagesToday: Int
    let messagesDailyCap: Int
    let messagesUsagePercent: Int
    let voiceSecondsToday: Int
    let voiceDailyCapSeconds: Int
    let voiceUsagePercent: Int
    let warnThresholdPercent: Int
    let shouldWarnMessages: Bool
    let shouldWarnVoice: Bool
    let messageLimitReached: Bool
    let voiceLimitReached: Bool

    enum CodingKeys: String, CodingKey {
        case messagesToday = "messages_today"
        case messagesDailyCap = "messages_daily_cap"
        case messagesUsagePercent = "messages_usage_percent"
        case voiceSecondsToday = "voice_seconds_today"
        case voiceDailyCapSeconds = "voice_daily_cap_seconds"
        case voiceUsagePercent = "voice_usage_percent"
        case warnThresholdPercent = "warn_threshold_percent"
        case shouldWarnMessages = "should_warn_messages"
        case shouldWarnVoice = "should_warn_voice"
        case messageLimitReached = "message_limit_reached"
        case voiceLimitReached = "voice_limit_reached"
    }
}

struct CompanionStateResponse: Codable {
    let characterId: String
    let trustScore: Int
    let trustLevel: Int
    let trustLevelName: String
    let emotionDefault: String
    let cosmeticsUnlocked: [String]
    let memoryEnabled: Bool
    let parentConsentMemory: Bool
    let voiceEnabled: Bool
    let nsfwBlocked: Bool
    let usage: CompanionUsageSnapshot?

    enum CodingKeys: String, CodingKey {
        case characterId = "character_id"
        case trustScore = "trust_score"
        case trustLevel = "trust_level"
        case trustLevelName = "trust_level_name"
        case emotionDefault = "emotion_default"
        case cosmeticsUnlocked = "cosmetics_unlocked"
        case memoryEnabled = "memory_enabled"
        case parentConsentMemory = "parent_consent_memory"
        case voiceEnabled = "voice_enabled"
        case nsfwBlocked = "nsfw_blocked"
        case usage
    }
}

struct CompanionLegalSection: Codable, Identifiable, Equatable {
    let id: String
    let title: String
    let body: String

    static func offlineFallback(localizationManager: LocalizationManager) -> [CompanionLegalSection] {
        [
            CompanionLegalSection(
                id: "ai_disclosure",
                title: localizationManager.localized("companion_legal_offline_ai_title"),
                body: localizationManager.localized("companion_legal_offline_ai_body")
            ),
            CompanionLegalSection(
                id: "coppa_152fz",
                title: localizationManager.localized("companion_legal_offline_parent_title"),
                body: localizationManager.localized("companion_legal_offline_parent_body")
            ),
            CompanionLegalSection(
                id: "voice_recognition_primary",
                title: localizationManager.localized("companion_legal_offline_voice_title"),
                body: localizationManager.localized("companion_legal_offline_voice_body")
            ),
            CompanionLegalSection(
                id: "wellness_disclaimer",
                title: localizationManager.localized("companion_legal_offline_wellness_title"),
                body: localizationManager.localized("companion_legal_offline_wellness_body")
            ),
        ]
    }
}

struct CompanionLegalResponse: Codable {
    let version: String
    let locale: String
    let appId: String
    let sections: [CompanionLegalSection]

    enum CodingKeys: String, CodingKey {
        case version
        case locale
        case appId = "app_id"
        case sections
    }
}

struct CompanionAttachmentPayload: Codable {
    let kind: String
    let filename: String
    let mimeType: String?
    let contentB64: String?

    enum CodingKeys: String, CodingKey {
        case kind
        case filename
        case mimeType = "mime_type"
        case contentB64 = "content_b64"
    }
}

struct CompanionChatRequest: Codable {
    let message: String
    let characterId: String
    let context: String
    let responseLanguage: String?
    let sessionId: String?
    let inputMode: String
    let securityExpertMode: Bool?
    let chatMode: String
    let workspaceId: String?
    let attachments: [CompanionAttachmentPayload]
    let wellnessPillar: String?
    let humorPreference: String?

    enum CodingKeys: String, CodingKey {
        case message
        case characterId = "character_id"
        case context
        case responseLanguage = "response_language"
        case sessionId = "session_id"
        case inputMode = "input_mode"
        case securityExpertMode = "security_expert_mode"
        case chatMode = "chat_mode"
        case workspaceId = "workspace_id"
        case attachments
        case wellnessPillar = "wellness_pillar"
        case humorPreference = "humor_preference"
    }
}

struct CompanionTTSResponse: Codable {
    let audioBase64: String
    let contentType: String
    let provider: String
    let cached: Bool
    let durationSeconds: Double?

    enum CodingKeys: String, CodingKey {
        case audioBase64 = "audio_base64"
        case contentType = "content_type"
        case provider
        case cached
        case durationSeconds = "duration_seconds"
    }
}

struct CompanionSTTResponse: Codable {
    let text: String
    let confidence: Double
    let provider: String
    let language: String
    let durationSec: Double?
    let audioRetentionSec: Int

    enum CodingKeys: String, CodingKey {
        case text
        case confidence
        case provider
        case language
        case durationSec = "duration_sec"
        case audioRetentionSec = "audio_retention_sec"
    }
}

struct CompanionTTSRequestBody: Codable {
    let text: String
    let characterId: String
    let locale: String

    enum CodingKeys: String, CodingKey {
        case text
        case characterId = "character_id"
        case locale
    }
}

struct CompanionChatResponse: Codable {
    let response: String
    let characterId: String
    let emotion: String
    let animationHint: String?
    let trustDelta: Int
    let trustScore: Int
    let trustLevel: Int
    let confidence: Double
    let intent: String?
    let companionDomain: String?
    let companionMood: String?
    let nsfwBlocked: Bool
    let cosmeticUnlocked: String?
    let showSocialBridge: Bool?
    let socialBridgeSuggestions: [String]?
    let trustStreakDays: Int?
    let cogsAlert: Bool?
    let chatMode: String?
    let toolsUsed: [String]?
    let suggestedActions: [CompanionSuggestedActionDTO]?

    enum CodingKeys: String, CodingKey {
        case response
        case characterId = "character_id"
        case emotion
        case animationHint = "animation_hint"
        case trustDelta = "trust_delta"
        case trustScore = "trust_score"
        case trustLevel = "trust_level"
        case confidence
        case intent
        case companionDomain = "companion_domain"
        case companionMood = "companion_mood"
        case nsfwBlocked = "nsfw_blocked"
        case cosmeticUnlocked = "cosmetic_unlocked"
        case showSocialBridge = "show_social_bridge"
        case socialBridgeSuggestions = "social_bridge_suggestions"
        case trustStreakDays = "trust_streak_days"
        case cogsAlert = "cogs_alert"
        case chatMode = "chat_mode"
        case toolsUsed = "tools_used"
        case suggestedActions = "suggested_actions"
    }
}

struct CompanionSuggestedActionDTO: Codable, Identifiable, Equatable {
    let id: String
    let title: String
}

struct CompanionWorkspaceDTO: Codable, Identifiable, Equatable {
    let workspaceId: String
    let title: String
    let characterId: String
    let threadId: String?
    let updatedAt: String?

    var id: String { workspaceId }

    enum CodingKeys: String, CodingKey {
        case workspaceId = "workspace_id"
        case title
        case characterId = "character_id"
        case threadId = "thread_id"
        case updatedAt = "updated_at"
    }
}

struct CompanionWorkspacesResponse: Codable {
    let workspaces: [CompanionWorkspaceDTO]
}

struct CompanionWorkspaceCreateBody: Encodable {
    let title: String
    let characterId: String

    enum CodingKeys: String, CodingKey {
        case title
        case characterId = "character_id"
    }
}

struct CompanionCogsResponse: Codable {
    let dailyUsd: Double
    let monthUsd: Double
    let turnsToday: Int
    let alertThresholdUsd: Double
    let alertTriggered: Bool

    enum CodingKeys: String, CodingKey {
        case dailyUsd = "daily_usd"
        case monthUsd = "month_usd"
        case turnsToday = "turns_today"
        case alertThresholdUsd = "alert_threshold_usd"
        case alertTriggered = "alert_triggered"
    }
}

struct CompanionCapabilitiesPayload: Codable {
    let features: [String: CompanionFeatureGate]?
    let subscriptionLevel: String?
    let limits: CompanionLimits?

    enum CodingKeys: String, CodingKey {
        case features
        case subscriptionLevel = "subscription_level"
        case limits
    }
}

struct CompanionFeatureGate: Codable {
    let enabled: Bool?
    let ui: CompanionFeatureUI?
}

struct CompanionFeatureUI: Codable {
    let flags: [String: Bool]
    let characters: [String]?
    /// Server metadata strings: `provider`, `tts_provider`, `hero_visual_tier`, …
    let strings: [String: String]
    /// Server metadata string lists: `chat_modes`, …
    let stringArrays: [String: [String]]
    /// Server metadata integers: `audio_retention_seconds`, …
    let integers: [String: Int]

    init(
        flags: [String: Bool] = [:],
        characters: [String]? = nil,
        strings: [String: String] = [:],
        stringArrays: [String: [String]] = [:],
        integers: [String: Int] = [:]
    ) {
        self.flags = flags
        self.characters = characters
        self.strings = strings
        self.stringArrays = stringArrays
        self.integers = integers
    }

    func flag(_ key: String) -> Bool? {
        flags[key]
    }

    func string(_ key: String) -> String? {
        strings[key]
    }

    func stringArray(_ key: String) -> [String]? {
        stringArrays[key]
    }

    func integer(_ key: String) -> Int? {
        integers[key]
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: DynamicCodingKey.self)
        var parsedFlags: [String: Bool] = [:]
        var parsedCharacters: [String]?
        var parsedStrings: [String: String] = [:]
        var parsedStringArrays: [String: [String]] = [:]
        var parsedIntegers: [String: Int] = [:]

        for key in container.allKeys {
            let name = key.stringValue

            if name == "characters" {
                if let list = try? container.decode([String].self, forKey: key) {
                    parsedCharacters = list
                } else if (try? container.decodeNil(forKey: key)) == true {
                    parsedCharacters = nil
                } else {
                    #if DEBUG
                    print("⚠️ CompanionFeatureUI: unexpected `characters` type")
                    #endif
                }
                continue
            }

            if name == "chat_modes" {
                if let list = try? container.decode([String].self, forKey: key) {
                    parsedStringArrays[name] = list
                } else if (try? container.decodeNil(forKey: key)) == true {
                    continue
                } else {
                    #if DEBUG
                    print("⚠️ CompanionFeatureUI: unexpected `chat_modes` type")
                    #endif
                }
                continue
            }

            if name == "audio_retention_seconds" {
                if let value = try? container.decode(Int.self, forKey: key) {
                    parsedIntegers[name] = value
                } else if let value = try? container.decode(Double.self, forKey: key) {
                    parsedIntegers[name] = Int(value)
                } else if (try? container.decodeNil(forKey: key)) == true {
                    continue
                } else {
                    #if DEBUG
                    print("⚠️ CompanionFeatureUI: unexpected `audio_retention_seconds` type")
                    #endif
                }
                continue
            }

            if name == "provider" || name == "tts_provider" || name == "hero_visual_tier" {
                if let value = try? container.decode(String.self, forKey: key) {
                    parsedStrings[name] = value
                } else if (try? container.decodeNil(forKey: key)) == true {
                    continue
                } else {
                    #if DEBUG
                    print("⚠️ CompanionFeatureUI: unexpected `\(name)` type")
                    #endif
                }
                continue
            }

            if let value = try? container.decode(Bool.self, forKey: key) {
                parsedFlags[name] = value
            } else if let value = try? container.decode(Int.self, forKey: key) {
                parsedFlags[name] = value != 0
            } else if (try? container.decodeNil(forKey: key)) == true {
                continue
            } else {
                #if DEBUG
                print("⚠️ CompanionFeatureUI: unsupported ui key `\(name)`")
                #endif
            }
        }

        flags = parsedFlags
        characters = parsedCharacters
        strings = parsedStrings
        stringArrays = parsedStringArrays
        integers = parsedIntegers
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: DynamicCodingKey.self)
        for (key, value) in flags {
            try container.encode(value, forKey: DynamicCodingKey(key))
        }
        if let characters {
            try container.encode(characters, forKey: DynamicCodingKey("characters"))
        }
        for (key, value) in strings {
            try container.encode(value, forKey: DynamicCodingKey(key))
        }
        for (key, value) in stringArrays {
            try container.encode(value, forKey: DynamicCodingKey(key))
        }
        for (key, value) in integers {
            try container.encode(value, forKey: DynamicCodingKey(key))
        }
    }
}

private struct DynamicCodingKey: CodingKey {
    var stringValue: String
    var intValue: Int?

    init(_ string: String) {
        self.stringValue = string
        self.intValue = nil
    }

    init?(stringValue: String) {
        self.init(stringValue)
    }

    init?(intValue: Int) {
        self.stringValue = "\(intValue)"
        self.intValue = intValue
    }
}

struct CompanionLimits: Codable {
    let maxAiMessages: Int?
    let voiceMinutesMonth: Int?

    enum CodingKeys: String, CodingKey {
        case maxAiMessages = "max_ai_messages"
        case voiceMinutesMonth = "voice_minutes_month"
    }
}

struct CompanionEphemeralTokenResponse: Codable {
    let token: String
    let expiresInSeconds: Int

    enum CodingKeys: String, CodingKey {
        case token
        case expiresInSeconds = "expires_in_seconds"
    }
}

struct CompanionThreadSummary: Codable, Identifiable {
    var id: String { threadId }
    let threadId: String
    let title: String
    let updatedAt: String
    let messageCount: Int
    let characterId: String

    enum CodingKeys: String, CodingKey {
        case threadId = "thread_id"
        case title
        case updatedAt = "updated_at"
        case messageCount = "message_count"
        case characterId = "character_id"
    }

    var updatedAtDisplay: String {
        CompanionThreadSummary.formatUpdatedAt(updatedAt)
    }

    private static func formatUpdatedAt(_ raw: String) -> String {
        let trimmed = String(raw.prefix(19))
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        guard let date = formatter.date(from: trimmed) else { return raw }
        let out = RelativeDateTimeFormatter()
        out.locale = Locale(identifier: "ru_RU")
        out.unitsStyle = .short
        return out.localizedString(for: date, relativeTo: Date())
    }
}

struct CompanionThreadsResponse: Codable {
    let threads: [CompanionThreadSummary]
}

struct CompanionThreadMessage: Codable, Identifiable {
    var id: String { "\(role)-\(createdAt)" }
    let role: String
    let text: String
    let createdAt: String
    let characterId: String?

    enum CodingKeys: String, CodingKey {
        case role
        case text
        case createdAt = "created_at"
        case characterId = "character_id"
    }
}

struct CompanionThreadMessagesResponse: Codable {
    let threadId: String
    let messages: [CompanionThreadMessage]

    enum CodingKeys: String, CodingKey {
        case threadId = "thread_id"
        case messages
    }
}

struct CompanionConsentSettings: Codable, Equatable {
    var memoryEnabled: Bool
    var childCanUseCompanion: Bool
    var allowedCharacters: [String]
    var vedicWisdomEnabled: Bool
    var familyId: String?
    var scope: String?

    enum CodingKeys: String, CodingKey {
        case memoryEnabled = "memory_enabled"
        case childCanUseCompanion = "child_can_use_companion"
        case allowedCharacters = "allowed_characters"
        case vedicWisdomEnabled = "vedic_wisdom_enabled"
        case familyId = "family_id"
        case scope
        case recorded
    }

    init(
        memoryEnabled: Bool = false,
        childCanUseCompanion: Bool = true,
        allowedCharacters: [String] = ["unicorn"],
        vedicWisdomEnabled: Bool = true,
        familyId: String? = nil,
        scope: String? = nil
    ) {
        self.memoryEnabled = memoryEnabled
        self.childCanUseCompanion = childCanUseCompanion
        self.allowedCharacters = allowedCharacters
        self.vedicWisdomEnabled = vedicWisdomEnabled
        self.familyId = familyId
        self.scope = scope
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        memoryEnabled = try c.decodeIfPresent(Bool.self, forKey: .memoryEnabled) ?? false
        childCanUseCompanion = try c.decodeIfPresent(Bool.self, forKey: .childCanUseCompanion) ?? true
        allowedCharacters = try c.decodeIfPresent([String].self, forKey: .allowedCharacters) ?? ["unicorn"]
        vedicWisdomEnabled = try c.decodeIfPresent(Bool.self, forKey: .vedicWisdomEnabled) ?? true
        familyId = try c.decodeIfPresent(String.self, forKey: .familyId)
        scope = try c.decodeIfPresent(String.self, forKey: .scope)
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(memoryEnabled, forKey: .memoryEnabled)
        try c.encode(childCanUseCompanion, forKey: .childCanUseCompanion)
        try c.encode(allowedCharacters, forKey: .allowedCharacters)
        try c.encode(vedicWisdomEnabled, forKey: .vedicWisdomEnabled)
        try c.encodeIfPresent(familyId, forKey: .familyId)
    }
}

struct CompanionConsentRequestBody: Encodable {
    let memoryEnabled: Bool
    let childCanUseCompanion: Bool
    let allowedCharacters: [String]
    let vedicWisdomEnabled: Bool
    let familyId: String?

    enum CodingKeys: String, CodingKey {
        case memoryEnabled = "memory_enabled"
        case childCanUseCompanion = "child_can_use_companion"
        case allowedCharacters = "allowed_characters"
        case vedicWisdomEnabled = "vedic_wisdom_enabled"
        case familyId = "family_id"
    }
}

struct CompanionMemoryItemDTO: Codable, Identifiable {
    var id: String { key }
    let key: String
    let summary: String
    let updatedAt: String

    enum CodingKeys: String, CodingKey {
        case key
        case summary
        case updatedAt = "updated_at"
    }
}

struct CompanionMemoryListResponse: Codable {
    let items: [CompanionMemoryItemDTO]
    let memoryEnabled: Bool
    let itemCount: Int

    enum CodingKeys: String, CodingKey {
        case items
        case memoryEnabled = "memory_enabled"
        case itemCount = "item_count"
    }
}

struct CompanionMemoryExportResponse: Codable {
    let exportedAt: String
    let storageScope: String
    let memoryEnabled: Bool
    let itemCount: Int
    let items: [CompanionMemoryItemDTO]

    enum CodingKeys: String, CodingKey {
        case exportedAt = "exported_at"
        case storageScope = "storage_scope"
        case memoryEnabled = "memory_enabled"
        case itemCount = "item_count"
        case items
    }
}

struct CompanionCosmeticItem: Codable, Identifiable, Equatable {
    let id: String
    let title: String
    let trustLevel: Int
    let unlocked: Bool

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case trustLevel = "trust_level"
        case unlocked
    }
}

struct CompanionCosmeticsResponse: Codable {
    let characterId: String
    let cosmetics: [CompanionCosmeticItem]

    enum CodingKeys: String, CodingKey {
        case characterId = "character_id"
        case cosmetics
    }
}

struct CompanionTeenHumorBody: Encodable {
    let humorPreference: String

    enum CodingKeys: String, CodingKey {
        case humorPreference = "humor_preference"
    }
}

struct CompanionProfileSettings: Codable, Equatable {
    var customInstructions: String
    var personalityPreset: String
    var securityExpertMode: Bool?
    var equippedCosmeticId: String?
    var equippedCosmeticCharacterId: String?
    let storageScope: String?
    let availablePresets: [String]?

    enum CodingKeys: String, CodingKey {
        case customInstructions = "custom_instructions"
        case personalityPreset = "personality_preset"
        case securityExpertMode = "security_expert_mode"
        case equippedCosmeticId = "equipped_cosmetic_id"
        case equippedCosmeticCharacterId = "equipped_cosmetic_character_id"
        case storageScope = "storage_scope"
        case availablePresets = "available_presets"
    }

    static let presetLabels: [String: String] = [
        "friendly": "Дружелюбный",
        "calm": "Спокойный",
        "playful": "Игривый",
        "mentor": "Наставник",
        "witty": "Остроумный"
    ]

    var personalityDisplayName: String {
        Self.presetLabels[personalityPreset] ?? personalityPreset
    }
}

struct CompanionProfileUpdateBody: Encodable {
    let customInstructions: String?
    let personalityPreset: String?
    let securityExpertMode: Bool?
    let equippedCosmeticId: String?
    let equippedCosmeticCharacterId: String?

    enum CodingKeys: String, CodingKey {
        case customInstructions = "custom_instructions"
        case personalityPreset = "personality_preset"
        case securityExpertMode = "security_expert_mode"
        case equippedCosmeticId = "equipped_cosmetic_id"
        case equippedCosmeticCharacterId = "equipped_cosmetic_character_id"
    }
}

struct CompanionEquippedCosmeticBody: Encodable {
    let equippedCosmeticId: String
    let equippedCosmeticCharacterId: String

    enum CodingKeys: String, CodingKey {
        case equippedCosmeticId = "equipped_cosmetic_id"
        case equippedCosmeticCharacterId = "equipped_cosmetic_character_id"
    }
}

struct CompanionMemoryDeleteResponse: Codable {
    let deleted: Bool
    let itemsRemoved: Int
    let memoryEnabled: Bool

    enum CodingKeys: String, CodingKey {
        case deleted
        case itemsRemoved = "items_removed"
        case memoryEnabled = "memory_enabled"
    }
}

struct CompanionFeedbackRequestBody: Encodable {
    let vote: String
    let characterId: String
    let threadId: String?
    let messageId: String?
    let assistantText: String?
    let userQueryText: String?

    enum CodingKeys: String, CodingKey {
        case vote
        case characterId = "character_id"
        case threadId = "thread_id"
        case messageId = "message_id"
        case assistantText = "assistant_text"
        case userQueryText = "user_query_text"
    }
}

struct CompanionFeedbackResponse: Codable {
    let recorded: Bool
    let vote: String
    let rating: Int
    let trustDelta: Int
    let trustScore: Int

    enum CodingKeys: String, CodingKey {
        case recorded
        case vote
        case rating
        case trustDelta = "trust_delta"
        case trustScore = "trust_score"
    }
}

struct CompanionStreamDonePayload: Codable {
    let response: String?
    let characterId: String?
    let emotion: String?
    let trustScore: Int?
    let trustLevel: Int?
    let trustDelta: Int?
    let done: Bool?
    let showSocialBridge: Bool?
    let socialBridgeSuggestions: [String]?
    let trustStreakDays: Int?
    let suggestedActions: [CompanionSuggestedActionDTO]?

    enum CodingKeys: String, CodingKey {
        case response
        case characterId = "character_id"
        case emotion
        case trustScore = "trust_score"
        case trustLevel = "trust_level"
        case trustDelta = "trust_delta"
        case done
        case showSocialBridge = "show_social_bridge"
        case socialBridgeSuggestions = "social_bridge_suggestions"
        case trustStreakDays = "trust_streak_days"
        case suggestedActions = "suggested_actions"
    }

    /// Pseudo-stream when `/stream` is unavailable but `/chat` works.
    static func fromChat(_ chat: CompanionChatResponse) -> CompanionStreamDonePayload {
        CompanionStreamDonePayload(
            response: chat.response,
            characterId: chat.characterId,
            emotion: chat.emotion,
            trustScore: chat.trustScore,
            trustLevel: chat.trustLevel,
            trustDelta: chat.trustDelta,
            done: true,
            showSocialBridge: chat.showSocialBridge,
            socialBridgeSuggestions: chat.socialBridgeSuggestions,
            trustStreakDays: chat.trustStreakDays,
            suggestedActions: chat.suggestedActions
        )
    }
}

struct CompanionChatBubble: Identifiable {
    let id: UUID
    let text: String
    let isUser: Bool
    var feedbackVote: String?
    var suggestedActions: [CompanionSuggestedActionDTO]?

    init(
        id: UUID = UUID(),
        text: String,
        isUser: Bool,
        feedbackVote: String? = nil,
        suggestedActions: [CompanionSuggestedActionDTO]? = nil
    ) {
        self.id = id
        self.text = text
        self.isUser = isUser
        self.feedbackVote = feedbackVote
        self.suggestedActions = suggestedActions
    }
}

enum CompanionHeroEmotion: String {
    case idle
    case happy
    case listening
    case speaking
    case alert
    case comfort
    case celebrate
    case thinking
    case sad
    case playful
    case curious
    case nostalgic
    case excited
}

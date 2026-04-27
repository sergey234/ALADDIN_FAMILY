import Foundation

enum ContentItemType: String, Codable, CaseIterable {
    case game
    case lesson
    case video
    case story
    case song
    case drawing
    case safety
    case career
}

enum ContentAgeBand: String, Codable, CaseIterable {
    case kids_1_6
    case school_7_12
    case teen_13_17
    case youngAdult_18_22
}

struct ContentCategory: Codable, Identifiable, Hashable {
    let id: String
    let titleKey: String
    let icon: String
    let ageBand: ContentAgeBand
}

struct ContentMetadata: Codable, Hashable {
    let locale: String
    let title: String
    let subtitle: String?
    let description: String?
    let tags: [String]
    let estimatedDurationSec: Int?
}

enum ContentDifficultyLevel: String, Codable, CaseIterable {
    case l1
    case l2
    case l3
    case l4
    case l5
}

enum ContentAssessmentType: String, Codable, CaseIterable {
    case quiz
    case scenario
    case creativeOutput
    case guidedPractice
}

enum ContentCognitiveLoad: String, Codable, CaseIterable {
    case low
    case medium
    case high
}

struct ContentLearningOutcomeContract: Codable, Hashable {
    let learningObjective: String
    let targetAgeWindow: String
    let difficultyLevel: ContentDifficultyLevel
    let successCriteria: String
    let assessmentType: ContentAssessmentType
    let estimatedCognitiveLoad: ContentCognitiveLoad
}

struct ContentItem: Codable, Identifiable, Hashable {
    let id: String
    let categoryId: String
    let type: ContentItemType
    let ageBand: ContentAgeBand
    let version: Int
    let metadata: ContentMetadata
    let payloadURL: URL?
    let checksumSHA256: String?
    let isOfflineAvailable: Bool
    let learningOutcomeContract: ContentLearningOutcomeContract?

    init(
        id: String,
        categoryId: String,
        type: ContentItemType,
        ageBand: ContentAgeBand,
        version: Int,
        metadata: ContentMetadata,
        payloadURL: URL?,
        checksumSHA256: String?,
        isOfflineAvailable: Bool,
        learningOutcomeContract: ContentLearningOutcomeContract? = nil
    ) {
        self.id = id
        self.categoryId = categoryId
        self.type = type
        self.ageBand = ageBand
        self.version = version
        self.metadata = metadata
        self.payloadURL = payloadURL
        self.checksumSHA256 = checksumSHA256
        self.isOfflineAvailable = isOfflineAvailable
        self.learningOutcomeContract = learningOutcomeContract
    }
}

struct ContentProgress: Codable, Hashable {
    let contentId: String
    var completionPercent: Double
    var attempts: Int
    var lastOpenedAt: Date?
    var completedAt: Date?
}

struct ContentManifest: Codable, Hashable {
    let manifestVersion: Int
    let generatedAt: Date
    let minSupportedAppVersion: String
    let checksumSHA256: String
    let signature: String?
    let categories: [ContentCategory]
    let items: [ContentItem]
}

struct ContentDeltaPatch: Codable, Hashable {
    let fromVersion: Int
    let toVersion: Int
    let added: [ContentItem]
    let updated: [ContentItem]
    let removedIds: [String]
    let checksumSHA256: String
}


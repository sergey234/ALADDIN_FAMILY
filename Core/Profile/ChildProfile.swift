import Foundation

// MARK: - Phase 7.1 — детский профиль (локальный контур до синка с сервером)

/// Возрастная группа контента / UX (грубая шкала для персонализации).
enum ChildAgeGroup: String, Codable, CaseIterable, Sendable {
    case preschool4to6
    case school7to10
    case tween11to13
    case teen14plus
}

/// Полный локальный профиль ребёнка в семейном приложении.
struct ChildProfile: Codable, Identifiable, Equatable, Sendable {
    var id: UUID
    /// Имя или ник, показываемый в детском интерфейсе.
    var displayName: String
    /// Идентификатор ребёнка на бэкенде (если уже связан).
    var serverUserId: String?
    /// Семейный контур (если известен).
    var familyId: String?
    var dateOfBirth: Date?
    var ageGroup: ChildAgeGroup?
    /// Ключ аватара / emoji из существующего селектора.
    var avatarKey: String?
    /// Локальная версия записи для merge-конфликтов между устройствами.
    var version: Int
    /// Последнее серверное `updatedAt` (если пришло с бэкенда/ростера).
    var lastServerUpdatedAt: Date?
    var createdAt: Date
    var updatedAt: Date

    init(
        id: UUID = UUID(),
        displayName: String,
        serverUserId: String? = nil,
        familyId: String? = nil,
        dateOfBirth: Date? = nil,
        ageGroup: ChildAgeGroup? = nil,
        avatarKey: String? = nil,
        version: Int = 1,
        lastServerUpdatedAt: Date? = nil,
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.displayName = displayName
        self.serverUserId = serverUserId
        self.familyId = familyId
        self.dateOfBirth = dateOfBirth
        self.ageGroup = ageGroup
        self.avatarKey = avatarKey
        self.version = max(1, version)
        self.lastServerUpdatedAt = lastServerUpdatedAt
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

// MARK: - Validation

enum ChildProfileValidationError: LocalizedError, Equatable {
    case emptyDisplayName
    case displayNameTooLong(max: Int)
    case serverUserIdTooLong(max: Int)
    case familyIdTooLong(max: Int)
    case avatarKeyTooLong(max: Int)

    var errorDescription: String? {
        switch self {
        case .emptyDisplayName:
            return "Имя ребёнка не может быть пустым."
        case .displayNameTooLong(let max):
            return "Имя ребёнка не длиннее \(max) символов."
        case .serverUserIdTooLong(let max):
            return "Идентификатор пользователя не длиннее \(max) символов."
        case .familyIdTooLong(let max):
            return "Идентификатор семьи не длиннее \(max) символов."
        case .avatarKeyTooLong(let max):
            return "Ключ аватара не длиннее \(max) символов."
        }
    }
}

extension ChildProfile {
    private enum Limits {
        static let displayName = 80
        static let serverUserId = 128
        static let familyId = 128
        static let avatarKey = 120
    }

    /// Нормализует пробелы и проверяет ограничения. Бросает `ChildProfileValidationError`.
    func validated() throws -> ChildProfile {
        let trimmed = displayName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw ChildProfileValidationError.emptyDisplayName }
        guard trimmed.count <= Limits.displayName else {
            throw ChildProfileValidationError.displayNameTooLong(max: Limits.displayName)
        }
        if let sid = serverUserId, sid.count > Limits.serverUserId {
            throw ChildProfileValidationError.serverUserIdTooLong(max: Limits.serverUserId)
        }
        if let fid = familyId, fid.count > Limits.familyId {
            throw ChildProfileValidationError.familyIdTooLong(max: Limits.familyId)
        }
        if let key = avatarKey, key.count > Limits.avatarKey {
            throw ChildProfileValidationError.avatarKeyTooLong(max: Limits.avatarKey)
        }
        var copy = self
        copy.displayName = trimmed
        return copy
    }
}

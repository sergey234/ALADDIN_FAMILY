import Foundation
import Combine

// MARK: - Phase 7.1 — управление детскими профилями (локально + бэкап)

/// Хранит и обновляет список `ChildProfile` в `UserDefaults`, экспортирует снимок в JSON.
@MainActor
final class ProfileManager: ObservableObject {
    static let shared = ProfileManager()

    private static let storageKey = "aladdin.child_profiles.v1"
    private static let encoder: JSONEncoder = {
        let e = JSONEncoder()
        e.outputFormatting = [.sortedKeys, .prettyPrinted]
        e.dateEncodingStrategy = .iso8601
        return e
    }()

    private static let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        return d
    }()

    @Published private(set) var profiles: [ChildProfile] = []
    /// Последний `family_id`, с которым синхронизировали детский ростер (диагностика / UI).
    @Published private(set) var lastSyncedChildRosterFamilyId: String?
    /// Последняя диагностическая сводка reconcile-шагов roster/profile sync.
    @Published private(set) var lastChildRosterReconcileSummary: String?
    @Published private(set) var lastChildRosterConflictCount: Int = 0
    @Published private(set) var lastChildRosterMergeStrategy: ChildRosterReconcilePolicy.MergeStrategy = .latestUpdatedAt
    @Published private(set) var lastDataRightsActionSummary: String?

    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        loadFromStorage()
    }

    func profile(id: UUID) -> ChildProfile? {
        profiles.first { $0.id == id }
    }

    /// Добавить или заменить профиль с тем же `id`.
    func upsert(_ profile: ChildProfile) throws {
        let normalized = try profile.validated()
        var toStore = normalized
        if let idx = profiles.firstIndex(where: { $0.id == normalized.id }) {
            toStore.createdAt = profiles[idx].createdAt
            toStore.version = max(1, profiles[idx].version) + 1
        } else {
            toStore.createdAt = normalized.createdAt
            toStore.version = max(1, normalized.version)
        }
        toStore.updatedAt = Date()
        if let idx = profiles.firstIndex(where: { $0.id == toStore.id }) {
            profiles[idx] = toStore
        } else {
            profiles.append(toStore)
        }
        persist()
    }

    func remove(id: UUID) {
        profiles.removeAll { $0.id == id }
        persist()
    }

    func replaceAll(_ list: [ChildProfile]) throws {
        var next: [ChildProfile] = []
        next.reserveCapacity(list.count)
        let now = Date()
        for p in list {
            var v = try p.validated()
            v.updatedAt = now
            v.version = max(1, v.version)
            next.append(v)
        }
        profiles = next
        persist()
    }

    // MARK: - Family roster (Phase 7.2)

    /// Обновляет локальные `ChildProfile` из ответа `/family/members` (роли `child` / `teenager` / `teen`).
    /// - Parameters:
    ///   - members: полный или частичный список с сервера.
    ///   - familyId: канонический идентификатор семьи (если известен).
    ///   - removeMissingServerLinkedChildren: при `true` удаляет профили с `serverUserId`, которых нет в переданном списке детей (не трогает записи без `serverUserId`).
    func syncChildRosterFromServer(
        members: [FamilyMemberResponse],
        familyId: String?,
        removeMissingServerLinkedChildren: Bool
    ) {
        let fid = familyId.flatMap { $0.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty }
        lastSyncedChildRosterFamilyId = fid
        let reconcileResult = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: profiles,
            serverMembers: members,
            familyId: fid,
            removeMissingServerLinkedChildren: removeMissingServerLinkedChildren,
            mergeStrategy: .latestUpdatedAt
        )

        do {
            try replaceAll(reconcileResult.profiles)
        } catch {
            print("⚠️ ProfileManager.syncChildRosterFromServer reconcile failed: \(error.localizedDescription)")
            return
        }

        lastChildRosterReconcileSummary = reconcileResult.summary
        lastChildRosterConflictCount = reconcileResult.conflicts
        lastChildRosterMergeStrategy = reconcileResult.mergeStrategy
        print("🔄 Child roster reconcile: \(reconcileResult.summary)")
    }

    @discardableResult
    func resolveChildRosterConflicts(
        members: [FamilyMemberResponse],
        familyId: String?,
        prefer strategy: ChildRosterReconcilePolicy.MergeStrategy,
        removeMissingServerLinkedChildren: Bool
    ) -> Bool {
        let fid = familyId.flatMap { $0.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty }
        let reconcileResult = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: profiles,
            serverMembers: members,
            familyId: fid,
            removeMissingServerLinkedChildren: removeMissingServerLinkedChildren,
            mergeStrategy: strategy
        )
        do {
            try replaceAll(reconcileResult.profiles)
            lastChildRosterReconcileSummary = reconcileResult.summary
            lastChildRosterConflictCount = reconcileResult.conflicts
            lastChildRosterMergeStrategy = reconcileResult.mergeStrategy
            return true
        } catch {
            print("⚠️ resolveChildRosterConflicts failed: \(error.localizedDescription)")
            return false
        }
    }

    // MARK: - Backup / restore

    struct BackupEnvelope: Codable, Sendable {
        var schemaVersion: Int
        var exportedAt: Date
        var profiles: [ChildProfile]
    }

    /// JSON для ручного экспорта / шаринга родителю (без облака).
    func exportBackupData() throws -> Data {
        let env = BackupEnvelope(schemaVersion: 1, exportedAt: Date(), profiles: profiles)
        return try Self.encoder.encode(env)
    }

    /// Импорт из `exportBackupData()`; при `merge: false` полностью заменяет список.
    func importBackup(data: Data, merge: Bool = false) throws {
        let env = try Self.decoder.decode(BackupEnvelope.self, from: data)
        guard env.schemaVersion == 1 else {
            throw ProfileManagerError.unsupportedBackupVersion(env.schemaVersion)
        }
        if merge {
            for p in env.profiles {
                try upsert(p)
            }
        } else {
            try replaceAll(env.profiles)
        }
    }

    /// Копия в Documents для восстановления после переустановки (опционально).
    func writeBackupFileToDocuments() throws -> URL {
        let data = try exportBackupData()
        let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        let url = dir.appendingPathComponent("child_profiles_backup.json", isDirectory: false)
        try data.write(to: url, options: [.atomic])
        return url
    }

    // MARK: - Data rights (DSAR-style child export/delete)

    struct ChildDataRightsPackage: Codable, Sendable {
        var schemaVersion: Int
        var exportedAt: Date
        var familyId: String?
        var childProfiles: [ChildProfile]
    }

    func exportChildDataRightsPackage(familyId: String? = nil) throws -> Data {
        let pkg = ChildDataRightsPackage(
            schemaVersion: 1,
            exportedAt: Date(),
            familyId: familyId,
            childProfiles: profiles
        )
        let data = try Self.encoder.encode(pkg)
        lastDataRightsActionSummary = "exported_profiles=\(profiles.count)"
        return data
    }

    @discardableResult
    func deleteChildData(serverUserId: String) -> Bool {
        let normalized = serverUserId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else { return false }
        let before = profiles.count
        profiles.removeAll { ($0.serverUserId ?? "").trimmingCharacters(in: .whitespacesAndNewlines) == normalized }
        let removed = max(0, before - profiles.count)
        if removed > 0 {
            persist()
            lastDataRightsActionSummary = "deleted_profiles=\(removed) serverUserId=\(normalized)"
            return true
        }
        return false
    }

    // MARK: - Private

    private func loadFromStorage() {
        guard let data = defaults.data(forKey: Self.storageKey) else {
            profiles = []
            return
        }
        if let decoded = try? Self.decoder.decode([ChildProfile].self, from: data) {
            profiles = decoded
        } else {
            profiles = []
        }
    }

    private func persist() {
        if let data = try? Self.encoder.encode(profiles) {
            defaults.set(data, forKey: Self.storageKey)
        }
    }
}

private extension String {
    var nilIfEmpty: String? {
        let t = trimmingCharacters(in: .whitespacesAndNewlines)
        return t.isEmpty ? nil : t
    }
}

enum ProfileManagerError: LocalizedError {
    case unsupportedBackupVersion(Int)

    var errorDescription: String? {
        switch self {
        case .unsupportedBackupVersion(let v):
            return "Неподдерживаемая версия бэкапа профилей: \(v)."
        }
    }
}

import Foundation

/// Shared App Group payload for Call Directory extension (af-4-02 / af-m2).
enum AntifakeCallDirectoryConstants {
    static let appGroupId = "group.com.aladdin.family"
    static let snapshotKey = "antifake_call_directory_v1"
    static let backupSnapshotKey = "antifake_call_directory_v1_backup"
    static let extensionBundleId = "family.aladdin.ios.ALADDINCallDirectory"
}

struct AntifakeCallDirectorySnapshot: Codable, Equatable {
    var identifiedNumbers: [AntifakeCallDirectoryIdentifiedEntry]
    var blockedNumbers: [Int64]
    var updatedAt: Date

    static let empty = AntifakeCallDirectorySnapshot(
        identifiedNumbers: [],
        blockedNumbers: [],
        updatedAt: .distantPast
    )
}

struct AntifakeCallDirectoryIdentifiedEntry: Codable, Equatable {
    let phoneNumber: Int64
    let label: String
}

enum AntifakeCallDirectoryStore {
    private static var defaults: UserDefaults? {
        UserDefaults(suiteName: AntifakeCallDirectoryConstants.appGroupId)
    }

    static func load() -> AntifakeCallDirectorySnapshot {
        guard let defaults,
              let data = defaults.data(forKey: AntifakeCallDirectoryConstants.snapshotKey),
              let snapshot = try? JSONDecoder().decode(AntifakeCallDirectorySnapshot.self, from: data)
        else {
            return .empty
        }
        return snapshot
    }

    /// C-10: backup current snapshot before replacing; restore on extension reload failure.
    static func saveReplacing(_ snapshot: AntifakeCallDirectorySnapshot) {
        guard let defaults else { return }
        if let current = defaults.data(forKey: AntifakeCallDirectoryConstants.snapshotKey) {
            defaults.set(current, forKey: AntifakeCallDirectoryConstants.backupSnapshotKey)
        }
        var normalized = snapshot
        normalized.identifiedNumbers = normalized.identifiedNumbers
            .sorted { $0.phoneNumber < $1.phoneNumber }
        normalized.blockedNumbers = Array(Set(normalized.blockedNumbers)).sorted()
        guard let data = try? JSONEncoder().encode(normalized) else { return }
        defaults.set(data, forKey: AntifakeCallDirectoryConstants.snapshotKey)
    }

    @discardableResult
    static func restoreBackupSnapshot() -> Bool {
        guard let defaults,
              let backup = defaults.data(forKey: AntifakeCallDirectoryConstants.backupSnapshotKey)
        else {
            return false
        }
        defaults.set(backup, forKey: AntifakeCallDirectoryConstants.snapshotKey)
        return true
    }

    static func save(_ snapshot: AntifakeCallDirectorySnapshot) {
        saveReplacing(snapshot)
    }

    /// E.164 digits only, e.g. +7 (900) → 79001234567
    static func parsePhoneNumber(_ raw: String) -> Int64? {
        let digits = raw.filter(\.isNumber)
        guard digits.count >= 10, digits.count <= 15 else { return nil }
        return Int64(digits)
    }

    static func mergeIdentified(numbers: [(Int64, String)]) {
        var snapshot = load()
        var map = Dictionary(uniqueKeysWithValues: snapshot.identifiedNumbers.map { ($0.phoneNumber, $0) })
        for (phone, label) in numbers {
            map[phone] = AntifakeCallDirectoryIdentifiedEntry(phoneNumber: phone, label: label)
        }
        snapshot.identifiedNumbers = map.values.sorted { $0.phoneNumber < $1.phoneNumber }
        saveReplacing(snapshot)
    }

    static func mergeBlocked(numbers: [Int64]) {
        var snapshot = load()
        snapshot.blockedNumbers = Array(Set(snapshot.blockedNumbers + numbers)).sorted()
        saveReplacing(snapshot)
    }

    /// C-09: merge delta payload into existing local snapshot.
    static func mergeDelta(
        existing: AntifakeCallDirectorySnapshot,
        identified: [AntifakeCallDirectoryIdentifiedEntry],
        blocked: [Int64],
        serverUpdatedAt: Date
    ) -> AntifakeCallDirectorySnapshot {
        var idMap = Dictionary(uniqueKeysWithValues: existing.identifiedNumbers.map { ($0.phoneNumber, $0) })
        for entry in identified {
            idMap[entry.phoneNumber] = entry
        }
        var blockedSet = Set(existing.blockedNumbers)
        blockedSet.formUnion(blocked)
        for phone in blocked {
            idMap.removeValue(forKey: phone)
        }
        return AntifakeCallDirectorySnapshot(
            identifiedNumbers: idMap.values.sorted { $0.phoneNumber < $1.phoneNumber },
            blockedNumbers: Array(blockedSet).sorted(),
            updatedAt: serverUpdatedAt
        )
    }

    static func clear() {
        guard let defaults else { return }
        defaults.removeObject(forKey: AntifakeCallDirectoryConstants.snapshotKey)
        defaults.removeObject(forKey: AntifakeCallDirectoryConstants.backupSnapshotKey)
    }

    /// N-03: drop synced scam numbers from App Group on account delete.
    static func clearForAccountDelete() {
        clear()
    }
}

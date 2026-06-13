import Foundation

/// Shared App Group payload for Call Directory extension (af-4-02 / af-m2).
enum AntifakeCallDirectoryConstants {
    static let appGroupId = "group.com.aladdin.family"
    static let snapshotKey = "antifake_call_directory_v1"
    static let extensionBundleId = "family.aladdin.ios.ALADDINCallDirectory"
    static let identificationLabel = "Возможный мошенник?"
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

    static func save(_ snapshot: AntifakeCallDirectorySnapshot) {
        guard let defaults else { return }
        var normalized = snapshot
        normalized.identifiedNumbers = normalized.identifiedNumbers
            .sorted { $0.phoneNumber < $1.phoneNumber }
        normalized.blockedNumbers = Array(Set(normalized.blockedNumbers)).sorted()
        normalized.updatedAt = Date()
        guard let data = try? JSONEncoder().encode(normalized) else { return }
        defaults.set(data, forKey: AntifakeCallDirectoryConstants.snapshotKey)
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
        save(snapshot)
    }

    static func mergeBlocked(numbers: [Int64]) {
        var snapshot = load()
        snapshot.blockedNumbers = Array(Set(snapshot.blockedNumbers + numbers)).sorted()
        save(snapshot)
    }
}

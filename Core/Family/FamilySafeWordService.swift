import Foundation

/// fws-01: local Keychain cache + `/api/family/safe-word` sync.
@MainActor
final class FamilySafeWordService: ObservableObject {
    static let shared = FamilySafeWordService()

    @Published private(set) var isConfiguredLocally = false
    @Published private(set) var isConfiguredOnServer = false
    @Published private(set) var lastUpdatedAt: String?

    private let keychain = KeychainManager.shared

    private init() {
        refreshLocalStatus()
    }

    func refreshLocalStatus(familyId: String? = nil) {
        let fid = resolvedFamilyId(explicit: familyId)
        guard !fid.isEmpty, loadRecord(familyId: fid) != nil else {
            isConfiguredLocally = false
            return
        }
        isConfiguredLocally = true
    }

    func refreshServerStatus() async {
        let result: Result<FamilySafeWordStatusResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getFamilySafeWordStatus { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            isConfiguredOnServer = payload.configured
            lastUpdatedAt = payload.updatedAt
        case .failure:
            break
        }
    }

    func savePhraseLocally(_ phrase: String, familyId: String? = nil) throws {
        let fid = resolvedFamilyId(explicit: familyId)
        guard !fid.isEmpty else { throw FamilySafeWordError.noFamily }
        if let code = FamilySafeWordHasher.validatePhrase(phrase) {
            throw FamilySafeWordError.validation(code)
        }
        let hashed = FamilySafeWordHasher.hashPhrase(phrase)
        let record = FamilySafeWordLocalRecord(
            saltHex: hashed.saltHex,
            hashHex: hashed.hashHex,
            updatedAt: ISO8601DateFormatter().string(from: Date())
        )
        guard let data = try? JSONEncoder().encode(record) else {
            throw FamilySafeWordError.persistenceFailed
        }
        keychain.save(data, scopedKey: Self.keychainAccount(familyId: fid))
        isConfiguredLocally = true
    }

    func verifyLocally(_ phrase: String, familyId: String? = nil) -> Bool {
        let fid = resolvedFamilyId(explicit: familyId)
        guard let record = loadRecord(familyId: fid) else { return false }
        return FamilySafeWordHasher.verifyPhrase(phrase, saltHex: record.saltHex, hashHex: record.hashHex)
    }

    func setPhraseOnServer(_ phrase: String) async throws {
        if let code = FamilySafeWordHasher.validatePhrase(phrase) {
            throw FamilySafeWordError.validation(code)
        }
        let result: Result<FamilySafeWordSetResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.setFamilySafeWord(phrase: phrase) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            isConfiguredOnServer = payload.configured
            lastUpdatedAt = payload.updatedAt
        case .failure(let error):
            throw error
        }
    }

    func verifyOnServer(_ phrase: String, context: String = "antifake") async -> FamilySafeWordVerifyResult {
        let result: Result<FamilySafeWordVerifyResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.verifyFamilySafeWord(phrase: phrase, context: context) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            return FamilySafeWordVerifyResult(
                configured: payload.configured,
                match: payload.match,
                parentsNotified: payload.parentsNotified ?? 0
            )
        case .failure:
            let localMatch = verifyLocally(phrase)
            return FamilySafeWordVerifyResult(configured: isConfiguredLocally, match: localMatch, parentsNotified: 0)
        }
    }

    func clearLocal(familyId: String? = nil) {
        let fid = resolvedFamilyId(explicit: familyId)
        keychain.delete(scopedKey: Self.keychainAccount(familyId: fid))
        isConfiguredLocally = false
    }

    private func loadRecord(familyId: String) -> FamilySafeWordLocalRecord? {
        guard let data = keychain.loadData(scopedKey: Self.keychainAccount(familyId: familyId)),
              let record = try? JSONDecoder().decode(FamilySafeWordLocalRecord.self, from: data) else {
            return nil
        }
        return record
    }

    private func resolvedFamilyId(explicit: String?) -> String {
        let trimmed = (explicit ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty { return trimmed }
        return (UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private static func keychainAccount(familyId: String) -> String {
        "family_safe_word_v1_\(familyId)"
    }
}

struct FamilySafeWordLocalRecord: Codable, Equatable {
    let saltHex: String
    let hashHex: String
    let updatedAt: String?
}

struct FamilySafeWordStatusResponse: Codable, Equatable {
    let familyId: String?
    let configured: Bool
    let updatedAt: String?
    let updatedByUserId: Int?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case configured
        case updatedAt = "updated_at"
        case updatedByUserId = "updated_by_user_id"
    }
}

struct FamilySafeWordSetResponse: Codable, Equatable {
    let familyId: String?
    let configured: Bool
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case configured
        case updatedAt = "updated_at"
    }
}

struct FamilySafeWordVerifyResponse: Codable, Equatable {
    let familyId: String?
    let configured: Bool
    let match: Bool
    let parentsNotified: Int?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case configured
        case match
        case parentsNotified = "parents_notified"
    }
}

struct FamilySafeWordVerifyResult: Equatable {
    let configured: Bool
    let match: Bool
    let parentsNotified: Int
}

enum FamilySafeWordError: LocalizedError {
    case noFamily
    case validation(String)
    case persistenceFailed
    case parentGateFailed

    var errorDescription: String? {
        switch self {
        case .noFamily: return "no_family"
        case .validation(let code): return code
        case .persistenceFailed: return "persistence_failed"
        case .parentGateFailed: return "parent_gate_failed"
        }
    }
}

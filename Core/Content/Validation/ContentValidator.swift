import Foundation
import CryptoKit

final class ContentValidator {
    static let shared = ContentValidator()

    private init() {}

    func validateManifest(_ manifest: ContentManifest) -> Bool {
        guard !manifest.items.isEmpty else { return false }
        guard manifest.manifestVersion > 0 else { return false }
        guard ContentExperienceResolver.shared.supportsAllKnownTypes() else { return false }
        guard manifest.items.allSatisfy({ ContentExperienceResolver.shared.isRoutable($0) }) else { return false }
        guard validateCatalogIntegrity(manifest) else { return false }
        return true
    }

    func validateChecksum(data: Data, expectedSHA256: String) -> Bool {
        let digest = SHA256.hash(data: data)
        let hash = digest.compactMap { String(format: "%02x", $0) }.joined()
        return hash.caseInsensitiveCompare(expectedSHA256) == .orderedSame
    }

    /// ECDSA P-256 over manifest payload; fail-closed on parse/verify errors.
    func verifySignature(payload: Data, signatureBase64: String, publicKeyBase64: String) -> Bool {
        guard !payload.isEmpty else { return false }
        guard !signatureBase64.isEmpty, !publicKeyBase64.isEmpty else { return false }
        guard
            let signatureData = Data(base64Encoded: signatureBase64),
            let publicKeyData = Data(base64Encoded: publicKeyBase64)
        else {
            return false
        }

        do {
            let publicKey = try P256.Signing.PublicKey(rawRepresentation: publicKeyData)
            if let derSignature = try? P256.Signing.ECDSASignature(derRepresentation: signatureData) {
                return publicKey.isValidSignature(derSignature, for: payload)
            }
            let rawSignature = try P256.Signing.ECDSASignature(rawRepresentation: signatureData)
            return publicKey.isValidSignature(rawSignature, for: payload)
        } catch {
            return false
        }
    }

    private func validateCatalogIntegrity(_ manifest: ContentManifest) -> Bool {
        // category IDs: non-empty + unique
        let categoryIds = manifest.categories.map { $0.id.trimmingCharacters(in: .whitespacesAndNewlines) }
        guard categoryIds.allSatisfy({ !$0.isEmpty }) else { return false }
        guard Set(categoryIds).count == categoryIds.count else { return false }

        // item IDs: non-empty + unique
        let itemIds = manifest.items.map { $0.id.trimmingCharacters(in: .whitespacesAndNewlines) }
        guard itemIds.allSatisfy({ !$0.isEmpty }) else { return false }
        guard Set(itemIds).count == itemIds.count else { return false }

        // metadata quality + category mapping
        let categorySet = Set(categoryIds)
        for item in manifest.items {
            guard categorySet.contains(item.categoryId) else { return false }
            guard !item.metadata.locale.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }
            guard !item.metadata.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }
            if let duration = item.metadata.estimatedDurationSec, duration <= 0 { return false }
            guard validateLearningOutcomeContract(item.learningOutcomeContract) else { return false }
        }

        // density gate: each category must have at least N items
        var counts: [String: Int] = [:]
        for item in manifest.items {
            counts[item.categoryId, default: 0] += 1
        }
        let minItems = max(1, AppConfig.contentCatalogMinItemsPerCategory)
        for categoryId in categoryIds {
            if counts[categoryId, default: 0] < minItems {
                return false
            }
        }

        return true
    }

    private func validateLearningOutcomeContract(_ contract: ContentLearningOutcomeContract?) -> Bool {
        // P2-001 strategy: contract is currently optional for backward compatibility,
        // but if provided, it must be complete and non-empty.
        guard let contract else { return true }
        guard !contract.learningObjective.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }
        guard !contract.targetAgeWindow.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }
        guard !contract.successCriteria.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }
        return true
    }
}


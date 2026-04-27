import Foundation

/// Канонические UTF-8 JSON байты для ECDSA P-256 подписи манифеста (G3 / W1-3).
/// Поле `signature` **не** входит в тело; `categories` и `items` сортируются по `id` для детерминизма.
enum ContentManifestSigning {

    private struct SigningBody: Codable {
        let manifestVersion: Int
        let generatedAt: Date
        let minSupportedAppVersion: String
        let checksumSHA256: String
        let categories: [ContentCategory]
        let items: [ContentItem]
    }

    static func canonicalSigningData(for manifest: ContentManifest) throws -> Data {
        let body = SigningBody(
            manifestVersion: manifest.manifestVersion,
            generatedAt: manifest.generatedAt,
            minSupportedAppVersion: manifest.minSupportedAppVersion,
            checksumSHA256: manifest.checksumSHA256,
            categories: manifest.categories.sorted { $0.id < $1.id },
            items: manifest.items.sorted { $0.id < $1.id }
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
        encoder.dateEncodingStrategy = .iso8601
        return try encoder.encode(body)
    }
}

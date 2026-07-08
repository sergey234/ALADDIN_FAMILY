import Foundation
import CommonCrypto

/// fws-01: PBKDF2-SHA256 — must match `family_safe_word_crypto.py` on the server.
enum FamilySafeWordHasher {
    private static let iterations: UInt32 = 100_000
    private static let keyLength = 32
    private static let saltLength = 16

    static func normalizePhrase(_ phrase: String) -> String {
        let trimmed = phrase.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return trimmed
            .split(whereSeparator: \.isWhitespace)
            .joined(separator: " ")
    }

    static func validatePhrase(_ phrase: String) -> String? {
        let normalized = normalizePhrase(phrase)
        if normalized.count < 4 { return "phrase_too_short" }
        if normalized.count > 120 { return "phrase_too_long" }
        if normalized.split(separator: " ").count < 2 { return "phrase_need_two_words" }
        return nil
    }

    static func hashPhrase(_ phrase: String, saltHex: String? = nil) -> (saltHex: String, hashHex: String) {
        let normalized = normalizePhrase(phrase)
        let saltData: Data
        if let saltHex, let decoded = Data(hexString: saltHex) {
            saltData = decoded
        } else {
            var bytes = [UInt8](repeating: 0, count: saltLength)
            _ = SecRandomCopyBytes(kSecRandomDefault, saltLength, &bytes)
            saltData = Data(bytes)
        }
        let hashData = pbkdf2SHA256(password: normalized, salt: saltData)
        return (saltData.hexString, hashData.hexString)
    }

    static func verifyPhrase(_ phrase: String, saltHex: String, hashHex: String) -> Bool {
        let candidate = hashPhrase(phrase, saltHex: saltHex).hashHex
        return candidate.lowercased() == hashHex.lowercased()
    }

    private static func pbkdf2SHA256(password: String, salt: Data) -> Data {
        let passwordData = Data(password.utf8)
        var derived = Data(count: keyLength)
        let status = derived.withUnsafeMutableBytes { derivedBytes in
            salt.withUnsafeBytes { saltBytes in
                passwordData.withUnsafeBytes { passwordBytes in
                    CCKeyDerivationPBKDF(
                        CCPBKDFAlgorithm(kCCPBKDF2),
                        passwordBytes.baseAddress?.assumingMemoryBound(to: Int8.self),
                        passwordData.count,
                        saltBytes.baseAddress?.assumingMemoryBound(to: UInt8.self),
                        salt.count,
                        CCPseudoRandomAlgorithm(kCCPRFHmacAlgSHA256),
                        iterations,
                        derivedBytes.baseAddress?.assumingMemoryBound(to: UInt8.self),
                        keyLength
                    )
                }
            }
        }
        guard status == kCCSuccess else {
            return Data(repeating: 0, count: keyLength)
        }
        return derived
    }
}

private extension Data {
    init?(hexString: String) {
        let cleaned = hexString.trimmingCharacters(in: .whitespacesAndNewlines)
        guard cleaned.count.isMultiple(of: 2) else { return nil }
        var data = Data(capacity: cleaned.count / 2)
        var index = cleaned.startIndex
        while index < cleaned.endIndex {
            let next = cleaned.index(index, offsetBy: 2)
            guard next <= cleaned.endIndex else { return nil }
            let byte = cleaned[index..<next]
            guard let value = UInt8(byte, radix: 16) else { return nil }
            data.append(value)
            index = next
        }
        self = data
    }

    var hexString: String {
        map { String(format: "%02x", $0) }.joined()
    }
}

import Foundation

/// D3.1 — initials circle for family strip / member card (no 3D).
enum PayPainsMemberInitials {
    static func from(name: String, fallbackEmoji: String? = nil) -> String {
        let cleaned = name
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "MEM_", with: "")
        let parts = cleaned
            .split(whereSeparator: { $0.isWhitespace || $0 == "-" || $0 == "_" })
            .map(String.init)
            .filter { !$0.isEmpty && !$0.hasPrefix("MEM") }

        if parts.count >= 2 {
            let a = parts[0].prefix(1)
            let b = parts[1].prefix(1)
            let pair = "\(a)\(b)".uppercased()
            if pair.unicodeScalars.allSatisfy({ CharacterSet.letters.contains($0) || CharacterSet.decimalDigits.contains($0) }) {
                return pair
            }
        }
        if let first = parts.first, let ch = first.first {
            let s = String(ch).uppercased()
            if s.unicodeScalars.allSatisfy({ CharacterSet.letters.contains($0) || CharacterSet.decimalDigits.contains($0) }) {
                return s
            }
        }
        if let emoji = fallbackEmoji?.trimmingCharacters(in: .whitespacesAndNewlines), !emoji.isEmpty {
            return String(emoji.prefix(1))
        }
        return "?"
    }
}

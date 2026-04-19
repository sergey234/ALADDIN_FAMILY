import Foundation

/// Разбор ссылок привязки устройства (`aladdin://bind?token=…`, при необходимости — полный URL в строке).
enum DevicePairingLinkParser {
    static func extractToken(from url: URL) -> String? {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false) else { return nil }
        let scheme = (components.scheme ?? "").lowercased()
        if scheme == "aladdin" {
            let host = (components.host ?? "").lowercased()
            if host == "bind" || components.path.contains("bind") {
                return tokenFromQueryItems(components.queryItems)
            }
        }
        if scheme == "https" || scheme == "http" {
            if let host = components.host?.lowercased(),
               host.contains("aladdin"),
               components.path.lowercased().contains("bind") || (components.queryItems?.contains(where: { $0.name == "token" }) ?? false) {
                return tokenFromQueryItems(components.queryItems)
            }
        }
        return tokenFromQueryItems(components.queryItems)
    }

    /// Сканер возвращает строку — может быть целиком URL, `aladdin://…` или уже извлечённый токен.
    static func extractToken(fromScannedString raw: String) -> String? {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        if let url = URL(string: trimmed), url.scheme != nil, let t = extractToken(from: url), !t.isEmpty {
            return t
        }
        // Сырой токен из UserDefaults / буфера (без query).
        if trimmed.range(of: #"^[A-Za-z0-9._-]{8,512}$"#, options: .regularExpression) != nil {
            return trimmed
        }
        return nil
    }

    private static func tokenFromQueryItems(_ items: [URLQueryItem]?) -> String? {
        guard let items else { return nil }
        for item in items where item.name == "token" {
            if let v = item.value?.trimmingCharacters(in: .whitespacesAndNewlines), !v.isEmpty {
                return v
            }
        }
        return nil
    }

    /// Формат отображения PIN: `334-329`.
    static func formattedPIN(_ digits: String) -> String {
        let d = digits.filter { $0.isNumber }
        guard d.count == 6 else { return digits }
        let i = d.index(d.startIndex, offsetBy: 3)
        return "\(d[..<i])-\(d[i...])"
    }
}

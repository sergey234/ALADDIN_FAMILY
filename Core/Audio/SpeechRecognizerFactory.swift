import Speech

/// Выбор первого доступного `SFSpeechRecognizer` (на устройстве ru-RU часто недоступен без Siri).
enum SpeechRecognizerFactory {
    static func bestAvailable(preferred: Locale) -> SFSpeechRecognizer? {
        var identifiers: [String] = [preferred.identifier]
        let lang = bcp47LanguageCode(from: preferred)

        switch lang {
        case "ru":
            identifiers.append(contentsOf: ["ru-RU", "ru"])
        case "zh":
            identifiers.append(contentsOf: ["zh-Hans", "zh-CN", "zh-Hant"])
        case "ar":
            identifiers.append(contentsOf: ["ar-SA", "ar"])
        case "en":
            identifiers.append(contentsOf: ["en-US", "en-GB", "en"])
        default:
            break
        }

        identifiers.append(contentsOf: ["en-US", Locale.current.identifier])

        var seen = Set<String>()
        for id in identifiers {
            guard seen.insert(id).inserted else { continue }
            guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: id)), recognizer.isAvailable else {
                continue
            }
            return recognizer
        }

        if let fallback = SFSpeechRecognizer(), fallback.isAvailable {
            return fallback
        }
        return nil
    }

    /// ISO 639-1 из `Locale` без API iOS 16+ (`Locale.language`).
    private static func bcp47LanguageCode(from locale: Locale) -> String {
        if let code = locale.languageCode, !code.isEmpty {
            return code
        }
        let normalized = locale.identifier.replacingOccurrences(of: "_", with: "-")
        if let first = normalized.split(separator: "-").first, !first.isEmpty {
            return String(first)
        }
        return normalized
    }
}

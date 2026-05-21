import Speech

/// Выбор `SFSpeechRecognizer` для live-распознавания (AI mic).
/// На реальном iPhone ru-RU часто требует загруженный язык Siri; на Simulator — только cloud.
enum SpeechRecognizerFactory {

    struct Selection {
        let recognizer: SFSpeechRecognizer
        /// `true` → `SFSpeechAudioBufferRecognitionRequest.requiresOnDeviceRecognition` (без облака Siri).
        let useOnDeviceRecognition: Bool
    }

    /// На Simulator нет локальных speech-assets → не дергаем `supportsOnDeviceRecognition` (иначе SFLocalSpeechRecognitionClient 4099 в логах).
    static var prefersOnDeviceRecognition: Bool {
        #if targetEnvironment(simulator)
        return false
        #else
        return true
        #endif
    }

    /// Быстрая проверка для UI (mic enabled) — cloud path, без probe on-device assets.
    static func isSpeechInputAvailable(preferred: Locale) -> Bool {
        cloudOnly(preferred: preferred) != nil
    }

    static func bestForLiveRecognition(preferred: Locale) -> Selection? {
        #if !targetEnvironment(simulator)
        // Live mic (AI): ru-RU on-device пакет часто не загружен → 20–30 с «зависание» и retry.
        // Siri cloud стартует сразу (текст уходит в Apple Speech, не на сервер ALADDIN).
        if prefersOnDeviceRecognition,
           bcp47LanguageCode(from: preferred) == "ru",
           let cloud = cloudOnly(preferred: preferred) {
            return cloud
        }
        #endif
        if prefersOnDeviceRecognition,
           let onDevice = firstAvailable(preferred: preferred, requireOnDevice: true) {
            return Selection(recognizer: onDevice, useOnDeviceRecognition: true)
        }
        return cloudOnly(preferred: preferred)
    }

    /// Siri cloud path (no `requiresOnDeviceRecognition`) — fallback when on-device pack is missing.
    static func cloudOnly(preferred: Locale) -> Selection? {
        guard let cloud = firstAvailable(preferred: preferred, requireOnDevice: false) else {
            return nil
        }
        return Selection(recognizer: cloud, useOnDeviceRecognition: false)
    }

    /// Файловая транскрипция (диктофон): на Simulator — cloud, на устройстве — on-device с fallback в сервисе.
    static func bestForFileTranscription(preferred: Locale) -> Selection? {
        if prefersOnDeviceRecognition,
           let onDevice = firstAvailable(preferred: preferred, requireOnDevice: true) {
            return Selection(recognizer: onDevice, useOnDeviceRecognition: true)
        }
        return cloudOnly(preferred: preferred)
    }

    /// Обратная совместимость (Voice Notes file transcription).
    static func bestAvailable(preferred: Locale) -> SFSpeechRecognizer? {
        bestForFileTranscription(preferred: preferred)?.recognizer
    }

    private static func firstAvailable(preferred: Locale, requireOnDevice: Bool) -> SFSpeechRecognizer? {
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
            guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: id)),
                  recognizer.isAvailable else {
                continue
            }
            if requireOnDevice {
                guard recognizer.supportsOnDeviceRecognition else { continue }
            }
            return recognizer
        }

        if !requireOnDevice, let fallback = SFSpeechRecognizer(), fallback.isAvailable {
            return fallback
        }
        return nil
    }

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

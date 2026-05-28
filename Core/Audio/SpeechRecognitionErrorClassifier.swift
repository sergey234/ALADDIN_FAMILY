import Foundation

/// Классификация ошибок Apple Speech (общая для AI и тестов).
enum SpeechRecognitionErrorClassifier {
    static func isBenign(_ error: Error) -> Bool {
        let ns = error as NSError
        if ns.domain == "kAFAssistantErrorDomain" && [216, 209, 1110].contains(ns.code) { return true }
        if ns.domain == NSURLErrorDomain && ns.code == NSURLErrorCancelled { return true }
        if ns.code == 216 { return true }
        return false
    }

    static func isOnDeviceModelMissing(_ error: Error) -> Bool {
        let ns = error as NSError
        return ns.domain == "kAFAssistantErrorDomain" && ns.code == 1101
    }

    /// Siri cloud transient — часто на устройстве при коротком hold-to-talk.
    static func isRetryPrompt(_ error: Error) -> Bool {
        let ns = error as NSError
        if ns.domain == "kAFAssistantErrorDomain" && ns.code == 203 { return true }
        if ns.domain == "EARErrorDomain" && ns.code == 3 { return true }
        return false
    }

    static func isServiceUnavailable(_ error: Error) -> Bool {
        if isBenign(error) || isOnDeviceModelMissing(error) { return false }
        let ns = error as NSError
        if ns.domain == "SiriCoreSiriConnectionErrorDomain" { return true }
        if ns.domain == "kAFAssistantErrorDomain", [1107, 1111].contains(ns.code) { return true }
        return false
    }
}

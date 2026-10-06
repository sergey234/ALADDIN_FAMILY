import AppIntents
import Foundation

/// VSL-C P1 — Siri / Shortcuts: «ALADDIN лог» → Voice Notes (`aladdin://voice/log`).
@available(iOS 16.0, *)
struct OpenVoiceSafetyLogIntent: AppIntent {
    static var title: LocalizedStringResource = "ALADDIN Voice Log"
    static var description = IntentDescription("Open ALADDIN voice notes to say link / check / remind.")
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult {
        VoiceSafetyNowStore.markPendingOpen()
        NotificationCenter.default.post(name: .navigateToVoiceNotes, object: nil)
        return .result()
    }
}

/// gai-06 — Siri / Shortcuts: «проверь ссылку» → Antifake Hub (как Voice Log Intent).
@available(iOS 16.0, *)
struct CheckAntifakeLinkIntent: AppIntent {
    static var title: LocalizedStringResource = "Check link with ALADDIN"
    static var description = IntentDescription("Open ALADDIN Antifake Hub to check a link or message.")
    static var openAppWhenRun: Bool = true

    @Parameter(title: "URL")
    var url: URL?

    @MainActor
    func perform() async throws -> some IntentResult {
        if let url {
            let value = url.absoluteString
            AntifakeSharePayloadStore.save(mode: .url, value: value)
        }
        NotificationCenter.default.post(name: .navigateToAntifakeCheck, object: nil)
        return .result()
    }
}

@available(iOS 16.0, *)
struct ALADDINAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OpenVoiceSafetyLogIntent(),
            phrases: [
                "Open \(.applicationName) voice log",
                "\(.applicationName) voice log",
                "Журнал \(.applicationName)",
                "Голосовой журнал \(.applicationName)"
            ],
            shortTitle: "Voice Log",
            systemImageName: "mic.circle.fill"
        )
        AppShortcut(
            intent: CheckAntifakeLinkIntent(),
            phrases: [
                "Check a link with \(.applicationName)",
                "\(.applicationName) check link",
                "Проверь ссылку в \(.applicationName)",
                "Проверить ссылку \(.applicationName)"
            ],
            shortTitle: "Check link",
            systemImageName: "link.badge.checkmark"
        )
    }
}

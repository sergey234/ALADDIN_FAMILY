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
    }
}

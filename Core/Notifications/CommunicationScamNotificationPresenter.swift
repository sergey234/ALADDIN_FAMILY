import Foundation
import Intents
import UserNotifications

/// WAVE3 E1 — Communication Notifications style for scam/spam family alerts.
enum CommunicationScamNotificationPresenter {

    static func decorateContent(
        _ content: UNMutableNotificationContent,
        displayName: String
    ) -> UNMutableNotificationContent {
        guard AppStoreBuildPolicy.allowsCommunicationNotifications else {
            return content
        }

        let handle = INPersonHandle(value: displayName, type: .unknown)
        let person = INPerson(
            personHandle: handle,
            nameComponents: nil,
            displayName: displayName,
            image: nil,
            contactIdentifier: nil,
            customIdentifier: displayName
        )

        let intent = INSendMessageIntent(
            recipients: [person],
            outgoingMessageType: .outgoingMessageText,
            content: content.body,
            speakableGroupName: nil,
            conversationIdentifier: "aladdin.scam.\(displayName)",
            serviceName: "ALADDIN",
            sender: person,
            attachments: nil
        )

        let interaction = INInteraction(intent: intent, response: nil)
        interaction.direction = .incoming
        do {
            try interaction.donate()
            let updated = try content.updating(from: intent)
            return updated as? UNMutableNotificationContent ?? content
        } catch {
            print("⚠️ CommunicationScamNotificationPresenter: \(error.localizedDescription)")
            return content
        }
    }

    /// Schedule a scam-style communication notification (local).
    static func scheduleScamAlert(title: String, body: String, callerLabel: String) async {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = "SCAM_COMM_ALERT"
        let decorated = decorateContent(content, displayName: callerLabel)

        let request = UNNotificationRequest(
            identifier: "scam.comm.\(UUID().uuidString)",
            content: decorated,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 0.5, repeats: false)
        )
        try? await UNUserNotificationCenter.current().add(request)
    }
}

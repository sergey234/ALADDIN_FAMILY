import Foundation
import Intents
import UIKit
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

    /// Trip push: person photo in the icon slot. Nil means keep the app logo.
    static func contentByApplyingAvatar(
        _ content: UNMutableNotificationContent,
        displayName: String,
        imageFileURL: URL
    ) -> UNMutableNotificationContent? {
        guard AppStoreBuildPolicy.allowsCommunicationNotifications else { return nil }
        guard let imageData = avatarJPEG(from: imageFileURL) else { return nil }

        let handle = INPersonHandle(value: displayName, type: .unknown)
        let person = INPerson(
            personHandle: handle,
            nameComponents: nil,
            displayName: displayName,
            image: INImage(imageData: imageData),
            contactIdentifier: nil,
            customIdentifier: "aladdin.avatar.\(displayName)"
        )
        let intent = INSendMessageIntent(
            recipients: [person],
            outgoingMessageType: .outgoingMessageText,
            content: content.body,
            speakableGroupName: nil,
            conversationIdentifier: "aladdin.trip.\(displayName)",
            serviceName: "ALADDIN",
            sender: person,
            attachments: nil
        )
        let interaction = INInteraction(intent: intent, response: nil)
        interaction.direction = .incoming
        do {
            try interaction.donate()
            let updated = try content.updating(from: intent)
            guard let mutable = updated as? UNMutableNotificationContent else { return nil }
            mutable.title = content.title
            mutable.body = content.body
            mutable.sound = content.sound
            mutable.userInfo = content.userInfo
            mutable.categoryIdentifier = content.categoryIdentifier
            if #available(iOS 15.0, *) {
                mutable.interruptionLevel = content.interruptionLevel
            }
            return mutable
        } catch {
            print("⚠️ trip avatar notification: \(error.localizedDescription)")
            return nil
        }
    }

    /// Small JPEG so the lock-screen icon stays a face, not a full camera file.
    private static func avatarJPEG(from url: URL) -> Data? {
        guard let image = UIImage(contentsOfFile: url.path) else { return nil }
        let maxSide: CGFloat = 320
        let longest = max(image.size.width, image.size.height)
        guard longest > 1 else { return nil }
        let scale = min(1, maxSide / longest)
        let size = CGSize(width: image.size.width * scale, height: image.size.height * scale)
        let scaled = UIGraphicsImageRenderer(size: size).image { _ in
            image.draw(in: CGRect(origin: .zero, size: size))
        }
        return scaled.jpegData(compressionQuality: 0.82)
    }
}

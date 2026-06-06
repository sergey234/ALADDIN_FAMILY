import SwiftUI

extension CompanionUsageBanner {
    struct UsageChipDescriptor: Equatable {
        let icon: String
        let label: String
        let tint: Color
        let accessibilityLabel: String
    }

    /// Короткая метка для immersive chip rail (только warn/limit).
    static func usageChipDescriptor(
        usage: CompanionUsageSnapshot?,
        localizationManager: LocalizationManager
    ) -> UsageChipDescriptor? {
        guard let usage else { return nil }
        if usage.messageLimitReached {
            let title = localizationManager.localized("companion_usage_msg_limit_title")
            return UsageChipDescriptor(
                icon: "exclamationmark.octagon.fill",
                label: title,
                tint: .red,
                accessibilityLabel: title
            )
        }
        if usage.voiceLimitReached {
            let title = localizationManager.localized("companion_usage_voice_limit_title")
            return UsageChipDescriptor(
                icon: "mic.slash.fill",
                label: title,
                tint: .orange,
                accessibilityLabel: title
            )
        }
        if usage.shouldWarnMessages {
            let left = max(0, usage.messagesDailyCap - usage.messagesToday)
            let label = String(
                format: localizationManager.localized("companion_usage_chip_messages"),
                left
            )
            return UsageChipDescriptor(
                icon: "bubble.left.and.bubble.right.fill",
                label: label,
                tint: .purple,
                accessibilityLabel: label
            )
        }
        if usage.shouldWarnVoice {
            let leftMin = max(1, max(0, usage.voiceDailyCapSeconds - usage.voiceSecondsToday) / 60)
            let label = String(
                format: localizationManager.localized("companion_usage_chip_voice"),
                leftMin
            )
            return UsageChipDescriptor(
                icon: "waveform",
                label: label,
                tint: .indigo,
                accessibilityLabel: label
            )
        }
        return nil
    }
}

import SwiftUI

/// P1-11 — предупреждение при ≥80% дневного лимита сообщений или голоса.
struct CompanionUsageBanner: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let usage: CompanionUsageSnapshot?

    var body: some View {
        if let banner = bannerContent {
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: banner.icon)
                    .foregroundStyle(banner.tint)
                VStack(alignment: .leading, spacing: 4) {
                    Text(banner.title)
                        .font(.subheadline.bold())
                    Text(banner.message)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 0)
            }
            .padding(12)
            .background(banner.tint.opacity(0.12), in: RoundedRectangle(cornerRadius: 12))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(banner.tint.opacity(0.35), lineWidth: 1)
            )
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(banner.title). \(banner.message)")
        }
    }

    private var bannerContent: BannerModel? {
        guard let usage else { return nil }
        if usage.messageLimitReached {
            return BannerModel(
                icon: "exclamationmark.octagon.fill",
                tint: .red,
                title: localizationManager.localized("companion_usage_msg_limit_title"),
                message: localizationManager.localized("companion_usage_msg_limit_body")
            )
        }
        if usage.voiceLimitReached {
            return BannerModel(
                icon: "mic.slash.fill",
                tint: .orange,
                title: localizationManager.localized("companion_usage_voice_limit_title"),
                message: localizationManager.localized("companion_usage_voice_limit_body")
            )
        }
        if usage.shouldWarnMessages {
            let left = max(0, usage.messagesDailyCap - usage.messagesToday)
            return BannerModel(
                icon: "bubble.left.and.bubble.right.fill",
                tint: .purple,
                title: localizationManager.localized("companion_usage_msg_warn_title"),
                message: String(
                    format: localizationManager.localized("companion_usage_msg_warn_body"),
                    usage.messagesUsagePercent,
                    left
                )
            )
        }
        if usage.shouldWarnVoice {
            let leftSec = max(0, usage.voiceDailyCapSeconds - usage.voiceSecondsToday)
            let leftMin = max(1, leftSec / 60)
            return BannerModel(
                icon: "waveform",
                tint: .indigo,
                title: localizationManager.localized("companion_usage_voice_warn_title"),
                message: String(
                    format: localizationManager.localized("companion_usage_voice_warn_body"),
                    leftMin,
                    usage.voiceUsagePercent
                )
            )
        }
        return nil
    }

    private struct BannerModel {
        let icon: String
        let tint: Color
        let title: String
        let message: String
    }
}

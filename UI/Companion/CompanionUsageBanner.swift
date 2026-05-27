import SwiftUI

/// P1-11 — предупреждение при ≥80% дневного лимита сообщений или голоса.
struct CompanionUsageBanner: View {
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
                title: "Лимит сообщений на сегодня",
                message: "Новые сообщения герою будут доступны завтра. Попроси родителя о тарифе Premium, если нужно больше."
            )
        }
        if usage.voiceLimitReached {
            return BannerModel(
                icon: "mic.slash.fill",
                tint: .orange,
                title: "Лимит голоса на сегодня",
                message: "Можно продолжить писать текстом. Завтра лимит обновится."
            )
        }
        if usage.shouldWarnMessages {
            let left = max(0, usage.messagesDailyCap - usage.messagesToday)
            return BannerModel(
                icon: "bubble.left.and.bubble.right.fill",
                tint: .purple,
                title: "Осталось мало сообщений",
                message: "Использовано \(usage.messagesUsagePercent)% лимита. Примерно \(left) сообщений на сегодня."
            )
        }
        if usage.shouldWarnVoice {
            let leftSec = max(0, usage.voiceDailyCapSeconds - usage.voiceSecondsToday)
            let leftMin = max(1, leftSec / 60)
            return BannerModel(
                icon: "waveform",
                tint: .indigo,
                title: "Голос почти на исходе",
                message: "Осталось около \(leftMin) мин голоса на сегодня (\(usage.voiceUsagePercent)% лимита)."
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

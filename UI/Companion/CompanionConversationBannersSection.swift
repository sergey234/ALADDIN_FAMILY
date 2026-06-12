import SwiftUI

/// AIL P1 — баннеры под сценой героя: полные полосы или chip rail в immersive (max 32 pt).
struct CompanionConversationBannersSection: View {
    enum DisplayMode {
        case full
        case chips
    }

    @EnvironmentObject private var localizationManager: LocalizationManager

    let mode: DisplayMode
    let usage: CompanionUsageSnapshot?
    let wellnessPillar: WellnessPillar?
    let wellnessMoodEmoji: String?
    let companionEntryBanner: String?
    let onDismissEntryBanner: () -> Void
    let wellnessRecapLine: String?
    let memoryChipsEnabled: Bool
    let memoryChipCount: Int
    let onMemoryChipTap: () -> Void

    private let chipMaxHeight: CGFloat = 32

    var body: some View {
        Group {
            if mode == .full {
                fullBanners
            } else {
                immersiveChipRail
            }
        }
    }

    @ViewBuilder
    private var fullBanners: some View {
        CompanionUsageBanner(usage: usage)
            .padding(.horizontal, 12)
            .padding(.vertical, 4)
        if let pillar = wellnessPillar {
            wellnessPillarFullBanner(pillar: pillar)
        }
        if let companionEntryBanner, !companionEntryBanner.isEmpty {
            entryFullBanner(text: companionEntryBanner)
        }
        if let wellnessRecapLine, !wellnessRecapLine.isEmpty {
            recapFullBanner(text: wellnessRecapLine)
        }
    }

    @ViewBuilder
    private var immersiveChipRail: some View {
        if hasAnyChip {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    if let usageChip = CompanionUsageBanner.usageChipDescriptor(
                        usage: usage,
                        localizationManager: localizationManager
                    ) {
                        bannerChip(
                            icon: usageChip.icon,
                            label: usageChip.label,
                            tint: usageChip.tint,
                            accessibilityLabel: usageChip.accessibilityLabel,
                            id: "companion_banner_chip_usage"
                        )
                    }
                    if let pillar = wellnessPillar {
                        let pillarLabel = localizationManager.localized(pillar.titleKey)
                            + (wellnessMoodEmoji.map { " \($0)" } ?? "")
                        bannerChip(
                            icon: "heart.text.square.fill",
                            label: pillarLabel,
                            tint: Color(hex: "A78BFA"),
                            accessibilityLabel: pillarLabel,
                            id: "companion_banner_chip_pillar"
                        )
                    }
                    if let companionEntryBanner, !companionEntryBanner.isEmpty {
                        entryChip(text: companionEntryBanner)
                    }
                    if let wellnessRecapLine, !wellnessRecapLine.isEmpty {
                        bannerChip(
                            icon: "clock.arrow.circlepath",
                            label: recapChipLabel(recap: wellnessRecapLine),
                            tint: Color(hex: "8B5CF6"),
                            accessibilityLabel: wellnessRecapLine,
                            id: "companion_banner_chip_recap"
                        )
                    }
                    if memoryChipsEnabled, memoryChipCount > 0 {
                        Button(action: onMemoryChipTap) {
                            bannerChipLabel(
                                icon: "brain.head.profile",
                                label: String(
                                    format: localizationManager.localized("companion_memory_chip_count"),
                                    memoryChipCount
                                ),
                                tint: Color(hex: "6366F1")
                            )
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("companion_banner_chip_memory")
                    }
                }
                .padding(.horizontal, 12)
            }
            .frame(maxWidth: .infinity)
            .frame(height: chipMaxHeight)
            .padding(.vertical, 4)
            .accessibilityIdentifier("companion_banner_chip_rail")
        }
    }

    private var hasAnyChip: Bool {
        CompanionUsageBanner.usageChipDescriptor(usage: usage, localizationManager: localizationManager) != nil
            || wellnessPillar != nil
            || !(companionEntryBanner ?? "").isEmpty
            || !(wellnessRecapLine ?? "").isEmpty
            || (memoryChipsEnabled && memoryChipCount > 0)
    }

    private func wellnessPillarFullBanner(pillar: WellnessPillar) -> some View {
        HStack(spacing: 8) {
            Text(localizationManager.localized("wellness_chip_mood"))
                .font(.caption2.bold())
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color(hex: "A78BFA").opacity(0.25))
                .clipShape(Capsule())
            Image(systemName: "heart.text.square.fill")
                .foregroundStyle(Color(hex: "A78BFA"))
            Text(localizationManager.localized(pillar.titleKey))
                .font(.caption.weight(.semibold))
                .foregroundStyle(Color.white.opacity(0.95))
            Spacer()
            if let wellnessMoodEmoji {
                Text(wellnessMoodEmoji)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color(hex: "8B5CF6").opacity(0.12))
        .accessibilityIdentifier("companion_wellness_pillar_banner")
    }

    private func entryFullBanner(text: String) -> some View {
        HStack(spacing: 8) {
            Image(systemName: "sparkles")
                .foregroundStyle(Color(hex: "A78BFA"))
            Text(text)
                .font(.caption)
                .foregroundStyle(Color.white.opacity(0.92))
            Spacer()
            Button(action: onDismissEntryBanner) {
                Image(systemName: "xmark.circle.fill")
                    .foregroundStyle(.secondary)
            }
            .accessibilityLabel(localizationManager.localized("companion_social_bridge_dismiss"))
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Color.mint.opacity(0.12))
        .accessibilityIdentifier("companion_wellness_mode_banner")
    }

    private func recapFullBanner(text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.caption)
                .foregroundStyle(Color(hex: "8B5CF6"))
            Text(text)
                .font(.caption)
                .foregroundStyle(Color.white.opacity(0.82))
                .fixedSize(horizontal: false, vertical: true)
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 6)
        .background(Color(hex: "8B5CF6").opacity(0.08))
        .accessibilityIdentifier("companion_wellness_recap_banner")
    }

    private func entryChip(text: String) -> some View {
        HStack(spacing: 4) {
            bannerChipLabel(
                icon: "sparkles",
                label: entryChipLabel(text: text),
                tint: Color.mint
            )
            Button(action: onDismissEntryBanner) {
                Image(systemName: "xmark.circle.fill")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(localizationManager.localized("companion_social_bridge_dismiss"))
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color.mint.opacity(0.18))
        .clipShape(Capsule())
        .accessibilityIdentifier("companion_banner_chip_entry")
    }

    private func bannerChip(
        icon: String,
        label: String,
        tint: Color,
        accessibilityLabel: String,
        id: String
    ) -> some View {
        bannerChipLabel(icon: icon, label: label, tint: tint)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(tint.opacity(0.48))
            .clipShape(Capsule())
            .overlay(
                Capsule()
                    .stroke(Color.white.opacity(0.28), lineWidth: 0.5)
            )
            .accessibilityElement(children: .combine)
            .accessibilityLabel(accessibilityLabel)
            .accessibilityIdentifier(id)
    }

    private func bannerChipLabel(icon: String, label: String, tint: Color) -> some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(tint)
            Text(label)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(Color.white.opacity(0.95))
                .lineLimit(1)
        }
    }

    private func recapChipLabel(recap: String) -> String {
        let trimmed = recap.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count <= 28 { return trimmed }
        return String(trimmed.prefix(25)) + "…"
    }

    private func entryChipLabel(text: String) -> String {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count <= 22 { return trimmed }
        return String(trimmed.prefix(19)) + "…"
    }
}

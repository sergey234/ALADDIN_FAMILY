import SwiftUI

/// fsl-07 — одна полоска дня: сон / учёба / экран. Без календаря.
struct FamilyDayStripView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @AppStorage("parental_bedtime_start") private var bedtimeStart: String = "22:00"
    @AppStorage("parental_bedtime_end") private var bedtimeEnd: String = "07:00"
    @AppStorage("parental_homework_mode") private var isHomeworkModeEnabled: Bool = false
    @AppStorage("parental_screen_time_limit") private var screenTimeLimit: String = "3h/day"

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("day_strip_title"))
                .font(.headline)
                .foregroundColor(.white)
                .accessibilityAddTraits(.isHeader)

            Text(localizationManager.localized("day_strip_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.75))
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: Spacing.s) {
                dayChip(
                    icon: "moon.zzz.fill",
                    title: localizationManager.localized("day_strip_sleep"),
                    value: "\(bedtimeStart)–\(bedtimeEnd)",
                    active: true
                )
                dayChip(
                    icon: "book.fill",
                    title: localizationManager.localized("day_strip_study"),
                    value: localizationManager.localized(
                        isHomeworkModeEnabled ? "day_strip_on" : "day_strip_off"
                    ),
                    active: isHomeworkModeEnabled
                )
                dayChip(
                    icon: "iphone",
                    title: localizationManager.localized("day_strip_screen"),
                    value: screenTimeLimit,
                    active: true
                )
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        .accessibilityIdentifier("family_day_strip")
    }

    private func dayChip(icon: String, title: String, value: String, active: Bool) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Label(title, systemImage: icon)
                .font(.caption.weight(.semibold))
                .foregroundColor(active ? .secondaryGold : .white.opacity(0.55))
                .lineLimit(1)
                .minimumScaleFactor(0.8)
            Text(value)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.85))
                .lineLimit(2)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.s)
        .background(Color.white.opacity(active ? 0.12 : 0.06))
        .cornerRadius(CornerRadius.medium)
    }
}

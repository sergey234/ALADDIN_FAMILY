import SwiftUI

/// A-01 / A-05 — shared 3-line honest copy for card + accordion (SSOT).
struct AntifakeQuickAccessCopyLines: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var line3Font: Font = .caption2

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xxs) {
            Text(localizationManager.localized("protection_antifake_card_line1"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
            Text(localizationManager.localized("protection_antifake_card_line2"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
            Text(localizationManager.localized("protection_antifake_card_line3"))
                .font(line3Font)
                .foregroundColor(.textSecondary.opacity(0.9))
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(AntifakeQuickAccessCopy.accessibilityLabel(localizationManager: localizationManager))
    }
}

enum AntifakeQuickAccessCopy {
    static func accessibilityLabel(localizationManager: LocalizationManager) -> String {
        [
            localizationManager.localized("protection_antifake_card_title"),
            localizationManager.localized("protection_antifake_card_line1"),
            localizationManager.localized("protection_antifake_card_line2"),
            localizationManager.localized("protection_antifake_card_line3")
        ].joined(separator: ". ")
    }
}

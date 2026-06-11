import SwiftUI

/// Inline upgrade CTA when API returns 403 `premium_required` (B2-07).
struct AntifakeInlinePremiumGateCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let message: String?
    let onUpgrade: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Label(
                localizationManager.localized("antifake_premium_required_title"),
                systemImage: "lock.shield.fill"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(message ?? localizationManager.localized("antifake_premium_required_body"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            PrimaryButton(localizationManager.localized("protection_upgrade_tariff")) {
                onUpgrade()
            }
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .warningOrange)
        .accessibilityIdentifier("antifake_inline_premium_gate")
    }
}

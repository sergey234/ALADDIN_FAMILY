import SwiftUI

// MARK: - fws-03 «Before transfer» social-engineering entry (Main + Elderly)

struct AntifakeTransferCheckCTA: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager

    var style: Style = .banner

    enum Style {
        case banner
        case elderlyButton
    }

    var body: some View {
        switch style {
        case .banner:
            banner
        case .elderlyButton:
            elderlyRow
        }
    }

    private var banner: some View {
        Button {
            openTransferCheck()
        } label: {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("🛡️")
                    .font(.title2)
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("antifake_transfer_cta_title"))
                        .font(.subheadline.weight(.bold))
                        .foregroundColor(.white)
                        .multilineTextAlignment(.leading)
                    Text(localizationManager.localized("antifake_transfer_cta_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.leading)
                }
                Spacer(minLength: 0)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.bold))
                    .foregroundColor(.secondaryGold)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .dangerRed)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("antifake_transfer_check_cta")
        .accessibilityHint(localizationManager.localized("antifake_transfer_cta_hint"))
    }

    private var elderlyRow: some View {
        Button {
            openTransferCheck()
        } label: {
            HStack(spacing: Spacing.m) {
                Text("💸")
                    .font(.system(size: 36))
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("antifake_transfer_cta_title"))
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                    Text(localizationManager.localized("antifake_transfer_cta_subtitle"))
                        .font(.system(size: 16))
                        .foregroundColor(.white.opacity(0.8))
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white.opacity(0.6))
            }
            .padding(Spacing.l)
            .stormGlassCard(cornerRadius: CornerRadius.large)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.dangerRed.opacity(0.35), lineWidth: 2)
            )
        }
        .buttonStyle(.plain)
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityIdentifier("antifake_transfer_check_cta_elderly")
    }

    private func openTransferCheck() {
        HapticFeedback.impact(.medium)
        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.antifakeTransferCheckEntry)
        navigationManager.navigateToAntifakeHub(tab: .text, textMode: .text)
        Task { await AntifakeFamilyPushRegistrar.shared.syncTokenIfNeeded() }
    }
}

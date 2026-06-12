import SwiftUI

/// p1-10 — согласие на эмоциональную поддержку (самопомощь, не врач).
struct WellnessConsentScreen: View {
    var embeddedInHome: Bool = false
    var onConsentAccepted: (() -> Void)?

    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    private var ageBand: String {
        WellnessSessionStore.cachedAgeBand ?? CompanionUserContext.companionAgeBand
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_consent_title", ageBand: ageBand))
                    .font(.title2.bold())

                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_consent_body", ageBand: ageBand))
                    .font(.body)
                    .foregroundStyle(.secondary)

                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_consent_jung_note", ageBand: ageBand))
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .padding(.vertical, 4)

                Button {
                    Task { await acceptAndContinue() }
                } label: {
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_consent_accept", ageBand: ageBand))
                        .font(.body.bold())
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))

                if !embeddedInHome {
                    Button {
                        navigationManager.wellnessGoBack()
                    } label: {
                        Text(localizationManager.localized("wellness_consent_decline"))
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }
            }
            .padding()
        }
        .navigationBarHidden(true)
        .background(StormMeshBackground(variant: .neutral))
        .foregroundColor(.white)
    }

    private func acceptAndContinue() async {
        do {
            _ = try await WellnessAPIService.shared.postConsent(accepted: true)
            WellnessSessionStore.acceptConsent()
        } catch {
            WellnessSessionStore.acceptConsent()
        }
        if embeddedInHome {
            onConsentAccepted?()
        } else {
            navigationManager.navigateTo(.wellnessHub)
        }
    }
}

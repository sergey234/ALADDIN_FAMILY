import SwiftUI

/// Hub-level paywall sheet + tariff refresh after dismiss (B2-07).
enum AntifakeHubPremiumCoordinator {

    @MainActor
    static func refreshTariffAfterPaywall() {
        ProtectionSettingsManager.shared.loadSettingsFromServer { _ in
            Task { @MainActor in
                TariffManager.shared.loadTariff()
            }
        }
    }
}

extension View {
    /// Presents tariffs sheet and refreshes protection/tariff state on dismiss.
    func antifakePremiumPaywallSheet(
        isPresented: Binding<Bool>,
        navigationManager: NavigationManager,
        localizationManager: LocalizationManager,
        subscriptionManager: SubscriptionManager
    ) -> some View {
        sheet(isPresented: isPresented, onDismiss: {
            AntifakeHubPremiumCoordinator.refreshTariffAfterPaywall()
        }) {
            NavigationView {
                TariffsScreen()
                    .environmentObject(navigationManager)
                    .environmentObject(localizationManager)
                    .environmentObject(subscriptionManager)
            }
        }
    }
}

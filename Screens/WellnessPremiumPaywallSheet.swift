import SwiftUI

/// p3-06 — Premium paywall for timeline / full assessments.
struct WellnessPremiumPaywallSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss

    var onUpgrade: (() -> Void)?

    var body: some View {
        WellnessNavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                Text(localizationManager.localized("wellness_premium_title"))
                    .font(.title2.bold())
                Text(localizationManager.localized("wellness_premium_body"))
                    .font(.body)
                    .foregroundStyle(.secondary)
                Button {
                    if let onUpgrade {
                        onUpgrade()
                    } else {
                        navigationManager.navigateTo(.tariffs)
                    }
                    dismiss()
                } label: {
                    Text(localizationManager.localized("wellness_premium_cta"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.purple)
                Button(localizationManager.localized("wellness_premium_later")) {
                    dismiss()
                }
                .frame(maxWidth: .infinity)
            }
            .padding()
            .navigationTitle(localizationManager.localized("wellness_premium_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_premium_later")) { dismiss() }
                }
            }
        }
    }
}

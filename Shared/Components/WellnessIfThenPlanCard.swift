import SwiftUI

/// fws-22 — if-then habit form (behavioral pillar, links fws-02 infrastructure).
struct WellnessIfThenPlanCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var ifPart = ""
    @State private var thenPart = ""
    @State private var savedMessage: String?
    @State private var errorMessage: String?
    @State private var isSaving = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(
                localizationManager.localized("wellness_if_then_title"),
                systemImage: "arrow.triangle.branch"
            )
            .font(.subheadline.bold())
            .foregroundColor(.white)

            Text(localizationManager.localized("wellness_if_then_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))

            TextField(localizationManager.localized("wellness_if_then_if_placeholder"), text: $ifPart)
                .padding(10)
                .stormGlassCard(cornerRadius: 10)
            TextField(localizationManager.localized("wellness_if_then_then_placeholder"), text: $thenPart)
                .padding(10)
                .stormGlassCard(cornerRadius: 10)

            Button {
                Task { await save() }
            } label: {
                Text(localizationManager.localized("wellness_if_then_save"))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color(hex: "8B5CF6"))
            .disabled(isSaving || composedLine.count < 6)

            if let savedMessage {
                Text(savedMessage).font(.caption).foregroundColor(.green)
            }
            if let errorMessage {
                Text(errorMessage).font(.caption).foregroundColor(.orange)
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .accessibilityIdentifier("wellness_if_then_card")
    }

    private var composedLine: String {
        let template = localizationManager.localized("wellness_if_then_template")
        return String(format: template, ifPart.trimmingCharacters(in: .whitespaces), thenPart.trimmingCharacters(in: .whitespaces))
    }

    @MainActor
    private func save() async {
        isSaving = true
        savedMessage = nil
        errorMessage = nil
        defer { isSaving = false }
        do {
            try await WellnessAPIService.shared.createHabit(ifThen: composedLine)
            ifPart = ""
            thenPart = ""
            savedMessage = localizationManager.localized("wellness_if_then_saved")
            HapticFeedback.notification(.success)
        } catch {
            errorMessage = localizationManager.localized("wellness_if_then_save_failed")
        }
    }
}

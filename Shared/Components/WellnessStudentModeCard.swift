import SwiftUI

/// fws-12 — teen opts into student band → campus pack + exam card.
struct WellnessStudentModeCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager

    @State private var enabled = false
    @State private var isSaving = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Toggle(isOn: $enabled) {
                Label(
                    localizationManager.localized("wellness_student_mode_title"),
                    systemImage: "graduationcap.fill"
                )
                .font(.subheadline.bold())
            }
            .toggleStyle(SwitchToggleStyle(tint: Color(hex: "8B5CF6")))
            .onChange(of: enabled) { newValue in
                Task { await persist(newValue) }
            }

            Text(localizationManager.localized("wellness_student_mode_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))

            if enabled {
                Button {
                    navigationManager.navigateToWellnessScreen(.wellnessExamMode, returnTo: .wellnessHub)
                } label: {
                    Text(localizationManager.localized("wellness_student_before_class_cta"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .tint(.orange)
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .accessibilityIdentifier("wellness_student_mode_card")
        .task {
            enabled = WellnessSessionStore.cachedAgeBand == "student"
        }
    }

    @MainActor
    private func persist(_ value: Bool) async {
        isSaving = true
        defer { isSaving = false }
        _ = try? await WellnessAPIService.shared.setStudentMode(value)
        if value {
            WellnessSessionStore.setCachedAgeBand("student")
        } else {
            WellnessSessionStore.setCachedAgeBand("teen")
        }
    }
}

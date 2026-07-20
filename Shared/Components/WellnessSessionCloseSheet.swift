import SwiftUI

/// psych-04/05/05b — structured session close (not freeform essay).
struct WellnessSessionCloseSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss

    @State private var learned = ""
    @State private var observe = ""
    @State private var smallStep = ""

    var ageBand: String = CompanionUserContext.companionAgeBand

    /// psych-05b — hide until FamilyChallenge (p2-9h) ships / flag on.
    private var challengeCTAEnabled: Bool {
        FamilyChallengesFeature.isEnabled
    }

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .warm).ignoresSafeArea()
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(localizationManager.localized("wellness_session_close_title"))
                            .font(.headline)

                        field(
                            titleKey: "wellness_session_close_learned",
                            text: $learned,
                            id: "wellness_session_close_learned"
                        )
                        field(
                            titleKey: "wellness_session_close_observe",
                            text: $observe,
                            id: "wellness_session_close_observe"
                        )
                        field(
                            titleKey: "wellness_session_close_step",
                            text: $smallStep,
                            id: "wellness_session_close_step"
                        )

                        Button {
                            saveAndDismiss()
                        } label: {
                            Text(localizationManager.localized("wellness_session_close_save"))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(Color(hex: "8B5CF6"))

                        VStack(spacing: 8) {
                            ctaButton(
                                titleKey: "wellness_session_close_cta_if_then",
                                systemImage: "arrow.triangle.branch"
                            ) {
                                saveLocal()
                                UserDefaults.standard.set(true, forKey: "wellness_focus_if_then_card")
                                dismiss()
                                if navigationManager.currentScreen != .wellnessHub {
                                    navigationManager.navigateToWellnessScreen(
                                        .wellnessHub,
                                        returnTo: navigationManager.currentScreen
                                    )
                                }
                            }
                            ctaButton(
                                titleKey: "wellness_session_close_cta_breath",
                                systemImage: "wind"
                            ) {
                                saveLocal()
                                WellnessSessionStore.setPendingExerciseId(WellnessBreath2Min.exerciseId)
                                dismiss()
                                navigationManager.navigateToWellnessScreen(
                                    .wellnessExercise,
                                    returnTo: navigationManager.currentScreen
                                )
                            }
                            ctaButton(
                                titleKey: "wellness_session_close_cta_checkin",
                                systemImage: "face.smiling"
                            ) {
                                saveLocal()
                                dismiss()
                                navigationManager.navigateToWellnessScreen(
                                    .wellnessCheckin,
                                    returnTo: navigationManager.currentScreen
                                )
                            }
                            if challengeCTAEnabled {
                                ctaButton(
                                    titleKey: "wellness_session_close_cta_challenge",
                                    systemImage: "flag.fill"
                                ) {
                                    saveLocal()
                                    if !smallStep.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                        UserDefaults.standard.set(
                                            smallStep,
                                            forKey: "family_challenge_draft_from_wellness"
                                        )
                                    }
                                    dismiss()
                                    navigationManager.navigateTo(.family)
                                }
                            }
                        }
                        .padding(.top, 4)

                        Text(localizationManager.localized("wellness_session_close_xp_note"))
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.65))
                    }
                    .padding()
                }
            }
            .foregroundColor(.white)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_guide_cancel")) { dismiss() }
                }
            }
        }
        .accessibilityIdentifier("wellness_session_close_sheet")
    }

    private func field(titleKey: String, text: Binding<String>, id: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized(titleKey))
                .font(.caption.weight(.semibold))
            TextField("", text: text)
                .textFieldStyle(.roundedBorder)
                .accessibilityIdentifier(id)
        }
    }

    private func ctaButton(titleKey: String, systemImage: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Label(localizationManager.localized(titleKey), systemImage: systemImage)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.white.opacity(0.9))
    }

    private func saveLocal() {
        let payload: [String: String] = [
            "learned": learned,
            "observe": observe,
            "step": smallStep,
            "at": ISO8601DateFormatter().string(from: Date()),
            "age_band": ageBand,
        ]
        if let data = try? JSONEncoder().encode(payload) {
            UserDefaults.standard.set(data, forKey: "wellness_session_close_last")
        }
        // psych-05: small step → if-then draft (no XP for chat itself)
        let step = smallStep.trimmingCharacters(in: .whitespacesAndNewlines)
        let obs = observe.trimmingCharacters(in: .whitespacesAndNewlines)
        if !step.isEmpty {
            UserDefaults.standard.set(step, forKey: "wellness_if_then_draft_action")
        }
        if !obs.isEmpty {
            UserDefaults.standard.set(obs, forKey: "wellness_if_then_draft_trigger")
        }
    }

    private func saveAndDismiss() {
        saveLocal()
        dismiss()
    }
}

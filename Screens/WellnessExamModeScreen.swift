import SwiftUI

/// fws-14 — exam date → countdown → breathing + one-thing CTA.
struct WellnessExamModeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var examDate = Date().addingTimeInterval(86400 * 7)
    @State private var title = ""
    @State private var parentDigest = false
    @State private var plan: WellnessExamPlanDTO?
    @State private var isLoading = true
    @State private var isSaving = false
    @State private var errorText: String?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    Text(localizationManager.localized("wellness_exam_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.85))

                    DatePicker(
                        localizationManager.localized("wellness_exam_date_label"),
                        selection: $examDate,
                        in: Date()...,
                        displayedComponents: [.date, .hourAndMinute]
                    )
                    .datePickerStyle(.graphical)
                    .tint(Color(hex: "8B5CF6"))

                    TextField(
                        localizationManager.localized("wellness_exam_title_placeholder"),
                        text: $title
                    )
                    .padding(12)
                    .stormGlassCard(cornerRadius: 12)

                    Toggle(
                        localizationManager.localized("wellness_exam_parent_digest"),
                        isOn: $parentDigest
                    )
                    .toggleStyle(SwitchToggleStyle(tint: Color(hex: "8B5CF6")))

                    Button {
                        Task { await savePlan() }
                    } label: {
                        Text(localizationManager.localized("wellness_exam_save"))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "8B5CF6"))
                    .disabled(isSaving)

                    if let plan {
                        countdownCard(plan)
                        actionButtons(plan)
                    }
                    if let errorText {
                        Text(errorText).font(.caption).foregroundStyle(.orange)
                    }
                }
                .padding()
            }
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .accessibilityIdentifier("wellness_exam_mode_screen")
        .task { await loadPlan() }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.wellnessGoBack() } label: {
                Image(systemName: "chevron.left").font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("wellness_exam_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    @ViewBuilder
    private func countdownCard(_ plan: WellnessExamPlanDTO) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("wellness_exam_countdown_title"))
                .font(.subheadline.bold())
            if let seconds = plan.secondsUntil {
                Text(formatCountdown(seconds))
                    .font(.title2.monospacedDigit().bold())
            }
            if let phase = plan.phase {
                Text(localizationManager.localized("wellness_exam_phase_\(phase)"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
    }

    @ViewBuilder
    private func actionButtons(_ plan: WellnessExamPlanDTO) -> some View {
        if plan.suggestBreathing == true {
            Button {
                openWellnessScreen(.wellnessTogether)
            } label: {
                Label(
                    localizationManager.localized("wellness_exam_breathing_cta"),
                    systemImage: "wind"
                )
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .tint(.cyan)
        }
        if plan.suggestOneThing == true {
            Button {
                openWellnessScreen(.wellnessOneThing)
            } label: {
                Label(
                    localizationManager.localized("wellness_exam_one_thing_cta"),
                    systemImage: "target"
                )
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color(hex: "8B5CF6"))
        }
    }

    private func openWellnessScreen(_ screen: NavigationManager.ALADDINScreen) {
        navigationManager.navigateToWellnessScreen(screen, returnTo: .wellnessHub)
    }

    private func formatCountdown(_ seconds: Int) -> String {
        if seconds <= 0 { return localizationManager.localized("wellness_exam_started") }
        let h = seconds / 3600
        let m = (seconds % 3600) / 60
        return String(format: localizationManager.localized("wellness_exam_countdown_format"), h, m)
    }

    @MainActor
    private func loadPlan() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let response = try await WellnessAPIService.shared.fetchExamPlan()
            plan = response.plan
            if let iso = response.plan?.examAt {
                let f = ISO8601DateFormatter()
                f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                if let d = f.date(from: iso) ?? ISO8601DateFormatter().date(from: iso) {
                    examDate = d
                }
            }
            title = response.plan?.title ?? ""
            parentDigest = response.plan?.parentDigest ?? false
        } catch {
            errorText = localizationManager.localized("wellness_exam_load_failed")
        }
    }

    @MainActor
    private func savePlan() async {
        isSaving = true
        errorText = nil
        defer { isSaving = false }
        let iso = ISO8601DateFormatter().string(from: examDate)
        do {
            let response = try await WellnessAPIService.shared.saveExamPlan(
                examAt: iso,
                title: title.isEmpty ? nil : title,
                parentDigest: parentDigest
            )
            plan = response.plan
            HapticFeedback.notification(.success)
        } catch {
            errorText = localizationManager.localized("wellness_exam_save_failed")
        }
    }
}

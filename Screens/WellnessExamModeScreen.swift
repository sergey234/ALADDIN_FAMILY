import SwiftUI
import UIKit

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
            ScrollView(.vertical, showsIndicators: true) {
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
                    .colorScheme(.dark)

                    TextField(
                        localizationManager.localized("wellness_exam_title_placeholder"),
                        text: $title
                    )
                    .wellnessReadableInput()

                    Toggle(
                        localizationManager.localized("wellness_exam_parent_digest"),
                        isOn: $parentDigest
                    )
                    .toggleStyle(SwitchToggleStyle(tint: Color(hex: "8B5CF6")))
                    .foregroundColor(.white)

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

                    if isLoading && plan == nil {
                        ProgressView()
                            .tint(.white)
                            .frame(maxWidth: .infinity)
                    }

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
            .aladdinChatKeyboardDismiss()
            .aladdinKeyboardDoneToolbar(
                title: localizationManager.localized("companion_conversation_done"),
                action: {
                    UIApplication.shared.sendAction(
                        #selector(UIResponder.resignFirstResponder),
                        to: nil,
                        from: nil,
                        for: nil
                    )
                }
            )
        }
        .navigationBarHidden(true)
        .accessibilityIdentifier("wellness_exam_mode_screen")
        .task { await loadPlan() }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.wellnessGoBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
                    .foregroundColor(.white)
            }
            Text(localizationManager.localized("wellness_exam_title"))
                .font(.headline.bold())
                .foregroundColor(.white)
            Spacer()
        }
    }

    @ViewBuilder
    private func countdownCard(_ plan: WellnessExamPlanDTO) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("wellness_exam_countdown_title"))
                .font(.subheadline.bold())
                .foregroundColor(.white)
            if let seconds = plan.secondsUntil {
                Text(formatCountdown(seconds))
                    .font(.title2.monospacedDigit().bold())
                    .foregroundColor(.white)
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
        if let local = WellnessExamLocalStore.load() {
            apply(plan: local)
        }
        do {
            let response = try await WellnessAPIService.shared.fetchExamPlan()
            if let remote = response.plan {
                apply(plan: remote)
                WellnessExamLocalStore.save(remote)
            }
            errorText = nil
        } catch {
            if plan == nil {
                errorText = localizationManager.localized("wellness_exam_load_failed")
            } else {
                errorText = localizationManager.localized("wellness_exam_offline_saved")
            }
        }
    }

    @MainActor
    private func savePlan() async {
        isSaving = true
        errorText = nil
        defer { isSaving = false }
        let iso = ISO8601DateFormatter().string(from: examDate)
        let localPlan = WellnessExamLocalStore.makePlan(
            examAt: iso,
            title: title.isEmpty ? nil : title,
            parentDigest: parentDigest,
            examDate: examDate
        )
        do {
            let response = try await WellnessAPIService.shared.saveExamPlan(
                examAt: iso,
                title: title.isEmpty ? nil : title,
                parentDigest: parentDigest
            )
            plan = response.plan ?? localPlan
            WellnessExamLocalStore.save(plan ?? localPlan)
            HapticFeedback.notification(.success)
        } catch {
            plan = localPlan
            WellnessExamLocalStore.save(localPlan)
            errorText = localizationManager.localized("wellness_exam_offline_saved")
            HapticFeedback.notification(.success)
        }
    }

    private func apply(plan remote: WellnessExamPlanDTO) {
        plan = remote
        if let iso = remote.examAt {
            let f = ISO8601DateFormatter()
            f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            if let d = f.date(from: iso) ?? ISO8601DateFormatter().date(from: iso) {
                examDate = d
            }
        }
        title = remote.title ?? ""
        parentDigest = remote.parentDigest ?? false
    }
}

// MARK: - Offline exam plan (P0 E)

private enum WellnessExamLocalStore {
    private static let key = "wellness_exam_plan_offline_v1"

    static func load() -> WellnessExamPlanDTO? {
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(WellnessExamPlanDTO.self, from: data)
    }

    static func save(_ plan: WellnessExamPlanDTO) {
        guard let data = try? JSONEncoder().encode(plan) else { return }
        UserDefaults.standard.set(data, forKey: key)
    }

    static func makePlan(
        examAt: String,
        title: String?,
        parentDigest: Bool,
        examDate: Date,
        now: Date = Date()
    ) -> WellnessExamPlanDTO {
        let seconds = max(0, Int(examDate.timeIntervalSince(now)))
        let phase: String
        if seconds <= 0 {
            phase = "past"
        } else if seconds <= 5 * 60 {
            phase = "final_5min"
        } else if seconds <= 24 * 3600 {
            phase = "day_before"
        } else {
            phase = "scheduled"
        }
        return WellnessExamPlanDTO(
            examAt: examAt,
            title: title,
            parentDigest: parentDigest,
            secondsUntil: seconds,
            phase: phase,
            suggestBreathing: true,
            suggestOneThing: true
        )
    }
}

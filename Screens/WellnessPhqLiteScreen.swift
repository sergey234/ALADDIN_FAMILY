import SwiftUI

/// fws-15 — PHQ-lite (5), teen variant with parent-share + crisis path.
struct WellnessPhqLiteScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var schema: WellnessPhqLiteSchemaResponse?
    @State private var answers: [Int] = Array(repeating: 0, count: 5)
    @State private var step = 0
    @State private var result: WellnessPhqSubmitResponse?
    @State private var errorText: String?
    @State private var parentShareEnabled = false
    @State private var isSavingShare = false
    @State private var showCrisisSheet = false

    private var isTeen: Bool {
        let role = (UserDefaults.standard.string(forKey: "current_user_role") ?? "").lowercased()
        return role.contains("teen") || role.contains("подрост")
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    if isTeen {
                        teenPrivacyCard
                    }
                    if let result {
                        resultView(result)
                    } else if let schema {
                        Text(schema.disclaimer)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.75))
                        if isTeen {
                            Text(localizationManager.localized("wellness_assessment_crisis_hint_teen"))
                                .font(.caption.weight(.semibold))
                                .foregroundColor(.warningOrange)
                        }
                        if step < schema.questions.count {
                            Text(schema.questions[step].text)
                                .font(.body.bold())
                            ForEach(schema.answerOptions) { opt in
                                Button {
                                    answers[step] = opt.value
                                    if step < 4 {
                                        step += 1
                                    } else {
                                        Task { await submit() }
                                    }
                                } label: {
                                    Text(localizationManager.localized(opt.labelKey))
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .padding(12)
                                        .stormGlassCard(cornerRadius: 10)
                                        .overlay {
                                            RoundedRectangle(cornerRadius: 10)
                                                .fill(answers[step] == opt.value ? Color(hex: "8B5CF6").opacity(0.25) : Color.clear)
                                        }
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    } else if let errorText {
                        Text(errorText).foregroundStyle(.orange)
                    } else {
                        ProgressView().tint(.white)
                    }
                }
                .padding()
            }
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .task { await loadSchema() }
        .fullScreenCover(isPresented: $showCrisisSheet) {
            WellnessReferralSheet(level: "L3", notifyParentsOnLoad: false, allowDismiss: true)
                .environmentObject(localizationManager)
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.wellnessGoBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(localizationManager.localized("wellness_assessment_phq_lite_title"))
                    .font(.headline.bold())
                if isTeen {
                    Text(localizationManager.localized("wellness_assessment_phq_lite_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
            }
            Spacer()
        }
    }

    private var teenPrivacyCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("wellness_teen_privacy_crisis_only"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
            Text(localizationManager.localized("wellness_trust_crisis_no_chat_log"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.7))
            Toggle(isOn: $parentShareEnabled) {
                Text(localizationManager.localized("wellness_teen_parent_share_toggle"))
                    .font(.subheadline)
            }
            .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
            .onChange(of: parentShareEnabled) { enabled in
                Task { await saveParentShare(enabled) }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private func resultView(_ r: WellnessPhqSubmitResponse) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(r.disclaimer).font(.caption).foregroundColor(.white.opacity(0.75))
            Text(String(format: localizationManager.localized("wellness_phq_result_score"), r.score))
                .font(.title3.bold())
            if r.suggestProfessional {
                Text(localizationManager.localized("wellness_assessment_result_moderate"))
                    .foregroundStyle(.orange)
            } else {
                Text(localizationManager.localized("wellness_assessment_result_mild"))
                    .foregroundStyle(.white.opacity(0.85))
            }
            if isTeen {
                Text(localizationManager.localized("wellness_teen_phq_parent_aggregate_hint"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            }
            if r.openCrisisSheet == true || r.escalationLevel == "L3" {
                Button {
                    showCrisisSheet = true
                } label: {
                    Label(
                        localizationManager.localized("wellness_crisis_one_tap_title"),
                        systemImage: "phone.fill"
                    )
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.dangerRed)
            }
            Button {
                navigationManager.wellnessGoBack()
            } label: {
                Text(localizationManager.localized("wellness_assessment_finish"))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color(hex: "8B5CF6"))
        }
    }

    private func loadSchema() async {
        do {
            schema = try await WellnessAPIService.shared.fetchPhqLiteSchema()
            if isTeen {
                let settings = try? await WellnessAPIService.shared.fetchSettings()
                parentShareEnabled = (settings?.settings.parentShareAggregate ?? 0) == 1
            }
        } catch {
            errorText = localizationManager.localized("wellness_assessment_blocked_child")
        }
    }

    private func submit() async {
        do {
            result = try await WellnessAPIService.shared.submitPhqLite(answers: answers)
            if result?.openCrisisSheet == true {
                showCrisisSheet = true
            }
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }

    private func saveParentShare(_ enabled: Bool) async {
        guard isTeen, !isSavingShare else { return }
        isSavingShare = true
        defer { isSavingShare = false }
        _ = try? await WellnessAPIService.shared.setParentShareAggregate(enabled)
    }
}

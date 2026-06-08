import SwiftUI

/// p2-03 — PHQ-lite / PHQ-9 / GAD-7 shared flow (screening, not diagnosis).
struct WellnessAssessmentFlowScreen: View {
    enum Kind: String {
        case phqLite
        case phq9
        case gad7
        case mbiLite

        static func fromStore() -> Kind {
            Kind(rawValue: WellnessSessionStore.assessmentFlowKind) ?? .phqLite
        }

        var titleKey: String {
            switch self {
            case .phqLite: return "wellness_assessment_phq_lite_title"
            case .phq9: return "wellness_assessment_phq9_title"
            case .gad7: return "wellness_assessment_gad7_title"
            case .mbiLite: return "wellness_assessment_mbi_title"
            }
        }
    }

    let kind: Kind

    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var schema: WellnessPhqLiteSchemaResponse?
    @State private var answers: [Int] = []
    @State private var step = 0
    @State private var result: WellnessPhqSubmitResponse?
    @State private var crisisFlag = false
    @State private var errorText: String?
    @State private var showReferralSheet = false
    @State private var referralLevel = "L2"

    private var ageBand: String {
        WellnessSessionStore.cachedAgeBand ?? CompanionUserContext.companionAgeBand
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    if let result {
                        resultView(result)
                    } else if let schema {
                        Text(schema.disclaimer)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.75))
                        if step < schema.questions.count {
                            Text(
                                String(
                                    format: localizationManager.localized("wellness_assessment_progress"),
                                    step + 1,
                                    schema.questions.count
                                )
                            )
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.75))
                            Text(schema.questions[step].text)
                                .font(.body.bold())
                            ForEach(schema.answerOptions) { opt in
                                Button {
                                    answers[step] = opt.value
                                    if step < schema.questions.count - 1 {
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
                                                .fill(
                                                    answers[step] == opt.value
                                                        ? Color(hex: "8B5CF6").opacity(0.25)
                                                        : Color.clear
                                                )
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
        .sheet(isPresented: $showReferralSheet) {
            WellnessReferralSheet(level: referralLevel)
                .environmentObject(localizationManager)
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            Text(localizationManager.localized(kind.titleKey))
                .font(.headline.bold())
            Spacer()
        }
    }

    private func resultView(_ r: WellnessPhqSubmitResponse) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(r.disclaimer).font(.caption).foregroundColor(.white.opacity(0.75))
            Text(String(format: localizationManager.localized("wellness_phq_result_score"), r.score))
                .font(.title3.bold())
            if crisisFlag {
                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_assessment_crisis_hint", ageBand: ageBand))
                    .foregroundStyle(.red)
                Button {
                    referralLevel = "L3"
                    showReferralSheet = true
                } label: {
                    Text(localizationManager.localized("wellness_helpline_open"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)
                Button {
                    navigationManager.navigateTo(.wellnessTrust)
                } label: {
                    Text(localizationManager.localized("wellness_trust_title"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            } else if r.suggestProfessional {
                Text(localizationManager.localized("wellness_assessment_result_moderate"))
                    .foregroundStyle(.orange)
                Button {
                    referralLevel = "L2"
                    showReferralSheet = true
                } label: {
                    Text(localizationManager.localized("wellness_helpline_open"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            } else {
                Text(localizationManager.localized("wellness_assessment_result_mild"))
            }
            Button {
                navigationManager.goBack()
            } label: {
                Text(localizationManager.localized("wellness_assessment_finish"))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private func loadSchema() async {
        do {
            switch kind {
            case .phqLite:
                schema = try await WellnessAPIService.shared.fetchPhqLiteSchema()
                answers = Array(repeating: 0, count: 5)
            case .phq9:
                schema = try await WellnessAPIService.shared.fetchPhq9Schema()
                answers = Array(repeating: 0, count: 9)
            case .gad7:
                schema = try await WellnessAPIService.shared.fetchGad7Schema()
                answers = Array(repeating: 0, count: 7)
            case .mbiLite:
                schema = try await WellnessAPIService.shared.fetchMbiLiteSchema()
                answers = Array(repeating: 0, count: 5)
            }
            step = 0
        } catch {
            errorText = localizationManager.localized("wellness_assessment_blocked_child")
        }
    }

    private func submit() async {
        do {
            switch kind {
            case .phqLite:
                result = try await WellnessAPIService.shared.submitPhqLite(answers: answers)
            case .phq9:
                let r = try await WellnessAPIService.shared.submitPhq9(answers: answers)
                result = r
                crisisFlag = r.crisisFlag ?? false
            case .gad7:
                result = try await WellnessAPIService.shared.submitGad7(answers: answers)
            case .mbiLite:
                result = try await WellnessAPIService.shared.submitMbiLite(answers: answers)
            }
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }
}

/// Hub: выбор опросника (teen+).
struct WellnessAssessmentsHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    private var showsMbiLite: Bool {
        let band = CompanionUserContext.companionAgeBand
        return band == "parent" || band == "senior" || band == "adult_app"
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Button { navigationManager.goBack() } label: {
                        Image(systemName: "chevron.left")
                    }
                    Text(localizationManager.localized("wellness_assessments_hub_title"))
                        .font(.headline.bold())
                    Spacer()
                }
                Text(localizationManager.localized("wellness_assessment_disclaimer"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
                assessmentRow(
                    titleKey: "wellness_assessment_phq_lite_title",
                    subtitleKey: "wellness_assessment_phq_lite_subtitle",
                    kind: .phqLite
                )
                assessmentRow(
                    titleKey: "wellness_assessment_phq9_title",
                    subtitleKey: "wellness_assessment_phq9_subtitle",
                    kind: .phq9
                )
                assessmentRow(
                    titleKey: "wellness_assessment_gad7_title",
                    subtitleKey: "wellness_assessment_gad7_subtitle",
                    kind: .gad7
                )
                if showsMbiLite {
                    assessmentRow(
                        titleKey: "wellness_assessment_mbi_title",
                        subtitleKey: "wellness_assessment_mbi_subtitle",
                        kind: .mbiLite
                    )
                }
            }
            .padding()
        }
    }

    private func assessmentRow(
        titleKey: String,
        subtitleKey: String,
        kind: WellnessAssessmentFlowScreen.Kind
    ) -> some View {
        Button {
            WellnessSessionStore.setAssessmentFlowKind(kind)
            navigationManager.navigateTo(.wellnessAssessmentFlow)
        } label: {
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized(titleKey))
                    .font(.subheadline.bold())
                Text(localizationManager.localized(subtitleKey))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(14)
            .stormGlassCard(cornerRadius: 12)
        }
        .buttonStyle(.plain)
    }
}

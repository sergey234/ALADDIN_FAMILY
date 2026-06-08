import SwiftUI

/// p1-06 iOS — PHQ-lite (5), not a diagnosis.
struct WellnessPhqLiteScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var schema: WellnessPhqLiteSchemaResponse?
    @State private var answers: [Int] = Array(repeating: 0, count: 5)
    @State private var step = 0
    @State private var result: WellnessPhqSubmitResponse?
    @State private var errorText: String?

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
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("wellness_assessment_phq_lite_title"))
                .font(.headline.bold())
            Spacer()
        }
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
            }
            Button {
                navigationManager.goBack()
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
        } catch {
            errorText = localizationManager.localized("wellness_assessment_blocked_child")
        }
    }

    private func submit() async {
        do {
            result = try await WellnessAPIService.shared.submitPhqLite(answers: answers)
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }
}

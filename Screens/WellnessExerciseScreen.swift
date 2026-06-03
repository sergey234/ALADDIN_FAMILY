import SwiftUI

/// p2-21 — structured exercise from Knowledge Pack.
struct WellnessExerciseScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var catalog: [WellnessExerciseCatalogItem] = []
    @State private var session: WellnessExerciseSessionDTO?
    @State private var answerText = ""
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showOutcomeSheet = false

    private var pillar: String {
        WellnessSessionStore.exercisePillar ?? "humanistic"
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header
                if let errorText {
                    Text(errorText).foregroundStyle(.orange)
                }
                if let session {
                    exerciseFlow(session)
                } else if isLoading {
                    ProgressView()
                } else {
                    catalogList
                }
            }
            .padding()
        }
        .accessibilityIdentifier("wellness_exercise_screen")
        .task { await bootstrap() }
        .sheet(isPresented: $showOutcomeSheet) {
            WellnessOutcomeSheet(pillar: pillar) {
                navigationManager.finishWellnessFlow()
            }
            .environmentObject(localizationManager)
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
            }
            Text(localizationManager.localized("wellness_exercise_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private var catalogList: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("wellness_exercise_pick"))
                .font(.subheadline)
                .foregroundStyle(.secondary)
            ForEach(catalog) { item in
                Button {
                    Task { await start(item) }
                } label: {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(item.exerciseId.replacingOccurrences(of: "_", with: " "))
                            .font(.subheadline.bold())
                        if let hint = item.introHint, !hint.isEmpty {
                            Text(hint).font(.caption).foregroundStyle(.secondary)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(12)
                    .background(Color.purple.opacity(0.08))
                    .cornerRadius(12)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func exerciseFlow(_ s: WellnessExerciseSessionDTO) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(
                String(
                    format: localizationManager.localized("wellness_exercise_step"),
                    s.stepIndex,
                    s.stepTotal
                )
            )
            .font(.caption.bold())
            .foregroundStyle(.secondary)
            Text(s.hint)
                .font(.body)
            if !s.completed {
                WellnessMultilineField(
                    title: localizationManager.localized("wellness_exercise_answer_placeholder"),
                    text: $answerText
                )
                .textFieldStyle(.roundedBorder)
                Button {
                    Task { await advance(s) }
                } label: {
                    Text(localizationManager.localized("wellness_exercise_next"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
            } else {
                Text(localizationManager.localized("wellness_exercise_done"))
                    .font(.headline)
                Button {
                    showOutcomeSheet = true
                } label: {
                    Text(localizationManager.localized("wellness_outcome_prompt"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .accessibilityIdentifier("wellness_exercise_open_outcome")
                Button {
                    navigationManager.popToWellnessHub()
                } label: {
                    Text(localizationManager.localized("wellness_outcome_skip"))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }
        }
    }

    private func bootstrap() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        if let active = try? await WellnessAPIService.shared.fetchActiveExercise().active,
           active.completed == false {
            session = active
            return
        }
        do {
            let resp = try await WellnessAPIService.shared.fetchExerciseCatalog(pillar: pillar)
            catalog = resp.exercises
        } catch {
            errorText = localizationManager.localized("wellness_error_offline_pillars")
        }
    }

    private func start(_ item: WellnessExerciseCatalogItem) async {
        do {
            let resp = try await WellnessAPIService.shared.startExercise(
                pillar: pillar,
                exerciseId: item.exerciseId
            )
            session = resp.session
            answerText = ""
        } catch {
            errorText = localizationManager.localized("wellness_error_pillar")
        }
    }

    private func advance(_ s: WellnessExerciseSessionDTO) async {
        let text = answerText.trimmingCharacters(in: .whitespacesAndNewlines)
        do {
            let resp = try await WellnessAPIService.shared.advanceExercise(
                id: s.id,
                answer: text.isEmpty ? nil : text
            )
            session = resp.session
            answerText = ""
            if resp.session.completed {
                showOutcomeSheet = true
            }
        } catch {
            errorText = localizationManager.localized("wellness_error_pillar")
        }
    }
}

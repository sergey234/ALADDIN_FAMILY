import SwiftUI

/// Child-facing baseline flow: study 5 words (≤2 min) → ordered recall (B12-T01).
struct MnemoBaselineAssessmentView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    var onCompleted: ((MnemonicBaselineAssessment.SessionResult) -> Void)? = nil

    private enum Phase {
        case study
        case recall
        case done
    }

    @State private var phase: Phase = .study
    @State private var secondsRemaining = MnemonicBaselineAssessment.timeLimitSeconds
    @State private var studyElapsed = 0
    @State private var targetWords: [String] = []
    @State private var recallChoices: [String] = []
    @State private var recallPicks: [String] = []
    @State private var sessionResult: MnemonicBaselineAssessment.SessionResult?
    @State private var recallFeedbackKey: String?

    private let studyTimer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    switch phase {
                    case .study:
                        studySection
                    case .recall:
                        recallSection
                    case .done:
                        doneSection
                    }
                }
                .padding(16)
            }
            .navigationTitle(localizationManager.localized("child_mnemo_baseline_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("child_interface_back")) {
                        dismiss()
                    }
                }
            }
        }
        .onAppear {
            targetWords = MnemonicBaselineAssessment.wordLocalizationKeys.map {
                localizationManager.localized($0)
            }
            recallChoices = targetWords.shuffled()
        }
        .onReceive(studyTimer) { _ in
            guard phase == .study else { return }
            if secondsRemaining > 0 {
                secondsRemaining -= 1
                studyElapsed += 1
            } else {
                beginRecall()
            }
        }
        .accessibilityIdentifier("child_mnemo_baseline_sheet")
    }

    private var studySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_baseline_subtitle"))
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.secondary)

            Text(
                String(
                    format: localizationManager.localized("child_mnemo_baseline_timer"),
                    secondsRemaining / 60,
                    secondsRemaining % 60
                )
            )
            .font(.system(size: 15, weight: .bold))
            .foregroundColor(.indigo)
            .accessibilityIdentifier("child_mnemo_baseline_timer")

            Text(localizationManager.localized("child_mnemo_baseline_study_hint"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)

            ForEach(Array(targetWords.enumerated()), id: \.offset) { index, word in
                Text("\(index + 1). \(word)")
                    .font(.system(size: 16, weight: .semibold))
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))
            }

            Button(localizationManager.localized("child_mnemo_baseline_start_recall")) {
                beginRecall()
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("child_mnemo_baseline_start_recall")
        }
    }

    private var recallSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_baseline_recall_title"))
                .font(.system(size: 15, weight: .semibold))

            if !recallPicks.isEmpty {
                Text(recallPicks.enumerated().map { "\($0.offset + 1). \($0.element)" }.joined(separator: " → "))
                    .font(.system(size: 14, weight: .semibold))
            }

            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 2), spacing: 8) {
                ForEach(recallChoices, id: \.self) { word in
                    Button(word) {
                        appendRecallWord(word)
                    }
                    .buttonStyle(.bordered)
                    .disabled(recallPicks.count >= targetWords.count)
                }
            }

            if let recallFeedbackKey {
                Text(localizationManager.localized(recallFeedbackKey))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(recallFeedbackKey.contains("ok") ? .green : .orange)
            }
        }
    }

    private var doneSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let sessionResult {
                Text(
                    String(
                        format: localizationManager.localized("child_mnemo_baseline_score"),
                        sessionResult.correctCount,
                        sessionResult.wordCount,
                        sessionResult.rawScorePercent
                    )
                )
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.green)
                .accessibilityIdentifier("child_mnemo_baseline_score")

                Text(
                    String(
                        format: localizationManager.localized("child_mnemo_baseline_mq"),
                        sessionResult.memoryQuotient
                    )
                )
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.purple)
                .accessibilityIdentifier("child_mnemo_baseline_mq")
            }

            Button(localizationManager.localized("child_interface_done")) {
                dismiss()
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private func beginRecall() {
        phase = .recall
        recallPicks = []
        recallFeedbackKey = nil
        recallChoices = targetWords.shuffled()
    }

    private func appendRecallWord(_ word: String) {
        guard recallPicks.count < targetWords.count else { return }
        recallPicks.append(word)
        guard recallPicks.count == targetWords.count else { return }

        let correct = zip(recallPicks, targetWords).filter { $0.0 == $0.1 }.count
        if recallPicks == targetWords {
            finishAssessment(correctCount: correct)
        } else {
            recallFeedbackKey = "child_mnemo_baseline_recall_retry"
            recallPicks = []
        }
    }

    private func finishAssessment(correctCount: Int) {
        let result = MnemonicBaselineAssessment.shared.recordResult(
            correctCount: correctCount,
            elapsedStudySeconds: studyElapsed,
            childId: MnemonicBaselineAssessment.activeChildId()
        )
        sessionResult = result
        recallFeedbackKey = "child_mnemo_baseline_recall_ok"
        phase = .done
        MnemonicSkillTracker.shared.recordSuccessfulRecall(count: correctCount)
        onCompleted?(result)
    }
}

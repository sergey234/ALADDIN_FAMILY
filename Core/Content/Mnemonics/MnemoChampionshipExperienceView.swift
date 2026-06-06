import SwiftUI

/// games.05 championship variant — 20 pegs / 5 min study → ordered recall; personal best only (B12-T06).
struct MnemoChampionshipExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    private enum Phase {
        case study
        case recall
        case done
    }

    @State private var phase: Phase = .study
    @State private var secondsRemaining = MnemonicChampionshipStore.timeLimitSeconds
    @State private var studyElapsed = 0
    @State private var targetSequence: [Int] = []
    @State private var recallPicks: [Int] = []
    @State private var sessionResult: MnemonicChampionshipStore.SessionResult?
    @State private var recallFeedbackKey: String?

    private let studyTimer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_championship_title"))
                .font(.system(size: 17, weight: .bold))

            Text(localizationManager.localized("child_mnemo_championship_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            let best = MnemonicChampionshipStore.shared.personalBest(
                childId: MnemonicBaselineAssessment.activeChildId()
            )
            if best > 0 {
                Text(
                    String(
                        format: localizationManager.localized("child_mnemo_championship_personal_best"),
                        best,
                        MnemonicChampionshipStore.itemCount
                    )
                )
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.purple)
                .accessibilityIdentifier("child_mnemo_championship_personal_best")
            }

            switch phase {
            case .study:
                studySection
            case .recall:
                recallSection
            case .done:
                doneSection
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onAppear {
            if targetSequence.isEmpty {
                targetSequence = MnemonicChampionshipStore.shared.makeSequence()
            }
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
        .accessibilityIdentifier("child_mnemo_championship_experience")
    }

    private var studySection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(
                String(
                    format: localizationManager.localized("child_mnemo_championship_timer"),
                    secondsRemaining / 60,
                    secondsRemaining % 60
                )
            )
            .font(.system(size: 15, weight: .bold))
            .foregroundColor(.indigo)
            .accessibilityIdentifier("child_mnemo_championship_timer")

            Text(localizationManager.localized("child_mnemo_championship_study_hint"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)

            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 6), count: 5), spacing: 6) {
                ForEach(Array(targetSequence.enumerated()), id: \.offset) { index, peg in
                    VStack(spacing: 2) {
                        Text("\(index + 1)")
                            .font(.system(size: 10, weight: .bold))
                            .foregroundColor(.secondary)
                        Text(MnemonicChampionshipStore.journeyPegEmojis[peg])
                            .font(.system(size: 22))
                    }
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .background(RoundedRectangle(cornerRadius: 8).fill(Color.indigo.opacity(0.08)))
                }
            }

            Button(localizationManager.localized("child_mnemo_championship_start_recall")) {
                beginRecall()
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("child_mnemo_championship_start_recall")
        }
    }

    private var recallSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_mnemo_championship_recall_title"))
                .font(.system(size: 14, weight: .semibold))

            Text(
                String(
                    format: localizationManager.localized("child_mnemo_championship_recall_progress"),
                    recallPicks.count,
                    MnemonicChampionshipStore.itemCount
                )
            )
            .font(.system(size: 12, weight: .medium))
            .foregroundColor(.secondary)

            if !recallPicks.isEmpty {
                Text(recallPicks.map { MnemonicChampionshipStore.journeyPegEmojis[$0] }.joined(separator: " "))
                    .font(.system(size: 16, weight: .bold))
                    .frame(maxWidth: .infinity, alignment: .center)
                    .lineLimit(2)
                    .minimumScaleFactor(0.7)
            }

            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 5), spacing: 8) {
                ForEach(Array(0..<MnemonicChampionshipStore.itemCount), id: \.self) { peg in
                    Button(MnemonicChampionshipStore.journeyPegEmojis[peg]) {
                        appendRecallPeg(peg)
                    }
                    .font(.system(size: 24))
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .buttonStyle(.bordered)
                    .disabled(recallPicks.count >= MnemonicChampionshipStore.itemCount)
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
        VStack(alignment: .leading, spacing: 10) {
            if let sessionResult {
                Text(
                    String(
                        format: localizationManager.localized("child_mnemo_championship_score"),
                        sessionResult.correctCount,
                        sessionResult.itemCount
                    )
                )
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.green)
                .accessibilityIdentifier("child_mnemo_championship_score")

                if sessionResult.isPersonalBest {
                    Text(localizationManager.localized("child_mnemo_championship_new_best"))
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.purple)
                        .accessibilityIdentifier("child_mnemo_championship_new_best")
                }
            }

            Button(localizationManager.localized("child_interface_done")) {
                Task { await onComplete() }
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private func beginRecall() {
        phase = .recall
        recallPicks = []
        recallFeedbackKey = nil
    }

    private func appendRecallPeg(_ peg: Int) {
        guard recallPicks.count < MnemonicChampionshipStore.itemCount else { return }
        recallPicks.append(peg)
        guard recallPicks.count == MnemonicChampionshipStore.itemCount else { return }

        let correctCount = zip(recallPicks, targetSequence).filter { $0.0 == $0.1 }.count
        finishChampionship(correctCount: correctCount)
    }

    private func finishChampionship(correctCount: Int) {
        let result = MnemonicChampionshipStore.shared.recordResult(
            correctCount: correctCount,
            elapsedStudySeconds: studyElapsed,
            childId: MnemonicBaselineAssessment.activeChildId()
        )
        sessionResult = result
        recallFeedbackKey = correctCount == MnemonicChampionshipStore.itemCount
            ? "child_mnemo_championship_recall_ok"
            : "child_mnemo_championship_recall_partial"
        phase = .done
        MnemonicSRSStore.shared.recordSuccess(itemId: item.id)
        MnemonicSkillTracker.shared.recordSuccessfulRecall(count: correctCount)
        if correctCount >= MnemonicChampionshipStore.itemCount / 2 {
            MnemonicRewardBridge.award(.memoryGame, itemId: item.id)
        }
    }
}

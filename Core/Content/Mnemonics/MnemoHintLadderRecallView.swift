import SwiftUI

/// RECALL UI — progressive hints without harsh red-X feedback (B14-T04).
struct MnemoHintLadderRecallView: View {
    @ObservedObject var localizationManager: LocalizationManager
    let itemId: String
    let attemptKey: String
    let prompt: String
    let options: [String]
    let correctIndex: Int
    let pictogramRevision: Int
    let onSelectAnswer: (Int) -> Void

    @State private var level: MnemonicHintLadder.Level = .image
    @State private var pendingSelection: Int?
    @State private var showGentleRetry = false
    @State private var showMicroWinToast = false

    private var correctAnswer: String {
        guard options.indices.contains(correctIndex) else { return "" }
        return options[correctIndex]
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            hintLadderStepHeader

            Text(prompt)
                .font(.system(size: 16, weight: .semibold))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))

            if level.rawValue >= MnemonicHintLadder.Level.image.rawValue {
                MnemoPictogramRecallHint(localizationManager: localizationManager, itemId: itemId)
                    .id(pictogramRevision)
            }

            switch level {
            case .image:
                imageLevelSection
            case .letter:
                letterLevelSection
            case .threeChoice:
                choiceLevelSection
            }

            if showMicroWinToast {
                Text(localizationManager.localized("child_mnemo_reward_micro_win"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.purple)
                    .accessibilityIdentifier("child_mnemo_micro_win_toast")
            }
        }
        .accessibilityIdentifier("child_mnemo_hint_ladder_recall")
        .onChange(of: pictogramRevision) { _ in
            level = .image
            pendingSelection = nil
        }
    }

    private var hintLadderStepHeader: some View {
        HStack(spacing: 8) {
            ForEach(MnemonicHintLadder.Level.allCases) { step in
                VStack(spacing: 4) {
                    Circle()
                        .fill(step.rawValue <= level.rawValue ? Color.purple.opacity(0.95) : Color.gray.opacity(0.3))
                        .frame(width: 8, height: 8)
                    Text(localizationManager.localized(step.localizationKey))
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
                .frame(maxWidth: .infinity)
                .accessibilityIdentifier("child_mnemo_hint_ladder_step_\(step.rawValue)")
            }
        }
    }

    private var imageLevelSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_mnemo_hint_ladder_recall_image_prompt"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)

            Button(localizationManager.localized("child_mnemo_hint_ladder_show_letter")) {
                level = .letter
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("child_mnemo_hint_ladder_show_letter")
        }
    }

    private var letterLevelSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(
                String(
                    format: localizationManager.localized("child_mnemo_hint_ladder_letter_format"),
                    MnemonicHintLadder.firstLetter(from: correctAnswer)
                )
            )
            .font(.system(size: 15, weight: .semibold))
            .foregroundColor(.purple)
            .accessibilityIdentifier("child_mnemo_hint_ladder_letter_hint")

            Button(localizationManager.localized("child_mnemo_hint_ladder_show_choices")) {
                level = .threeChoice
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("child_mnemo_hint_ladder_show_choices")
        }
    }

    private var choiceLevelSection: some View {
        VStack(spacing: 8) {
            if showGentleRetry {
                Text(localizationManager.localized("child_mnemo_hint_ladder_try_again"))
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.orange)
            }

            ForEach(Array(options.enumerated()), id: \.offset) { index, option in
                Button {
                    handleChoice(index)
                } label: {
                    Text(option)
                        .font(.system(size: 15, weight: .semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .foregroundColor(.white)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(choiceBackgroundColor(index: index))
                        )
                }
                .disabled(pendingSelection != nil)
                .accessibilityIdentifier("child_mnemo_hint_ladder_choice_\(index)")
            }
        }
    }

    private func handleChoice(_ index: Int) {
        guard pendingSelection == nil else { return }
        pendingSelection = index
        if MnemonicRewardBridge.awardRecallAttempt(itemId: itemId, attemptKey: attemptKey) {
            showMicroWinToast = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
                showMicroWinToast = false
            }
        }
        if index == correctIndex {
            SoundEffectPlayer.shared.play(.success, priority: .medium)
            onSelectAnswer(index)
            pendingSelection = nil
        } else {
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
            showGentleRetry = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
                pendingSelection = nil
                showGentleRetry = false
            }
        }
    }

    private func choiceBackgroundColor(index: Int) -> Color {
        guard let pendingSelection else { return Color.indigo.opacity(0.85) }
        if index == correctIndex, pendingSelection == correctIndex {
            return Color.green.opacity(0.85)
        }
        if index == pendingSelection {
            return Color.orange.opacity(0.8)
        }
        return Color.gray.opacity(0.55)
    }
}

import SwiftUI

/// Metacognition — «какую технику выбрал?» after REWARD, age 13+ (B14-T06).
struct MnemoReflectPhaseView: View {
    @ObservedObject var localizationManager: LocalizationManager
    let correctTechnique: MnemonicTechnique
    let onComplete: () -> Void

    @State private var selectedTechnique: MnemonicTechnique?
    @State private var feedbackKey: String?

    private var techniqueOptions: [MnemonicTechnique] {
        var options: [MnemonicTechnique] = [correctTechnique]
        for technique in MnemonicTechnique.allCases where technique != .spacedReview {
            if options.count >= 3 { break }
            if technique != correctTechnique { options.append(technique) }
        }
        return options.shuffled()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_reflect_title"))
                .font(.system(size: 16, weight: .bold))

            Text(localizationManager.localized("child_mnemo_reflect_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            Text(localizationManager.localized("child_mnemo_reflect_prompt"))
                .font(.system(size: 15, weight: .semibold))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.purple.opacity(0.08)))

            if selectedTechnique == nil {
                VStack(spacing: 8) {
                    ForEach(techniqueOptions, id: \.rawValue) { technique in
                        Button(localizationManager.localized(technique.localizationKey)) {
                            handleSelection(technique)
                        }
                        .buttonStyle(.borderedProminent)
                        .frame(maxWidth: .infinity)
                        .accessibilityIdentifier("child_mnemo_reflect_option_\(technique.rawValue)")
                    }
                }
            } else if let feedbackKey {
                Text(localizationManager.localized(feedbackKey))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(feedbackKey == "child_mnemo_reflect_feedback_ok" ? .green : .orange)

                if feedbackKey == "child_mnemo_reflect_feedback_hint" {
                    Text(
                        String(
                            format: localizationManager.localized("child_mnemo_reflect_technique_format"),
                            localizationManager.localized(correctTechnique.localizationKey)
                        )
                    )
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
                }

                Button(localizationManager.localized("child_interface_done")) {
                    onComplete()
                }
                .buttonStyle(.borderedProminent)
                .accessibilityIdentifier("child_mnemo_reflect_done")
            }
        }
        .accessibilityIdentifier("child_mnemo_reflect_phase")
    }

    private func handleSelection(_ technique: MnemonicTechnique) {
        selectedTechnique = technique
        if technique == correctTechnique {
            feedbackKey = "child_mnemo_reflect_feedback_ok"
            SoundEffectPlayer.shared.play(.success, priority: .medium)
        } else {
            feedbackKey = "child_mnemo_reflect_feedback_hint"
            SoundEffectPlayer.shared.play(.warning, priority: .low)
        }
        MasterLogger.shared.business(
            "MNEMO-B14 reflect technique=\(technique.rawValue) correct=\(correctTechnique.rawValue)"
        )
    }
}

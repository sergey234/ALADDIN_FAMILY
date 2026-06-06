import SwiftUI

/// Metacognition — выбор техники до урока, age 13+ (B14-T07).
struct MnemoTechniquePickerView: View {
    @ObservedObject var localizationManager: LocalizationManager
    let itemId: String
    let recommendedTechnique: MnemonicTechnique
    let onSelect: (MnemonicTechnique) -> Void

    @State private var selectedTechnique: MnemonicTechnique?

    private var techniqueOptions: [MnemonicTechnique] {
        MnemonicStudyTechniqueMap.pickerOptions(for: itemId)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_technique_picker_title"))
                .font(.system(size: 16, weight: .bold))

            Text(localizationManager.localized("child_mnemo_technique_picker_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            Text(localizationManager.localized(MnemonicStudyTechniqueMap.pickerContextKey(for: itemId)))
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.indigo)
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))

            Text(localizationManager.localized("child_mnemo_technique_picker_prompt"))
                .font(.system(size: 15))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.08)))

            if selectedTechnique == nil {
                VStack(spacing: 8) {
                    ForEach(techniqueOptions, id: \.rawValue) { technique in
                        Button {
                            handleSelection(technique)
                        } label: {
                            HStack {
                                Text(localizationManager.localized(technique.localizationKey))
                                Spacer()
                                if technique == recommendedTechnique {
                                    Text(localizationManager.localized("child_mnemo_technique_picker_recommended_badge"))
                                        .font(.system(size: 11, weight: .bold))
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(Capsule().fill(Color.green.opacity(0.2)))
                                }
                            }
                        }
                        .buttonStyle(.borderedProminent)
                        .frame(maxWidth: .infinity)
                        .accessibilityIdentifier("child_mnemo_technique_picker_option_\(technique.rawValue)")
                    }
                }
            } else if let selectedTechnique {
                Text(
                    String(
                        format: localizationManager.localized("child_mnemo_technique_picker_selected_format"),
                        localizationManager.localized(selectedTechnique.localizationKey)
                    )
                )
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.green)

                Button(localizationManager.localized("child_mnemo_technique_picker_continue")) {
                    onSelect(selectedTechnique)
                }
                .buttonStyle(.borderedProminent)
                .accessibilityIdentifier("child_mnemo_technique_picker_continue")
            }
        }
        .accessibilityIdentifier("child_mnemo_technique_picker_phase")
    }

    private func handleSelection(_ technique: MnemonicTechnique) {
        selectedTechnique = technique
        SoundEffectPlayer.shared.play(.success, priority: .low)
        MasterLogger.shared.business(
            "MNEMO-B14 technique pick=\(technique.rawValue) recommended=\(recommendedTechnique.rawValue) item=\(itemId)"
        )
    }
}

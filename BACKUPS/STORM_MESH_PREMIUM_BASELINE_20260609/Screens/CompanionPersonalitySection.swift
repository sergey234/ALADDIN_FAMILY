import SwiftUI

/// P1-04: свои инструкции и тон личности героя (семейный scope, только родитель).
struct CompanionPersonalitySection: View {
    @State private var customInstructions = ""
    @State private var personalityPreset = "friendly"
    @State private var securityExpertMode = false
    @State private var availablePresets: [String] = CompanionPersonalityPresets.allPresets
    @State private var isLoading = true
    @State private var isSaving = false
    @State private var statusMessage: String?
    @State private var errorText: String?

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: 8) {
                Text("✨")
                    .font(.title2)
                Text("Тон и инструкции героя")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }

            Text("Как Grok Custom Instructions: родитель задаёт стиль общения для всей семьи. Без телефонов, адресов и паролей.")
                .font(.caption)
                .foregroundColor(.textSecondary)

            if isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
            } else {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Стиль")
                        .font(.subheadline.weight(.semibold))
                    Picker("Стиль", selection: $personalityPreset) {
                        ForEach(availablePresets, id: \.self) { preset in
                            Text(CompanionProfileSettings.presetLabels[preset] ?? preset)
                                .tag(preset)
                        }
                    }
                    .pickerStyle(.segmented)
                }

                Toggle(isOn: $securityExpertMode) {
                    Text("Режим «эксперт безопасности» по умолчанию")
                        .font(.subheadline)
                }

                VStack(alignment: .leading, spacing: 6) {
                    Text("Свои инструкции (до 500 символов)")
                        .font(.subheadline.weight(.semibold))
                    TextEditor(text: $customInstructions)
                        .frame(minHeight: 88, maxHeight: 120)
                        .padding(8)
                        .background(Color.backgroundMedium.opacity(0.25))
                        .cornerRadius(10)
                        .onChange(of: customInstructions) { newValue in
                            if newValue.count > 500 {
                                customInstructions = String(newValue.prefix(500))
                            }
                        }
                    Text("\(customInstructions.count)/500")
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }

                Button {
                    Task { await save() }
                } label: {
                    HStack {
                        if isSaving { ProgressView().tint(.white) }
                        Text(isSaving ? "Сохраняем…" : "Сохранить тон и инструкции")
                    }
                    .font(.bodyBold)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                }
                .background(Color.secondaryGold.opacity(0.9), in: RoundedRectangle(cornerRadius: 12))
                .disabled(isSaving)

                if let statusMessage {
                    Text(statusMessage)
                        .font(.caption)
                        .foregroundColor(.green)
                }
                if let errorText {
                    Text(errorText)
                        .font(.caption)
                        .foregroundColor(.orange)
                }
            }
        }
        .padding(Spacing.m)
        .background(Color.secondaryGold.opacity(0.08))
        .cornerRadius(CornerRadius.medium)
        .task { await load() }
    }

    private func load() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let profile = try await CompanionAPIService.shared.fetchProfile()
            customInstructions = profile.customInstructions
            personalityPreset = profile.personalityPreset
            securityExpertMode = profile.securityExpertMode ?? false
            if let presets = profile.availablePresets, !presets.isEmpty {
                availablePresets = presets
            } else {
                availablePresets = CompanionPersonalityPresets.presetsForUI(ageBand: nil)
            }
            if !availablePresets.contains(personalityPreset) {
                personalityPreset = availablePresets.first ?? "friendly"
            }
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func save() async {
        isSaving = true
        errorText = nil
        statusMessage = nil
        defer { isSaving = false }
        do {
            _ = try await CompanionAPIService.shared.updateProfile(
                customInstructions: customInstructions.trimmingCharacters(in: .whitespacesAndNewlines),
                personalityPreset: personalityPreset,
                securityExpertMode: securityExpertMode
            )
            statusMessage = "Герой будет говорить в выбранном стиле."
            HapticFeedback.impact(.light)
        } catch {
            errorText = error.localizedDescription
        }
    }
}

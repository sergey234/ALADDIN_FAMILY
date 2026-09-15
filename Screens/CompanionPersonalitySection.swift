import SwiftUI

/// P1-04: свои инструкции и тон личности героя (семейный scope, только родитель).
struct CompanionPersonalitySection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

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
                Text(localizationManager.localized("companion_personality_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }

            Text(localizationManager.localized("companion_personality_grok_hint"))
                .font(.caption)
                .foregroundColor(.textSecondary)

            if isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
            } else {
                VStack(alignment: .leading, spacing: 6) {
                    Text(localizationManager.localized("companion_personality_style"))
                        .font(.subheadline.weight(.semibold))
                    Picker(localizationManager.localized("companion_personality_style"), selection: $personalityPreset) {
                        ForEach(availablePresets, id: \.self) { preset in
                            Text(CompanionProfileSettings.presetLabels[preset] ?? preset)
                                .tag(preset)
                        }
                    }
                    .pickerStyle(.segmented)
                }

                Toggle(isOn: $securityExpertMode) {
                    Text(localizationManager.localized("companion_personality_security_expert"))
                        .font(.subheadline)
                }

                VStack(alignment: .leading, spacing: 6) {
                    Text(localizationManager.localized("companion_personality_custom_instructions"))
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
                        Text(
                            isSaving
                                ? localizationManager.localized("companion_saving")
                                : localizationManager.localized("companion_personality_save")
                        )
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
            statusMessage = localizationManager.localized("companion_personality_saved")
            HapticFeedback.impact(.light)
        } catch {
            errorText = error.localizedDescription
        }
    }
}

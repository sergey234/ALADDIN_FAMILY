import SwiftUI

/// P0.2c — structured dump sheet + CTAs.
struct VoiceNotesStructureSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss

    let result: VoiceNotesStructureResult

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .neutral).ignoresSafeArea()
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 14) {
                        section(titleKey: "voice_structure_tasks", items: result.tasks)
                        section(titleKey: "voice_structure_people", items: result.people)
                        section(titleKey: "voice_structure_urgent", items: result.urgent)
                        section(titleKey: "voice_structure_list", items: result.listCandidates)

                        if let raw = result.rawFallback, !raw.isEmpty {
                            Text(localizationManager.localized("voice_structure_raw_fallback"))
                                .font(.caption.weight(.semibold))
                            Text(raw)
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.8))
                        }

                        VStack(spacing: 8) {
                            cta("voice_structure_cta_companion", icon: "bubble.left.and.bubble.right") {
                                let draft = flattenForDraft()
                                UserDefaults.standard.set(draft, forKey: AppConfig.UserDefaultsKeys.pendingAIAssistantDraftMessage)
                                dismiss()
                                navigationManager.navigateToCompanionHome(returnTo: navigationManager.currentScreen)
                            }
                            cta("voice_structure_cta_steps", icon: "list.number") {
                                UserDefaults.standard.set(flattenForDraft(), forKey: CompanionBreakStepsService.draftKey)
                                dismiss()
                                navigationManager.navigateToCompanionHome(returnTo: navigationManager.currentScreen)
                            }
                            cta("voice_structure_cta_list", icon: "cart") {
                                if !result.listCandidates.isEmpty {
                                    UserDefaults.standard.set(
                                        result.listCandidates.joined(separator: "\n"),
                                        forKey: "family_list_draft_from_voice"
                                    )
                                }
                                dismiss()
                                navigationManager.navigateTo(.familyList)
                            }
                        }
                    }
                    .padding()
                }
            }
            .foregroundColor(.white)
            .navigationTitle(localizationManager.localized("voice_structure_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_guide_cancel")) { dismiss() }
                }
            }
        }
        .accessibilityIdentifier("voice_notes_structure_sheet")
    }

    private func section(titleKey: String, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized(titleKey))
                .font(.subheadline.weight(.semibold))
            if items.isEmpty {
                Text("—")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.5))
            } else {
                ForEach(items, id: \.self) { item in
                    Text("• \(item)")
                        .font(.subheadline)
                }
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.08))
        .cornerRadius(10)
    }

    private func cta(_ key: String, icon: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Label(localizationManager.localized(key), systemImage: icon)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
        }
        .buttonStyle(.borderedProminent)
        .tint(Color(hex: "8B5CF6"))
    }

    private func flattenForDraft() -> String {
        var lines: [String] = []
        if !result.urgent.isEmpty { lines.append("Urgent: " + result.urgent.joined(separator: "; ")) }
        if !result.tasks.isEmpty { lines.append("Tasks: " + result.tasks.joined(separator: "; ")) }
        if !result.people.isEmpty { lines.append("People: " + result.people.joined(separator: "; ")) }
        if !result.listCandidates.isEmpty { lines.append("List: " + result.listCandidates.joined(separator: "; ")) }
        if let raw = result.rawFallback, !raw.isEmpty { lines.append(raw) }
        return lines.joined(separator: "\n")
    }
}

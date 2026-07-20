import SwiftUI

/// fws-22 / psych-05 — if-then habit form; loads draft from session close.
struct WellnessIfThenPlanCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var ifPart = ""
    @State private var thenPart = ""
    @State private var savedMessage: String?
    @State private var errorMessage: String?
    @State private var isSaving = false
    @State private var highlight = false

    private static let draftActionKey = "wellness_if_then_draft_action"
    private static let draftTriggerKey = "wellness_if_then_draft_trigger"
    private static let focusKey = "wellness_focus_if_then_card"

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(
                localizationManager.localized("wellness_if_then_title"),
                systemImage: "arrow.triangle.branch"
            )
            .font(.subheadline.bold())
            .foregroundColor(.white)

            Text(localizationManager.localized("wellness_if_then_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))

            TextField(localizationManager.localized("wellness_if_then_if_placeholder"), text: $ifPart)
                .padding(10)
                .stormGlassCard(cornerRadius: 10)
                .accessibilityIdentifier("wellness_if_then_if")
            TextField(localizationManager.localized("wellness_if_then_then_placeholder"), text: $thenPart)
                .padding(10)
                .stormGlassCard(cornerRadius: 10)
                .accessibilityIdentifier("wellness_if_then_then")

            Button {
                Task { await save() }
            } label: {
                Text(localizationManager.localized("wellness_if_then_save"))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color(hex: "8B5CF6"))
            .disabled(isSaving || composedLine.count < 6)
            .accessibilityIdentifier("wellness_if_then_save")

            if let savedMessage {
                Text(savedMessage).font(.caption).foregroundColor(.green)
            }
            if let errorMessage {
                Text(errorMessage).font(.caption).foregroundColor(.orange)
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(highlight ? Color(hex: "8B5CF6") : Color.clear, lineWidth: 2)
        )
        .accessibilityIdentifier("wellness_if_then_card")
        .onAppear { loadDraftFromSessionClose() }
    }

    private var composedLine: String {
        let template = localizationManager.localized("wellness_if_then_template")
        return String(
            format: template,
            ifPart.trimmingCharacters(in: .whitespaces),
            thenPart.trimmingCharacters(in: .whitespaces)
        )
    }

    private func loadDraftFromSessionClose() {
        let defaults = UserDefaults.standard
        if ifPart.isEmpty,
           let trigger = defaults.string(forKey: Self.draftTriggerKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
           !trigger.isEmpty {
            ifPart = trigger
        }
        if thenPart.isEmpty,
           let action = defaults.string(forKey: Self.draftActionKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
           !action.isEmpty {
            thenPart = action
        }
        if defaults.bool(forKey: Self.focusKey) {
            highlight = true
            defaults.set(false, forKey: Self.focusKey)
        }
    }

    private func clearDraft() {
        let defaults = UserDefaults.standard
        defaults.removeObject(forKey: Self.draftActionKey)
        defaults.removeObject(forKey: Self.draftTriggerKey)
    }

    @MainActor
    private func save() async {
        isSaving = true
        savedMessage = nil
        errorMessage = nil
        defer { isSaving = false }
        do {
            try await WellnessAPIService.shared.createHabit(ifThen: composedLine)
            // psych-05: XP only when user later marks Done — saving plan is not chat XP.
            // Optional micro-ack without farming: no grant here.
            clearDraft()
            ifPart = ""
            thenPart = ""
            highlight = false
            savedMessage = localizationManager.localized("wellness_if_then_saved")
            HapticFeedback.notification(.success)
        } catch {
            errorMessage = localizationManager.localized("wellness_if_then_save_failed")
        }
    }
}

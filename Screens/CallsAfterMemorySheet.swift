import SwiftUI

/// Post-call «save what we agreed» sheet — always-available fallback when mic-during-PSTN fails.
struct CallsAfterMemorySheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @ObservedObject private var lifecycle = CallsLifecycleService.shared
    @Environment(\.dismiss) private var dismiss

    @State private var draftGoal = ""
    @State private var draftNote = ""

    var body: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("calls_after_title")) {
                    Text(localizationManager.localized("calls_after_subtitle"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                    TextField(localizationManager.localized("calls_prep_goal_placeholder"), text: $draftGoal)
                    TextField(localizationManager.localized("calls_after_note_placeholder"), text: $draftNote)
                        .lineLimit(6)
                }
                Section {
                    Button(action: saveNote) {
                        Text(localizationManager.localized("calls_after_save"))
                    }
                    .disabled(isSaveDisabled)
                    .accessibilityIdentifier("calls_after_save_button")

                    Button(action: saveAndOpenAntifake) {
                        Text(localizationManager.localized("calls_after_antifake_cta"))
                    }
                }
            }
            .navigationBarTitle(localizationManager.localized("calls_after_nav_title"), displayMode: .inline)
            .navigationBarItems(leading:
                Button(action: closeSheet) {
                    Text(localizationManager.localized("common_close"))
                }
            )
            .onAppear {
                if draftGoal.isEmpty { draftGoal = lifecycle.armedGoal }
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }

    private var isSaveDisabled: Bool {
        draftNote.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            && draftGoal.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            && lifecycle.armedGoal.isEmpty
    }

    private func closeSheet() {
        lifecycle.showAfterSheet = false
        dismiss()
    }

    private func saveNote() {
        _ = lifecycle.saveAfterNote(
            goal: draftGoal.isEmpty ? lifecycle.armedGoal : draftGoal,
            note: draftNote
        )
        dismiss()
    }

    private func saveAndOpenAntifake() {
        _ = lifecycle.saveAfterNote(
            goal: draftGoal.isEmpty ? lifecycle.armedGoal : draftGoal,
            note: draftNote.isEmpty
                ? localizationManager.localized("calls_after_antifake_note")
                : draftNote
        )
        dismiss()
        navigationManager.navigateToAntifakeHub()
    }
}

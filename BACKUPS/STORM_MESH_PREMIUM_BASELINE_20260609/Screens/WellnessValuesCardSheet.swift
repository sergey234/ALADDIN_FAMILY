import SwiftUI

/// p3-07 — ACT values card (optional humanistic).
struct WellnessValuesCardSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var selected: Set<String> = []
    @State private var note = ""
    @State private var saving = false
    @State private var errorText: String?

    private let options = ["kindness", "growth", "connection", "calm", "health"]

    var body: some View {
        WellnessNavigationStack {
            Form {
                Section {
                    Text(localizationManager.localized("wellness_values_card_title"))
                    Text(localizationManager.localized("wellness_values_card_subtitle"))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Section {
                    ForEach(options, id: \.self) { id in
                        Button {
                            toggle(id)
                        } label: {
                            HStack {
                                Text(localizationManager.localized("wellness_values_\(id)"))
                                Spacer()
                                if selected.contains(id) {
                                    Image(systemName: "checkmark.circle.fill")
                                }
                            }
                        }
                        .foregroundStyle(.primary)
                    }
                }
                Section {
                    WellnessMultilineField(
                        title: localizationManager.localized("wellness_values_note_placeholder"),
                        text: $note,
                        lineLimit: 2...4,
                        minHeight: 64
                    )
                }
                if let errorText {
                    Text(errorText).foregroundStyle(.orange)
                }
            }
            .navigationTitle(localizationManager.localized("wellness_values_card_title"))
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("wellness_checkin_save")) {
                        Task { await save() }
                    }
                    .disabled(saving || selected.isEmpty)
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_premium_later")) { dismiss() }
                }
            }
        }
    }

    private func toggle(_ id: String) {
        if selected.contains(id) {
            selected.remove(id)
        } else if selected.count < 2 {
            selected.insert(id)
        }
    }

    private func save() async {
        saving = true
        defer { saving = false }
        do {
            _ = try await WellnessAPIService.shared.saveValuesCard(
                valueIds: Array(selected),
                note: note.isEmpty ? nil : note
            )
            dismiss()
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }
}

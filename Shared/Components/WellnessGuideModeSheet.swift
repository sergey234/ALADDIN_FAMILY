import SwiftUI

/// psych-02 — pick guide mode (A). Default structured_view; child → presence only.
struct WellnessGuideModeSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var store = WellnessGuideSessionStore.shared
    @Environment(\.dismiss) private var dismiss

    let ageBand: String
    var onContinue: () -> Void

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .warm).ignoresSafeArea()
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(localizationManager.localized("wellness_guide_disclaimer"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))

                        Text(localizationManager.localized("wellness_guide_mode_title"))
                            .font(.headline)
                            .foregroundColor(.white)

                        ForEach(store.modes(forAgeBand: ageBand)) { mode in
                            modeRow(mode)
                        }

                        Button {
                            onContinue()
                            dismiss()
                        } label: {
                            Text(localizationManager.localized("wellness_guide_continue"))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 14)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(Color(hex: "8B5CF6"))
                        .padding(.top, 8)
                    }
                    .padding()
                }
            }
            .foregroundColor(.white)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_guide_cancel")) { dismiss() }
                }
            }
        }
        .accessibilityIdentifier("wellness_guide_mode_sheet")
    }

    private func modeRow(_ mode: WellnessGuideSessionStore.ModeOption) -> some View {
        let selected = store.normalizedMode(for: ageBand) == mode.id
        return Button {
            store.selectMode(mode.id, ageBand: ageBand)
        } label: {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized(mode.labelKey))
                        .font(.subheadline.weight(.semibold))
                    Text(localizationManager.localized(mode.hintKey))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
                Spacer()
                Image(systemName: selected ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(selected ? Color(hex: "F5D76E") : .white.opacity(0.5))
            }
            .padding(12)
            .background(selected ? Color.white.opacity(0.14) : Color.white.opacity(0.06))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("wellness_guide_mode_\(mode.id)")
    }
}

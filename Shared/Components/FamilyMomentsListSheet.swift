import SwiftUI

/// p2-9b lite — list local Moments (private; full API later).
struct FamilyMomentsListSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var moments: [FamilyMomentLocal] = []
    @State private var draft = ""

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .warm).ignoresSafeArea()
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizationManager.localized("family_moments_disclaimer"))
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.7))
                    HStack {
                        TextField(localizationManager.localized("family_moments_placeholder"), text: $draft)
                            .textFieldStyle(.roundedBorder)
                        Button {
                            addManual()
                        } label: {
                            Image(systemName: "plus.circle.fill")
                        }
                        .disabled(draft.trimmingCharacters(in: .whitespacesAndNewlines).count < 2)
                        .accessibilityIdentifier("family_moments_add")
                    }
                    if moments.isEmpty {
                        Text(localizationManager.localized("family_moments_empty"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.65))
                    } else {
                        List {
                            ForEach(moments) { m in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(m.text).font(.subheadline)
                                    Text(m.createdAt).font(.caption2).foregroundColor(.secondary)
                                }
                                .listRowBackground(Color.white.opacity(0.08))
                            }
                        }
                        .listStyle(.plain)
                        .modifier(HiddenListBackgroundIfAvailable())
                    }
                    Spacer(minLength: 0)
                }
                .padding()
            }
            .foregroundColor(.white)
            .navigationTitle(localizationManager.localized("family_moments_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_guide_cancel")) { dismiss() }
                }
            }
        }
        .onAppear { moments = FamilyMomentsLocalStore.list() }
        .accessibilityIdentifier("family_moments_sheet")
    }

    private func addManual() {
        let text = draft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard text.count >= 2 else { return }
        _ = FamilyMomentsLocalStore.append(text: text, kind: "manual")
        draft = ""
        moments = FamilyMomentsLocalStore.list()
    }
}

/// iOS 15-safe: hide List chrome background when API exists (iOS 16+).
private struct HiddenListBackgroundIfAvailable: ViewModifier {
    @ViewBuilder
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.scrollContentBackground(.hidden)
        } else {
            content
        }
    }
}

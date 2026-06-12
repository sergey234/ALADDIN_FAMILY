import SwiftUI

/// p2-20 — dream notes (Jung lite; server gate FEATURE_WELLNESS_JUNG).
struct WellnessDreamJournalScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var dreams: [WellnessDreamEntry] = []
    @State private var dreamText = ""
    @State private var moodTag = ""
    @State private var errorText: String?
    @State private var showDisclaimerSheet = false

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    disclaimerRow
                    WellnessMultilineField(
                        title: localizationManager.localized("wellness_dream_prompt"),
                        text: $dreamText
                    )
                    .wellnessReadableInput()
                    TextField(
                        localizationManager.localized("wellness_dream_mood_tag"),
                        text: $moodTag
                    )
                    .wellnessReadableInput()
                    Button {
                        Task { await save() }
                    } label: {
                        Text(localizationManager.localized("wellness_dream_save"))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "8B5CF6"))
                    .disabled(dreamText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                    if let errorText {
                        Text(errorText).foregroundStyle(.orange)
                    }
                    ForEach(dreams) { d in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(d.createdAt).font(.caption2).foregroundColor(.white.opacity(0.7))
                            Text(d.dreamText).foregroundColor(.white)
                            if let tag = d.moodTag, !tag.isEmpty {
                                Text(tag).font(.caption).foregroundColor(.white.opacity(0.75))
                            }
                        }
                        .padding(10)
                        .stormGlassCard(cornerRadius: 10)
                    }
                }
                .padding()
            }
        }
        .navigationBarHidden(true)
        .task { await load() }
        .sheet(isPresented: $showDisclaimerSheet) {
            dreamDisclaimerSheet
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.wellnessGoBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
                    .foregroundColor(.white)
            }
            Text(localizationManager.localized("wellness_dream_title"))
                .font(.headline.bold())
                .foregroundColor(.white)
            Spacer()
        }
    }

    private var disclaimerRow: some View {
        HStack(alignment: .top, spacing: 8) {
            Text(localizationManager.localized("wellness_dream_disclaimer"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.85))
            Button {
                showDisclaimerSheet = true
            } label: {
                Label(
                    localizationManager.localized("wellness_dream_disclaimer_more"),
                    systemImage: "info.circle"
                )
                .font(.caption.bold())
                .foregroundColor(Color(hex: "C4B5FD"))
            }
            .buttonStyle(.plain)
        }
    }

    private var dreamDisclaimerSheet: some View {
        NavigationView {
            List {
                Text(localizationManager.localized("wellness_dream_disclaimer_sheet_1"))
                Text(localizationManager.localized("wellness_dream_disclaimer_sheet_2"))
                Text(localizationManager.localized("wellness_dream_disclaimer_sheet_3"))
            }
            .navigationTitle(localizationManager.localized("wellness_dream_disclaimer_sheet_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("common_close")) {
                        showDisclaimerSheet = false
                    }
                }
            }
        }
        .environmentObject(localizationManager)
    }

    private func load() async {
        do {
            dreams = try await WellnessAPIService.shared.fetchDreams().dreams
        } catch {
            errorText = localizationManager.localized("wellness_dream_unavailable")
        }
    }

    private func save() async {
        let text = dreamText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        do {
            try await WellnessAPIService.shared.postDream(
                text: text,
                moodTag: moodTag.isEmpty ? nil : moodTag
            )
            dreamText = ""
            moodTag = ""
            await load()
        } catch {
            errorText = localizationManager.localized("wellness_dream_unavailable")
        }
    }
}

// MARK: - Readable input on dark wellness backgrounds

private struct WellnessReadableInputModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(10)
            .background(Color.white.opacity(0.96))
            .cornerRadius(10)
            .foregroundColor(Color.primary)
            .accentColor(Color(hex: "8B5CF6"))
    }
}

private extension View {
    func wellnessReadableInput() -> some View {
        modifier(WellnessReadableInputModifier())
    }
}

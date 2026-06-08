import SwiftUI

/// p2-20 — dream notes (Jung lite; server gate FEATURE_WELLNESS_JUNG).
struct WellnessDreamJournalScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var dreams: [WellnessDreamEntry] = []
    @State private var dreamText = ""
    @State private var moodTag = ""
    @State private var errorText: String?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    Text(localizationManager.localized("wellness_dream_disclaimer"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))
                    Text(localizationManager.localized("wellness_dream_reflect_hint"))
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.75))
                    WellnessMultilineField(
                        title: localizationManager.localized("wellness_dream_prompt"),
                        text: $dreamText
                    )
                    .textFieldStyle(.roundedBorder)
                    TextField(
                        localizationManager.localized("wellness_dream_mood_tag"),
                        text: $moodTag
                    )
                    .textFieldStyle(.roundedBorder)
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
                            Text(d.dreamText)
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
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .task { await load() }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("wellness_dream_title"))
                .font(.headline.bold())
            Spacer()
        }
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

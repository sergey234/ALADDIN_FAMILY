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
    @State private var showCoachmark = false

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    disclaimerRow
                    WellnessMultilineField(
                        title: localizationManager.localized("wellness_dream_placeholder"),
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
        .accessibilityIdentifier("wellness_dream_journal_screen")
        .task { await load() }
        .onAppear { presentCoachmarkIfNeeded() }
        .alert(localizationManager.localized("wellness_dream_coachmark_title"), isPresented: $showCoachmark) {
            Button(localizationManager.localized("common_ok")) {
                UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.wellnessDreamJournalCoachmarkSeen)
            }
        } message: {
            Text(localizationManager.localized("wellness_dream_coachmark_body"))
        }
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
            .accessibilityIdentifier("wellness_subpage_back")
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

    private func presentCoachmarkIfNeeded() {
        guard !UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.wellnessDreamJournalCoachmarkSeen) else { return }
        showCoachmark = true
    }

    private func load() async {
        errorText = nil
        let local = WellnessDreamLocalStore.load()
        do {
            let remote = try await WellnessAPIService.shared.fetchDreams().dreams
            WellnessDreamLocalStore.clearSynced(with: remote)
            dreams = WellnessDreamLocalStore.mergeWithRemote(remote)
        } catch {
            dreams = local
            if dreams.isEmpty {
                errorText = localizationManager.localized("wellness_dream_unavailable")
            } else {
                errorText = localizationManager.localized("wellness_dream_offline_saved")
            }
        }
    }

    private func save() async {
        let text = dreamText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        errorText = nil
        do {
            try await WellnessAPIService.shared.postDream(
                text: text,
                moodTag: moodTag.isEmpty ? nil : moodTag
            )
            dreamText = ""
            moodTag = ""
            await load()
        } catch {
            WellnessDreamLocalStore.append(
                text: text,
                moodTag: moodTag.isEmpty ? nil : moodTag
            )
            dreamText = ""
            moodTag = ""
            dreams = WellnessDreamLocalStore.load()
            errorText = localizationManager.localized("wellness_dream_offline_saved")
        }
    }
}

// MARK: - Offline store (ux-6-06)

private enum WellnessDreamLocalStore {
    private static let entriesKey = "wellness_dream_journal_offline_v1"
    private static let nextIdKey = "wellness_dream_journal_offline_next_id"
    private static let maxEntries = 50

    static func load() -> [WellnessDreamEntry] {
        guard let data = UserDefaults.standard.data(forKey: entriesKey) else { return [] }
        return (try? JSONDecoder().decode([WellnessDreamEntry].self, from: data)) ?? []
    }

    static func append(text: String, moodTag: String?) {
        var entries = load()
        let nextId = (UserDefaults.standard.object(forKey: nextIdKey) as? Int) ?? -1
        let entry = WellnessDreamEntry(
            id: nextId,
            dreamText: text,
            moodTag: moodTag,
            createdAt: ISO8601DateFormatter().string(from: Date())
        )
        UserDefaults.standard.set(nextId - 1, forKey: nextIdKey)
        entries.insert(entry, at: 0)
        if entries.count > maxEntries {
            entries = Array(entries.prefix(maxEntries))
        }
        persist(entries)
    }

    static func mergeWithRemote(_ remote: [WellnessDreamEntry]) -> [WellnessDreamEntry] {
        let local = load()
        guard !local.isEmpty else { return remote }
        let remoteTexts = Set(remote.map { $0.dreamText.trimmingCharacters(in: .whitespacesAndNewlines) })
        let pendingLocal = local.filter {
            !remoteTexts.contains($0.dreamText.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        return (remote + pendingLocal).sorted { $0.createdAt > $1.createdAt }
    }

    static func clearSynced(with remote: [WellnessDreamEntry]) {
        let remoteTexts = Set(remote.map { $0.dreamText.trimmingCharacters(in: .whitespacesAndNewlines) })
        let remaining = load().filter {
            !remoteTexts.contains($0.dreamText.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        persist(remaining)
    }

    private static func persist(_ entries: [WellnessDreamEntry]) {
        guard let data = try? JSONEncoder().encode(entries) else { return }
        UserDefaults.standard.set(data, forKey: entriesKey)
    }
}

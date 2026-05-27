import SwiftUI

/// Hub: выбор героя (Kids / Games entry).
struct CompanionHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @StateObject private var caps = CompanionCapabilitiesService.shared
    @AppStorage("companion_selected_character_id") private var selectedCharacterId: String = "unicorn"
    @AppStorage("companion_active_thread_id") private var activeThreadId: String = ""
    @AppStorage("companion_equipped_cosmetic_id") private var equippedCosmeticId: String = ""
    @State private var characters: [CompanionCharacterDTO] = []
    @State private var trustScore: Int = 10
    @State private var usageSnapshot: CompanionUsageSnapshot?
    @State private var showLegal = false
    @State private var threads: [CompanionThreadSummary] = []
    @State private var isLoading = true
    @State private var errorText: String?
    var embeddedInHome: Bool = false
    var showsHistory: Bool = true
    var showsCosmetics: Bool = true
    var onHeroPicked: ((String) -> Void)? = nil

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color.purple.opacity(0.35), Color.blue.opacity(0.25)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    HStack {
                        Text("Разговор с героем")
                            .font((embeddedInHome ? Font.title2 : .largeTitle).bold())
                            .foregroundColor(.white)
                        Spacer()
                        if !embeddedInHome {
                            Button {
                                showLegal = true
                            } label: {
                                Image(systemName: "doc.text")
                                    .foregroundStyle(.white.opacity(0.9))
                            }
                            .accessibilityLabel("Правила AI-компаньона")
                        }
                    }

                    if !embeddedInHome {
                        CompanionUsageBanner(usage: usageSnapshot)
                            .colorScheme(.dark)
                    }

                    if isLoading {
                        ProgressView().tint(.white)
                    } else if let errorText {
                        Text(errorText).foregroundColor(.orange)
                    } else if characters.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Герои пока недоступны")
                                .font(.headline)
                                .foregroundColor(.white)
                            Text("Попроси родителя открыть «Семья» → настройки родительского контроля → раздел «AI-компаньон» и включить «Разговор с героем».")
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.9))
                        }
                    } else {
                        if showsHistory && !threads.isEmpty {
                            Text("История")
                                .font(.title2.bold())
                                .foregroundColor(.white)
                            ForEach(threads) { thread in
                                Button {
                                    selectedCharacterId = thread.characterId
                                    activeThreadId = thread.threadId
                                    if let onHeroPicked {
                                        onHeroPicked(thread.characterId)
                                    } else {
                                        navigationManager.navigateTo(.companionConversation)
                                    }
                                } label: {
                                    HStack(spacing: 12) {
                                        Text(CompanionHeroRiveMapping.heroBaseEmoji(characterId: thread.characterId))
                                            .font(.title2)
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(thread.title)
                                                .font(.subheadline.weight(.semibold))
                                                .lineLimit(1)
                                            Text("\(thread.messageCount) сообщ. · \(thread.updatedAtDisplay)")
                                                .font(.caption)
                                                .opacity(0.8)
                                        }
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                    }
                                    .padding(12)
                                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
                                }
                                .buttonStyle(.plain)
                            }
                        }

                        if showsCosmetics {
                            CompanionCosmeticsSection(
                                characterId: selectedCharacterId,
                                trustScore: trustScore,
                                equippedCosmeticId: $equippedCosmeticId
                            )
                            .padding(12)
                            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
                        }

                        Text("Герои")
                            .font(.title2.bold())
                            .foregroundColor(.white)

                        ForEach(characters) { hero in
                            Button {
                                selectedCharacterId = hero.id
                                activeThreadId = ""
                                if let onHeroPicked {
                                    onHeroPicked(hero.id)
                                } else {
                                    navigationManager.navigateTo(.companionConversation)
                                }
                            } label: {
                                HStack(spacing: 16) {
                                    Text(CompanionHeroRiveMapping.heroBaseEmoji(characterId: hero.id))
                                        .font(.system(size: 44))
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(hero.displayName).font(.headline)
                                        Text(hero.tagline).font(.subheadline).opacity(0.85)
                                        Text(defaultStyleLabel(for: hero.id))
                                            .font(.caption)
                                            .foregroundStyle(.white.opacity(0.75))
                                    }
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                }
                                .padding()
                                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding()
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showLegal) {
            NavigationView {
                CompanionLegalScreen()
                    .environmentObject(navigationManager)
                    .environmentObject(localizationManager)
            }
            .navigationViewStyle(.stack)
        }
        .task {
            await caps.refresh()
            await loadHub()
        }
    }

    private func defaultStyleLabel(for characterId: String) -> String {
        let ageBand = characters.contains(where: { $0.id == "genie" }) ? "parent" : "child"
        let preset = CompanionPersonalityPresets.defaultPreset(
            characterId: characterId,
            ageBand: ageBand
        )
        let name = CompanionProfileSettings.presetLabels[preset] ?? preset
        return "Стиль по умолчанию: \(name)"
    }

    private func loadHub() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            async let chars = CompanionAPIService.shared.fetchCharacters()
            async let hist = CompanionAPIService.shared.fetchThreads()
            async let state = CompanionAPIService.shared.fetchState(characterId: selectedCharacterId)
            characters = try await chars
            threads = (try? await hist) ?? []
            if let st = try? await state {
                trustScore = st.trustScore
                usageSnapshot = st.usage
            }
            CompanionAnalytics.track(.open, characterId: selectedCharacterId)
        } catch {
            errorText = error.localizedDescription
        }
    }
}

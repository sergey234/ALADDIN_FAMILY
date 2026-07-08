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
    @State private var showOnePager = false
    @State private var teenHumorLess = false
    @State private var threads: [CompanionThreadSummary] = []
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showingOfflineCache = false
    var embeddedInHome: Bool = false
    var showsHistory: Bool = true
    var showsCosmetics: Bool = true
    var onHeroPicked: ((String) -> Void)? = nil

    var body: some View {
        ZStack {
            if !embeddedInHome {
                StormMeshBackground(variant: .warm)
            }

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    HStack {
                        Text(localizationManager.localized("companion_hub_title"))
                            .font((embeddedInHome ? Font.title2 : .largeTitle).bold())
                            .foregroundColor(.white)
                        Spacer()
                        if !embeddedInHome {
                            Button {
                                showOnePager = true
                            } label: {
                                Image(systemName: "person.3")
                                    .foregroundStyle(.white.opacity(0.9))
                            }
                            .accessibilityLabel(localizationManager.localized("companion_heroes_one_pager_title"))
                            Button {
                                showLegal = true
                            } label: {
                                Image(systemName: "doc.text")
                                    .foregroundStyle(.white.opacity(0.9))
                            }
                            .accessibilityLabel(localizationManager.localized("companion_hub_legal"))
                        }
                    }

                    if !embeddedInHome {
                        CompanionUsageBanner(usage: usageSnapshot)
                            .colorScheme(.dark)
                    }

                    if showingOfflineCache {
                        Text(localizationManager.localized("companion_offline_cached_hint"))
                            .font(.caption)
                            .foregroundColor(.orange)
                    }

                    if isLoading {
                        ProgressView().tint(.white)
                    } else if let errorText {
                        Text(errorText).foregroundColor(.orange)
                    } else if characters.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(localizationManager.localized("companion_hub_no_heroes_title"))
                                .font(.headline)
                                .foregroundColor(.white)
                            Text(localizationManager.localized("companion_hub_no_heroes_body"))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.9))
                        }
                    } else {
                        if showsHistory && !threads.isEmpty {
                            Text(localizationManager.localized("companion_hub_history"))
                                .font(.title2.bold())
                                .foregroundColor(.white)
                            ForEach(threads) { thread in
                                Button {
                                    selectedCharacterId = thread.characterId
                                    activeThreadId = thread.threadId
                                    if let onHeroPicked {
                                        onHeroPicked(thread.characterId)
                                    } else {
                                        navigationManager.navigateTo(.companionHome)
                                    }
                                } label: {
                                    HStack(spacing: 12) {
                                        CompanionHubHeroPreview(characterId: thread.characterId)
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(thread.title)
                                                .font(.subheadline.weight(.semibold))
                                                .lineLimit(1)
                                            Text(String(format: localizationManager.localized("companion_thread_meta"), thread.messageCount, thread.updatedAtDisplay))
                                                .font(.caption)
                                                .opacity(0.8)
                                        }
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                    }
                                    .padding(12)
                                    .stormGlassCard(cornerRadius: 12)
                                }
                                .buttonStyle(.plain)
                                .accessibilityLabel("\(thread.title), \(String(format: localizationManager.localized("companion_thread_meta"), thread.messageCount, thread.updatedAtDisplay))")
                            }
                        }

                        if showsCosmetics {
                            CompanionCosmeticsSection(
                                characterId: selectedCharacterId,
                                trustScore: trustScore,
                                equippedCosmeticId: $equippedCosmeticId
                            )
                            .padding(12)
                            .stormGlassCard(cornerRadius: 16)
                        }

                        if CompanionUserContext.companionAgeBand == "teen" {
                            teenHumorSection
                        }

                        Text(localizationManager.localized("companion_hub_heroes"))
                            .font(.title2.bold())
                            .foregroundColor(.white)

                        ForEach(characters) { hero in
                            Button {
                                CompanionHeroRouter.markUserOverride(characterId: hero.id)
                                selectedCharacterId = hero.id
                                activeThreadId = ""
                                if let onHeroPicked {
                                    onHeroPicked(hero.id)
                                } else {
                                    navigationManager.navigateTo(.companionHome)
                                }
                            } label: {
                                HStack(spacing: 16) {
                                    CompanionHubHeroPreview(characterId: hero.id, diameter: 88)
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(hero.displayName).font(.headline)
                                        Text(hero.tagline).font(.subheadline).opacity(0.85)
                                        Text(heroStyleCaption(for: hero.id))
                                            .font(.caption)
                                            .foregroundStyle(.white.opacity(0.75))
                                        if let humorHint = heroHumorHint(for: hero.id) {
                                            Text(humorHint)
                                                .font(.caption2)
                                                .foregroundStyle(.white.opacity(0.65))
                                                .lineLimit(2)
                                        }
                                    }
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                }
                                .padding()
                                .stormGlassCard(cornerRadius: 16)
                            }
                            .buttonStyle(.plain)
                            .accessibilityLabel(
                                "\(hero.displayName). \(hero.tagline). \(heroStyleCaption(for: hero.id))"
                            )
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
        .sheet(isPresented: $showOnePager) {
            NavigationView {
                CompanionHeroesOnePagerView()
                    .environmentObject(localizationManager)
            }
            .navigationViewStyle(.stack)
        }
        .onAppear {
            teenHumorLess = CompanionSettings.cachedTeenHumorPreference() == "less"
        }
        .task {
            await caps.refresh()
            await loadHub()
        }
    }

    /// Короткая подпись тона героя (без «Стиль по умолчанию»).
    private func heroStyleCaption(for characterId: String) -> String {
        let key: String
        switch characterId {
        case "aladdin": key = "companion_hero_style_aladdin"
        case "genie": key = "companion_hero_style_genie"
        default: key = "companion_hero_style_unicorn"
        }
        let text = localizationManager.localized(key)
        return text != key ? text : characterId
    }

    /// hero-x-50 — humor hint under hero card (ru/en via LocalizationManager).
    private func heroHumorHint(for characterId: String) -> String? {
        let key = CompanionSettings.humorHintKey(for: characterId)
        let text = localizationManager.localized(key)
        return text != key ? text : nil
    }

    /// hero-x-67 — teen «Меньше шуток» slider.
    private var teenHumorSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("companion_teen_humor_title"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.white)
            Text(localizationManager.localized("companion_teen_humor_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
            Toggle(isOn: $teenHumorLess) {
                Text(localizationManager.localized(teenHumorLess ? "companion_teen_humor_less" : "companion_teen_humor_normal"))
                    .font(.subheadline)
                    .foregroundColor(.white)
            }
            .tint(.purple)
            .accessibilityIdentifier("companion_teen_humor_toggle")
            .onChange(of: teenHumorLess) { less in
                let pref = less ? "less" : "normal"
                CompanionSettings.setCachedTeenHumorPreference(pref)
                Task {
                    try? await CompanionAPIService.shared.updateTeenHumorPreference(pref)
                }
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 16)
    }

    private func loadHub() async {
        isLoading = true
        errorText = nil
        showingOfflineCache = false
        defer { isLoading = false }
        do {
            async let chars = CompanionAPIService.shared.fetchCharacters()
            async let hist = CompanionAPIService.shared.fetchThreads()
            async let state = CompanionAPIService.shared.fetchState(characterId: selectedCharacterId)
            let fetchedCharacters = try await chars
            let allowed = Set(caps.allowedCharactersFromCapabilities)
            characters = fetchedCharacters.filter { allowed.contains($0.id) }
            let liveThreads = (try? await hist) ?? []
            threads = liveThreads
            CompanionOfflineStore.saveThreads(liveThreads)
            if let st = try? await state {
                trustScore = st.trustScore
                usageSnapshot = st.usage
            }
            CompanionAnalytics.track(.open, characterId: selectedCharacterId)
        } catch {
            let cached = CompanionOfflineStore.loadThreads()
            if !cached.isEmpty {
                threads = cached
                showingOfflineCache = true
            } else {
                errorText = error.localizedDescription
            }
        }
    }
}

/// hero-x-69 — parent/teen one-pager «что умеют герои».
struct CompanionHeroesOnePagerView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(localizationManager.localized("companion_heroes_one_pager_intro"))
                    .font(.body)
                heroBlock("companion_heroes_one_pager_unicorn")
                heroBlock("companion_heroes_one_pager_aladdin")
                heroBlock("companion_heroes_one_pager_genie")
            }
            .padding()
        }
        .navigationTitle(localizationManager.localized("companion_heroes_one_pager_title"))
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button(localizationManager.localized("close")) { dismiss() }
            }
        }
    }

    @ViewBuilder
    private func heroBlock(_ key: String) -> some View {
        Text(localizationManager.localized(key))
            .font(.subheadline)
            .padding(12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.purple.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
    }
}

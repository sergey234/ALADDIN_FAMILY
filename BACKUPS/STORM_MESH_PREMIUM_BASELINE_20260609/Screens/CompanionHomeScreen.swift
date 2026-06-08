import SwiftUI

/// Единый «Мир героев» — 4 вкладки: Главное · AI поддержка · Герои · Мой мир.
struct CompanionHomeScreen: View {
    enum Tab: Int, CaseIterable {
        case main
        case wellness
        case heroes
        case mine

        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .main: return localizationManager.localized("companion_tab_main")
            case .wellness: return localizationManager.localized("companion_tab_wellness")
            case .heroes: return localizationManager.localized("companion_tab_heroes")
            case .mine: return localizationManager.localized("companion_tab_mine")
            }
        }

        var icon: String {
            switch self {
            case .main: return "bubble.left.and.bubble.right.fill"
            case .wellness: return "heart.text.square.fill"
            case .heroes: return "sparkles"
            case .mine: return "globe.europe.africa.fill"
            }
        }
    }

    var initialTab: Tab = .main
    var initialCharacterId: String?

    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @StateObject private var caps = CompanionCapabilitiesService.shared
    @AppStorage("companion_selected_character_id") private var selectedCharacterId: String = "unicorn"
    @AppStorage("companion_active_thread_id") private var activeThreadId: String = ""
    @State private var tab: Tab = .main
    @State private var availableCharacters: [CompanionCharacterDTO] = []
    @State private var wellnessTabReady = WellnessSessionStore.hasAcceptedConsent
    @State private var mainConversationPresence: CompanionHeroLayout.ConversationPresence = .standard

    private let tabActiveColor = Color(hex: "C4B5FD")
    private let tabInactiveColor = Color(hex: "E2E8F0").opacity(0.82)

    var body: some View {
        ZStack {
            CompanionHomeBackground()
            VStack(spacing: 0) {
                headerBar
                tabContent
                homeTabBar
                    .frame(height: hidesMainTabBar ? 0 : nil)
                    .opacity(hidesMainTabBar ? 0 : 1)
                    .allowsHitTesting(!hidesMainTabBar)
                    .clipped()
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            tab = initialTab
            wellnessTabReady = WellnessSessionStore.hasAcceptedConsent
            if let initialCharacterId, !initialCharacterId.isEmpty {
                selectedCharacterId = initialCharacterId
            }
            Task { await loadCharacters() }
        }
        .onChange(of: navigationManager.companionHomeTargetTab) { raw in
            guard let raw, let picked = Tab(rawValue: raw) else { return }
            tab = picked
            navigationManager.companionHomeTargetTab = nil
        }
        .onChange(of: tab) { _ in
            if tab != .main, mainConversationPresence == .immersive {
                mainConversationPresence = .standard
            }
        }
    }

    private var hidesMainTabBar: Bool {
        tab == .main && mainConversationPresence == .immersive
    }

    private var headerCompact: Bool {
        tab == .main && mainConversationPresence == .immersive
    }

    private var headerBar: some View {
        HStack {
            Button {
                navigationManager.goBackFromCompanionHome()
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            .accessibilityLabel(localizationManager.localized("companion_back"))

            if !headerCompact {
                Text(localizationManager.localized("companion_home_title"))
                    .font(.headline.bold())
            } else {
                Text(CompanionHeroRiveMapping.heroBaseEmoji(characterId: selectedCharacterId))
                    .font(.title3)
            }
            Spacer()
        }
        .foregroundColor(.white)
        .padding(.horizontal, 16)
        .padding(.vertical, headerCompact ? 6 : 10)
        .animation(.easeInOut(duration: 0.25), value: headerCompact)
    }

    @ViewBuilder
    private var tabContent: some View {
        switch tab {
        case .main:
            CompanionConversationScreen(
                embeddedInHome: true,
                availableCharacters: availableCharacters,
                onSelectCharacter: { id in
                    selectedCharacterId = id
                    activeThreadId = ""
                },
                onOpenMineTab: { tab = .mine },
                onPresenceChange: { presence in
                    withAnimation(.easeInOut(duration: 0.25)) {
                        mainConversationPresence = presence
                    }
                }
            )
        case .wellness:
            if wellnessTabReady {
                WellnessHubScreen(embeddedInHome: true)
            } else {
                WellnessConsentScreen(
                    embeddedInHome: true,
                    onConsentAccepted: { wellnessTabReady = true }
                )
            }
        case .heroes:
            CompanionHubScreen(
                embeddedInHome: true,
                showsHistory: false,
                showsCosmetics: false,
                onHeroPicked: { id in
                    selectedCharacterId = id
                    activeThreadId = ""
                    tab = .main
                }
            )
        case .mine:
            CompanionMineTabView(
                selectedCharacterId: $selectedCharacterId,
                activeThreadId: $activeThreadId,
                onOpenConversation: { tab = .main }
            )
        }
    }

    private var homeTabBar: some View {
        HStack(spacing: 0) {
            ForEach(Tab.allCases, id: \.rawValue) { item in
                Button {
                    tab = item
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: item.icon)
                            .font(.system(size: 18, weight: tab == item ? .semibold : .regular))
                            .symbolRenderingMode(.hierarchical)
                        Text(item.title(localizationManager: localizationManager))
                            .font(.caption2.weight(tab == item ? .bold : .medium))
                            .lineLimit(1)
                            .minimumScaleFactor(0.75)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .foregroundColor(tab == item ? tabActiveColor : tabInactiveColor)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("companion_home_tab_\(item.rawValue)")
            }
        }
        .padding(.horizontal, 6)
        .padding(.top, 6)
        .padding(.bottom, 8)
        .background(
            Color.black.opacity(0.48)
                .background(.ultraThinMaterial)
        )
    }

    private func loadCharacters() async {
        await caps.refresh()
        let fetched = (try? await CompanionAPIService.shared.fetchCharacters()) ?? []
        let allowed = Set(caps.allowedCharactersFromCapabilities)
        availableCharacters = fetched.filter { allowed.contains($0.id) }
        if !availableCharacters.contains(where: { $0.id == selectedCharacterId }),
           let first = availableCharacters.first {
            selectedCharacterId = first.id
        }
    }
}

struct CompanionHomeBackground: View {
    var body: some View {
        LinearGradient(
            colors: [Color.purple.opacity(0.35), Color.blue.opacity(0.25)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .ignoresSafeArea()
    }
}

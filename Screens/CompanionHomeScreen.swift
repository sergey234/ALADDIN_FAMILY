import SwiftUI

/// Единый «Мир героев» — 3 вкладки: Главное · Герои · Моё (E+C).
struct CompanionHomeScreen: View {
    enum Tab: Int, CaseIterable {
        case main
        case heroes
        case mine

        var title: String {
            switch self {
            case .main: return "Главное"
            case .heroes: return "Герои"
            case .mine: return "Моё"
            }
        }

        var icon: String {
            switch self {
            case .main: return "bubble.left.and.bubble.right.fill"
            case .heroes: return "sparkles"
            case .mine: return "heart.circle.fill"
            }
        }
    }

    var initialTab: Tab = .main

    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @AppStorage("companion_selected_character_id") private var selectedCharacterId: String = "unicorn"
    @AppStorage("companion_active_thread_id") private var activeThreadId: String = ""
    @State private var tab: Tab = .main
    @State private var availableCharacters: [CompanionCharacterDTO] = []

    var body: some View {
        ZStack {
            CompanionHomeBackground()
            VStack(spacing: 0) {
                headerBar
                tabContent
                homeTabBar
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            tab = initialTab
            Task { await loadCharacters() }
            CompanionAnalytics.track(.open, characterId: selectedCharacterId)
        }
    }

    private var headerBar: some View {
        HStack {
            Button {
                navigationManager.goBack()
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            .accessibilityLabel("Назад")

            Text("Мир героев")
                .font(.headline.bold())
            Spacer()
        }
        .foregroundColor(.white)
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
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
                onOpenMineTab: { tab = .mine }
            )
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
                            .font(.system(size: 18))
                        Text(item.title)
                            .font(.caption2.weight(tab == item ? .bold : .regular))
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .foregroundColor(tab == item ? .white : .white.opacity(0.55))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 8)
        .padding(.bottom, 6)
        .background(.ultraThinMaterial.opacity(0.35))
    }

    private func loadCharacters() async {
        availableCharacters = (try? await CompanionAPIService.shared.fetchCharacters()) ?? []
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

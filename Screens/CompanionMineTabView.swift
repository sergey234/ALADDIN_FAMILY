import SwiftUI

/// Вкладка «Мой мир» — trust, наряды, история, правила (единое место, без дублей в разговоре).
struct CompanionMineTabView: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @Binding var selectedCharacterId: String
    @Binding var activeThreadId: String
    var onOpenConversation: () -> Void

    @AppStorage("companion_equipped_cosmetic_id") private var equippedCosmeticId: String = ""
    @AppStorage("companion_response_tts_enabled") private var responseTTSEnabled = true
    @AppStorage(CompanionSettings.heroPresencePinStorageKey) private var heroPresencePinRaw: String = CompanionSettings.HeroPresencePinMode.auto.rawValue
    @State private var trustScore: Int = 10
    @State private var threads: [CompanionThreadSummary] = []
    @State private var workspaces: [CompanionWorkspaceDTO] = []
    @State private var cogs: CompanionCogsResponse?
    @State private var showLegal = false
    @State private var showCreateWorkspace = false
    @State private var newWorkspaceTitle = ""
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showingOfflineCache = false

    private var showsParentOps: Bool {
        CompanionUserContext.companionAgeBand == "parent" && !CompanionUserContext.isChildProfile
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                trustCard

                if showsParentOps, let cogs {
                    cogsCard(cogs)
                }

                if showsParentOps, !CompanionLastToolsStore.displayLine.isEmpty {
                    lastToolsCard
                }

                if showsParentOps {
                    workspacesSection
                }

                Toggle(isOn: $responseTTSEnabled) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(localizationManager.localized("companion_mine_tts_title"))
                            .font(.subheadline.weight(.semibold))
                        Text(localizationManager.localized("companion_mine_tts_subtitle"))
                            .font(.caption)
                            .opacity(0.85)
                    }
                }
                .tint(.purple)
                .padding(14)
                .stormGlassCard(cornerRadius: 16)
                .foregroundColor(.white)
                .accessibilityIdentifier("companion_mine_tts_toggle")

                if showsParentOps {
                    heroPresencePinSection
                }

                CompanionCosmeticsSection(
                    characterId: selectedCharacterId,
                    trustScore: trustScore,
                    equippedCosmeticId: $equippedCosmeticId
                )
                .padding(12)
                .stormGlassCard(cornerRadius: 16)

                if showingOfflineCache {
                    Text(localizationManager.localized("companion_offline_cached_hint"))
                        .font(.caption)
                        .foregroundColor(.orange)
                }

                if !threads.isEmpty {
                    Text(localizationManager.localized("companion_hub_history"))
                        .font(.title3.bold())
                        .foregroundColor(.white)
                    ForEach(threads) { thread in
                        Button {
                            selectedCharacterId = thread.characterId
                            activeThreadId = thread.threadId
                            onOpenConversation()
                        } label: {
                            threadRow(thread)
                        }
                        .buttonStyle(.plain)
                    }
                }

                Button {
                    showLegal = true
                } label: {
                    Label(localizationManager.localized("companion_mine_rules"), systemImage: "doc.text")
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(14)
                        .stormGlassCard(cornerRadius: 12)
                }
                .buttonStyle(.plain)
                .foregroundColor(.white)
                .accessibilityIdentifier("companion_mine_rules_button")

                if let errorText {
                    Text(errorText).foregroundColor(.orange).font(.caption)
                }
            }
            .padding()
        }
        .sheet(isPresented: $showLegal) {
            NavigationView {
                CompanionLegalScreen()
                    .environmentObject(navigationManager)
                    .environmentObject(localizationManager)
            }
            .navigationViewStyle(.stack)
        }
        .alert(localizationManager.localized("companion_mine_workspace_new_title"), isPresented: $showCreateWorkspace) {
            TextField(localizationManager.localized("companion_mine_workspace_new_title"), text: $newWorkspaceTitle)
            Button(localizationManager.localized("companion_mine_workspace_cancel"), role: .cancel) {
                newWorkspaceTitle = ""
            }
            Button(localizationManager.localized("companion_mine_workspace_create_action")) {
                Task { await createWorkspace() }
            }
        }
        .task { await reload() }
        .onChange(of: selectedCharacterId) { _ in
            Task {
                do {
                    try await reloadTrust()
                } catch {
                    errorText = error.localizedDescription
                }
            }
        }
    }

    private var heroPresencePinSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("companion_hero_pin_title"))
                    .font(.subheadline.weight(.semibold))
                Text(localizationManager.localized("companion_hero_pin_subtitle"))
                    .font(.caption)
                    .opacity(0.85)
            }
            Picker("", selection: $heroPresencePinRaw) {
                Text(localizationManager.localized("companion_hero_pin_auto"))
                    .tag(CompanionSettings.HeroPresencePinMode.auto.rawValue)
                Text(localizationManager.localized("companion_hero_pin_always_focused"))
                    .tag(CompanionSettings.HeroPresencePinMode.alwaysFocused.rawValue)
                Text(localizationManager.localized("companion_hero_pin_always_standard"))
                    .tag(CompanionSettings.HeroPresencePinMode.alwaysStandard.rawValue)
            }
            .pickerStyle(.segmented)
            .onChange(of: heroPresencePinRaw) { newValue in
                if let mode = CompanionSettings.HeroPresencePinMode(rawValue: newValue) {
                    CompanionSettings.setCachedHeroPresencePinMode(mode)
                }
            }
        }
        .padding(14)
        .stormGlassCard(cornerRadius: 16)
        .foregroundColor(.white)
        .accessibilityIdentifier("companion_mine_hero_pin_section")
    }

    private var trustCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("companion_mine_trust_title"))
                .font(.headline)
                .foregroundColor(.white)
            Text(
                String(
                    format: localizationManager.localized("companion_mine_trust_value"),
                    trustScore,
                    CompanionHeroRiveMapping.heroBaseEmoji(characterId: selectedCharacterId),
                    CompanionDisplayNames.heroName(characterId: selectedCharacterId, localizationManager: localizationManager)
                )
            )
            .font(.subheadline)
            .foregroundColor(.white.opacity(0.9))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .stormGlassCard(cornerRadius: 16)
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("companion_mine_trust_card")
    }

    private var lastToolsCard: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("companion_mine_tools_title"))
                .font(.headline)
            Text(CompanionLastToolsStore.displayLine)
                .font(.caption.monospaced())
                .foregroundColor(.white.opacity(0.85))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .stormGlassCard(cornerRadius: 16)
        .foregroundColor(.white)
        .accessibilityIdentifier("companion_mine_tools_card")
    }

    private func cogsCard(_ cogs: CompanionCogsResponse) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("companion_mine_cogs_title"))
                .font(.headline)
            Text(
                String(
                    format: localizationManager.localized("companion_mine_cogs_value"),
                    cogs.dailyUsd,
                    cogs.monthUsd,
                    cogs.turnsToday
                )
            )
            .font(.subheadline)
            if cogs.alertTriggered {
                Text(
                    String(
                        format: localizationManager.localized("companion_mine_cogs_alert"),
                        cogs.alertThresholdUsd
                    )
                )
                .font(.caption)
                .foregroundColor(.orange)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .stormGlassCard(cornerRadius: 16)
        .foregroundColor(.white)
        .accessibilityIdentifier("companion_mine_cogs_card")
    }

    private var workspacesSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(localizationManager.localized("companion_mine_workspaces_title"))
                    .font(.title3.bold())
                Spacer()
                Button {
                    showCreateWorkspace = true
                } label: {
                    Text(localizationManager.localized("companion_mine_workspace_create"))
                        .font(.caption.weight(.semibold))
                }
            }
            .foregroundColor(.white)

            if workspaces.isEmpty {
                Text(localizationManager.localized("companion_cosmetics_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            } else {
                ForEach(workspaces) { workspace in
                    Button {
                        selectWorkspace(workspace)
                    } label: {
                        HStack {
                            Image(systemName: "folder.fill")
                            Text(workspace.title)
                                .lineLimit(1)
                            Spacer()
                            Image(systemName: "chevron.right")
                        }
                        .padding(12)
                        .stormGlassCard(cornerRadius: 12)
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(.white)
                }
            }
        }
        .accessibilityIdentifier("companion_mine_workspaces_section")
    }

    private func threadRow(_ thread: CompanionThreadSummary) -> some View {
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
        .foregroundColor(.white)
        .accessibilityLabel("\(thread.title), \(String(format: localizationManager.localized("companion_thread_meta"), thread.messageCount, thread.updatedAtDisplay))")
    }

    private func reload() async {
        isLoading = true
        errorText = nil
        showingOfflineCache = false
        defer { isLoading = false }
        do {
            let live = (try? await CompanionAPIService.shared.fetchThreads()) ?? []
            threads = live
            CompanionOfflineStore.saveThreads(live)
            try await reloadTrust()
            if showsParentOps {
                async let cogsTask = CompanionAPIService.shared.fetchCogs()
                async let workspacesTask = CompanionAPIService.shared.fetchWorkspaces()
                cogs = try? await cogsTask
                workspaces = (try? await workspacesTask) ?? []
            }
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

    private func reloadTrust() async throws {
        let state = try await CompanionAPIService.shared.fetchState(characterId: selectedCharacterId)
        trustScore = state.trustScore
    }

    private func selectWorkspace(_ workspace: CompanionWorkspaceDTO) {
        UserDefaults.standard.set(workspace.workspaceId, forKey: "companion_active_workspace_id")
        selectedCharacterId = workspace.characterId
        if let threadId = workspace.threadId, !threadId.isEmpty {
            activeThreadId = threadId
        }
        onOpenConversation()
    }

    private func createWorkspace() async {
        let title = newWorkspaceTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        newWorkspaceTitle = ""
        guard !title.isEmpty else { return }
        do {
            let created = try await CompanionAPIService.shared.createWorkspace(
                title: title,
                characterId: selectedCharacterId
            )
            workspaces.insert(created, at: 0)
            selectWorkspace(created)
        } catch {
            errorText = error.localizedDescription
        }
    }
}

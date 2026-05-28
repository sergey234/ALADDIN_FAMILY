import SwiftUI

/// Вкладка «Моё» — trust, наряды, история, правила (единое место, без дублей в разговоре).
struct CompanionMineTabView: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @Binding var selectedCharacterId: String
    @Binding var activeThreadId: String
    var onOpenConversation: () -> Void

    @AppStorage("companion_equipped_cosmetic_id") private var equippedCosmeticId: String = ""
    @AppStorage("companion_response_tts_enabled") private var responseTTSEnabled = true
    @State private var trustScore: Int = 10
    @State private var threads: [CompanionThreadSummary] = []
    @State private var showLegal = false
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showingOfflineCache = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                trustCard

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
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
                .foregroundColor(.white)
                .accessibilityIdentifier("companion_mine_tts_toggle")

                CompanionCosmeticsSection(
                    characterId: selectedCharacterId,
                    trustScore: trustScore,
                    equippedCosmeticId: $equippedCosmeticId
                )
                .padding(12)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))

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
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
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
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("companion_mine_trust_card")
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
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
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
}

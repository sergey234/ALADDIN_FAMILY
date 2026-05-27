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

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                trustCard

                Toggle(isOn: $responseTTSEnabled) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Озвучивать ответы героя")
                            .font(.subheadline.weight(.semibold))
                        Text("Голос при текстовых сообщениях и субтитре")
                            .font(.caption)
                            .opacity(0.85)
                    }
                }
                .tint(.purple)
                .padding(14)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
                .foregroundColor(.white)

                CompanionCosmeticsSection(
                    characterId: selectedCharacterId,
                    trustScore: trustScore,
                    equippedCosmeticId: $equippedCosmeticId
                )
                .padding(12)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))

                if !threads.isEmpty {
                    Text("История")
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
                    Label("Правила AI-компаньона", systemImage: "doc.text")
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(14)
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
                }
                .buttonStyle(.plain)
                .foregroundColor(.white)

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
            Text("Дружба с героем")
                .font(.headline)
                .foregroundColor(.white)
            Text("Trust: \(trustScore) · \(CompanionHeroRiveMapping.heroBaseEmoji(characterId: selectedCharacterId)) \(displayName(for: selectedCharacterId))")
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.9))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }

    private func threadRow(_ thread: CompanionThreadSummary) -> some View {
        HStack(spacing: 12) {
            CompanionHubHeroPreview(characterId: thread.characterId)
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
        .foregroundColor(.white)
    }

    private func displayName(for id: String) -> String {
        switch id {
        case "aladdin": return "Аладдин"
        case "genie": return "Джин"
        default: return "Единорог"
        }
    }

    private func reload() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            threads = (try? await CompanionAPIService.shared.fetchThreads()) ?? []
            try await reloadTrust()
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func reloadTrust() async throws {
        let state = try await CompanionAPIService.shared.fetchState(characterId: selectedCharacterId)
        trustScore = state.trustScore
    }
}

import SwiftUI

/// P1-09 — правовые тексты AI-компаньона (COPPA / 152-ФЗ / App Store disclosure).
struct CompanionLegalScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    var onAcknowledge: (() -> Void)?

    @State private var sections: [CompanionLegalSection] = []
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showPrivacy = false
    @State private var showTerms = false
    @State private var hasLoaded = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Правила AI-компаньона")
                    .font(.title2.bold())

                Text("Для детей и родителей. Соответствие COPPA и 152-ФЗ «О персональных данных».")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                if isLoading {
                    ProgressView()
                } else if let errorText {
                    Text(errorText).foregroundStyle(.orange)
                } else {
                    ForEach(sections) { section in
                        legalBlock(section)
                    }
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Полные документы")
                        .font(.headline)
                    Button("Политика конфиденциальности") { showPrivacy = true }
                    Button("Пользовательское соглашение") { showTerms = true }
                }
                .padding(.top, 8)

                Text("Вопросы: support@aladdin-ai.ru")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                if let onAcknowledge {
                    Button {
                        onAcknowledge()
                    } label: {
                        Text("Понятно, продолжить")
                            .font(.body.bold())
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.purple)
                    .padding(.top, 8)
                }
            }
            .padding()
        }
        .navigationTitle("Правила")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("Закрыть") {
                    if let onAcknowledge {
                        onAcknowledge()
                    } else {
                        dismiss()
                    }
                }
            }
        }
        .task {
            guard !hasLoaded else { return }
            hasLoaded = true
            await load()
        }
        .sheet(isPresented: $showPrivacy) {
            NavigationView {
                PrivacyPolicyScreen()
                    .environmentObject(navigationManager)
                    .environmentObject(localizationManager)
            }
            .navigationViewStyle(.stack)
        }
        .sheet(isPresented: $showTerms) {
            NavigationView {
                TermsOfServiceScreen()
                    .environmentObject(navigationManager)
                    .environmentObject(localizationManager)
            }
            .navigationViewStyle(.stack)
        }
    }

    @ViewBuilder
    private func legalBlock(_ section: CompanionLegalSection) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(section.title)
                .font(.headline)
            Text(section.body)
                .font(.subheadline)
                .foregroundStyle(.primary)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))
    }

    private func load() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let resp = try await CompanionAPIService.shared.fetchLegal()
            sections = resp.sections
        } catch {
            sections = CompanionLegalSection.offlineFallback
            errorText = nil
        }
    }
}

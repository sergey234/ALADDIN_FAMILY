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
        ZStack {
            StormMeshBackground(variant: .legal)
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text(localizationManager.localized("companion_legal_title"))
                        .font(.title2.bold())
                        .foregroundColor(.white)

                    Text(localizationManager.localized("companion_legal_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.85))

                    if isLoading {
                        ProgressView()
                            .tint(.white)
                    } else if let errorText {
                        Text(errorText).foregroundStyle(.orange)
                    } else {
                        ForEach(sections) { section in
                            legalBlock(section)
                        }
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        Text(localizationManager.localized("companion_legal_full_docs"))
                            .font(.headline)
                            .foregroundColor(.white)
                        Button(localizationManager.localized("companion_legal_privacy")) { showPrivacy = true }
                            .foregroundColor(Color(hex: "C4B5FD"))
                        Button(localizationManager.localized("companion_legal_terms")) { showTerms = true }
                            .foregroundColor(Color(hex: "C4B5FD"))
                    }
                    .padding(.top, 8)

                    Text(localizationManager.localized("companion_legal_contact"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))

                    if let onAcknowledge {
                        Button {
                            onAcknowledge()
                        } label: {
                            Text(localizationManager.localized("companion_legal_ack"))
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
        }
        .navigationTitle(localizationManager.localized("companion_legal_nav_title"))
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button(localizationManager.localized("companion_legal_close")) {
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
                .foregroundColor(.white)
            Text(section.body)
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.9))
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.12))
        .cornerRadius(12)
    }

    private func load() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let resp = try await CompanionAPIService.shared.fetchLegal()
            sections = resp.sections
        } catch {
            sections = CompanionLegalSection.offlineFallback(localizationManager: localizationManager)
            errorText = nil
        }
    }
}

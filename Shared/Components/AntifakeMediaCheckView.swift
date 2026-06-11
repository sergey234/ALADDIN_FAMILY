import SwiftUI
import UniformTypeIdentifiers

struct AntifakeMediaCheckView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel: AntifakeMediaCheckViewModel
    @State private var showFileImporter = false

    private let titleKey: String
    private let hintKey: String
    private let systemImage: String
    private let panelId: String

    init(
        mediaKind: AntifakeMediaKind,
        titleKey: String,
        hintKey: String,
        systemImage: String,
        panelId: String,
        showPremiumPaywall: Binding<Bool>
    ) {
        _viewModel = StateObject(wrappedValue: AntifakeMediaCheckViewModel(mediaKind: mediaKind))
        _showPremiumPaywall = showPremiumPaywall
        self.titleKey = titleKey
        self.hintKey = hintKey
        self.systemImage = systemImage
        self.panelId = panelId
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Label(localizationManager.localized(titleKey), systemImage: systemImage)
                .font(.headline)
                .foregroundColor(.white)

            Text(localizationManager.localized(hintKey))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            if viewModel.mediaKind == .call {
                callMetadataFields
            }

            if let filename = viewModel.selectedFilename {
                HStack {
                    Image(systemName: "doc.fill")
                        .foregroundColor(.secondaryGold)
                    Text(filename)
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .lineLimit(2)
                    Spacer()
                    Button {
                        viewModel.clearSelection()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.white.opacity(0.6))
                    }
                    .buttonStyle(.plain)
                }
                .padding(Spacing.m)
                .stormGlassCard(cornerRadius: CornerRadius.medium)
                .accessibilityIdentifier("\(panelId)_selected_file")
            } else {
                SecondaryButton(
                    localizationManager.localized("antifake_pick_file_button"),
                    icon: "folder.badge.plus"
                ) {
                    showFileImporter = true
                }
                .accessibilityIdentifier("\(panelId)_pick_button")
            }

            if let statusMessage = viewModel.statusMessage {
                HStack(spacing: Spacing.s) {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    Text(statusMessage)
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.85))
                }
            }

            if viewModel.requiresPremiumUpgrade {
                AntifakeInlinePremiumGateCard(message: viewModel.errorMessage) {
                    showPremiumPaywall = true
                }
                .environmentObject(localizationManager)
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .font(.subheadline)
                    .foregroundColor(.dangerRed)
                    .accessibilityIdentifier("\(panelId)_error")
            }

            PrimaryButton(
                localizationManager.localized("antifake_check_button"),
                isLoading: viewModel.isChecking,
                isDisabled: !viewModel.canSubmit
            ) {
                Task {
                    let ok = await viewModel.submitCheck()
                    if viewModel.requiresPremiumUpgrade {
                        showPremiumPaywall = true
                    } else if ok {
                        HapticFeedback.notification(.success)
                    } else if viewModel.errorMessage != nil {
                        HapticFeedback.notification(.error)
                    }
                }
            }
            .accessibilityIdentifier("\(panelId)_check_button")

            if let verdict = viewModel.verdict {
                AntifakeVerdictCard(verdict: verdict)
                    .environmentObject(localizationManager)
            }
        }
        .accessibilityIdentifier(panelId)
        .fileImporter(
            isPresented: $showFileImporter,
            allowedContentTypes: AntifakeMediaCheckViewModel.allowedContentTypes(for: viewModel.mediaKind),
            allowsMultipleSelection: false
        ) { result in
            Task { await ingestFileImport(result) }
        }
    }

    private var callMetadataFields: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            TextField(
                localizationManager.localized("antifake_call_caller_id_placeholder"),
                text: $viewModel.callerId
            )
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .keyboardType(.phonePad)
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
            .accessibilityIdentifier("\(panelId)_caller_id")

            TextField(
                localizationManager.localized("antifake_call_display_name_placeholder"),
                text: $viewModel.displayName
            )
            .textInputAutocapitalization(.words)
            .autocorrectionDisabled()
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
            .accessibilityIdentifier("\(panelId)_display_name")
        }
    }

    @MainActor
    private func ingestFileImport(_ result: Result<[URL], Error>) async {
        switch result {
        case .failure:
            return
        case .success(let urls):
            guard let url = urls.first else { return }
            let didAccess = url.startAccessingSecurityScopedResource()
            defer {
                if didAccess { url.stopAccessingSecurityScopedResource() }
            }
            do {
                let data = try Data(contentsOf: url)
                viewModel.setSelectedFile(data: data, filename: url.lastPathComponent)
            } catch {
                viewModel.clearSelection()
            }
        }
    }
}

enum AntifakeVideoInputMode: String, CaseIterable, Identifiable {
    case video
    case document

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .video: return "antifake_mode_video"
        case .document: return "antifake_mode_document"
        }
    }

    var mediaKind: AntifakeMediaKind {
        switch self {
        case .video: return .video
        case .document: return .document
        }
    }
}

struct AntifakeVideoCheckPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @State private var inputMode: AntifakeVideoInputMode = .video

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack(spacing: Spacing.xs) {
                ForEach(AntifakeVideoInputMode.allCases) { mode in
                    Button {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            inputMode = mode
                        }
                        HapticFeedback.selection()
                    } label: {
                        Text(localizationManager.localized(mode.titleKey))
                            .font(.caption.weight(.semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.s)
                            .foregroundColor(inputMode == mode ? .white : .white.opacity(0.65))
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(inputMode == mode
                                          ? Color.secondaryGold.opacity(0.35)
                                          : Color.white.opacity(0.08))
                            )
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("antifake_video_mode_\(mode.rawValue)")
                }
            }

            AntifakeMediaCheckView(
                mediaKind: inputMode.mediaKind,
                titleKey: inputMode == .video ? "antifake_video_title" : "antifake_document_title",
                hintKey: inputMode == .video ? "antifake_video_hint" : "antifake_document_hint",
                systemImage: inputMode == .video ? "film.fill" : "doc.text.fill",
                panelId: inputMode == .video ? "antifake_video_panel" : "antifake_document_panel",
                showPremiumPaywall: $showPremiumPaywall
            )
            .id(inputMode)
            .environmentObject(localizationManager)
        }
    }
}

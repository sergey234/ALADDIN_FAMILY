import SwiftUI

/// B2-02 / af-6-01 — Antifake Hub: 4 pipelines (text · audio · video · call).
struct AntifakeHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var subscriptionManager: SubscriptionManager
    @StateObject private var tariffManager = TariffManager.shared
    @ObservedObject private var protectionSettingsManager = ProtectionSettingsManager.shared

    @State private var selectedTab: AntifakeHubTab = .text
    @State private var showPremiumPaywall = false
    @State private var showAppleLimits = false
    @State private var sharePrefill: AntifakeSharePayload?
    @State private var pendingTextMode: AntifakeTextInputMode?

    private var hasPremiumAccess: Bool {
        _ = protectionSettingsManager.settings
        return tariffManager.isCategoryAvailable(.deepfakes)
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .shield)

            VStack(spacing: 0) {
                header
                tabPicker
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.s)

                ScrollView(.vertical, showsIndicators: false) {
                    tabContent
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.bottom, Spacing.xxl)
                }
            }
        }
        .navigationBarHidden(true)
        .accessibilityIdentifier("antifake_hub_root")
        .antifakePremiumPaywallSheet(
            isPresented: $showPremiumPaywall,
            navigationManager: navigationManager,
            localizationManager: localizationManager,
            subscriptionManager: subscriptionManager
        )
        .onAppear {
            applyPendingHubNavigationIfNeeded()
        }
        .onChange(of: navigationManager.pendingAntifakeHubTab) { _ in
            applyPendingHubNavigationIfNeeded()
        }
        .onChange(of: navigationManager.pendingAntifakeTextMode) { _ in
            applyPendingHubNavigationIfNeeded()
        }
        .sheet(isPresented: $showAppleLimits) {
            AntifakeAppleLimitsSheet()
                .environmentObject(localizationManager)
        }
    }

    private func applyPendingHubNavigationIfNeeded() {
        if let tab = navigationManager.pendingAntifakeHubTab {
            navigationManager.pendingAntifakeHubTab = nil
            selectedTab = tab
        }
        if let mode = navigationManager.pendingAntifakeTextMode {
            navigationManager.pendingAntifakeTextMode = nil
            pendingTextMode = mode
            selectedTab = .text
        }
    }

    private var header: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("antifake_hub_title"),
            subtitle: localizationManager.localized("antifake_hub_subtitle"),
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            rightButtons: [
                NavigationActionButton(
                    icon: "info.circle",
                    accessibilityLabel: localizationManager.localized("antifake_how_it_works")
                ) {
                    showAppleLimits = true
                }
            ],
            onBack: { navigationManager.goBack() }
        )
    }

    private var tabPicker: some View {
        HStack(spacing: Spacing.xs) {
            ForEach(AntifakeHubTab.allCases) { tab in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedTab = tab
                    }
                    HapticFeedback.selection()
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: tab.iconName)
                            .font(.body.weight(.semibold))
                        Text(localizationManager.localized(tab.titleKey))
                            .font(.caption2.weight(.medium))
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Spacing.s)
                    .foregroundColor(selectedTab == tab ? .white : .white.opacity(0.65))
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(selectedTab == tab ? Color.secondaryGold.opacity(0.35) : Color.white.opacity(0.08))
                    )
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("antifake_hub_tab_\(tab.rawValue)")
            }
        }
    }

    @ViewBuilder
    private var tabContent: some View {
        if !hasPremiumAccess {
            premiumGateCard
        } else {
            switch selectedTab {
            case .text:
                AntifakeTextCheckView(
                    showPremiumPaywall: $showPremiumPaywall,
                    sharePrefill: $sharePrefill,
                    prefillTextMode: $pendingTextMode
                )
            case .audio:
                AntifakeMediaCheckView(
                    mediaKind: .audio,
                    titleKey: "antifake_audio_title",
                    hintKey: "antifake_audio_hint",
                    systemImage: "mic.fill",
                    panelId: "antifake_audio_panel",
                    showPremiumPaywall: $showPremiumPaywall
                )
                .environmentObject(localizationManager)
            case .video:
                AntifakeVideoCheckPanel(showPremiumPaywall: $showPremiumPaywall)
                    .environmentObject(localizationManager)
            case .call:
                AntifakeMediaCheckView(
                    mediaKind: .call,
                    titleKey: "antifake_call_title",
                    hintKey: "antifake_call_hint",
                    systemImage: "phone.arrow.up.right.fill",
                    panelId: "antifake_call_panel",
                    showPremiumPaywall: $showPremiumPaywall
                )
                .environmentObject(localizationManager)
            }
        }
    }

    private var premiumGateCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Label(localizationManager.localized("antifake_premium_required_title"), systemImage: "lock.shield.fill")
                .font(.headline)
                .foregroundColor(.white)

            Text(localizationManager.localized("antifake_premium_required_body"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            PrimaryButton(localizationManager.localized("protection_upgrade_tariff")) {
                showPremiumPaywall = true
            }
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .warningOrange)
        .accessibilityIdentifier("antifake_hub_premium_gate")
    }
}

// MARK: - Tabs

enum AntifakeHubTab: String, CaseIterable, Identifiable {
    case text
    case audio
    case video
    case call

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .text: return "antifake_tab_text"
        case .audio: return "antifake_tab_audio"
        case .video: return "antifake_tab_video"
        case .call: return "antifake_tab_call"
        }
    }

    var iconName: String {
        switch self {
        case .text: return "text.quote"
        case .audio: return "waveform"
        case .video: return "video.fill"
        case .call: return "phone.fill"
        }
    }
}

// MARK: - Tab placeholders (B2-04…06 wire API)

// MARK: - Text / URL check (B2-04)

struct AntifakeTextCheckView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @Binding var sharePrefill: AntifakeSharePayload?
    @Binding var prefillTextMode: AntifakeTextInputMode?
    @StateObject private var viewModel = AntifakeTextCheckViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            modePicker

            Text(localizationManager.localized(viewModel.inputMode.hintKey))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            inputField

            if viewModel.requiresPremiumUpgrade {
                AntifakeInlinePremiumGateCard(message: viewModel.errorMessage) {
                    showPremiumPaywall = true
                }
                .environmentObject(localizationManager)
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .font(.subheadline)
                    .foregroundColor(.dangerRed)
                    .accessibilityIdentifier("antifake_text_error")
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
            .accessibilityIdentifier("antifake_text_check_button")

            if let verdict = viewModel.verdict {
                AntifakeVerdictCard(verdict: verdict)
                    .environmentObject(localizationManager)
            }
        }
        .onAppear {
            applySharePrefillIfNeeded()
            applyPrefillTextModeIfNeeded()
        }
        .onChange(of: sharePrefill) { _ in
            applySharePrefillIfNeeded()
        }
        .onChange(of: prefillTextMode) { _ in
            applyPrefillTextModeIfNeeded()
        }
    }

    private func applyPrefillTextModeIfNeeded() {
        guard let mode = prefillTextMode else { return }
        viewModel.inputMode = mode
        viewModel.verdict = nil
        viewModel.errorMessage = nil
        prefillTextMode = nil
    }

    private func applySharePrefillIfNeeded() {
        guard let payload = sharePrefill else { return }
        viewModel.applySharePayload(payload)
        sharePrefill = nil
    }

    private var modePicker: some View {
        HStack(spacing: Spacing.xs) {
            ForEach(AntifakeTextInputMode.allCases) { mode in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        viewModel.inputMode = mode
                        viewModel.verdict = nil
                        viewModel.errorMessage = nil
                    }
                    HapticFeedback.selection()
                } label: {
                    Text(localizationManager.localized(mode.titleKey))
                        .font(.caption.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.s)
                        .foregroundColor(viewModel.inputMode == mode ? .white : .white.opacity(0.65))
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(viewModel.inputMode == mode
                                      ? Color.secondaryGold.opacity(0.35)
                                      : Color.white.opacity(0.08))
                        )
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("antifake_mode_\(mode.rawValue)")
            }
        }
    }

    @ViewBuilder
    private var inputField: some View {
        switch viewModel.inputMode {
        case .text:
            TextEditor(text: $viewModel.inputText)
                .frame(minHeight: 120)
                .padding(Spacing.s)
                .stormGlassCard(cornerRadius: CornerRadius.medium)
                .accessibilityIdentifier("antifake_text_input")
        case .url:
            TextField(
                localizationManager.localized("antifake_url_placeholder"),
                text: $viewModel.inputUrl
            )
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .keyboardType(.URL)
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
            .accessibilityIdentifier("antifake_url_input")
        }
    }
}

struct AntifakeAudioCheckView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool

    var body: some View {
        AntifakeMediaCheckView(
            mediaKind: .audio,
            titleKey: "antifake_audio_title",
            hintKey: "antifake_audio_hint",
            systemImage: "mic.fill",
            panelId: "antifake_audio_panel",
            showPremiumPaywall: $showPremiumPaywall
        )
        .environmentObject(localizationManager)
    }
}

struct AntifakeVideoCheckView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool

    var body: some View {
        AntifakeVideoCheckPanel(showPremiumPaywall: $showPremiumPaywall)
            .environmentObject(localizationManager)
    }
}

#if DEBUG
struct AntifakeHubScreen_Previews: PreviewProvider {
    static var previews: some View {
        AntifakeHubScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
            .environmentObject(SubscriptionManager.shared)
    }
}
#endif

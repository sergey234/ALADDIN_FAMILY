import SwiftUI
import UIKit

/// B2-02 / af-6-01 — Antifake Hub: text · document · audio · video · call (fsl-01 document tab).
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
    @State private var documentSharePrefill: AntifakeSharePayload?
    @State private var pendingTextMode: AntifakeTextInputMode?
    @State private var showPostCallUploadPrompt = false
    @AppStorage("antifake_share_tip_dismissed") private var shareTipDismissed = false

    private var hasPremiumAccess: Bool {
        _ = protectionSettingsManager.settings
        return AntifakeAccessPolicy.isHubAvailable(tariffManager: tariffManager)
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .shield)

            VStack(spacing: 0) {
                header
                trustBanner
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.s)
                if !shareTipDismissed {
                    shareOnboardTip
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.bottom, Spacing.s)
                }
                tabPicker
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.s)

                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        tabContent
                        askAssistantHelpCard
                        if hasPremiumAccess {
                            AntifakeFamilyReportsSection()
                                .environmentObject(localizationManager)
                            AntifakeCheckHistorySection()
                                .environmentObject(localizationManager)
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .aladdinChatKeyboardDismiss()
                .aladdinKeyboardDoneToolbar(
                    title: localizationManager.localized("companion_conversation_done"),
                    action: {
                        UIApplication.shared.sendAction(
                            #selector(UIResponder.resignFirstResponder),
                            to: nil,
                            from: nil,
                            for: nil
                        )
                    }
                )
            }
        }
        .navigationBarHidden(true)
        .accessibilityIdentifier("antifake_hub_root")
        .accessibilityLabel(localizationManager.localized("antifake_hub_title"))
        .accessibilityHint(localizationManager.localized("antifake_hub_subtitle"))
        .antifakePremiumPaywallSheet(
            isPresented: $showPremiumPaywall,
            navigationManager: navigationManager,
            localizationManager: localizationManager,
            subscriptionManager: subscriptionManager
        )
        .onAppear {
            applyPendingHubNavigationIfNeeded()
            if hasPremiumAccess {
                ProtectionSettingsManager.shared.syncPremiumDeepfakesIfNeeded(for: tariffManager.currentTariff)
            }
        }
        .onChange(of: navigationManager.pendingAntifakeHubTab) { _ in
            applyPendingHubNavigationIfNeeded()
        }
        .onChange(of: navigationManager.pendingAntifakeTextMode) { _ in
            applyPendingHubNavigationIfNeeded()
        }
        .onChange(of: navigationManager.pendingAntifakeSharePayload) { _ in
            applyPendingHubNavigationIfNeeded()
        }
        .sheet(isPresented: $showAppleLimits) {
            AntifakeAppleLimitsSheet()
                .environmentObject(localizationManager)
        }
    }

    private func applyPendingHubNavigationIfNeeded() {
        if navigationManager.consumeAntifakePostCallPromptIfNeeded() {
            showPostCallUploadPrompt = true
            selectedTab = .call
        }
        if let tab = navigationManager.pendingAntifakeHubTab {
            navigationManager.pendingAntifakeHubTab = nil
            selectedTab = tab
        }
        if let mode = navigationManager.pendingAntifakeTextMode {
            navigationManager.pendingAntifakeTextMode = nil
            pendingTextMode = mode
            selectedTab = .text
        }
        if let payload = navigationManager.pendingAntifakeSharePayload {
            navigationManager.pendingAntifakeSharePayload = nil
            switch payload.mode {
            case .document:
                selectedTab = .document
                documentSharePrefill = payload
            case .text, .url:
                selectedTab = .text
                sharePrefill = payload
            }
        }
    }

    /// browse-01 — Share + виджет + Siri (усиление fsl-11).
    private var shareOnboardTip: some View {
        HStack(alignment: .top, spacing: Spacing.s) {
            Image(systemName: "square.and.arrow.up")
                .foregroundColor(.secondaryGold)
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized("share_onboard_title"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                Text(localizationManager.localized("share_onboard_body"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .fixedSize(horizontal: false, vertical: true)
                VStack(alignment: .leading, spacing: 4) {
                    Label(localizationManager.localized("share_onboard_path_share"), systemImage: "square.and.arrow.up")
                    Label(localizationManager.localized("share_onboard_path_widget"), systemImage: "rectangle.on.rectangle")
                    Label(localizationManager.localized("share_onboard_path_siri"), systemImage: "mic.fill")
                }
                .font(.caption2.weight(.medium))
                .foregroundColor(.secondaryGold)
            }
            Spacer(minLength: 0)
            Button {
                shareTipDismissed = true
                HapticFeedback.selection()
            } label: {
                Image(systemName: "xmark")
                    .font(.caption.weight(.bold))
                    .foregroundColor(.white.opacity(0.7))
                    .padding(6)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(localizationManager.localized("share_onboard_dismiss"))
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .secondaryGold)
        .accessibilityIdentifier("antifake_share_onboard_tip")
    }

    private var trustBanner: some View {
        Button {
            showAppleLimits = true
        } label: {
            HStack(alignment: .top, spacing: Spacing.s) {
                Image(systemName: "exclamationmark.shield")
                    .foregroundColor(.yellow)
                Text(localizationManager.localized("antifake_trust_banner"))
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.92))
                    .multilineTextAlignment(.leading)
                Spacer(minLength: 0)
            }
            .padding(Spacing.s)
            .stormGlassCard(cornerRadius: 12)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("antifake_trust_banner")
        .accessibilityLabel(localizationManager.localized("antifake_trust_banner"))
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
            onBack: {
                navigationManager.goBackToPreviousScreen(reason: "AntifakeHub.onBack")
            }
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
                .accessibilityLabel(localizationManager.localized(tab.titleKey))
                .accessibilityAddTraits(selectedTab == tab ? .isSelected : [])
            }
        }
    }

    private var askAssistantHelpCard: some View {
        Button {
            guard let url = URL(string: AppConfig.supportAssistantURL) else { return }
            UIApplication.shared.open(url)
        } label: {
            HStack(spacing: Spacing.m) {
                Image(systemName: "sparkles")
                    .font(.title3.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .accessibilityHidden(true)
                VStack(alignment: .leading, spacing: 2) {
                    Text(localizationManager.localized("support_ask_assistant"))
                        .font(.subheadline.bold())
                        .foregroundColor(.white)
                    Text(localizationManager.localized("support_ask_assistant_antifake_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 0)
                Image(systemName: "arrow.up.right")
                    .foregroundColor(.white.opacity(0.7))
                    .accessibilityHidden(true)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .secondaryGold)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("antifake_ask_assistant_cta")
        .accessibilityLabel(localizationManager.localized("support_ask_assistant"))
        .accessibilityHint(localizationManager.localized("support_ask_assistant_antifake_subtitle"))
    }

    @ViewBuilder
    private var tabContent: some View {
        if !hasPremiumAccess {
            premiumGateCard
            premiumLockedTabPreview
        } else {
            switch selectedTab {
            case .text:
                AntifakeTextCheckView(
                    showPremiumPaywall: $showPremiumPaywall,
                    sharePrefill: $sharePrefill,
                    prefillTextMode: $pendingTextMode
                )
            case .document:
                AntifakeDocumentCheckView(
                    showPremiumPaywall: $showPremiumPaywall,
                    documentSharePrefill: $documentSharePrefill
                )
                .environmentObject(localizationManager)
            case .audio:
                AntifakeQuickVoiceCaptureView(showPremiumPaywall: $showPremiumPaywall)
                    .environmentObject(localizationManager)
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
                AntifakeCallTabView(
                    showPremiumPaywall: $showPremiumPaywall,
                    showPostCallUploadPrompt: $showPostCallUploadPrompt
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
                .accessibilityAddTraits(.isHeader)

            Text(localizationManager.localized("antifake_premium_gate_honest_body"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            VStack(alignment: .leading, spacing: Spacing.xs) {
                premiumBullet("antifake_premium_gate_bullet_1")
                premiumBullet("antifake_premium_gate_bullet_2")
                premiumBullet("antifake_premium_gate_bullet_3")
            }

            Text(localizationManager.localized("antifake_premium_gate_no_demo"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.7))

            Text(localizationManager.localized("antifake_premium_limits_footnote"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.65))

            PrimaryButton(localizationManager.localized("protection_upgrade_tariff")) {
                showPremiumPaywall = true
            }
            .accessibilityLabel(localizationManager.localized("protection_upgrade_tariff"))
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .warningOrange)
        .accessibilityIdentifier("antifake_hub_premium_gate")
        .accessibilityLabel(localizationManager.localized("antifake_premium_required_title"))
        .accessibilityHint(localizationManager.localized("antifake_premium_gate_no_demo"))
    }

    private func premiumBullet(_ key: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.s) {
            Image(systemName: "checkmark.seal.fill")
                .foregroundColor(.secondaryGold)
                .accessibilityHidden(true)
            Text(localizationManager.localized(key))
                .font(.caption)
                .foregroundColor(.white.opacity(0.9))
        }
    }

    private var premiumLockedTabPreview: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("antifake_premium_locked_tabs_title"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.white.opacity(0.75))
                .accessibilityAddTraits(.isHeader)
            HStack(spacing: Spacing.xs) {
                ForEach(AntifakeHubTab.allCases) { tab in
                    VStack(spacing: 4) {
                        Image(systemName: tab.iconName)
                        Text(localizationManager.localized(tab.titleKey))
                            .font(.caption2)
                            .lineLimit(1)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Spacing.s)
                    .foregroundColor(.white.opacity(0.35))
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(Color.white.opacity(0.15), lineWidth: 1)
                    )
                    .accessibilityLabel(localizationManager.localized(tab.titleKey))
                    .accessibilityHint(localizationManager.localized("antifake_premium_locked_tab_hint"))
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .accessibilityIdentifier("antifake_hub_locked_tabs_preview")
    }
}

// MARK: - Tabs

enum AntifakeHubTab: String, CaseIterable, Identifiable {
    case text
    case document
    case audio
    case video
    case call

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .text: return "antifake_tab_text"
        case .document: return "antifake_tab_document"
        case .audio: return "antifake_tab_audio"
        case .video: return "antifake_tab_video"
        case .call: return "antifake_tab_call"
        }
    }

    var iconName: String {
        switch self {
        case .text: return "text.quote"
        case .document: return "doc.text.viewfinder"
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
    @StateObject private var viewModel = AntifakeTextCheckViewModel(localizationManager: .shared)
    @State private var showTransferEntryBanner = false
    @State private var showTranslateThenCheckTip = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            if showTransferEntryBanner {
                transferEntryBanner
            }
            modePicker

            Text(localizationManager.localized(viewModel.inputMode.hintKey))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            pasteFromClipboardRow

            // gai-04 — SMS на другом языке: системный Translate → вставить → наш вердикт.
            translateThenCheckRow

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
                AntifakeVerdictCard(
                    verdict: verdict,
                    variant: viewModel.inputMode == .url ? .urlDisinformation : .standard
                )
                    .environmentObject(localizationManager)
            }
        }
        .onAppear {
            applySharePrefillIfNeeded()
            applyPrefillTextModeIfNeeded()
            showTransferEntryBanner = UserDefaults.standard.bool(
                forKey: AppConfig.UserDefaultsKeys.antifakeTransferCheckEntry
            )
            if showTransferEntryBanner {
                UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.antifakeTransferCheckEntry)
            }
        }
        .onChange(of: sharePrefill) { _ in
            applySharePrefillIfNeeded()
        }
        .onChange(of: prefillTextMode) { _ in
            applyPrefillTextModeIfNeeded()
        }
        .alert(
            localizationManager.localized("antifake_translate_then_check_title"),
            isPresented: $showTranslateThenCheckTip
        ) {
            Button(localizationManager.localized("common_ok"), role: .cancel) {}
        } message: {
            Text(localizationManager.localized("antifake_translate_then_check_body"))
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

    private var transferEntryBanner: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(localizationManager.localized("antifake_transfer_banner_title"))
                .font(.subheadline.weight(.bold))
                .foregroundColor(.warningOrange)
            Text(localizationManager.localized("antifake_transfer_banner_body"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.85))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.warningOrange.opacity(0.15))
        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        .accessibilityIdentifier("antifake_transfer_entry_banner")
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

    private var pasteFromClipboardRow: some View {
        Button {
            viewModel.pasteFromClipboard()
            HapticFeedback.selection()
        } label: {
            Label(
                localizationManager.localized("antifake_paste_button"),
                systemImage: "doc.on.clipboard"
            )
            .font(.subheadline.weight(.semibold))
            .frame(maxWidth: .infinity, minHeight: 44)
            .foregroundColor(viewModel.hasClipboardContent ? .secondaryGold : .white.opacity(0.45))
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .strokeBorder(
                        viewModel.hasClipboardContent
                            ? Color.secondaryGold.opacity(0.55)
                            : Color.white.opacity(0.2),
                        lineWidth: 1
                    )
            )
        }
        .buttonStyle(.plain)
        .disabled(!viewModel.hasClipboardContent)
        .accessibilityIdentifier("antifake_paste_button")
        .accessibilityHint(localizationManager.localized("antifake_paste_button_hint"))
    }

    private var translateThenCheckRow: some View {
        Button {
            let snapshot: String
            switch viewModel.inputMode {
            case .url:
                snapshot = viewModel.inputUrl
            case .text:
                snapshot = viewModel.inputText
            case .contact:
                snapshot = [viewModel.callerId, viewModel.displayName]
                    .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                    .filter { !$0.isEmpty }
                    .joined(separator: " ")
            }
            let trimmed = snapshot.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty {
                UIPasteboard.general.string = trimmed
            }
            showTranslateThenCheckTip = true
            HapticFeedback.selection()
        } label: {
            Label(
                localizationManager.localized("antifake_translate_then_check_button"),
                systemImage: "character.book.closed"
            )
            .font(.subheadline.weight(.semibold))
            .frame(maxWidth: .infinity, minHeight: 44)
            .foregroundColor(.secondaryGold)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .strokeBorder(Color.secondaryGold.opacity(0.55), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("antifake_translate_then_check_button")
        .accessibilityHint(localizationManager.localized("antifake_translate_then_check_hint"))
    }

    @ViewBuilder
    private var inputField: some View {
        switch viewModel.inputMode {
        case .text:
            TextEditor(text: $viewModel.inputText)
                .frame(minHeight: 120)
                .padding(Spacing.s)
                .modifier(AladdinHideTextEditorBackground())
                .wellnessReadableInput()
                .stormGlassCard(cornerRadius: CornerRadius.medium)
                .accessibilityIdentifier("antifake_text_input")
                .accessibilityLabel(localizationManager.localized("antifake_mode_text"))
        case .url:
            VStack(alignment: .leading, spacing: Spacing.xs) {
                fieldLabel(localizationManager.localized("antifake_url_field_label"))
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
        case .contact:
            VStack(alignment: .leading, spacing: Spacing.s) {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    fieldLabel(localizationManager.localized("antifake_contact_caller_label"))
                    TextField(
                        localizationManager.localized("antifake_call_caller_id_placeholder"),
                        text: $viewModel.callerId
                    )
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .keyboardType(.phonePad)
                    .padding(Spacing.m)
                    .stormGlassCard(cornerRadius: CornerRadius.medium)
                    .accessibilityIdentifier("antifake_contact_caller_input")
                }
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    fieldLabel(localizationManager.localized("antifake_contact_name_label"))
                    TextField(
                        localizationManager.localized("antifake_call_display_name_placeholder"),
                        text: $viewModel.displayName
                    )
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
                    .padding(Spacing.m)
                    .stormGlassCard(cornerRadius: CornerRadius.medium)
                    .accessibilityIdentifier("antifake_contact_name_input")
                }
            }
        }
    }

    private func fieldLabel(_ title: String) -> some View {
        Text(title)
            .font(.caption.weight(.semibold))
            .foregroundColor(.white.opacity(0.9))
            .accessibilityAddTraits(.isHeader)
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

/// fsl-01 — Документ: фото/PDF через уже существующий antifake document API.
struct AntifakeDocumentCheckView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @Binding var documentSharePrefill: AntifakeSharePayload?

    var body: some View {
        AntifakeMediaCheckView(
            mediaKind: .document,
            titleKey: "antifake_document_title",
            hintKey: "antifake_document_hint",
            systemImage: "doc.text.viewfinder",
            panelId: "antifake_document_panel",
            showPremiumPaywall: $showPremiumPaywall,
            documentSharePrefill: $documentSharePrefill
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
            .environmentObject(LocalizationManager.shared)
            .environmentObject(SubscriptionManager.shared)
    }
}
#endif

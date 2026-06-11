import SwiftUI

/// B4-01 — Identity Hub: Detect · Attempts · Monitor.
struct IdentityHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var subscriptionManager: SubscriptionManager

    @State private var selectedTab: IdentityHubTab = .detect
    @State private var showPremiumPaywall = false

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .premium)

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
        .accessibilityIdentifier("identity_hub_root")
        .onAppear {
            applyPendingTabIfNeeded()
        }
        .onChange(of: navigationManager.pendingIdentityHubTab) { tab in
            guard let tab else { return }
            navigationManager.pendingIdentityHubTab = nil
            selectedTab = tab
        }
        .antifakePremiumPaywallSheet(
            isPresented: $showPremiumPaywall,
            navigationManager: navigationManager,
            localizationManager: localizationManager,
            subscriptionManager: subscriptionManager
        )
    }

    private func applyPendingTabIfNeeded() {
        if let tab = navigationManager.pendingIdentityHubTab {
            navigationManager.pendingIdentityHubTab = nil
            selectedTab = tab
        }
    }

    private var header: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("identity_hub_title"),
            subtitle: localizationManager.localized("identity_hub_subtitle"),
            showBackButton: true,
            onBack: { navigationManager.goBack() }
        )
    }

    private var tabPicker: some View {
        HStack(spacing: Spacing.xs) {
            ForEach(IdentityHubTab.allCases) { tab in
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
                .accessibilityIdentifier("identity_hub_tab_\(tab.rawValue)")
            }
        }
    }

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .detect:
            IdentityHubDetectPanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .attempts:
            IdentityHubAttemptsPanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .monitor:
            IdentityHubMonitorPanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .coverage:
            IdentityHubThreatCoverageView()
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
        }
    }
}

enum IdentityHubTab: String, CaseIterable, Identifiable {
    case detect
    case attempts
    case monitor
    case coverage

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .detect: return "identity_hub_tab_detect"
        case .attempts: return "identity_hub_tab_attempts"
        case .monitor: return "identity_hub_tab_monitor"
        case .coverage: return "identity_hub_tab_coverage"
        }
    }

    var iconName: String {
        switch self {
        case .detect: return "person.text.rectangle"
        case .attempts: return "list.bullet.rectangle"
        case .monitor: return "bell.badge.shield.half.filled"
        case .coverage: return "checkmark.shield.fill"
        }
    }
}

// MARK: - Detect (B4-02 wires API)

struct IdentityHubDetectPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = IdentityDetectViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("identity_hub_detect_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            TextField(
                localizationManager.localized("identity_hub_snils_placeholder"),
                text: $viewModel.snilsInput
            )
            .keyboardType(.numbersAndPunctuation)
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
            .accessibilityIdentifier("identity_hub_snils_input")

            if viewModel.requiresPremiumUpgrade {
                AntifakeInlinePremiumGateCard(message: viewModel.errorMessage) {
                    showPremiumPaywall = true
                }
                .environmentObject(localizationManager)
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .font(.subheadline)
                    .foregroundColor(.dangerRed)
                    .accessibilityIdentifier("identity_hub_detect_error")
            }

            PrimaryButton(
                localizationManager.localized("identity_hub_detect_button"),
                isLoading: viewModel.isChecking,
                isDisabled: !viewModel.canSubmit
            ) {
                Task {
                    let ok = await viewModel.submitDetect()
                    if viewModel.requiresPremiumUpgrade {
                        showPremiumPaywall = true
                    } else if ok {
                        HapticFeedback.notification(.success)
                    } else if viewModel.errorMessage != nil {
                        HapticFeedback.notification(.error)
                    }
                }
            }
            .accessibilityIdentifier("identity_hub_detect_button")

            if let verdict = viewModel.verdict {
                AntifakeVerdictCard(verdict: verdict)
                    .environmentObject(localizationManager)
                    .accessibilityIdentifier("identity_hub_detect_verdict")
            }
        }
    }
}

// MARK: - Attempts (B4-03)

struct IdentityHubAttemptsPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = IdentityTheftViewModel()

    @State private var filterAction = "all"
    @State private var filterSeverity = "all"

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("identity_hub_attempts_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            if let stats = viewModel.stats {
                HStack(spacing: Spacing.s) {
                    metricChip(
                        title: localizationManager.localized("identity_theft_total_attempts"),
                        value: "\(stats.totalAttempts)"
                    )
                    metricChip(
                        title: localizationManager.localized("identity_theft_blocked"),
                        value: "\(stats.blockedAttempts)"
                    )
                    metricChip(
                        title: localizationManager.localized("identity_theft_suspicious"),
                        value: "\(stats.suspiciousActivities)"
                    )
                }
            }

            filtersSection

            if viewModel.requiresPremiumUpgrade {
                AntifakeInlinePremiumGateCard(message: viewModel.errorMessage) {
                    showPremiumPaywall = true
                }
                .environmentObject(localizationManager)
            } else if let error = viewModel.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
                    .accessibilityIdentifier("identity_hub_attempts_error")
            }

            if viewModel.attempts.isEmpty && !viewModel.isLoading {
                emptyState
            } else {
                ForEach(viewModel.attempts) { attempt in
                    attemptRow(attempt)
                }
            }
        }
        .overlay {
            if viewModel.isLoading && viewModel.attempts.isEmpty {
                ProgressView()
                    .tint(.white)
            }
        }
        .refreshable {
            await reloadData()
        }
        .task {
            await reloadData()
        }
        .onChange(of: filterAction) { _ in
            Task { await reloadData() }
        }
        .onChange(of: filterSeverity) { _ in
            Task { await reloadData() }
        }
    }

    private var emptyState: some View {
        VStack(spacing: Spacing.s) {
            Image(systemName: "checkmark.shield.fill")
                .font(.system(size: 36))
                .foregroundColor(.successGreen)
            Text(localizationManager.localized("identity_theft_no_attempts"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.7))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, Spacing.l)
    }

    private var filtersSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("identity_theft_filters"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.white.opacity(0.85))

            HStack(spacing: Spacing.s) {
                filterMenu(
                    title: actionFilterLabel,
                    accessibilityId: "identity_hub_attempts_filter_action"
                ) {
                    filterOption("all", labelKey: "identity_theft_filter_all_actions", binding: $filterAction)
                    filterOption("blocked", labelKey: "identity_theft_filter_blocked", binding: $filterAction)
                    filterOption("allowed", labelKey: "identity_theft_filter_allowed", binding: $filterAction)
                    filterOption("suspicious", labelKey: "identity_theft_action_suspicious", binding: $filterAction)
                }

                filterMenu(
                    title: severityFilterLabel,
                    accessibilityId: "identity_hub_attempts_filter_severity"
                ) {
                    filterOption("all", labelKey: "identity_theft_filter_all", binding: $filterSeverity)
                    filterOption("critical", labelKey: "dark_web_severity_critical", binding: $filterSeverity)
                    filterOption("high", labelKey: "dark_web_severity_high", binding: $filterSeverity)
                    filterOption("medium", labelKey: "violation_severity_medium", binding: $filterSeverity)
                    filterOption("low", labelKey: "violation_severity_low", binding: $filterSeverity)
                }
            }
        }
    }

    private var actionFilterLabel: String {
        switch filterAction {
        case "blocked": return localizationManager.localized("identity_theft_filter_blocked")
        case "allowed": return localizationManager.localized("identity_theft_filter_allowed")
        case "suspicious": return localizationManager.localized("identity_theft_action_suspicious")
        default: return localizationManager.localized("identity_theft_filter_all_actions")
        }
    }

    private var severityFilterLabel: String {
        switch filterSeverity {
        case "critical": return localizationManager.localized("dark_web_severity_critical")
        case "high": return localizationManager.localized("dark_web_severity_high")
        case "medium": return localizationManager.localized("violation_severity_medium")
        case "low": return localizationManager.localized("violation_severity_low")
        default: return localizationManager.localized("identity_theft_filter_all")
        }
    }

    private func filterMenu<Content: View>(
        title: String,
        accessibilityId: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        Menu(content: content) {
            HStack(spacing: 4) {
                Text(title)
                    .font(.caption)
                    .lineLimit(1)
                Image(systemName: "chevron.down")
                    .font(.caption2)
            }
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.s)
            .padding(.vertical, Spacing.xs)
            .stormGlassCard(cornerRadius: CornerRadius.large)
        }
        .accessibilityIdentifier(accessibilityId)
    }

    private func filterOption(_ value: String, labelKey: String, binding: Binding<String>) -> some View {
        Button {
            binding.wrappedValue = value
        } label: {
            Label(
                localizationManager.localized(labelKey),
                systemImage: binding.wrappedValue == value ? "checkmark" : ""
            )
        }
    }

    private func reloadData() async {
        let action = filterAction == "all" ? nil : filterAction
        let severity = filterSeverity == "all" ? nil : filterSeverity
        await viewModel.loadData(action: action, severity: severity)
        if viewModel.requiresPremiumUpgrade {
            showPremiumPaywall = true
        }
    }

    private func attemptRow(_ attempt: IdentityTheftAttempt) -> some View {
        let isProcessing = viewModel.processingAttemptId == attempt.id

        return VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(alignment: .top) {
                HStack(spacing: Spacing.xs) {
                    Text(attempt.dataType.icon)
                        .font(.caption)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(attempt.dataType.localizedDisplayName(localizationManager))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        Text(attempt.requestSource)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                        Text(attempt.formattedTimestamp)
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.55))
                    }
                }

                Spacer()

                VStack(alignment: .trailing, spacing: 4) {
                    actionBadge(attempt.action)
                    severityBadge(attempt.severity)
                }
            }

            if let details = attempt.details {
                Text(details)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.65))
            }

            HStack(spacing: Spacing.s) {
                if attempt.action == .blocked || attempt.action == .suspicious || attempt.action == .requiresReview {
                    actionButton(
                        title: localizationManager.localized("identity_theft_action_allow"),
                        color: .secondaryGold,
                        disabled: isProcessing
                    ) {
                        Task { await viewModel.allowAttempt(attemptId: attempt.id) }
                    }
                }
                if attempt.action == .allowed || attempt.action == .suspicious || attempt.action == .requiresReview {
                    actionButton(
                        title: localizationManager.localized("identity_theft_action_block"),
                        color: .dangerRed,
                        disabled: isProcessing
                    ) {
                        Task { await viewModel.blockAttempt(attemptId: attempt.id) }
                    }
                }
                if attempt.action == .suspicious {
                    actionButton(
                        title: localizationManager.localized("identity_theft_action_whitelist"),
                        color: .white.opacity(0.9),
                        disabled: isProcessing
                    ) {
                        Task { await viewModel.addToWhitelist(source: attempt.requestSource) }
                    }
                }

                if isProcessing {
                    ProgressView()
                        .scaleEffect(0.8)
                        .tint(.white)
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .accessibilityIdentifier("identity_hub_attempt_row_\(attempt.id)")
    }

    private func actionBadge(_ action: AttemptAction) -> some View {
        Text(action.localizedDisplayName(localizationManager))
            .font(.caption2.weight(.semibold))
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.xs)
            .padding(.vertical, 2)
            .background(
                Capsule()
                    .fill(action == .blocked ? Color.successGreen.opacity(0.85) : Color.warningOrange.opacity(0.85))
            )
    }

    private func severityBadge(_ severity: AttemptSeverity) -> some View {
        Text(severity.localizedDisplayName(localizationManager))
            .font(.caption2.weight(.semibold))
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.xs)
            .padding(.vertical, 2)
            .background(
                Capsule()
                    .fill(severity == .critical || severity == .high ? Color.dangerRed.opacity(0.85) : Color.warningOrange.opacity(0.85))
            )
    }

    private func actionButton(
        title: String,
        color: Color,
        disabled: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
        }
        .buttonStyle(.plain)
        .foregroundColor(color)
        .disabled(disabled)
    }

    private func metricChip(title: String, value: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.headline.weight(.bold))
                .foregroundColor(.white)
            Text(title)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.75))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.s)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}

// MARK: - Monitor (B4-04 fraud toggle → agent)

struct IdentityHubMonitorPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = IdentityMonitorViewModel()
    @ObservedObject private var protectionSettingsManager = ProtectionSettingsManager.shared

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("identity_hub_monitor_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            if let stats = viewModel.stats {
                HStack(spacing: Spacing.s) {
                    metricChip(
                        title: localizationManager.localized("identity_theft_suspicious"),
                        value: "\(stats.suspiciousActivities)"
                    )
                    metricChip(
                        title: localizationManager.localized("identity_theft_blocked"),
                        value: "\(stats.blockedAttempts)"
                    )
                }
            }

            fraudProtectionToggle

            if viewModel.requiresPremiumUpgrade {
                AntifakeInlinePremiumGateCard(message: viewModel.errorMessage) {
                    showPremiumPaywall = true
                }
                .environmentObject(localizationManager)
            } else if let error = viewModel.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
                    .accessibilityIdentifier("identity_hub_monitor_error")
            }

            if viewModel.isFraudProtectionEnabled {
                PrimaryButton(
                    localizationManager.localized("identity_hub_monitor_credit_button"),
                    isLoading: viewModel.isRunningMonitor,
                    isDisabled: !viewModel.canRunCreditMonitor
                ) {
                    Task {
                        await viewModel.runCreditMonitor()
                        if viewModel.requiresPremiumUpgrade {
                            showPremiumPaywall = true
                        } else if viewModel.monitorVerdict != nil {
                            HapticFeedback.notification(.success)
                        }
                    }
                }
                .accessibilityIdentifier("identity_hub_monitor_credit_button")
            }

            if let verdict = viewModel.monitorVerdict {
                AntifakeVerdictCard(verdict: verdict)
                    .environmentObject(localizationManager)
                    .accessibilityIdentifier("identity_hub_monitor_verdict")
            }
        }
        .overlay {
            if viewModel.isLoadingStats && viewModel.stats == nil {
                ProgressView()
                    .tint(.white)
            }
        }
        .refreshable {
            await viewModel.refresh()
            if viewModel.requiresPremiumUpgrade {
                showPremiumPaywall = true
            }
        }
        .onAppear {
            viewModel.syncFraudEnabledFromLocalSettings()
        }
        .onChange(of: protectionSettingsManager.settings.fraudEnabled) { _ in
            viewModel.syncFraudEnabledFromLocalSettings()
        }
        .task {
            await viewModel.refresh()
            if viewModel.requiresPremiumUpgrade {
                showPremiumPaywall = true
            }
        }
    }

    private var fraudProtectionToggle: some View {
        HStack(alignment: .center, spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("identity_hub_monitor_toggle_title"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                Text(localizationManager.localized("identity_hub_monitor_toggle_subtitle"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            }

            Spacer(minLength: Spacing.s)

            if viewModel.isUpdatingToggle {
                ProgressView()
                    .tint(.white)
            } else {
                ALADDINToggle(
                    isOn: fraudToggleBinding,
                    size: 36
                )
                .disabled(!viewModel.isFraudCategoryAvailable && !viewModel.isFraudProtectionEnabled)
                .accessibilityIdentifier("identity_hub_monitor_fraud_toggle")
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private var fraudToggleBinding: Binding<Bool> {
        Binding(
            get: { viewModel.isFraudProtectionEnabled },
            set: { newValue in
                Task {
                    await viewModel.setFraudProtectionEnabled(newValue)
                    if viewModel.requiresPremiumUpgrade {
                        showPremiumPaywall = true
                    } else if newValue, viewModel.monitorVerdict != nil {
                        HapticFeedback.notification(.success)
                    } else if viewModel.errorMessage != nil {
                        HapticFeedback.notification(.error)
                    }
                }
            }
        )
    }

    private func metricChip(title: String, value: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.headline.weight(.bold))
                .foregroundColor(.white)
            Text(title)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.75))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.s)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}

#if DEBUG
struct IdentityHubScreen_Previews: PreviewProvider {
    static var previews: some View {
        IdentityHubScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
            .environmentObject(SubscriptionManager.shared)
    }
}
#endif

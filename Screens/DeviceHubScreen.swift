import SwiftUI

/// B5-01 — Device Hub: Cyber · Components · Mobile · IoT · Coverage.
struct DeviceHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var subscriptionManager: SubscriptionManager

    @State private var selectedTab: DeviceHubTab = .cyber
    @State private var showPremiumPaywall = false

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
        .accessibilityIdentifier("device_hub_root")
        .onAppear { applyPendingTabIfNeeded() }
        .onChange(of: navigationManager.pendingDeviceHubTab) { tab in
            guard let tab else { return }
            navigationManager.pendingDeviceHubTab = nil
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
        if let tab = navigationManager.pendingDeviceHubTab {
            navigationManager.pendingDeviceHubTab = nil
            selectedTab = tab
        }
    }

    private var header: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("device_hub_title"),
            subtitle: localizationManager.localized("device_hub_subtitle"),
            showBackButton: true,
            onBack: { navigationManager.goBack() }
        )
    }

    private var tabPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: Spacing.xs) {
                ForEach(DeviceHubTab.allCases) { tab in
                    Button {
                        withAnimation(.easeInOut(duration: 0.2)) { selectedTab = tab }
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
                        .padding(.horizontal, Spacing.s)
                        .padding(.vertical, Spacing.s)
                        .foregroundColor(selectedTab == tab ? .white : .white.opacity(0.65))
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(selectedTab == tab ? Color.secondaryGold.opacity(0.35) : Color.white.opacity(0.08))
                        )
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("device_hub_tab_\(tab.rawValue)")
                }
            }
        }
    }

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .cyber:
            DeviceHubCyberPanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .components:
            DeviceHubComponentsPanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .mobile:
            DeviceHubMobilePanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .iot:
            DeviceHubIoTPanel(showPremiumPaywall: $showPremiumPaywall)
                .environmentObject(localizationManager)
        case .coverage:
            DeviceHubThreatCoverageView()
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
        }
    }
}

enum DeviceHubTab: String, CaseIterable, Identifiable {
    case cyber
    case components
    case mobile
    case iot
    case coverage

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .cyber: return "device_hub_tab_cyber"
        case .components: return "device_hub_tab_components"
        case .mobile: return "device_hub_tab_mobile"
        case .iot: return "device_hub_tab_iot"
        case .coverage: return "device_hub_tab_coverage"
        }
    }

    var iconName: String {
        switch self {
        case .cyber: return "shield.lefthalf.filled"
        case .components: return "square.grid.2x2.fill"
        case .mobile: return "iphone"
        case .iot: return "house.fill"
        case .coverage: return "checkmark.shield.fill"
        }
    }
}

// MARK: - Cyber panel (B5-02, B5-05, B5-09)

private struct DeviceHubCyberPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = DeviceCyberScanViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            if let stats = viewModel.protectionStats {
                protectionStatsCard(stats)
            }

            PrimaryButton(
                localizationManager.localized("malware_detection.quick_scan"),
                icon: "magnifyingglass",
                isLoading: viewModel.isRunningQuickScan
            ) {
                Task { await viewModel.runQuickScan() }
            }

            PrimaryButton(
                localizationManager.localized("device_hub_eicar_test"),
                icon: "ladybug.fill",
                isLoading: viewModel.isRunningEicarTest
            ) {
                Task { await viewModel.runEicarTest() }
            }

            if viewModel.eicarDetected {
                Text(localizationManager.localized("device_hub_eicar_detected"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.warningOrange)
            }

            if let scan = viewModel.lastScan {
                DeviceScanResultCard(result: scan)
                    .environmentObject(localizationManager)
            }

            if viewModel.serverThreatCount > 0 {
                Text("\(localizationManager.localized("device_hub_server_threats")): \(viewModel.serverThreatCount)")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.75))
            }

            errorBanner
        }
        .task { await viewModel.refresh() }
        .onChange(of: viewModel.requiresPremiumUpgrade) { needsUpgrade in
            if needsUpgrade { showPremiumPaywall = true }
        }
    }

    private func protectionStatsCard(_ stats: ProtectionStatsResponse) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("device_hub_protection_stats"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.white)
            HStack {
                statCell(
                    title: localizationManager.localized("device_hub_stats_blocked"),
                    value: "\(stats.threatsBlocked)"
                )
                statCell(
                    title: localizationManager.localized("device_hub_stats_score"),
                    value: "\(stats.securityScore)"
                )
                statCell(
                    title: localizationManager.localized("device_hub_stats_active"),
                    value: "\(stats.functionsActive)"
                )
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private func statCell(title: String, value: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.weight(.bold))
                .foregroundColor(.secondaryGold)
            Text(title)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.7))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
    }

    @ViewBuilder
    private var errorBanner: some View {
        if let error = viewModel.errorMessage {
            Text(error)
                .font(.caption)
                .foregroundColor(.dangerRed)
        }
    }
}

// MARK: - Components panel (B5-03)

private struct DeviceHubComponentsPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = DeviceComponentsScanViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("device_hub_components_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            ForEach(DeviceComponentScanKind.allCases) { kind in
                PrimaryButton(
                    localizationManager.localized(kind.titleKey),
                    icon: kind.systemImage,
                    isLoading: viewModel.runningKind == kind
                ) {
                    Task { await viewModel.runScan(kind) }
                }
            }

            if let verdict = viewModel.phishingVerdict {
                AntifakeVerdictCard(verdict: verdict)
                    .environmentObject(localizationManager)
            }
            if let result = viewModel.networkResult {
                DeviceScanResultCard(result: result)
                    .environmentObject(localizationManager)
            }
            if let result = viewModel.mobileResult {
                DeviceScanResultCard(result: result)
                    .environmentObject(localizationManager)
            }
            if let incident = viewModel.incidentResult {
                DeviceIncidentResultCard(result: incident)
                    .environmentObject(localizationManager)
            }

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
            }
        }
        .onChange(of: viewModel.requiresPremiumUpgrade) { needsUpgrade in
            if needsUpgrade { showPremiumPaywall = true }
        }
    }
}

// MARK: - Mobile panel (B5-07)

private struct DeviceHubMobilePanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = DeviceMobilePanelViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("tariffs_threat_category_mobile"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                    Text(localizationManager.localized("device_hub_mobile_toggle_hint"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
                Spacer()
                if viewModel.isUpdatingToggle {
                    ProgressView().tint(.white)
                } else {
                    ALADDINToggle(isOn: mobileToggleBinding, size: 36)
                }
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)

            PrimaryButton(
                localizationManager.localized("mobile_security.security_check"),
                icon: "checkmark.shield",
                isLoading: viewModel.isRunningScan
            ) {
                Task { await viewModel.runDeviceScan() }
            }

            if let scan = viewModel.lastScan {
                DeviceScanResultCard(result: scan)
                    .environmentObject(localizationManager)
            }

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
            }
        }
        .onAppear { viewModel.syncMobileEnabledFromLocalSettings() }
        .onChange(of: viewModel.requiresPremiumUpgrade) { needsUpgrade in
            if needsUpgrade { showPremiumPaywall = true }
        }
    }

    private var mobileToggleBinding: Binding<Bool> {
        Binding(
            get: { viewModel.isMobileProtectionEnabled },
            set: { newValue in
                Task {
                    await viewModel.setMobileProtectionEnabled(newValue)
                    if viewModel.requiresPremiumUpgrade { showPremiumPaywall = true }
                }
            }
        )
    }
}

// MARK: - IoT panel (B5-04, B5-08)

private struct DeviceHubIoTPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @StateObject private var viewModel = DeviceIoTPanelViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("tariffs_threat_category_iot"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                    Text(localizationManager.localized("device_hub_iot_toggle_hint"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
                Spacer()
                ALADDINToggle(isOn: iotToggleBinding, size: 36)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)

            HStack {
                statCell(title: localizationManager.localized("iot_security_devices_label"), value: "\(viewModel.devicesCount)")
                statCell(title: localizationManager.localized("iot_security_threats_label"), value: "\(viewModel.threatsCount)")
                statCell(title: localizationManager.localized("iot_security_protection_label"), value: "\(viewModel.protectionLevel)%")
            }

            PrimaryButton(
                localizationManager.localized("device_hub_iot_scan"),
                icon: "wifi.router.fill",
                isLoading: viewModel.isScanning
            ) {
                Task { await viewModel.runHomeScan() }
            }

            ForEach(viewModel.threats) { threat in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(threat.description)
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        Text(threat.severity.rawValue.capitalized)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    Spacer()
                    Button {
                        Task { await viewModel.fixThreat(threat.id) }
                    } label: {
                        if viewModel.fixingThreatId == threat.id {
                            ProgressView()
                                .tint(.secondaryGold)
                        } else {
                            Text(localizationManager.localized("device_hub_iot_fix"))
                                .font(.caption.weight(.semibold))
                                .foregroundColor(.secondaryGold)
                        }
                    }
                    .disabled(viewModel.fixingThreatId != nil)
                }
                .padding(Spacing.m)
                .stormGlassCard(cornerRadius: CornerRadius.medium)
            }

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
            }
        }
        .task { await viewModel.refresh() }
        .onAppear { viewModel.syncIoTEnabledFromLocalSettings() }
        .onChange(of: viewModel.requiresPremiumUpgrade) { needsUpgrade in
            if needsUpgrade { showPremiumPaywall = true }
        }
    }

    private var iotToggleBinding: Binding<Bool> {
        Binding(
            get: { viewModel.isIoTProtectionEnabled },
            set: { newValue in
                Task {
                    await viewModel.setIoTProtectionEnabled(newValue)
                    if viewModel.requiresPremiumUpgrade { showPremiumPaywall = true }
                }
            }
        )
    }

    private func statCell(title: String, value: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.weight(.bold))
                .foregroundColor(.secondaryGold)
            Text(title)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
    }
}

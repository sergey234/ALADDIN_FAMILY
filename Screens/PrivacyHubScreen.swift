import SwiftUI

/// B3-05 — Privacy Hub: Dark Web · Data Cleanup · Location Bubble.
struct PrivacyHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var selectedTab: PrivacyHubTab = .darkWeb

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .data)

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
        .accessibilityIdentifier("privacy_hub_root")
        .onAppear {
            applyPendingTabIfNeeded()
        }
        .onChange(of: navigationManager.pendingPrivacyHubTab) { tab in
            guard let tab else { return }
            navigationManager.pendingPrivacyHubTab = nil
            selectedTab = tab
        }
    }

    private func applyPendingTabIfNeeded() {
        if let tab = navigationManager.pendingPrivacyHubTab {
            navigationManager.pendingPrivacyHubTab = nil
            selectedTab = tab
        }
    }

    private var header: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("privacy_hub_title"),
            subtitle: localizationManager.localized("privacy_hub_subtitle"),
            showBackButton: true,
            onBack: { navigationManager.goBack() }
        )
    }

    private var tabPicker: some View {
        HStack(spacing: Spacing.xs) {
            ForEach(PrivacyHubTab.allCases) { tab in
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
                            .fill(selectedTab == tab ? Color.primaryBlue.opacity(0.35) : Color.white.opacity(0.08))
                    )
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("privacy_hub_tab_\(tab.rawValue)")
            }
        }
    }

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .darkWeb:
            PrivacyHubDarkWebPanel()
                .environmentObject(localizationManager)
        case .cleanup:
            PrivacyHubCleanupPanel()
                .environmentObject(localizationManager)
        case .location:
            PrivacyHubLocationPanel()
                .environmentObject(localizationManager)
        }
    }
}

enum PrivacyHubTab: String, CaseIterable, Identifiable {
    case darkWeb
    case cleanup
    case location

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .darkWeb: return "privacy_hub_tab_darkweb"
        case .cleanup: return "privacy_hub_tab_cleanup"
        case .location: return "privacy_hub_tab_location"
        }
    }

    var iconName: String {
        switch self {
        case .darkWeb: return "eye.trianglebadge.exclamationmark"
        case .cleanup: return "trash.fill"
        case .location: return "location.fill"
        }
    }
}

// MARK: - Dark Web (B3-01, B3-02)

struct PrivacyHubDarkWebPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = DarkWebMonitoringViewModel()
    @State private var showDataInput = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_hub_darkweb_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            if let stats = viewModel.stats {
                HStack(spacing: Spacing.s) {
                    metricChip(title: localizationManager.localized("dark_web_total_leaks"), value: "\(stats.totalLeaks)")
                    metricChip(title: localizationManager.localized("dark_web_new_leaks"), value: "\(stats.newLeaks)")
                }
            }

            PrimaryButton(
                localizationManager.localized("dark_web_scan_start_button"),
                isLoading: viewModel.isScanning,
                isDisabled: !AppConfig.isDarkWebServerScanEnabled || viewModel.isLoading
            ) {
                Task {
                    await viewModel.startScan()
                    if viewModel.errorMessage == nil {
                        HapticFeedback.notification(.success)
                    }
                }
            }
            .accessibilityIdentifier("privacy_hub_darkweb_scan_cta")

            Button {
                showDataInput = true
            } label: {
                Label(localizationManager.localized("dark_web_scan_add_data"), systemImage: "plus.circle")
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.secondaryGold)
            }
            .buttonStyle(.plain)

            if viewModel.leaks.isEmpty && !viewModel.isLoading {
                Text(localizationManager.localized("dark_web_no_leaks"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.7))
            } else {
                ForEach(viewModel.leaks.prefix(8)) { leak in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(leak.maskedValue)
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        Text(leak.source)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(Spacing.m)
                    .stormGlassCard(cornerRadius: CornerRadius.medium)
                }
            }

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
            }
        }
        .task {
            await viewModel.loadData()
        }
        .sheet(isPresented: $showDataInput) {
            DarkWebDataInputView(isPresented: $showDataInput, viewModel: viewModel)
                .environmentObject(localizationManager)
        }
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

// MARK: - Data Cleanup (B3-03)

struct PrivacyHubCleanupPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = PrivacyReportsViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_hub_cleanup_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            if let stats = viewModel.cleanupStats {
                HStack(spacing: Spacing.s) {
                    metricChip(
                        title: localizationManager.localized("privacy_cleanup_total_freed"),
                        value: stats.formattedTotalFreed
                    )
                    metricChip(
                        title: localizationManager.localized("privacy_cleanup_count"),
                        value: "\(stats.cleanupsCount)"
                    )
                }
            }

            PrimaryButton(
                localizationManager.localized("privacy_cleanup_start"),
                isLoading: viewModel.isLoading
            ) {
                Task {
                    await viewModel.startCleanup(categories: ["cache", "temp", "logs"])
                    if viewModel.errorMessage == nil {
                        HapticFeedback.notification(.success)
                    }
                }
            }
            .accessibilityIdentifier("privacy_hub_cleanup_start")

            ForEach(viewModel.cleanupRecords.prefix(6)) { record in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(record.categories.map(\.name).joined(separator: ", "))
                            .font(.subheadline.weight(.medium))
                            .foregroundColor(.white)
                        Text(record.formattedDate)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    Spacer()
                    Text(record.formattedFreedSpace)
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.successGreen)
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
        .task {
            await viewModel.loadCleanupData()
        }
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

// MARK: - Location Bubble (B3-04)

struct PrivacyHubLocationPanel: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = PrivacyReportsViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_hub_location_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            if let stats = viewModel.locationStats {
                HStack(spacing: Spacing.s) {
                    metricChip(
                        title: localizationManager.localized("privacy_location_blocked"),
                        value: "\(stats.blockedRequests)"
                    )
                    metricChip(
                        title: localizationManager.localized("privacy_location_current_accuracy"),
                        value: stats.currentAccuracy.localizedDisplayName(localizationManager)
                    )
                }
            }

            PrimaryButton(
                localizationManager.localized("privacy_hub_location_generate"),
                isLoading: viewModel.isLoading
            ) {
                Task {
                    await viewModel.sendLocationBubble()
                    if viewModel.errorMessage == nil {
                        HapticFeedback.notification(.success)
                    }
                }
            }
            .accessibilityIdentifier("privacy_hub_location_bubble")

            ForEach(viewModel.locationRequests.prefix(6)) { request in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(request.appName)
                            .font(.subheadline.weight(.medium))
                            .foregroundColor(.white)
                        Text(request.formattedTimestamp)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    Spacer()
                    Text(request.action.localizedDisplayName(localizationManager))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(request.action == .blocked ? .successGreen : .warningOrange)
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
        .task {
            await viewModel.loadLocationData()
        }
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
struct PrivacyHubScreen_Previews: PreviewProvider {
    static var previews: some View {
        PrivacyHubScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
#endif

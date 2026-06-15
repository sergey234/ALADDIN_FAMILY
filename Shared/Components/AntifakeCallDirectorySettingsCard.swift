import SwiftUI
import CallKit

/// Call Directory enable + sync row (af-m2).
struct AntifakeCallDirectorySettingsCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var enabledStatus: CXCallDirectoryManager.EnabledStatus = .unknown
    @State private var isSyncing = false
    @State private var statusMessage: String?
    @State private var syncSucceeded = false
    @State private var showSetupGuide = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(localizationManager.localized("antifake_call_directory_title"), systemImage: "phone.badge.checkmark")
                .font(.headline)
                .foregroundColor(.white)

            Text(localizationManager.localized("antifake_call_directory_body"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.85))

            Text(statusText)
                .font(.caption.weight(.semibold))
                .foregroundColor(statusColor)
                .accessibilityIdentifier("antifake_call_directory_status_text")

            if enabledStatus == .disabled {
                HStack(alignment: .top, spacing: Spacing.xs) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.warningOrange)
                    Text(localizationManager.localized("antifake_call_directory_disabled_banner"))
                        .font(.caption2)
                        .foregroundColor(.warningOrange)
                }
                .padding(Spacing.s)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.warningOrange.opacity(0.15))
                .cornerRadius(CornerRadius.small)
                .accessibilityIdentifier("antifake_call_directory_disabled_banner")
            }

            VStack(spacing: Spacing.s) {
                SecondaryButton(
                    localizationManager.localized("antifake_call_directory_open_settings"),
                    icon: "list.number"
                ) {
                    showSetupGuide = true
                }
                PrimaryButton(
                    localizationManager.localized("antifake_call_directory_sync"),
                    icon: "arrow.triangle.2.circlepath",
                    isLoading: isSyncing,
                    isDisabled: isSyncing
                ) {
                    Task { await syncNow() }
                }
            }

            if let statusMessage, !statusMessage.isEmpty {
                Text(statusMessage)
                    .font(.caption2)
                    .foregroundColor(syncSucceeded ? .successGreen : .warningOrange)
            }

            postCallReminderToggle
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        .accessibilityIdentifier("antifake_call_directory_card")
        .accessibilityLabel(localizationManager.localized("antifake_call_directory_title"))
        .accessibilityHint(localizationManager.localized("antifake_call_directory_body"))
        .task { await refreshStatus() }
        .sheet(isPresented: $showSetupGuide) {
            AntifakeCallDirectorySetupSheet(onDismiss: { showSetupGuide = false })
                .environmentObject(localizationManager)
        }
    }

    private var statusText: String {
        switch enabledStatus {
        case .enabled:
            return localizationManager.localized("antifake_call_directory_status_enabled")
        case .disabled:
            return localizationManager.localized("antifake_call_directory_status_disabled")
        case .unknown:
            return localizationManager.localized("antifake_call_directory_status_unknown")
        @unknown default:
            return localizationManager.localized("antifake_call_directory_status_unknown")
        }
    }

    private var statusColor: Color {
        enabledStatus == .enabled ? .successGreen : .warningOrange
    }

    private var postCallReminderToggle: some View {
        Toggle(isOn: Binding(
            get: { AppConfig.isAntifakePostCallReminderEnabled },
            set: { UserDefaults.standard.set($0, forKey: AppConfig.UserDefaultsKeys.antifakePostCallReminderEnabled) }
        )) {
            Text(localizationManager.localized("antifake_post_call_reminder_toggle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.9))
        }
        .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
        .accessibilityIdentifier("antifake_post_call_reminder_toggle")
    }

    private func refreshStatus() async {
        let previous = enabledStatus
        enabledStatus = await AntifakeCallDirectorySyncService.extensionStatus()
        if enabledStatus == .enabled, previous != .enabled {
            AntifakeAnalytics.track(.cdEnable)
        }
    }

    private func syncNow() async {
        isSyncing = true
        defer { isSyncing = false }
        let outcome = await AntifakeCallDirectorySyncService.syncFromServer()
        await refreshStatus()
        switch outcome {
        case .success(let syncedCount, let updatedAt):
            syncSucceeded = true
            let dateText = DateFormatter.localizedString(from: updatedAt, dateStyle: .short, timeStyle: .none)
            statusMessage = String(
                format: localizationManager.localized("antifake_call_directory_sync_success_count"),
                syncedCount,
                dateText
            )
            AntifakeFamilyCDStatusReporter.report(
                extensionEnabled: enabledStatus == .enabled,
                syncedCount: syncedCount
            )
            AntifakeAnalytics.track(
                .cdSync,
                extra: ["synced_count": String(syncedCount)]
            )
            HapticFeedback.notification(.success)
        case .failure(let kind):
            syncSucceeded = false
            statusMessage = localizedSyncError(for: kind)
        }
    }

    private func localizedSyncError(for kind: AntifakeCallDirectorySyncFailure) -> String {
        switch kind {
        case .notFound:
            return localizationManager.localized("antifake_call_directory_sync_error_404")
        case .unauthorized:
            return localizationManager.localized("antifake_call_directory_sync_error_auth")
        case .premiumRequired:
            return localizationManager.localized("antifake_call_directory_sync_error_premium")
        case .other:
            return localizationManager.localized("antifake_call_directory_sync_error_generic")
        }
    }
}

/// A-08 — animated onboarding hint (Settings → Phone → ALADDIN toggle).
private struct AntifakeCallDirectorySetupAnimation: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var phase = 0

    private let symbols = ["gearshape.fill", "phone.fill", "togglepower"]

    var body: some View {
        HStack(spacing: Spacing.m) {
            ForEach(Array(symbols.enumerated()), id: \.offset) { index, symbol in
                Image(systemName: symbol)
                    .font(.system(size: index == phase ? 34 : 26, weight: .semibold))
                    .foregroundColor(index == phase ? .primaryBlue : .textSecondary.opacity(0.5))
                    .frame(maxWidth: .infinity)
                    .scaleEffect(index == phase ? 1.08 : 1.0)
                    .animation(.easeInOut(duration: 0.35), value: phase)
                if index < symbols.count - 1 {
                    Image(systemName: "chevron.right")
                        .font(.caption.weight(.bold))
                        .foregroundColor(.textSecondary.opacity(0.4))
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(localizationManager.localized("antifake_call_directory_setup_animation_accessibility"))
        .onAppear {
            Timer.scheduledTimer(withTimeInterval: 1.2, repeats: true) { _ in
                phase = (phase + 1) % symbols.count
            }
        }
    }
}

/// Step-by-step guide — iOS has no public deep link to Phone → Call Blocking (af-m2 UX).
private struct AntifakeCallDirectorySetupSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onDismiss: () -> Void

    private var usesIOS18AppsPhonePath: Bool {
        if #available(iOS 18.0, *) { return true }
        return false
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("antifake_call_directory_setup_intro"))
                        .font(.body)
                        .foregroundColor(.textSecondary)

                    AntifakeCallDirectorySetupAnimation()
                        .environmentObject(localizationManager)
                        .padding(.vertical, Spacing.s)

                    VStack(alignment: .leading, spacing: Spacing.s) {
                        setupStep(localizationManager.localized("antifake_call_directory_setup_step1"))
                        if usesIOS18AppsPhonePath {
                            setupStep(localizationManager.localized("antifake_call_directory_setup_step2_ios18"))
                            setupStep(localizationManager.localized("antifake_call_directory_setup_step3_ios18"))
                            setupStep(localizationManager.localized("antifake_call_directory_setup_step4_ios18"))
                        } else {
                            setupStep(localizationManager.localized("antifake_call_directory_setup_step2"))
                            setupStep(localizationManager.localized("antifake_call_directory_setup_step3"))
                            setupStep(localizationManager.localized("antifake_call_directory_setup_step4"))
                        }
                        setupStep(localizationManager.localized("antifake_call_directory_setup_step5_retry"))
                    }
                    .padding(Spacing.m)
                    .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .primaryBlue)

                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Label(
                            localizationManager.localized("antifake_call_directory_setup_retry_title"),
                            systemImage: "arrow.clockwise.circle.fill"
                        )
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.warningOrange)
                        Text(localizationManager.localized("antifake_call_directory_setup_retry_body"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .fixedSize(horizontal: false, vertical: true)
                        Toggle(isOn: .constant(true)) {
                            Text("ALADDIN")
                                .font(.caption.weight(.semibold))
                        }
                        .toggleStyle(SwitchToggleStyle(tint: .successGreen))
                        .disabled(true)
                        .accessibilityLabel("ALADDIN")
                        .accessibilityHint(localizationManager.localized("antifake_call_directory_setup_retry_title"))
                    }
                    .padding(Spacing.m)
                    .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .warningOrange)
                    .accessibilityIdentifier("antifake_call_directory_setup_retry")
                }
                .padding(Spacing.screenPadding)
            }
            .background(StormMeshBackground(variant: .shield).ignoresSafeArea())
            .navigationTitle(localizationManager.localized("antifake_call_directory_setup_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("antifake_call_directory_setup_done")) {
                        onDismiss()
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func setupStep(_ text: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.s) {
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.primaryBlue)
            Text(text)
                .font(.subheadline)
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

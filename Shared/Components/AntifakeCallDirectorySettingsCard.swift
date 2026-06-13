import SwiftUI
import CallKit

/// Call Directory enable + sync row (af-m2).
struct AntifakeCallDirectorySettingsCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var enabledStatus: CXCallDirectoryManager.EnabledStatus = .unknown
    @State private var isSyncing = false
    @State private var statusMessage: String?

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

            HStack(spacing: Spacing.s) {
                SecondaryButton(
                    localizationManager.localized("antifake_call_directory_open_settings"),
                    icon: "gear"
                ) {
                    if let url = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(url)
                    }
                }
                PrimaryButton(
                    localizationManager.localized("antifake_call_directory_sync"),
                    isLoading: isSyncing,
                    isDisabled: isSyncing
                ) {
                    Task { await syncNow() }
                }
            }

            if let statusMessage, !statusMessage.isEmpty {
                Text(statusMessage)
                    .font(.caption2)
                    .foregroundColor(.warningOrange)
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        .accessibilityIdentifier("antifake_call_directory_card")
        .task { await refreshStatus() }
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

    private func refreshStatus() async {
        enabledStatus = await AntifakeCallDirectorySyncService.extensionStatus()
    }

    private func syncNow() async {
        isSyncing = true
        defer { isSyncing = false }
        statusMessage = await AntifakeCallDirectorySyncService.syncFromServer()
        await refreshStatus()
        if statusMessage == nil {
            HapticFeedback.notification(.success)
        }
    }
}

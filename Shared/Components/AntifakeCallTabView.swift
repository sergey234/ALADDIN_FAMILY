import SwiftUI

/// Call tab: recording check (Section A) + Call Directory incoming labels (Section B).
struct AntifakeCallTabView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool
    @Binding var showPostCallUploadPrompt: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            recordingSection
            incomingLabelsSection
        }
    }

    private var recordingSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            AntifakeHubSectionHeader(
                titleKey: "antifake_call_section_recording_title",
                subtitleKey: "antifake_call_section_recording_subtitle"
            )
            .environmentObject(localizationManager)
            .accessibilityIdentifier("antifake_call_section_recording")

            AntifakeMediaCheckView(
                mediaKind: .call,
                titleKey: "antifake_call_title",
                hintKey: "antifake_call_hint",
                systemImage: "phone.arrow.up.right.fill",
                panelId: "antifake_call_panel",
                showPremiumPaywall: $showPremiumPaywall,
                showPostCallUploadPrompt: $showPostCallUploadPrompt,
                showsPanelTitle: false
            )
            .environmentObject(localizationManager)

            AntifakePostCallReminderToggle()
                .environmentObject(localizationManager)
        }
    }

    private var incomingLabelsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.xs)

            AntifakeHubSectionHeader(
                titleKey: "antifake_call_section_incoming_title",
                subtitleKey: "antifake_call_section_incoming_subtitle"
            )
            .environmentObject(localizationManager)
            .accessibilityIdentifier("antifake_call_section_incoming")

            AntifakeCallDirectorySettingsCard()
                .environmentObject(localizationManager)
        }
    }
}

struct AntifakeHubSectionHeader: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let titleKey: String
    let subtitleKey: String

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(localizationManager.localized(titleKey))
                .font(.headline)
                .foregroundColor(.white)
                .accessibilityAddTraits(.isHeader)
            Text(localizationManager.localized(subtitleKey))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

struct AntifakePostCallReminderToggle: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
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
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}

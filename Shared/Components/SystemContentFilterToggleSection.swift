import SwiftUI

/// WAVE3 — toggle for NE Content Filter, placed next to Safari Content Blocker UX.
struct SystemContentFilterToggleSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let categories: [ContentBlockerCategory]
    var compact: Bool = false

    @AppStorage(SystemContentFilterRulesStore.optedInDefaultsKey) private var isOn: Bool = false
    @State private var isBusy = false
    @State private var statusMessage: String?

    var body: some View {
        if AppStoreBuildPolicy.allowsSystemContentFilter {
            VStack(alignment: .leading, spacing: Spacing.s) {
                Toggle(isOn: Binding(
                    get: { isOn },
                    set: { newValue in
                        apply(newValue)
                    }
                )) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(localizationManager.localized("system_filter_toggle_title"))
                            .font(compact ? .caption.weight(.semibold) : .subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                        Text(localizationManager.localized("system_filter_toggle_footer"))
                            .font(.caption2)
                            .foregroundColor(.textSecondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .tint(.secondaryGold)
                .disabled(isBusy)
                .accessibilityIdentifier("system_content_filter_toggle")

                if isBusy {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.secondaryGold)
                }

                if let statusMessage, !statusMessage.isEmpty {
                    Text(statusMessage)
                        .font(.caption2)
                        .foregroundColor(.warningOrange)
                        .fixedSize(horizontal: false, vertical: true)
                        .accessibilityIdentifier("system_content_filter_status")
                }
            }
            .padding(compact ? Spacing.s : Spacing.m)
            .background(Color.white.opacity(compact ? 0.06 : 0.10))
            .cornerRadius(CornerRadius.medium)
        }
    }

    private func apply(_ enabled: Bool) {
        isBusy = true
        statusMessage = nil
        HapticFeedback.impact(.light)
        SystemContentFilterRulesStore.setEnabled(enabled, categories: categories) { result in
            DispatchQueue.main.async {
                isBusy = false
                switch result {
                case .success:
                    isOn = enabled
                    statusMessage = enabled
                        ? localizationManager.localized("system_filter_toggle_on_hint")
                        : localizationManager.localized("system_filter_toggle_off_hint")
                    HapticFeedback.notification(.success)
                case .failure(let error):
                    isOn = false
                    statusMessage = String(
                        format: localizationManager.localized("system_filter_toggle_error_fmt"),
                        error.localizedDescription
                    )
                    HapticFeedback.notification(.error)
                }
            }
        }
    }
}

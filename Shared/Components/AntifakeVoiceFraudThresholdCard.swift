import SwiftUI

/// fws-06 — GenAI/voice fraud sensitivity for Call Directory + post-call ingest.
struct AntifakeVoiceFraudThresholdCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var settings = AntifakeSettingsService.shared

    @State private var draftThreshold: Double = 72
    @State private var isSaving = false
    @State private var statusMessage: String?

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("antifake_voice_fraud_threshold_title"),
                systemImage: "waveform.badge.magnifyingglass"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(localizationManager.localized("antifake_voice_fraud_threshold_body"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.85))
                .fixedSize(horizontal: false, vertical: true)

            presetRow

            HStack {
                Text(localizationManager.localized("antifake_voice_fraud_threshold_slider_label"))
                    .font(.caption.weight(.semibold))
                Spacer()
                Text(String(format: localizationManager.localized("antifake_voice_fraud_threshold_value"), Int(draftThreshold)))
                    .font(.caption.monospacedDigit())
                    .foregroundColor(.secondaryGold)
            }

            Slider(
                value: $draftThreshold,
                in: Double(settings.minThresholdPercent)...Double(settings.maxThresholdPercent),
                step: 5
            ) { editing in
                if !editing {
                    Task { await persistThreshold(triggerSync: true) }
                }
            }
            .tint(.secondaryGold)
            .accessibilityIdentifier("antifake_voice_fraud_threshold_slider")

            Text(thresholdHint)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.7))

            if let statusMessage, !statusMessage.isEmpty {
                Text(statusMessage)
                    .font(.caption2)
                    .foregroundColor(.warningOrange)
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .secondaryGold)
        .accessibilityIdentifier("antifake_voice_fraud_threshold_card")
        .task {
            await settings.refresh()
            draftThreshold = Double(settings.thresholdPercent)
        }
        .onChange(of: settings.thresholdPercent) { value in
            draftThreshold = Double(value)
        }
    }

    private var presetRow: some View {
        HStack(spacing: Spacing.s) {
            presetButton(
                titleKey: "antifake_voice_fraud_preset_mild",
                value: settings.presetMild()
            )
            presetButton(
                titleKey: "antifake_voice_fraud_preset_balanced",
                value: settings.presetBalanced()
            )
            presetButton(
                titleKey: "antifake_voice_fraud_preset_strict",
                value: settings.presetStrict()
            )
        }
    }

    private func presetButton(titleKey: String, value: Int) -> some View {
        let selected = Int(draftThreshold) == value
        return Button {
            draftThreshold = Double(value)
            Task { await persistThreshold(triggerSync: true) }
        } label: {
            Text(localizationManager.localized(titleKey))
                .font(.caption2.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(selected ? Color.secondaryGold.opacity(0.35) : Color.white.opacity(0.08))
                .cornerRadius(8)
        }
        .buttonStyle(.plain)
        .foregroundColor(.white)
    }

    private var thresholdHint: String {
        let value = Int(draftThreshold)
        if value <= settings.presetMild() {
            return localizationManager.localized("antifake_voice_fraud_threshold_hint_mild")
        }
        if value >= settings.presetStrict() {
            return localizationManager.localized("antifake_voice_fraud_threshold_hint_strict")
        }
        return localizationManager.localized("antifake_voice_fraud_threshold_hint_balanced")
    }

    private func persistThreshold(triggerSync: Bool) async {
        guard !isSaving else { return }
        isSaving = true
        defer { isSaving = false }
        statusMessage = nil
        let ok = await settings.updateThreshold(Int(draftThreshold))
        if !ok {
            statusMessage = localizationManager.localized("antifake_voice_fraud_threshold_save_error")
            return
        }
        guard triggerSync else { return }
        // Stricter threshold must drop numbers no longer returned by server — force full sync.
        AntifakeCallDirectoryStore.saveReplacing(.empty)
        let sync = await AntifakeCallDirectorySyncService.syncFromServer()
        if case .failure(let kind) = sync {
            switch kind {
            case .premiumRequired:
                statusMessage = localizationManager.localized("antifake_call_directory_sync_error_premium")
            case .unauthorized:
                statusMessage = localizationManager.localized("antifake_call_directory_sync_error_auth")
            default:
                statusMessage = localizationManager.localized("antifake_voice_fraud_threshold_sync_hint")
            }
        }
    }
}

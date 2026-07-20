import SwiftUI

/// p2-10e — ON/OFF, track, volume (persisted).
struct BreathAmbientAudioControls: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var enabled = BreathAmbientAudioSettings.isEnabled
    @State private var track = BreathAmbientAudioSettings.track
    @State private var volume = Double(BreathAmbientAudioSettings.volume)

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Toggle(
                localizationManager.localized("wellness_breath_audio_toggle"),
                isOn: $enabled
            )
            .toggleStyle(SwitchToggleStyle(tint: Color(hex: "8B5CF6")))
            .onChange(of: enabled) { on in
                BreathAmbientAudioSettings.isEnabled = on
                if on {
                    BreathAmbientAudioPlayer.shared.startIfNeeded()
                } else {
                    BreathAmbientAudioPlayer.shared.stop()
                }
            }
            .accessibilityIdentifier("wellness_breath_audio_toggle")

            if enabled {
                Picker(
                    localizationManager.localized("wellness_breath_audio_track"),
                    selection: $track
                ) {
                    ForEach(BreathAmbientTrack.allCases) { t in
                        Text(localizationManager.localized(t.titleKey)).tag(t)
                    }
                }
                .pickerStyle(.segmented)
                .onChange(of: track) { t in
                    BreathAmbientAudioSettings.track = t
                    BreathAmbientAudioPlayer.shared.startIfNeeded()
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("wellness_breath_audio_volume"))
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.7))
                    Slider(value: $volume, in: 0...1, step: 0.05)
                        .tint(Color(hex: "8B5CF6"))
                        .onChange(of: volume) { v in
                            BreathAmbientAudioSettings.volume = Float(v)
                            BreathAmbientAudioPlayer.shared.applyVolume()
                        }
                        .accessibilityIdentifier("wellness_breath_audio_volume")
                }
            }
        }
        .font(.caption)
        .foregroundColor(.white)
    }
}

import SwiftUI

struct AudioSettingsView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool

    @State private var masterVolume: Float = 1.0
    @State private var effectsVolume: Float = 0.8
    @State private var musicVolume: Float = 0.6
    @State private var isMuted: Bool = false

    var body: some View {
        NavigationView {
            Form {
                Section("Audio") {
                    Toggle("Mute", isOn: Binding(
                        get: { isMuted },
                        set: {
                            isMuted = $0
                            AudioManager.shared.setMuted($0)
                        }
                    ))
                    sliderRow(title: "Master", value: $masterVolume) { AudioManager.shared.setMasterVolume($0) }
                    sliderRow(title: "Effects", value: $effectsVolume) { AudioManager.shared.setEffectsVolume($0) }
                    sliderRow(title: "Music", value: $musicVolume) { AudioManager.shared.setMusicVolume($0) }
                }

                Section("Preview") {
                    Button("Play click") {
                        SoundEffectPlayer.shared.play(.click, priority: .low)
                    }
                    Button("Play success") {
                        SoundEffectPlayer.shared.play(.success, priority: .medium)
                    }
                    Button("Voice prompt") {
                        let lang = localizationManager.currentLanguage == .russian ? "ru-RU" : "en-US"
                        let text = localizationManager.currentLanguage == .russian
                            ? "Проверьте настройки звука."
                            : "Audio settings preview."
                        SoundEffectPlayer.shared.playVoicePrompt(text, languageCode: lang, priority: .high)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("audio_settings_title"))
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button(localizationManager.localized("child_interface_back")) {
                        isPresented = false
                    }
                }
            }
            .onAppear {
                // Keep UI in sync with persisted audio preferences.
                masterVolume = AudioManager.shared.masterVolume
                effectsVolume = AudioManager.shared.effectsVolume
                musicVolume = AudioManager.shared.musicVolume
                isMuted = AudioManager.shared.isMuted
            }
        }
    }

    private func sliderRow(title: String, value: Binding<Float>, onChange: @escaping (Float) -> Void) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("\(title): \(Int(value.wrappedValue * 100))%")
            Slider(
                value: Binding(
                    get: { Double(value.wrappedValue) },
                    set: {
                        value.wrappedValue = Float($0)
                        onChange(value.wrappedValue)
                    }
                ),
                in: 0...1
            )
        }
        .padding(.vertical, 4)
    }
}


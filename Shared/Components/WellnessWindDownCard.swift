import SwiftUI

/// fws-18 — wind-down toggle + bedtime picker (local pushes 30/15/5 min).
struct WellnessWindDownCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var onPreviewStories: () -> Void

    @State private var enabled = WellnessSessionStore.windDownEnabled
    @State private var hour = WellnessSessionStore.windDownBedtime.hour
    @State private var minute = WellnessSessionStore.windDownBedtime.minute

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Toggle(isOn: $enabled) {
                Label(
                    localizationManager.localized("wellness_wind_down_title"),
                    systemImage: "moon.zzz.fill"
                )
                .font(.subheadline.bold())
            }
            .toggleStyle(SwitchToggleStyle(tint: Color(hex: "8B5CF6")))
            .onChange(of: enabled) { newValue in
                WellnessSessionStore.setWindDownEnabled(newValue)
                Task { await WindDownScheduler.shared.reschedule() }
            }

            Text(localizationManager.localized("wellness_wind_down_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))

            if enabled {
                HStack {
                    Text(localizationManager.localized("wellness_wind_down_bedtime"))
                        .font(.caption)
                    Spacer()
                    Picker("", selection: $hour) {
                        ForEach(18..<24, id: \.self) { h in
                            Text(String(format: "%02d", h)).tag(h)
                        }
                    }
                    .pickerStyle(.menu)
                    Text(":")
                    Picker("", selection: $minute) {
                        ForEach([0, 15, 30, 45], id: \.self) { m in
                            Text(String(format: "%02d", m)).tag(m)
                        }
                    }
                    .pickerStyle(.menu)
                }
                .onChange(of: hour) { _ in persistBedtime() }
                .onChange(of: minute) { _ in persistBedtime() }

                Button(action: onPreviewStories) {
                    Text(localizationManager.localized("wellness_wind_down_preview_stories"))
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.plain)
                .foregroundColor(.secondaryGold)
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .accessibilityIdentifier("wellness_wind_down_card")
    }

    private func persistBedtime() {
        WellnessSessionStore.setWindDownBedtime(hour: hour, minute: minute)
        Task { await WindDownScheduler.shared.reschedule() }
    }
}

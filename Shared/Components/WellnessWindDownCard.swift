import SwiftUI

/// fws-18 — wind-down toggle + bedtime picker (local pushes 30/15/5 min).
struct WellnessWindDownCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var onPreviewStories: () -> Void

    @State private var enabled = WellnessSessionStore.windDownEnabled
    @State private var hour = WellnessSessionStore.windDownBedtime.hour
    @State private var minute = WellnessSessionStore.windDownBedtime.minute
    @State private var notificationDenied = false
    @State private var confirmLine: String?

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
                Task { await applySchedule() }
            }

            Text(localizationManager.localized("wellness_wind_down_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))

            if notificationDenied {
                AladdinNotificationDeniedBanner(
                    message: localizationManager.localized("notification_denied_open_settings"),
                    buttonTitle: localizationManager.localized("notification_open_settings"),
                    onOpenSettings: { AladdinNotificationDeniedBanner.openSystemSettings() }
                )
            }

            if let confirmLine {
                Text(confirmLine)
                    .font(.caption)
                    .foregroundColor(Color(hex: "86EFAC"))
            }

            if enabled {
                HStack {
                    Text(localizationManager.localized("wellness_wind_down_bedtime"))
                        .font(.caption)
                        .foregroundColor(.white)
                    Spacer()
                    Picker("", selection: $hour) {
                        ForEach(18..<24, id: \.self) { h in
                            Text(String(format: "%02d", h)).tag(h)
                        }
                    }
                    .pickerStyle(.menu)
                    Text(":")
                        .foregroundColor(.white)
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

                Button {
                    Task { await sendTestPush() }
                } label: {
                    Text(localizationManager.localized("wellness_wind_down_test_push"))
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.plain)
                .foregroundColor(.white.opacity(0.85))
                .accessibilityIdentifier("wellness_wind_down_test_push")
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .accessibilityIdentifier("wellness_wind_down_card")
        .task { await refreshConfirm() }
    }

    private func persistBedtime() {
        WellnessSessionStore.setWindDownBedtime(hour: hour, minute: minute)
        Task { await applySchedule() }
    }

    private func applySchedule() async {
        if enabled {
            let granted = await WindDownScheduler.shared.requestAuthorizationIfNeeded()
            notificationDenied = !granted
        } else {
            notificationDenied = false
        }
        await WindDownScheduler.shared.reschedule()
        await refreshConfirm()
    }

    private func refreshConfirm() async {
        guard enabled, let next = WindDownScheduler.shared.nextVisibleFire() else {
            confirmLine = nil
            return
        }
        confirmLine = [
            localizationManager.localized("habit_local_enabled"),
            LocalDailyReminderMath.nextFireLine(date: next, localization: localizationManager)
        ].joined(separator: " · ")
    }

    private func sendTestPush() async {
        let granted = await WindDownScheduler.shared.requestAuthorizationIfNeeded()
        notificationDenied = !granted
        guard granted else { return }
        await WindDownScheduler.shared.fireTestNotification()
        confirmLine = localizationManager.localized("wellness_wind_down_test_push_sent")
        HapticFeedback.notification(.success)
    }
}

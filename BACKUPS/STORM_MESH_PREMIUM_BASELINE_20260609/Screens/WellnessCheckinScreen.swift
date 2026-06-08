import SwiftUI

/// p1-13 — check-in (локально; sync на сервер — p1-02).
struct WellnessCheckinScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var mood = "ok"
    @State private var sleepHours: Double = 7
    @State private var stressLevel: Double = 3
    @State private var saved = false
    @State private var offlineQueued = false

    private let moods: [(id: String, emoji: String, key: String)] = [
        ("great", "😊", "wellness_mood_great"),
        ("ok", "🙂", "wellness_mood_ok"),
        ("sad", "😢", "wellness_mood_sad"),
        ("anxious", "😰", "wellness_mood_anxious"),
        ("tired", "😴", "wellness_mood_tired"),
    ]

    private var ageBand: String {
        WellnessSessionStore.cachedAgeBand ?? CompanionUserContext.companionAgeBand
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                header

                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_checkin_title", ageBand: ageBand))
                    .font(.title3.bold())
                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_checkin_subtitle", ageBand: ageBand))
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                moodPicker

                VStack(alignment: .leading, spacing: 8) {
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_sleep_label", ageBand: ageBand))
                        .font(.subheadline.weight(.semibold))
                    Slider(value: $sleepHours, in: 3...12, step: 0.5)
                    Text(String(format: localizationManager.localized("wellness_sleep_hours"), sleepHours))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_stress_label", ageBand: ageBand))
                        .font(.subheadline.weight(.semibold))
                    Slider(value: $stressLevel, in: 1...5, step: 1)
                    HStack {
                        Text(localizationManager.localized("wellness_stress_low"))
                        Spacer()
                        Text(localizationManager.localized("wellness_stress_high"))
                    }
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                }

                Button {
                    saveCheckin()
                } label: {
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_checkin_save", ageBand: ageBand))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))

                if saved {
                    if offlineQueued {
                        Text(localizationManager.localized("wellness_checkin_offline_saved"))
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                    Button {
                        navigationManager.navigateToCompanionHome(returnTo: .wellnessCheckin)
                    } label: {
                        Text(WellnessAgeL10n.text(localizationManager, key: "wellness_checkin_talk_after", ageBand: ageBand))
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }
            }
            .padding()
        }
        .onAppear { loadDraft() }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
            }
            Text(localizationManager.localized("nav_screen_wellness_checkin"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private var moodPicker: some View {
        HStack(spacing: 8) {
            ForEach(moods, id: \.id) { item in
                Button {
                    mood = item.id
                } label: {
                    VStack(spacing: 4) {
                        Text(item.emoji).font(.title2)
                        Text(WellnessAgeL10n.text(localizationManager, key: item.key, ageBand: ageBand))
                            .font(.caption2)
                            .lineLimit(1)
                            .minimumScaleFactor(0.7)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(mood == item.id ? Color(hex: "8B5CF6").opacity(0.25) : Color.gray.opacity(0.12))
                    .cornerRadius(12)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func loadDraft() {
        if let draft = WellnessSessionStore.loadCheckin() {
            mood = draft.mood
            sleepHours = draft.sleepHours
            stressLevel = Double(draft.stressLevel)
            WellnessWidgetBridge.syncFromCheckin(moodId: mood, localizationManager: localizationManager)
        }
    }

    private func saveCheckin() {
        let draft = WellnessCheckinDraft(
            mood: mood,
            sleepHours: sleepHours,
            stressLevel: Int(stressLevel),
            savedAt: Date()
        )
        WellnessSessionStore.saveCheckin(draft)
        WellnessOfflineStore.saveCheckinDraft(draft)
        WellnessWidgetBridge.syncFromCheckin(moodId: mood, localizationManager: localizationManager)
        saved = true
        offlineQueued = false
        HapticFeedback.impact(.light)
        Task {
            do {
                try await WellnessAPIService.shared.postCheckin(
                    mood: mood,
                    sleepHours: sleepHours,
                    stressLevel: Int(stressLevel)
                )
                await applyCheckinLoopForCompanion()
            } catch {
                offlineQueued = true
            }
        }
    }

    /// r100-5-proactive — после check-in подсказка в чате с дорожкой от loop.
    private func applyCheckinLoopForCompanion() async {
        let outcome = await WellnessLoopCoordinator.runAndApply(
            message: "",
            requestedPillar: WellnessSessionStore.activePillar
        )
        guard case .proceed = outcome else { return }
        guard let pillarId = WellnessSessionStore.activePillar,
              let pillar = WellnessPillar(rawValue: pillarId) else { return }
        let name = localizationManager.localized(pillar.titleKey)
        let banner = String(
            format: localizationManager.localized("wellness_checkin_companion_banner"),
            name
        )
        WellnessSessionStore.setCompanionEntryBanner(banner)
    }
}

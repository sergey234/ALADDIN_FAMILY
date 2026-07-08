import SwiftUI

/// fws-16 — 7-day phone detox challenge linked to screen-time habits.
struct PhoneDetoxChallengeCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager

    @State private var challenge: WellnessDetoxChallengeDTO?
    @State private var weeklyKey: String?
    @State private var isLoading = true
    @State private var message: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(
                localizationManager.localized("wellness_detox_title"),
                systemImage: "iphone.slash"
            )
            .font(.subheadline.bold())

            Text(localizationManager.localized("wellness_detox_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))

            if isLoading {
                ProgressView().tint(.white)
            } else if let challenge {
                Text(
                    String(
                        format: localizationManager.localized("wellness_detox_progress"),
                        challenge.daysCompleted,
                        challenge.daysTotal
                    )
                )
                .font(.caption.monospacedDigit())

                if challenge.finished {
                    Text(localizationManager.localized("wellness_detox_finished"))
                        .font(.caption)
                        .foregroundColor(.green)
                } else if challenge.active {
                    Button {
                        Task { await markDay() }
                    } label: {
                        Text(localizationManager.localized("wellness_detox_mark_day"))
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "8B5CF6"))
                } else {
                    Button {
                        Task { await start() }
                    } label: {
                        Text(localizationManager.localized("wellness_detox_start"))
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "8B5CF6"))
                }

                Button {
                    navigationManager.navigateTo(.parentalControl)
                } label: {
                    Text(localizationManager.localized("wellness_detox_open_limits"))
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.plain)
                .foregroundColor(.secondaryGold)
            }

            if let weeklyKey {
                Text(localizationManager.localized(weeklyKey))
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.75))
            }
            if let message {
                Text(message).font(.caption).foregroundStyle(.orange)
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .accessibilityIdentifier("wellness_phone_detox_card")
        .task { await load() }
    }

    @MainActor
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let resp = try await WellnessAPIService.shared.fetchDetoxChallenge()
            challenge = resp.challenge
            weeklyKey = resp.weekly?.messageKey
        } catch {
            message = localizationManager.localized("wellness_detox_load_failed")
        }
    }

    @MainActor
    private func start() async {
        do {
            let resp = try await WellnessAPIService.shared.startDetoxChallenge()
            challenge = resp.challenge
            HapticFeedback.notification(.success)
        } catch {
            message = localizationManager.localized("wellness_detox_start_failed")
        }
    }

    @MainActor
    private func markDay() async {
        do {
            let resp = try await WellnessAPIService.shared.recordDetoxDay(underLimit: true)
            challenge = resp.challenge
            HapticFeedback.impact(.light)
        } catch {
            message = localizationManager.localized("wellness_detox_mark_failed")
        }
    }
}

import SwiftUI

/// fws-19 — 5 min behavioral «one thing» fullscreen ring session.
struct WellnessOneThingSessionScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var oneThing = ""
    @State private var secondsLeft = 5 * 60
    @State private var isRunning = false
    @State private var finished = false
    @State private var timer: Timer?
    @State private var heroId: String = "unicorn"

    private let totalSeconds = 5 * 60
    private var sessionEmotion: CompanionHeroEmotion {
        CompanionHeroRiveMapping.emotionForWellnessSession(pillar: "behavioral", sessionKind: "one_thing")
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)
            VStack(spacing: 20) {
                header
                CompanionHeroAvatarView(
                    characterId: heroId,
                    emotion: sessionEmotion,
                    lipSyncPhase: 0,
                    stageStyle: .hubThumbnail
                )
                .frame(width: 88, height: 88)
                .accessibilityIdentifier("wellness_one_thing_hero")
                if !finished {
                    Text(localizationManager.localized("wellness_one_thing_intro"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.85))
                        .multilineTextAlignment(.center)

                    WellnessMultilineField(
                        title: localizationManager.localized("wellness_one_thing_placeholder"),
                        text: $oneThing
                    )
                    .disabled(isRunning)

                    ZStack {
                        Circle()
                            .stroke(Color.white.opacity(0.15), lineWidth: 12)
                        Circle()
                            .trim(from: 0, to: progress)
                            .stroke(Color(hex: "8B5CF6"), style: StrokeStyle(lineWidth: 12, lineCap: .round))
                            .rotationEffect(.degrees(-90))
                        Text(timeLabel)
                            .font(.title.monospacedDigit().bold())
                    }
                    .frame(width: 160, height: 160)
                    .accessibilityIdentifier("wellness_one_thing_ring")

                    Button {
                        if isRunning { stopTimer() } else { startTimer() }
                    } label: {
                        Text(localizationManager.localized(isRunning ? "wellness_one_thing_pause" : "wellness_one_thing_start"))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "8B5CF6"))
                    .disabled(oneThing.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                } else {
                    Text(localizationManager.localized("wellness_one_thing_done"))
                        .font(.title3.bold())
                    Text(oneThing)
                        .font(.body)
                        .padding()
                        .stormGlassCard(cornerRadius: 12)
                    Button {
                        navigationManager.finishWellnessFlow()
                    } label: {
                        Text(localizationManager.localized("wellness_one_thing_close"))
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "8B5CF6"))
                }
                Spacer(minLength: 0)
            }
            .padding()
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .onDisappear { stopTimer() }
        .accessibilityIdentifier("wellness_one_thing_screen")
        .task {
            heroId = CompanionHeroRouter.resolve(
                entryPoint: .conversation,
                wellnessPillar: "behavioral"
            )
            _ = try? await WellnessAPIService.shared.setSessionPillar("behavioral")
        }
    }

    private var header: some View {
        HStack {
            Button {
                stopTimer()
                navigationManager.wellnessGoBack()
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.title3)
            }
            Spacer()
            Text(localizationManager.localized("wellness_one_thing_title"))
                .font(.headline.bold())
            Spacer()
            Color.clear.frame(width: 24, height: 24)
        }
    }

    private var progress: Double {
        1.0 - Double(secondsLeft) / Double(totalSeconds)
    }

    private var timeLabel: String {
        let m = secondsLeft / 60
        let s = secondsLeft % 60
        return String(format: "%d:%02d", m, s)
    }

    private func startTimer() {
        guard !oneThing.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        isRunning = true
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            if secondsLeft > 0 {
                secondsLeft -= 1
            } else {
                completeSession()
            }
        }
    }

    private func stopTimer() {
        timer?.invalidate()
        timer = nil
        isRunning = false
    }

    private func completeSession() {
        stopTimer()
        finished = true
        HapticFeedback.notification(.success)
        Task {
            try? await WellnessAPIService.shared.endWellnessSession()
        }
    }
}

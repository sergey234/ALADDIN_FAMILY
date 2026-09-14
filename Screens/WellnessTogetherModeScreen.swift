import SwiftUI

/// p2-44 — Together Mode: shared 3 min box breathing timer.
struct WellnessTogetherModeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var session: WellnessTogetherSession?
    @State private var secondsLeft = 180
    @State private var phase = "in"
    @State private var isRunning = false
    @State private var timer: Timer?
    @State private var statusNote: String?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)

            ScrollView(.vertical, showsIndicators: true) {
                VStack(alignment: .leading, spacing: 20) {
                    HStack {
                        Button { stopAndBack() } label: {
                            Image(systemName: "chevron.left")
                                .font(.body.weight(.semibold))
                                .foregroundColor(.white)
                        }
                        Text(localizationManager.localized("wellness_together_title"))
                            .font(.headline.bold())
                            .foregroundColor(.white)
                        Spacer()
                    }
                    if let session {
                        Text(introText(for: session))
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.85))
                        ForEach(session.steps, id: \.self) { step in
                            Text("• \(step)")
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.85))
                        }
                        if let statusNote {
                            Text(statusNote)
                                .font(.caption)
                                .foregroundColor(.orange)
                        }
                        ZStack {
                            Circle()
                                .stroke(Color.white.opacity(0.25), lineWidth: 12)
                            Text(timeString(secondsLeft))
                                .font(.system(size: 44, weight: .bold, design: .rounded))
                                .foregroundColor(.white)
                            Text(phase == "in"
                                 ? localizationManager.localized("wellness_together_breathe_in")
                                 : localizationManager.localized("wellness_together_breathe_out"))
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.85))
                                .offset(y: 56)
                        }
                        .frame(height: 200)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .stormGlassCard(cornerRadius: CornerRadius.medium)
                        Button {
                            if isRunning { pauseTimer() } else { startTimer() }
                        } label: {
                            Text(
                                localizationManager.localized(
                                    isRunning ? "wellness_together_pause" : "wellness_together_start"
                                )
                            )
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(Color(hex: "8B5CF6"))
                    } else {
                        ProgressView().tint(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 40)
                    }
                }
                .padding()
            }
        }
        .navigationBarHidden(true)
        .onDisappear { pauseTimer() }
        .task { await loadSession() }
    }

    private func introText(for session: WellnessTogetherSession) -> String {
        if let key = session.introKey, !key.isEmpty {
            let text = localizationManager.localized(key)
            if text != key { return text }
        }
        return session.intro
    }

    private func timeString(_ sec: Int) -> String {
        String(format: "%d:%02d", sec / 60, sec % 60)
    }

    private func loadSession() async {
        if let s = try? await WellnessAPIService.shared.fetchTogetherSession() {
            session = s
            secondsLeft = s.durationSec
            statusNote = nil
            return
        }
        let local = WellnessTogetherSession.localFallback(localization: localizationManager)
        session = local
        secondsLeft = local.durationSec
        statusNote = localizationManager.localized("wellness_together_offline_local")
    }

    private func startTimer() {
        guard let session else { return }
        isRunning = true
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            Task { @MainActor in
                guard secondsLeft > 0 else {
                    pauseTimer()
                    return
                }
                secondsLeft -= 1
                let elapsed = session.durationSec - secondsLeft
                let cycle = max(1, session.breathInSec + session.breathOutSec)
                let pos = elapsed % cycle
                phase = pos < session.breathInSec ? "in" : "out"
            }
        }
    }

    private func pauseTimer() {
        isRunning = false
        timer?.invalidate()
        timer = nil
    }

    private func stopAndBack() {
        pauseTimer()
        navigationManager.wellnessGoBack()
    }
}

extension WellnessTogetherSession {
    static func localFallback(localization: LocalizationManager) -> WellnessTogetherSession {
        WellnessTogetherSession(
            title: localization.localized("wellness_together_title"),
            intro: localization.localized("wellness_together_parent_intro"),
            durationSec: 180,
            breathInSec: 4,
            breathOutSec: 4,
            steps: [
                localization.localized("wellness_together_step_1"),
                localization.localized("wellness_together_step_2"),
                localization.localized("wellness_together_step_3"),
            ],
            titleKey: nil,
            introKey: "wellness_together_parent_intro"
        )
    }
}

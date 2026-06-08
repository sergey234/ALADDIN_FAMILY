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

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Button { stopAndBack() } label: {
                        Image(systemName: "chevron.left")
                    }
                    Text(localizationManager.localized("wellness_together_title"))
                        .font(.headline.bold())
                    Spacer()
                }
                if let session {
                    Text(introText(for: session))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    ForEach(session.steps, id: \.self) { step in
                        Text("• \(step)")
                            .font(.caption)
                    }
                    ZStack {
                        Circle()
                            .stroke(Color.purple.opacity(0.2), lineWidth: 12)
                        Text(timeString(secondsLeft))
                            .font(.system(size: 44, weight: .bold, design: .rounded))
                        Text(phase == "in"
                             ? localizationManager.localized("wellness_together_breathe_in")
                             : localizationManager.localized("wellness_together_breathe_out"))
                            .font(.caption)
                            .offset(y: 56)
                    }
                    .frame(height: 200)
                    .frame(maxWidth: .infinity)
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
                    .tint(.purple)
                } else {
                    ProgressView()
                }
            }
            .padding()
        }
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
        }
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
                let cycle = session.breathInSec + session.breathOutSec
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
        navigationManager.goBack()
    }
}

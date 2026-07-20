import Foundation
import SwiftUI

/// p2-10a — local 2-min breathing (no API pack required).
struct WellnessBreath2MinView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    var onComplete: () -> Void
    var onCancel: () -> Void

    @State private var secondsLeft = 120
    @State private var phaseInhale = true
    @State private var running = false
    @State private var completed = false
    @State private var tick: Timer?
    @State private var phaseTick: Timer?

    private let totalSeconds = 120

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(localizationManager.localized("wellness_breath_2min_title"))
                .font(.headline.bold())
            Text(localizationManager.localized("wellness_breath_2min_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
            Text(localizationManager.localized("wellness_breath_2min_disclaimer"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.55))

            ZStack {
                Circle()
                    .stroke(Color.white.opacity(0.2), lineWidth: 8)
                    .frame(width: 160, height: 160)
                Circle()
                    .trim(from: 0, to: progress)
                    .stroke(Color(hex: "8B5CF6"), style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                    .frame(width: 160, height: 160)
                VStack(spacing: 4) {
                    Text(phaseLabel)
                        .font(.subheadline.weight(.semibold))
                    Text(timeLabel)
                        .font(.title2.monospacedDigit())
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .accessibilityIdentifier("wellness_breath_2min_timer")

            BreathAmbientAudioControls()

            if completed {
                Text(localizationManager.localized("wellness_breath_2min_done"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.green.opacity(0.9))
                Button {
                    BreathAmbientAudioPlayer.shared.stop()
                    onComplete()
                } label: {
                    Text(localizationManager.localized("wellness_breath_2min_finish"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))
                .accessibilityIdentifier("wellness_breath_2min_finish")
            } else if running {
                Button {
                    stopTimers()
                    running = false
                    BreathAmbientAudioPlayer.shared.stop()
                } label: {
                    Text(localizationManager.localized("wellness_breath_2min_pause"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.bordered)
            } else {
                Button {
                    start()
                } label: {
                    Text(localizationManager.localized("wellness_breath_2min_start"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))
                .accessibilityIdentifier("wellness_breath_2min_start")
            }

            Button(action: {
                stopTimers()
                BreathAmbientAudioPlayer.shared.stop()
                onCancel()
            }) {
                Text(localizationManager.localized("wellness_guide_cancel"))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
        }
        .onDisappear {
            stopTimers()
            BreathAmbientAudioPlayer.shared.stop()
        }
    }

    private var progress: CGFloat {
        CGFloat(totalSeconds - secondsLeft) / CGFloat(totalSeconds)
    }

    private var timeLabel: String {
        let m = secondsLeft / 60
        let s = secondsLeft % 60
        return String(format: "%d:%02d", m, s)
    }

    private var phaseLabel: String {
        phaseInhale
            ? localizationManager.localized("wellness_together_breathe_in")
            : localizationManager.localized("wellness_together_breathe_out")
    }

    private func start() {
        if secondsLeft <= 0 { secondsLeft = totalSeconds }
        running = true
        completed = false
        BreathAmbientAudioPlayer.shared.startIfNeeded()
        tick?.invalidate()
        phaseTick?.invalidate()
        tick = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            Task { @MainActor in
                guard running else { return }
                if secondsLeft <= 1 {
                    secondsLeft = 0
                    running = false
                    completed = true
                    stopTimers()
                    BreathAmbientAudioPlayer.shared.stop()
                    HapticFeedback.notification(.success)
                } else {
                    secondsLeft -= 1
                }
            }
        }
        phaseTick = Timer.scheduledTimer(withTimeInterval: 4, repeats: true) { _ in
            Task { @MainActor in
                guard running else { return }
                phaseInhale.toggle()
            }
        }
    }

    private func stopTimers() {
        tick?.invalidate()
        tick = nil
        phaseTick?.invalidate()
        phaseTick = nil
    }
}

enum WellnessBreath2Min {
    static let exerciseId = "breath_2min"
}

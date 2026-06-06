import SwiftUI

/// 30-second focus WARMUP before ENCODE (B14-T05).
struct MnemoWarmupPhaseView: View {
    @ObservedObject var localizationManager: LocalizationManager
    let techniqueTitle: String
    let onComplete: () -> Void

    @State private var secondsRemaining: Int = MnemoLessonFlow.warmupDurationSeconds
    @State private var isRunning = true

    private let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_warmup_title"))
                .font(.system(size: 16, weight: .bold))

            Text(localizationManager.localized("child_mnemo_warmup_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            Text(
                String(
                    format: localizationManager.localized("child_mnemo_warmup_technique_format"),
                    techniqueTitle
                )
            )
            .font(.system(size: 14, weight: .semibold))
            .foregroundColor(.indigo)

            Text(localizationManager.localized("child_mnemo_warmup_focus_prompt"))
                .font(.system(size: 15))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.mint.opacity(0.12)))

            Text(
                String(
                    format: localizationManager.localized("child_mnemo_warmup_timer_format"),
                    secondsRemaining
                )
            )
            .font(.system(size: 28, weight: .bold, design: .rounded))
            .foregroundColor(.indigo)
            .frame(maxWidth: .infinity)
            .accessibilityIdentifier("child_mnemo_warmup_timer")

            if secondsRemaining == 0 {
                Button(localizationManager.localized("child_mnemo_warmup_start_encode")) {
                    onComplete()
                }
                .buttonStyle(.borderedProminent)
                .accessibilityIdentifier("child_mnemo_warmup_start_encode")
            } else {
                Button(localizationManager.localized("child_mnemo_warmup_skip")) {
                    isRunning = false
                    onComplete()
                }
                .buttonStyle(.bordered)
                .accessibilityIdentifier("child_mnemo_warmup_skip")
            }
        }
        .onReceive(timer) { _ in
            guard isRunning, secondsRemaining > 0 else { return }
            secondsRemaining -= 1
            if secondsRemaining == 0 {
                isRunning = false
            }
        }
        .accessibilityIdentifier("child_mnemo_warmup_phase")
    }
}

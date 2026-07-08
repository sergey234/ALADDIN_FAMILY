import SwiftUI

/// fws-05 — circular fake-risk meter for audio/video/call verdicts.
struct AntifakeConfidenceRingView: View {
    let percent: Int
    let accentColor: Color
    var lineWidth: CGFloat = 10

    private var clampedPercent: Int {
        min(max(percent, 0), 100)
    }

    private var progress: Double {
        Double(clampedPercent) / 100.0
    }

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.15), lineWidth: lineWidth)
            Circle()
                .trim(from: 0, to: progress)
                .stroke(
                    accentColor,
                    style: StrokeStyle(lineWidth: lineWidth, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
            VStack(spacing: 2) {
                Text("\(clampedPercent)%")
                    .font(.title2.weight(.bold))
                    .foregroundColor(.white)
                    .monospacedDigit()
            }
        }
        .frame(width: 88, height: 88)
        .accessibilityIdentifier("antifake_confidence_ring")
        .accessibilityLabel("\(clampedPercent) percent fake risk")
    }
}

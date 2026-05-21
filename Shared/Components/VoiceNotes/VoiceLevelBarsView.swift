import SwiftUI

/// Полоски уровня звука (AI / диктофон).
struct VoiceLevelBarsView: View {
    let level: Double
    var barCount: Int = 20
    var activeColor: Color = .red
    var inactiveColor: Color = Color.gray.opacity(0.25)

    private var safeLevel: Double {
        guard level.isFinite else { return 0 }
        return min(max(level, 0), 1)
    }

    var body: some View {
        HStack(spacing: 2) {
            ForEach(0..<max(barCount, 1), id: \.self) { index in
                let threshold = Double(index + 1) / Double(max(barCount, 1))
                RoundedRectangle(cornerRadius: 2)
                    .fill(safeLevel >= threshold ? activeColor : inactiveColor)
                    .frame(width: 3, height: barHeight(for: index))
            }
        }
        .frame(height: 28)
        .animation(.easeOut(duration: 0.08), value: safeLevel)
    }

    private func barHeight(for index: Int) -> CGFloat {
        let base = CGFloat(6 + (index % 5) * 2)
        let boost = CGFloat(safeLevel) * 12
        return max(4, min(base + boost, 28))
    }
}

/// Волна заметки: реальные амплитуды из m4a или декоративный fallback.
struct VoiceNoteWaveformView: View {
    let durationSec: Int
    var seed: Int = 0
    var samples: [CGFloat]?

    private var barHeights: [CGFloat] {
        if let samples, !samples.isEmpty { return samples }
        return (0..<24).map { decorativeHeight(index: $0) }
    }

    var body: some View {
        HStack(spacing: 2) {
            ForEach(Array(barHeights.enumerated()), id: \.offset) { _, height in
                RoundedRectangle(cornerRadius: 1)
                    .fill(Color.orange.opacity(samples == nil ? 0.45 : 0.75))
                    .frame(width: 2, height: max(4, min(height, 22)))
            }
        }
        .frame(height: 22)
    }

    private func decorativeHeight(index: Int) -> CGFloat {
        let raw = seed &+ index &+ max(durationSec, 0)
        let n = ((raw % 17) + 17) % 17
        return CGFloat(4 + n)
    }
}

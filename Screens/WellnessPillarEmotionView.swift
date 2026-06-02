import SwiftUI

/// p3-09 — pillar emotion chip (maps to Rive state names).
struct WellnessPillarEmotionView: View {
    let pillar: String

    private var riveState: String {
        switch pillar.lowercased() {
        case "cognitive": return "think"
        case "behavioral": return "step"
        case "jung": return "dream"
        default: return "presence"
        }
    }

    private var color: Color {
        switch pillar.lowercased() {
        case "cognitive": return Color(red: 0.49, green: 0.30, blue: 1.0)
        case "behavioral": return Color(red: 0.0, green: 0.75, blue: 0.65)
        case "jung": return Color(red: 0.36, green: 0.42, blue: 0.75)
        default: return Color(red: 1.0, green: 0.44, blue: 0.38)
        }
    }

    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(color.opacity(0.35))
                .frame(width: 28, height: 28)
            Text(riveState)
                .font(.caption.bold())
        }
    }
}

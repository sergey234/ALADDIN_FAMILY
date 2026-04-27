import SwiftUI

enum CharacterEmotion: Equatable {
    case neutral
    case happy
    case surprised
    case supportive

    var symbolName: String {
        switch self {
        case .neutral:
            return "sparkles"
        case .happy:
            return "face.smiling"
        case .surprised:
            return "bolt.heart"
        case .supportive:
            return "hand.raised.fill"
        }
    }

    var accent: Color {
        switch self {
        case .neutral:
            return .white
        case .happy:
            return .yellow
        case .surprised:
            return .cyan
        case .supportive:
            return .mint
        }
    }
}

enum CharacterActivityState: Equatable {
    case idle
    case active
}

struct CharacterAvatarView: View {
    let emotion: CharacterEmotion
    let activity: CharacterActivityState

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            Circle()
                .fill(
                    RadialGradient(
                        colors: [emotion.accent.opacity(0.55), Color.white.opacity(0.10)],
                        center: .topLeading,
                        startRadius: 6,
                        endRadius: 70
                    )
                )
                .overlay(
                    Circle()
                        .strokeBorder(Color.white.opacity(0.35), lineWidth: 1)
                )

            Image(systemName: emotion.symbolName)
                .font(.system(size: 30, weight: .semibold))
                .foregroundStyle(.white)
                .symbolRenderingMode(.hierarchical)
                .accessibilityHidden(true)
        }
        .frame(width: 86, height: 86)
        .scaleEffect(scale)
        .animation(reduceMotion ? nil : .spring(response: 0.35, dampingFraction: 0.72), value: emotion)
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.85).repeatForever(autoreverses: true), value: activity)
    }

    private var scale: CGFloat {
        if reduceMotion { return 1.0 }
        switch activity {
        case .idle:
            return 1.0
        case .active:
            return 1.04
        }
    }
}

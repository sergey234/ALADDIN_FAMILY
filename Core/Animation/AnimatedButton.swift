import SwiftUI

enum AnimatedButtonTone: Equatable {
    case playful
    case study
    case calm

    fileprivate var pulseColors: [Color] {
        switch self {
        case .playful:
            return [Color.pink.opacity(0.55), Color.purple.opacity(0.35)]
        case .study:
            return [Color.cyan.opacity(0.45), Color.blue.opacity(0.30)]
        case .calm:
            return [Color.white.opacity(0.35), Color.white.opacity(0.12)]
        }
    }
}

enum AnimatedButtonFlash: Equatable {
    case none
    case success
    case error
}

struct AnimatedButton<Label: View>: View {
    let tone: AnimatedButtonTone
    let isLoading: Bool
    let haptics: Bool
    let playsSound: Bool
    let isDisabled: Bool
    let action: () async -> AnimatedButtonFlash
    @ViewBuilder let label: () -> Label

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var isPressed = false
    @State private var pulse = false
    @State private var flash: AnimatedButtonFlash = .none
    @State private var isRunning = false

    init(
        tone: AnimatedButtonTone = .playful,
        isLoading: Bool = false,
        haptics: Bool = true,
        playsSound: Bool = true,
        isDisabled: Bool = false,
        action: @escaping () async -> AnimatedButtonFlash,
        @ViewBuilder label: @escaping () -> Label
    ) {
        self.tone = tone
        self.isLoading = isLoading
        self.haptics = haptics
        self.playsSound = playsSound
        self.isDisabled = isDisabled
        self.action = action
        self.label = label
    }

    var body: some View {
        Button(action: { Task { await runAction() } }) {
            ZStack {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: tone.pulseColors,
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .opacity((pulse && !reduceMotion) ? 0.35 : 0.0)
                    .blur(radius: 10)
                    .allowsHitTesting(false)

                label()
                    .opacity((isLoading || isRunning) ? 0.35 : 1.0)

                if isLoading || isRunning {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.white)
                }

                flashOverlay
            }
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .contentShape(Rectangle())
            .scaleEffect(isPressed ? 0.98 : (pulse && !reduceMotion ? 1.01 : 1.0))
            .animation(reduceMotion ? nil : .spring(response: 0.22, dampingFraction: 0.78), value: isPressed)
            .animation(reduceMotion ? nil : .easeInOut(duration: 0.9).repeatForever(autoreverses: true), value: pulse)
            .animation(reduceMotion ? nil : .easeInOut(duration: 0.18), value: flash)
        }
        .buttonStyle(.plain)
        .disabled(isDisabled || isLoading || isRunning)
        .accessibilityAddTraits(.isButton)
        .onAppear {
            guard !reduceMotion else { return }
            pulse = true
        }
        .onChange(of: reduceMotion) { newValue in
            pulse = !newValue
        }
    }

    @ViewBuilder
    private var flashOverlay: some View {
        switch flash {
        case .none:
            EmptyView()
        case .success:
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .strokeBorder(Color.green.opacity(0.95), lineWidth: 3)
        case .error:
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .strokeBorder(Color.red.opacity(0.95), lineWidth: 3)
        }
    }

    private func runAction() async {
        guard !isDisabled else { return }
        guard !isLoading else { return }
        guard !isRunning else { return }

        if haptics {
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        }
        if playsSound {
            SoundEffectPlayer.shared.play(.tapSoft, priority: .low)
        }

        if !reduceMotion {
            isPressed = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.08) {
                isPressed = false
            }
        }

        await MainActor.run { isRunning = true }
        let result = await action()
        await MainActor.run {
            isRunning = false
            flash = result
        }

        guard result != .none, !reduceMotion else {
            await MainActor.run { flash = .none }
            return
        }

        try? await Task.sleep(nanoseconds: 450_000_000)
        await MainActor.run { flash = .none }
    }
}

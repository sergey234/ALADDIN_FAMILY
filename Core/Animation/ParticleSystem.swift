import SwiftUI

// MARK: - Burst kinds (Phase 6 — визуальные эффекты)

enum CelebrationBurstKind: Equatable {
    /// Конфетти вниз от верхней кромки
    case confetti
    /// Звёзды при правильном ответе в квизе
    case correctAnswerStars
    /// «Магия» при достижении цели / ачивке
    case achievementMagic
    /// Короткий всплеск при покупке награды в магазине
    case rewardPurchase
}

private struct BurstParticleSeed: Identifiable {
    let id = UUID()
    let angleRadians: CGFloat
    let speed: CGFloat
    let size: CGFloat
    let spinPerSecond: CGFloat
    let color: Color
    let delay: CGFloat
}

/// Лёгкая система частиц: один `Canvas`, ограниченное число спрайтов, уважает Reduce Motion.
struct CelebrationParticleBurstView: View {
    let kind: CelebrationBurstKind
    let active: Bool
    var onFinished: (() -> Void)?

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var seeds: [BurstParticleSeed] = []
    @State private var elapsed: CGFloat = 0
    @State private var running = false

    private var duration: CGFloat {
        switch kind {
        case .confetti: return 1.55
        case .correctAnswerStars: return 1.1
        case .achievementMagic: return 1.85
        case .rewardPurchase: return 0.95
        }
    }

    private var particleCap: Int {
        PerformanceBudget.celebrationParticleCount(for: kind)
    }

    var body: some View {
        GeometryReader { geo in
            Canvas { context, size in
                guard running, !reduceMotion else { return }
                let center = CGPoint(x: size.width * 0.5, y: size.height * 0.35)
                let originConfetti = CGPoint(x: size.width * 0.5, y: -8)
                let magicCenter = CGPoint(x: size.width * 0.5, y: size.height * 0.42)

                for seed in seeds {
                    let localT = max(0, min(1, (elapsed - seed.delay) / max(0.25, duration - seed.delay)))
                    context.drawLayer { sub in
                        var layer = sub
                        switch kind {
                        case .confetti:
                            drawConfettiPiece(
                                context: &layer,
                                seed: seed,
                                t: localT,
                                origin: originConfetti,
                                width: size.width
                            )
                        case .correctAnswerStars:
                            drawStar(
                                context: &layer,
                                seed: seed,
                                t: localT,
                                center: center,
                                canvasSize: size
                            )
                        case .achievementMagic, .rewardPurchase:
                            drawMagicSpark(
                                context: &layer,
                                seed: seed,
                                t: localT,
                                center: magicCenter
                            )
                        }
                    }
                }
            }
            .onReceive(
                Timer.publish(
                    every: 1.0 / PerformanceBudget.celebrationParticleCanvasFPS,
                    on: .main,
                    in: .common
                ).autoconnect()
            ) { _ in
                guard running else { return }
                elapsed += 1.0 / CGFloat(PerformanceBudget.celebrationParticleCanvasFPS)
                if elapsed >= duration {
                    running = false
                    elapsed = 0
                    seeds = []
                    onFinished?()
                }
            }
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
        .onChange(of: active) { newValue in
            guard newValue else {
                running = false
                elapsed = 0
                seeds = []
                return
            }
            guard !reduceMotion else {
                onFinished?()
                return
            }
            seeds = Self.makeSeeds(kind: kind, cap: particleCap)
            elapsed = 0
            running = true
        }
        .onAppear {
            if active && !reduceMotion {
                seeds = Self.makeSeeds(kind: kind, cap: particleCap)
                elapsed = 0
                running = true
            }
        }
    }

    private func drawConfettiPiece(
        context: inout GraphicsContext,
        seed: BurstParticleSeed,
        t: CGFloat,
        origin: CGPoint,
        width: CGFloat
    ) {
        let gravity: CGFloat = 420
        let x = origin.x + cos(seed.angleRadians) * seed.speed * t * width * 0.45
        let y = origin.y + sin(seed.angleRadians) * seed.speed * t * 120 + 0.5 * gravity * t * t
        let alpha = max(0, 1 - t * 1.05)
        context.translateBy(x: x, y: y)
        context.rotate(by: .degrees(Double(seed.spinPerSecond * t * 360)))
        let rect = CGRect(x: -seed.size * 0.5, y: -seed.size * 0.25, width: seed.size, height: seed.size * 0.55)
        context.fill(Path(roundedRect: rect, cornerRadius: 2), with: .color(seed.color.opacity(Double(alpha))))
    }

    private func drawStar(
        context: inout GraphicsContext,
        seed: BurstParticleSeed,
        t: CGFloat,
        center: CGPoint,
        canvasSize: CGSize
    ) {
        let dist = seed.speed * t * min(canvasSize.width, canvasSize.height) * 0.22
        let x = center.x + cos(seed.angleRadians) * dist
        let y = center.y + sin(seed.angleRadians) * dist - CGFloat(t * t) * 40
        let alpha = max(0, 1 - t * 1.2)
        context.translateBy(x: x, y: y)
        context.rotate(by: .degrees(Double(seed.spinPerSecond * t * 180)))
        let r = seed.size * (1 - t * 0.35)
        let star = Path { p in
            let points = 5
            for i in 0..<(points * 2) {
                let angle = CGFloat(i) * .pi / CGFloat(points) - .pi / 2
                let rad = i.isMultiple(of: 2) ? r : r * 0.45
                let px = cos(angle) * rad
                let py = sin(angle) * rad
                if i == 0 { p.move(to: CGPoint(x: px, y: py)) } else { p.addLine(to: CGPoint(x: px, y: py)) }
            }
            p.closeSubpath()
        }
        context.fill(star, with: .color(seed.color.opacity(Double(alpha))))
    }

    private func drawMagicSpark(
        context: inout GraphicsContext,
        seed: BurstParticleSeed,
        t: CGFloat,
        center: CGPoint
    ) {
        let wobble = sin(t * .pi * 3 + seed.angleRadians) * 6
        let x = center.x + cos(seed.angleRadians) * seed.speed * t * 140 + wobble
        let y = center.y + sin(seed.angleRadians) * seed.speed * t * 140 - t * 30
        let alpha = max(0, 1 - t * 0.95)
        context.translateBy(x: x, y: y)
        let rect = CGRect(x: -seed.size * 0.5, y: -seed.size * 0.5, width: seed.size, height: seed.size)
        context.fill(Path(ellipseIn: rect), with: .color(seed.color.opacity(Double(alpha))))
    }

    private static func makeSeeds(kind: CelebrationBurstKind, cap: Int) -> [BurstParticleSeed] {
        var out: [BurstParticleSeed] = []
        out.reserveCapacity(cap)
        for i in 0..<cap {
            let hue = CGFloat(i) / CGFloat(max(1, cap - 1))
            let color: Color
            switch kind {
            case .confetti:
                color = Color(hue: Double(hue * 0.85 + 0.05), saturation: 0.75, brightness: 0.95)
            case .correctAnswerStars:
                color = i.isMultiple(of: 2) ? Color.yellow : Color.orange
            case .achievementMagic:
                color = Color(hue: 0.12 + Double(hue) * 0.08, saturation: 0.55, brightness: 0.98)
            case .rewardPurchase:
                color = i.isMultiple(of: 2)
                    ? Color(hue: 0.14, saturation: 0.7, brightness: 1.0)
                    : Color(hue: 0.08, saturation: 0.65, brightness: 0.98)
            }
            let angle: CGFloat
            let speed: CGFloat
            switch kind {
            case .confetti:
                angle = .pi * 0.15 + CGFloat(i) / CGFloat(cap) * .pi * 0.7
                speed = 0.35 + CGFloat.random(in: 0.05...0.25)
            case .correctAnswerStars:
                angle = CGFloat(i) / CGFloat(cap) * .pi * 2
                speed = 0.55 + CGFloat.random(in: 0...0.2)
            case .achievementMagic:
                angle = CGFloat(i) / CGFloat(cap) * .pi * 2 + CGFloat.random(in: -0.2...0.2)
                speed = 0.4 + CGFloat.random(in: 0...0.35)
            case .rewardPurchase:
                angle = CGFloat(i) / CGFloat(cap) * .pi * 2
                speed = 0.55 + CGFloat.random(in: 0...0.25)
            }
            let size: CGFloat
            switch kind {
            case .confetti:
                size = CGFloat.random(in: 6...11)
            case .correctAnswerStars:
                size = CGFloat.random(in: 10...16)
            case .achievementMagic:
                size = CGFloat.random(in: 5...12)
            case .rewardPurchase:
                size = CGFloat.random(in: 4...9)
            }
            let spin = CGFloat.random(in: -1.2...1.2)
            let delay = (kind == .confetti) ? CGFloat(i) * 0.012 : 0
            out.append(
                BurstParticleSeed(
                    angleRadians: angle,
                    speed: speed,
                    size: size,
                    spinPerSecond: spin,
                    color: color,
                    delay: delay
                )
            )
        }
        return out
    }
}

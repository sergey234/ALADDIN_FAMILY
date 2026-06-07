import SwiftUI

/// P1-08 / HERO-3-19 — процедурная сцена до production `.riv` (full-body rect или Hub-круг).
struct CompanionHeroAnimatedView: View {
    let characterId: String
    let emotion: CompanionHeroEmotion
    let lipSyncPhase: CGFloat
    var stageStyle: CompanionHeroLayout.StageStyle = .hubThumbnail
    var stageContentMode: CompanionHeroLayout.HeroStageContentMode = .fit
    var stageSize: CGSize = CGSize(
        width: CompanionHeroLayout.hubThumbnailDiameterPt,
        height: CompanionHeroLayout.hubThumbnailDiameterPt
    )

    @State private var pulse = false

    private var unit: CGFloat { CompanionHeroLayout.scaleUnit(for: stageSize.shortSide) }

    var body: some View {
        TimelineView(.animation(minimumInterval: 1 / 30)) { timeline in
            let t = timeline.date.timeIntervalSinceReferenceDate
            let lipActive = emotion == .speaking || lipSyncPhase > 0
            let mouthOpen = CompanionHeroLipSync.proceduralMouthOpen(isActive: lipActive, time: t)
            Group {
                switch stageStyle {
                case .hubThumbnail:
                    hubThumbnailStage(t: t, mouthOpen: mouthOpen)
                case .conversationFullBody:
                    fullBodyStage(t: t, mouthOpen: mouthOpen)
                }
            }
            .frame(width: stageSize.width, height: stageSize.height)
        }
        .onAppear { pulse = true }
        .onChange(of: emotion) { _ in pulse.toggle() }
    }

    @ViewBuilder
    private func hubThumbnailStage(t: TimeInterval, mouthOpen: CGFloat) -> some View {
        ZStack {
            Circle()
                .fill(CompanionHeroRiveMapping.backgroundGradient(for: emotion))
                .scaleEffect(pulseScale(t: t))
            characterFace(t: t, mouthOpen: mouthOpen, fullBody: false)
        }
    }

    @ViewBuilder
    private func fullBodyStage(t: TimeInterval, mouthOpen: CGFloat) -> some View {
        ZStack {
            RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
                .fill(
                    CompanionHeroRiveMapping.stageBackground(
                        characterId: characterId,
                        emotion: emotion
                    )
                )
                .overlay {
                    RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
                        .fill(CompanionHeroRiveMapping.backgroundGradient(for: emotion))
                        .opacity(0.35)
                }
                .scaleEffect(pulseScale(t: t))

            // «Пол» сцены — как у Grok stage lighting
            VStack {
                Spacer()
                Ellipse()
                    .fill(
                        RadialGradient(
                            colors: [.white.opacity(0.18), .clear],
                            center: .center,
                            startRadius: 4,
                            endRadius: stageSize.width * 0.45
                        )
                    )
                    .frame(width: stageSize.width * 0.9, height: stageSize.height * 0.12)
                    .offset(y: stageSize.height * 0.04)
            }

            characterFace(t: t, mouthOpen: mouthOpen, fullBody: true)
                .scaleEffect(
                    stageContentMode == .fillBottom
                        ? CompanionHeroLayout.stageFillScaleFactor(stageSize: stageSize)
                        : 1,
                    anchor: .bottom
                )
        }
        .clipShape(
            RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
        )
    }

    @ViewBuilder
    private func characterFace(t: TimeInterval, mouthOpen: CGFloat, fullBody: Bool) -> some View {
        let bobAmplitude: CGFloat = {
            if emotion.suppressesPlayfulVisuals { return 1.0 * unit }
            if emotion == .listening { return (fullBody ? 5 : 3) * unit }
            return 1.5 * unit
        }()
        let bobY = sin(t * (emotion == .thinking ? 1.2 : 2.4)) * bobAmplitude
        let emojiSize = fullBody ? stageSize.height * 0.48 : 44 * unit
        let mouthYOffset = fullBody ? stageSize.height * 0.06 : 14 * unit

        ZStack {
            Text(CompanionHeroRiveMapping.heroBaseEmoji(characterId: characterId))
                .font(.system(size: emojiSize))
                .offset(y: fullBody ? stageSize.height * 0.06 + bobY : bobY)
                .rotationEffect(.degrees(headTilt))
                .scaleEffect(faceScale)

            if !fullBody {
                proceduralMouth(mouthOpen: mouthOpen)
                    .offset(y: bobY + mouthYOffset)
            }

            emotionOverlay(t: t, fullBody: fullBody)
        }
    }

    @ViewBuilder
    private func proceduralMouth(mouthOpen: CGFloat) -> some View {
        if mouthOpen > 0.05 {
            Capsule()
                .fill(Color.primary.opacity(0.55))
                .frame(
                    width: (14 + mouthOpen * 10) * unit,
                    height: (4 + mouthOpen * 14) * unit
                )
        } else {
            Capsule()
                .fill(Color.primary.opacity(0.4))
                .frame(width: mouthLineWidth, height: mouthLineHeight)
        }
    }

    private var mouthLineWidth: CGFloat {
        let base: CGFloat
        if emotion.suppressesPlayfulVisuals { base = 10 }
        else {
            switch emotion {
            case .happy, .playful, .excited, .celebrate: base = 16
            case .sad: base = 10
            default: base = 12
            }
        }
        return base * unit
    }

    private var mouthLineHeight: CGFloat {
        let base: CGFloat
        if emotion.suppressesPlayfulVisuals { base = 2 }
        else {
            switch emotion {
            case .sad: base = 2
            case .happy, .playful, .excited, .celebrate: base = 3
            default: base = 2.5
            }
        }
        return base * unit
    }

    private var headTilt: Double {
        if emotion.suppressesPlayfulVisuals { return 4 }
        switch emotion {
        case .curious: return -6
        case .sad, .comfort: return 4
        case .playful, .excited: return -10
        default: return 0
        }
    }

    private var faceScale: CGFloat {
        if emotion.suppressesPlayfulVisuals { return 0.96 }
        switch emotion {
        case .excited, .celebrate: return 1.12
        case .alert: return 1.05
        case .sad: return 0.94
        default: return 1.0
        }
    }

    private func pulseScale(t: TimeInterval) -> CGFloat {
        let base: CGFloat = 1.0
        guard emotion == .listening || emotion == .thinking || emotion == .speaking else { return base }
        return base + CGFloat(sin(t * 3)) * 0.02
    }

    @ViewBuilder
    private func emotionOverlay(t: TimeInterval, fullBody: Bool) -> some View {
        switch emotion {
        case .listening:
            if fullBody {
                RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius - 4, style: .continuous)
                    .stroke(Color.purple.opacity(0.45), lineWidth: 3 * unit)
                    .scaleEffect(1 + CGFloat(sin(t * 4)) * 0.01)
            } else {
                Circle()
                    .stroke(Color.purple.opacity(0.5), lineWidth: 2 * unit)
                    .frame(width: 88 * unit, height: 88 * unit)
                    .scaleEffect(1 + CGFloat(sin(t * 4)) * 0.04)
            }
        case .thinking:
            Text("💭")
                .font(.system(size: (fullBody ? 28 : 12) * unit))
                .offset(
                    x: (fullBody ? stageSize.width * 0.28 : 36 * unit),
                    y: (fullBody ? -stageSize.height * 0.22 : -36 * unit)
                )
                .opacity(0.7 + sin(t * 2) * 0.2)
        case .alert:
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: (fullBody ? 28 : 18) * unit))
                .foregroundStyle(.orange)
                .offset(
                    x: (fullBody ? stageSize.width * 0.32 : 34 * unit),
                    y: (fullBody ? -stageSize.height * 0.28 : -34 * unit)
                )
        case .celebrate, .excited:
            if !emotion.suppressesPlayfulVisuals {
                Text("✨")
                    .font(.system(size: (fullBody ? 24 : 16) * unit))
                    .offset(
                        x: (fullBody ? -stageSize.width * 0.3 : -30 * unit),
                        y: (fullBody ? -stageSize.height * 0.26 : -34 * unit)
                    )
                    .rotationEffect(.degrees(sin(t * 5) * 20))
            }
        default:
            EmptyView()
        }
    }
}

private extension CGSize {
    var shortSide: CGFloat { min(width, height) }
}

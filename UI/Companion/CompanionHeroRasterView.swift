import SwiftUI

/// HERO-3-07 — production master PNG (360×480) до замены placeholder `.riv`.
/// Файлы: `Resources/Companion/{unicorn,aladdin,genie}_master.png`
struct CompanionHeroRasterView: View {
    let characterId: String
    let emotion: CompanionHeroEmotion
    let lipSyncPhase: CGFloat
    var stageStyle: CompanionHeroLayout.StageStyle = .hubThumbnail
    var stageSize: CGSize = CGSize(
        width: CompanionHeroLayout.hubThumbnailDiameterPt,
        height: CompanionHeroLayout.hubThumbnailDiameterPt
    )

    @State private var pulse = false

    private var unit: CGFloat { CompanionHeroLayout.scaleUnit(for: min(stageSize.width, stageSize.height)) }

    var body: some View {
        TimelineView(.animation(minimumInterval: 1 / 30)) { timeline in
            let t = timeline.date.timeIntervalSinceReferenceDate
            let lipActive = emotion == .speaking || lipSyncPhase > 0
            let mouthOpen = CompanionHeroLipSync.proceduralMouthOpen(isActive: lipActive, time: t)
            Group {
                switch stageStyle {
                case .hubThumbnail:
                    hubStage(t: t, mouthOpen: mouthOpen)
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
    private func hubStage(t: TimeInterval, mouthOpen: CGFloat) -> some View {
        ZStack {
            Circle()
                .fill(CompanionHeroRiveMapping.backgroundGradient(for: emotion))
            masterImage(t: t, mouthOpen: mouthOpen, hub: true)
        }
        .clipShape(Circle())
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
            masterImage(t: t, mouthOpen: mouthOpen, hub: false)
        }
        .clipShape(
            RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
        )
    }

    @ViewBuilder
    private func masterImage(t: TimeInterval, mouthOpen: CGFloat, hub: Bool) -> some View {
        let bobY = emotionBobOffset(t: t, hub: hub)
        let scale = emotionScale(t: t, hub: hub)
        if let uiImage = CompanionHeroRiveHost.bundledMasterUIImage(characterId: characterId) {
            Image(uiImage: uiImage)
                .resizable()
                .scaledToFit()
                .scaleEffect(scale)
                .offset(y: bobY)
                .overlay(alignment: .bottom) {
                    if mouthOpen > 0.05 {
                        mouthOverlay(mouthOpen: mouthOpen, hub: hub)
                    }
                }
                .accessibilityLabel(CompanionHeroRiveMapping.accessibilityLabel(emotion: emotion))
        } else {
            CompanionHeroAnimatedView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageSize: stageSize
            )
        }
    }

    @ViewBuilder
    private func mouthOverlay(mouthOpen: CGFloat, hub: Bool) -> some View {
        let w = (hub ? 28 : stageSize.width * 0.12) * unit
        let h = max(4, w * 0.35 * mouthOpen)
        Capsule()
            .fill(Color.black.opacity(0.35))
            .frame(width: w, height: h)
            .offset(y: hub ? -12 * unit : -stageSize.height * 0.14)
            .animation(.easeInOut(duration: 0.12), value: mouthOpen)
    }

    private func emotionBobOffset(t: TimeInterval, hub: Bool) -> CGFloat {
        if emotion.suppressesPlayfulVisuals { return 0 }
        let amp: CGFloat = {
            switch emotion {
            case .listening: return hub ? 3 * unit : 5 * unit
            case .thinking: return hub ? 2 * unit : 4 * unit
            case .playful, .excited, .celebrate: return hub ? 4 * unit : 8 * unit
            default: return hub ? 1.5 * unit : 3 * unit
            }
        }()
        let speed = emotion == .thinking ? 1.2 : 2.4
        return sin(t * speed) * amp
    }

    private func emotionScale(t: TimeInterval, hub: Bool) -> CGFloat {
        if emotion.suppressesPlayfulVisuals { return 1 }
        if emotion == .playful || emotion == .excited {
            return 1 + (hub ? 0.03 : 0.05) * sin(t * 3)
        }
        if pulse && (emotion == .happy || emotion == .celebrate) {
            return 1 + (hub ? 0.02 : 0.04)
        }
        return 1
    }
}

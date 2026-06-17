import SwiftUI
import UIKit

/// HERO-3-07 — production master PNG (360×480) до замены placeholder `.riv`.
/// Файлы: `Resources/Companion/{unicorn,aladdin,genie}_master.png`
struct CompanionHeroRasterView: View {
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
    @Environment(\.scenePhase) private var scenePhase
    @State private var isVisible = false
    @State private var didLogPath = false

    private var unit: CGFloat { CompanionHeroLayout.scaleUnit(for: min(stageSize.width, stageSize.height)) }

    var body: some View {
        TimelineView(.animation(minimumInterval: animationInterval)) { timeline in
            let t = timeline.date.timeIntervalSinceReferenceDate
            let lipActive = emotion == .speaking || lipSyncPhase > 0
            let mouthOpen = CompanionHeroLipSync.proceduralMouthOpen(isActive: lipActive, time: t)
            Group {
                if shouldAnimate {
                    switch stageStyle {
                    case .hubThumbnail:
                        hubStage(t: t, mouthOpen: mouthOpen)
                    case .conversationFullBody:
                        fullBodyStage(t: t, mouthOpen: mouthOpen)
                    }
                } else {
                    switch stageStyle {
                    case .hubThumbnail:
                        hubStage(t: 0, mouthOpen: 0)
                    case .conversationFullBody:
                        fullBodyStage(t: 0, mouthOpen: 0)
                    }
                }
            }
            .frame(width: stageSize.width, height: stageSize.height)
        }
        .onAppear {
            pulse = true
            isVisible = true
            if !didLogPath {
                didLogPath = true
                CompanionHeroRiveHost.logHeroPath(
                    characterId: characterId,
                    renderPath: "PNG",
                    vmStatus: "n/a"
                )
            }
        }
        .onDisappear { isVisible = false }
        .onChange(of: emotion) { _ in pulse.toggle() }
        .onChange(of: scenePhase) { phase in
            isVisible = (phase == .active)
        }
    }

    private var shouldAnimate: Bool {
        isVisible && scenePhase == .active
    }

    private var animationInterval: TimeInterval {
        stageStyle == .hubThumbnail ? (1 / 15) : (1 / 30)
    }

    @ViewBuilder
    private func hubStage(t: TimeInterval, mouthOpen: CGFloat) -> some View {
        ZStack(alignment: .topLeading) {
            Circle()
                .fill(CompanionHeroRiveMapping.backgroundGradient(for: emotion))
            masterImage(t: t, mouthOpen: mouthOpen, hub: true)
            debugPathBadge
        }
        .clipShape(Circle())
    }

    @ViewBuilder
    private func fullBodyStage(t: TimeInterval, mouthOpen: CGFloat) -> some View {
        ZStack(alignment: .topLeading) {
            RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
                .fill(
                    CompanionHeroRiveMapping.stageBackground(
                        characterId: characterId,
                        emotion: emotion
                    )
                )
            masterImage(t: t, mouthOpen: mouthOpen, hub: false)
            debugPathBadge
        }
        .clipShape(
            RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
        )
    }

    @ViewBuilder
    private var debugPathBadge: some View {
        #if DEBUG
        Text(CompanionHeroRiveHost.debugHeroPathLabel(characterId: characterId, usesRive: false))
            .font(.caption2.monospaced())
            .padding(4)
            .background(.black.opacity(0.55))
            .foregroundStyle(.orange)
            .clipShape(RoundedRectangle(cornerRadius: 4))
            .padding(6)
        #endif
    }

    @ViewBuilder
    private func masterImage(t: TimeInterval, mouthOpen: CGFloat, hub: Bool) -> some View {
        let bobY = emotionBobOffset(t: t, hub: hub)
        let scale = emotionScale(t: t, hub: hub)
        if let uiImage = CompanionHeroRiveHost.bundledMasterUIImage(characterId: characterId) {
            scaledMasterImage(uiImage: uiImage, hub: hub, bobY: bobY, scale: scale, mouthOpen: mouthOpen)
        } else {
            CompanionHeroAnimatedView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageContentMode: stageContentMode,
                stageSize: stageSize
            )
        }
    }

    @ViewBuilder
    private func scaledMasterImage(
        uiImage: UIImage,
        hub: Bool,
        bobY: CGFloat,
        scale: CGFloat,
        mouthOpen: CGFloat
    ) -> some View {
        let image = Image(uiImage: uiImage)
            .resizable()
        Group {
            switch stageContentMode {
            case .fit:
                image
                    .scaledToFit()
            case .fillBottom:
                image
                    .scaledToFill()
                    .frame(width: stageSize.width, height: stageSize.height, alignment: .bottom)
                    .clipped()
            }
        }
        .scaleEffect(scale)
        .offset(y: bobY)
        .overlay(alignment: .bottom) {
            if mouthOpen > 0.05 {
                mouthOverlay(mouthOpen: mouthOpen, hub: hub)
            }
        }
        .accessibilityLabel(CompanionHeroRiveMapping.accessibilityLabel(emotion: emotion))
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
            case .idle: return hub ? 4 * unit : 8 * unit
            case .listening: return hub ? 3 * unit : 5 * unit
            case .thinking: return hub ? 2 * unit : 4 * unit
            case .playful, .excited, .celebrate: return hub ? 4 * unit : 8 * unit
            default: return hub ? 2 * unit : 5 * unit
            }
        }()
        let speed = emotion == .thinking ? 1.2 : (emotion == .idle ? 1.5 : 2.4)
        return sin(t * speed) * amp
    }

    private func emotionScale(t: TimeInterval, hub: Bool) -> CGFloat {
        if emotion.suppressesPlayfulVisuals { return 1 }
        if emotion == .idle {
            return 1 + (hub ? 0.015 : 0.02) * sin(t * 1.5)
        }
        if emotion == .playful || emotion == .excited {
            return 1 + (hub ? 0.03 : 0.05) * sin(t * 3)
        }
        if pulse && (emotion == .happy || emotion == .celebrate) {
            return 1 + (hub ? 0.02 : 0.04)
        }
        return 1
    }
}

import SwiftUI

/// P1-08 / P1-23 — Hero avatar: Rive state map + rich fallback until `.riv` is bundled.
struct CompanionHeroAvatarView: View {
    let characterId: String
    let emotion: CompanionHeroEmotion
    let lipSyncPhase: CGFloat
    var equippedCosmeticId: String = ""
    var stageStyle: CompanionHeroLayout.StageStyle = .hubThumbnail
    var stageContentMode: CompanionHeroLayout.HeroStageContentMode = .fit
    var stageSize: CGSize = CGSize(
        width: CompanionHeroLayout.hubThumbnailDiameterPt,
        height: CompanionHeroLayout.hubThumbnailDiameterPt
    )

    private var unit: CGFloat { CompanionHeroLayout.scaleUnit(for: stageSize.shortSide) }

    var body: some View {
        ZStack {
            if !equippedCosmeticId.isEmpty {
                cosmeticFrame
            }
            heroCore
                .id(characterId)
            if let symbol = CompanionCosmeticVisuals.overlaySymbol(for: equippedCosmeticId) {
                Image(systemName: symbol)
                    .font(.system(size: 12 * unit, weight: .bold))
                    .foregroundStyle(.yellow)
                    .offset(
                        x: stageSize.width * 0.36,
                        y: -stageSize.height * 0.36
                    )
            }
        }
        .accessibilityLabel(CompanionHeroRiveMapping.accessibilityLabel(emotion: emotion))
        .accessibilityHint("Rive state: \(CompanionHeroRiveMapping.riveStateName(for: emotion))")
    }

    @ViewBuilder
    private var cosmeticFrame: some View {
        let gradient = LinearGradient(
            colors: CompanionCosmeticVisuals.ringColors(for: equippedCosmeticId),
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        switch stageStyle {
        case .hubThumbnail:
            Circle()
                .stroke(gradient, lineWidth: 3 * unit)
                .frame(width: 104 * unit, height: 104 * unit)
                .opacity(0.9)
        case .conversationFullBody:
            RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius + 2, style: .continuous)
                .stroke(gradient, lineWidth: 3 * unit)
                .frame(width: stageSize.width + 6, height: stageSize.height + 6)
                .opacity(0.9)
        }
    }

    @ViewBuilder
    private var heroCore: some View {
        if CompanionHeroRiveHost.shouldUseRasterMaster(characterId: characterId) {
            CompanionHeroRasterView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageContentMode: stageContentMode,
                stageSize: stageSize
            )
        } else if CompanionHeroRiveHost.shouldAttemptRiveRuntime(characterId: characterId) {
            #if canImport(RiveRuntime)
            CompanionHeroRiveRuntimeView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageContentMode: stageContentMode,
                stageSize: stageSize
            )
            #else
            CompanionHeroAnimatedView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageContentMode: stageContentMode,
                stageSize: stageSize
            )
            #endif
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
}

private extension CGSize {
    var shortSide: CGFloat { min(width, height) }
}

enum CompanionHeroRiveMapping {
    /// Имена state machine в Rive-файле (добавить `Resources/Companion/unicorn.riv`).
    static func riveStateName(for emotion: CompanionHeroEmotion) -> String {
        switch emotion {
        case .idle: return "idle"
        case .happy: return "happy"
        case .listening: return "listening"
        case .speaking: return "speaking"
        case .alert: return "alert"
        case .comfort: return "comfort"
        case .celebrate: return "celebrate"
        case .thinking: return "thinking"
        case .sad: return "sad"
        case .playful: return "playful"
        case .curious: return "curious"
        case .nostalgic: return "nostalgic"
        case .excited: return "excited"
        }
    }

    /// Базовый emoji героя (🧞 только у `genie`, человек у `aladdin`).
    static func heroBaseEmoji(characterId: String) -> String {
        switch characterId {
        case "unicorn": return "🦄"
        case "genie": return "🧞"
        case "aladdin": return "🧑‍🎓"
        default: return "🦄"
        }
    }

    static func displayEmoji(characterId: String, emotion: CompanionHeroEmotion) -> String {
        let base = heroBaseEmoji(characterId: characterId)
        switch emotion {
        case .playful: return "😄"
        case .sad: return "🥺"
        case .alert: return "⚠️"
        case .comfort: return "🤗"
        case .celebrate, .excited, .happy: return "🎉"
        case .curious: return "🤔"
        case .nostalgic: return "🌅"
        case .thinking, .listening: return base
        case .speaking: return "🗣️"
        case .idle: return base
        }
    }

    /// Full-body stage (OB_01 / OB_02 / OB_05) — прямоугольник, не круг.
    static func stageBackground(characterId: String, emotion: CompanionHeroEmotion) -> LinearGradient {
        let base: [Color]
        switch characterId {
        case "genie":
            base = [
                Color(red: 0.08, green: 0.38, blue: 0.48),
                Color(red: 0.04, green: 0.18, blue: 0.28)
            ]
        case "aladdin":
            base = [
                Color(red: 0.14, green: 0.26, blue: 0.42),
                Color(red: 0.22, green: 0.16, blue: 0.12)
            ]
        default:
            base = [
                Color(red: 0.32, green: 0.18, blue: 0.42),
                Color(red: 0.18, green: 0.12, blue: 0.32)
            ]
        }
        if emotion == .alert {
            return LinearGradient(
                colors: [base[0], Color.orange.opacity(0.35)],
                startPoint: .top,
                endPoint: .bottom
            )
        }
        return LinearGradient(colors: base, startPoint: .top, endPoint: .bottom)
    }

    static func backgroundGradient(for emotion: CompanionHeroEmotion) -> LinearGradient {
        let colors: [Color]
        switch emotion {
        case .alert:
            colors = [.orange.opacity(0.5), .red.opacity(0.35)]
        case .sad, .comfort:
            colors = [.blue.opacity(0.35), .purple.opacity(0.25)]
        case .playful, .excited, .celebrate, .happy:
            colors = [.yellow.opacity(0.45), .pink.opacity(0.35)]
        case .nostalgic:
            colors = [.orange.opacity(0.3), .purple.opacity(0.3)]
        case .curious:
            colors = [.mint.opacity(0.4), .cyan.opacity(0.3)]
        default:
            colors = [.purple.opacity(0.35), .blue.opacity(0.25)]
        }
        return LinearGradient(colors: colors, startPoint: .topLeading, endPoint: .bottomTrailing)
    }

    static func accessibilityLabel(emotion: CompanionHeroEmotion) -> String {
        switch emotion {
        case .listening: return "Герой слушает"
        case .speaking: return "Герой говорит"
        case .thinking: return "Герой думает"
        case .alert: return "Герой настороже"
        case .playful: return "Герой веселится"
        case .sad: return "Герой сочувствует"
        case .comfort: return "Герой поддерживает"
        case .nostalgic: return "Герой вспоминает с теплом"
        case .curious: return "Герой заинтересован"
        case .excited, .celebrate, .happy: return "Герой радуется"
        case .idle: return "Герой ждёт"
        }
    }
}

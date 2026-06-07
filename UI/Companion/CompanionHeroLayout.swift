import SwiftUI

/// Разметка Companion — Grok Companions: крупная **прямоугольная** сцена + узкий диалог снизу.
/// AIL (§6.2b): `standard` / `focused` / `immersive` — см. COMPANION_HERO_IMMERSIVE_IMPLEMENTATION_PLAN.md
enum CompanionHeroLayout {
    /// Режим **standard** (GROK §6.2) — доли от GeometryReader «Главное».
    static let heroZoneHeightFraction: CGFloat = 0.56
    static let chatZoneHeightFraction: CGFloat = 0.28

    static let heroStatusOverlayHeight: CGFloat = 48
    static let stageHorizontalPadding: CGFloat = 12
    static let stageCornerRadius: CGFloat = 20
    static let minFaceShortSidePt: CGFloat = 96
    static let hubThumbnailDiameterPt: CGFloat = 96
    static let riveArtboardSize = CGSize(width: 360, height: 480)

    /// Debounce выхода из immersive после окончания голоса (сек).
    static let immersiveVoiceIdleDebounceSec: TimeInterval = 2.0

    enum ConversationPresence: Equatable {
        case standard
        case focused
        case immersive
    }

    enum HeroStageContentMode: Equatable {
        case fit
        case fillBottom
    }

    struct PresenceLayout: Equatable {
        let heroZoneFraction: CGFloat
        let chatZoneFraction: CGFloat
        let contentMode: HeroStageContentMode
        let statusOverlayAtTop: Bool
        let stageBottomInset: CGFloat
    }

    enum StageStyle {
        case hubThumbnail
        case conversationFullBody
    }

    struct ConversationMetrics: Equatable {
        let presence: ConversationPresence
        let heroZoneHeight: CGFloat
        let chatZoneHeight: CGFloat
        let stageSize: CGSize
        let contentMode: HeroStageContentMode
        let statusOverlayAtTop: Bool
        let stageBottomInset: CGFloat

        var scaleReference: CGFloat {
            min(stageSize.width, stageSize.height)
        }
    }

    static func presenceLayout(_ presence: ConversationPresence) -> PresenceLayout {
        switch presence {
        case .standard:
            return PresenceLayout(
                heroZoneFraction: heroZoneHeightFraction,
                chatZoneFraction: chatZoneHeightFraction,
                contentMode: .fit,
                statusOverlayAtTop: false,
                stageBottomInset: heroStatusOverlayHeight
            )
        case .focused:
            return PresenceLayout(
                heroZoneFraction: 0.72,
                chatZoneFraction: 0.20,
                contentMode: .fit,
                statusOverlayAtTop: false,
                stageBottomInset: heroStatusOverlayHeight
            )
        case .immersive:
            return PresenceLayout(
                heroZoneFraction: 0.88,
                chatZoneFraction: 0.12,
                contentMode: .fillBottom,
                statusOverlayAtTop: true,
                stageBottomInset: 8
            )
        }
    }

    /// Масштаб от `fit` к `fillBottom` для artboard 360×480.
    static func stageFillScaleFactor(
        stageSize: CGSize,
        artboard: CGSize = riveArtboardSize
    ) -> CGFloat {
        guard artboard.width > 0, artboard.height > 0 else { return 1 }
        let fit = min(stageSize.width / artboard.width, stageSize.height / artboard.height)
        let fill = max(stageSize.width / artboard.width, stageSize.height / artboard.height)
        guard fit > 0 else { return 1 }
        return fill / fit
    }

    static func conversationMetrics(
        contentSize: CGSize,
        presence: ConversationPresence = .standard
    ) -> ConversationMetrics {
        let height = max(contentSize.height, 400)
        let width = max(contentSize.width, 320)
        let pl = presenceLayout(presence)
        let heroH = height * pl.heroZoneFraction
        let chatH = max(72, height * pl.chatZoneFraction)
        let stageW = width - stageHorizontalPadding * 2
        let stageH = max(
            minFaceShortSidePt,
            heroH - pl.stageBottomInset - 8
        )
        return ConversationMetrics(
            presence: presence,
            heroZoneHeight: heroH,
            chatZoneHeight: chatH,
            stageSize: CGSize(width: stageW, height: stageH),
            contentMode: pl.contentMode,
            statusOverlayAtTop: pl.statusOverlayAtTop,
            stageBottomInset: pl.stageBottomInset
        )
    }

    static func scaleUnit(for reference: CGFloat) -> CGFloat {
        max(reference / minFaceShortSidePt, 1)
    }

    /// Приоритет: immersive > focused > standard
    static func resolvePresence(
        messagesEmpty: Bool,
        isVoiceActive: Bool,
        userPinnedChrome: Bool,
        immersiveEnabled: Bool,
        pinMode: CompanionSettings.HeroPresencePinMode = .auto
    ) -> ConversationPresence {
        guard immersiveEnabled else { return .standard }
        if userPinnedChrome, !isVoiceActive {
            switch pinMode {
            case .alwaysStandard:
                return .standard
            case .alwaysFocused, .auto:
                return messagesEmpty ? .standard : .focused
            }
        }
        if isVoiceActive { return .immersive }
        switch pinMode {
        case .alwaysFocused:
            return .focused
        case .alwaysStandard:
            return .standard
        case .auto:
            if !messagesEmpty { return .focused }
            return .standard
        }
    }
}

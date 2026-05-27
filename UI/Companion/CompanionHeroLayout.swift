import SwiftUI

/// Разметка Companion — Grok Companions: крупная **прямоугольная** сцена + узкий диалог снизу.
enum CompanionHeroLayout {
    static let heroZoneHeightFraction: CGFloat = 0.56
    static let chatZoneHeightFraction: CGFloat = 0.28
    /// Высота статус-оверлея на сцене (эмоция + доверие).
    static let heroStatusOverlayHeight: CGFloat = 48
    static let stageHorizontalPadding: CGFloat = 12
    static let stageCornerRadius: CGFloat = 20
    /// MIMIC-Q1: минимальный размер «лица» (короткая сторона сцены).
    static let minFaceShortSidePt: CGFloat = 96
    static let hubThumbnailDiameterPt: CGFloat = 96
    /// Rive export: прямоугольный artboard full-body (pt @1x).
    static let riveArtboardSize = CGSize(width: 360, height: 480)

    enum StageStyle {
        /// Hub: круг 96×96.
        case hubThumbnail
        /// Conversation: прямоугольник на всю hero-зону (как Ani).
        case conversationFullBody
    }

    struct ConversationMetrics: Equatable {
        let heroZoneHeight: CGFloat
        let chatZoneHeight: CGFloat
        let stageSize: CGSize

        var scaleReference: CGFloat {
            min(stageSize.width, stageSize.height)
        }
    }

    static func conversationMetrics(contentSize: CGSize) -> ConversationMetrics {
        let height = max(contentSize.height, 400)
        let width = max(contentSize.width, 320)
        let heroH = height * heroZoneHeightFraction
        let chatH = max(88, height * chatZoneHeightFraction)
        let stageW = width - stageHorizontalPadding * 2
        let stageH = max(
            minFaceShortSidePt,
            heroH - heroStatusOverlayHeight - 8
        )
        return ConversationMetrics(
            heroZoneHeight: heroH,
            chatZoneHeight: chatH,
            stageSize: CGSize(width: stageW, height: stageH)
        )
    }

    static func scaleUnit(for reference: CGFloat) -> CGFloat {
        max(reference / minFaceShortSidePt, 1)
    }
}

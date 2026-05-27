import SwiftUI

/// Превью героя в Hub/истории: Rive или процедурный fallback (не только emoji).
struct CompanionHubHeroPreview: View {
    let characterId: String
    var diameter: CGFloat = CompanionHeroLayout.hubThumbnailDiameterPt

    var body: some View {
        CompanionHeroAvatarView(
            characterId: characterId,
            emotion: .idle,
            lipSyncPhase: 0,
            stageStyle: .hubThumbnail,
            stageSize: CGSize(width: diameter, height: diameter)
        )
        .accessibilityHidden(true)
    }
}

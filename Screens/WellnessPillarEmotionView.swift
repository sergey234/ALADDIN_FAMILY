import SwiftUI

/// r100-7-07 / HERO-3-07b — превью **выбранного** companion-героя на карточке дорожки (те же 3× `.riv`, hub ~48pt).
struct WellnessPillarEmotionView: View {
    let pillar: String

    @AppStorage("companion_selected_character_id") private var characterId: String = "unicorn"

    private var wellnessPillar: WellnessPillar? {
        WellnessPillar(rawValue: pillar.lowercased())
    }

    private var accentColor: Color {
        switch pillar.lowercased() {
        case "cognitive": return Color(red: 0.49, green: 0.30, blue: 1.0)
        case "behavioral": return Color(red: 0.0, green: 0.75, blue: 0.65)
        case "jung": return Color(red: 0.36, green: 0.42, blue: 0.75)
        default: return Color(red: 1.0, green: 0.44, blue: 0.38)
        }
    }

    var body: some View {
        Group {
            if let p = wellnessPillar {
                CompanionHeroAvatarView(
                    characterId: characterId,
                    emotion: p.companionHubPreviewEmotion,
                    lipSyncPhase: 0,
                    stageStyle: .hubThumbnail,
                    stageSize: CGSize(width: 48, height: 48)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(accentColor.opacity(0.55), lineWidth: 2)
                )
                .accessibilityIdentifier("wellness_pillar_rive_\(p.rawValue)")
            } else {
                fallbackChip
            }
        }
    }

    private var fallbackChip: some View {
        Circle()
            .fill(accentColor.opacity(0.35))
            .frame(width: 28, height: 28)
    }
}

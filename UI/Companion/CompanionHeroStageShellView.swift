import SwiftUI

/// Прямоугольная сцена без Rive и без emoji — только фон героя.
/// Используется на симуляторе iOS 15.x (Metal/Rive unstable) или пока view не готов к отрисовке.
struct CompanionHeroStageShellView: View {
    let characterId: String
    let emotion: CompanionHeroEmotion
    var stageStyle: CompanionHeroLayout.StageStyle = .conversationFullBody
    var stageSize: CGSize

    var body: some View {
        let fill = CompanionHeroRiveMapping.stageBackground(characterId: characterId, emotion: emotion)
        Group {
            switch stageStyle {
            case .hubThumbnail:
                Circle().fill(fill)
            case .conversationFullBody:
                RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
                    .fill(fill)
            }
        }
        .frame(width: stageSize.width, height: stageSize.height)
        .overlay(alignment: .bottom) {
            #if DEBUG
            if CompanionHeroRiveHost.isSimulatorIOS15MetalUnstable {
                Text("Rive: проверка на реальном устройстве")
                    .font(.caption2)
                    .foregroundStyle(.white.opacity(0.75))
                    .padding(8)
            }
            #endif
        }
        .accessibilityLabel("Сцена героя")
    }
}

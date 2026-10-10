import SwiftUI

/// Единый цвет акцента карточки тарифа (главная + профиль).
/// Канон: `docs/ALADDIN_SHYAM_COLOR_CANON.md`
enum TariffAccentPalette {
    static func color(for level: SubscriptionLevel) -> Color {
        switch level {
        case .free:
            return .shyamStorm
        case .trial:
            return .shyamPeacock
        case .personal:
            return .shyamSapphire
        case .family:
            // Владелец: золото только на семейном тарифе.
            return .shyamGold
        case .premium:
            return .shyamLotus
        }
    }
}

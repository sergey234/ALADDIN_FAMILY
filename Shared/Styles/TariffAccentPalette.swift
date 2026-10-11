import SwiftUI

/// Единый цвет акцента карточки тарифа (главная + профиль + экран тарифов).
/// Канон: `docs/ALADDIN_SHYAM_COLOR_CANON.md`
///
/// Важно: цвет на **главной** берётся из `SubscriptionManager.getCurrentLevel()`
/// (реальный JWT / trial), а не из «выбранной» плашки на экране тарифов.
/// Пока StoreKit/сервер не сменили уровень — карточка останется `free` = `shyamStorm`.
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

import SwiftUI
import UIKit

/// Preview / A/B for Clay G1 icons (канон 2026-11-11).
/// - `legacy` — Классика: SF / emoji
/// - `aliveBlue` — **Золото**: Glyph-first (без Blue disc; `*_Blue` не используем)
/// - `aliveBlack` — **Значки**: black-disc A/B
/// Storage: `UserDefaults` key `aladdin_icon_disc_style`.
enum AliveIconDiscStyle: String, CaseIterable, Identifiable {
    case legacy
    case aliveBlue
    case aliveBlack

    var id: String { rawValue }

    static let storageKey = "aladdin_icon_disc_style"

    /// DEBUG preview: Glyph (Золото). Release stays legacy until user picks in Settings.
    static var defaultStyle: AliveIconDiscStyle {
        #if DEBUG
        return .aliveBlue
        #else
        return .legacy
        #endif
    }

    static var current: AliveIconDiscStyle {
        let raw = UserDefaults.standard.string(forKey: storageKey) ?? defaultStyle.rawValue
        return AliveIconDiscStyle(rawValue: raw) ?? defaultStyle
    }

    /// Loc keys — RU/EN in Localizable.strings (P3: «Значки» → «Иконки»).
    var titleKey: String {
        switch self {
        case .legacy: return "settings_icon_style_classic"
        case .aliveBlue: return "settings_icon_style_gold"
        case .aliveBlack: return "settings_icon_style_icons"
        }
    }

    /// Fallback RU if strings missing (should not show raw keys).
    var titleRU: String {
        switch self {
        case .legacy: return "Классика"
        case .aliveBlue: return "Золото"
        case .aliveBlack: return "Иконки"
        }
    }
}

/// Wave1 G1 anchors — asset base without `_Black` / `_Glyph` (`_Blue` deprecated / не wire).
enum AliveIconID: String {
    case profile = "A01_Profile"
    case notif = "A02_Notif"
    case devices = "A03_Devices"
    case protect = "A04_Protect"
    case tariff = "A05_Tariff"
    case premium = "A06_Premium"
    case check = "A07_Check"
    case child = "A08_Child"
    case whereFamily = "A09_Where"
    case chipFamily = "A10_ChipFamily"
    case fabLocate = "A11_FabLocate"
    case kids = "A12_Kids"
    /// Main tab «Игра» — crop из unicorn_master (P1).
    case unicorn = "U01_Unicorn"
    /// Main плитка «Настройки» — gear Glyph/Black (P2 M04).
    case settings = "M04_Settings"
    /// Main плитка «Аналитика» — bars Glyph/Black (P2 M03).
    case analytics = "M03_Analytics"
    /// Main плитка «60+» — senior Glyph/Black (P2 M02).
    case senior60 = "M02_Senior60"
    /// Main плитка «Удобный режим» — house Glyph/Black (P2 M05).
    case simpleHome = "M05_SimpleHome"
    /// Удобный · строка AI Друзья (+ заранее под плитку Main).
    case aiFriends = "M01_AIFriends"
    /// Удобный · Меню.
    case menu = "D02_Menu"
    /// Удобный · Полная версия (Main).
    case fullApp = "D03_FullApp"
    /// Тарифы · Free.
    case tariffFree = "T01_Free"
    /// Тарифы · Personal.
    case tariffPersonal = "T02_Personal"
    /// Тарифы · Family.
    case tariffFamily = "T03_Family"
    /// Тарифы · Trial.
    case tariffTrial = "T04_Trial"
    /// Семья · участники / список.
    case famMembers = "F01_Members"
    /// Семья · чат.
    case famChat = "F02_Chat"
    /// Семья · группы.
    case famGroups = "F03_Groups"
    /// Семья · пригласить.
    case famInvite = "F04_Invite"
    /// Карта · вкладка Езда (L15).
    case mapDriving = "W01_Driving"
    /// Удобный · Ребёнок · дверь Пауза (Wave C C04).
    case childPause = "C04_Pause"
    /// Удобный · Ребёнок · дверь Сайты (Wave C C05).
    case childSites = "C05_Sites"
    /// Удобный · Ребёнок · дверь Лимит (Wave C C06).
    case childLimit = "C06_Limit"
    /// Удобный · Ребёнок · дверь Сон (Wave C C07).
    case childBedtime = "C07_Bedtime"
    /// Удобный · Ребёнок · дверь Награда (Wave C C08).
    case childReward = "C08_Reward"
    /// Удобный · Ребёнок · дверь Минуты (Wave C C09).
    case childMinutes = "C09_Minutes"
    /// Удобный · Ребёнок · дверь Экран ребёнка (Wave C C10).
    case childScreen = "C10_ChildScreen"
    /// Удобный · Ребёнок · «Кто виден на карте» (Wave C C01).
    case mapVis = "C01_MapVis"
    /// Удобный · Ребёнок · capsule «Только я» (Wave C C03). C02 → reuse `.famGroups`.
    case mapMe = "C03_MapMe"
    /// Семья · parental · блокировка контента (Wave C P01).
    case parentalContentBlock = "P01_ContentBlock"
    /// Семья · parental · время (Wave C P02).
    case parentalTime = "P02_Time"
    /// Семья · parental · мониторинг (Wave C P03).
    case parentalMonitor = "P03_Monitor"
    /// Семья · parental · гео (Wave C P04).
    case parentalGeo = "P04_Geo"
    /// Семья · parental · отчёты (Wave C P05).
    case parentalReports = "P05_Reports"
    /// Семья · parental · обход (Wave C P07). P06 → reuse `.settings`.
    case parentalBypass = "P07_Bypass"
    /// Antifake · tab Текст (Wave C AF01).
    case afText = "AF01_Text"
    /// Antifake · tab Документ (Wave C AF02).
    case afDoc = "AF02_Doc"
    /// Antifake · tab Голос (Wave C AF03).
    case afAudio = "AF03_Audio"
    /// Antifake · tab Видео (Wave C AF04).
    case afVideo = "AF04_Video"
    /// Antifake · tab Звонок (Wave C AF05).
    case afCall = "AF05_Call"
    /// Antifake · семейная база (Wave C AF08). AF07 → reuse `.aiFriends`.
    case afFamilyDB = "AF08_FamilyDB"

    func assetName(for style: AliveIconDiscStyle) -> String? {
        switch style {
        case .legacy:
            return nil
        case .aliveBlue:
            // Золото: только Glyph (Blue disc не в плане / не в app).
            return "ICON_G1_\(rawValue)_Glyph"
        case .aliveBlack:
            return "ICON_G1_\(rawValue)_Black"
        }
    }

    static func assetName(id: AliveIconID, style: AliveIconDiscStyle) -> String? {
        id.assetName(for: style)
    }
}

/// Renders G1 asset when style ≠ legacy and image exists; otherwise `legacy` content.
struct AliveGlyph<Legacy: View>: View {
    let id: AliveIconID
    let size: CGFloat
    @AppStorage(AliveIconDiscStyle.storageKey) private var styleRaw: String = AliveIconDiscStyle.defaultStyle.rawValue
    private let legacy: () -> Legacy

    init(id: AliveIconID, size: CGFloat, @ViewBuilder legacy: @escaping () -> Legacy) {
        self.id = id
        self.size = size
        self.legacy = legacy
    }

    var body: some View {
        let style = AliveIconDiscStyle(rawValue: styleRaw) ?? AliveIconDiscStyle.defaultStyle
        if style != .legacy,
           let name = id.assetName(for: style),
           UIImage(named: name) != nil {
            Image(name)
                .resizable()
                .scaledToFit()
                .frame(width: size, height: size)
                .accessibilityHidden(true)
        } else {
            legacy()
        }
    }
}

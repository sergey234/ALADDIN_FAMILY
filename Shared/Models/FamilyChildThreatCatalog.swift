import Foundation

/// B6-05 — chd-01…17 child threat matrix (SECURITY_UNIFIED_100_PERCENT_PLAN §4.3).
enum FamilyChildThreat: String, CaseIterable, Identifiable, Sendable {
    case chd01 = "chd-01"
    case chd02 = "chd-02"
    case chd03 = "chd-03"
    case chd04 = "chd-04"
    case chd05 = "chd-05"
    case chd06 = "chd-06"
    case chd07 = "chd-07"
    case chd08 = "chd-08"
    case chd09 = "chd-09"
    case chd10 = "chd-10"
    case chd11 = "chd-11"
    case chd12 = "chd-12"
    case chd13 = "chd-13"
    case chd14 = "chd-14"
    case chd15 = "chd-15"
    case chd16 = "chd-16"
    case chd17 = "chd-17"

    var id: String { rawValue }

    var catalogIndex: Int {
        switch self {
        case .chd01: return 1
        case .chd02: return 2
        case .chd03: return 3
        case .chd04: return 4
        case .chd05: return 5
        case .chd06: return 6
        case .chd07: return 7
        case .chd08: return 8
        case .chd09: return 9
        case .chd10: return 10
        case .chd11: return 11
        case .chd12: return 12
        case .chd13: return 13
        case .chd14: return 14
        case .chd15: return 15
        case .chd16: return 16
        case .chd17: return 17
        }
    }

    var titleKey: String { "tariffs_threat_child_\(catalogIndex)" }
    var pipelineKey: String { "family_hub_chd_\(String(format: "%02d", catalogIndex))_pipeline" }

    var route: FamilyChildThreatRoute {
        switch self {
        case .chd01, .chd07, .chd09:
            return .familyRoot
        case .chd02, .chd05, .chd08, .chd10, .chd11, .chd16, .chd17:
            return .parentalControl
        case .chd03:
            return .familyRoot
        case .chd04:
            return .familyRoot
        case .chd06:
            return .parentalControl
        case .chd12:
            return .networkProtection
        case .chd13:
            return .familyRoot
        case .chd14, .chd15:
            return .antifakeTab(.text, textMode: .text)
        }
    }

    var systemImage: String {
        switch self {
        case .chd01, .chd07, .chd10: return "eye.trianglebadge.exclamationmark"
        case .chd02, .chd16: return "bubble.left.and.exclamationmark"
        case .chd03: return "doc.richtext"
        case .chd04: return "location.circle.fill"
        case .chd05, .chd08, .chd17: return "gamecontroller.fill"
        case .chd06, .chd09: return "creditcard.fill"
        case .chd11: return "heart.slash.fill"
        case .chd12: return "megaphone.fill"
        case .chd13, .chd14: return "person.crop.circle.badge.exclamationmark"
        case .chd15: return "person.crop.circle.fill.badge.questionmark"
        }
    }
}

enum FamilyChildThreatRoute: Equatable, Sendable {
    case familyRoot
    case parentalControl
    case networkProtection
    case antifakeTab(AntifakeHubTab, textMode: AntifakeTextInputMode?)
}

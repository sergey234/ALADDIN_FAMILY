import Foundation

/// B4-05 — frd-01…12 fraud threat matrix (SECURITY_UNIFIED_100_PERCENT_PLAN §4.2).
enum IdentityFraudThreat: String, CaseIterable, Identifiable, Sendable {
    case frd01 = "frd-01"
    case frd02 = "frd-02"
    case frd03 = "frd-03"
    case frd04 = "frd-04"
    case frd05 = "frd-05"
    case frd06 = "frd-06"
    case frd07 = "frd-07"
    case frd08 = "frd-08"
    case frd09 = "frd-09"
    case frd10 = "frd-10"
    case frd11 = "frd-11"
    case frd12 = "frd-12"

    var id: String { rawValue }

    var catalogIndex: Int {
        switch self {
        case .frd01: return 1
        case .frd02: return 2
        case .frd03: return 3
        case .frd04: return 4
        case .frd05: return 5
        case .frd06: return 6
        case .frd07: return 7
        case .frd08: return 8
        case .frd09: return 9
        case .frd10: return 10
        case .frd11: return 11
        case .frd12: return 12
        }
    }

    var titleKey: String {
        "identity_hub_frd_\(String(format: "%02d", catalogIndex))_title"
    }

    var pipelineKey: String {
        "identity_hub_frd_\(String(format: "%02d", catalogIndex))_pipeline"
    }

    var route: IdentityFraudThreatRoute {
        switch self {
        case .frd01, .frd06:
            return .identityTab(.detect)
        case .frd02, .frd10, .frd11:
            return .antifakeTab(.text, textMode: .text)
        case .frd03, .frd07, .frd08:
            return .identityTab(.monitor)
        case .frd04:
            return .antifakeTab(.call, textMode: nil)
        case .frd05, .frd09:
            return .antifakeTab(.text, textMode: .url)
        case .frd12:
            return .antifakeTab(.text, textMode: .text)
        }
    }

    var systemImage: String {
        switch self {
        case .frd01, .frd06: return "person.text.rectangle"
        case .frd02, .frd10, .frd11, .frd12: return "text.quote"
        case .frd03, .frd07: return "creditcard.fill"
        case .frd04: return "phone.fill"
        case .frd05, .frd09: return "link"
        case .frd08: return "simcard.fill"
        }
    }
}

enum IdentityFraudThreatRoute: Equatable, Sendable {
    case identityTab(IdentityHubTab)
    case antifakeTab(AntifakeHubTab, textMode: AntifakeTextInputMode?)
}

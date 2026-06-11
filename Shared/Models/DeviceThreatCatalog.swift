import Foundation

/// B5-06…08 — cyb / mob / iot threat matrices (SECURITY_UNIFIED_100_PERCENT_PLAN §4.1, §4.7, §4.9).
enum DeviceCyberThreat: String, CaseIterable, Identifiable, Sendable {
    case cyb01 = "cyb-01"
    case cyb02 = "cyb-02"
    case cyb03 = "cyb-03"
    case cyb04 = "cyb-04"
    case cyb05 = "cyb-05"
    case cyb06 = "cyb-06"
    case cyb07 = "cyb-07"
    case cyb08 = "cyb-08"
    case cyb09 = "cyb-09"
    case cyb10 = "cyb-10"

    var id: String { rawValue }

    var catalogIndex: Int {
        switch self {
        case .cyb01: return 1
        case .cyb02: return 2
        case .cyb03: return 3
        case .cyb04: return 4
        case .cyb05: return 5
        case .cyb06: return 6
        case .cyb07: return 7
        case .cyb08: return 8
        case .cyb09: return 9
        case .cyb10: return 10
        }
    }

    var titleKey: String { "tariffs_threat_cyber_\(catalogIndex)" }
    var pipelineKey: String { "device_hub_cyb_\(String(format: "%02d", catalogIndex))_pipeline" }

    var route: DeviceThreatRoute {
        switch self {
        case .cyb08: return .deviceTab(.components)
        default: return .deviceTab(.cyber)
        }
    }

    var systemImage: String {
        switch self {
        case .cyb01, .cyb09: return "ladybug.fill"
        case .cyb02, .cyb08: return "network"
        case .cyb03: return "lock.fill"
        case .cyb04, .cyb07: return "eye.fill"
        case .cyb05: return "megaphone.fill"
        case .cyb06: return "wrench.and.screwdriver.fill"
        case .cyb10: return "memorychip"
        }
    }
}

enum DeviceMobileThreat: String, CaseIterable, Identifiable, Sendable {
    case mob01 = "mob-01"
    case mob02 = "mob-02"
    case mob03 = "mob-03"
    case mob04 = "mob-04"
    case mob05 = "mob-05"
    case mob06 = "mob-06"
    case mob07 = "mob-07"
    case mob08 = "mob-08"
    case mob09 = "mob-09"
    case mob10 = "mob-10"

    var id: String { rawValue }

    var catalogIndex: Int {
        switch self {
        case .mob01: return 1
        case .mob02: return 2
        case .mob03: return 3
        case .mob04: return 4
        case .mob05: return 5
        case .mob06: return 6
        case .mob07: return 7
        case .mob08: return 8
        case .mob09: return 9
        case .mob10: return 10
        }
    }

    var titleKey: String { "tariffs_threat_mobile_\(catalogIndex)" }
    var pipelineKey: String { "device_hub_mob_\(String(format: "%02d", catalogIndex))_pipeline" }

    var route: DeviceThreatRoute {
        switch self {
        case .mob04: return .antifakeTab(.text, textMode: .text)
        default: return .deviceTab(.mobile)
        }
    }

    var systemImage: String {
        switch self {
        case .mob01, .mob05: return "apps.iphone"
        case .mob02: return "arrow.down.app.fill"
        case .mob03: return "lock.shield.fill"
        case .mob04: return "message.fill"
        case .mob06: return "wifi.exclamationmark"
        case .mob07: return "person.crop.circle.badge.exclamationmark"
        case .mob08: return "location.fill"
        case .mob09: return "creditcard.fill"
        case .mob10: return "battery.100.bolt"
        }
    }
}

enum DeviceIoTThreat: String, CaseIterable, Identifiable, Sendable {
    case iot01 = "iot-01"
    case iot02 = "iot-02"
    case iot03 = "iot-03"
    case iot04 = "iot-04"
    case iot05 = "iot-05"
    case iot06 = "iot-06"
    case iot07 = "iot-07"
    case iot08 = "iot-08"
    case iot09 = "iot-09"
    case iot10 = "iot-10"

    var id: String { rawValue }

    var catalogIndex: Int {
        switch self {
        case .iot01: return 1
        case .iot02: return 2
        case .iot03: return 3
        case .iot04: return 4
        case .iot05: return 5
        case .iot06: return 6
        case .iot07: return 7
        case .iot08: return 8
        case .iot09: return 9
        case .iot10: return 10
        }
    }

    var titleKey: String { "tariffs_threat_iot_\(catalogIndex)" }
    var pipelineKey: String { "device_hub_iot_\(String(format: "%02d", catalogIndex))_pipeline" }

    var route: DeviceThreatRoute { .deviceTab(.iot) }

    var systemImage: String {
        switch self {
        case .iot01: return "house.fill"
        case .iot02: return "camera.fill"
        case .iot03: return "key.fill"
        case .iot04: return "speaker.wave.2.fill"
        case .iot05: return "lightbulb.fill"
        case .iot06: return "thermometer"
        case .iot07: return "lock.open.fill"
        case .iot08: return "antenna.radiowaves.left.and.right"
        case .iot09: return "wifi.router.fill"
        case .iot10: return "sensor.fill"
        }
    }
}

enum DeviceThreatRoute: Equatable, Sendable {
    case deviceTab(DeviceHubTab)
    case antifakeTab(AntifakeHubTab, textMode: AntifakeTextInputMode?)
}

enum DeviceComponentScanKind: String, CaseIterable, Identifiable, Sendable {
    case phishing
    case network
    case mobile
    case incident

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .phishing: return "device_hub_scan_phishing"
        case .network: return "device_hub_scan_network"
        case .mobile: return "device_hub_scan_mobile"
        case .incident: return "device_hub_scan_incident"
        }
    }

    var systemImage: String {
        switch self {
        case .phishing: return "link.badge.plus"
        case .network: return "wifi"
        case .mobile: return "iphone"
        case .incident: return "exclamationmark.triangle.fill"
        }
    }
}

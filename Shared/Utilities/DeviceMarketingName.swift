import Foundation
import UIKit

/// Local `utsname` → marketing name (no network). ProdQA S04/S17.
enum DeviceMarketingName {
    /// Prefer UserDefaults override, else map hw.machine, else generic "iPhone"/"iPad".
    static func displayName(overrideKey: String = "device_model_override_v1") -> String {
        let trimmed = UserDefaults.standard.string(forKey: overrideKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !trimmed.isEmpty { return trimmed }

        let code = machineCode()
        if let mapped = table[code] { return mapped }

        switch UIDevice.current.userInterfaceIdiom {
        case .pad: return "iPad"
        case .phone: return "iPhone"
        default: return UIDevice.current.model
        }
    }

    static func machineCode() -> String {
        var systemInfo = utsname()
        uname(&systemInfo)
        return withUnsafePointer(to: &systemInfo.machine) {
            $0.withMemoryRebound(to: CChar.self, capacity: 1) { ptr in
                String(validatingUTF8: ptr) ?? ""
            }
        }
    }

    /// Compact card line: «iPhone 16 · Ребёнок B»
    static func modelPlusRole(roleLabel: String) -> String {
        let model = displayName()
        let role = roleLabel.trimmingCharacters(in: .whitespacesAndNewlines)
        if role.isEmpty { return model }
        return "\(model) · \(role)"
    }

    // Keep table small; unknown codes fall back to idiom label.
    private static let table: [String: String] = [
        "iPhone14,2": "iPhone 13 Pro",
        "iPhone14,3": "iPhone 13 Pro Max",
        "iPhone14,4": "iPhone 13 mini",
        "iPhone14,5": "iPhone 13",
        "iPhone14,6": "iPhone SE (3rd)",
        "iPhone14,7": "iPhone 14",
        "iPhone14,8": "iPhone 14 Plus",
        "iPhone15,2": "iPhone 14 Pro",
        "iPhone15,3": "iPhone 14 Pro Max",
        "iPhone15,4": "iPhone 15",
        "iPhone15,5": "iPhone 15 Plus",
        "iPhone16,1": "iPhone 15 Pro",
        "iPhone16,2": "iPhone 15 Pro Max",
        "iPhone17,1": "iPhone 16 Pro",
        "iPhone17,2": "iPhone 16 Pro Max",
        "iPhone17,3": "iPhone 16",
        "iPhone17,4": "iPhone 16 Plus",
        "iPhone17,5": "iPhone 16e",
        "i386": "Simulator",
        "x86_64": "Simulator",
        "arm64": "Simulator"
    ]
}

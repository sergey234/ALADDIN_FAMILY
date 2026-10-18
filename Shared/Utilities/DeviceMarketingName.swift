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

    static var currentDeviceIdentifier: String? {
        UIDevice.current.identifierForVendor?.uuidString
    }

    static func genericDisplayName(for rawType: String) -> String {
        let normalized = rawType.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch normalized {
        case "iphone", "ios", "phone", "smartphone":
            return "iPhone"
        case "ipad", "tablet":
            return "iPad"
        case "mac", "macos":
            return "Mac"
        case "android":
            return "Android"
        default:
            return rawType.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "iPhone" : rawType
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

enum DeviceDisplayNameResolver {
    static func displayTitle(
        storedName: String,
        modelName: String?,
        deviceId: String,
        typeRaw: String
    ) -> String {
        if let explicitModel = cleaned(modelName), !explicitModel.isEmpty {
            return explicitModel
        }

        let stored = storedName.trimmingCharacters(in: .whitespacesAndNewlines)
        let genericType = DeviceMarketingName.genericDisplayName(for: typeRaw)

        if isCurrentDevice(deviceId), shouldPreferHardwareName(storedName: stored, genericType: genericType) {
            return DeviceMarketingName.displayName()
        }

        if shouldPreferHardwareName(storedName: stored, genericType: genericType) {
            return genericType
        }

        return stored.isEmpty ? genericType : stored
    }

    static func displayTitle(device: Device) -> String {
        displayTitle(
            storedName: device.name,
            modelName: device.modelName,
            deviceId: device.id,
            typeRaw: device.type.rawValue
        )
    }

    static func displayTitle(device: Device, detail: DeviceDetailResponse?) -> String {
        displayTitle(
            storedName: detail?.name ?? device.name,
            modelName: detail?.modelName ?? device.modelName,
            deviceId: detail?.id ?? device.id,
            typeRaw: detail?.type ?? device.type.rawValue
        )
    }

    private static func cleaned(_ value: String?) -> String? {
        value?.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private static func isCurrentDevice(_ deviceId: String) -> Bool {
        guard let current = DeviceMarketingName.currentDeviceIdentifier else { return false }
        return deviceId.caseInsensitiveCompare(current) == .orderedSame
    }

    private static func shouldPreferHardwareName(storedName: String, genericType: String) -> Bool {
        if storedName.isEmpty { return true }
        if storedName.caseInsensitiveCompare(genericType) == .orderedSame { return true }
        if storedName.contains("·") || storedName.contains("•") { return true }

        let lower = storedName.lowercased()
        return lower.contains("parent")
            || lower.contains("child")
            || lower.contains("teen")
            || lower.contains("elderly")
            || lower.contains("родител")
            || lower.contains("ребен")
            || lower.contains("ребён")
            || lower.contains("люд")
    }
}

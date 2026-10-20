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
        "iPhone12,1": "iPhone 11",
        "iPhone12,3": "iPhone 11 Pro",
        "iPhone12,5": "iPhone 11 Pro Max",
        "iPhone12,8": "iPhone SE (2nd)",
        "iPhone13,1": "iPhone 12 mini",
        "iPhone13,2": "iPhone 12",
        "iPhone13,3": "iPhone 12 Pro",
        "iPhone13,4": "iPhone 12 Pro Max",
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

/// Sends this handset's marketing name once. The server keeps a specific name if one is already stored.
enum HandsetModelReporter {
    static let handsetIdKey = "aladdin_handset_server_device_id"
    private static let lock = NSLock()
    private static var inFlight = Set<String>()

    struct Candidate {
        let id: String
        let owner: String
        let typeRaw: String
        let modelName: String?
    }

    static func reportFromList(_ devices: [Candidate]) {
        let hardware = DeviceMarketingName.displayName()
        guard isSpecific(hardware) else { return }
        guard let deviceId = resolveId(devices: devices) else { return }
        send(deviceId: deviceId, hardware: hardware)
    }

    static func reportKnownDevice(_ deviceId: String) {
        let hardware = DeviceMarketingName.displayName()
        guard isSpecific(hardware) else { return }
        let trimmed = deviceId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        send(deviceId: trimmed, hardware: hardware)
    }

    private static func send(deviceId: String, hardware: String) {
        let sentKey = "aladdin_handset_model_sent_v1_\(deviceId)"
        if UserDefaults.standard.string(forKey: sentKey) == hardware { return }
        lock.lock()
        if inFlight.contains(deviceId) {
            lock.unlock()
            return
        }
        inFlight.insert(deviceId)
        lock.unlock()
        Task { @MainActor in
            APIService.shared.reportHandsetModel(deviceId: deviceId, modelName: hardware) { result in
                lock.lock()
                inFlight.remove(deviceId)
                lock.unlock()
                if case .success(let response) = result, response.success {
                    UserDefaults.standard.set(hardware, forKey: sentKey)
                    UserDefaults.standard.set(deviceId, forKey: handsetIdKey)
                }
            }
        }
    }

    private static func resolveId(devices: [Candidate]) -> String? {
        let remembered = UserDefaults.standard.string(forKey: handsetIdKey) ?? ""
        if !remembered.isEmpty, devices.contains(where: { $0.id == remembered }) {
            return remembered
        }
        let me = (UserDefaults.standard.string(forKey: "current_user_name") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !me.isEmpty else { return nil }
        let idiom: String = UIDevice.current.userInterfaceIdiom == .pad ? "iPad" : "iPhone"
        let matches = devices.filter { device in
            device.owner.trimmingCharacters(in: .whitespacesAndNewlines).caseInsensitiveCompare(me) == .orderedSame
                && device.typeRaw.caseInsensitiveCompare(idiom) == .orderedSame
                && !isSpecific(device.modelName ?? "")
        }
        guard matches.count == 1, let only = matches.first else { return nil }
        return only.id
    }

    private static func isSpecific(_ raw: String) -> Bool {
        let cleaned = raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if cleaned.isEmpty { return false }
        return !["iphone", "ipad", "mac", "android", "phone", "smartphone", "tablet", "ios"].contains(cleaned)
    }
}

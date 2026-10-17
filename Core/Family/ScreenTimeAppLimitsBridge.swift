import Foundation
import FamilyControls
import DeviceActivity
import ManagedSettings
import CryptoKit

/// Bridges named App Limits (Instagram/TikTok…) ↔ opaque token hashes on the child device.
enum ScreenTimeAppLimitsBridge {
    /// SSOT keys live on `ScreenTimeUsageStore` (shared with extensions that must not import this type).
    static var recordsKey: String { ScreenTimeUsageStore.appLimitsRecordsKey }
    static var mapKey: String { ScreenTimeUsageStore.appTokenMapKey }

    struct Record: Codable, Equatable, Identifiable {
        var id: String { (tokenHash?.isEmpty == false ? tokenHash! : displayName).lowercased() }
        var displayName: String
        var limitMinutes: Int
        var tokenHash: String?
    }

    private static var defaults: UserDefaults {
        UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
    }

    static func loadRecords() -> [Record] {
        if let data = defaults.data(forKey: recordsKey),
           let decoded = try? JSONDecoder().decode([Record].self, from: data),
           !decoded.isEmpty {
            return decoded
        }
        // Seed from legacy name-only UI defaults.
        let legacyNames = ScreenTimeUsageStore.trackedAppNames
        return legacyNames.map { name in
            let key = "app_\(name.lowercased().replacingOccurrences(of: " ", with: "_"))_time_limit"
            let minutes: Int = {
                if UserDefaults.standard.object(forKey: key) != nil {
                    return max(5, Int(UserDefaults.standard.double(forKey: key)))
                }
                switch name {
                case "Instagram", "VK", "Odnoklassniki": return 30
                case "TikTok": return 20
                case "YouTube": return 45
                case "WhatsApp", "Telegram", "Games": return 60
                case "Discord": return 30
                default: return 60
                }
            }()
            return Record(displayName: name, limitMinutes: minutes, tokenHash: tokenHash(forDisplayName: name))
        }
    }

    static func saveRecords(_ records: [Record]) {
        if let data = try? JSONEncoder().encode(records) {
            defaults.set(data, forKey: recordsKey)
            UserDefaults.standard.set(data, forKey: recordsKey)
            #if DEBUG
            let summary = records.map { "\($0.displayName)=\($0.limitMinutes)" }.joined(separator: ", ")
            print("🎚️ SCREEN_TIME AppLimitsBridge.saveRecords: \(summary)")
            #endif
        }
        var map = loadTokenMap()
        for r in records {
            if let h = r.tokenHash, !h.isEmpty {
                map[r.displayName.lowercased()] = h
            }
            let appKey = "app_\(r.displayName.lowercased().replacingOccurrences(of: " ", with: "_"))_time_limit"
            UserDefaults.standard.set(Double(r.limitMinutes), forKey: appKey)
        }
        saveTokenMap(map)
        for r in records {
            let udKey = "parental_\(r.displayName.lowercased().replacingOccurrences(of: " ", with: "_"))_limit"
            UserDefaults.standard.set("\(r.limitMinutes) min", forKey: udKey)
        }
        applyLimitSecondsToUsageStore(records)
    }

    static func tokenHash(forDisplayName name: String) -> String? {
        loadTokenMap()[name.lowercased()]
    }

    static func loadTokenMap() -> [String: String] {
        (defaults.dictionary(forKey: mapKey) as? [String: String]) ?? [:]
    }

    static func saveTokenMap(_ map: [String: String]) {
        defaults.set(map, forKey: mapKey)
        UserDefaults.standard.set(map, forKey: mapKey)
    }

    /// Stable hash for an ApplicationToken (no raw token leaves the device).
    static func hashApplicationToken(_ token: ApplicationToken) -> String {
        if let data = try? JSONEncoder().encode(token) {
            let digest = SHA256.hash(data: data)
            return digest.map { String(format: "%02x", $0) }.joined()
        }
        return String(token.hashValue)
    }

    /// After FamilyActivityPicker on child: bind selection tokens into map + records.
    static func bindSelection(_ selection: FamilyActivitySelection) {
        var map = loadTokenMap()
        var records = loadRecords()
        let tokens = Array(selection.applicationTokens)
        for (idx, token) in tokens.enumerated() {
            let hash = hashApplicationToken(token)
            // Prefer existing named slots; otherwise create App N.
            if idx < records.count {
                records[idx].tokenHash = hash
                map[records[idx].displayName.lowercased()] = hash
            } else {
                let name = "App \(idx + 1)"
                records.append(Record(displayName: name, limitMinutes: 60, tokenHash: hash))
                map[name.lowercased()] = hash
            }
        }
        saveTokenMap(map)
        saveRecords(records)

        // Apply shields from selection — only when Family Controls is allowed in this binary.
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else {
            #if DEBUG
            print("🎚️ SCREEN_TIME bindSelection: FC gated — skip ManagedSettings apply")
            #endif
            return
        }
        let store = ManagedSettingsStore()
        store.shield.applications = selection.applicationTokens.isEmpty ? nil : selection.applicationTokens
        store.shield.applicationCategories = selection.categoryTokens.isEmpty
            ? nil
            : .specific(selection.categoryTokens)
    }

    /// Write limitSeconds into today's usage snapshot apps (by tokenHash or displayName).
    static func applyLimitSecondsToUsageStore(_ records: [Record]? = nil) {
        let list = records ?? loadRecords()
        guard var snap = ScreenTimeUsageStore.load() else {
            // Still seed empty day so parent UI can show limits later.
            let familyId = FamilyLocalStore.loadPersistedFamilyId()
            let memberId = UserDefaults.standard.string(forKey: "your_member_id")
                ?? UserDefaults.standard.string(forKey: "active_child_profile_server_id")
                ?? ""
            let apps = list.map {
                ScreenTimeUsageStore.AppMinute(
                    tokenHash: $0.tokenHash ?? $0.displayName.lowercased(),
                    displayName: $0.displayName,
                    seconds: 0,
                    limitSeconds: $0.limitMinutes * 60
                )
            }
            _ = ScreenTimeUsageStore.upsertToday(
                familyId: familyId,
                memberId: memberId,
                totalSeconds: 0,
                apps: apps
            )
            return
        }
        var apps = snap.apps
        for rec in list {
            let limitSec = rec.limitMinutes * 60
            if let hash = rec.tokenHash,
               let idx = apps.firstIndex(where: { $0.tokenHash == hash }) {
                apps[idx].limitSeconds = limitSec
                if apps[idx].displayName == nil { apps[idx].displayName = rec.displayName }
            } else if let idx = apps.firstIndex(where: {
                ($0.displayName ?? "").lowercased() == rec.displayName.lowercased()
            }) {
                apps[idx].limitSeconds = limitSec
                if apps[idx].tokenHash.isEmpty, let h = rec.tokenHash { apps[idx].tokenHash = h }
            } else {
                apps.append(
                    ScreenTimeUsageStore.AppMinute(
                        tokenHash: rec.tokenHash ?? rec.displayName.lowercased(),
                        displayName: rec.displayName,
                        seconds: 0,
                        limitSeconds: limitSec
                    )
                )
            }
        }
        snap.apps = apps
        snap.updatedAt = Date()
        _ = ScreenTimeUsageStore.save(snap)
    }

    /// DeviceActivity threshold events for child Monitor schedule.
    static func thresholdEvents() -> [DeviceActivityEvent.Name: DeviceActivityEvent] {
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else { return [:] }
        var events: [DeviceActivityEvent.Name: DeviceActivityEvent] = [:]
        // Selection applications (if any) + minute thresholds from records.
        let defaults = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
        var applications = Set<ApplicationToken>()
        if let data = defaults.data(forKey: ScreenTimeUsageStore.selectionKey),
           let selection = try? PropertyListDecoder().decode(FamilyActivitySelection.self, from: data) {
            applications = selection.applicationTokens
        }
        guard !applications.isEmpty else { return [:] }
        // One shared threshold event at the minimum limit among selected apps (Monitor wakes + refresh).
        let minMinutes = loadRecords().map(\.limitMinutes).filter { $0 > 0 }.min() ?? 30
        let name = DeviceActivityEvent.Name("aladdin.limit.selected")
        events[name] = DeviceActivityEvent(
            applications: applications,
            threshold: DateComponents(minute: max(5, minMinutes))
        )
        return events
    }
}

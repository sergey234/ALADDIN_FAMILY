import Foundation
import DeviceActivity
import ManagedSettings
import FamilyControls

/// F4 — ночной замок: отдельное DeviceActivity-расписание (не путать с дневным мониторингом минут).
/// Щиты пишутся в **именованный** ManagedSettingsStore (iOS 16+), чтобы дневной мониторинг их не стирал.
/// На iOS 15 — дефолтный store (именованный API недоступен).
enum BedtimeNightLock {
    static let activityName = DeviceActivityName("aladdin.family.bedtime")
    /// Raw name shared with DeviceActivityMonitor extension (`aladdin.bedtime`).
    static let storeNameRaw = "aladdin.bedtime"

    private static let enabledKey = "aladdin.bedtime.lock.enabled"
    private static let startHourKey = "aladdin.bedtime.start.hour"
    private static let startMinuteKey = "aladdin.bedtime.start.minute"
    private static let endHourKey = "aladdin.bedtime.end.hour"
    private static let endMinuteKey = "aladdin.bedtime.end.minute"

    private static var center: DeviceActivityCenter { DeviceActivityCenter() }

    private static var store: ManagedSettingsStore {
        if #available(iOS 16.0, *) {
            return ManagedSettingsStore(named: ManagedSettingsStore.Name(storeNameRaw))
        }
        return ManagedSettingsStore()
    }

    private static var defaults: UserDefaults {
        UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
    }

    static var isEnabled: Bool {
        get { defaults.bool(forKey: enabledKey) }
        set { defaults.set(newValue, forKey: enabledKey) }
    }

    /// Сохранить окно сна и поставить расписание (на телефоне ребёнка с Family Controls).
    static func saveAndSchedule(start: Date, end: Date, enabled: Bool = true) {
        let cal = Calendar.current
        let s = cal.dateComponents([.hour, .minute], from: start)
        let e = cal.dateComponents([.hour, .minute], from: end)
        let sh = s.hour ?? 22
        let sm = s.minute ?? 0
        let eh = e.hour ?? 7
        let em = e.minute ?? 0

        defaults.set(sh, forKey: startHourKey)
        defaults.set(sm, forKey: startMinuteKey)
        defaults.set(eh, forKey: endHourKey)
        defaults.set(em, forKey: endMinuteKey)
        isEnabled = enabled

        let fmt = DateFormatter()
        fmt.dateFormat = "HH:mm"
        UserDefaults.standard.set(fmt.string(from: start), forKey: "parental_bedtime_start")
        UserDefaults.standard.set(fmt.string(from: end), forKey: "parental_bedtime_end")
        UserDefaults.standard.set("\(fmt.string(from: start))-\(fmt.string(from: end))", forKey: "parental_bedtime")

        guard AppStoreBuildPolicy.allowsSystemFamilyControls else {
            print("ℹ️ BedtimeNightLock: Family Controls gated — times saved, schedule skipped")
            return
        }

        if enabled {
            do {
                try startMonitoring(startHour: sh, startMinute: sm, endHour: eh, endMinute: em)
                if isCurrentlyInBedtimeWindow(now: Date()) {
                    applyBedtimeShields()
                }
            } catch {
                print("⚠️ BedtimeNightLock schedule failed: \(error.localizedDescription)")
            }
        } else {
            stopMonitoring()
            clearBedtimeShields()
        }
    }

    /// Повторный старт после pipeline Family Controls на устройстве ребёнка.
    static func rescheduleFromSavedIfNeeded() {
        guard isEnabled else { return }
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else { return }
        let sh = defaults.object(forKey: startHourKey) as? Int ?? 22
        let sm = defaults.object(forKey: startMinuteKey) as? Int ?? 0
        let eh = defaults.object(forKey: endHourKey) as? Int ?? 7
        let em = defaults.object(forKey: endMinuteKey) as? Int ?? 0
        do {
            try startMonitoring(startHour: sh, startMinute: sm, endHour: eh, endMinute: em)
            if isCurrentlyInBedtimeWindow(now: Date()) {
                applyBedtimeShields()
            }
        } catch {
            print("⚠️ BedtimeNightLock reschedule failed: \(error.localizedDescription)")
        }
    }

    static func applyBedtimeShields() {
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else { return }
        // Категории приложений целиком — телефон «закрыт» на ночь (Phone/SOS Apple не режет так же).
        store.shield.applicationCategories = .all()
        defaults.set(Date().timeIntervalSince1970, forKey: "aladdin.bedtime.shield_on_at")
        print("🌙 BedtimeNightLock: shields ON")
    }

    static func clearBedtimeShields() {
        store.shield.applicationCategories = nil
        store.shield.applications = nil
        store.shield.webDomains = nil
        defaults.set(Date().timeIntervalSince1970, forKey: "aladdin.bedtime.shield_off_at")
        print("🌅 BedtimeNightLock: shields OFF")
    }

    static func isBedtimeActivity(_ name: DeviceActivityName) -> Bool {
        name == activityName
    }

    static func isCurrentlyInBedtimeWindow(now: Date, calendar: Calendar = .current) -> Bool {
        guard isEnabled else { return false }
        let sh = defaults.object(forKey: startHourKey) as? Int ?? 22
        let sm = defaults.object(forKey: startMinuteKey) as? Int ?? 0
        let eh = defaults.object(forKey: endHourKey) as? Int ?? 7
        let em = defaults.object(forKey: endMinuteKey) as? Int ?? 0
        let nowMin = calendar.component(.hour, from: now) * 60 + calendar.component(.minute, from: now)
        let startMin = sh * 60 + sm
        let endMin = eh * 60 + em
        if startMin == endMin { return false }
        if startMin < endMin {
            return nowMin >= startMin && nowMin < endMin
        }
        // Через полночь: 22:00 → 07:00
        return nowMin >= startMin || nowMin < endMin
    }

    private static func startMonitoring(startHour: Int, startMinute: Int, endHour: Int, endMinute: Int) throws {
        center.stopMonitoring([activityName])
        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: startHour, minute: startMinute),
            intervalEnd: DateComponents(hour: endHour, minute: endMinute),
            repeats: true
        )
        try center.startMonitoring(activityName, during: schedule)
        print("🌙 BedtimeNightLock: monitoring \(startHour):\(startMinute)–\(endHour):\(endMinute)")
    }

    private static func stopMonitoring() {
        center.stopMonitoring([activityName])
    }
}

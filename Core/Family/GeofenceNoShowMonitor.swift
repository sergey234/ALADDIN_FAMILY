import Foundation
import UserNotifications

/// geo-02 / geo-rel-02 — No Show: ждали Place к времени, нет enter → мягкий локальный пуш.
/// Расписание локально + UNCalendarNotificationTrigger (срабатывает не только на экране).
struct GeofenceNoShowSchedule: Codable, Equatable, Identifiable {
    var id: UUID
    var placeName: String
    var hour: Int
    var minute: Int
    var enabled: Bool
    /// Calendar weekday values (1=Sunday … 7=Saturday). `nil` / empty = every day.
    var weekdays: [Int]?
    /// Minutes after HH:MM before soft push if still no enter (15…30). Late / delayed arrival window.
    var graceMinutes: Int

    init(
        id: UUID = UUID(),
        placeName: String,
        hour: Int,
        minute: Int,
        enabled: Bool = true,
        weekdays: [Int]? = nil,
        graceMinutes: Int = 15
    ) {
        self.id = id
        self.placeName = placeName
        self.hour = hour
        self.minute = minute
        self.enabled = enabled
        self.weekdays = weekdays
        self.graceMinutes = Self.clampGrace(graceMinutes)
    }

    enum CodingKeys: String, CodingKey {
        case id, placeName, hour, minute, enabled, weekdays, graceMinutes
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(UUID.self, forKey: .id)
        placeName = try c.decode(String.self, forKey: .placeName)
        hour = try c.decode(Int.self, forKey: .hour)
        minute = try c.decode(Int.self, forKey: .minute)
        enabled = try c.decodeIfPresent(Bool.self, forKey: .enabled) ?? true
        weekdays = try c.decodeIfPresent([Int].self, forKey: .weekdays)
        graceMinutes = Self.clampGrace(try c.decodeIfPresent(Int.self, forKey: .graceMinutes) ?? 15)
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(id, forKey: .id)
        try c.encode(placeName, forKey: .placeName)
        try c.encode(hour, forKey: .hour)
        try c.encode(minute, forKey: .minute)
        try c.encode(enabled, forKey: .enabled)
        try c.encodeIfPresent(weekdays, forKey: .weekdays)
        try c.encode(graceMinutes, forKey: .graceMinutes)
    }

    static func clampGrace(_ value: Int) -> Int {
        min(30, max(15, value))
    }

    func applies(onWeekday weekday: Int) -> Bool {
        guard let days = weekdays, !days.isEmpty else { return true }
        return days.contains(weekday)
    }

    /// Check / calendar wake time = expected arrival + grace.
    func checkHourMinute() -> (hour: Int, minute: Int) {
        let total = hour * 60 + minute + Self.clampGrace(graceMinutes)
        let wrapped = ((total % (24 * 60)) + (24 * 60)) % (24 * 60)
        return (wrapped / 60, wrapped % 60)
    }
}

enum GeofenceNoShowMonitor {
    static let checkNotificationType = "geofence_noshow_check"
    private static let schedulesKey = "aladdin_geofence_noshow_schedules_v1"
    private static let firedKeyPrefix = "aladdin_geofence_noshow_fired_"
    private static let calendarIdPrefix = "geofence_noshow_cal_"

    static func loadSchedules() -> [GeofenceNoShowSchedule] {
        guard let data = UserDefaults.standard.data(forKey: schedulesKey),
              let decoded = try? JSONDecoder().decode([GeofenceNoShowSchedule].self, from: data) else {
            return []
        }
        return decoded
    }

    static func saveSchedules(_ items: [GeofenceNoShowSchedule]) {
        guard let data = try? JSONEncoder().encode(items) else { return }
        UserDefaults.standard.set(data, forKey: schedulesKey)
        resyncCalendarTriggers()
    }

    /// Schedule silent calendar wakes so checkDue runs even when the modal is closed.
    static func resyncCalendarTriggers() {
        let center = UNUserNotificationCenter.current()
        center.getPendingNotificationRequests { pending in
            let stale = pending
                .map(\.identifier)
                .filter { $0.hasPrefix(calendarIdPrefix) }
            center.removePendingNotificationRequests(withIdentifiers: stale)

            let schedules = loadSchedules().filter(\.enabled)
            guard !schedules.isEmpty else { return }

            center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
                guard granted else { return }
                for schedule in schedules {
                    scheduleCalendarRequests(for: schedule, center: center)
                }
            }
        }
    }

    private static func scheduleCalendarRequests(for schedule: GeofenceNoShowSchedule, center: UNUserNotificationCenter) {
        let weekdays: [Int]
        if let days = schedule.weekdays, !days.isEmpty {
            weekdays = days
        } else {
            weekdays = Array(1...7)
        }

        for weekday in weekdays {
            let check = schedule.checkHourMinute()
            var comps = DateComponents()
            comps.hour = check.hour
            comps.minute = check.minute
            comps.weekday = weekday

            let content = UNMutableNotificationContent()
            content.title = " "
            content.body = " "
            content.sound = nil
            content.userInfo = [
                "type": checkNotificationType,
                "schedule_id": schedule.id.uuidString,
                "place": schedule.placeName
            ]
            // Invisible wake: suppressed in willPresent; checkDue may fire the real alert.
            content.interruptionLevel = .passive

            let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: true)
            let id = "\(calendarIdPrefix)\(schedule.id.uuidString)_w\(weekday)"
            let request = UNNotificationRequest(identifier: id, content: content, trigger: trigger)
            center.add(request, withCompletionHandler: nil)
        }
    }

    /// Call from calendar wake, scene active, or modal open.
    /// Soft push at expected time + grace (15…30 min) if no enter yet.
    static func checkDue(now: Date = Date(), localization: LocalizationManager = .shared) {
        let cal = Calendar.current
        let hour = cal.component(.hour, from: now)
        let minute = cal.component(.minute, from: now)
        let weekday = cal.component(.weekday, from: now)
        let dayStamp = Self.dayStamp(now)

        for schedule in loadSchedules() where schedule.enabled {
            guard schedule.applies(onWeekday: weekday) else { continue }
            let check = schedule.checkHourMinute()
            let due = check.hour == hour && abs(check.minute - minute) <= 2
            guard due else { continue }

            let firedKey = firedKeyPrefix + schedule.id.uuidString + "_" + dayStamp
            if UserDefaults.standard.bool(forKey: firedKey) { continue }

            let arrivedToday = GeofenceEventStore.events(lastDays: 1).contains {
                $0.isArrival && Self.namesMatch($0.regionName, schedule.placeName, localization: localization)
            }
            if arrivedToday {
                UserDefaults.standard.set(true, forKey: firedKey)
                continue
            }

            UserDefaults.standard.set(true, forKey: firedKey)
            NotificationManager.shared.sendLocalNotification(
                title: localization.localized("geofence_noshow_push_title"),
                body: String(
                    format: localization.localized("geofence_noshow_push_body"),
                    schedule.placeName,
                    String(format: "%02d:%02d", schedule.hour, schedule.minute)
                ),
                category: .family,
                userInfo: [
                    "type": "geofence_noshow",
                    "deepLink": "aladdin://family/location",
                    "place": schedule.placeName
                ],
                delay: 0.3
            )
        }
    }

    private static func namesMatch(_ a: String, _ b: String, localization: LocalizationManager) -> Bool {
        let x = a.lowercased()
        let y = b.lowercased()
        if x == y || x.contains(y) || y.contains(x) { return true }
        let home = localization.localized("geofences_home").lowercased()
        let school = localization.localized("geofences_school").lowercased()
        if (x.contains(home) && y.contains(home)) || (x.contains(school) && y.contains(school)) {
            return true
        }
        return false
    }

    private static func dayStamp(_ date: Date) -> String {
        let f = DateFormatter()
        f.calendar = Calendar.current
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: date)
    }
}

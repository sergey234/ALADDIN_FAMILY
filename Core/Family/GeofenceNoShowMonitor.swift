import Foundation

/// geo-02 — No Show: ждали Place к времени, нет enter → мягкий локальный пуш.
/// Расписание хранится локально (час/минута + имя места). Без GPS-трека.
struct GeofenceNoShowSchedule: Codable, Equatable, Identifiable {
    var id: UUID
    var placeName: String
    var hour: Int
    var minute: Int
    var enabled: Bool
}

enum GeofenceNoShowMonitor {
    private static let schedulesKey = "aladdin_geofence_noshow_schedules_v1"
    private static let firedKeyPrefix = "aladdin_geofence_noshow_fired_"

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
    }

    /// Вызывать периодически (foreground / background fetch). Окно ±2 минуты после HH:MM.
    static func checkDue(now: Date = Date(), localization: LocalizationManager = .shared) {
        let cal = Calendar.current
        let hour = cal.component(.hour, from: now)
        let minute = cal.component(.minute, from: now)
        let dayStamp = Self.dayStamp(now)

        for schedule in loadSchedules() where schedule.enabled {
            let due = schedule.hour == hour && abs(schedule.minute - minute) <= 2
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

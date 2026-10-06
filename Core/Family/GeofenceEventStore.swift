import Foundation
import CoreLocation
import UIKit

/// fsl-05 — живые события геозон (без демо «09:15»).
struct GeofenceDayEvent: Codable, Equatable, Identifiable {
    let id: String
    let time: String
    let action: String
    let isArrival: Bool
    let regionName: String
    let createdAt: Date
}

enum GeofenceEventStore {
    private static let key = "aladdin_geofence_day_events_v1"
    private static let dayKey = "aladdin_geofence_day_stamp_v1"

    static func todayEvents() -> [GeofenceDayEvent] {
        purgeIfNewDay()
        return load().sorted { $0.createdAt > $1.createdAt }
    }

    static func asLocationEvents() -> [LocationEvent] {
        todayEvents().map {
            LocationEvent(
                time: $0.time,
                action: $0.action,
                status: $0.isArrival ? .arrival : .departure
            )
        }
    }

    static func record(
        regionIdentifier: String,
        isArrival: Bool,
        localization: LocalizationManager = .shared
    ) {
        purgeIfNewDay()
        let name = resolveGeofenceName(regionId: regionIdentifier, localization: localization)
        let formatter = DateFormatter()
        formatter.locale = localization.locale
        formatter.dateFormat = "HH:mm"
        let time = formatter.string(from: Date())

        let action: String
        if isArrival {
            if isSchoolName(name, localization: localization) {
                action = localization.localized("location_arrived_school")
            } else {
                action = String(format: localization.localized("location_arrived_named"), name)
            }
        } else {
            if isSchoolName(name, localization: localization) {
                action = localization.localized("location_left_school")
            } else {
                action = String(format: localization.localized("location_left_named"), name)
            }
        }

        var events = load()
        events.append(
            GeofenceDayEvent(
                id: UUID().uuidString,
                time: time,
                action: action,
                isArrival: isArrival,
                regionName: name,
                createdAt: Date()
            )
        )
        // Keep only today, max 40
        if events.count > 40 {
            events = Array(events.suffix(40))
        }
        save(events)

        // Local push for school arrival (parent may be same device / Always auth on child phone)
        if isArrival, isSchoolName(name, localization: localization) {
            FamilyShieldWeekDigestStore.recordSchoolArrival()
            NotificationManager.shared.sendLocalNotification(
                title: localization.localized("geofence_school_push_title"),
                body: String(format: localization.localized("geofence_school_push_body"), name),
                category: .family,
                userInfo: [
                    "type": "geofence_school_arrival",
                    "deepLink": "aladdin://family/location"
                ],
                delay: 0.2
            )
        }

        NotificationCenter.default.post(name: .geofenceDayEventsDidChange, object: nil)
    }

    private static func isSchoolName(_ name: String, localization: LocalizationManager) -> Bool {
        let school = localization.localized("geofences_school").lowercased()
        let n = name.lowercased()
        return n.contains(school) || n.contains("школ") || n.contains("school")
    }

    private static func resolveGeofenceName(regionId: String, localization: LocalizationManager) -> String {
        let geofencesKey = "geofences_settings"
        if let data = UserDefaults.standard.data(forKey: geofencesKey),
           let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data),
           let match = decoded.first(where: { $0.id.uuidString == regionId }) {
            return match.name
        }
        return localization.localized("family_geofence")
    }

    private static func purgeIfNewDay() {
        let stamp = dayStamp()
        let saved = UserDefaults.standard.string(forKey: dayKey)
        if saved != stamp {
            UserDefaults.standard.set(stamp, forKey: dayKey)
            save([])
        }
    }

    private static func dayStamp() -> String {
        let f = DateFormatter()
        f.calendar = Calendar.current
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: Date())
    }

    private static func load() -> [GeofenceDayEvent] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let decoded = try? JSONDecoder().decode([GeofenceDayEvent].self, from: data) else {
            return []
        }
        return decoded
    }

    private static func save(_ events: [GeofenceDayEvent]) {
        guard let data = try? JSONEncoder().encode(events) else { return }
        UserDefaults.standard.set(data, forKey: key)
    }
}

extension Notification.Name {
    static let geofenceDayEventsDidChange = Notification.Name("geofenceDayEventsDidChange")
    static let familyPresenceDidChange = Notification.Name("familyPresenceDidChange")
}

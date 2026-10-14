import Foundation
import CoreLocation
import UIKit

/// fsl-05 / geo-01 / geo-03 — живые события геозон (enter/exit), не GPS-трек.
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
    /// geo-03: храним до 7 суток enter/exit (не линию маршрута).
    private static let retentionDays = 7
    private static let maxEvents = 200

    static func todayEvents() -> [GeofenceDayEvent] {
        events(lastDays: 1)
    }

    /// События за последние `days` календарных суток (включая сегодня).
    static func events(lastDays: Int) -> [GeofenceDayEvent] {
        purgeOlderThanRetention()
        let days = max(1, lastDays)
        let cal = Calendar.current
        let start = cal.startOfDay(for: cal.date(byAdding: .day, value: -(days - 1), to: Date()) ?? Date())
        return load()
            .filter { $0.createdAt >= start }
            .sorted { $0.createdAt > $1.createdAt }
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
        purgeOlderThanRetention()
        let name = resolveGeofenceName(regionId: regionIdentifier, localization: localization)
        let formatter = DateFormatter()
        formatter.locale = localization.locale
        formatter.dateFormat = "HH:mm"
        let time = formatter.string(from: Date())

        let action: String
        if isArrival {
            if isSchoolName(name, localization: localization) {
                action = localization.localized("location_arrived_school")
            } else if isHomeName(name, localization: localization) {
                action = localization.localized("location_returned_home")
            } else {
                action = String(format: localization.localized("location_arrived_named"), name)
            }
        } else {
            if isSchoolName(name, localization: localization) {
                action = localization.localized("location_left_school")
            } else if isHomeName(name, localization: localization) {
                action = localization.localized("location_left_home")
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
        if events.count > maxEvents {
            events = Array(events.suffix(maxEvents))
        }
        save(events)

        if isArrival, isSchoolName(name, localization: localization) {
            FamilyShieldWeekDigestStore.recordSchoolArrival()
        }

        // W5 hybrid: local banner for every place enter/exit (not only home/school).
        let pushTitleKey: String
        let pushBodyKey: String
        let typeKey: String
        if isArrival {
            if isSchoolName(name, localization: localization) {
                pushTitleKey = "geofence_school_push_title"
                pushBodyKey = "geofence_school_push_body"
                typeKey = "geofence_school_arrival"
            } else if isHomeName(name, localization: localization) {
                pushTitleKey = "geofence_home_push_title"
                pushBodyKey = "geofence_home_push_body"
                typeKey = "geofence_home_arrival"
            } else {
                pushTitleKey = "geofence_place_push_title"
                pushBodyKey = "geofence_place_arrived_body"
                typeKey = "geofence_place_arrival"
            }
        } else {
            pushTitleKey = "geofence_place_push_title"
            pushBodyKey = "geofence_place_left_body"
            typeKey = "geofence_place_departure"
        }

        let correlation = "geofence-\(regionIdentifier)-\(isArrival ? "in" : "out")-\(Int(Date().timeIntervalSince1970 / 60))"
        NotificationManager.shared.sendLocalNotification(
            title: localization.localized(pushTitleKey),
            body: String(format: localization.localized(pushBodyKey), name),
            category: .family,
            userInfo: [
                "type": typeKey,
                "event_id": correlation,
                "correlation_id": correlation,
                "deepLink": "aladdin://family/location"
            ],
            delay: 0.2
        )

        // Soft server/APNs path via family chat (throttled).
        Task { @MainActor in
            GeofenceFamilyBridge.softNotifyFamilyIfNeeded(
                placeName: name,
                isArrival: isArrival,
                regionId: regionIdentifier,
                localization: localization
            )
        }

        NotificationCenter.default.post(name: .geofenceDayEventsDidChange, object: nil)
    }

    private static func isSchoolName(_ name: String, localization: LocalizationManager) -> Bool {
        let school = localization.localized("geofences_school").lowercased()
        let n = name.lowercased()
        return n.contains(school) || n.contains("школ") || n.contains("school")
    }

    private static func isHomeName(_ name: String, localization: LocalizationManager) -> Bool {
        let home = localization.localized("geofences_home").lowercased()
        let n = name.lowercased()
        return n.contains(home) || n.contains("дом") || n.contains("home")
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

    private static func purgeOlderThanRetention() {
        let cal = Calendar.current
        guard let cutoff = cal.date(byAdding: .day, value: -retentionDays, to: Date()) else { return }
        let start = cal.startOfDay(for: cutoff)
        let kept = load().filter { $0.createdAt >= start }
        save(kept)
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

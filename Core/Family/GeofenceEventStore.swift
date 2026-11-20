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
        let resolved = resolveGeofenceName(regionId: regionIdentifier, localization: localization)
        let name = resolved.displayName
        let formatter = DateFormatter()
        formatter.locale = localization.locale
        formatter.dateFormat = "HH:mm"
        let time = formatter.string(from: Date())
        let eventId = UUID().uuidString

        let action = actionLine(name: name, isArrival: isArrival, localization: localization)

        var events = load()
        events.append(
            GeofenceDayEvent(
                id: eventId,
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

        // QA-05 A: if settings had no place name — reverse-geocode street and rewrite event.
        if resolved.needsStreetFallback, let coord = resolved.coordinate {
            Task { @MainActor in
                let loc = CLLocation(latitude: coord.latitude, longitude: coord.longitude)
                if let street = await GeofenceGeocodingService.shared.reverseGeocodeAddressLine(for: loc),
                   !street.isEmpty {
                    rewriteEventName(eventId: eventId, name: street, isArrival: isArrival, localization: localization)
                }
            }
        }

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
                ShareArrivedHomeOffer.noteHomeArrivalIfEligible()
            } else {
                pushTitleKey = "geofence_place_push_title"
                pushBodyKey = "geofence_place_arrived_body"
                typeKey = "geofence_place_arrival"
            }
        } else {
            if isSchoolName(name, localization: localization) {
                pushTitleKey = "geofence_place_push_title"
                pushBodyKey = "geofence_place_left_body"
                typeKey = "geofence_school_departure"
            } else if isHomeName(name, localization: localization) {
                pushTitleKey = "geofence_place_push_title"
                pushBodyKey = "geofence_place_left_body"
                typeKey = "geofence_home_departure"
            } else {
                pushTitleKey = "geofence_place_push_title"
                pushBodyKey = "geofence_place_left_body"
                typeKey = "geofence_place_departure"
            }
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
                "deepLink": "aladdin://family/location",
                "priority": "high"
            ],
            delay: 0.2
        )

        // Soft chat (throttled) + dedicated parent APNs path (L4 — needs server deploy GO).
        Task { @MainActor in
            GeofenceFamilyBridge.softNotifyFamilyIfNeeded(
                placeName: name,
                isArrival: isArrival,
                regionId: regionIdentifier,
                localization: localization
            )
            GeofenceFamilyBridge.notifyParentsViaAPIIfNeeded(
                placeName: name,
                isArrival: isArrival,
                regionId: regionIdentifier,
                eventType: typeKey,
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

    private struct ResolvedPlaceName {
        let displayName: String
        let needsStreetFallback: Bool
        let coordinate: CLLocationCoordinate2D?
    }

    private static func actionLine(
        name: String,
        isArrival: Bool,
        localization: LocalizationManager
    ) -> String {
        if isArrival {
            if isSchoolName(name, localization: localization) {
                return localization.localized("location_arrived_school")
            }
            if isHomeName(name, localization: localization) {
                return localization.localized("location_returned_home")
            }
            return String(format: localization.localized("location_arrived_named"), name)
        }
        if isSchoolName(name, localization: localization) {
            return localization.localized("location_left_school")
        }
        if isHomeName(name, localization: localization) {
            return localization.localized("location_left_home")
        }
        return String(format: localization.localized("location_left_named"), name)
    }

    private static func rewriteEventName(
        eventId: String,
        name: String,
        isArrival: Bool,
        localization: LocalizationManager
    ) {
        var events = load()
        guard let idx = events.firstIndex(where: { $0.id == eventId }) else { return }
        let old = events[idx]
        events[idx] = GeofenceDayEvent(
            id: old.id,
            time: old.time,
            action: actionLine(name: name, isArrival: isArrival, localization: localization),
            isArrival: old.isArrival,
            regionName: name,
            createdAt: old.createdAt
        )
        save(events)
        NotificationCenter.default.post(name: .geofenceDayEventsDidChange, object: nil)
    }

    /// QA-05 A: place name from settings → address → reverse-geocode street (async).
    private static func resolveGeofenceName(
        regionId: String,
        localization: LocalizationManager
    ) -> ResolvedPlaceName {
        let generic = localization.localized("family_geofence")
        let coords = GeofenceGeocodingService.loadStoredCoordinatesMap()
        let geofencesKey = "geofences_settings"
        if let data = UserDefaults.standard.data(forKey: geofencesKey),
           let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data),
           let match = decoded.first(where: {
               $0.id.uuidString.caseInsensitiveCompare(regionId) == .orderedSame
           }) {
            let trimmedName = match.name.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmedName.isEmpty, trimmedName.caseInsensitiveCompare(generic) != .orderedSame {
                return ResolvedPlaceName(
                    displayName: trimmedName,
                    needsStreetFallback: false,
                    coordinate: coords[match.id]
                )
            }
            let trimmedAddress = match.address.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmedAddress.isEmpty {
                return ResolvedPlaceName(
                    displayName: trimmedAddress,
                    needsStreetFallback: false,
                    coordinate: coords[match.id]
                )
            }
            return ResolvedPlaceName(
                displayName: generic,
                needsStreetFallback: coords[match.id] != nil,
                coordinate: coords[match.id]
            )
        }
        // Region id may already be a human label from older builds.
        if !regionId.isEmpty,
           UUID(uuidString: regionId) == nil,
           regionId.caseInsensitiveCompare(generic) != .orderedSame {
            return ResolvedPlaceName(displayName: regionId, needsStreetFallback: false, coordinate: nil)
        }
        return ResolvedPlaceName(displayName: generic, needsStreetFallback: false, coordinate: nil)
    }

    /// Write only on change: reads run inside SwiftUI `body`, and on iOS ≤16 any UserDefaults
    /// write re-invalidates every `@AppStorage` view → infinite layout loop (watchdog kill).
    private static func purgeOlderThanRetention() {
        let cal = Calendar.current
        guard let cutoff = cal.date(byAdding: .day, value: -retentionDays, to: Date()) else { return }
        let start = cal.startOfDay(for: cutoff)
        let all = load()
        let kept = all.filter { $0.createdAt >= start }
        guard kept.count != all.count else { return }
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
    static let shareArrivedHomeOffer = ShareArrivedHomeOffer.offerNotification
}

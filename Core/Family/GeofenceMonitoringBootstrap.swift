import CoreLocation
import Foundation

/// geo-rel-05 — cold start / scene active: reload region monitoring if consent + auth.
@MainActor
enum GeofenceMonitoringBootstrap {
    private static let geofencesKey = "geofences_settings"

    /// Reload places → geocode → CLCircularRegion. Optionally upgrade to Always.
    static func reloadIfNeeded(
        locationManager: LocationManager = .shared,
        requestAlwaysUpgrade: Bool = true
    ) async {
        guard GeofencePlacesConsentStore.hasAccepted else { return }

        if requestAlwaysUpgrade {
            switch locationManager.authorizationStatus {
            case .notDetermined:
                locationManager.requestAuthorization(always: false)
            case .authorizedWhenInUse:
                locationManager.requestAlwaysUpgradeIfEligible()
            default:
                break
            }
        }

        guard locationManager.hasRequiredAuthorization() else { return }

        let geofences = loadGeofences()
        guard !geofences.isEmpty else { return }

        let coordinates = await GeofenceGeocodingService.shared.syncCoordinates(for: geofences)
        locationManager.loadAndMonitorGeofences(geofences, coordinates: coordinates)

        if locationManager.hasRequiredAuthorization(forBackground: true) {
            locationManager.startSignificantLocationChanges()
        }

        GeofenceNoShowMonitor.resyncCalendarTriggers()
        GeofenceNoShowMonitor.checkDue()
    }

    static func loadGeofences() -> [GeofenceItem] {
        guard let data = UserDefaults.standard.data(forKey: geofencesKey),
              let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) else {
            return []
        }
        return decoded.map {
            GeofenceItem(id: $0.id, name: $0.name, address: $0.address, radius: $0.radius, isActive: $0.isActive)
        }
    }

    /// Status key for one place row (localization key without "geofence" jargon).
    static func placeStatusKey(
        for item: GeofenceItem,
        locationManager: LocationManager = .shared
    ) -> String {
        if !GeofencePlacesConsentStore.hasAccepted {
            return "geofence_status_needs_consent"
        }
        let status = locationManager.authorizationStatus
        if status == .denied || status == .restricted {
            return "geofence_status_need_permission"
        }
        if status == .authorizedWhenInUse {
            return "geofence_status_need_always"
        }
        if status != .authorizedAlways && status != .authorizedWhenInUse {
            return "geofence_status_need_permission"
        }
        let coords = GeofenceGeocodingService.shared.loadStoredCoordinates()
        if coords[item.id] == nil {
            return "geofence_status_no_coords"
        }
        if locationManager.monitoredRegions[item.id.uuidString] != nil {
            return "geofence_status_monitoring"
        }
        return "geofence_status_ready"
    }
}

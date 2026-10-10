import CoreLocation
import Foundation

/// B6-04 — address → coordinate for parental geofence region monitoring.
@MainActor
final class GeofenceGeocodingService {
    static let shared = GeofenceGeocodingService()

    private let geocoder = CLGeocoder()
    /// Separate instance — Apple allows one in-flight request per CLGeocoder.
    private let reverseGeocoder = CLGeocoder()
    private let storageKey = "geofences_with_coordinates_v1"

    private init() {}

    func loadStoredCoordinates() -> [UUID: CLLocationCoordinate2D] {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([GeofenceWithCoordinatesCodable].self, from: data) else {
            return [:]
        }
        var map: [UUID: CLLocationCoordinate2D] = [:]
        for item in decoded {
            guard let geofence = item.toGeofenceWithCoordinates() else { continue }
            map[geofence.id] = geofence.center
        }
        return map
    }

    func syncCoordinates(for geofences: [GeofenceItem]) async -> [UUID: CLLocationCoordinate2D] {
        var coordinates: [UUID: CLLocationCoordinate2D] = [:]
        var persisted: [GeofenceWithCoordinatesCodable] = []
        let existing = loadStoredByAddress()

        for geofence in geofences {
            let normalized = normalizeAddress(geofence.address)
            if normalized.isEmpty { continue }

            if let cached = existing[normalized] {
                coordinates[geofence.id] = cached.center
                persisted.append(GeofenceWithCoordinatesCodable(from: cached.withId(geofence.id)))
                continue
            }

            do {
                let center = try await geocodeAddress(normalized)
                let withCoords = geofence.withCoordinates(
                    latitude: center.latitude,
                    longitude: center.longitude
                )
                coordinates[geofence.id] = center
                persisted.append(GeofenceWithCoordinatesCodable(from: withCoords))
            } catch {
                print("⚠️ GeofenceGeocodingService: '\(geofence.name)' — \(error.localizedDescription)")
            }
        }

        if let encoded = try? JSONEncoder().encode(persisted) {
            UserDefaults.standard.set(encoded, forKey: storageKey)
        }
        return coordinates
    }

    private func loadStoredByAddress() -> [String: GeofenceWithCoordinates] {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([GeofenceWithCoordinatesCodable].self, from: data) else {
            return [:]
        }
        var map: [String: GeofenceWithCoordinates] = [:]
        for item in decoded {
            guard let geofence = item.toGeofenceWithCoordinates() else { continue }
            map[normalizeAddress(geofence.address)] = geofence
        }
        return map
    }

    private func geocodeAddress(_ address: String) async throws -> CLLocationCoordinate2D {
        try await withCheckedThrowingContinuation { continuation in
            geocoder.geocodeAddressString(address) { placemarks, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                guard let location = placemarks?.first?.location else {
                    continuation.resume(throwing: GeofenceGeocodingError.noPlacemark)
                    return
                }
                continuation.resume(returning: location.coordinate)
            }
        }
    }

    /// Reverse geocode: city / locality for human-readable status (keeps raw coords in UI separately).
    func reverseGeocodeLocality(for location: CLLocation) async -> String? {
        await withCheckedContinuation { continuation in
            reverseGeocoder.reverseGeocodeLocation(location) { placemarks, _ in
                let mark = placemarks?.first
                let city = mark?.locality?.trimmingCharacters(in: .whitespacesAndNewlines)
                let area = mark?.administrativeArea?.trimmingCharacters(in: .whitespacesAndNewlines)
                if let city, !city.isEmpty {
                    continuation.resume(returning: city)
                } else if let area, !area.isEmpty {
                    continuation.resume(returning: area)
                } else {
                    continuation.resume(returning: nil)
                }
            }
        }
    }

    /// If current GPS is inside (or near) a saved place radius — return that place name.
    func nearestConfiguredPlaceName(to location: CLLocation) -> String? {
        let stored = loadStoredCoordinates()
        guard !stored.isEmpty else { return nil }
        guard let data = UserDefaults.standard.data(forKey: "geofences_settings"),
              let items = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) else {
            return nil
        }
        var best: (name: String, distance: CLLocationDistance)?
        for item in items {
            guard item.isActive else { continue }
            guard let center = stored[item.id] else { continue }
            let placeLoc = CLLocation(latitude: center.latitude, longitude: center.longitude)
            let distance = location.distance(from: placeLoc)
            let threshold = max(item.radius, 80)
            guard distance <= threshold * 1.25 else { continue }
            if best == nil || distance < best!.distance {
                best = (item.name, distance)
            }
        }
        return best?.name
    }

    /// Demo seed addresses (Lenin / Pushkin) — not real family places.
    static func isDemoPlaceholderAddress(_ address: String, localization: LocalizationManager) -> Bool {
        let normalized = address.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let demos = [
            localization.localized("geofences_street_lenin"),
            localization.localized("geofences_street_pushkin"),
        ].map { $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() }
        return demos.contains(normalized)
    }

    private func normalizeAddress(_ address: String) -> String {
        address.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
    }
}

enum GeofenceGeocodingError: LocalizedError {
    case noPlacemark

    var errorDescription: String? {
        switch self {
        case .noPlacemark: return "Geocoding returned no coordinates."
        }
    }
}

private extension GeofenceWithCoordinates {
    func withId(_ id: UUID) -> GeofenceWithCoordinates {
        GeofenceWithCoordinates(
            id: id,
            name: name,
            address: address,
            radius: radius,
            latitude: latitude,
            longitude: longitude
        )
    }
}

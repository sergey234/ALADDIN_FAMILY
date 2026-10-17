import Foundation

/// WAVE3 L13 — push real place coords to parental API; never hydrate UI from mock GET lists.
@MainActor
enum GeofencePlacesCloudSync {
    private static let activeChildKey = "active_child_profile_server_id"

    /// Soft upsert after local geocode success. Failures are logged only (local places remain SSOT).
    static func upsertPlace(
        _ place: GeofenceItem,
        latitude: Double,
        longitude: Double
    ) {
        let childId = UserDefaults.standard.string(forKey: activeChildKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        guard !childId.isEmpty else {
            print("ℹ️ GeofencePlacesCloudSync: skip — no active child id")
            return
        }
        guard abs(latitude) > 0.0001 || abs(longitude) > 0.0001 else {
            print("⚠️ GeofencePlacesCloudSync: refuse zero coords")
            return
        }

        ParentalControlManager.shared.addGeofenceToServer(
            childId: childId,
            name: place.name,
            latitude: latitude,
            longitude: longitude,
            radius: place.radius,
            isActive: place.isActive
        ) { result in
            switch result {
            case .success:
                print("✅ GeofencePlacesCloudSync: upserted '\(place.name)'")
            case .failure(let error):
                print("⚠️ GeofencePlacesCloudSync: \(error.localizedDescription)")
            }
        }
    }
}

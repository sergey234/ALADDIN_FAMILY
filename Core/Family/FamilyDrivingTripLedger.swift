import CoreLocation
import Foundation

/// Локальный SSOT завершённых поездок (per member).
/// Серверный `/api/reports/driving/stats` сейчас отдаёт mock — клиент **не** использует его.
/// Life360-паттерн: поездка с устройства члена → история + неделя/месяц + PDF на этого человека.
enum FamilyDrivingTripLedger {
    private static let indexKey = "family_driving_trip_ledger_v1"
    private static let metaPrefix = "driving_trip_meta_v1_"
    private static let maxTrips = 200

    struct TripMeta: Codable {
        var tripId: String
        var memberId: String
        var memberName: String
        var startedAt: Date
    }

    // MARK: - Active trip meta (paired with DrivingTripTrackStore)

    static func beginMeta(tripId: String, memberId: String, memberName: String, at: Date = Date()) {
        let meta = TripMeta(
            tripId: tripId,
            memberId: memberId.isEmpty ? "current" : memberId,
            memberName: memberName.isEmpty ? "Me" : memberName,
            startedAt: at
        )
        if let data = try? JSONEncoder().encode(meta) {
            UserDefaults.standard.set(data, forKey: metaPrefix + tripId)
        }
    }

    static func loadMeta(tripId: String) -> TripMeta? {
        guard let data = UserDefaults.standard.data(forKey: metaPrefix + tripId),
              let meta = try? JSONDecoder().decode(TripMeta.self, from: data) else {
            return nil
        }
        return meta
    }

    static func clearMeta(tripId: String) {
        UserDefaults.standard.removeObject(forKey: metaPrefix + tripId)
    }

    /// Текущий member на этом устройстве (для auto-trip).
    static func currentDeviceMember() -> (id: String, name: String) {
        let id = (UserDefaults.standard.string(forKey: "your_member_id") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let name = (UserDefaults.standard.string(forKey: "your_member_name") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if !id.isEmpty {
            return (id, name.isEmpty ? "Me" : name)
        }
        return ("current", name.isEmpty ? "Me" : name)
    }

    // MARK: - Finish → ledger

    /// Собрать отчёт из GPS-трека и положить в ledger. Без выдуманных точек.
    @discardableResult
    static func finalizeActiveTrip(
        tripId: String,
        end: CLLocationCoordinate2D?,
        memberId: String? = nil,
        memberName: String? = nil
    ) -> DrivingReport? {
        if let end {
            DrivingTripTrackStore.append(tripId: tripId, coordinate: end)
        }
        let points = DrivingTripTrackStore.load(tripId: tripId)
        guard points.count >= 2 else {
            DrivingTripTrackStore.finish(tripId: tripId, end: nil)
            clearMeta(tripId: tripId)
            return nil
        }

        let meta = loadMeta(tripId: tripId)
        let device = currentDeviceMember()
        let uid = (memberId?.isEmpty == false ? memberId! : (meta?.memberId ?? device.id))
        let uname = (memberName?.isEmpty == false ? memberName! : (meta?.memberName ?? device.name))
        let startedAt = meta?.startedAt ?? Date().addingTimeInterval(-Double(max(points.count - 1, 1) * 30))
        let endedAt = Date()

        var distanceM: Double = 0
        var maxSpeedKmh: Double = 0
        for i in 1..<points.count {
            let a = CLLocation(latitude: points[i - 1].latitude, longitude: points[i - 1].longitude)
            let b = CLLocation(latitude: points[i].latitude, longitude: points[i].longitude)
            let d = a.distance(from: b)
            distanceM += d
            // ~30s sample gap from tracker — rough speed only from real spacing.
            let speed = (d / 30.0) * 3.6
            if speed.isFinite { maxSpeedKmh = max(maxSpeedKmh, min(speed, 180)) }
        }
        let duration = max(endedAt.timeIntervalSince(startedAt), 60)
        let distanceKm = distanceM / 1000.0
        let avgSpeed = duration > 0 ? (distanceKm / (duration / 3600.0)) : 0
        let safety = safetyScore(maxSpeedKmh: maxSpeedKmh)
        let violations: [DrivingViolation] = maxSpeedKmh >= 120
            ? [DrivingViolation(
                type: .speedExceeded,
                timestamp: endedAt,
                description: "High speed \(Int(maxSpeedKmh)) km/h",
                severity: maxSpeedKmh >= 140 ? .high : .medium
            )]
            : []

        let first = points.first!
        let last = points.last!
        let report = DrivingReport(
            id: tripId,
            userId: uid,
            userName: uname,
            startTime: startedAt,
            endTime: endedAt,
            startLocation: String(format: "%.4f, %.4f", first.latitude, first.longitude),
            endLocation: String(format: "%.4f, %.4f", last.latitude, last.longitude),
            distance: distanceKm,
            duration: duration,
            averageSpeed: avgSpeed,
            maxSpeed: maxSpeedKmh,
            safetyScore: safety,
            events: [],
            violations: violations,
            positioningSystem: "GPS",
            startLatitude: first.latitude,
            startLongitude: first.longitude,
            endLatitude: last.latitude,
            endLongitude: last.longitude,
            routePoints: points
        )

        upsert(report)
        DrivingTripTrackStore.finish(tripId: tripId, end: nil)
        clearMeta(tripId: tripId)
        return report
    }

    private static func safetyScore(maxSpeedKmh: Double) -> Double {
        if maxSpeedKmh >= 140 { return 4.0 }
        if maxSpeedKmh >= 120 { return 6.0 }
        if maxSpeedKmh >= 100 { return 7.5 }
        return 9.0
    }

    // MARK: - Index

    static func upsert(_ report: DrivingReport) {
        var all = loadAll()
        all.removeAll { $0.id == report.id }
        all.insert(report, at: 0)
        if all.count > maxTrips {
            all = Array(all.prefix(maxTrips))
        }
        saveAll(all)
    }

    static func loadAll() -> [DrivingReport] {
        guard let data = UserDefaults.standard.data(forKey: indexKey),
              let decoded = try? JSONDecoder().decode([DrivingReport].self, from: data) else {
            return []
        }
        return decoded
    }

    private static func saveAll(_ reports: [DrivingReport]) {
        if let data = try? JSONEncoder().encode(reports) {
            UserDefaults.standard.set(data, forKey: indexKey)
        }
    }

    static func reports(memberId: String?, period: String) -> [DrivingReport] {
        let start = periodStart(period)
        let mid = (memberId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        return loadAll().filter { report in
            guard report.startTime >= start else { return false }
            guard !mid.isEmpty, mid != "current" else { return true }
            // «current» / this device: also match empty / current aliases.
            if mid == currentDeviceMember().id {
                return report.userId == mid
                    || report.userId == "current"
                    || report.userId.isEmpty
            }
            return report.userId == mid
        }
        .sorted { $0.startTime > $1.startTime }
    }

    static func stats(from reports: [DrivingReport], period: String) -> DrivingStats {
        let trips = reports.count
        let distance = reports.reduce(0.0) { $0 + $1.distance }
        let duration = reports.reduce(0.0) { $0 + $1.duration }
        let violations = reports.reduce(0) { $0 + $1.violations.count }
        let avgSafety: Double
        if trips == 0 {
            avgSafety = 0
        } else {
            avgSafety = reports.reduce(0.0) { $0 + $1.safetyScore } / Double(trips)
        }
        return DrivingStats(
            totalTrips: trips,
            totalDistance: distance,
            totalDuration: duration,
            averageSafetyScore: avgSafety,
            violationsCount: violations,
            period: period,
            positioningSystem: trips > 0 ? "GPS" : nil
        )
    }

    static func periodStart(_ period: String) -> Date {
        let now = Date()
        let cal = Calendar.current
        switch period {
        case "today":
            return cal.startOfDay(for: now)
        case "month":
            return cal.date(byAdding: .day, value: -30, to: now) ?? now
        case "year":
            return cal.date(byAdding: .day, value: -365, to: now) ?? now
        default: // week
            return cal.date(byAdding: .day, value: -7, to: now) ?? now
        }
    }

    /// Merge remote + local by id (prefer richer route / longer list).
    static func merge(remote: [DrivingReport], local: [DrivingReport]) -> [DrivingReport] {
        var map: [String: DrivingReport] = [:]
        for r in local { map[r.id] = r }
        for r in remote {
            if let existing = map[r.id] {
                map[r.id] = r.hasGPSTrack || r.routePoints.count >= existing.routePoints.count
                    ? DrivingTripTrackStore.mergeInto(r)
                    : DrivingTripTrackStore.mergeInto(existing)
            } else {
                map[r.id] = DrivingTripTrackStore.mergeInto(r)
            }
        }
        return map.values.sorted { $0.startTime > $1.startTime }
    }
}

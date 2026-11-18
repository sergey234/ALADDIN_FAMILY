import CoreLocation
import CoreMotion
import Foundation
import UserNotifications

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
    /// Display name empty → UI shows localized `where_phone_you` («Вы» / You).
    static func currentDeviceMember() -> (id: String, name: String) {
        let id = (UserDefaults.standard.string(forKey: "your_member_id") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let storedName = (UserDefaults.standard.string(forKey: "your_member_name") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let fallbackName = (UserDefaults.standard.string(forKey: "user_display_name")
            ?? UserDefaults.standard.string(forKey: "user_name")
            ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let name = storedName.isEmpty ? fallbackName : storedName
        if !id.isEmpty {
            return (id, name)
        }
        return ("current", name)
    }

    // MARK: - Finish → ledger

    /// Auto trips below this are GPS noise / parking shuffles: no ledger row, no push.
    static let minAutoTripKm: Double = 0.5
    static let minAutoTripSeconds: TimeInterval = 120

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
            print("TRIP_AUTO finalize FAIL id=\(tripId) points=\(points.count) (need ≥2) — honest empty, no fake track")
            DrivingTripTrackStore.finish(tripId: tripId, end: nil)
            clearMeta(tripId: tripId)
            return nil
        }

        let meta = loadMeta(tripId: tripId)
        let device = currentDeviceMember()
        let uid = (memberId?.isEmpty == false ? memberId! : (meta?.memberId ?? device.id))
        let uname = (memberName?.isEmpty == false ? memberName! : (meta?.memberName ?? device.name))
        let metrics = DrivingTripAnalyzer.analyze(points: points)
        let startedAt = meta?.startedAt
            ?? points.first?.t
            ?? Date().addingTimeInterval(-Double(max(points.count - 1, 1) * 30))
        // Stale close (iOS paused updates on parking): end = last real fix, not «now».
        let endedAt = points.last?.t ?? Date()

        let rawDuration = endedAt.timeIntervalSince(startedAt)
        if tripId.hasPrefix("auto_"),
           metrics.distanceKm < minAutoTripKm || rawDuration < minAutoTripSeconds {
            print(
                "TRIP_AUTO drop id=\(tripId) — too short km=\(String(format: "%.2f", metrics.distanceKm)) " +
                "sec=\(Int(rawDuration)) points=\(points.count)"
            )
            DrivingTripTrackStore.remove(tripId: tripId)
            clearMeta(tripId: tripId)
            return nil
        }

        let maxSpeedKmh = metrics.maxSpeedKmh
        let duration = max(rawDuration, 60)
        let distanceKm = metrics.distanceKm
        let avgSpeed = duration > 0 ? (distanceKm / (duration / 3600.0)) : 0
        let safety = max(1.0, safetyScore(maxSpeedKmh: maxSpeedKmh) - 0.5 * Double(metrics.harshViolations.count))
        var violations: [DrivingViolation] = metrics.harshViolations
        if maxSpeedKmh >= 120 {
            violations.append(DrivingViolation(
                type: .speedExceeded,
                timestamp: metrics.maxSpeedAt ?? endedAt,
                description: "High speed \(Int(maxSpeedKmh)) km/h",
                severity: maxSpeedKmh >= 140 ? .high : .medium
            ))
        }

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
            events: metrics.events,
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
        print(
            "TRIP_AUTO finalize OK id=\(tripId) member=\(uid)/\(uname) " +
            "km=\(String(format: "%.1f", distanceKm)) vmax=\(Int(maxSpeedKmh)) points=\(points.count)"
        )
        // H1: local push + deep link (RU/EN via LocalizationManager on MainActor).
        Task { @MainActor in
            if await DriveActivityClassifier.wasNotDriving(from: startedAt, to: endedAt) {
                print("TRIP_AUTO drop id=\(tripId) — motion says cycling/walking, not a car trip")
                removeReport(id: tripId)
                return
            }
            Self.notifyTripEnded(report)
            await enrichStreetLabels(for: report)
        }
        return report
    }

    static func report(id: String) -> DrivingReport? {
        loadAll().first { $0.id == id }
    }

    static func removeReport(id: String) {
        var all = loadAll()
        all.removeAll { $0.id == id }
        saveAll(all)
        DrivingTripTrackStore.remove(tripId: id)
    }

    /// P0.4 H1 — Life360-style trip completed push → map + polyline.
    /// Lock-screen parity: name as title, 🏁 km + 🚗 max speed, avatar attachment, time-sensitive.
    @MainActor
    private static func notifyTripEnded(_ report: DrivingReport) {
        let loc = LocalizationManager.shared
        let displayName: String = {
            let raw = report.userName.trimmingCharacters(in: .whitespacesAndNewlines)
            if raw.isEmpty || raw.lowercased() == "me" || report.userId == currentDeviceMember().id
                || report.userId == "current" {
                return loc.localized("where_phone_you")
            }
            return raw
        }()
        // Life360: title = person name; body = flag+distance / car+max speed (two lines).
        let title = displayName
        let body = String(
            format: loc.localized("family_trip_ended_push_body_life360"),
            report.distance,
            Int(report.maxSpeed.rounded())
        )
        let deepLink = FamilyPushDeepLink.mapURL(
            memberId: report.userId,
            focus: .trips,
            tripId: report.id
        )
        let avatarURL = Self.notificationAvatarFileURL()
        let tripSound = Self.tripEndedNotificationSound()
        NotificationManager.shared.sendLocalNotification(
            title: title,
            body: body,
            category: .family,
            userInfo: [
                "type": "family_trip_ended",
                "member_id": report.userId,
                "display_name": displayName,
                "trip_id": report.id,
                "deepLink": deepLink
            ],
            delay: 0.2,
            sound: tripSound,
            identifier: "family_trip_ended_\(report.id)",
            attachmentFileURL: avatarURL,
            timeSensitive: true
        )
        FamilyPushDeepLink.enqueue(
            memberId: report.userId,
            displayName: displayName,
            focus: .trips,
            openMap: false,
            tripId: report.id
        )
    }

    /// Map/profile photo for the lock-screen thumbnail (same file as the family map avatar).
    private static func notificationAvatarFileURL() -> URL? {
        let source = ProfileImageManager.shared.fileURLForNotificationAttachment(for: .main)
        guard FileManager.default.fileExists(atPath: source.path) else { return nil }
        // UNNotificationAttachment may delete/move the file — copy into tmp.
        let dest = FileManager.default.temporaryDirectory
            .appendingPathComponent("trip_avatar_\(UUID().uuidString).jpg")
        do {
            if FileManager.default.fileExists(atPath: dest.path) {
                try FileManager.default.removeItem(at: dest)
            }
            try FileManager.default.copyItem(at: source, to: dest)
            return dest
        } catch {
            print("TRIP_AUTO avatar attach copy failed: \(error.localizedDescription)")
            return nil
        }
    }

    /// Custom `trip_ended.caf` at bundle root (Copy Bundle Resources). Source: Mixkit Digital quick tone.
    /// See `Resources/Sounds/TRIP_ENDED_SOUND_SOURCE.txt`. Falls back to system default if missing.
    private static func tripEndedNotificationSound() -> UNNotificationSound {
        if Bundle.main.url(forResource: "trip_ended", withExtension: "caf") != nil {
            return UNNotificationSound(named: UNNotificationSoundName("trip_ended.caf"))
        }
        return .default
    }

    /// Reverse-geocode start/end when labels still look like coordinates.
    @MainActor
    static func enrichStreetLabels(for report: DrivingReport) async {
        guard looksLikeCoordinatePair(report.startLocation)
            || looksLikeCoordinatePair(report.endLocation)
            || report.startLatitude != nil else { return }
        let startCoord: CLLocationCoordinate2D? = {
            if let lat = report.startLatitude, let lon = report.startLongitude {
                return CLLocationCoordinate2D(latitude: lat, longitude: lon)
            }
            return nil
        }()
        let endCoord: CLLocationCoordinate2D? = {
            if let lat = report.endLatitude, let lon = report.endLongitude {
                return CLLocationCoordinate2D(latitude: lat, longitude: lon)
            }
            return nil
        }()
        var startLabel = report.startLocation
        var endLabel = report.endLocation
        if let c = startCoord, looksLikeCoordinatePair(report.startLocation) {
            let loc = CLLocation(latitude: c.latitude, longitude: c.longitude)
            if let line = await GeofenceGeocodingService.shared.reverseGeocodeAddressLine(for: loc) {
                startLabel = line
            }
        }
        if let c = endCoord, looksLikeCoordinatePair(report.endLocation) {
            let loc = CLLocation(latitude: c.latitude, longitude: c.longitude)
            if let line = await GeofenceGeocodingService.shared.reverseGeocodeAddressLine(for: loc) {
                endLabel = line
            }
        }
        guard startLabel != report.startLocation || endLabel != report.endLocation else { return }
        print("WHERE_PHONE trip streets id=\(report.id) start=\(startLabel) end=\(endLabel)")
        let updated = DrivingReport(
            id: report.id,
            userId: report.userId,
            userName: report.userName,
            startTime: report.startTime,
            endTime: report.endTime,
            startLocation: startLabel,
            endLocation: endLabel,
            distance: report.distance,
            duration: report.duration,
            averageSpeed: report.averageSpeed,
            maxSpeed: report.maxSpeed,
            safetyScore: report.safetyScore,
            events: report.events,
            violations: report.violations,
            positioningSystem: report.positioningSystem,
            startLatitude: report.startLatitude,
            startLongitude: report.startLongitude,
            endLatitude: report.endLatitude,
            endLongitude: report.endLongitude,
            routePoints: report.routePoints
        )
        upsert(updated)
    }

    static func looksLikeCoordinatePair(_ raw: String) -> Bool {
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        // e.g. "53.1069, 50.0843"
        let parts = t.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }
        guard parts.count == 2,
              Double(parts[0]) != nil,
              Double(parts[1]) != nil else { return false }
        return true
    }

    private static func safetyScore(maxSpeedKmh: Double) -> Double {
        if maxSpeedKmh >= 140 { return 4.0 }
        if maxSpeedKmh >= 120 { return 6.0 }
        if maxSpeedKmh >= 100 { return 7.5 }
        return 9.0
    }

    /// QA-04 A: median-of-window filter + hard UI/ledger cap ~140 (drops GPS 180 spikes).
    fileprivate static func cappedPeakSpeedKmh(_ samples: [Double], uiCap: Double = 140) -> Double {
        guard !samples.isEmpty else { return 0 }
        let sorted = samples.sorted()
        let median: Double
        if sorted.count % 2 == 0 {
            median = (sorted[sorted.count / 2 - 1] + sorted[sorted.count / 2]) / 2
        } else {
            median = sorted[sorted.count / 2]
        }
        // Keep samples within ~1.6× median (or absolute 160) before taking peak.
        let filtered = samples.filter { $0 <= max(median * 1.6, median + 25) }
        let peak = (filtered.isEmpty ? samples : filtered).max() ?? 0
        return min(peak, uiCap)
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

    /// Explicit delete only (period × member). Never called on dismiss/background.
    @discardableResult
    static func deleteReports(memberId: String?, period: String) -> [String] {
        let start = periodStart(period)
        let mid = (memberId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let deviceId = currentDeviceMember().id
        var all = loadAll()
        var removedIds: [String] = []
        all.removeAll { report in
            guard report.startTime >= start else { return false }
            let matchesMember: Bool
            if mid.isEmpty || mid == "current" {
                matchesMember = true
            } else if mid == deviceId {
                matchesMember = report.userId == mid
                    || report.userId == "current"
                    || report.userId.isEmpty
            } else {
                matchesMember = report.userId == mid
            }
            guard matchesMember else { return false }
            removedIds.append(report.id)
            return true
        }
        if !removedIds.isEmpty {
            saveAll(all)
            for id in removedIds {
                DrivingTripTrackStore.remove(tripId: id)
                clearMeta(tripId: id)
            }
            print("TRIP_AUTO ledger delete period=\(period) member=\(mid) count=\(removedIds.count)")
        }
        return removedIds
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

/// Trip metrics from real GPS fixes only (time + Doppler speed when present).
/// Trips saved before build 34 have no timestamps → legacy 30 s spacing, no events.
enum DrivingTripAnalyzer {
    struct Metrics {
        let distanceKm: Double
        let maxSpeedKmh: Double
        let maxSpeedAt: Date?
        let events: [DrivingEvent]
        let harshViolations: [DrivingViolation]
    }

    static let hardBrakeMps2: Double = -3.4
    static let hardAccelMps2: Double = 3.0
    private static let minEventSpeedKmh: Double = 20
    private static let maxEventGapSeconds: TimeInterval = 12
    private static let eventDedupSeconds: TimeInterval = 15
    private static let legacyGapSeconds: TimeInterval = 30

    static func analyze(points: [DrivingRoutePoint]) -> Metrics {
        guard points.count >= 2 else {
            return Metrics(distanceKm: 0, maxSpeedKmh: 0, maxSpeedAt: nil, events: [], harshViolations: [])
        }
        let hasTime = points.allSatisfy { $0.t != nil }
        var distanceM: Double = 0
        var speedKmh: [Double?] = Array(repeating: nil, count: points.count)
        if let v = points[0].v { speedKmh[0] = v * 3.6 }

        for i in 1..<points.count {
            let a = CLLocation(latitude: points[i - 1].latitude, longitude: points[i - 1].longitude)
            let b = CLLocation(latitude: points[i].latitude, longitude: points[i].longitude)
            let d = a.distance(from: b)
            distanceM += d
            if let v = points[i].v {
                speedKmh[i] = v * 3.6
            } else if hasTime, let t0 = points[i - 1].t, let t1 = points[i].t {
                let dt = t1.timeIntervalSince(t0)
                if dt >= 1 { speedKmh[i] = d / dt * 3.6 }
            } else if !hasTime {
                speedKmh[i] = d / legacyGapSeconds * 3.6
            }
        }

        var samples: [Double] = []
        var peak: (speed: Double, at: Date?)?
        for (i, s) in speedKmh.enumerated() {
            guard let s, s.isFinite, s > 0, s <= 160 else { continue }
            samples.append(s)
            if peak == nil || s > peak!.speed { peak = (s, points[i].t) }
        }
        let maxSpeed = FamilyDrivingTripLedger.cappedPeakSpeedKmh(samples)

        var events: [DrivingEvent] = []
        var violations: [DrivingViolation] = []
        if hasTime {
            var lastAt: [DrivingEventType: Date] = [:]
            for i in 1..<points.count {
                guard let t0 = points[i - 1].t, let t1 = points[i].t,
                      let s0 = speedKmh[i - 1], let s1 = speedKmh[i] else { continue }
                let dt = t1.timeIntervalSince(t0)
                guard dt >= 1, dt <= maxEventGapSeconds else { continue }
                let accel = (s1 - s0) / 3.6 / dt
                let type: DrivingEventType
                if accel <= hardBrakeMps2, s0 >= minEventSpeedKmh {
                    type = .braking
                } else if accel >= hardAccelMps2, s1 >= minEventSpeedKmh {
                    type = .acceleration
                } else {
                    continue
                }
                if let prev = lastAt[type], t1.timeIntervalSince(prev) < eventDedupSeconds { continue }
                lastAt[type] = t1
                let magnitude = abs(accel)
                let place = String(format: "%.5f, %.5f", points[i].latitude, points[i].longitude)
                events.append(DrivingEvent(type: type, timestamp: t1, severity: min(1, magnitude / 6), location: place))
                violations.append(DrivingViolation(
                    type: type == .braking ? .harshBraking : .harshAcceleration,
                    timestamp: t1,
                    description: String(format: "%.1f m/s²", magnitude),
                    severity: magnitude >= 4.5 ? .high : .medium
                ))
            }
        }

        return Metrics(
            distanceKm: distanceM / 1000.0,
            maxSpeedKmh: maxSpeed,
            maxSpeedAt: peak?.at,
            events: events,
            harshViolations: violations
        )
    }
}

/// Life360-style «car only»: drop a speed-detected trip when iPhone motion says it was a bike/walk.
/// No Motion permission / no data → keep the trip (never hide a real drive).
enum DriveActivityClassifier {
    struct Segment {
        let start: Date
        let automotive: Bool
        let nonCar: Bool
    }

    static func wasNotDriving(from: Date, to: Date) async -> Bool {
        guard to > from,
              CMMotionActivityManager.isActivityAvailable(),
              CMMotionActivityManager.authorizationStatus() == .authorized else { return false }
        let manager = CMMotionActivityManager()
        let activities: [CMMotionActivity] = await withCheckedContinuation { continuation in
            manager.queryActivityStarting(from: from, to: to, to: OperationQueue()) { list, _ in
                continuation.resume(returning: list ?? [])
            }
        }
        withExtendedLifetime(manager) {}
        let segments = activities
            .filter { $0.confidence != .low }
            .map { Segment(start: $0.startDate, automotive: $0.automotive, nonCar: $0.cycling || $0.walking || $0.running) }
        return isNotDriving(segments, end: to)
    }

    static func isNotDriving(_ segments: [Segment], end: Date) -> Bool {
        let sorted = segments.sorted { $0.start < $1.start }
        guard let first = sorted.first else { return false }
        var automotiveSec: TimeInterval = 0
        var nonCarSec: TimeInterval = 0
        for (i, seg) in sorted.enumerated() {
            let next = i + 1 < sorted.count ? sorted[i + 1].start : end
            let length = max(0, next.timeIntervalSince(seg.start))
            if seg.automotive { automotiveSec += length } else if seg.nonCar { nonCarSec += length }
        }
        let total = max(end.timeIntervalSince(first.start), 1)
        return automotiveSec < 60 && nonCarSec >= total * 0.5
    }
}

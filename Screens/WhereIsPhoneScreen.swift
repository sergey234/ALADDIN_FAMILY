import SwiftUI
import CoreLocation
import MapKit

/// Pay-pains F7–F10: last real point + map, today’s place trail, travel minutes.
/// No continuous Life360-style tracking.
struct WhereIsPhoneScreen: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var placeCount = 0
    @State private var latestEvent: GeofenceDayEvent?
    @State private var todayTrail: [GeofenceDayEvent] = []
    @State private var shares: [WherePhoneShare] = []
    @State private var remoteSignals: [WherePhoneFamilySignal] = []
    @State private var remotePoints: [WherePhoneFamilyPoint] = []
    @State private var isSending = false
    @State private var statusText: String?
    @State private var locatorHint: String?
    @State private var showPlaces = false
    @State private var mapCoordinate: CLLocationCoordinate2D?
    @State private var mapPointName: String?
    @State private var mapPointAt: Date?
    @State private var travelMinutesToday: Int?
    @State private var mapRegion = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 55.75, longitude: 37.62),
        span: MKCoordinateSpan(latitudeDelta: 0.04, longitudeDelta: 0.04)
    )

    @StateObject private var locator = WherePhoneOneShot()

    private struct MapPin: Identifiable {
        let id = UUID()
        let coordinate: CLLocationCoordinate2D
        let title: String
    }

    private var mapPins: [MapPin] {
        guard let coordinate = mapCoordinate else { return [] }
        return [
            MapPin(
                coordinate: coordinate,
                title: mapPointName ?? localizationManager.localized("where_phone_you")
            )
        ]
    }

    private var hideOthers: Bool {
        let role = UserDefaults.standard.string(forKey: "current_user_role") ?? ""
        return role == "child" || role == "teenager"
    }

    private var myMemberId: String {
        (UserDefaults.standard.string(forKey: "your_member_id") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var signalLines: [WherePhoneFamilySignal] {
        WherePhoneFamilyBoard.signals(
            local: latestEvent,
            localName: displayName(),
            localMemberId: myMemberId,
            remote: remoteSignals,
            hideOthers: hideOthers
        )
    }

    private var pointLines: [WherePhoneFamilyPoint] {
        WherePhoneFamilyBoard.points(
            local: shares,
            localMemberId: myMemberId,
            remote: remotePoints,
            hideOthers: hideOthers
        )
    }

    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("where_phone_map_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                mapCard
                placesCard
                trailCard
                shareCard
                lostCard
            }
        }
        .sheet(isPresented: $showPlaces) {
            GeofencesSettingsModal(isPresented: $showPlaces)
                .environmentObject(localizationManager)
        }
        .onAppear(perform: reload)
        .onReceive(NotificationCenter.default.publisher(for: .geofenceDayEventsDidChange)) { _ in
            reload()
        }
        .accessibilityIdentifier("where_phone_screen")
    }

    private var mapCard: some View {
        card(symbol: "map.fill", titleKey: "where_phone_map_card_title") {
            if mapCoordinate != nil {
                // iOS 15+ MapKit (deployment 15.2) — one pin, not a live track.
                Map(coordinateRegion: $mapRegion, annotationItems: mapPins) { pin in
                    MapMarker(coordinate: pin.coordinate, tint: .orange)
                }
                .frame(height: 168)
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                .disabled(true)
                .accessibilityIdentifier("where_phone_map")

                if let at = mapPointAt {
                    Text(
                        String(
                            format: localizationManager.localized("where_phone_map_point_time"),
                            mapPointName ?? localizationManager.localized("where_phone_you"),
                            WherePhoneTime.ago(since: at, localization: localizationManager)
                        )
                    )
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                    .fixedSize(horizontal: false, vertical: true)
                }
            } else {
                Text(localizationManager.localized("where_phone_map_empty"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if let travelMinutesToday, travelMinutesToday > 0 {
                Text(
                    String(
                        format: localizationManager.localized("pay_pains_where_travel_fmt"),
                        travelMinutesToday
                    )
                )
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .accessibilityIdentifier("where_phone_travel_minutes")
            }
        }
    }

    private var trailCard: some View {
        card(symbol: "list.bullet.rectangle", titleKey: "where_phone_trail_title") {
            if todayTrail.isEmpty {
                Text(localizationManager.localized("where_phone_trail_empty"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            } else {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    ForEach(todayTrail) { event in
                        Text(trailLine(event))
                            .font(.subheadline)
                            .foregroundColor(.textPrimary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .accessibilityIdentifier("where_phone_trail")
            }
        }
    }

    private func trailLine(_ event: GeofenceDayEvent) -> String {
        let actionKey = event.isArrival ? "where_phone_signal_arrived" : "where_phone_signal_left"
        let action = String(
            format: localizationManager.localized(actionKey),
            event.regionName
        )
        return "\(event.time) · \(action)"
    }

    private var placesCard: some View {
        card(symbol: "house.fill", titleKey: "where_phone_places_title") {
            if !signalLines.isEmpty {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    ForEach(signalLines) { line in
                        Text(signalText(line))
                            .font(.subheadline)
                            .foregroundColor(.textPrimary)
                            .fixedSize(horizontal: false, vertical: true)
                            .accessibilityIdentifier("where_phone_event")
                    }
                }
            } else if placeCount == 0 {
                actionButton("where_phone_places_empty", id: "where_phone_add_place") {
                    showPlaces = true
                }
            } else {
                Text(placesWaitingLine())
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var shareCard: some View {
        card(symbol: "mappin.circle.fill", titleKey: "where_phone_share_title") {
            Text(localizationManager.localized("where_phone_share_hint_map"))
                .font(.caption)
                .foregroundColor(.textSecondary)

            if !pointLines.isEmpty {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    ForEach(pointLines) { line in
                        Text(personLine(name: line.name, at: line.at))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                            .accessibilityIdentifier("where_phone_share_line")
                    }
                }
            } else {
                Text(localizationManager.localized("where_phone_share_empty"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
            }

            if let statusText {
                Text(statusText)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityIdentifier("where_phone_share_status")
            }

            actionButton(
                isSending ? "where_phone_share_sending" : "where_phone_share_button",
                id: "where_phone_send"
            ) {
                sendPlace()
            }
            .disabled(isSending)
        }
    }

    private var lostCard: some View {
        card(symbol: "iphone", titleKey: "where_phone_lost_title") {
            Text(localizationManager.localized("where_phone_lost_note"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                step("1", "where_phone_lost_step1")
                step("2", "where_phone_lost_step2")
                step("3", "where_phone_lost_step3")
            }
            .accessibilityIdentifier("where_phone_locator_steps")

            actionButton("where_phone_lost_button", id: "where_phone_open_locator") {
                openLocator()
            }

            if let locatorHint {
                Text(locatorHint)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityIdentifier("where_phone_locator_hint")
            }
        }
    }

    private func card<Content: View>(
        symbol: String,
        titleKey: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.s) {
                Image(systemName: symbol)
                    .font(.body.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(width: 28, height: 28)
                Text(localizationManager.localized(titleKey))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            content()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.35))
        .cornerRadius(CornerRadius.medium)
    }

    private func actionButton(_ key: String, id: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(localizationManager.localized(key))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.backgroundDark)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.secondaryGold)
                .cornerRadius(CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier(id)
    }

    private func step(_ number: String, _ key: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: Spacing.s) {
            Text(number)
                .font(.caption.weight(.bold))
                .foregroundColor(.secondaryGold)
                .frame(width: 16)
            Text(localizationManager.localized(key))
                .font(.subheadline)
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private func reload() {
        placeCount = WherePhonePlaceCount.current()
        latestEvent = GeofenceEventStore.events(lastDays: 7).first
        todayTrail = GeofenceEventStore.todayEvents().sorted { $0.createdAt < $1.createdAt }
        travelMinutesToday = WherePhoneTravel.minutesInTransitToday()
        shares = WherePhoneShareStore.load()
        if let last = WherePhoneLastPointStore.load() {
            mapCoordinate = last.coordinate
            mapPointName = last.name
            mapPointAt = last.at
            mapRegion = MKCoordinateRegion(
                center: last.coordinate,
                span: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02)
            )
        } else if let share = shares.first, let lat = share.latitude, let lon = share.longitude {
            let coord = CLLocationCoordinate2D(latitude: lat, longitude: lon)
            mapCoordinate = coord
            mapPointName = share.name
            mapPointAt = share.createdAt
            mapRegion = MKCoordinateRegion(
                center: coord,
                span: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02)
            )
        } else {
            mapCoordinate = nil
            mapPointName = nil
            mapPointAt = nil
        }
        APIService.shared.getFamilyWherePhone { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let snapshot):
                    self.remoteSignals = snapshot.signals
                    self.remotePoints = snapshot.points
                    print("WHERE_PHONE family signals=\(snapshot.signals.count) points=\(snapshot.points.count)")
                case .failure:
                    print("WHERE_PHONE family sync fail")
                }
            }
        }
    }

    private func signalText(_ line: WherePhoneFamilySignal) -> String {
        let actionKey = line.isArrival ? "where_phone_signal_arrived" : "where_phone_signal_left"
        let action = String(
            format: localizationManager.localized(actionKey),
            line.placeName
        )
        return String(
            format: localizationManager.localized("where_phone_event_line"),
            line.name,
            WherePhoneTime.ago(since: line.at, localization: localizationManager),
            action
        )
    }

    private func personLine(name: String, at: Date) -> String {
        String(
            format: localizationManager.localized("where_phone_person_time"),
            name,
            WherePhoneTime.ago(since: at, localization: localizationManager)
        )
    }

    private func displayName() -> String {
        let raw = (UserDefaults.standard.string(forKey: "user_name")
            ?? UserDefaults.standard.string(forKey: "user_display_name")
            ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if !raw.isEmpty, !raw.hasPrefix("MEM_") {
            return raw
        }
        return localizationManager.localized("where_phone_you")
    }

    private func placesWaitingLine() -> String {
        let names = WherePhonePlaceCount.names()
        guard !names.isEmpty else {
            return localizationManager.localized("where_phone_places_none")
        }
        return String(
            format: localizationManager.localized("where_phone_places_waiting"),
            names.joined(separator: ", ")
        )
    }

    private func sendPlace() {
        isSending = true
        statusText = nil
        if let cached = LocationManager.shared.currentLocation,
           abs(cached.timestamp.timeIntervalSinceNow) < 15 * 60 {
            print("WHERE_PHONE send using cached location")
            deliver(cached)
            return
        }
        print("WHERE_PHONE send asking for one location")
        locator.request { result in
            switch result {
            case .failure(let error):
                self.isSending = false
                let ns = error as NSError
                print("WHERE_PHONE send fail domain=\(ns.domain) code=\(ns.code)")
                self.statusText = self.shareFailureText(error)
            case .success(let location):
                print("WHERE_PHONE send ok")
                self.deliver(location)
            }
        }
    }

    private func shareFailureText(_ error: Error) -> String {
        if case WherePhoneLocationError.denied = error {
            return localizationManager.localized("where_phone_share_denied")
        }
        let ns = error as NSError
        if ns.domain == kCLErrorDomain, ns.code == CLError.denied.rawValue {
            return localizationManager.localized("where_phone_share_denied")
        }
        return localizationManager.localized("where_phone_share_no_gps")
    }

    private func deliver(_ location: CLLocation) {
        isSending = false
        let name = displayName()
        let lat = location.coordinate.latitude
        let lon = location.coordinate.longitude
        WherePhoneShareStore.add(name: name, isMine: true, latitude: lat, longitude: lon)
        WherePhoneLastPointStore.save(name: name, latitude: lat, longitude: lon)
        shares = WherePhoneShareStore.load()
        mapCoordinate = location.coordinate
        mapPointName = name
        mapPointAt = Date()
        mapRegion = MKCoordinateRegion(
            center: location.coordinate,
            span: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02)
        )
        statusText = localizationManager.localized("where_phone_share_sent")
        let mapURL = String(
            format: "https://maps.apple.com/?ll=%f,%f",
            lat,
            lon
        )
        let line = String(
            format: localizationManager.localized("where_phone_chat_line"),
            name,
            mapURL
        )
        Task {
            _ = await FamilyAutoAlertSender.send(
                FamilyAutoAlertEvent(
                    kind: .imOk,
                    displayName: name,
                    legacyPlaintext: line
                ),
                localization: localizationManager
            )
        }
        APIService.shared.postFamilyWherePhonePoint(displayName: name, mapURL: mapURL) { result in
            if case .success(true) = result {
                print("WHERE_PHONE family point saved")
            } else {
                print("WHERE_PHONE family point save fail")
            }
        }
    }

    private func openLocator() {
        #if targetEnvironment(simulator)
        print("WHERE_PHONE locator skipped: simulator has no Find My app")
        locatorHint = localizationManager.localized("where_phone_lost_manual")
        return
        #else
        locatorHint = nil
        guard let url = URL(string: "findmy://") else {
            print("WHERE_PHONE locator url invalid")
            locatorHint = localizationManager.localized("where_phone_lost_manual")
            return
        }
        print("WHERE_PHONE locator open")
        UIApplication.shared.open(url, options: [:]) { opened in
            DispatchQueue.main.async {
                print("WHERE_PHONE locator opened=\(opened)")
                locatorHint = opened ? nil : localizationManager.localized("where_phone_lost_manual")
            }
        }
        #endif
    }
}

enum WherePhonePlaceCount {
    static func names() -> [String] {
        guard let data = UserDefaults.standard.data(forKey: "geofences_settings"),
              let items = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) else {
            return []
        }
        return items.filter(\.isActive).map(\.name).filter { !$0.isEmpty }
    }

    static func current() -> Int {
        names().count
    }
}

struct WherePhoneShare: Codable, Identifiable, Equatable {
    let id: String
    let name: String
    let createdAt: Date
    let isMine: Bool
    let latitude: Double?
    let longitude: Double?
}

enum WherePhoneShareStore {
    private static let key = "aladdin_where_phone_shares_v1"
    private static let maxCount = 20

    static func load() -> [WherePhoneShare] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let items = try? JSONDecoder().decode([WherePhoneShare].self, from: data) else {
            return []
        }
        return items.sorted { $0.createdAt > $1.createdAt }
    }

    static func add(
        name: String,
        isMine: Bool,
        latitude: Double? = nil,
        longitude: Double? = nil,
        now: Date = Date()
    ) {
        var items = load()
        items.insert(
            WherePhoneShare(
                id: UUID().uuidString,
                name: name,
                createdAt: now,
                isMine: isMine,
                latitude: latitude,
                longitude: longitude
            ),
            at: 0
        )
        if items.count > maxCount {
            items = Array(items.prefix(maxCount))
        }
        if let data = try? JSONEncoder().encode(items) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }

    static func visible(_ shares: [WherePhoneShare], hideOthers: Bool) -> [WherePhoneShare] {
        let sorted = shares.sorted { $0.createdAt > $1.createdAt }
        guard hideOthers else { return sorted }
        return sorted.filter(\.isMine)
    }
}

/// Last real map pin for F7 (one point, not a live track).
enum WherePhoneLastPointStore {
    private static let key = "aladdin_where_phone_last_point_v1"

    struct Point: Codable {
        let name: String
        let latitude: Double
        let longitude: Double
        let at: Date
    }

    static func save(name: String, latitude: Double, longitude: Double, at: Date = Date()) {
        let point = Point(name: name, latitude: latitude, longitude: longitude, at: at)
        if let data = try? JSONEncoder().encode(point) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }

    static func load() -> (coordinate: CLLocationCoordinate2D, name: String, at: Date)? {
        guard let data = UserDefaults.standard.data(forKey: key),
              let point = try? JSONDecoder().decode(Point.self, from: data) else {
            return nil
        }
        return (
            CLLocationCoordinate2D(latitude: point.latitude, longitude: point.longitude),
            point.name,
            point.at
        )
    }
}

/// F10: closed departure→arrival legs today only. No invented trips.
enum WherePhoneTravel {
    static func minutesInTransitToday() -> Int? {
        let events = GeofenceEventStore.todayEvents().sorted { $0.createdAt < $1.createdAt }
        guard !events.isEmpty else { return nil }
        var total: TimeInterval = 0
        var lastDeparture: Date?
        for event in events {
            if !event.isArrival {
                lastDeparture = event.createdAt
            } else if let dep = lastDeparture {
                let delta = event.createdAt.timeIntervalSince(dep)
                if delta > 0, delta < 12 * 60 * 60 {
                    total += delta
                }
                lastDeparture = nil
            }
        }
        let minutes = Int(total / 60)
        return minutes > 0 ? minutes : nil
    }
}

enum WherePhoneTime {
    static func ago(since date: Date, localization: LocalizationManager, now: Date = Date()) -> String {
        let minutes = max(0, Int(now.timeIntervalSince(date) / 60))
        if minutes < 1 {
            return localization.localized("where_phone_ago_now")
        }
        if minutes < 60 {
            return String(format: localization.localized("where_phone_ago_min"), minutes)
        }
        let hours = minutes / 60
        if hours < 24 {
            return String(format: localization.localized("where_phone_ago_hour"), hours)
        }
        return String(format: localization.localized("where_phone_ago_day"), hours / 24)
    }
}

private final class WherePhoneOneShot: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var completion: ((Result<CLLocation, Error>) -> Void)?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
    }

    func request(_ completion: @escaping (Result<CLLocation, Error>) -> Void) {
        self.completion = completion
        didAsk = false
        guard CLLocationManager.locationServicesEnabled() else {
            finish(.failure(WherePhoneLocationError.unavailable))
            return
        }
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            askOnce()
        case .notDetermined:
            print("WHERE_PHONE waiting for location permission")
            manager.requestWhenInUseAuthorization()
        case .restricted, .denied:
            finish(.failure(WherePhoneLocationError.denied))
        @unknown default:
            finish(.failure(WherePhoneLocationError.unavailable))
        }
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        guard completion != nil else { return }
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            askOnce()
        case .restricted, .denied:
            finish(.failure(WherePhoneLocationError.denied))
        default:
            break
        }
    }

    private var didAsk = false

    private func askOnce() {
        guard !didAsk else { return }
        didAsk = true
        print("WHERE_PHONE requestLocation")
        manager.requestLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else {
            finish(.failure(WherePhoneLocationError.unavailable))
            return
        }
        finish(.success(location))
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        finish(.failure(error))
    }

    private func finish(_ result: Result<CLLocation, Error>) {
        let callback = completion
        completion = nil
        DispatchQueue.main.async {
            callback?(result)
        }
    }
}

private enum WherePhoneLocationError: Error {
    case denied
    case unavailable
}

struct WherePhoneFamilySignal: Identifiable, Equatable {
    let memberId: String
    let name: String
    let placeName: String
    let isArrival: Bool
    let at: Date
    var id: String { memberId }
}

struct WherePhoneFamilyPoint: Identifiable, Equatable {
    let memberId: String
    let name: String
    let at: Date
    var id: String { memberId }
}

struct WherePhoneFamilySnapshot {
    let signals: [WherePhoneFamilySignal]
    let points: [WherePhoneFamilyPoint]
}

struct FamilyWherePhoneAPIResponse: Codable {
    let ok: Bool
    let signals: [FamilyWherePhoneSignalDTO]
    let points: [FamilyWherePhonePointDTO]

    func snapshot() -> WherePhoneFamilySnapshot {
        WherePhoneFamilySnapshot(
            signals: signals.compactMap { $0.signal() },
            points: points.compactMap { $0.point() }
        )
    }
}

struct FamilyWherePhoneSignalDTO: Codable {
    let memberId: String
    let displayName: String
    let placeName: String
    let isArrival: Bool
    let happenedAt: String?

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case displayName = "display_name"
        case placeName = "place_name"
        case isArrival = "is_arrival"
        case happenedAt = "happened_at"
    }

    func signal() -> WherePhoneFamilySignal? {
        guard let at = WherePhoneISO.date(from: happenedAt) else { return nil }
        return WherePhoneFamilySignal(
            memberId: memberId,
            name: displayName,
            placeName: placeName,
            isArrival: isArrival,
            at: at
        )
    }
}

struct FamilyWherePhonePointDTO: Codable {
    let memberId: String
    let displayName: String
    let happenedAt: String?

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case displayName = "display_name"
        case happenedAt = "happened_at"
    }

    func point() -> WherePhoneFamilyPoint? {
        guard let at = WherePhoneISO.date(from: happenedAt) else { return nil }
        return WherePhoneFamilyPoint(memberId: memberId, name: displayName, at: at)
    }
}

enum WherePhoneISO {
    static func date(from raw: String?) -> Date? {
        guard let raw, !raw.isEmpty else { return nil }
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = iso.date(from: raw) { return date }
        iso.formatOptions = [.withInternetDateTime]
        return iso.date(from: raw)
    }
}

enum WherePhoneFamilyBoard {
    static func signals(
        local: GeofenceDayEvent?,
        localName: String,
        localMemberId: String,
        remote: [WherePhoneFamilySignal],
        hideOthers: Bool
    ) -> [WherePhoneFamilySignal] {
        var byId: [String: WherePhoneFamilySignal] = [:]
        let mine = localMemberId.isEmpty ? "self" : localMemberId
        for row in remote {
            if hideOthers, row.memberId != mine { continue }
            byId[row.memberId] = newer(byId[row.memberId], row)
        }
        if let local {
            let row = WherePhoneFamilySignal(
                memberId: mine,
                name: localName,
                placeName: local.regionName,
                isArrival: local.isArrival,
                at: local.createdAt
            )
            byId[mine] = newer(byId[mine], row)
        }
        return byId.values.sorted { $0.at > $1.at }
    }

    static func points(
        local: [WherePhoneShare],
        localMemberId: String,
        remote: [WherePhoneFamilyPoint],
        hideOthers: Bool
    ) -> [WherePhoneFamilyPoint] {
        var byId: [String: WherePhoneFamilyPoint] = [:]
        let mine = localMemberId.isEmpty ? "self" : localMemberId
        for row in remote {
            if hideOthers, row.memberId != mine { continue }
            byId[row.memberId] = newer(byId[row.memberId], row)
        }
        if let localMine = local.first {
            let row = WherePhoneFamilyPoint(memberId: mine, name: localMine.name, at: localMine.createdAt)
            byId[mine] = newer(byId[mine], row)
        }
        return byId.values.sorted { $0.at > $1.at }
    }

    private static func newer(_ left: WherePhoneFamilySignal?, _ right: WherePhoneFamilySignal) -> WherePhoneFamilySignal {
        guard let left else { return right }
        return right.at >= left.at ? right : left
    }

    private static func newer(_ left: WherePhoneFamilyPoint?, _ right: WherePhoneFamilyPoint) -> WherePhoneFamilyPoint {
        guard let left else { return right }
        return right.at >= left.at ? right : left
    }
}

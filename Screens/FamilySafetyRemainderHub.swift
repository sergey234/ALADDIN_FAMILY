import SwiftUI
import UIKit
import CoreLocation
import MapKit
import EventKit

// MARK: - GATES (100% remainder, no Figma, no P4)
// G1 Live points = Core Location only (no fake pins)
// G2 Pet wizard = profile+routines; no live GPS pet layer
// G3 SOS hold → local family notify; no «помощь едет»
// G4 Wave A empties = honest soon / settings links
// G5 Loc via localized() keys already in strings

// MARK: - Live location (B-depth)

@MainActor
final class FamilyMapLiveLocationController: NSObject, ObservableObject, CLLocationManagerDelegate {
    static let shared = FamilyMapLiveLocationController()

    @Published var coordinate: CLLocationCoordinate2D?
    @Published var speedKmh: Int?
    @Published var updatedAt: Date?
    /// QA-08: horizontal accuracy in meters (−1 = unknown).
    @Published var accuracyMeters: Double = -1
    @Published var authStatus: CLAuthorizationStatus = .notDetermined

    private let manager = CLLocationManager()
    private var active = false

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.distanceFilter = 15
        authStatus = manager.authorizationStatus
    }

    /// Continuous live GPS: Always Allow **and** Family+ / trial / premium (not Free/Personal).
    var isLiveEntitled: Bool { FamilyMapLiveAccess.isEntitled }

    func startIfNeeded() {
        active = true
        authStatus = manager.authorizationStatus
        guard FamilyMapLiveAccess.isEntitled else {
            manager.stopUpdatingLocation()
            return
        }
        switch authStatus {
        case .authorizedAlways:
            // Свежая точка при открытой карте; в фоне — significant-change через LocationManager.
            manager.startUpdatingLocation()
            LocationManager.shared.startSignificantLocationChanges()
            Task { await GeofenceMonitoringBootstrap.reloadIfNeeded() }
        case .authorizedWhenInUse:
            // Пока нет доступа при закрытом приложении: last-point / one-shot share.
            manager.stopUpdatingLocation()
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        default:
            manager.stopUpdatingLocation()
        }
    }

    func stop() {
        active = false
        manager.stopUpdatingLocation()
    }

    /// QA-08 A: one-shot refresh («Обновить моё место»).
    func requestFreshFix() {
        authStatus = manager.authorizationStatus
        guard authStatus == .authorizedAlways || authStatus == .authorizedWhenInUse else {
            manager.requestWhenInUseAuthorization()
            return
        }
        manager.requestLocation()
        if FamilyMapLiveAccess.isEntitled, authStatus == .authorizedAlways {
            manager.startUpdatingLocation()
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        Task { @MainActor in
            self.authStatus = manager.authorizationStatus
            guard self.active, FamilyMapLiveAccess.isEntitled else {
                manager.stopUpdatingLocation()
                return
            }
            if manager.authorizationStatus == .authorizedAlways {
                manager.startUpdatingLocation()
                LocationManager.shared.startSignificantLocationChanges()
            } else {
                manager.stopUpdatingLocation()
            }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let loc = locations.last else { return }
        Task { @MainActor in
            guard FamilyMapLiveAccess.isEntitled else { return }
            self.coordinate = loc.coordinate
            self.updatedAt = loc.timestamp
            self.accuracyMeters = loc.horizontalAccuracy
            // Real CL only; drop invalid / GPS spikes. UI also caps at 140 — 181 km/h was a spike.
            let kmh = loc.speed * 3.6
            let speedOK = loc.speedAccuracy < 0 || loc.speedAccuracy <= 8
            if loc.speed >= 0,
               loc.horizontalAccuracy >= 0,
               loc.horizontalAccuracy < 40,
               speedOK,
               kmh <= 140 {
                self.speedKmh = Int(kmh.rounded())
            } else {
                self.speedKmh = nil
            }
            // Тихая зона + авто-поездка + серверный last-point (единый путь).
            if FamilyMapQuietZoneStore.allowsFamilyShare(loc) {
                LocationManager.shared.reportCurrentLocation(loc)
            } else {
                // Не шлём; локальный pin на карте всё равно может показать «тихая зона».
            }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("FamilyMapLiveLocation: \(error.localizedDescription)")
    }
}

/// Live map entitlement: trial · family · premium. Free/Personal = last-point + share only.
enum FamilyMapLiveAccess {
    @MainActor
    static var isEntitled: Bool {
        if SubscriptionManager.shared.trialStatus?.isActive == true { return true }
        switch SubscriptionManager.shared.getCurrentLevel() {
        case .trial, .family, .premium:
            return true
        case .free, .personal:
            return false
        }
    }
}

// Quiet zone store: Core/Family/FamilyMapQuietZoneStore.swift

// MARK: - Share link duration (B-depth)

enum FamilyMapShareDuration: Int, CaseIterable, Identifiable {
    case oneHour = 1
    case eightHours = 8
    case twentyFour = 24
    var id: Int { rawValue }
    var titleKey: String {
        switch self {
        case .oneHour: return "map_share_dur_1h"
        case .eightHours: return "map_share_dur_8h"
        case .twentyFour: return "map_share_dur_24h"
        }
    }
}

enum FamilyMapShareSessionStore {
    private static let hoursKey = "where_phone_share_duration_hours_v1"
    private static let expiresKey = "where_phone_share_expires_at_v1"

    static var selectedHours: Int {
        get {
            let v = UserDefaults.standard.integer(forKey: hoursKey)
            return v > 0 ? v : FamilyMapShareDuration.oneHour.rawValue
        }
        set { UserDefaults.standard.set(newValue, forKey: hoursKey) }
    }

    static var expiresAt: Date? {
        get {
            let ts = UserDefaults.standard.double(forKey: expiresKey)
            return ts > 0 ? Date(timeIntervalSince1970: ts) : nil
        }
        set {
            if let newValue {
                UserDefaults.standard.set(newValue.timeIntervalSince1970, forKey: expiresKey)
            } else {
                UserDefaults.standard.removeObject(forKey: expiresKey)
            }
        }
    }

    static var isActive: Bool {
        guard let exp = expiresAt else { return false }
        return exp > Date()
    }

    static func beginSession(hours: Int, now: Date = Date()) {
        selectedHours = hours
        expiresAt = now.addingTimeInterval(TimeInterval(hours) * 3600)
    }

    static func endSession() {
        expiresAt = nil
    }
}

// MARK: - Life360-style live map (one MKMapView for screen lifetime)

/// UIKit host: single `MKMapView` pinned to edges. Sheet overlay in SwiftUI must NEVER
/// change this view’s frame — only slide over it. Interaction toggles with sheet detent.
final class FamilyHubLiveMapViewController: UIViewController, MKMapViewDelegate {
    let mapView = MKMapView(frame: .zero)
    var onRegionChangedByUser: ((MKCoordinateRegion) -> Void)?
    /// P0-3: tap avatar pin → open member sheet (Life360).
    var onPinSelected: (() -> Void)?

    private var pinDiameter: CGFloat = 36
    private var lastRegion = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 0, longitude: 0),
        span: MKCoordinateSpan(latitudeDelta: 0, longitudeDelta: 0)
    )
    private var lastPinLat: Double?
    private var lastPinLon: Double?
    private var lastPinTitle = ""
    private var lastAppliedPinDiameter: CGFloat = -1
    private var lastMapTypeRaw = ""
    private var isProgrammaticRegionChange = false

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black
        mapView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(mapView)
        NSLayoutConstraint.activate([
            mapView.topAnchor.constraint(equalTo: view.topAnchor),
            mapView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            mapView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            mapView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
        mapView.delegate = self
        mapView.isRotateEnabled = false
        mapView.isPitchEnabled = false
        mapView.showsCompass = false
        mapView.pointOfInterestFilter = .includingAll
    }

    private var lastQuietRadius: CLLocationDistance = -1

    /// Cheap apply — skip MapKit work unless inputs actually changed.
    func apply(
        region: MKCoordinateRegion,
        coordinate: CLLocationCoordinate2D?,
        title: String,
        mapTypeRaw: String,
        pinDiameter: CGFloat,
        interactionEnabled: Bool,
        forceCamera: Bool,
        quietRadiusMeters: CLLocationDistance = 0
    ) {
        self.pinDiameter = pinDiameter
        mapView.isScrollEnabled = interactionEnabled
        mapView.isZoomEnabled = interactionEnabled

        if mapTypeRaw != lastMapTypeRaw {
            lastMapTypeRaw = mapTypeRaw
            switch mapTypeRaw {
            case "satellite": mapView.mapType = .satellite
            case "street": mapView.mapType = .standard
            default: mapView.mapType = .mutedStandard
            }
        }

        let regionChanged =
            forceCamera
            || abs(lastRegion.center.latitude - region.center.latitude) > 0.00005
            || abs(lastRegion.center.longitude - region.center.longitude) > 0.00005
            || abs(lastRegion.span.latitudeDelta - region.span.latitudeDelta) > 0.0002
            || abs(lastRegion.span.longitudeDelta - region.span.longitudeDelta) > 0.0002
        if regionChanged {
            isProgrammaticRegionChange = true
            mapView.setRegion(region, animated: forceCamera)
            lastRegion = region
            DispatchQueue.main.async { [weak self] in
                self?.isProgrammaticRegionChange = false
            }
        }

        let lat = coordinate?.latitude
        let lon = coordinate?.longitude
        let pinChanged =
            lat != lastPinLat
            || lon != lastPinLon
            || title != lastPinTitle
            || abs(pinDiameter - lastAppliedPinDiameter) > 0.5
        if pinChanged || forceCamera {
            lastPinLat = lat
            lastPinLon = lon
            lastPinTitle = title
            lastAppliedPinDiameter = pinDiameter
            mapView.removeAnnotations(mapView.annotations.filter { !($0 is MKUserLocation) })
            if let coordinate {
                let pin = MKPointAnnotation()
                pin.coordinate = coordinate
                pin.title = title
                mapView.addAnnotation(pin)
            }
        }

        // HUB-P1.8 — optional quiet-zone circle around pin (Life360 purple circle).
        let quietChanged =
            abs(quietRadiusMeters - lastQuietRadius) > 0.5
            || pinChanged
            || forceCamera
        if quietChanged {
            lastQuietRadius = quietRadiusMeters
            mapView.removeOverlays(mapView.overlays.filter { $0 is MKCircle })
            if let coordinate, quietRadiusMeters >= 50 {
                let circle = MKCircle(center: coordinate, radius: quietRadiusMeters)
                mapView.addOverlay(circle)
            }
        }
    }

    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        if annotation is MKUserLocation { return nil }
        let id = "family_hub_avatar_pin"
        let view = (mapView.dequeueReusableAnnotationView(withIdentifier: id) as? FamilyHubAvatarPinView)
            ?? FamilyHubAvatarPinView(annotation: annotation, reuseIdentifier: id)
        view.annotation = annotation
        view.apply(size: pinDiameter, title: annotation.title ?? nil)
        return view
    }

    func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
        if let circle = overlay as? MKCircle {
            let r = MKCircleRenderer(circle: circle)
            // Quiet-zone: gold (не Life360 purple) — P0 2026-11-11
            r.fillColor = UIColor(red: 0.961, green: 0.620, blue: 0.043, alpha: 0.18) // #F59E0B
            r.strokeColor = UIColor(red: 0.961, green: 0.620, blue: 0.043, alpha: 0.85)
            r.lineWidth = 2
            return r
        }
        return MKOverlayRenderer(overlay: overlay)
    }

    func mapView(_ mapView: MKMapView, regionDidChangeAnimated animated: Bool) {
        guard !isProgrammaticRegionChange else { return }
        lastRegion = mapView.region
        onRegionChangedByUser?(mapView.region)
    }

    func mapView(_ mapView: MKMapView, didSelect view: MKAnnotationView) {
        guard !(view.annotation is MKUserLocation) else { return }
        onPinSelected?()
        if let annotation = view.annotation {
            mapView.deselectAnnotation(annotation, animated: false)
        }
    }
}

/// SwiftUI bridge — one VC / one MKMapView for the life of the representable.
struct FamilyHubLiveMapRepresentable: UIViewControllerRepresentable {
    @Binding var region: MKCoordinateRegion
    var coordinate: CLLocationCoordinate2D?
    var title: String
    var mapTypeRaw: String
    var pinDiameter: CGFloat = 36
    /// Peek/half sheet → map pan/zoom on. Large sheet or drag → map gestures off.
    var interactionEnabled: Bool
    /// Bump (e.g. locate FAB) to force camera without waiting for epsilon.
    var cameraToken: Int = 0
    /// HUB-P1.8 — quiet-zone radius in meters (0 = hide circle).
    var quietRadiusMeters: CLLocationDistance = 0
    var onPinSelected: (() -> Void)? = nil

    func makeUIViewController(context: Context) -> FamilyHubLiveMapViewController {
        let vc = FamilyHubLiveMapViewController()
        let coordinator = context.coordinator
        vc.onRegionChangedByUser = { newRegion in
            coordinator.parent.region = newRegion
        }
        vc.onPinSelected = {
            coordinator.parent.onPinSelected?()
        }
        return vc
    }

    func updateUIViewController(_ vc: FamilyHubLiveMapViewController, context: Context) {
        context.coordinator.parent = self
        let force = context.coordinator.lastCameraToken != cameraToken
        context.coordinator.lastCameraToken = cameraToken
        let coordinator = context.coordinator
        vc.onRegionChangedByUser = { newRegion in
            coordinator.parent.region = newRegion
        }
        vc.onPinSelected = {
            coordinator.parent.onPinSelected?()
        }
        vc.apply(
            region: region,
            coordinate: coordinate,
            title: title,
            mapTypeRaw: mapTypeRaw,
            pinDiameter: pinDiameter,
            interactionEnabled: interactionEnabled,
            forceCamera: force,
            quietRadiusMeters: quietRadiusMeters
        )
    }

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    final class Coordinator {
        var parent: FamilyHubLiveMapRepresentable
        var lastCameraToken: Int = -1
        init(_ parent: FamilyHubLiveMapRepresentable) { self.parent = parent }
    }
}

/// Snapshot fallback (Reduce Motion / offline tile fail) — not primary Life360 path.
struct FamilyHubMapSnapshotView: View {
    var center: CLLocationCoordinate2D
    var span: MKCoordinateSpan
    var mapTypeRaw: String
    var pinTitle: String?
    var pinDiameter: CGFloat = 36
    var showPin: Bool

    @State private var image: UIImage?
    @State private var renderToken = UUID()

    private var renderKey: String {
        String(
            format: "%.5f,%.5f,%.4f,%.4f,%@,%.0f,%d",
            center.latitude, center.longitude,
            span.latitudeDelta, span.longitudeDelta,
            mapTypeRaw, pinDiameter, showPin ? 1 : 0
        )
    }

    var body: some View {
        GeometryReader { geo in
            ZStack {
                if let image {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(width: geo.size.width, height: geo.size.height)
                        .clipped()
                } else {
                    Color.backgroundMedium.opacity(0.55)
                    ProgressView().tint(Color.secondaryGold)
                }
                if showPin {
                    FamilyHubSwiftUIPin(title: pinTitle, diameter: pinDiameter)
                        .offset(y: -pinDiameter * 0.15)
                }
            }
            .onAppear { scheduleRender(size: geo.size) }
            .onChange(of: renderKey) { _ in scheduleRender(size: geo.size) }
            .onChange(of: geo.size.width) { _ in scheduleRender(size: geo.size) }
            .onChange(of: geo.size.height) { _ in scheduleRender(size: geo.size) }
        }
    }

    private func scheduleRender(size: CGSize) {
        guard size.width > 8, size.height > 8 else { return }
        let token = UUID()
        renderToken = token
        let options = MKMapSnapshotter.Options()
        options.region = MKCoordinateRegion(center: center, span: span)
        options.size = size
        options.scale = UIScreen.main.scale
        switch mapTypeRaw {
        case "satellite": options.mapType = .satellite
        case "street": options.mapType = .standard
        default: options.mapType = .mutedStandard
        }
        MKMapSnapshotter(options: options).start { snapshot, _ in
            guard let snapshot else { return }
            DispatchQueue.main.async {
                guard token == renderToken else { return }
                image = snapshot.image
            }
        }
    }
}

struct FamilyHubSwiftUIPin: View {
    var title: String?
    var diameter: CGFloat

    var body: some View {
        let d = max(24, min(56, diameter))
        let letter: String = {
            if let c = title?.trimmingCharacters(in: .whitespacesAndNewlines).first {
                return String(c).uppercased()
            }
            return "·"
        }()
        Text(letter)
            .font(.system(size: d * 0.38, weight: .bold))
            .foregroundColor(.secondaryGold)
            .frame(width: d, height: d)
            .background(Color.backgroundMedium)
            .clipShape(Circle())
            .overlay(Circle().stroke(Color.secondaryGold, lineWidth: 2))
            .accessibilityHidden(true)
    }
}

/// Circular avatar-style pin on live MKMapView. S29: photo when present, else letter.
private final class FamilyHubAvatarPinView: MKAnnotationView {
    private let bubble = UILabel()
    private let ring = UIView()
    private let photoView = UIImageView()
    private static let breatheKey = "aladdin_pin_breathe"

    override init(annotation: MKAnnotation?, reuseIdentifier: String?) {
        super.init(annotation: annotation, reuseIdentifier: reuseIdentifier)
        clusteringIdentifier = nil
        canShowCallout = false
        isEnabled = true
        ring.backgroundColor = UIColor(Color.backgroundMedium)
        ring.layer.borderColor = UIColor(Color.secondaryGold).cgColor
        ring.layer.borderWidth = 2
        ring.clipsToBounds = true
        addSubview(ring)
        photoView.contentMode = .scaleAspectFill
        photoView.clipsToBounds = true
        photoView.isHidden = true
        ring.addSubview(photoView)
        bubble.textAlignment = .center
        bubble.textColor = UIColor(Color.secondaryGold)
        bubble.font = .systemFont(ofSize: 14, weight: .bold)
        ring.addSubview(bubble)
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(reduceMotionChanged),
            name: UIAccessibility.reduceMotionStatusDidChangeNotification,
            object: nil
        )
    }

    required init?(coder aDecoder: NSCoder) { nil }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window == nil {
            stopBreathe()
        } else {
            startBreatheIfNeeded()
        }
    }

    @objc private func reduceMotionChanged() {
        startBreatheIfNeeded()
    }

    func apply(size: CGFloat, title: String?) {
        // P4: L=56; cap 64 so breathe ±8% не обрезается layout-ом.
        let d = max(24, min(64, size))
        frame = CGRect(x: 0, y: 0, width: d, height: d)
        centerOffset = CGPoint(x: 0, y: -d / 4)
        ring.frame = bounds
        ring.layer.cornerRadius = d / 2
        photoView.frame = bounds
        photoView.layer.cornerRadius = d / 2
        bubble.frame = bounds
        bubble.font = .systemFont(ofSize: d * 0.38, weight: .bold)
        // Prefer cropped profile photo (same store as AvatarCropEditor).
        if let image = ProfileImageManager.shared.loadProfileImage(for: .main) {
            photoView.image = image
            photoView.isHidden = false
            bubble.isHidden = true
        } else {
            photoView.image = nil
            photoView.isHidden = true
            bubble.isHidden = false
            let letter = (title?.trimmingCharacters(in: .whitespacesAndNewlines).first).map(String.init) ?? "·"
            bubble.text = letter.uppercased()
        }
        startBreatheIfNeeded()
    }

    /// P4.2: «дышит» ±8%, цикл 1.8 с. Не трогает GPS / quiet-zone meters.
    private func startBreatheIfNeeded() {
        if UIAccessibility.isReduceMotionEnabled || window == nil {
            stopBreathe()
            return
        }
        guard ring.layer.animation(forKey: Self.breatheKey) == nil else { return }
        let anim = CABasicAnimation(keyPath: "transform.scale")
        anim.fromValue = 1.0
        anim.toValue = 1.08
        anim.duration = 0.9
        anim.autoreverses = true
        anim.repeatCount = .infinity
        anim.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        ring.layer.add(anim, forKey: Self.breatheKey)
    }

    private func stopBreathe() {
        ring.layer.removeAnimation(forKey: Self.breatheKey)
        ring.layer.transform = CATransform3DIdentity
    }
}

/// Compatibility wrapper around the Life360 live host.
struct FamilyHubMapKitView: View {
    @Binding var region: MKCoordinateRegion
    var coordinate: CLLocationCoordinate2D?
    var title: String
    var mapTypeRaw: String
    var pinDiameter: CGFloat = 36
    var interactionEnabled: Bool = true
    var cameraToken: Int = 0

    var body: some View {
        FamilyHubLiveMapRepresentable(
            region: $region,
            coordinate: coordinate,
            title: title,
            mapTypeRaw: mapTypeRaw,
            pinDiameter: pinDiameter,
            interactionEnabled: interactionEnabled,
            cameraToken: cameraToken
        )
    }
}

// MARK: - Local pet profile (01i — no live GPS)

struct FamilyPetProfile: Codable, Identifiable, Equatable {
    var id: UUID
    var name: String
    var breed: String
    var notes: String
    var walkReminder: Bool
    var feedReminder: Bool
    var medicineReminder: Bool
    /// Wave B H15: `dog` | `cat` | `other` — optional for older local saves.
    var kind: String

    enum CodingKeys: String, CodingKey {
        case id, name, breed, notes, walkReminder, feedReminder, medicineReminder, kind
    }

    init(
        id: UUID,
        name: String,
        breed: String,
        notes: String,
        walkReminder: Bool,
        feedReminder: Bool,
        medicineReminder: Bool,
        kind: String = "dog"
    ) {
        self.id = id
        self.name = name
        self.breed = breed
        self.notes = notes
        self.walkReminder = walkReminder
        self.feedReminder = feedReminder
        self.medicineReminder = medicineReminder
        self.kind = kind
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(UUID.self, forKey: .id)
        name = try c.decode(String.self, forKey: .name)
        breed = try c.decode(String.self, forKey: .breed)
        notes = try c.decode(String.self, forKey: .notes)
        walkReminder = try c.decode(Bool.self, forKey: .walkReminder)
        feedReminder = try c.decode(Bool.self, forKey: .feedReminder)
        medicineReminder = try c.decode(Bool.self, forKey: .medicineReminder)
        kind = try c.decodeIfPresent(String.self, forKey: .kind) ?? "dog"
    }

    var heroAssetName: String {
        switch kind {
        case "cat": return "ICON_ALIVE_HERO_H15_PetCat"
        case "other": return "ICON_ALIVE_HERO_H15_PetOther"
        default: return "ICON_ALIVE_HERO_H15_PetDog"
        }
    }
}

enum FamilyPetProfileStore {
    private static let key = "family_pet_profiles_v1"

    static func load() -> [FamilyPetProfile] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let rows = try? JSONDecoder().decode([FamilyPetProfile].self, from: data) else {
            return []
        }
        return rows
    }

    static func save(_ rows: [FamilyPetProfile]) {
        if let data = try? JSONEncoder().encode(rows) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }

    static func append(_ pet: FamilyPetProfile) {
        var rows = load()
        rows.append(pet)
        save(rows)
    }
}

// MARK: - Pin preview (B-depth)

struct FamilyMapPinPreviewSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("where_phone_pin_preview_done") private var previewDone = true
    /// QA-15 / P4: default L (56pt). Sheet retired from hub onAppear.
    @AppStorage("where_phone_pin_size") private var pinSizeRaw: String = "L"

    private var previewDiameter: CGFloat {
        switch pinSizeRaw {
        case "S": return 28
        case "L": return 56
        default: return 36
        }
    }

    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.m) {
                ZStack {
                    Circle()
                        .fill(Color.backgroundMedium)
                        .frame(width: previewDiameter, height: previewDiameter)
                        .overlay(Circle().stroke(Color.secondaryGold, lineWidth: 2))
                    Text("A")
                        .font(.system(size: previewDiameter * 0.38, weight: .bold))
                        .foregroundColor(.secondaryGold)
                }
                .padding(.top, Spacing.m)
                Text(localizationManager.localized("map_pin_preview_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                Text(localizationManager.localized("map_pin_preview_body"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                Text(localizationManager.localized("map_pin_size_title"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.textSecondary)
                HStack(spacing: Spacing.s) {
                    ForEach(["S", "M", "L"], id: \.self) { size in
                        Button {
                            pinSizeRaw = size
                        } label: {
                            Text(localizationManager.localized("map_pin_size_\(size.lowercased())"))
                                .font(.subheadline.weight(.semibold))
                                .foregroundColor(pinSizeRaw == size ? .backgroundDark : .textPrimary)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .background(pinSizeRaw == size ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("map_pin_size_\(size)")
                    }
                }
                Button {
                    previewDone = true
                    isPresented = false
                } label: {
                    Text(localizationManager.localized("map_pin_preview_ok"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
                Spacer()
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                previewDone = true
                isPresented = false
            })
        }
    }
}

// MARK: - Invite / role (B-depth 01f)

struct FamilyMapInviteRoleSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    var onPicked: (String) -> Void

    private let roles: [(key: String, id: String)] = [
        ("map_role_mom", "mom"),
        ("map_role_dad", "dad"),
        ("map_role_child", "child")
    ]

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_role_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("map_create_circle_teaser"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.textSecondary)
                ForEach(roles, id: \.id) { role in
                    Button {
                        onPicked(role.id)
                        isPresented = false
                        navigationManager.navigateTo(.family)
                    } label: {
                        Text(localizationManager.localized(role.key))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(Spacing.m)
                            .stormGlassCard(cornerRadius: CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                }
                Button {
                    isPresented = false
                    navigationManager.navigateTo(.family)
                } label: {
                    Text(localizationManager.localized("map_role_skip"))
                        .font(.subheadline)
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.plain)
                Spacer()
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
        }
    }
}

// MARK: - Pet wizard 01i

struct FamilyPetWizardSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var name = ""
    @State private var breed = ""
    @State private var notes = ""
    @State private var walk = true
    @State private var feed = true
    /// Q22: free-text reminder instead of fixed «medicine» toggle.
    @State private var customReminder = ""
    @State private var saved = false
    /// JOB05–07 CapCut · H15 type picker · dog / cat / other.
    @State private var selectedKind: String = "dog"

    private let petKinds: [(id: String, titleKey: String, asset: String)] = [
        ("dog", "pet_type_dog", "ICON_ALIVE_HERO_H15_PetDog"),
        ("cat", "pet_type_cat", "ICON_ALIVE_HERO_H15_PetCat"),
        ("other", "pet_type_other", "ICON_ALIVE_HERO_H15_PetOther")
    ]

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("pet_add_title"))
                        .font(AladdinFamilyType.title2())
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("map_soon_pet_body"))
                        .font(AladdinFamilyType.caption())
                        .foregroundColor(.textSecondary)

                    Text(localizationManager.localized("pet_type_picker_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    HStack(spacing: Spacing.m) {
                        ForEach(petKinds, id: \.id) { kind in
                            Button {
                                SelectionHaptic.selection()
                                selectedKind = kind.id
                            } label: {
                                VStack(spacing: 8) {
                                    Image(kind.asset)
                                        .resizable()
                                        .scaledToFit()
                                        .frame(width: 88, height: 88)
                                        .clipShape(Circle())
                                        .overlay(
                                            Circle()
                                                .stroke(
                                                    selectedKind == kind.id
                                                        ? Color.secondaryGold
                                                        : Color.clear,
                                                    lineWidth: 3
                                                )
                                        )
                                    Text(localizationManager.localized(kind.titleKey))
                                        .font(.caption.weight(.semibold))
                                        .foregroundColor(
                                            selectedKind == kind.id
                                                ? .secondaryGold
                                                : .textSecondary
                                        )
                                }
                                .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.plain)
                            .accessibilityIdentifier("pet_type_\(kind.id)")
                        }
                    }
                    .padding(.vertical, 4)
                    .accessibilityIdentifier("pet_type_picker_h15")

                    TextField(localizationManager.localized("pet_name_ph"), text: $name)
                        .textFieldStyle(.roundedBorder)
                    TextField(localizationManager.localized("pet_breed_ph"), text: $breed)
                        .textFieldStyle(.roundedBorder)
                    TextField(localizationManager.localized("pet_notes_ph"), text: $notes)
                        .textFieldStyle(.roundedBorder)
                    Toggle(isOn: $walk) {
                        Text(localizationManager.localized("pet_routine_walk"))
                            .foregroundColor(.textPrimary)
                    }
                    .tint(.secondaryGold)
                    Toggle(isOn: $feed) {
                        Text(localizationManager.localized("pet_routine_feed"))
                            .foregroundColor(.textPrimary)
                    }
                    .tint(.secondaryGold)
                    Text(localizationManager.localized("pet_custom_reminder_toggle"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    TextField(localizationManager.localized("pet_custom_reminder_ph"), text: $customReminder)
                        .textFieldStyle(.roundedBorder)
                        .accessibilityIdentifier("pet_custom_reminder_field")

                    if saved {
                        Text(localizationManager.localized("pet_saved_local"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }

                    Button {
                        savePet()
                    } label: {
                        Text(localizationManager.localized("pet_save_cta"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.backgroundDark)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(Color.secondaryGold)
                            .cornerRadius(CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                    .disabled(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(Spacing.l)
            }
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
        }
    }

    private func savePet() {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let custom = customReminder.trimmingCharacters(in: .whitespacesAndNewlines)
        var mergedNotes = notes.trimmingCharacters(in: .whitespacesAndNewlines)
        if !custom.isEmpty {
            if mergedNotes.isEmpty {
                mergedNotes = custom
            } else if !mergedNotes.contains(custom) {
                mergedNotes = "\(mergedNotes)\n\(custom)"
            }
        }
        let pet = FamilyPetProfile(
            id: UUID(),
            name: trimmed,
            breed: breed.trimmingCharacters(in: .whitespacesAndNewlines),
            notes: mergedNotes,
            walkReminder: walk,
            feedReminder: feed,
            medicineReminder: false,
            kind: selectedKind
        )
        FamilyPetProfileStore.append(pet)
        var habits = UserDefaults.standard.stringArray(forKey: "family_pet_habit_flags_v1") ?? []
        if walk { habits.append("walk:\(pet.id.uuidString)") }
        if feed { habits.append("feed:\(pet.id.uuidString)") }
        if !custom.isEmpty { habits.append("custom:\(pet.id.uuidString)") }
        UserDefaults.standard.set(Array(Set(habits)), forKey: "family_pet_habit_flags_v1")
        syncPetRoutinesToFamilyHabits(pet, customReminder: custom)
        saved = true
        HapticFeedback.notification(.success)
    }

    private func syncPetRoutinesToFamilyHabits(_ pet: FamilyPetProfile, customReminder: String) {
        Task { @MainActor in
            var config = FamilyHabitRemindersService.shared.config
            var customs = config.custom
            func appendRoutine(title: String, hour: Int) {
                guard customs.count < FamilyHabitCustomReminder.maxPerFamily else { return }
                let full = "\(pet.name) · \(title)"
                if customs.contains(where: { $0.title == full }) { return }
                customs.append(
                    FamilyHabitCustomReminder(
                        title: String(full.prefix(FamilyHabitCustomReminder.titleMaxLength)),
                        emoji: "🐾",
                        enabled: true,
                        mode: .onceDaily,
                        hour: hour,
                        minute: 0
                    )
                )
            }
            if pet.walkReminder {
                appendRoutine(title: localizationManager.localized("pet_routine_walk"), hour: 9)
            }
            if pet.feedReminder {
                appendRoutine(title: localizationManager.localized("pet_routine_feed"), hour: 19)
            }
            if !customReminder.isEmpty {
                appendRoutine(title: customReminder, hour: 10)
            }
            config.custom = customs
            config.normalizeCustom()
            let members = FamilyLocalStore.loadPersistedMembers()
            _ = await FamilyHabitRemindersService.shared.saveLocalThenSync(
                config: config,
                members: members
            )
        }
    }
}

// MARK: - Preferred external maps (locale)

/// RU / русский → Яндекс; EN / англоязычные регионы → Apple. User can always switch.
enum FamilyMapsPreference {
    static let storageKey = "where_phone_preferred_maps"
    private static let seededKey = "where_phone_preferred_maps_seeded_v2"
    private static let userChoseKey = "where_phone_preferred_maps_user_set"

    static func markUserChose(_ value: String) {
        UserDefaults.standard.set(value, forKey: storageKey)
        UserDefaults.standard.set(true, forKey: userChoseKey)
    }

    static func ensureSeeded(language: LocalizationManager.Language) {
        if UserDefaults.standard.bool(forKey: userChoseKey) {
            UserDefaults.standard.set(true, forKey: seededKey)
            return
        }
        // One-shot locale seed (v2). Overwrites previous hard-coded «yandex» if user never picked.
        if !UserDefaults.standard.bool(forKey: seededKey) {
            UserDefaults.standard.set(systemDefault(language: language), forKey: storageKey)
            UserDefaults.standard.set(true, forKey: seededKey)
        }
    }

    static func systemDefault(language: LocalizationManager.Language) -> String {
        let region: String = {
            if #available(iOS 16.0, *) {
                return Locale.current.region?.identifier ?? ""
            }
            return Locale.current.regionCode ?? ""
        }().uppercased()

        // Russia (and app RU) → Yandex.
        if region == "RU" || language == .russian {
            return "yandex"
        }
        // English-speaking countries / app EN → Apple Maps.
        let englishRegions: Set<String> = ["US", "GB", "AU", "CA", "NZ", "IE", "ZA"]
        if englishRegions.contains(region) || language == .english {
            return "apple"
        }
        return "apple"
    }

    static func resolved(language: LocalizationManager.Language) -> String {
        ensureSeeded(language: language)
        return UserDefaults.standard.string(forKey: storageKey) ?? systemDefault(language: language)
    }
}

// MARK: - Routes sheet (B-depth L-P3-09)

struct FamilyMapRoutesSheet: View {
    @Binding var isPresented: Bool
    var coordinate: CLLocationCoordinate2D?
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("where_phone_preferred_maps") private var preferredMaps = "yandex"

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_routes_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("map_routes_body"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.white.opacity(0.92))

                // Preferred app first (RU→Yandex, EN→Apple); user always sees both.
                if preferredMaps == "apple" {
                    appleExternalRow
                    yandexExternalRow
                } else {
                    yandexExternalRow
                    appleExternalRow
                }

                routeRow(titleKey: "map_routes_drive", systemImage: "car.fill", modeKey: MKLaunchOptionsDirectionsModeDriving)
                routeRow(titleKey: "map_routes_walk", systemImage: "figure.walk", modeKey: MKLaunchOptionsDirectionsModeWalking)
                routeRow(titleKey: "map_routes_transit", systemImage: "bus.fill", modeKey: MKLaunchOptionsDirectionsModeTransit)
                Spacer()
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
            .onAppear {
                preferredMaps = FamilyMapsPreference.resolved(language: localizationManager.currentLanguage)
            }
        }
    }

    private var yandexExternalRow: some View {
        openExternalRow(
            titleKey: "where_phone_open_yandex_maps",
            systemImage: "map.fill",
            isPreferred: preferredMaps == "yandex"
        ) {
            openInYandex()
        }
    }

    private var appleExternalRow: some View {
        openExternalRow(
            titleKey: "where_phone_open_apple_maps",
            systemImage: "map",
            isPreferred: preferredMaps == "apple"
        ) {
            openInAppleDriving()
        }
    }

    private func openExternalRow(
        titleKey: String,
        systemImage: String,
        isPreferred: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                Image(systemName: systemImage)
                    .foregroundColor(.secondaryGold)
                    .frame(width: 28)
                Text(localizationManager.localized(titleKey))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                if isPreferred {
                    Text(localizationManager.localized("where_phone_maps_preferred_badge"))
                        .font(.caption2.weight(.bold))
                        .foregroundColor(.backgroundDark)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.secondaryGold)
                        .clipShape(Capsule())
                }
                Spacer()
                Image(systemName: "arrow.up.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .disabled(coordinate == nil)
    }

    private func routeRow(titleKey: String, systemImage: String, modeKey: String) -> some View {
        Button {
            openDirections(modeKey: modeKey)
        } label: {
            HStack(spacing: Spacing.m) {
                Image(systemName: systemImage)
                    .foregroundColor(.secondaryGold)
                    .frame(width: 28)
                Text(localizationManager.localized(titleKey))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                Spacer()
                Image(systemName: "arrow.up.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .disabled(coordinate == nil)
    }

    private func openDirections(modeKey: String) {
        guard let coordinate else { return }
        FamilyMapsPreference.markUserChose("apple")
        preferredMaps = "apple"
        let placemark = MKPlacemark(coordinate: coordinate)
        let item = MKMapItem(placemark: placemark)
        item.name = localizationManager.localized("where_phone_map_card_title")
        item.openInMaps(launchOptions: [MKLaunchOptionsDirectionsModeKey: modeKey])
        isPresented = false
    }

    private func openInAppleDriving() {
        FamilyMapsPreference.markUserChose("apple")
        preferredMaps = "apple"
        openDirections(modeKey: MKLaunchOptionsDirectionsModeDriving)
    }

    private func openInYandex() {
        guard let coordinate else { return }
        FamilyMapsPreference.markUserChose("yandex")
        preferredMaps = "yandex"
        let lat = coordinate.latitude
        let lon = coordinate.longitude
        let appURL = URL(string: String(format: "yandexmaps://maps.yandex.ru/?rtext=~%.6f,%.6f&rtt=auto", lat, lon))
        let webURL = URL(string: String(format: "https://yandex.ru/maps/?rtext=~%.6f,%.6f&rtt=auto", lat, lon))
        if let appURL, UIApplication.shared.canOpenURL(appURL) {
            UIApplication.shared.open(appURL)
        } else if let webURL {
            UIApplication.shared.open(webURL)
        }
        isPresented = false
    }
}

// MARK: - Crash confirm (Wave C)

struct FamilyCrashConfirmSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var isSending = false
    @State private var statusText: String?

    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.m) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 48))
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized("crash_confirm_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                Text(localizationManager.localized("crash_limits_body"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.white.opacity(0.92))
                    .multilineTextAlignment(.center)
                if isSending {
                    ProgressView()
                        .tint(Color.secondaryGold)
                        .accessibilityIdentifier("crash_confirm_progress")
                    Text(statusText ?? localizationManager.localized("crash_confirm_sending"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.92))
                        .multilineTextAlignment(.center)
                }
                Button {
                    sendNeedHelpTapped()
                } label: {
                    Text(localizationManager.localized("crash_confirm_yes"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.secondaryGold.opacity(isSending ? 0.55 : 1))
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(isSending)
                .accessibilityIdentifier("crash_confirm_yes")
                Button {
                    guard !isSending else { return }
                    isPresented = false
                } label: {
                    Text(localizationManager.localized("crash_confirm_no"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .stormGlassCard(cornerRadius: CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(isSending)
                .accessibilityIdentifier("crash_confirm_no")
                Spacer()
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                guard !isSending else { return }
                isPresented = false
            })
        }
    }

    /// Device QA: haptic immediately; 3s UI timeout; never wait on 60s network.
    private func sendNeedHelpTapped() {
        guard !isSending else { return }
        HapticFeedback.impact(.medium)
        isSending = true
        statusText = localizationManager.localized("crash_confirm_sending")
        let offline = !OfflineManager.shared.isOnline
        if offline {
            statusText = localizationManager.localized("crash_confirm_offline")
        }
        Task { @MainActor in
            defer { isSending = false }
            let timedOut = await withTimeout(seconds: 3) {
                await FamilyMapFamilyAlert.sendNeedHelp(localization: localizationManager)
            }
            if timedOut {
                // Local ack already fired inside ImOk/NeedHelp; queue for network retry.
                FamilyMapFamilyAlert.enqueueNeedHelpOffline(localization: localizationManager)
                print("WHERE_PHONE crash yes → local_queued (network timeout)")
                ToastManager.shared.showInfo(localizationManager.localized("crash_confirm_local_queued"))
                statusText = localizationManager.localized("crash_confirm_local_queued")
                // Keep sheet open briefly so owner sees explicit status.
                try? await Task.sleep(nanoseconds: 900_000_000)
                isPresented = false
                return
            }
            if offline {
                print("WHERE_PHONE crash yes → offline queued")
                ToastManager.shared.showInfo(localizationManager.localized("crash_confirm_offline"))
                statusText = localizationManager.localized("crash_confirm_offline")
            } else {
                print("WHERE_PHONE crash yes → sent")
                ToastManager.shared.showSuccess(localizationManager.localized("crash_confirm_sent"))
                statusText = localizationManager.localized("crash_confirm_sent")
            }
            isPresented = false
        }
    }

    /// Returns `true` if the work did not finish before `seconds`.
    private func withTimeout(seconds: Double, operation: @escaping () async -> Void) async -> Bool {
        await withTaskGroup(of: Bool.self) { group in
            group.addTask {
                await operation()
                return false
            }
            group.addTask {
                try? await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
                return true
            }
            let first = await group.next() ?? true
            group.cancelAll()
            return first
        }
    }
}

/// Shared SOS / crash → family chat path (E2EE + local ack). No roadside dispatch.
enum FamilyMapFamilyAlert {
    @MainActor
    static func sendNeedHelp(localization: LocalizationManager) async {
        let name = displayName(localization: localization)
        _ = await FamilyImOkService.sendNeedHelp(
            displayName: name,
            localization: localization,
            attachLocation: true
        )
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "family_sos_last_sent_ts")
        NotificationCenter.default.post(name: Notification.Name("aladdin.family.sos.sent"), object: nil)
    }

    /// On UI timeout / offline — queue for later flush; do not block the sheet.
    @MainActor
    static func enqueueNeedHelpOffline(localization: LocalizationManager) {
        let name = displayName(localization: localization)
        FamilyImOkOfflineQueue.enqueue(
            FamilyAutoAlertEvent(
                kind: .needHelp,
                displayName: name,
                legacyPlaintext: localization.localized("crash_confirm_yes")
            )
        )
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "family_sos_last_sent_ts")
    }

    private static func displayName(localization: LocalizationManager) -> String {
        let name = (
            UserDefaults.standard.string(forKey: "user_name")
                ?? UserDefaults.standard.string(forKey: "user_display_name")
                ?? localization.localized("where_phone_you")
        ).trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? localization.localized("where_phone_you") : name
    }
}

// MARK: - SOS hold control (Wave C)

struct FamilySOSHoldButton: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var progress: CGFloat = 0
    @State private var holding = false
    @State private var sent = false
    @State private var timer: Timer?

    private let holdSeconds: CGFloat = 3
    private let diameter: CGFloat = 132

    var body: some View {
        VStack(spacing: Spacing.s) {
            Text(sent
                 ? localizationManager.localized("sos_sent_family")
                 : localizationManager.localized("sos_hold_hint"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .multilineTextAlignment(.center)

            // P4.4: круг + кольцо прогресса (полоску убрали). Hold 3с / fireSOS без изменений.
            ZStack {
                Circle()
                    .fill(Color.secondaryGold.opacity(holding ? 0.28 : 0.15))
                    .frame(width: diameter, height: diameter)
                Circle()
                    .stroke(Color.secondaryGold.opacity(0.28), lineWidth: 4)
                    .frame(width: diameter, height: diameter)
                Circle()
                    .trim(from: 0, to: max(progress, holding ? 0.02 : 0))
                    .stroke(
                        Color.secondaryGold,
                        style: StrokeStyle(lineWidth: 4, lineCap: .round)
                    )
                    .rotationEffect(.degrees(-90))
                    .frame(width: diameter, height: diameter)
                    .animation(holding ? .linear(duration: 0.05) : .easeOut(duration: 0.2), value: progress)
                VStack(spacing: 4) {
                    Text("SOS")
                        .font(.title2.weight(.black))
                        .foregroundColor(.secondaryGold)
                    if holding {
                        Text(String(
                            format: localizationManager.localized("sos_countdown"),
                            max(1, Int(ceil(holdSeconds * (1 - progress))))
                        ))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    }
                }
            }
            .contentShape(Circle())
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { _ in
                        guard !sent else { return }
                        if !holding { beginHold() }
                    }
                    .onEnded { _ in
                        cancelHold(resetProgress: !sent)
                    }
            )
            .accessibilityIdentifier("where_phone_sos_hold_button")
        }
    }

    private func beginHold() {
        holding = true
        progress = 0
        timer?.invalidate()
        let start = Date()
        timer = Timer.scheduledTimer(withTimeInterval: 0.05, repeats: true) { t in
            let elapsed = CGFloat(Date().timeIntervalSince(start))
            progress = min(1, elapsed / holdSeconds)
            if progress >= 1 {
                t.invalidate()
                fireSOS()
            }
        }
    }

    private func cancelHold(resetProgress: Bool) {
        holding = false
        timer?.invalidate()
        timer = nil
        if resetProgress { progress = 0 }
    }

    private func fireSOS() {
        holding = false
        sent = true
        progress = 1
        HapticFeedback.notification(.warning)
        Task { @MainActor in
            await FamilyMapFamilyAlert.sendNeedHelp(localization: localizationManager)
        }
    }
}

// MARK: - Wave A extras (inside Antifake Hub — not a separate «Проверить» sheet)

/// Call Directory · Анти-Баннер · honest empties. Embedded under Antifake checks.
struct AntifakeWaveAExtrasSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var contentBlocker = ContentBlockerManager.shared
    @State private var adblockOn = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("pay_pains_door_check_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.white)

            sectionCard(
                title: localizationManager.localized("calldir_guide_title"),
                body: localizationManager.localized("calldir_guide_body")
            ) {
                AntifakeCallDirectorySettingsCard()
            }

            sectionCard(
                title: localizationManager.localized("adblock_title"),
                body: localizationManager.localized("adblock_body")
            ) {
                Toggle(isOn: $adblockOn) {
                    Text(localizationManager.localized("adblock_toggle"))
                        .foregroundColor(.white)
                }
                .tint(.secondaryGold)
                .onChange(of: adblockOn) { on in
                    Task {
                        // Honest: reuse existing Safari content categories (no fake “ads-only” enum).
                        if on {
                            try? await contentBlocker.enableContentBlocker(categories: [.shopping, .news])
                        } else {
                            await contentBlocker.disableContentBlocker()
                        }
                    }
                }
                Text(localizationManager.localized("adblock_safari_steps_title"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized("adblock_safari_steps_body"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                Button {
                    if let url = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Text(localizationManager.localized("adblock_safari_open_settings"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("adblock_safari_open_settings")
            }

            emptySoonCard(titleKey: "lists_empty_title", bodyKey: "lists_empty_body")
            emptySoonCard(titleKey: "home_net_title", bodyKey: "home_net_body")
            emptySoonCard(titleKey: "vk_connect_title", bodyKey: "vk_connect_body")
        }
        .onAppear {
            adblockOn = contentBlocker.isEnabled
        }
        .accessibilityIdentifier("antifake_wave_a_extras")
    }

    private func sectionCard<Content: View>(
        title: String,
        body: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(title)
                .font(AladdinFamilyType.title3())
                .foregroundColor(.white)
            Text(body)
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(.white.opacity(0.8))
            content()
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private func emptySoonCard(titleKey: String, bodyKey: String) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized(titleKey))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.white)
            Text(localizationManager.localized(bodyKey))
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(.white.opacity(0.8))
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
}

/// Legacy wrapper — prefer embedding `AntifakeWaveAExtrasSection` in Antifake Hub.
struct PayPainsCheckDoorSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        NavigationView {
            ScrollView {
                AntifakeWaveAExtrasSection()
                    .environmentObject(localizationManager)
                    .padding(Spacing.l)
            }
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
        }
    }
}

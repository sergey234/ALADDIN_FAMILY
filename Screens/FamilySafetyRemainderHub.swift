import SwiftUI
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

    func startIfNeeded() {
        active = true
        authStatus = manager.authorizationStatus
        switch authStatus {
        case .authorizedAlways, .authorizedWhenInUse:
            manager.startUpdatingLocation()
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        default:
            break
        }
    }

    func stop() {
        active = false
        manager.stopUpdatingLocation()
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        Task { @MainActor in
            self.authStatus = manager.authorizationStatus
            if self.active,
               manager.authorizationStatus == .authorizedAlways
                || manager.authorizationStatus == .authorizedWhenInUse {
                manager.startUpdatingLocation()
            }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let loc = locations.last else { return }
        Task { @MainActor in
            self.coordinate = loc.coordinate
            self.updatedAt = loc.timestamp
            if loc.speed >= 0 {
                self.speedKmh = Int((loc.speed * 3.6).rounded())
            } else {
                self.speedKmh = nil
            }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("FamilyMapLiveLocation: \(error.localizedDescription)")
    }
}

// MARK: - Quiet zone store (B-depth)

enum FamilyMapQuietZoneStore {
    private static let key = "where_phone_quiet_zone_meters_v1"
    static var meters: Double {
        get {
            let v = UserDefaults.standard.double(forKey: key)
            return v > 0 ? v : 150
        }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }

    /// True when GPS is within quiet radius of any saved place center.
    @MainActor
    static func contains(_ location: CLLocation) -> Bool {
        let radius = meters
        let centers = GeofenceGeocodingService.shared.loadStoredCoordinates().values
        for center in centers {
            let place = CLLocation(latitude: center.latitude, longitude: center.longitude)
            if location.distance(from: place) <= radius {
                return true
            }
        }
        return false
    }
}

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
}

// MARK: - MapKit preview with street/satellite (iOS 15)

struct FamilyHubMapKitView: UIViewRepresentable {
    @Binding var region: MKCoordinateRegion
    var coordinate: CLLocationCoordinate2D?
    var title: String
    var mapTypeRaw: String

    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView(frame: .zero)
        map.isZoomEnabled = false
        map.isScrollEnabled = false
        map.isRotateEnabled = false
        map.isPitchEnabled = false
        map.delegate = context.coordinator
        return map
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        switch mapTypeRaw {
        case "satellite":
            mapView.mapType = .satellite
        case "street":
            mapView.mapType = .standard
        default:
            mapView.mapType = .mutedStandard
        }
        mapView.setRegion(region, animated: false)
        mapView.removeAnnotations(mapView.annotations)
        if let coordinate {
            let pin = MKPointAnnotation()
            pin.coordinate = coordinate
            pin.title = title
            mapView.addAnnotation(pin)
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator: NSObject, MKMapViewDelegate {
        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            if annotation is MKUserLocation { return nil }
            let id = "family_hub_pin"
            let view = mapView.dequeueReusableAnnotationView(withIdentifier: id)
                ?? MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: id)
            view.annotation = annotation
            if let marker = view as? MKMarkerAnnotationView {
                marker.markerTintColor = UIColor(Color.secondaryGold)
            }
            return view
        }
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
    @AppStorage("where_phone_pin_preview_done") private var previewDone = false

    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.m) {
                Image("FIG_L01_MapPinBattery")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 96, height: 96)
                Text(localizationManager.localized("map_pin_preview_title"))
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                Text(localizationManager.localized("map_pin_preview_body"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
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
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("map_create_circle_teaser"))
                    .font(.subheadline)
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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
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
    @State private var medicine = false
    @State private var saved = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("pet_add_title"))
                        .font(.system(.title2, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("map_soon_pet_body"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
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
                    Toggle(isOn: $medicine) {
                        Text(localizationManager.localized("pet_routine_medicine"))
                            .foregroundColor(.textPrimary)
                    }
                    .tint(.secondaryGold)

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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
        }
    }

    private func savePet() {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let pet = FamilyPetProfile(
            id: UUID(),
            name: trimmed,
            breed: breed.trimmingCharacters(in: .whitespacesAndNewlines),
            notes: notes.trimmingCharacters(in: .whitespacesAndNewlines),
            walkReminder: walk,
            feedReminder: feed,
            medicineReminder: medicine
        )
        FamilyPetProfileStore.append(pet)
        var habits = UserDefaults.standard.stringArray(forKey: "family_pet_habit_flags_v1") ?? []
        if walk { habits.append("walk:\(pet.id.uuidString)") }
        if feed { habits.append("feed:\(pet.id.uuidString)") }
        if medicine { habits.append("med:\(pet.id.uuidString)") }
        UserDefaults.standard.set(Array(Set(habits)), forKey: "family_pet_habit_flags_v1")
        syncPetRoutinesToFamilyHabits(pet)
        saved = true
        HapticFeedback.notification(.success)
    }

    private func syncPetRoutinesToFamilyHabits(_ pet: FamilyPetProfile) {
        Task { @MainActor in
            var config = FamilyHabitRemindersService.shared.config
            var customs = config.custom
            func appendRoutine(titleKey: String, hour: Int) {
                guard customs.count < FamilyHabitCustomReminder.maxPerFamily else { return }
                let title = "\(pet.name) · \(localizationManager.localized(titleKey))"
                if customs.contains(where: { $0.title == title }) { return }
                customs.append(
                    FamilyHabitCustomReminder(
                        title: String(title.prefix(FamilyHabitCustomReminder.titleMaxLength)),
                        emoji: "🐾",
                        enabled: true,
                        mode: .onceDaily,
                        hour: hour,
                        minute: 0
                    )
                )
            }
            if pet.walkReminder { appendRoutine(titleKey: "pet_routine_walk", hour: 9) }
            if pet.feedReminder { appendRoutine(titleKey: "pet_routine_feed", hour: 19) }
            if pet.medicineReminder { appendRoutine(titleKey: "pet_routine_medicine", hour: 10) }
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

// MARK: - Routes sheet (B-depth L-P3-09)

struct FamilyMapRoutesSheet: View {
    @Binding var isPresented: Bool
    var coordinate: CLLocationCoordinate2D?
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_routes_title"))
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("map_routes_body"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                routeRow(titleKey: "map_routes_drive", systemImage: "car.fill", modeKey: MKLaunchOptionsDirectionsModeDriving)
                routeRow(titleKey: "map_routes_walk", systemImage: "figure.walk", modeKey: MKLaunchOptionsDirectionsModeWalking)
                routeRow(titleKey: "map_routes_transit", systemImage: "bus.fill", modeKey: MKLaunchOptionsDirectionsModeTransit)
                Spacer()
            }
            .padding(Spacing.l)
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
        }
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
        let placemark = MKPlacemark(coordinate: coordinate)
        let item = MKMapItem(placemark: placemark)
        item.name = localizationManager.localized("where_phone_map_card_title")
        item.openInMaps(launchOptions: [MKLaunchOptionsDirectionsModeKey: modeKey])
        isPresented = false
    }
}

// MARK: - Crash confirm (Wave C)

struct FamilyCrashConfirmSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var isSending = false

    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.m) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 48))
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized("crash_confirm_title"))
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                Text(localizationManager.localized("crash_limits_body"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                Button {
                    guard !isSending else { return }
                    isSending = true
                    Task { @MainActor in
                        await FamilyMapFamilyAlert.sendNeedHelp(localization: localizationManager)
                        isSending = false
                        isPresented = false
                    }
                } label: {
                    Text(localizationManager.localized("crash_confirm_yes"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(isSending)
                .accessibilityIdentifier("crash_confirm_yes")
                Button {
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
                .accessibilityIdentifier("crash_confirm_no")
                Spacer()
            }
            .padding(Spacing.l)
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
        }
    }
}

/// Shared SOS / crash → family chat path (E2EE + local ack). No roadside dispatch.
enum FamilyMapFamilyAlert {
    @MainActor
    static func sendNeedHelp(localization: LocalizationManager) async {
        let name = (
            UserDefaults.standard.string(forKey: "user_name")
                ?? UserDefaults.standard.string(forKey: "user_display_name")
                ?? localization.localized("where_phone_you")
        ).trimmingCharacters(in: .whitespacesAndNewlines)
        _ = await FamilyImOkService.sendNeedHelp(
            displayName: name.isEmpty ? localization.localized("where_phone_you") : name,
            localization: localization,
            attachLocation: true
        )
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "family_sos_last_sent_ts")
        NotificationCenter.default.post(name: Notification.Name("aladdin.family.sos.sent"), object: nil)
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

    var body: some View {
        VStack(spacing: Spacing.s) {
            Text(sent
                 ? localizationManager.localized("sos_sent_family")
                 : localizationManager.localized("sos_hold_hint"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.secondaryGold)

            ZStack {
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.secondaryGold.opacity(0.15))
                    .frame(height: 56)
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.secondaryGold.opacity(0.45))
                    .frame(maxWidth: .infinity, maxHeight: 56, alignment: .leading)
                    .scaleEffect(x: max(progress, 0.02), y: 1, anchor: .leading)
                Text(holding
                     ? String(format: localizationManager.localized("sos_countdown"), max(1, Int(ceil(holdSeconds * (1 - progress)))))
                     : localizationManager.localized("sos_hold_hint"))
                    .font(.subheadline.weight(.bold))
                    .foregroundColor(.textPrimary)
            }
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

// MARK: - Wave A check door extras

struct PayPainsCheckDoorSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @ObservedObject private var contentBlocker = ContentBlockerManager.shared
    @State private var adblockOn = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("pay_pains_door_check_title"))
                        .font(.system(.title2, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)

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
                                .foregroundColor(.textPrimary)
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
                        Text(localizationManager.localized("adblock_safari_tip"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }

                    emptySoonCard(
                        titleKey: "lists_empty_title",
                        bodyKey: "lists_empty_body"
                    )
                    emptySoonCard(
                        titleKey: "home_net_title",
                        bodyKey: "home_net_body"
                    )
                    emptySoonCard(
                        titleKey: "vk_connect_title",
                        bodyKey: "vk_connect_body"
                    )

                    Button {
                        isPresented = false
                        navigationManager.navigateToAntifakeHub(tab: .text)
                    } label: {
                        Text(localizationManager.localized("pay_pains_door_check_subtitle"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.backgroundDark)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(Color.secondaryGold)
                            .cornerRadius(CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                }
                .padding(Spacing.l)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented = false
            })
            .onAppear {
                adblockOn = contentBlocker.isEnabled
            }
        }
    }

    private func sectionCard<Content: View>(
        title: String,
        body: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(title)
                .font(.system(.title3, design: .serif).weight(.bold))
                .foregroundColor(.textPrimary)
            Text(body)
                .font(.subheadline)
                .foregroundColor(.textSecondary)
            content()
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private func emptySoonCard(titleKey: String, bodyKey: String) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized(titleKey))
                .font(.system(.title3, design: .serif).weight(.bold))
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized(bodyKey))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
}

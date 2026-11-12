import SwiftUI
import CoreLocation
import MapKit
import UIKit
import EventKit
import UserNotifications

/// Family hub «Где семья»: L-P3-01 (4-tab + X) · L-P3-01d (5 chips + scroll-spy).
/// No fake pins / no continuous spy track / Pet·Items = soon sheets.
struct WhereIsPhoneScreen: View {
    @Binding var isPresented: Bool
    /// Close hub sheet first, then parent runs navigate (e.g. tariffs) — otherwise push dies under sheet.
    var onLeaveToNavigate: ((NavigationManager.ALADDINScreen) -> Void)? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var analyticsViewModel = AnalyticsViewModel(service: RemoteAnalyticsService())
    @AppStorage("family_access_mode") private var familyAccessMode = "full"
    @State private var inQuietZone = false
    @State private var shareExpiresAt: Date? = FamilyMapShareSessionStore.expiresAt

    private enum HubTab: Int, CaseIterable, Identifiable {
        case location, driving, safety, subscription
        var id: Int { rawValue }

        var titleKey: String {
            switch self {
            case .location: return "map_tab_location"
            case .driving: return "map_tab_driving"
            case .safety: return "map_tab_safety"
            case .subscription: return "map_tab_subscription"
            }
        }

        var systemImage: String {
            switch self {
            case .location: return "location.fill"
            case .driving: return "car.fill"
            case .safety: return "shield.fill"
            case .subscription: return "crown.fill"
            }
        }
    }

    /// Sheet sections under Location (Life360 5-chip strip).
    private enum SheetChip: Int, CaseIterable, Identifiable, Hashable {
        case people, pets, items, places, events
        var id: Int { rawValue }

        var titleKey: String {
            switch self {
            case .people: return "map_chip_people"
            case .pets: return "map_chip_pets"
            case .items: return "map_chip_items"
            case .places: return "map_chip_places"
            case .events: return "map_chip_events"
            }
        }

        var systemImage: String {
            switch self {
            case .people: return "person.2.fill"
            case .pets: return "pawprint.fill"
            case .items: return "key.fill"
            case .places: return "house.fill"
            case .events: return "calendar"
            }
        }
    }

    /// Nested hub presents — queue one after dismiss so sheets don’t stack.
    private enum PendingHubSheet: Equatable {
        case places(preferredNameKey: String?)
        case routes
        case familyGroups
        case mapType
        case invisibleHat
        case alwaysAllow
        case petWizard
        case petSoon
        case itemsSoon
        case familyCalendar
        case crashSettings
        case softPaywall
        case softInvite
        case inviteRole
    }

    @State private var hubTab: HubTab = .location
    /// One system Motion & Fitness prompt per hub session (Driving / Safety).
    @State private var didAskMotionThisSession = false
    @State private var activeChip: SheetChip = .people
    @State private var isChipProgrammaticScroll = false
    @State private var chipScrollRequest = 0
    /// W2 Q34–Q36 Life360: 0 = map ~full · 1 = sheet covers ~90%.
    /// Start at peek so map is the hero (not a 50/50 split). CLIP = primary (MAP-95 PASS).
    @State private var sheetExpansion: CGFloat = 0.08
    @State private var sheetDragStart: CGFloat = 0.08
    @State private var sheetDragActive = false
    /// Pane height for converting drag px → expansion (set by GeometryReader).
    @State private var locationPaneHeight: CGFloat = 560
    /// Emergency only: `true` → iOS 16+ S2 system detents. Default **false** = CLIP on all OS.
    private let preferLocationSystemSheetS2 = false
    /// S2: system sheet on Location tab (only if preferLocationSystemSheetS2).
    @State private var showLocationSystemSheet = false
    /// S2: false = medium · true = fraction(0.95). Не храним PresentationDetent в @State (iOS 15 deploy).
    @State private var locationSheetIsFull = false
    /// Bump to force live map camera (locate FAB) without epsilon wait.
    @State private var mapCameraToken: Int = 0
    @State private var placeCount = 0
    @State private var latestEvent: GeofenceDayEvent?
    @State private var todayTrail: [GeofenceDayEvent] = []
    @State private var shares: [WherePhoneShare] = []
    @State private var remoteSignals: [WherePhoneFamilySignal] = []
    @State private var remotePoints: [WherePhoneFamilyPoint] = []
    @State private var isSending = false
    /// Debounce double-taps on CTA (device lag / stacked sheets).
    @State private var lastWherePhoneTapId: String = ""
    @State private var lastWherePhoneTapAt: Date = .distantPast
    /// 1A: one deferred present after dismiss (member / S2 location sheet).
    @State private var pendingHubSheet: PendingHubSheet?
    /// Explicit send-fail UI (CLError 0 was only statusText in scroll).
    @State private var sendFailAlertMessage: String?
    @State private var statusText: String?
    @State private var locatorHint: String?
    @State private var showPlaces = false
    /// S30 — chip → open places modal with prefilled name key.
    @State private var placesPreferredNameKey: String? = nil
    @State private var showFamilyGroups = false
    @State private var mapGroupFilterId: UUID? = FamilyGroupLabelStore.selectedFilterGroupId
    @State private var familyGroups: [FamilyGroupLabelStore.Group] = FamilyGroupLabelStore.load()
    @State private var showPetSoon = false
    @State private var showPetWizard = false
    @State private var showItemsSoon = false
    @State private var showFamilyCalendar = false
    @State private var showCrashSettings = false
    @State private var showMapTypeSheet = false
    @State private var showAlwaysAllowSheet = false
    @State private var showSoftPaywall = false
    @State private var showSoftInvite = false
    @State private var showInviteRole = false
    @State private var showRoutes = false
    @State private var showInvisibleHatSheet = false
    @State private var showCrashConfirm = false
    /// JOB11–12 · Safety SOS education pager (0 = intro, 1 = release).
    @State private var sosEduPage: Int = 0
    @State private var shareDuration: FamilyMapShareDuration =
        FamilyMapShareDuration(rawValue: FamilyMapShareSessionStore.selectedHours) ?? .oneHour
    @State private var journalIndex: Double = 0
    @State private var quietMeters: Double = FamilyMapQuietZoneStore.meters
    @State private var selectedMember: HubMemberCard?
    /// P0-5: member avatar crop pipeline (reuse AvatarCropEditor + ImagePicker).
    @State private var memberAvatarImage: UIImage?
    @State private var memberAvatarEpoch: Int = 0
    @State private var showMemberImagePicker = false
    @State private var memberCropSource: UIImage?
    @State private var savedPets: [FamilyPetProfile] = FamilyPetProfileStore.load()
    @StateObject private var liveLocation = FamilyMapLiveLocationController.shared
    @AppStorage("where_phone_pin_preview_done") private var pinPreviewDone = true
    /// QA-15: always L; pin-preview sheet retired.
    @AppStorage("where_phone_pin_size") private var pinSizeRaw: String = "L"
    @State private var localEvents: [FamilyMapLocalEvent] = FamilyMapLocalEventStore.load()
    @State private var draftEventTitle = ""
    @State private var draftEventPlace = ""
    @State private var draftEventStart = Date()
    @State private var draftEventEnd = Date().addingTimeInterval(3600)
    @State private var draftAddToIOS = true
    @State private var draftAudienceIds: Set<String> = []
    @State private var calendarRoster: [FamilyMemberData] = []
    @AppStorage("aladdin_crash_detection_consent_v1") private var crashConsentAccepted = false
    @AppStorage("where_phone_map_type") private var mapTypeRaw: String = "auto"
    @AppStorage("where_phone_always_prompt_done") private var alwaysPromptDone = false
    @AppStorage("where_phone_first_open_ts") private var firstOpenTs: Double = 0
    @AppStorage("where_phone_soft_paywall_done") private var softPaywallDone = false
    /// Seeded by locale: RU→Yandex, EN→Apple. User can always switch.
    @AppStorage("where_phone_preferred_maps") private var preferredMaps = "yandex"
    @State private var mapCoordinate: CLLocationCoordinate2D?
    @State private var mapPointName: String?
    @State private var mapPointAt: Date?
    @State private var mapPinSource: MapPinSource = .none
    @State private var travelMinutesToday: Int?
    @State private var mapRegion = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 55.75, longitude: 37.62),
        span: MKCoordinateSpan(latitudeDelta: 0.04, longitudeDelta: 0.04)
    )
    @State private var showOpenInMapsSheet = false

    private enum MapPinSource: String {
        case none, live, local, remote
    }

    @StateObject private var locator = WherePhoneOneShot()

    private struct HubMemberCard: Identifiable {
        let id: String
        let name: String
        let at: Date
    }

    private enum HubMapType: String, CaseIterable, Identifiable {
        case auto, street, satellite
        var id: String { rawValue }
        var titleKey: String {
            switch self {
            case .auto: return "map_type_auto"
            case .street: return "map_type_street"
            case .satellite: return "map_type_satellite"
            }
        }
    }

    private var hideOthers: Bool {
        let role = UserDefaults.standard.string(forKey: "current_user_role") ?? ""
        if role == "child" || role == "teenager" { return true }
        // Wave A Full/Limited — limited hides other members’ live board rows.
        return familyAccessMode == "limited"
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
        let all = WherePhoneFamilyBoard.points(
            local: shares,
            localMemberId: myMemberId,
            remote: remotePoints,
            hideOthers: hideOthers
        )
        guard let filterId = mapGroupFilterId,
              let group = familyGroups.first(where: { $0.id == filterId }),
              !group.memberIds.isEmpty else {
            return all
        }
        let allowed = Set(group.memberIds)
        return all.filter { allowed.contains($0.memberId) }
    }

    var body: some View {
        applyHubLifecycle(applySecondarySheets(applyPrimarySheets(hubRootStack)))
            .accessibilityIdentifier("where_phone_screen")
    }

    /// Split from `body` — compiler type-check timeout on one giant modifier chain.
    @ViewBuilder
    private var hubRootStack: some View {
        ZStack {
            // Location = Life360 canvas (map under chrome). Other tabs keep classic stack.
            if hubTab == .location {
                locationLife360Canvas
            } else {
                AladdinSnowballPalette.canvasGradient
                    .ignoresSafeArea()

                VStack(spacing: 0) {
                    hubHeader
                        .background(Color.backgroundMedium.opacity(0.5))
                    Group {
                        switch hubTab {
                        case .location:
                            EmptyView()
                        case .driving:
                            drivingTabPane
                        case .safety:
                            safetyTabPane
                        case .subscription:
                            subscriptionTabPane
                        }
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    hubTabBar
                }
            }
        }
        .onChange(of: hubTab) { tab in
            if tab == .driving || tab == .safety {
                askMotionIfNeededForHub()
            }
            // 3A: leaving Location must not leave deferred nested presents → cascade.
            clearNestedHubSheetsForTabChange(to: tab)
        }
    }

    /// Triggers iOS Motion & Fitness dialog once so ALADDIN appears in system Settings list.
    private func askMotionIfNeededForHub() {
        guard !didAskMotionThisSession else { return }
        didAskMotionThisSession = true
        Task { @MainActor in
            _ = await SensitivePermissionCoordinator.requestMotionIfNeeded()
        }
    }

    private func applyPrimarySheets<Content: View>(_ content: Content) -> some View {
        content
            .sheet(isPresented: $showPlaces, onDismiss: {
                placesPreferredNameKey = nil
                flushPendingHubSheetIfNeeded(reason: "placesDismiss")
            }) {
                GeofencesSettingsModal(
                    isPresented: $showPlaces,
                    preferredNameKey: placesPreferredNameKey
                )
                .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showFamilyGroups, onDismiss: {
                familyGroups = FamilyGroupLabelStore.load()
                mapGroupFilterId = FamilyGroupLabelStore.selectedFilterGroupId
            }) {
                FamilyGroupsModal(isPresented: $showFamilyGroups)
                    .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showPetSoon) {
                soonSheet(
                    titleKey: "map_soon_pet_title",
                    bodyKey: "map_soon_pet_body",
                    isPresented: $showPetSoon
                )
            }
            .sheet(isPresented: $showPetWizard, onDismiss: {
                savedPets = FamilyPetProfileStore.load()
            }) {
                FamilyPetWizardSheet(isPresented: $showPetWizard)
                    .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showInviteRole) {
                FamilyMapInviteRoleSheet(isPresented: $showInviteRole) { _ in }
                    .environmentObject(localizationManager)
                    .environmentObject(navigationManager)
            }
            .sheet(isPresented: $showRoutes) {
                FamilyMapRoutesSheet(isPresented: $showRoutes, coordinate: mapCoordinate)
                    .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showCrashConfirm) {
                FamilyCrashConfirmSheet(isPresented: $showCrashConfirm)
                    .environmentObject(localizationManager)
            }
    }

    private func applySecondarySheets<Content: View>(_ content: Content) -> some View {
        content
            .sheet(isPresented: $showItemsSoon) {
                soonSheet(
                    titleKey: "items_promo_title",
                    bodyKey: "items_promo_body",
                    isPresented: $showItemsSoon
                )
            }
            .sheet(isPresented: $showFamilyCalendar) {
                familyCalendarSheet
            }
            .sheet(isPresented: $showSoftPaywall) {
                softPaywallSheet
            }
            .sheet(isPresented: $showSoftInvite) {
                softInviteSheet
            }
            .sheet(isPresented: $showCrashSettings) {
                CrashDetectionSettingsModal(
                    componentId: "crash_detection_agent",
                    isPresented: $showCrashSettings
                )
                .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showMapTypeSheet) {
                mapTypeSheet
            }
            .sheet(isPresented: $showInvisibleHatSheet) {
                quietZoneSheet
            }
            .sheet(isPresented: $showAlwaysAllowSheet) {
                alwaysAllowSheet
            }
            .sheet(item: $selectedMember, onDismiss: {
                flushPendingHubSheetIfNeeded(reason: "memberDismiss")
            }) { member in
                memberDetailSheet(member)
            }
            .sheet(isPresented: $showMemberImagePicker) {
                ImagePicker(selectedImage: $memberCropSource)
            }
            .sheet(isPresented: Binding(
                get: { memberCropSource != nil },
                set: { if !$0 { memberCropSource = nil } }
            )) {
                if let source = memberCropSource {
                    AvatarCropEditor(
                        image: source,
                        onCommit: { cropped in
                            _ = ProfileImageManager.shared.saveProfileImage(cropped, for: .main)
                            memberAvatarImage = cropped
                            memberAvatarEpoch += 1
                            memberCropSource = nil
                            HapticFeedback.notification(.success)
                        },
                        onCancel: {
                            memberCropSource = nil
                        }
                    )
                    .environmentObject(localizationManager)
                }
            }
    }

    private var quietZoneSheet: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_privacy_zone_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized("map_privacy_zone_hint"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.white.opacity(0.85))
                Slider(value: $quietMeters, in: 50...500, step: 25)
                    .tint(Color.secondaryGold)
                    .onChange(of: quietMeters) { value in
                        FamilyMapQuietZoneStore.meters = value
                        print("WHERE_PHONE quiet meters=\(Int(value))")
                    }
                Text(
                    String(
                        format: localizationManager.localized("map_unit_meters"),
                        Int(quietMeters)
                    )
                )
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.75))
                Spacer()
            }
            .padding(Spacing.l)
            .background(StormMeshBackground(variant: .shield).ignoresSafeArea())
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("common_close")) {
                        showInvisibleHatSheet = false
                    }
                }
            }
        }
        .accessibilityIdentifier("where_phone_invisible_hat_sheet")
    }

    private func applyHubLifecycle<Content: View>(_ content: Content) -> some View {
        content
            .onAppear {
                preferredMaps = FamilyMapsPreference.resolved(language: localizationManager.currentLanguage)
                reload()
                liveLocation.startIfNeeded()
                savedPets = FamilyPetProfileStore.load()
                maybeOfferAlwaysAllow()
                maybeOfferSoftPaywall()
                // QA-15: never auto-present pin size sheet; force L.
                pinPreviewDone = true
                if pinSizeRaw != "L" { pinSizeRaw = "L" }
                applyPendingFamilyPushFocusIfNeeded()
            }
            .onDisappear {
                liveLocation.stop()
            }
            .onReceive(NotificationCenter.default.publisher(for: .geofenceDayEventsDidChange)) { _ in
                reload()
            }
            .onReceive(liveLocation.$coordinate) { coord in
                // Continuous live pin: Always Allow + Family+/trial/premium.
                guard FamilyMapLiveAccess.isEntitled,
                      liveLocation.authStatus == .authorizedAlways,
                      let coord else {
                    applyBestMapPin()
                    return
                }
                let loc = CLLocation(latitude: coord.latitude, longitude: coord.longitude)
                let quiet = FamilyMapQuietZoneStore.contains(loc)
                inQuietZone = quiet
                applyMapPin(
                    coord,
                    name: mapPointName ?? localizationManager.localized("where_phone_map_card_title"),
                    at: liveLocation.updatedAt ?? Date(),
                    source: .live
                )
                guard !quiet else { return }
                WherePhoneLastPointStore.save(
                    name: mapPointName ?? localizationManager.localized("where_phone_map_card_title"),
                    latitude: coord.latitude,
                    longitude: coord.longitude
                )
            }
            .onReceive(liveLocation.$authStatus) { _ in
                applyBestMapPin()
            }
            .onChange(of: crashConsentAccepted) { enabled in
                Task { @MainActor in
                    if enabled {
                        try? await CrashDetectionManager.shared.startMonitoring()
                    } else {
                        try? await CrashDetectionManager.shared.stopMonitoring()
                    }
                }
            }
            .onChange(of: shareDuration) { dur in
                FamilyMapShareSessionStore.selectedHours = dur.rawValue
            }
            .alert(
                localizationManager.localized("where_phone_share_button"),
                isPresented: Binding(
                    get: { sendFailAlertMessage != nil },
                    set: { if !$0 { sendFailAlertMessage = nil } }
                )
            ) {
                Button(localizationManager.localized("common_ok"), role: .cancel) {
                    sendFailAlertMessage = nil
                }
            } message: {
                Text(sendFailAlertMessage ?? "")
            }
    }

    /// 3A — wipe nested presents when switching hub tabs (stops Driving cascade).
    private func clearNestedHubSheetsForTabChange(to tab: HubTab) {
        print("WHERE_PHONE hubTab → \(String(describing: tab)) clear nested + pending")
        pendingHubSheet = nil
        showPlaces = false
        showRoutes = false
        showFamilyGroups = false
        showPetSoon = false
        showPetWizard = false
        showItemsSoon = false
        showFamilyCalendar = false
        showCrashSettings = false
        showMapTypeSheet = false
        showInvisibleHatSheet = false
        showAlwaysAllowSheet = false
        showSoftPaywall = false
        showSoftInvite = false
        showInviteRole = false
        showCrashConfirm = false
        selectedMember = nil
        showMemberImagePicker = false
        memberCropSource = nil
        if tab != .location {
            showLocationSystemSheet = false
        } else if preferLocationSystemSheetS2 {
            showLocationSystemSheet = true
            locationSheetIsFull = false
        } else {
            showLocationSystemSheet = false
            sheetExpansion = 0.08
            sheetDragStart = 0.08
        }
    }

    /// 1A — present nested sheet; if member/S2 location sheet blocks, dismiss first then flush.
    private func queueHubSheet(_ action: PendingHubSheet) {
        let blockedByMember = selectedMember != nil
        let blockedByS2 = preferLocationSystemSheetS2 && showLocationSystemSheet
        if blockedByMember || blockedByS2 {
            print("WHERE_PHONE pending set → \(String(describing: action)) blocked member=\(blockedByMember) s2=\(blockedByS2)")
            pendingHubSheet = action
            if blockedByMember {
                selectedMember = nil
            }
            if blockedByS2 {
                showLocationSystemSheet = false
            }
            // Flush on next runloop after dismiss animation starts.
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                self.flushPendingHubSheetIfNeeded(reason: "afterDismiss")
            }
            return
        }
        print("WHERE_PHONE present → \(String(describing: action))")
        applyPendingHubSheet(action)
    }

    private func flushPendingHubSheetIfNeeded(reason: String) {
        guard let action = pendingHubSheet else { return }
        pendingHubSheet = nil
        print("WHERE_PHONE pending flush reason=\(reason) → \(String(describing: action))")
        applyPendingHubSheet(action)
    }

    private func applyPendingHubSheet(_ action: PendingHubSheet) {
        switch action {
        case .places(let key):
            placesPreferredNameKey = key
            showPlaces = true
        case .routes:
            showRoutes = true
        case .familyGroups:
            showFamilyGroups = true
        case .mapType:
            showMapTypeSheet = true
        case .invisibleHat:
            showInvisibleHatSheet = true
        case .alwaysAllow:
            showAlwaysAllowSheet = true
        case .petWizard:
            showPetWizard = true
        case .petSoon:
            showPetSoon = true
        case .itemsSoon:
            showItemsSoon = true
        case .familyCalendar:
            showFamilyCalendar = true
        case .crashSettings:
            showCrashSettings = true
        case .softPaywall:
            showSoftPaywall = true
        case .softInvite:
            showSoftInvite = true
        case .inviteRole:
            showInviteRole = true
        }
    }

    /// X закрывает хаб → Удобный (`isPresented = false`), не «стек Назад».
    private var hubHeader: some View {
        HStack {
            // Title follows active tab (not always «Карта» on Subscription/Safety).
            Text(localizationManager.localized(hubTab.titleKey))
                .font(AladdinFamilyType.title2())
                .foregroundColor(.textPrimary)

            Spacer()

            Button {
                HapticFeedback.impact(.light)
                isPresented = false
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 28))
                    .foregroundColor(.textSecondary)
            }
            .accessibilityIdentifier("where_phone_hub_close")
            .accessibilityLabel(localizationManager.localized("common_close"))
        }
        .padding(Spacing.m)
    }

    /// Visible sheet height (Life360). Канон MAP-95-CLIP PASS — см. UNIFIED §3.1.
    /// full = 95% экрана − tab; mapStrip = geo − sheet − tab (layout, не overlay над Metal).
    /// Baseline до S1: `docs/competitors/WHERE_PHONE_SHEET_SETTINGS_BASELINE_BEFORE_S1_2026-11-09.md`
    private func locationSheetFullTarget(mapHeight: CGFloat, tabBarHeight: CGFloat) -> CGFloat {
        max(120, mapHeight * 0.95 - tabBarHeight)
    }

    private func locationSheetHeight(mapHeight: CGFloat, tabBarHeight: CGFloat) -> CGFloat {
        let usable = max(160, mapHeight - tabBarHeight)
        let fullH = locationSheetFullTarget(mapHeight: mapHeight, tabBarHeight: tabBarHeight)
        // Peek: grabber+chips only so map strip ≥ ~0.85 (symmetric to full cover 0.95).
        let peekH = max(110, usable * 0.12)
        let halfH = usable * 0.48
        if sheetExpansion <= 0.42 {
            let t = max(0, sheetExpansion) / 0.42
            return peekH + (halfH - peekH) * t
        }
        let t = (sheetExpansion - 0.42) / 0.58
        return halfH + (fullH - halfH) * min(1, max(0, t))
    }

    /// DIAG: sheet + mapStrip (CLIP). G1 full: (sheetH+tab)/geoH ≥ 0.90 · mapStrip/geoH ≤ 0.08.
    private func logS1bSheetHeight(reason: String, mapHeight: CGFloat, tabBarHeight: CGFloat, sheetH: CGFloat) {
        let fullTarget = locationSheetFullTarget(mapHeight: mapHeight, tabBarHeight: tabBarHeight)
        let mapStrip = max(0, mapHeight - sheetH - tabBarHeight)
        let sheetRatio = mapHeight > 0 ? (sheetH + tabBarHeight) / mapHeight : 0
        let stripRatio = mapHeight > 0 ? mapStrip / mapHeight : 0
        print(
            "WHERE_PHONE sheet S1b height reason=\(reason) sheetH=\(Int(sheetH)) geoH=\(Int(mapHeight)) " +
            "mapStrip=\(Int(mapStrip)) expansion=\(String(format: "%.2f", sheetExpansion)) " +
            "fullTarget=\(Int(fullTarget)) cover=\(String(format: "%.2f", sheetRatio)) " +
            "strip=\(String(format: "%.2f", stripRatio)) tab=\(Int(tabBarHeight))"
        )
    }

    private var sheetDragGesture: some Gesture {
        DragGesture(minimumDistance: 8, coordinateSpace: .local)
            .onChanged { value in
                if !sheetDragActive {
                    sheetDragActive = true
                    sheetDragStart = sheetExpansion
                }
                let span = max(locationPaneHeight, 400)
                let delta = -value.translation.height / span
                let next = min(1, max(0, sheetDragStart + delta))
                guard abs(next - sheetExpansion) >= 0.025 || next == 0 || next == 1 else { return }
                var transaction = Transaction()
                transaction.disablesAnimations = true
                withTransaction(transaction) {
                    sheetExpansion = next
                }
            }
            .onEnded { value in
                sheetDragActive = false
                let span = max(locationPaneHeight, 400)
                let delta = -value.translation.height / span
                let raw = min(1, max(0, sheetDragStart + delta))
                let snapped: CGFloat
                // B: full snap = 1.0 so height formula hits ~95% (not 0.95→~91%).
                if raw < 0.22 { snapped = 0.08 }
                else if raw < 0.62 { snapped = 0.42 }
                else { snapped = 1.0 }
                withAnimation(.spring(response: 0.34, dampingFraction: 0.88)) {
                    sheetExpansion = snapped
                }
                sheetDragStart = snapped
                let tabBarH: CGFloat = 64
                let geoH = max(locationPaneHeight, 400)
                let sheetH = locationSheetHeight(mapHeight: geoH, tabBarHeight: tabBarH)
                logS1bSheetHeight(reason: "snap", mapHeight: geoH, tabBarHeight: tabBarH, sheetH: sheetH)
                HapticFeedback.selection()
            }
    }

    /// Grabber + chips = one drag surface (Life360: pull the sheet, not only a 5pt capsule).
    private var sheetDragHeader: some View {
        VStack(spacing: 0) {
            Capsule()
                .fill(Color.secondaryGold.opacity(0.75))
                .frame(width: 48, height: 5)
                .padding(.top, 10)
                .padding(.bottom, 8)
            sheetChipStrip
                .padding(.bottom, Spacing.s)
        }
        .frame(maxWidth: .infinity)
        .contentShape(Rectangle())
        .background(Color.backgroundDark.opacity(0.97))
        .accessibilityIdentifier("where_phone_sheet_drag_handle")
        .accessibilityLabel(localizationManager.localized("map_sheet_drag_a11y"))
        .accessibilityHint(localizationManager.localized("map_sheet_drag_hint"))
        // simultaneous — chips stay tappable; vertical drag still resizes sheet.
        .simultaneousGesture(sheetDragGesture)
    }

    /// Map pan/zoom when sheet is peek/half and not mid-drag.
    private var mapInteractionEnabled: Bool {
        if #available(iOS 16.0, *), preferLocationSystemSheetS2 {
            return !locationSheetIsFull
        }
        return !sheetDragActive && sheetExpansion < 0.92
    }

    /// Expand location sheet to ~95% (CLIP expansion · S2 detent only if fallback on).
    private func expandLocationSheetToFull() {
        print("WHERE_PHONE sheet expandToFull requested (was full=\(locationSheetIsFull) expansion=\(String(format: "%.2f", sheetExpansion)) s2=\(preferLocationSystemSheetS2))")
        withAnimation(.interactiveSpring(response: 0.32, dampingFraction: 0.86)) {
            if #available(iOS 16.0, *), preferLocationSystemSheetS2 {
                locationSheetIsFull = true
            } else {
                sheetExpansion = 1.0
            }
        }
        print("WHERE_PHONE sheet expandToFull applied full=\(locationSheetIsFull) expansion=\(String(format: "%.2f", sheetExpansion))")
    }

    /// Binding for system detents without storing PresentationDetent on iOS 15-deployed type.
    @available(iOS 16.0, *)
    private var locationDetentBinding: Binding<PresentationDetent> {
        Binding(
            get: { locationSheetIsFull ? .fraction(0.95) : .medium },
            set: { newValue in
                let full = (newValue != .medium)
                print("WHERE_PHONE sheet detent set → \(full ? "fraction(0.95)" : "medium") (was full=\(locationSheetIsFull))")
                locationSheetIsFull = full
            }
        )
    }

    /// Full-screen Life360 canvas. Primary = CLIP (S1b) on all OS — MAP-95 PASS.
    /// S2 system detents only if `preferLocationSystemSheetS2` (emergency fallback).
    private var locationLife360Canvas: some View {
        GeometryReader { geo in
            let tabBarH: CGFloat = 64
            Group {
                if #available(iOS 16.0, *), preferLocationSystemSheetS2 {
                    locationLife360CanvasS2(geo: geo, tabBarH: tabBarH)
                } else {
                    locationLife360CanvasS1b(geo: geo, tabBarH: tabBarH)
                }
            }
            .onAppear {
                locationPaneHeight = geo.size.height
                let path = preferLocationSystemSheetS2 ? "S2" : "CLIP"
                print(
                    "WHERE_PHONE sheet canvas appear path=\(path) h=\(Int(geo.size.height)) " +
                    "full=\(locationSheetIsFull) expansion=\(String(format: "%.2f", sheetExpansion)) " +
                    "systemSheet=\(showLocationSystemSheet)"
                )
                if #available(iOS 16.0, *), preferLocationSystemSheetS2 {
                    showLocationSystemSheet = true
                } else {
                    showLocationSystemSheet = false
                }
            }
            .onChange(of: geo.size.height) { h in locationPaneHeight = h }
            .onChange(of: locationSheetIsFull) { full in
                print("WHERE_PHONE sheet full flag → \(full)")
            }
            .onChange(of: sheetExpansion) { exp in
                print("WHERE_PHONE sheet expansion → \(String(format: "%.2f", exp))")
            }
        }
        .accessibilityIdentifier("where_phone_tab_location")
    }

    /// S2: map + chrome; bottom sheet via system detents (medium / 0.95). Tab bar sticky inside sheet.
    @available(iOS 16.0, *)
    private func locationLife360CanvasS2(geo: GeometryProxy, tabBarH: CGFloat) -> some View {
        let fabBottomPad = locationSheetIsFull
            ? (geo.size.height * 0.10 + tabBarH)
            : max(220, geo.size.height * 0.56)
        return ZStack(alignment: .bottom) {
            FamilyHubLiveMapRepresentable(
                region: $mapRegion,
                coordinate: mapCoordinate,
                title: friendlyPointName(mapPointName),
                mapTypeRaw: mapTypeRaw,
                pinDiameter: pinDiameterForSize(pinSizeRaw),
                interactionEnabled: mapInteractionEnabled,
                cameraToken: mapCameraToken,
                quietRadiusMeters: quietMeters,
                onPinSelected: {
                    openMemberFromMapPin()
                }
            )
            .ignoresSafeArea()
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .accessibilityIdentifier("where_phone_map_pane")

            Color.black.opacity(locationSheetIsFull ? 0.42 : 0.18)
                .ignoresSafeArea()
                .allowsHitTesting(false)

            VStack(spacing: 0) {
                hubHeader
                    .background(
                        LinearGradient(
                            colors: [
                                Color.backgroundDark.opacity(0.78),
                                Color.backgroundDark.opacity(0.0)
                            ],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    // Header only — do not let empty VStack steal FAB/map hits.
                    .zIndex(2)

                HStack {
                    Spacer()
                    mapStatusBadges
                }
                .padding(.horizontal, Spacing.m)
                .padding(.top, 4)
                .zIndex(2)

                Spacer(minLength: 0)
                    .allowsHitTesting(false)

                HStack {
                    Spacer()
                    mapFabStack
                }
                .padding(.trailing, Spacing.m)
                .padding(.bottom, fabBottomPad)
                .opacity(locationSheetIsFull ? 0.25 : 1)
                .allowsHitTesting(!locationSheetIsFull)
                .zIndex(5)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        }
        .sheet(isPresented: $showLocationSystemSheet, onDismiss: {
            flushPendingHubSheetIfNeeded(reason: "s2LocationDismiss")
        }) {
            locationSystemSheetContent(tabBarH: tabBarH)
                .presentationDetents([.medium, .fraction(0.95)], selection: locationDetentBinding)
                .presentationDragIndicator(.visible)
                .interactiveDismissDisabled(true)
                .modifier(LocationSheetChromeModifier())
        }
        .onChange(of: hubTab) { tab in
            // Tab clear owns nested flags (3A). S2 only re-opens location sheet here.
            if preferLocationSystemSheetS2 {
                showLocationSystemSheet = (tab == .location)
                if tab == .location {
                    locationSheetIsFull = false
                }
            }
        }
    }

    @available(iOS 16.0, *)
    private func locationSystemSheetContent(tabBarH: CGFloat) -> some View {
        VStack(spacing: 0) {
            sheetChipStrip
                .padding(.top, Spacing.s)
                .padding(.bottom, Spacing.s)

            ScrollViewReader { proxy in
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: Spacing.m) {
                        mapMetaSheetBlock
                        peopleSheetSection.id(SheetChip.people)
                        petsSheetSection.id(SheetChip.pets)
                        itemsSheetSection.id(SheetChip.items)
                        placesSheetSection.id(SheetChip.places)
                        eventsSheetSection.id(SheetChip.events)
                        lostCard.id("where_phone_lost_card")
                    }
                    .padding(.horizontal, Spacing.m)
                    .padding(.bottom, Spacing.xl)
                }
                .coordinateSpace(name: "wherePhoneSheetScroll")
                .onPreferenceChange(WherePhoneSectionFramesKey.self) { frames in
                    updateActiveChipFromScroll(frames)
                }
                .onChange(of: chipScrollRequest) { _ in
                    guard chipScrollRequest > 0 else { return }
                    withAnimation(.easeInOut(duration: 0.28)) {
                        if activeChip == .events {
                            proxy.scrollTo("where_phone_lost_card", anchor: .top)
                        } else {
                            proxy.scrollTo(activeChip, anchor: .top)
                        }
                    }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                        isChipProgrammaticScroll = false
                    }
                }
            }
            .frame(maxHeight: .infinity)

            hubTabBar
                .frame(height: tabBarH)
                .background(Color.backgroundDark.opacity(0.98))
        }
        .background(Color.backgroundDark.opacity(0.98))
        .accessibilityIdentifier("where_phone_system_sheet")
    }

    /// MAP-95-CLIP (iOS 15): VStack layout — map frame = только верхняя полоска; sheet+tab ниже.
    /// MKMapView/Metal не может «просветить» поверх sheet (в отличие от overlay/z-order).
    private func locationLife360CanvasS1b(geo: GeometryProxy, tabBarH: CGFloat) -> some View {
        let sheetH = locationSheetHeight(mapHeight: geo.size.height, tabBarHeight: tabBarH)
        let mapStripH = max(36, geo.size.height - sheetH - tabBarH)
        return VStack(spacing: 0) {
            ZStack(alignment: .top) {
                FamilyHubLiveMapRepresentable(
                    region: $mapRegion,
                    coordinate: mapCoordinate,
                    title: friendlyPointName(mapPointName),
                    mapTypeRaw: mapTypeRaw,
                    pinDiameter: pinDiameterForSize(pinSizeRaw),
                    interactionEnabled: mapInteractionEnabled,
                    cameraToken: mapCameraToken,
                    quietRadiusMeters: quietMeters,
                    onPinSelected: {
                        openMemberFromMapPin()
                    }
                )
                .frame(width: geo.size.width, height: mapStripH)
                .clipped()
                .accessibilityIdentifier("where_phone_map_pane")

                Color.black.opacity(0.08 + 0.35 * sheetExpansion)
                    .frame(width: geo.size.width, height: mapStripH)
                    .allowsHitTesting(false)

                VStack(spacing: 0) {
                    hubHeader
                        .background(
                            LinearGradient(
                                colors: [
                                    Color.backgroundDark.opacity(0.78),
                                    Color.backgroundDark.opacity(0.0)
                                ],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )

                    HStack {
                        Spacer()
                        mapStatusBadges
                    }
                    .padding(.horizontal, Spacing.m)
                    .padding(.top, 4)

                    Spacer(minLength: 0)

                    HStack {
                        Spacer()
                        mapFabStack
                    }
                    .padding(.trailing, Spacing.m)
                    .padding(.bottom, Spacing.s)
                    // Keep FABs tappable until sheet is nearly full (was 0.55 → dead controls).
                    .opacity(sheetExpansion > 0.88 ? 0.25 : 1)
                    .allowsHitTesting(sheetExpansion < 0.92)
                    .zIndex(5)
                }
                .frame(width: geo.size.width, height: mapStripH, alignment: .top)
            }
            .frame(width: geo.size.width, height: mapStripH)
            .clipped()

            VStack(spacing: 0) {
                sheetDragHeader
                if sheetDragActive {
                    Color.backgroundMedium.opacity(0.4)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    locationSheetScrollBody
                }
            }
            .frame(width: geo.size.width, height: sheetH, alignment: .top)
            .background(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(Color.backgroundDark.opacity(0.98))
                    .shadow(color: .black.opacity(0.4), radius: 16, y: -4)
            )
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))

            hubTabBar
                .frame(width: geo.size.width, height: tabBarH)
                .background(Color.backgroundDark.opacity(0.98))
        }
        .frame(width: geo.size.width, height: geo.size.height, alignment: .top)
        .onAppear {
            logS1bSheetHeight(
                reason: "appear",
                mapHeight: geo.size.height,
                tabBarHeight: tabBarH,
                sheetH: sheetH
            )
        }
        .onChange(of: sheetExpansion) { _ in
            let h = locationSheetHeight(mapHeight: geo.size.height, tabBarHeight: tabBarH)
            if abs(sheetExpansion - 1.0) < 0.001 || abs(sheetExpansion - 0.42) < 0.001 || abs(sheetExpansion - 0.08) < 0.001 {
                logS1bSheetHeight(
                    reason: "expansionSettled",
                    mapHeight: geo.size.height,
                    tabBarHeight: tabBarH,
                    sheetH: h
                )
            }
        }
    }

    private var locationSheetScrollBody: some View {
        ScrollViewReader { proxy in
            ScrollView(.vertical, showsIndicators: true) {
                VStack(spacing: Spacing.m) {
                    mapMetaSheetBlock
                    peopleSheetSection.id(SheetChip.people)
                    petsSheetSection.id(SheetChip.pets)
                    itemsSheetSection.id(SheetChip.items)
                    placesSheetSection.id(SheetChip.places)
                    eventsSheetSection.id(SheetChip.events)
                    lostCard.id("where_phone_lost_card")
                }
                .padding(.horizontal, Spacing.m)
                .padding(.bottom, Spacing.xl)
            }
            .coordinateSpace(name: "wherePhoneSheetScroll")
            .onPreferenceChange(WherePhoneSectionFramesKey.self) { frames in
                updateActiveChipFromScroll(frames)
            }
            .onChange(of: chipScrollRequest) { _ in
                guard chipScrollRequest > 0 else { return }
                withAnimation(.easeInOut(duration: 0.28)) {
                    if activeChip == .events {
                        proxy.scrollTo("where_phone_lost_card", anchor: .top)
                    } else {
                        proxy.scrollTo(activeChip, anchor: .top)
                    }
                }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                    isChipProgrammaticScroll = false
                }
            }
        }
        .frame(maxHeight: .infinity)
    }

    private var mapStatusBadges: some View {
        VStack(alignment: .trailing, spacing: 6) {
            // QA-08 A: refresh my place + accuracy ±m · time.
            Button {
                HapticFeedback.selection()
                liveLocation.requestFreshFix()
                ToastManager.shared.showSuccess(
                    localizationManager.localized("map_refresh_my_place_toast")
                )
            } label: {
                HStack(spacing: 6) {
                    Image(systemName: "location.north.line.fill")
                        .font(.caption.weight(.bold))
                    Text(localizationManager.localized("map_refresh_my_place"))
                        .font(.caption.weight(.bold))
                }
                .foregroundColor(.backgroundDark)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(Color.secondaryGold.opacity(0.95))
                .clipShape(Capsule())
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("where_phone_refresh_my_place")

            if liveLocation.accuracyMeters >= 0, mapCoordinate != nil {
                Text(
                    String(
                        format: localizationManager.localized("map_accuracy_meters_format"),
                        Int(liveLocation.accuracyMeters.rounded())
                    )
                )
                .font(.caption2.weight(.bold))
                .foregroundColor(.backgroundDark)
                .padding(.horizontal, 10)
                .padding(.vertical, 5)
                .background(Color.white.opacity(0.88))
                .clipShape(Capsule())
                .accessibilityIdentifier("where_phone_accuracy_badge")
            }

            if mapCoordinate == nil || mapPinSource == .none {
                Text(localizationManager.localized("map_live_no_signal"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.backgroundDark)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.secondaryGold.opacity(0.9))
                    .clipShape(Capsule())
                    .accessibilityIdentifier("where_phone_no_signal_badge")
            }
            if inQuietZone {
                Text(localizationManager.localized("map_quiet_active_badge"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.backgroundDark)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.secondaryGold.opacity(0.9))
                    .clipShape(Capsule())
            }
            // Wall-clock of last GPS fix. Hide when «только что» (same minute as now) — avoids «С 12:24» noise.
            if mapCoordinate != nil, mapPinSource != .none, let at = mapPointAt,
               Date().timeIntervalSince(at) >= 60 {
                Text(
                    String(
                        format: localizationManager.localized("dens_map_pin_time"),
                        Self.wallClockTime(at)
                    )
                )
                .font(.caption.weight(.bold))
                .foregroundColor(.backgroundDark)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(Color.secondaryGold.opacity(0.92))
                .clipShape(Capsule())
                .accessibilityIdentifier("where_phone_pin_time_badge")
            }
            if mapPinSource == .live,
               let speed = liveLocation.speedKmh,
               speed > 0,
               speed <= 140,
               !inQuietZone {
                // Cap UI at 140 km/h — GPS spikes (e.g. 181) are noise, not real driving.
                Text(
                    String(
                        format: localizationManager.localized("map_live_speed_online"),
                        speed
                    )
                )
                    .font(.caption.weight(.bold))
                    .foregroundColor(.backgroundDark)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.secondaryGold)
                    .clipShape(Capsule())
                    .accessibilityIdentifier("where_phone_speed_badge")
            }
        }
    }

    private var sheetChipStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: Spacing.s) {
                ForEach(SheetChip.allCases) { chip in
                    Button {
                        HapticFeedback.selection()
                        print("WHERE_PHONE sheet chip tap → \(chip)")
                        // Expand only if not already near-full (avoids layout thrash on iOS 15).
                        if sheetExpansion < 0.95 {
                            expandLocationSheetToFull()
                        }
                        isChipProgrammaticScroll = true
                        activeChip = chip
                        chipScrollRequest += 1
                    } label: {
                        VStack(spacing: 4) {
                            // Chips Where — всегда Классика (SF), без Glyph/Blue/Black (P0.4).
                            Image(systemName: chip.systemImage)
                                .font(.system(size: 16, weight: .semibold))
                            Text(localizationManager.localized(chip.titleKey))
                                .font(.caption2.weight(.semibold))
                                .lineLimit(1)
                        }
                        .foregroundColor(activeChip == chip ? Color.backgroundDark : Color.textSecondary)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.s)
                        .background(
                            Capsule()
                                .fill(activeChip == chip ? Color.secondaryGold : Color.backgroundMedium.opacity(0.55))
                        )
                        .overlay(
                            Capsule()
                                .stroke(Color.secondaryGold.opacity(activeChip == chip ? 0 : 0.35), lineWidth: 1)
                        )
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("where_phone_chip_\(chip.rawValue)")
                }
            }
            .padding(.horizontal, Spacing.m)
        }
        .accessibilityIdentifier("where_phone_chip_strip")
    }

    private var peopleSheetSection: some View {
        sectionFrame(.people) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                /// JOB08 CapCut · H17 FamilyWalk · People hero · UI 320×220 (map bg kept).
                peopleFamilyHeroWalk
                familyGroupsFilterBar
                inviteBanner
                shareCard
                trailCard
            }
        }
    }

    /// JOB08b · Walk variant · «семья на карте» · не OB_*.
    private var peopleFamilyHeroWalk: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Image("ICON_ALIVE_HERO_H17_FamilyWalk")
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .frame(height: 220)
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                .accessibilityHidden(true)
            Text(localizationManager.localized("where_phone_family_hero_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized("where_phone_family_hero_body"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("where_phone_people_hero_family_walk")
    }

    /// Circles B — filter people list by group label (same family roster).
    private var familyGroupsFilterBar: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("family_groups_map_filter"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.textSecondary)
                Spacer()
                Button {
                    queueHubSheet(.familyGroups)
                } label: {
                    Text(localizationManager.localized("family_groups_title"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_open_groups")
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Spacing.s) {
                    groupFilterChip(
                        title: localizationManager.localized("family_groups_filter_all"),
                        selected: mapGroupFilterId == nil
                    ) {
                        mapGroupFilterId = nil
                        FamilyGroupLabelStore.selectedFilterGroupId = nil
                        HapticFeedback.selection()
                    }
                    ForEach(familyGroups) { group in
                        groupFilterChip(
                            title: String(
                                format: localizationManager.localized("family_groups_filter_group"),
                                group.title
                            ),
                            selected: mapGroupFilterId == group.id
                        ) {
                            mapGroupFilterId = group.id
                            FamilyGroupLabelStore.selectedFilterGroupId = group.id
                            HapticFeedback.selection()
                        }
                    }
                }
            }
            .accessibilityIdentifier("where_phone_group_filter")
        }
        .onAppear {
            familyGroups = FamilyGroupLabelStore.load()
            mapGroupFilterId = FamilyGroupLabelStore.selectedFilterGroupId
        }
    }

    private func groupFilterChip(title: String, selected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundColor(selected ? .backgroundDark : .secondaryGold)
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
                .background(selected ? Color.secondaryGold : Color.clear)
                .overlay(Capsule().stroke(Color.secondaryGold.opacity(0.45), lineWidth: 1))
                .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }

    private var petsSheetSection: some View {
        sectionFrame(.pets) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                /// JOB05 CapCut · H15 dog hero · Pets empty · UI 120×120.
                petsHeroDogRow
                if !savedPets.isEmpty {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        ForEach(savedPets) { pet in
                            HStack(spacing: Spacing.m) {
                                Image(pet.heroAssetName)
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 56, height: 56)
                                    .clipShape(Circle())
                                    .accessibilityHidden(true)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(pet.name)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundColor(.textPrimary)
                                    if !pet.breed.isEmpty {
                                        Text(pet.breed)
                                            .font(.caption)
                                            .foregroundColor(.textSecondary)
                                    }
                                }
                                Spacer()
                            }
                            .padding(Spacing.m)
                            .aladdinProductCard(cornerRadius: CornerRadius.medium)
                        }
                        Text(localizationManager.localized("map_soon_pet_body"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                soonSectionCard(
                    titleKey: "map_soon_pet_title",
                    bodyKey: "map_soon_pet_body",
                    ctaKey: "pet_add_title",
                    symbol: "pawprint.fill"
                ) {
                    queueHubSheet(.petWizard)
                }
            }
        }
    }

    /// JOB05 CapCut · dog sticker · transparent PNG · Pets chip hero.
    private var petsHeroDogRow: some View {
        HStack(alignment: .center, spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized("where_phone_pets_hero_title"))
                    .font(AladdinFamilyType.title3())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("where_phone_pets_hero_body"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 8)
            Image("ICON_ALIVE_HERO_H15_PetDog")
                .resizable()
                .scaledToFit()
                .frame(width: 120, height: 120)
                .accessibilityHidden(true)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("where_phone_pets_hero_dog")
    }

    private var itemsSheetSection: some View {
        sectionFrame(.items) {
            soonSectionCard(
                titleKey: "items_promo_title",
                bodyKey: "items_promo_body",
                ctaKey: "items_promo_cta",
                symbol: "key.fill"
            ) {
                queueHubSheet(.itemsSoon)
            }
        }
    }

    private var placesSheetSection: some View {
        sectionFrame(.places) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                // Wave B JOB01 — 3D place pin (Life360 H14). One slot: Places sheet hero.
                placesHeroLandPinRow
                placesCard
                // S19d densitiy — stops today (real geofences only; empty = honest).
                densPlacesDayCard
                // S19e — 30-day history upsell (B1 copy, short).
                densLocationHistoryCard
                HStack(spacing: Spacing.s) {
                    placeSuggestChip("map_places_suggest_home")
                    placeSuggestChip("map_places_suggest_school")
                    placeSuggestChip("map_places_suggest_work")
                    placeSuggestChip("map_places_suggest_other")
                }
                actionButton("map_places_manage", id: "where_phone_manage_places") {
                    queueHubSheet(.places(preferredNameKey: nil))
                }
            }
        }
    }

    /// JOB01 CapCut hero · UI 120×120 · transparent PNG · no checker in app.
    private var placesHeroLandPinRow: some View {
        HStack(alignment: .center, spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized("where_phone_places_title"))
                    .font(AladdinFamilyType.title3())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("where_phone_places_empty"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 8)
            Image("ICON_ALIVE_HERO_H14_PlaceLandPin")
                .resizable()
                .scaledToFit()
                .frame(width: 120, height: 120)
                .accessibilityHidden(true)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("where_phone_places_hero_land_pin")
    }

    private var densPlacesDayCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("dens_places_day_title"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textPrimary)
            let names = densTodayPlaceNames()
            if names.isEmpty {
                Text(localizationManager.localized("dens_places_day_empty"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Button {
                    HapticFeedback.selection()
                    queueHubSheet(.places(preferredNameKey: nil))
                } label: {
                    Text(localizationManager.localized("map_member_save_place"))
                        .font(.caption.weight(.bold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_places_day_save_empty")
            } else {
                ForEach(names, id: \.self) { name in
                    HStack(spacing: Spacing.s) {
                        Image(systemName: "mappin.circle.fill")
                            .foregroundColor(.secondaryGold)
                        // C1: no Life360 «В » / «At » prefix on stay titles.
                        Text(Self.streetTitleWithoutAtPrefix(name))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.textPrimary)
                        Spacer(minLength: 0)
                        Button {
                            HapticFeedback.selection()
                            queueHubSheet(.places(preferredNameKey: nil))
                        } label: {
                            Text(localizationManager.localized("map_member_save_place"))
                                .font(.caption2.weight(.bold))
                                .foregroundColor(.secondaryGold)
                                .lineLimit(1)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.28))
        )
        .accessibilityIdentifier("where_phone_places_day")
    }

    private var densLocationHistoryCard: some View {
        Button {
            SelectionHaptic.selection()
            if let leave = onLeaveToNavigate {
                leave(.tariffs)
            } else {
                navigationManager.navigateTo(.tariffs)
            }
        } label: {
            HStack(spacing: Spacing.m) {
                Image(systemName: "calendar")
                    .foregroundColor(.secondaryGold)
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("location_history_30d_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("location_history_30d_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.92))
                }
                Spacer()
                Text(localizationManager.localized("location_history_30d_cta"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.secondaryGold)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.28))
            )
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("where_phone_history_30d")
    }

    /// Real saved places only — no invented “today stops” timeline without events API.
    private func densTodayPlaceNames() -> [String] {
        let key = "geofences_settings"
        guard let data = UserDefaults.standard.data(forKey: key),
              let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) else {
            return []
        }
        return decoded
            .map(\.name)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
    }

    private func placeSuggestChip(_ key: String) -> some View {
        Button {
            runWherePhoneTap(id: "where_phone_\(key)") {
                queueHubSheet(.places(preferredNameKey: key))
            }
        } label: {
            Text(localizationManager.localized(key))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
                .overlay(Capsule().stroke(Color.secondaryGold.opacity(0.45), lineWidth: 1))
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("where_phone_\(key)")
    }

    private var eventsSheetSection: some View {
        sectionFrame(.events) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                // Wave B JOB02 — calendar+pencil (Life360 H14/H09). One slot: Events sheet.
                eventsHeroCalendarRow
                VStack(alignment: .leading, spacing: Spacing.s) {
                    if localEvents.isEmpty {
                        Text(localizationManager.localized("family_cal_empty"))
                            .font(.subheadline)
                            .foregroundColor(.textSecondary)
                    } else {
                        ForEach(localEvents.prefix(3)) { event in
                            Text("\(event.title) · \(event.place)")
                                .font(.subheadline)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    Text(localizationManager.localized("family_cal_local_only"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    actionButton("family_cal_add", id: "where_phone_add_event") {
                        queueHubSheet(.familyCalendar)
                    }
                }
                .padding(Spacing.m)
                .frame(maxWidth: .infinity, alignment: .leading)
                .aladdinProductCard(cornerRadius: CornerRadius.large)
            }
        }
    }

    /// JOB02 CapCut · UI 96×96 · transparent PNG · Events chip only (not Places).
    private var eventsHeroCalendarRow: some View {
        HStack(alignment: .center, spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized("family_cal_title"))
                    .font(AladdinFamilyType.title3())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("family_cal_empty"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 8)
            Image("ICON_ALIVE_HERO_H14_CalendarPencil")
                .resizable()
                .scaledToFit()
                .frame(width: 96, height: 96)
                .accessibilityHidden(true)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("where_phone_events_hero_calendar")
    }

    private var inviteBanner: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("map_invite_banner_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized("map_create_circle_teaser"))
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(.textSecondary)
            actionButton("map_invite_banner_cta", id: "where_phone_invite_banner") {
                showInviteRole = true
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private func soonSectionCard(
        titleKey: String,
        bodyKey: String,
        ctaKey: String,
        symbol: String,
        action: @escaping () -> Void
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.s) {
                Image(systemName: symbol)
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized(titleKey))
                    .font(AladdinFamilyType.title3())
                    .foregroundColor(.textPrimary)
            }
            Text(localizationManager.localized(bodyKey))
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            actionButton(ctaKey, id: "where_phone_soon_\(titleKey)") {
                action()
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private func soonSheet(
        titleKey: String,
        bodyKey: String,
        isPresented: Binding<Bool>
    ) -> some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized(titleKey))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized(bodyKey))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Spacer()
                Button {
                    isPresented.wrappedValue = false
                } label: {
                    Text(localizationManager.localized("map_soon_ok"))
                        .font(AladdinFamilyType.subheadline(weight: .semibold))
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                isPresented.wrappedValue = false
            })
        }
    }

    private func sectionFrame<Content: View>(
        _ chip: SheetChip,
        @ViewBuilder content: () -> Content
    ) -> some View {
        content()
            .background(
                GeometryReader { geo in
                    Color.clear.preference(
                        key: WherePhoneSectionFramesKey.self,
                        value: [chip.rawValue: geo.frame(in: .named("wherePhoneSheetScroll")).minY]
                    )
                }
            )
    }

    private func updateActiveChipFromScroll(_ frames: [Int: CGFloat]) {
        guard !isChipProgrammaticScroll, !frames.isEmpty else { return }
        // Highlight the section whose top is nearest below the sticky chips (~0…80).
        let threshold: CGFloat = 72
        let ranked = frames.compactMap { raw, minY -> (SheetChip, CGFloat)? in
            guard let chip = SheetChip(rawValue: raw) else { return nil }
            return (chip, minY)
        }
        .sorted { abs($0.1 - threshold) < abs($1.1 - threshold) }
        if let best = ranked.first, activeChip != best.0 {
            activeChip = best.0
            // Round2 S10: haptic on finger scroll-spy, same as chip tap.
            SelectionHaptic.selection()
        }
    }

    /// §17 step 3 — existing DrivingReportsModal (honest empty/trips, no fake metrics).
    private var drivingTabPane: some View {
        DrivingReportsModal(
            isPresented: Binding(
                get: { hubTab == .driving },
                set: { if !$0 { hubTab = .location } }
            )
        )
        .environmentObject(localizationManager)
        .environmentObject(navigationManager)
        .environmentObject(analyticsViewModel)
        .accessibilityIdentifier("where_phone_tab_driving")
    }

    /// JOB11–12 · CapCut heroes · UI ~280×200 · copy from Life360 H06/H13 adapted to ALADDIN (no competitor name).
    private var safetySOSEducationCarousel: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("sos_edu_nav_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)

            TabView(selection: $sosEduPage) {
                sosEduIntroPage.tag(0)
                sosEduReleasePage.tag(1)
            }
            .tabViewStyle(.page(indexDisplayMode: .automatic))
            .frame(height: 420)
            .accessibilityIdentifier("where_phone_safety_sos_edu_pager")
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
    }

    private var sosEduIntroPage: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Image("ICON_ALIVE_HERO_H06_SOSIntro")
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .frame(height: 200)
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                .accessibilityHidden(true)
            Text(localizationManager.localized("sos_edu_intro_title"))
                .font(AladdinFamilyType.subheadline(weight: .semibold))
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
            ForEach(
                ["sos_edu_intro_bullet_1", "sos_edu_intro_bullet_2", "sos_edu_intro_bullet_3"],
                id: \.self
            ) { key in
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.secondaryGold)
                        .font(.caption)
                    Text(localizationManager.localized(key))
                        .font(AladdinFamilyType.caption())
                        .foregroundColor(.white.opacity(0.92))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            Button {
                HapticFeedback.selection()
                withAnimation { sosEduPage = 1 }
            } label: {
                Text(localizationManager.localized("sos_edu_intro_cta"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.secondaryGold)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("where_phone_sos_edu_intro_cta")
            Spacer(minLength: 0)
        }
        .padding(.bottom, Spacing.s)
        .accessibilityIdentifier("where_phone_safety_sos_intro_hero")
    }

    private var sosEduReleasePage: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Image("ICON_ALIVE_HERO_H13_SOSRelease")
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .frame(height: 200)
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                .accessibilityHidden(true)
            Text(localizationManager.localized("sos_edu_release_title"))
                .font(AladdinFamilyType.subheadline(weight: .semibold))
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
            Text(localizationManager.localized("sos_edu_release_cta"))
                .font(.caption.weight(.bold))
                .foregroundColor(.secondaryGold)
            Spacer(minLength: 0)
        }
        .padding(.bottom, Spacing.s)
        .accessibilityIdentifier("where_phone_safety_sos_release_hero")
    }

    /// §17 step 3 — Safety chrome: crash toggle + settings + contacts count (no fake dispatch).
    private var safetyTabPane: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "shield.fill")
                        .font(.title2.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                    Text(localizationManager.localized("map_hub_safety_title"))
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(.textPrimary)
                }

                Text(localizationManager.localized("map_hub_safety_body"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)

                Toggle(isOn: $crashConsentAccepted) {
                    Text(localizationManager.localized("crash_consent_accept"))
                        .font(AladdinFamilyType.subheadline(weight: .semibold))
                        .foregroundColor(.textPrimary)
                }
                .tint(Color.secondaryGold)
                .accessibilityIdentifier("where_phone_safety_crash_toggle")
                .onAppear {
                    // Align runtime with stored consent (settings modal may have started already).
                    if crashConsentAccepted {
                        Task { try? await CrashDetectionManager.shared.startMonitoring() }
                    }
                }

                Text(
                    String(
                        format: localizationManager.localized("map_hub_safety_contacts_fmt"),
                        emergencyContactsCount()
                    )
                )
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(.white.opacity(0.92))

                Text(localizationManager.localized("crash_limits_body"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)

                /// JOB11–12 CapCut · H06 intro + H13 release · Safety SOS education (hold unchanged).
                safetySOSEducationCarousel

                Text(localizationManager.localized("map_hub_safety_sos_note"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)

                FamilySOSHoldButton()
                    .environmentObject(localizationManager)
                    .id("where_phone_sos_hold_anchor")

                actionButton("crash_confirm_preview_cta", id: "where_phone_crash_confirm") {
                    showCrashConfirm = true
                }

                Text(localizationManager.localized("map_soon_tile_title") + " · " + localizationManager.localized("map_soon_tile_body"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                Text(localizationManager.localized("map_soon_evac_title") + " · " + localizationManager.localized("map_soon_evac_body"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)

                actionButton("map_hub_safety_open_settings", id: "where_phone_safety_settings") {
                    showCrashSettings = true
                }
            }
            .padding(Spacing.l)
            .frame(maxWidth: .infinity, alignment: .leading)
            .stormGlassCard(cornerRadius: CornerRadius.large)
            .padding(Spacing.m)
        }
        .accessibilityIdentifier("where_phone_tab_safety")
    }

    /// §17 step 3 — thin subscription chrome → close hub + navigate Tariffs (not full screen embed).
    private var subscriptionTabPane: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                HStack(spacing: Spacing.s) {
                    // A06 Premium — Золото/Значки; Классика = SF crown (P2 one-slot).
                    AliveGlyph(id: .premium, size: 28) {
                        Image(systemName: "crown.fill")
                            .font(.title2.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                    Text(localizationManager.localized("map_hub_subscription_title"))
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(.textPrimary)
                }
                Text(localizationManager.localized("map_hub_subscription_body"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                actionButton("map_hub_subscription_cta", id: "where_phone_open_tariffs") {
                    leaveHubThenNavigate(to: NavigationManager.ALADDINScreen.tariffs)
                }
            }
            .padding(Spacing.l)
            .frame(maxWidth: .infinity, alignment: .leading)
            .stormGlassCard(cornerRadius: CornerRadius.large)
            .padding(Spacing.m)
        }
        .accessibilityIdentifier("where_phone_tab_subscription")
    }

    private func leaveHubThenNavigate(to screen: NavigationManager.ALADDINScreen) {
        if let onLeaveToNavigate {
            onLeaveToNavigate(screen)
            return
        }
        // Fallback if presented without parent callback.
        isPresented = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            navigationManager.navigateTo(screen)
        }
    }

    private func emergencyContactsCount() -> Int {
        guard let data = UserDefaults.standard.data(forKey: "emergency_contacts"),
              let contacts = try? JSONDecoder().decode([EmergencyContact].self, from: data) else {
            return 0
        }
        return contacts.count
    }

    private var mapFabStack: some View {
        VStack(spacing: Spacing.s) {
            Button {
                print("WHERE_PHONE FAB map-type tap")
                HapticFeedback.selection()
                queueHubSheet(.mapType)
            } label: {
                Image("FIG_L03_FABLayers")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 48, height: 48)
                    .contentShape(Circle())
                    .clipShape(Circle())
                    .overlay(Circle().stroke(Color.secondaryGold.opacity(0.35), lineWidth: 1))
            }
            .buttonStyle(MapFabPressStyle())
            .accessibilityIdentifier("where_phone_fab_map_type")

            fabButton(systemImage: "location.fill", id: "where_phone_fab_locate", aliveIcon: .fabLocate) {
                print("WHERE_PHONE FAB locate tap")
                HapticFeedback.selection()
                if let coordinate = mapCoordinate {
                    mapRegion.center = coordinate
                    mapCameraToken += 1
                } else {
                    locatorHint = localizationManager.localized("map_live_no_signal")
                }
            }
            .accessibilityLabel(localizationManager.localized("map_live_locate_me"))

            fabButton(systemImage: "arrow.triangle.turn.up.right.diamond.fill", id: "where_phone_fab_routes") {
                print("WHERE_PHONE FAB routes tap")
                HapticFeedback.selection()
                queueHubSheet(.routes)
            }

            // Round2 S20/S27: Life360-style «шапка-невидимка» entry (quiet zone radius).
            fabButton(systemImage: "eye.slash.fill", id: "where_phone_fab_invisible_hat") {
                print("WHERE_PHONE FAB invisible-hat tap")
                HapticFeedback.selection()
                queueHubSheet(.invisibleHat)
            }
            .accessibilityLabel(localizationManager.localized("map_create_invisible_hat"))
        }
        .contentShape(Rectangle())
    }

    private func fabButton(
        systemImage: String,
        id: String,
        aliveIcon: AliveIconID? = nil,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Group {
                if let aliveIcon {
                    AliveGlyph(id: aliveIcon, size: 34) {
                        Image(systemName: systemImage)
                            .font(.body.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                } else {
                    Image(systemName: systemImage)
                        .font(.body.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
            }
            .frame(width: 48, height: 48)
            .contentShape(Circle())
            .background(Color.backgroundMedium.opacity(0.92))
            .clipShape(Circle())
            .overlay(Circle().stroke(Color.secondaryGold.opacity(0.4), lineWidth: 1))
        }
        .buttonStyle(MapFabPressStyle())
        .accessibilityIdentifier(id)
    }

    /// P4.3: лёгкий spring на всех FAB при тапе (логика та же).
    private struct MapFabPressStyle: ButtonStyle {
        func makeBody(configuration: Configuration) -> some View {
            configuration.label
                .scaleEffect(configuration.isPressed ? 0.92 : 1.0)
                .animation(
                    .spring(response: 0.25, dampingFraction: 0.55),
                    value: configuration.isPressed
                )
        }
    }

    private var mapTypeSheet: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_type_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                ForEach(HubMapType.allCases) { type in
                    Button {
                        mapTypeRaw = type.rawValue
                        showMapTypeSheet = false
                    } label: {
                        HStack {
                            Text(localizationManager.localized(type.titleKey))
                                .font(AladdinFamilyType.subheadline(weight: .semibold))
                                .foregroundColor(.textPrimary)
                            Spacer()
                            if mapTypeRaw == type.rawValue {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.secondaryGold)
                            }
                        }
                        .padding(Spacing.m)
                        .stormGlassCard(cornerRadius: CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                }
                Button {
                    showMapTypeSheet = false
                    queueHubSheet(.petSoon)
                } label: {
                    HStack {
                        Image(systemName: "pawprint.fill")
                            .foregroundColor(.secondaryGold)
                        Text(localizationManager.localized("map_soon_pet_title"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                        Spacer()
                        Text(localizationManager.localized("map_soon_ok"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.m)
                    .stormGlassCard(cornerRadius: CornerRadius.medium)
                }
                .buttonStyle(.plain)
                Spacer()
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                showMapTypeSheet = false
            })
        }
    }

    private var alwaysAllowSheet: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                /// JOB09 CapCut · H25 FamilyHug Stand · Always Allow · UI 320×220.
                Image("ICON_ALIVE_HERO_H25_FamilyHugStand")
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity)
                    .frame(height: 200)
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    .accessibilityHidden(true)
                    .accessibilityIdentifier("where_phone_always_hero_hug")
                Text(localizationManager.localized("map_perm_always_title"))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("map_perm_always_body"))
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Text(localizationManager.localized("map_perm_precise_hint"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.textSecondary)
                // W9 Q15: Motion honest row (no fake toggle) → Settings.
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("map_motion_row_title"))
                        .font(AladdinFamilyType.subheadline(weight: .semibold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("map_motion_row_body"))
                        .font(AladdinFamilyType.caption())
                        .foregroundColor(.white.opacity(0.92))
                    Button {
                        if let url = URL(string: UIApplication.openSettingsURLString) {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        Text(localizationManager.localized("map_motion_open_settings"))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("where_phone_motion_settings")
                }
                .padding(Spacing.s)
                .frame(maxWidth: .infinity, alignment: .leading)
                .stormGlassCard(cornerRadius: CornerRadius.medium)
                Text(localizationManager.localized("map_bt_soon_title") + " — " + localizationManager.localized("map_bt_soon_body"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)

                // BG B — Background App Refresh explanation + Settings
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("bg_refresh_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("bg_refresh_body"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                    Text(localizationManager.localized("bg_refresh_hint"))
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                    Button {
                        if let url = URL(string: UIApplication.openSettingsURLString) {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        Text(localizationManager.localized("bg_refresh_open_settings"))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("where_phone_bg_refresh_settings")
                }
                .padding(Spacing.s)
                .frame(maxWidth: .infinity, alignment: .leading)
                .stormGlassCard(cornerRadius: CornerRadius.medium)

                Spacer()
                actionButton("map_perm_always_cta", id: "where_phone_always_continue") {
                    LocationManager.shared.requestAlwaysUpgradeIfEligible()
                    alwaysPromptDone = true
                    showAlwaysAllowSheet = false
                }
                Button {
                    if let url = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Text(localizationManager.localized("map_perm_open_settings"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_always_settings")
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                alwaysPromptDone = true
                showAlwaysAllowSheet = false
            })
        }
    }

    private func memberDetailSheet(_ member: HubMemberCard) -> some View {
        // HUB-P1.5 — Day Journal (L360 4–13): title + date + timeline first; actions below.
        NavigationView {
            VStack(spacing: 0) {
                // HUB-P1.8 — sticky «шапка-невидимка» CTA above journal scroll.
                Button {
                    HapticFeedback.selection()
                    print("WHERE_PHONE day journal → sticky hat")
                    selectedMember = nil
                    queueHubSheet(.invisibleHat)
                } label: {
                    HStack(spacing: Spacing.s) {
                        Image(systemName: "eye.slash.fill")
                            .foregroundColor(.secondaryGold)
                        Text(localizationManager.localized("map_create_invisible_hat"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                        Spacer(minLength: 0)
                        Image(systemName: "chevron.right")
                            .font(.caption.weight(.bold))
                            .foregroundColor(.textSecondary)
                    }
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.s)
                    .background(Color.backgroundMedium.opacity(0.45))
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_journal_sticky_hat")

                ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("family_day_journal_title"))
                        .font(AladdinFamilyType.title2())
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.top, Spacing.s)

                    Text(Self.dayJournalDateLabel())
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.textSecondary)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, 6)
                        .background(Capsule().fill(Color.backgroundMedium.opacity(0.45)))
                        .frame(maxWidth: .infinity, alignment: .center)
                        .accessibilityIdentifier("where_phone_day_journal_date")

                    memberAvatarHeader(member)

                    Text(member.name)
                        .font(AladdinFamilyType.title2())
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .center)

                    // C2: «Возле:» when we have a map place name for this member.
                    if let place = mapPointName?.trimmingCharacters(in: .whitespacesAndNewlines),
                       !place.isEmpty {
                        Text(
                            String(
                                format: localizationManager.localized("map_live_near_place"),
                                Self.streetTitleWithoutAtPrefix(place)
                            )
                        )
                        .font(.subheadline)
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .center)
                    }
                    // S19a: «С HH:MM» wall-clock (Life360) + relative ago.
                    Text(
                        String(
                            format: localizationManager.localized("map_member_since_fmt"),
                            Self.wallClockTime(member.at)
                        )
                    )
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    Text(
                        String(
                            format: localizationManager.localized("map_live_last_seen"),
                            WherePhoneTime.ago(since: member.at, localization: localizationManager)
                        )
                    )
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .frame(maxWidth: .infinity, alignment: .center)

                    memberDayJournalCard(memberId: member.id)

                    actionButton("map_member_save_place", id: "where_phone_member_save") {
                        queueHubSheet(.places(preferredNameKey: nil))
                    }
                    actionButton("map_member_directions", id: "where_phone_member_directions") {
                        queueHubSheet(.routes)
                    }

                    // Trip cards (real endpoints / honest empty) — densitiy mini-map in S19-POLISH.
                    memberRecentTripsCard

                    // Stays today (real geofences only).
                    densPlacesDayCard

                    // S19a / S19d — weekly trips card → real Driving tab (no mock).
                    memberWeeklyTripsCard

                    // S19a — driving insight locks (honest paywall; no fake event counts).
                    memberDrivingLocksCard

                    // 30d history upsell (B1).
                    densLocationHistoryCard

                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(localizationManager.localized("map_member_quiet_zone"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                        Text(localizationManager.localized("map_privacy_zone_hint"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.92))
                        Slider(value: $quietMeters, in: 50...500, step: 25) {
                            Text(localizationManager.localized("map_member_quiet_zone"))
                        }
                        .tint(Color.secondaryGold)
                        .onChange(of: quietMeters) { value in
                            FamilyMapQuietZoneStore.meters = value
                            print("WHERE_PHONE quiet meters=\(Int(value))")
                        }
                        Text(
                            String(
                                format: localizationManager.localized("map_unit_meters"),
                                Int(quietMeters)
                            )
                        )
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.92))
                        Text(localizationManager.localized("map_share_link_title"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.s)
                        Picker(localizationManager.localized("map_share_duration"), selection: $shareDuration) {
                            ForEach(FamilyMapShareDuration.allCases) { dur in
                                Text(localizationManager.localized(dur.titleKey)).tag(dur)
                            }
                        }
                        .pickerStyle(.segmented)
                        if let exp = shareExpiresAt, FamilyMapShareSessionStore.isActive {
                            let minsLeft = max(1, Int(ceil(exp.timeIntervalSinceNow / 60)))
                            Text(
                                String(
                                    format: localizationManager.localized("map_share_expires_fmt"),
                                    minsLeft
                                )
                            )
                            .font(.caption)
                            .foregroundColor(.secondaryGold)
                        } else if shareExpiresAt != nil {
                            Text(localizationManager.localized("map_share_expired"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                .padding(Spacing.l)
                }
            }
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                selectedMember = nil
            })
            .onAppear {
                print("WHERE_PHONE day journal present member=\(member.id)")
                if memberAvatarImage == nil {
                    memberAvatarImage = ProfileImageManager.shared.loadProfileImage(for: .main)
                }
            }
            .id(memberAvatarEpoch)
        }
    }

    /// HUB-P1.5 — chronological day trail (places + trips), real data only.
    private func memberDayJournalCard(memberId: String) -> some View {
        let trips = FamilyDrivingTripLedger.reports(memberId: memberId, period: "today")
        return VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("map_journal_title"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textPrimary)
            if todayTrail.isEmpty && trips.isEmpty {
                Text(localizationManager.localized("family_day_journal_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
            } else {
                if todayTrail.count > 1 {
                    Text(localizationManager.localized("map_journal_scrub_hint"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    let idx = min(max(0, Int(journalIndex.rounded())), todayTrail.count - 1)
                    Text(trailLine(todayTrail[idx]))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                        .fixedSize(horizontal: false, vertical: true)
                    Slider(
                        value: $journalIndex,
                        in: 0...Double(todayTrail.count - 1),
                        step: 1
                    )
                    .tint(Color.secondaryGold)
                    .accessibilityIdentifier("where_phone_day_journal_scrub")
                }
                ForEach(todayTrail) { event in
                    Text(trailLine(event))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
                ForEach(trips.prefix(6)) { trip in
                    Button {
                        SelectionHaptic.selection()
                        selectedMember = nil
                        hubTab = .driving
                    } label: {
                        HStack(spacing: Spacing.s) {
                            Image(systemName: "car.fill")
                                .foregroundColor(.secondaryGold)
                            Text(
                                "\(Self.streetTitleWithoutAtPrefix(trip.startLocation)) → \(Self.streetTitleWithoutAtPrefix(trip.endLocation))"
                            )
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.textPrimary)
                            .lineLimit(2)
                            Spacer(minLength: 0)
                            Text(Self.wallClockTime(trip.startTime))
                                .font(.caption2.monospacedDigit())
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.28))
        )
        .accessibilityIdentifier("where_phone_day_journal")
    }

    private static func dayJournalDateLabel() -> String {
        let f = DateFormatter()
        f.locale = .current
        f.setLocalizedDateFormatFromTemplate("EEEEdMMMM")
        return f.string(from: Date())
    }

    /// P0-5: Life360-style overlapping avatar — tap opens crop/pan.
    private func memberAvatarHeader(_ member: HubMemberCard) -> some View {
        Button {
            HapticFeedback.selection()
            showMemberImagePicker = true
        } label: {
            ZStack {
                Circle()
                    .fill(Color.backgroundMedium.opacity(0.55))
                    .frame(width: 96, height: 96)
                if let memberAvatarImage {
                    Image(uiImage: memberAvatarImage)
                        .resizable()
                        .scaledToFill()
                        .frame(width: 96, height: 96)
                        .clipShape(Circle())
                } else {
                    Text(String(member.name.prefix(1)).uppercased())
                        .font(.system(size: 36, weight: .bold, design: .rounded))
                        .foregroundColor(.secondaryGold)
                }
                Circle()
                    .stroke(Color.secondaryGold, lineWidth: 3)
                    .frame(width: 96, height: 96)
            }
            .overlay(alignment: .bottomTrailing) {
                Image(systemName: "camera.fill")
                    .font(.caption.weight(.bold))
                    .foregroundColor(.backgroundDark)
                    .padding(6)
                    .background(Circle().fill(Color.secondaryGold))
                    .offset(x: 4, y: 4)
            }
        }
        .buttonStyle(.plain)
        .frame(maxWidth: .infinity)
        .padding(.top, Spacing.s)
        .accessibilityIdentifier("where_phone_member_avatar")
        .accessibilityLabel(localizationManager.localized("avatar_crop_title"))
    }

    /// S19: trip card + mini-map from real local GPS track when present (never invent mid-points).
    /// Whole card opens Driving tab (trial/family/premium entitled) — not only the footer link.
    private var memberRecentTripsCard: some View {
        let liveTrip = Self.liveTripPreviewReport()
        return Button {
            print("WHERE_PHONE member recent-trips card tap → driving tab")
            SelectionHaptic.selection()
            selectedMember = nil
            hubTab = .driving
        } label: {
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("map_member_weekly_trips_title"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                if let liveTrip {
                    Text("\(Self.streetTitleWithoutAtPrefix(liveTrip.startLocation)) → \(Self.streetTitleWithoutAtPrefix(liveTrip.endLocation))")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                    TripEndpointMapPreview(report: liveTrip)
                        .frame(height: 120)
                        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        .allowsHitTesting(false)
                        .accessibilityIdentifier("where_phone_member_trip_minimap")
                } else {
                    Text(localizationManager.localized("map_journal_empty"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.92))
                    Text(localizationManager.localized("trip_no_map_track"))
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.92))
                }
                Text(
                    String(
                        format: localizationManager.localized("map_member_weekly_trips_subtitle"),
                        Self.weekStartLabel()
                    )
                )
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.28))
            )
            .contentShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("where_phone_member_recent_trips")
    }

    /// Build a preview report from the active (or last known) local GPS track — real samples only.
    private static func liveTripPreviewReport() -> DrivingReport? {
        guard let tripId = DrivingTripTrackStore.activeTripId else { return nil }
        let pts = DrivingTripTrackStore.load(tripId: tripId)
        guard pts.count >= 2,
              let first = pts.first,
              let last = pts.last else { return nil }
        return DrivingReport(
            id: tripId,
            userId: "local",
            userName: "",
            startTime: Date().addingTimeInterval(-Double(pts.count) * 30),
            endTime: Date(),
            startLocation: String(format: "%.4f, %.4f", first.latitude, first.longitude),
            endLocation: String(format: "%.4f, %.4f", last.latitude, last.longitude),
            distance: 0,
            duration: 0,
            averageSpeed: 0,
            maxSpeed: 0,
            safetyScore: 0,
            events: [],
            violations: [],
            startLatitude: first.latitude,
            startLongitude: first.longitude,
            endLatitude: last.latitude,
            endLongitude: last.longitude,
            routePoints: pts
        )
    }

    /// P0-3: pin tap → member card for the current map pin.
    private func openMemberFromMapPin() {
        HapticFeedback.selection()
        expandLocationSheetToFull()
        let id: String
        let name: String
        let at: Date
        if mapPinSource == .remote,
           let remote = remotePoints.first(where: { $0.coordinate != nil }) {
            id = remote.memberId.isEmpty ? "remote" : remote.memberId
            name = friendlyPointName(remote.name)
            at = remote.at
        } else {
            id = myMemberId.isEmpty ? "self" : myMemberId
            name = displayName()
            at = mapPointAt ?? Date()
        }
        print("WHERE_PHONE pin → day journal id=\(id) name=\(name)")
        selectedMember = HubMemberCard(id: id, name: name, at: at)
    }

    /// S19a Life360 parity: open real weekly driving reports (Driving tab).
    /// JOB03b CapCut · Red SUV · member sheet (не Driving hero) · UI 96×96.
    private var memberWeeklyTripsCard: some View {
        Button {
            SelectionHaptic.selection()
            selectedMember = nil
            hubTab = .driving
        } label: {
            HStack(alignment: .center, spacing: Spacing.m) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("map_member_weekly_trips_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                        .multilineTextAlignment(.leading)
                    Text(
                        String(
                            format: localizationManager.localized("map_member_weekly_trips_subtitle"),
                            Self.weekStartLabel()
                        )
                    )
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.92))
                }
                Spacer(minLength: 8)
                Image("ICON_ALIVE_HERO_H18_SUV_Red")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 96, height: 96)
                    .accessibilityHidden(true)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.92))
            }
            .padding(Spacing.m)
            .aladdinProductCard(cornerRadius: CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("where_phone_member_weekly_trips")
    }

    /// S19a — Speeding / distraction / hard accel. Locked without entitlement; never invent counts.
    private var memberDrivingLocksCard: some View {
        let entitled = FamilyMapLiveAccess.isEntitled
        return VStack(alignment: .leading, spacing: Spacing.s) {
            if !entitled {
                /// JOB04 CapCut · H16 GoldLock · member drive unlock · UI 96×96 (второй слот).
                Button {
                    SelectionHaptic.selection()
                    selectedMember = nil
                    if let leave = onLeaveToNavigate {
                        leave(.tariffs)
                    } else {
                        navigationManager.navigateTo(.tariffs)
                    }
                } label: {
                    HStack(alignment: .center, spacing: Spacing.m) {
                        Text(localizationManager.localized("map_drive_unlock_cta"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        Spacer(minLength: 8)
                        Image("ICON_ALIVE_HERO_H16_GoldLock")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 96, height: 96)
                            .accessibilityHidden(true)
                        Image(systemName: "chevron.right")
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.m)
                    .aladdinProductCard(cornerRadius: CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_member_drive_unlock")
            }

            ForEach(
                [
                    ("map_drive_lock_speeding", "speedometer"),
                    ("map_drive_lock_inattention", "iphone.radiowaves.left.and.right"),
                    ("map_drive_lock_acceleration", "bolt.fill")
                ],
                id: \.0
            ) { key, symbol in
                HStack(spacing: Spacing.m) {
                    Image(systemName: symbol)
                        .foregroundColor(.secondaryGold)
                        .frame(width: 28)
                    Text(localizationManager.localized(key))
                        .font(.subheadline)
                        .foregroundColor(.textPrimary)
                    Spacer()
                    Image(systemName: entitled ? "checkmark.circle.fill" : "lock.fill")
                        .foregroundColor(entitled ? .secondaryGold : .textSecondary)
                }
                .padding(.vertical, 6)
                .accessibilityIdentifier("where_phone_drive_lock_\(key)")
            }

            if !entitled {
                Text(localizationManager.localized("map_drive_locks_hint"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.22))
        )
    }

    private static func wallClockTime(_ date: Date) -> String {
        let f = DateFormatter()
        f.locale = .current
        f.dateFormat = "HH:mm"
        return f.string(from: date)
    }

    private static func weekStartLabel() -> String {
        let cal = Calendar.current
        let start = cal.dateInterval(of: .weekOfYear, for: Date())?.start ?? Date()
        let f = DateFormatter()
        f.locale = .current
        f.setLocalizedDateFormatFromTemplate("EEEEdMMM")
        return f.string(from: start)
    }

    private func maybeOfferAlwaysAllow() {
        guard !alwaysPromptDone else { return }
        let status = LocationManager.shared.authorizationStatus
        if status == .authorizedWhenInUse {
            showAlwaysAllowSheet = true
        }
    }

    private func maybeOfferSoftPaywall() {
        let now = Date().timeIntervalSince1970
        if firstOpenTs <= 0 {
            firstOpenTs = now
            return
        }
        // W4 Q01: soft invite D+1 when family still alone (before premium soft wall).
        maybeOfferSoftInvite(now: now)
        guard !softPaywallDone else { return }
        let days = (now - firstOpenTs) / 86_400
        // N=3 calendar days of hub use (master L-P3-01e) — W5 premium value nudge.
        if days >= 3 {
            showSoftPaywall = true
        }
    }

    /// Soft invite ~24h after first map open if roster still tiny (once).
    private func maybeOfferSoftInvite(now: Double) {
        let dismissed = UserDefaults.standard.bool(forKey: "family_invite_soft_dismissed_v1")
        guard !dismissed else { return }
        let hours = (now - firstOpenTs) / 3600
        guard hours >= 24 else { return }
        let members = FamilyLocalStore.loadPersistedMembers()
        guard members.count < 2 else { return }
        UserDefaults.standard.set(true, forKey: "family_invite_soft_dismissed_v1")
        showSoftInvite = true
    }

    private var softInviteSheet: some View {
        VStack(spacing: Spacing.m) {
            /// JOB08a CapCut · H17 FamilyKneel · soft invite · UI ~320×220.
            Image("ICON_ALIVE_HERO_H17_FamilyKneel")
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .frame(height: 200)
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                .accessibilityHidden(true)
            Text(localizationManager.localized("family_invite_soft_title"))
                .font(AladdinFamilyType.title2())
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
            Text(localizationManager.localized("family_invite_soft_body"))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            Text(localizationManager.localized("family_invite_ttl_hint"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
            actionButton("family_invite_soft_cta", id: "where_phone_soft_invite_cta") {
                showSoftInvite = false
                showInviteRole = true
            }
            Button {
                showSoftInvite = false
            } label: {
                Text(localizationManager.localized("family_invite_soft_later"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("where_phone_soft_invite_later")
        }
        .padding(Spacing.l)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .padding(Spacing.l)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black.opacity(0.55).ignoresSafeArea())
    }

    private var softPaywallSheet: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("premium_nudge_map_title"))
                .font(AladdinFamilyType.title2())
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
            Text(localizationManager.localized("premium_nudge_map_body"))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            actionButton("premium_nudge_cta", id: "where_phone_soft_paywall_try") {
                softPaywallDone = true
                showSoftPaywall = false
                leaveHubThenNavigate(to: NavigationManager.ALADDINScreen.tariffs)
            }
            Button {
                softPaywallDone = true
                showSoftPaywall = false
            } label: {
                Text(localizationManager.localized("map_soft_paywall_later"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("where_phone_soft_paywall_later")
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .padding(Spacing.l)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black.opacity(0.55).ignoresSafeArea())
    }

    private var familyCalendarSheet: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("family_cal_title"))
                        .font(AladdinFamilyType.title2())
                        .foregroundColor(.textPrimary)

                    Text(localizationManager.localized("family_cal_create_title"))
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(.textPrimary)
                    TextField(localizationManager.localized("family_cal_name_ph"), text: $draftEventTitle)
                        .textFieldStyle(.roundedBorder)
                    TextField(localizationManager.localized("family_cal_location_ph"), text: $draftEventPlace)
                        .textFieldStyle(.roundedBorder)

                    HStack(spacing: Spacing.s) {
                        calendarDayChip("family_cal_today") {
                            draftEventStart = Self.combine(day: Date(), time: draftEventStart)
                            draftEventEnd = draftEventStart.addingTimeInterval(3600)
                        }
                        calendarDayChip("family_cal_tomorrow") {
                            let tomorrow = Calendar.current.date(byAdding: .day, value: 1, to: Date()) ?? Date()
                            draftEventStart = Self.combine(day: tomorrow, time: draftEventStart)
                            draftEventEnd = draftEventStart.addingTimeInterval(3600)
                        }
                    }

                    // Q24: graphical DatePicker draws black digits — force light inset for contrast on storm bg.
                    DatePicker(
                        localizationManager.localized("family_cal_pick_date"),
                        selection: $draftEventStart,
                        displayedComponents: [.date]
                    )
                    .datePickerStyle(.graphical)
                    .tint(Color.secondaryGold)
                    .colorScheme(.light)
                    .padding(Spacing.s)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.white.opacity(0.92))
                    )
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    .accessibilityIdentifier("where_phone_family_calendar_picker")
                    .onChange(of: draftEventStart) { newStart in
                        if draftEventEnd <= newStart {
                            draftEventEnd = newStart.addingTimeInterval(3600)
                        }
                    }

                    DatePicker(
                        localizationManager.localized("family_cal_start"),
                        selection: $draftEventStart,
                        displayedComponents: [.hourAndMinute]
                    )
                    .tint(Color.secondaryGold)
                    DatePicker(
                        localizationManager.localized("family_cal_end"),
                        selection: $draftEventEnd,
                        displayedComponents: [.hourAndMinute]
                    )
                    .tint(Color.secondaryGold)

                    Text(localizationManager.localized("family_cal_who_title"))
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("family_cal_who_hint"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)

                    Button {
                        draftAudienceIds = Set(calendarRoster.map(\.canonicalId))
                    } label: {
                        Text(localizationManager.localized("family_cal_who_all"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("where_phone_cal_who_all")

                    if calendarRoster.isEmpty {
                        Text(localizationManager.localized("family_cal_who_you"))
                            .font(.subheadline)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.s)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .stormGlassCard(cornerRadius: CornerRadius.medium)
                    } else {
                        ForEach(calendarRoster, id: \.canonicalId) { member in
                            Toggle(isOn: Binding(
                                get: { draftAudienceIds.contains(member.canonicalId) },
                                set: { on in
                                    if on { draftAudienceIds.insert(member.canonicalId) }
                                    else { draftAudienceIds.remove(member.canonicalId) }
                                }
                            )) {
                                Text(member.isCurrentUser
                                     ? localizationManager.localized("family_cal_who_you")
                                     : member.name)
                                    .font(.subheadline)
                                    .foregroundColor(.textPrimary)
                            }
                            .tint(Color.secondaryGold)
                            .accessibilityIdentifier("where_phone_cal_who_\(member.canonicalId)")
                        }
                    }

                    Toggle(isOn: $draftAddToIOS) {
                        Text(localizationManager.localized("family_cal_to_ios"))
                            .font(.subheadline)
                            .foregroundColor(.textPrimary)
                    }
                    .tint(Color.secondaryGold)
                    Text(localizationManager.localized("family_cal_local_only"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)

                    if localEvents.isEmpty {
                        Text(localizationManager.localized("family_cal_empty"))
                            .font(.subheadline)
                            .foregroundColor(.textSecondary)
                    } else {
                        ForEach(localEvents) { event in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(event.title)
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundColor(.textPrimary)
                                Text(event.place)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            .padding(Spacing.s)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .stormGlassCard(cornerRadius: CornerRadius.medium)
                        }
                    }

                    actionButton("family_cal_add", id: "where_phone_cal_save") {
                        saveDraftFamilyEvent()
                    }
                }
                .padding(Spacing.l)
            }
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                showFamilyCalendar = false
            })
            .onAppear {
                calendarRoster = FamilyLocalStore.loadPersistedMembers()
                if draftAudienceIds.isEmpty {
                    draftAudienceIds = Set(calendarRoster.map(\.canonicalId))
                }
                if draftEventEnd <= draftEventStart {
                    draftEventEnd = draftEventStart.addingTimeInterval(3600)
                }
            }
        }
    }

    private func calendarDayChip(_ key: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(localizationManager.localized(key))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    Capsule().stroke(Color.secondaryGold.opacity(0.7), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }

    private static func combine(day: Date, time: Date) -> Date {
        let cal = Calendar.current
        let dayParts = cal.dateComponents([.year, .month, .day], from: day)
        let timeParts = cal.dateComponents([.hour, .minute], from: time)
        var merged = DateComponents()
        merged.year = dayParts.year
        merged.month = dayParts.month
        merged.day = dayParts.day
        merged.hour = timeParts.hour
        merged.minute = timeParts.minute
        return cal.date(from: merged) ?? day
    }

    private func saveDraftFamilyEvent() {
        let title = draftEventTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !title.isEmpty else { return }
        let place = draftEventPlace.trimmingCharacters(in: .whitespacesAndNewlines)
        let end = max(draftEventEnd, draftEventStart.addingTimeInterval(900))
        let audience = Array(draftAudienceIds)
        let event = FamilyMapLocalEvent(
            id: UUID(),
            title: title,
            place: place.isEmpty ? localizationManager.localized("family_cal_place") : place,
            start: draftEventStart,
            end: end,
            audienceIds: audience
        )
        FamilyMapLocalEventStore.append(event)
        localEvents = FamilyMapLocalEventStore.load()
        scheduleFamilyEventReminder(event)
        draftEventTitle = ""
        draftEventPlace = ""
        draftAudienceIds = Set(calendarRoster.map(\.canonicalId))
        if draftAddToIOS {
            Task { await addEventToIOSCalendar(event) }
        }
        showFamilyCalendar = false
    }

    private func scheduleFamilyEventReminder(_ event: FamilyMapLocalEvent) {
        let fire = event.start.addingTimeInterval(-15 * 60)
        guard fire > Date() else { return }
        let content = UNMutableNotificationContent()
        content.title = localizationManager.localized("family_cal_reminder_title")
        content.body = String(
            format: localizationManager.localized("family_cal_reminder_body"),
            event.title,
            event.place
        )
        content.sound = .default
        content.userInfo = [
            "type": "family_event",
            "event_id": event.id.uuidString,
            "deepLink": FamilyPushDeepLink.mapURL(memberId: nil, focus: .map)
        ]
        let comps = Calendar.current.dateComponents(
            [.year, .month, .day, .hour, .minute],
            from: fire
        )
        let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
        let request = UNNotificationRequest(
            identifier: "family_event_\(event.id.uuidString)",
            content: content,
            trigger: trigger
        )
        UNUserNotificationCenter.current().add(request, withCompletionHandler: nil)
    }

    private func addEventToIOSCalendar(_ event: FamilyMapLocalEvent) async {
        let granted = await FamilyHabitEventKitSync.shared.requestAccess()
        guard granted else { return }
        let store = EKEventStore()
        let ek = EKEvent(eventStore: store)
        ek.title = event.title
        ek.location = event.place
        ek.startDate = event.start
        ek.endDate = event.end
        ek.calendar = store.defaultCalendarForNewEvents
        do {
            try store.save(ek, span: .thisEvent)
        } catch {
            print("📅 family map EventKit save error: \(error.localizedDescription)")
        }
    }

    /// Visual-only map hub icons (L15). Same taps / no QR / pin+chips unchanged.
    private func hubAliveIcon(for tab: HubTab) -> AliveIconID {
        switch tab {
        case .location: return .whereFamily
        case .driving: return .mapDriving
        case .safety: return .protect
        case .subscription: return .premium
        }
    }

    private var hubTabBar: some View {
        HStack(spacing: 0) {
            ForEach(HubTab.allCases) { tab in
                Button {
                    HapticFeedback.selection()
                    hubTab = tab
                } label: {
                    VStack(spacing: 4) {
                        // L15 hub tabs · size 22 (план) · 3 стиля; чипы/пин не трогаем.
                        AliveGlyph(id: hubAliveIcon(for: tab), size: 22) {
                            Image(systemName: tab.systemImage)
                                .font(.system(size: 18, weight: .semibold))
                        }
                        Text(localizationManager.localized(tab.titleKey))
                            .font(AladdinFamilyType.caption(weight: .semibold))
                            .lineLimit(1)
                            .minimumScaleFactor(0.75)
                    }
                    // Calm Navy tab: gold active, near-white inactive (readable on dark bar).
                    .foregroundColor(hubTab == tab ? Color.secondaryGold : Color.white.opacity(0.92))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Spacing.s)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_hub_tab_\(tab.rawValue)")
            }
        }
        .padding(.horizontal, Spacing.xs)
        .padding(.bottom, Spacing.xs)
        .background(
            AladdinSnowballPalette.canvasTop
                .overlay(
                    Rectangle()
                        .fill(Color.secondaryGold.opacity(0.45))
                        .frame(height: 1),
                    alignment: .top
                )
        )
        .accessibilityIdentifier("where_phone_hub_tab_bar")
    }

    /// Last-point copy + Open in Maps — lives in the sheet (map itself is full-bleed live).
    private var mapMetaSheetBlock: some View {
        card(symbol: "map.fill", titleKey: "where_phone_map_card_title") {
            if let coordinate = mapCoordinate, let at = mapPointAt {
                Text(
                    String(
                        format: localizationManager.localized("where_phone_map_point_time"),
                        friendlyPointName(mapPointName),
                        WherePhoneTime.ago(since: at, localization: localizationManager)
                    )
                )
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)

                Text(localizationManager.localized("map_anti_spy_note"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                Button {
                    showOpenInMapsSheet = true
                } label: {
                    Text(localizationManager.localized("where_phone_open_in_maps"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.s)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_open_in_maps")
                .confirmationDialog(
                    localizationManager.localized("where_phone_open_in_maps_title"),
                    isPresented: $showOpenInMapsSheet,
                    titleVisibility: .visible
                ) {
                    if preferredMaps == "apple" {
                        Button(localizationManager.localized("where_phone_open_apple_maps")) {
                            FamilyMapsPreference.markUserChose("apple")
                            preferredMaps = "apple"
                            openInAppleMaps(coordinate)
                        }
                        Button(localizationManager.localized("where_phone_open_yandex_maps")) {
                            FamilyMapsPreference.markUserChose("yandex")
                            preferredMaps = "yandex"
                            openInYandexMaps(coordinate)
                        }
                    } else {
                        Button(localizationManager.localized("where_phone_open_yandex_maps")) {
                            FamilyMapsPreference.markUserChose("yandex")
                            preferredMaps = "yandex"
                            openInYandexMaps(coordinate)
                        }
                        Button(localizationManager.localized("where_phone_open_apple_maps")) {
                            FamilyMapsPreference.markUserChose("apple")
                            preferredMaps = "apple"
                            openInAppleMaps(coordinate)
                        }
                    }
                    Button(localizationManager.localized("common_cancel"), role: .cancel) {}
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
        .accessibilityIdentifier("where_phone_map")
    }

    private var trailCard: some View {
        card(symbol: "list.bullet.rectangle", titleKey: "map_journal_title") {
            if todayTrail.isEmpty {
                Text(localizationManager.localized("map_journal_empty"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            } else {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("map_journal_scrub_hint"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    let idx = min(max(0, Int(journalIndex.rounded())), todayTrail.count - 1)
                    Text(trailLine(todayTrail[idx]))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                        .fixedSize(horizontal: false, vertical: true)
                    if todayTrail.count > 1 {
                        Slider(
                            value: $journalIndex,
                            in: 0...Double(todayTrail.count - 1),
                            step: 1
                        )
                        .tint(Color.secondaryGold)
                        .accessibilityIdentifier("where_phone_journal_scrub")
                        .onChange(of: journalIndex) { _ in
                            SelectionHaptic.selection()
                        }
                    }
                    ForEach(todayTrail) { event in
                        Text(trailLine(event))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
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
                    queueHubSheet(.places(preferredNameKey: nil))
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
        card(symbol: "mappin.circle.fill", titleKey: "map_share_activity_title") {
            Text(localizationManager.localized("map_share_activity_hint"))
                .font(.caption)
                .foregroundColor(.textSecondary)

            Picker(localizationManager.localized("map_share_duration"), selection: $shareDuration) {
                ForEach(FamilyMapShareDuration.allCases) { dur in
                    Text(localizationManager.localized(dur.titleKey)).tag(dur)
                }
            }
            .pickerStyle(.segmented)
            .accessibilityIdentifier("where_phone_share_duration")

            if let exp = shareExpiresAt, FamilyMapShareSessionStore.isActive {
                let minsLeft = max(1, Int(ceil(exp.timeIntervalSinceNow / 60)))
                Text(
                    String(
                        format: localizationManager.localized("map_share_active_fmt"),
                        minsLeft
                    )
                )
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
            } else if shareExpiresAt != nil {
                Text(localizationManager.localized("map_share_expired"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }

            if !pointLines.isEmpty {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    ForEach(pointLines) { line in
                        Button {
                            selectedMember = HubMemberCard(
                                id: line.memberId,
                                name: line.name,
                                at: line.at
                            )
                        } label: {
                            Text(personLine(name: line.name, at: line.at))
                                .font(.subheadline.weight(.semibold))
                                .foregroundColor(.textPrimary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .buttonStyle(.plain)
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

            if FamilyMapShareSessionStore.isActive {
                Button {
                    HapticFeedback.selection()
                    FamilyMapShareSessionStore.endSession()
                    shareExpiresAt = nil
                    statusText = localizationManager.localized("map_share_stop")
                } label: {
                    Text(localizationManager.localized("map_share_stop"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.dangerRed)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.s)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("where_phone_share_stop")
            }
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
        Button {
            runWherePhoneTap(id: id, action: action)
        } label: {
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

    /// Instant haptic + DIAG; debounce 300ms per id; never await network here.
    private func runWherePhoneTap(id: String, action: @escaping () -> Void) {
        HapticFeedback.selection()
        print("WHERE_PHONE tap id=\(id) t=\(Date())")
        let now = Date()
        if id == lastWherePhoneTapId, now.timeIntervalSince(lastWherePhoneTapAt) < 0.3 {
            return
        }
        lastWherePhoneTapId = id
        lastWherePhoneTapAt = now
        action()
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
        applyBestMapPin()
        APIService.shared.getFamilyWherePhone { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let snapshot):
                    self.remoteSignals = snapshot.signals
                    self.remotePoints = snapshot.points
                    print("WHERE_PHONE family signals=\(snapshot.signals.count) points=\(snapshot.points.count)")
                    self.applyBestMapPin()
                case .failure:
                    print("WHERE_PHONE family sync fail")
                }
            }
        }
    }

    /// Hybrid pin: live (Always + Family+) → local last-point / share → remote family map_url.
    private func applyBestMapPin() {
        if FamilyMapLiveAccess.isEntitled,
           liveLocation.authStatus == .authorizedAlways,
           let coord = liveLocation.coordinate {
            applyMapPin(
                coord,
                name: mapPointName ?? localizationManager.localized("where_phone_map_card_title"),
                at: liveLocation.updatedAt ?? Date(),
                source: .live
            )
            return
        }
        if let last = WherePhoneLastPointStore.load() {
            applyMapPin(last.coordinate, name: friendlyPointName(last.name), at: last.at, source: .local)
            return
        }
        if let share = shares.first, let lat = share.latitude, let lon = share.longitude {
            let coord = CLLocationCoordinate2D(latitude: lat, longitude: lon)
            applyMapPin(coord, name: friendlyPointName(share.name), at: share.createdAt, source: .local)
            return
        }
        let mine = myMemberId.isEmpty ? "self" : myMemberId
        let remoteCandidates = remotePoints.filter { $0.coordinate != nil }
        let preferredRemote = remoteCandidates.first(where: { $0.memberId != mine })
            ?? remoteCandidates.first
        if let remote = preferredRemote, let coord = remote.coordinate {
            applyMapPin(coord, name: friendlyPointName(remote.name), at: remote.at, source: .remote)
            return
        }
        mapCoordinate = nil
        mapPointName = nil
        mapPointAt = nil
        mapPinSource = .none
    }

    private func applyMapPin(
        _ coordinate: CLLocationCoordinate2D,
        name: String,
        at: Date,
        source: MapPinSource
    ) {
        mapCoordinate = coordinate
        mapPointName = name
        mapPointAt = at
        mapPinSource = source
        mapRegion = MKCoordinateRegion(
            center: coordinate,
            span: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02)
        )
    }

    /// R10: open member sheet from push (SOS / ImOK / battery).
    private func applyPendingFamilyPushFocusIfNeeded() {
        guard let pending = FamilyPushDeepLink.consumePendingMember() else { return }
        sheetExpansion = 0.55
        hubTab = .location
        activeChip = .people
        let focus = pending.focus
        if focus == .sos || focus == .battery || focus == .imOk {
            let id = pending.id.isEmpty ? "push_focus" : pending.id
            let name = pending.name.isEmpty
                ? localizationManager.localized("battery_critical_member_fallback")
                : pending.name
            selectedMember = HubMemberCard(id: id, name: name, at: Date())
        }
        FamilyPushDeepLink.clearFocus()
    }

    private func signalText(_ line: WherePhoneFamilySignal) -> String {
        let actionKey = line.isArrival ? "where_phone_signal_arrived" : "where_phone_signal_left"
        let action = String(
            format: localizationManager.localized(actionKey),
            line.placeName
        )
        return String(
            format: localizationManager.localized("where_phone_event_line"),
            friendlyPointName(line.name),
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
        friendlyPointName(
            UserDefaults.standard.string(forKey: "user_name")
                ?? UserDefaults.standard.string(forKey: "user_display_name")
        )
    }

    /// QA16 F2: never show raw `User` / MEM_* on the map caption.
    /// P4: L = 56 (было 48) — пин с буквой/фото чуть крупнее на Life360-карте.
    private func pinDiameterForSize(_ raw: String) -> CGFloat {
        switch raw {
        case "S": return 28
        case "L": return 56
        default: return 36
        }
    }

    private func friendlyPointName(_ raw: String?) -> String {
        let trimmed = (raw ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let lowered = trimmed.lowercased()
        let junk: Set<String> = ["user", "unknown", "null", "n/a", "none", "-"]
        if trimmed.isEmpty || trimmed.hasPrefix("MEM_") || junk.contains(lowered) {
            return localizationManager.localized("where_phone_you")
        }
        return Self.streetTitleWithoutAtPrefix(trimmed)
    }

    /// C1: drop Life360-style «В » / «At » before street names.
    private static func streetTitleWithoutAtPrefix(_ raw: String) -> String {
        var s = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let prefixes = ["В ", "в ", "At ", "at ", "On ", "on "]
        for p in prefixes where s.hasPrefix(p) {
            s = String(s.dropFirst(p.count)).trimmingCharacters(in: .whitespacesAndNewlines)
            break
        }
        return s
    }

    private func openInAppleMaps(_ coordinate: CLLocationCoordinate2D) {
        let item = MKMapItem(placemark: MKPlacemark(coordinate: coordinate))
        item.name = friendlyPointName(mapPointName)
        item.openInMaps(launchOptions: [
            MKLaunchOptionsMapCenterKey: NSValue(mkCoordinate: coordinate),
            MKLaunchOptionsMapSpanKey: NSValue(mkCoordinateSpan: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02))
        ])
    }

    private func openInYandexMaps(_ coordinate: CLLocationCoordinate2D) {
        let lat = coordinate.latitude
        let lon = coordinate.longitude
        // App scheme first; fall back to mobile web (no Yandex SDK).
        let appURL = URL(string: String(format: "yandexmaps://maps.yandex.ru/?pt=%.6f,%.6f&z=16&l=map", lon, lat))
        let webURL = URL(string: String(format: "https://yandex.ru/maps/?pt=%.6f,%.6f&z=16&l=map", lon, lat))
        if let appURL, UIApplication.shared.canOpenURL(appURL) {
            UIApplication.shared.open(appURL)
        } else if let webURL {
            UIApplication.shared.open(webURL)
        }
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
        HapticFeedback.selection()
        print("WHERE_PHONE tap id=where_phone_send t=\(Date())")
        isSending = true
        statusText = localizationManager.localized("where_phone_share_sending")
        if let cached = LocationManager.shared.currentLocation,
           abs(cached.timestamp.timeIntervalSinceNow) < 15 * 60 {
            print("WHERE_PHONE send using cached location")
            deliver(cached)
            return
        }
        print("WHERE_PHONE send asking for one location")
        locator.request { result in
            DispatchQueue.main.async {
                switch result {
                case .failure(let error):
                    self.isSending = false
                    let ns = error as NSError
                    print("WHERE_PHONE send fail domain=\(ns.domain) code=\(ns.code)")
                    let message = self.shareFailureText(error)
                    self.statusText = message
                    self.sendFailAlertMessage = message
                case .success(let location):
                    print("WHERE_PHONE send ok")
                    self.deliver(location)
                }
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
        if FamilyMapQuietZoneStore.contains(location) {
            inQuietZone = true
            statusText = localizationManager.localized("map_quiet_share_blocked")
            return
        }
        inQuietZone = false
        let name = displayName()
        let lat = location.coordinate.latitude
        let lon = location.coordinate.longitude
        FamilyMapShareSessionStore.beginSession(hours: shareDuration.rawValue)
        shareExpiresAt = FamilyMapShareSessionStore.expiresAt
        WherePhoneShareStore.add(name: name, isMine: true, latitude: lat, longitude: lon)
        WherePhoneLastPointStore.save(name: name, latitude: lat, longitude: lon)
        shares = WherePhoneShareStore.load()
        applyMapPin(location.coordinate, name: name, at: Date(), source: .local)
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
    let latitude: Double?
    let longitude: Double?
    let mapURL: String?

    var id: String { memberId }

    var coordinate: CLLocationCoordinate2D? {
        if let latitude, let longitude {
            return CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        }
        return WherePhoneMapURL.coordinate(from: mapURL)
    }

    init(
        memberId: String,
        name: String,
        at: Date,
        latitude: Double? = nil,
        longitude: Double? = nil,
        mapURL: String? = nil
    ) {
        self.memberId = memberId
        self.name = name
        self.at = at
        self.latitude = latitude
        self.longitude = longitude
        self.mapURL = mapURL
    }
}

/// Parse family share links → pin (Apple `ll=` / Yandex `pt=`).
enum WherePhoneMapURL {
    static func coordinate(from raw: String?) -> CLLocationCoordinate2D? {
        guard let raw, !raw.isEmpty, let url = URL(string: raw) else { return nil }
        if let items = URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems {
            if let ll = items.first(where: { $0.name == "ll" })?.value {
                let parts = ll.split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
                if parts.count >= 2 {
                    return CLLocationCoordinate2D(latitude: parts[0], longitude: parts[1])
                }
            }
            if let pt = items.first(where: { $0.name == "pt" })?.value {
                // Yandex pt=lon,lat
                let parts = pt.split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
                if parts.count >= 2 {
                    return CLLocationCoordinate2D(latitude: parts[1], longitude: parts[0])
                }
            }
        }
        return nil
    }
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
    let mapURL: String?

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case displayName = "display_name"
        case happenedAt = "happened_at"
        case mapURL = "map_url"
    }

    func point() -> WherePhoneFamilyPoint? {
        guard let at = WherePhoneISO.date(from: happenedAt) else { return nil }
        let parsed = WherePhoneMapURL.coordinate(from: mapURL)
        return WherePhoneFamilyPoint(
            memberId: memberId,
            name: displayName,
            at: at,
            latitude: parsed?.latitude,
            longitude: parsed?.longitude,
            mapURL: mapURL
        )
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
            let row = WherePhoneFamilyPoint(
                memberId: mine,
                name: localMine.name,
                at: localMine.createdAt,
                latitude: localMine.latitude,
                longitude: localMine.longitude
            )
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

// MARK: - Scroll-spy preferences (L-P3-01d)

private struct WherePhoneSectionFramesKey: PreferenceKey {
    static var defaultValue: [Int: CGFloat] { [:] }

    static func reduce(value: inout [Int: CGFloat], nextValue: () -> [Int: CGFloat]) {
        value.merge(nextValue(), uniquingKeysWith: { $1 })
    }
}

// MARK: - Local family calendar (Calendar D v1 — this iPhone only)

struct FamilyMapLocalEvent: Identifiable, Codable, Equatable {
    let id: UUID
    var title: String
    var place: String
    var start: Date
    var end: Date
    /// S32 — who can see (local roster ids). Empty = this device only.
    var audienceIds: [String]

    enum CodingKeys: String, CodingKey {
        case id, title, place, start, end, audienceIds
    }

    init(
        id: UUID,
        title: String,
        place: String,
        start: Date,
        end: Date,
        audienceIds: [String] = []
    ) {
        self.id = id
        self.title = title
        self.place = place
        self.start = start
        self.end = end
        self.audienceIds = audienceIds
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(UUID.self, forKey: .id)
        title = try c.decode(String.self, forKey: .title)
        place = try c.decode(String.self, forKey: .place)
        start = try c.decode(Date.self, forKey: .start)
        end = try c.decode(Date.self, forKey: .end)
        audienceIds = try c.decodeIfPresent([String].self, forKey: .audienceIds) ?? []
    }
}

/// S2: dark sheet chrome + map interaction under sheet (iOS 16.4+).
private struct LocationSheetChromeModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            content
                .presentationBackground(Color.backgroundDark.opacity(0.98))
                .presentationBackgroundInteraction(.enabled(upThrough: .fraction(0.95)))
        } else {
            content
        }
    }
}

enum FamilyMapLocalEventStore {
    private static let key = "where_phone_family_cal_events_v1"

    static func load() -> [FamilyMapLocalEvent] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let rows = try? JSONDecoder().decode([FamilyMapLocalEvent].self, from: data) else {
            return []
        }
        return rows.sorted { $0.start < $1.start }
    }

    static func append(_ event: FamilyMapLocalEvent) {
        var rows = load()
        rows.append(event)
        if let data = try? JSONEncoder().encode(rows) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }
}

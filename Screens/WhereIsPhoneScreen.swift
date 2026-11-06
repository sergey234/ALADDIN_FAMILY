import SwiftUI
import CoreLocation
import MapKit
import UIKit
import EventKit

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

    @State private var hubTab: HubTab = .location
    @State private var activeChip: SheetChip = .people
    @State private var isChipProgrammaticScroll = false
    @State private var chipScrollRequest = 0
    /// W2 Q34–Q36: 0 = map large · 1 = sheet dominates (Life360-style drag).
    @State private var sheetExpansion: CGFloat = 0.35
    @State private var sheetDragStart: CGFloat = 0.35
    @State private var sheetDragActive = false
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
    @State private var showPetSoon = false
    @State private var showPetWizard = false
    @State private var showItemsSoon = false
    @State private var showFamilyCalendar = false
    @State private var showCrashSettings = false
    @State private var showMapTypeSheet = false
    @State private var showAlwaysAllowSheet = false
    @State private var showSoftPaywall = false
    @State private var showSoftInvite = false
    @State private var showPinPreview = false
    @State private var showInviteRole = false
    @State private var showRoutes = false
    @State private var showCrashConfirm = false
    @State private var shareDuration: FamilyMapShareDuration =
        FamilyMapShareDuration(rawValue: FamilyMapShareSessionStore.selectedHours) ?? .oneHour
    @State private var journalIndex: Double = 0
    @State private var quietMeters: Double = FamilyMapQuietZoneStore.meters
    @State private var selectedMember: HubMemberCard?
    @State private var savedPets: [FamilyPetProfile] = FamilyPetProfileStore.load()
    @StateObject private var liveLocation = FamilyMapLiveLocationController.shared
    @AppStorage("where_phone_pin_preview_done") private var pinPreviewDone = false
    @AppStorage("where_phone_pin_size") private var pinSizeRaw: String = "M"
    @State private var localEvents: [FamilyMapLocalEvent] = FamilyMapLocalEventStore.load()
    @State private var draftEventTitle = ""
    @State private var draftEventPlace = ""
    @State private var draftEventStart = Date()
    @State private var draftAddToIOS = true
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
        WherePhoneFamilyBoard.points(
            local: shares,
            localMemberId: myMemberId,
            remote: remotePoints,
            hideOthers: hideOthers
        )
    }

    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()

            VStack(spacing: 0) {
                hubHeader

                Group {
                    switch hubTab {
                    case .location:
                        locationPane
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
        .sheet(isPresented: $showPlaces) {
            GeofencesSettingsModal(isPresented: $showPlaces)
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
        .sheet(isPresented: $showPinPreview) {
            FamilyMapPinPreviewSheet(isPresented: $showPinPreview)
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
        .sheet(isPresented: $showAlwaysAllowSheet) {
            alwaysAllowSheet
        }
        .sheet(item: $selectedMember) { member in
            memberDetailSheet(member)
        }
        .onAppear {
            preferredMaps = FamilyMapsPreference.resolved(language: localizationManager.currentLanguage)
            reload()
            liveLocation.startIfNeeded()
            savedPets = FamilyPetProfileStore.load()
            maybeOfferAlwaysAllow()
            maybeOfferSoftPaywall()
            if !pinPreviewDone {
                showPinPreview = true
            }
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
        .accessibilityIdentifier("where_phone_screen")
    }

    /// X закрывает хаб → Удобный (`isPresented = false`), не «стек Назад».
    private var hubHeader: some View {
        HStack {
            // Title follows active tab (not always «Карта» on Subscription/Safety).
            Text(localizationManager.localized(hubTab.titleKey))
                .font(.system(.title2, design: .serif).weight(.bold))
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
        .background(Color.backgroundMedium.opacity(0.5))
    }

    /// Map height shrinks as sheet expands (Life360 drag parity).
    private var locationMapMaxHeight: CGFloat {
        let collapsed: CGFloat = 320
        let expanded: CGFloat = 112
        return collapsed - (collapsed - expanded) * sheetExpansion
    }

    private var locationPane: some View {
        VStack(spacing: 0) {
            ZStack(alignment: .trailing) {
                ScrollView(.vertical, showsIndicators: false) {
                    mapCard
                        .padding(.horizontal, Spacing.m)
                        .padding(.top, Spacing.s)
                }
                .frame(maxHeight: locationMapMaxHeight)
                .animation(.easeInOut(duration: 0.2), value: sheetExpansion)
                .accessibilityIdentifier("where_phone_map_pane")

                mapFabStack
                    .padding(.trailing, Spacing.m)
                    .padding(.bottom, Spacing.s)
            }

            // Drag handle: pull up → more list / less map; pull down → map fullscreen-ish.
            Capsule()
                .fill(Color.secondaryGold.opacity(0.55))
                .frame(width: 40, height: 5)
                .padding(.top, 6)
                .padding(.bottom, 4)
                .frame(maxWidth: .infinity)
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 8)
                        .onChanged { value in
                            if !sheetDragActive {
                                sheetDragActive = true
                                sheetDragStart = sheetExpansion
                            }
                            let delta = -value.translation.height / 280
                            sheetExpansion = min(1, max(0, sheetDragStart + delta))
                        }
                        .onEnded { value in
                            sheetDragActive = false
                            let delta = -value.translation.height / 280
                            let raw = min(1, max(0, sheetDragStart + delta))
                            // Snap to 3 detents (Q34/Q35/Q36).
                            let snapped: CGFloat
                            if raw < 0.22 { snapped = 0.08 }
                            else if raw < 0.55 { snapped = 0.35 }
                            else { snapped = 0.85 }
                            withAnimation(.spring(response: 0.32, dampingFraction: 0.86)) {
                                sheetExpansion = snapped
                            }
                            sheetDragStart = snapped
                        }
                )
                .accessibilityIdentifier("where_phone_sheet_drag_handle")
                .accessibilityLabel(localizationManager.localized("map_sheet_drag_a11y"))

            sheetChipStrip
                .padding(.vertical, Spacing.s)
                .background(Color.backgroundMedium.opacity(0.55))

            ScrollViewReader { proxy in
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: Spacing.m) {
                        peopleSheetSection.id(SheetChip.people)
                        petsSheetSection.id(SheetChip.pets)
                        itemsSheetSection.id(SheetChip.items)
                        placesSheetSection.id(SheetChip.places)
                        eventsSheetSection.id(SheetChip.events)
                        lostCard
                    }
                    .padding(Spacing.m)
                    .padding(.bottom, Spacing.xl)
                }
                .coordinateSpace(name: "wherePhoneSheetScroll")
                .onPreferenceChange(WherePhoneSectionFramesKey.self) { frames in
                    updateActiveChipFromScroll(frames)
                }
                .onChange(of: chipScrollRequest) { _ in
                    guard chipScrollRequest > 0 else { return }
                    withAnimation(.easeInOut(duration: 0.28)) {
                        proxy.scrollTo(activeChip, anchor: .top)
                    }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                        isChipProgrammaticScroll = false
                    }
                }
            }
        }
        .accessibilityIdentifier("where_phone_tab_location")
    }

    private var sheetChipStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: Spacing.s) {
                ForEach(SheetChip.allCases) { chip in
                    Button {
                        HapticFeedback.selection()
                        isChipProgrammaticScroll = true
                        activeChip = chip
                        chipScrollRequest += 1
                    } label: {
                        VStack(spacing: 4) {
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
                inviteBanner
                shareCard
                trailCard
            }
        }
    }

    private var petsSheetSection: some View {
        sectionFrame(.pets) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                if !savedPets.isEmpty {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        ForEach(savedPets) { pet in
                            HStack {
                                Image(systemName: "pawprint.fill")
                                    .foregroundColor(.secondaryGold)
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
                            .stormGlassCard(cornerRadius: CornerRadius.medium)
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
                    showPetWizard = true
                }
            }
        }
    }

    private var itemsSheetSection: some View {
        sectionFrame(.items) {
            soonSectionCard(
                titleKey: "items_promo_title",
                bodyKey: "items_promo_body",
                ctaKey: "items_promo_cta",
                symbol: "key.fill"
            ) {
                showItemsSoon = true
            }
        }
    }

    private var placesSheetSection: some View {
        sectionFrame(.places) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                placesCard
                HStack(spacing: Spacing.s) {
                    placeSuggestChip("map_places_suggest_home")
                    placeSuggestChip("map_places_suggest_school")
                    placeSuggestChip("map_places_suggest_work")
                }
                actionButton("map_places_manage", id: "where_phone_manage_places") {
                    showPlaces = true
                }
            }
        }
    }

    private func placeSuggestChip(_ key: String) -> some View {
        Button {
            showPlaces = true
        } label: {
            Text(localizationManager.localized(key))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
                .overlay(Capsule().stroke(Color.secondaryGold.opacity(0.45), lineWidth: 1))
        }
        .buttonStyle(.plain)
    }

    private var eventsSheetSection: some View {
        sectionFrame(.events) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "calendar")
                        .foregroundColor(.secondaryGold)
                    Text(localizationManager.localized("family_cal_title"))
                        .font(.system(.title3, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)
                }
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
                    showFamilyCalendar = true
                }
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, alignment: .leading)
            .stormGlassCard(cornerRadius: CornerRadius.large)
        }
    }

    private var inviteBanner: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("map_invite_banner_title"))
                .font(.system(.title3, design: .serif).weight(.bold))
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized("map_create_circle_teaser"))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
            actionButton("map_invite_banner_cta", id: "where_phone_invite_banner") {
                HapticFeedback.impact(.light)
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
                    .font(.system(.title3, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
            }
            Text(localizationManager.localized(bodyKey))
                .font(.subheadline)
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
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized(bodyKey))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Spacer()
                Button {
                    isPresented.wrappedValue = false
                } label: {
                    Text(localizationManager.localized("map_soon_ok"))
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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
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
        .environmentObject(analyticsViewModel)
        .accessibilityIdentifier("where_phone_tab_driving")
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
                        .font(.system(.title3, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)
                }

                Text(localizationManager.localized("map_hub_safety_body"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                Toggle(isOn: $crashConsentAccepted) {
                    Text(localizationManager.localized("crash_consent_accept"))
                        .font(.subheadline.weight(.semibold))
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
                .font(.subheadline)
                .foregroundColor(.textSecondary)

                Text(localizationManager.localized("crash_limits_body"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                Text(localizationManager.localized("map_hub_safety_sos_note"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                FamilySOSHoldButton()
                    .environmentObject(localizationManager)

                actionButton("crash_confirm_preview_cta", id: "where_phone_crash_confirm") {
                    showCrashConfirm = true
                }

                Text(localizationManager.localized("map_soon_tile_title") + " · " + localizationManager.localized("map_soon_tile_body"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Text(localizationManager.localized("map_soon_evac_title") + " · " + localizationManager.localized("map_soon_evac_body"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
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
                    Image(systemName: "crown.fill")
                        .font(.title2.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                    Text(localizationManager.localized("map_hub_subscription_title"))
                        .font(.system(.title3, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)
                }
                Text(localizationManager.localized("map_hub_subscription_body"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
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
                showMapTypeSheet = true
            } label: {
                Image("FIG_L03_FABLayers")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 44, height: 44)
                    .clipShape(Circle())
                    .overlay(Circle().stroke(Color.secondaryGold.opacity(0.35), lineWidth: 1))
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("where_phone_fab_map_type")

            fabButton(systemImage: "location.fill", id: "where_phone_fab_locate") {
                if let coordinate = mapCoordinate {
                    withAnimation {
                        mapRegion.center = coordinate
                    }
                } else {
                    locatorHint = localizationManager.localized("map_live_no_signal")
                }
            }

            fabButton(systemImage: "arrow.triangle.turn.up.right.diamond.fill", id: "where_phone_fab_routes") {
                showRoutes = true
            }
        }
    }

    private func fabButton(systemImage: String, id: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: systemImage)
                .font(.body.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .frame(width: 44, height: 44)
                .background(Color.backgroundMedium.opacity(0.92))
                .clipShape(Circle())
                .overlay(Circle().stroke(Color.secondaryGold.opacity(0.4), lineWidth: 1))
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier(id)
    }

    private var mapTypeSheet: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_type_title"))
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                ForEach(HubMapType.allCases) { type in
                    Button {
                        mapTypeRaw = type.rawValue
                        showMapTypeSheet = false
                    } label: {
                        HStack {
                            Text(localizationManager.localized(type.titleKey))
                                .font(.subheadline.weight(.semibold))
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
                    showPetSoon = true
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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                showMapTypeSheet = false
            })
        }
    }

    private var alwaysAllowSheet: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("map_perm_always_title"))
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("map_perm_always_body"))
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Text(localizationManager.localized("map_perm_precise_hint"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                // W9 Q15: Motion honest row (no fake toggle) → Settings.
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("map_motion_row_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("map_motion_row_body"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                alwaysPromptDone = true
                showAlwaysAllowSheet = false
            })
        }
    }

    private func memberDetailSheet(_ member: HubMemberCard) -> some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(member.name)
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(
                    String(
                        format: localizationManager.localized("map_live_last_seen"),
                        WherePhoneTime.ago(since: member.at, localization: localizationManager)
                    )
                )
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                actionButton("map_member_save_place", id: "where_phone_member_save") {
                    showPlaces = true
                    selectedMember = nil
                }
                actionButton("map_member_directions", id: "where_phone_member_directions") {
                    selectedMember = nil
                    showRoutes = true
                }
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("map_member_quiet_zone"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("map_privacy_zone_hint"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Slider(value: $quietMeters, in: 50...500, step: 25) {
                        Text(localizationManager.localized("map_member_quiet_zone"))
                    }
                    .tint(Color.secondaryGold)
                    .onChange(of: quietMeters) { value in
                        FamilyMapQuietZoneStore.meters = value
                    }
                    Text("\(Int(quietMeters)) m")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
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
                Spacer()
            }
            .padding(Spacing.l)
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                selectedMember = nil
            })
        }
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
            Text(localizationManager.localized("family_invite_soft_title"))
                .font(.system(.title2, design: .serif).weight(.bold))
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
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .padding(Spacing.l)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black.opacity(0.55).ignoresSafeArea())
    }

    private var softPaywallSheet: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("premium_nudge_map_title"))
                .font(.system(.title2, design: .serif).weight(.bold))
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
                        .font(.system(.title2, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)
                    // Q24: graphical DatePicker draws black digits — force light inset for contrast on storm bg.
                    DatePicker(
                        "",
                        selection: $draftEventStart,
                        displayedComponents: [.date]
                    )
                    .datePickerStyle(.graphical)
                    .labelsHidden()
                    .tint(Color.secondaryGold)
                    .colorScheme(.light)
                    .padding(Spacing.s)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.white.opacity(0.92))
                    )
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    .accessibilityIdentifier("where_phone_family_calendar_picker")

                    Text(localizationManager.localized("family_cal_create_title"))
                        .font(.system(.title3, design: .serif).weight(.bold))
                        .foregroundColor(.textPrimary)
                    TextField(localizationManager.localized("family_cal_name_ph"), text: $draftEventTitle)
                        .textFieldStyle(.roundedBorder)
                    TextField(localizationManager.localized("family_cal_location_ph"), text: $draftEventPlace)
                        .textFieldStyle(.roundedBorder)
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
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                showFamilyCalendar = false
            })
        }
    }

    private func saveDraftFamilyEvent() {
        let title = draftEventTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !title.isEmpty else { return }
        let place = draftEventPlace.trimmingCharacters(in: .whitespacesAndNewlines)
        let event = FamilyMapLocalEvent(
            id: UUID(),
            title: title,
            place: place.isEmpty ? localizationManager.localized("family_cal_place") : place,
            start: draftEventStart,
            end: draftEventStart.addingTimeInterval(3600)
        )
        FamilyMapLocalEventStore.append(event)
        localEvents = FamilyMapLocalEventStore.load()
        draftEventTitle = ""
        draftEventPlace = ""
        if draftAddToIOS {
            Task { await addEventToIOSCalendar(event) }
        }
        showFamilyCalendar = false
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

    private var hubTabBar: some View {
        HStack(spacing: 0) {
            ForEach(HubTab.allCases) { tab in
                Button {
                    HapticFeedback.selection()
                    hubTab = tab
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: tab.systemImage)
                            .font(.system(size: 18, weight: .semibold))
                        Text(localizationManager.localized(tab.titleKey))
                            .font(.caption2.weight(.semibold))
                            .lineLimit(1)
                            .minimumScaleFactor(0.75)
                    }
                    .foregroundColor(hubTab == tab ? Color.secondaryGold : Color.textSecondary)
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
            Color.backgroundMedium.opacity(0.85)
                .overlay(
                    Rectangle()
                        .fill(Color.secondaryGold.opacity(0.25))
                        .frame(height: 1),
                    alignment: .top
                )
        )
        .accessibilityIdentifier("where_phone_hub_tab_bar")
    }

    private var mapCard: some View {
        card(symbol: "map.fill", titleKey: "where_phone_map_card_title") {
            // Always MapKit preview (Life360-lite). Pin optional; empty = no signal / last-point hole.
            FamilyHubMapKitView(
                region: $mapRegion,
                coordinate: mapCoordinate,
                title: friendlyPointName(mapPointName),
                mapTypeRaw: mapTypeRaw,
                pinDiameter: pinDiameterForSize(pinSizeRaw)
            )
            .frame(height: max(140, locationMapMaxHeight - 36))
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .accessibilityIdentifier("where_phone_map")
            .overlay(alignment: .topTrailing) {
                VStack(alignment: .trailing, spacing: 6) {
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
                    if mapPinSource == .live,
                       let speed = liveLocation.speedKmh,
                       speed > 0,
                       !inQuietZone {
                        Text(String(format: localizationManager.localized("map_live_speed_badge"), speed))
                            .font(.caption.weight(.bold))
                            .foregroundColor(.backgroundDark)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(Color.secondaryGold)
                            .clipShape(Capsule())
                            .accessibilityIdentifier("where_phone_speed_badge")
                    }
                }
                .padding(8)
            }

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

                // Yandex default first, then Apple — user always chooses.
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
                    // Preferred first: RU→Yandex, EN→Apple; both always available.
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
    private func pinDiameterForSize(_ raw: String) -> CGFloat {
        switch raw {
        case "S": return 28
        case "L": return 48
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
        return trimmed
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

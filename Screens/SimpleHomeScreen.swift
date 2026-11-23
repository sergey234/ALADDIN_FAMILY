import SwiftUI
import UIKit

/// Hybrid Simple Home Shell — «Удобный режим».
/// Pay-pains F3: при `PayPainsUIFlags.usesNewPayPainsHome` — полоса семьи + 3 двери + Меню.
/// Иначе: прежняя сетка плиток. Канон: `docs/ML_HANDOFF_PAY_PAINS_2026-10-28.md` §18/§28.
struct SimpleHomeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var subscriptionManager: SubscriptionManager
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.sizeCategory) private var sizeCategory

    /// HYBRID orbit UI (glass doors). Off → classic pay-pains list. Accessibility large type always list.
    @AppStorage("aladdin.simpleHomeHybridOrbit") private var hybridOrbitEnabled = true
    @AppStorage("aladdin.simpleHomePreferred") private var simpleHomePreferred = false
    @State private var showMoreSheet = false
    @State private var showVoiceNotes = false
    @State private var showChildDoor = false
    @State private var showPayPainsMenu = false
    @State private var pendingMoreNavigation: (() -> Void)?
    /// После раздела из «Все разделы» — снова открыть меню (назад ≠ сразу Удобный режим).
    @State private var restorePayPainsMenuOnReturn = false
    /// Сначала закрыть sheet «Ребёнок», потом navigate — иначе переход под sheet и «ничего не видно».
    @State private var pendingChildNavigation: (() -> Void)?
    @State private var showSoftReview = false
    @State private var showBedtimeSettings = false
    @State private var showChildMinutes = false
    @State private var childMinutesEnabled = true
    @State private var showWherePhone = false
    /// Family strip inputs: Keychain/JWT/roster decode must not run inside `body`
    /// (IPS build 30: SimpleHome body → FamilyLocalStore on main → 0x8BADF00D under the Day Journal).
    @State private var familyStripRosterCount = 0
    @State private var familyStripFirstName: String?
    /// After closing «Где семья» sheet — navigate (tariffs etc.) so push is not buried under modal.
    @State private var pendingWherePhoneNavigation: (() -> Void)?
    @State private var showChildPauseSheet = false
    @AppStorage("family_access_mode") private var familyAccessMode = "full"
    @AppStorage("parental_internet_paused") private var internetPaused = false
    @State private var pauseBusy = false
    @State private var pauseError: String?
    /// Entry-only: doors spin clockwise once around orbit, then rest (0 = done).
    @State private var hybridDoorIntroSpinDegrees: Double = 0
    @State private var hybridDoorIntroPlayed = false
    /// CapCut hero carousel (R01=5811 cutout + R02…R06). Off when Reduce Motion.
    @State private var hybridHeroIndex = 0
    @State private var hybridHeroRotationTask: Task<Void, Never>?
    /// Preloaded UIImages aligned 1:1 with `hybridHeroAssetNames` (nil = missing asset).
    /// Do not `compactMap` — index must match rotation idx or the center goes empty/wrong.
    @State private var hybridHeroImages: [UIImage?] = []
    /// Nudge hero art slightly up inside the circle (optical center).
    private static let hybridHeroYNudge: CGFloat = -14
    /// R04 phone is taller in-frame — lower + slight shrink so Dynamic Island / top bezel stay visible.
    private static let hybridHeroR04YNudge: CGFloat = 8
    private static let hybridHeroR04Scale: CGFloat = 0.90

    /// Orbit hero set: 5811 family-shield cutout + 5 CapCut cutouts (PNG alpha).
    private static let hybridHeroAssetNames: [String] = [
        "SimpleHome_Hero_5811",
        "SimpleHome_Hero_R02_FamilyWalk",
        "SimpleHome_Hero_R03_ShieldFirewall",
        "SimpleHome_Hero_R04_FamilyMapPhone",
        "SimpleHome_Hero_R05_ShieldVerify",
        "SimpleHome_Hero_R06_GlobePin"
    ]

    private static func hybridHeroLayout(for assetName: String) -> (y: CGFloat, scale: CGFloat) {
        if assetName.contains("R04_FamilyMapPhone") {
            return (y: hybridHeroR04YNudge, scale: hybridHeroR04Scale)
        }
        return (y: hybridHeroYNudge, scale: 1.0)
    }
    /// ~6.5s between frames (Device QA: 6–7s).
    private static let hybridHeroRotationSeconds: UInt64 = 6_500_000_000
    private static let hybridHeroCrossfade: Double = 0.45

    private let tileMinHeight: CGFloat = 120
    private var usesPayPainsHome: Bool { PayPainsUIFlags.usesNewPayPainsHome }
    /// Orbit only when pay-pains home + flag + not accessibility Dynamic Type (list fallback).
    private var usesHybridOrbit: Bool {
        usesPayPainsHome && hybridOrbitEnabled && !sizeCategory.isAccessibilityCategory
    }
    /// A sheet hides the orbit; its decorative motion must not keep re-rendering underneath
    /// (Where-is-family → Day Journal sits on top of this screen).
    private var isHomeCoveredBySheet: Bool {
        showWherePhone || showChildDoor || showPayPainsMenu || showMoreSheet || showVoiceNotes
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .premium)
            VStack(spacing: 0) {
                headerBar
                ScrollView(.vertical, showsIndicators: true) {
                    Group {
                        if usesPayPainsHome {
                            payPainsHomeContent
                        } else {
                            legacyHomeContent
                        }
                    }
                    .padding(.horizontal, Spacing.l)
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xl)
                }
            }

            if showSoftReview {
                PayPainsSoftReviewModal(
                    onWriteReview: {
                        PayPainsSoftReviewPrompt.markHandled()
                        showSoftReview = false
                        AppStoreReviewPrompt.openWriteReviewPage()
                    },
                    onLater: {
                        PayPainsSoftReviewPrompt.markHandled()
                        showSoftReview = false
                    }
                )
                .environmentObject(localizationManager)
                .transition(.opacity)
                .zIndex(20)
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            PayPainsSoftReviewPrompt.recordUsageDay()
            if PayPainsSoftReviewPrompt.shouldPresent {
                showSoftReview = true
            }
            preloadHybridHeroImagesIfNeeded()
            startHybridHeroRotationIfNeeded()
            refreshFamilyStripSnapshot()
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("FamilyMembersUpdated"))) { _ in
            refreshFamilyStripSnapshot()
        }
        .onDisappear {
            // Leave Convenient Mode → stop carousel (orbit remount must NOT cancel).
            hybridHeroRotationTask?.cancel()
            hybridHeroRotationTask = nil
        }
        .onReceive(NotificationCenter.default.publisher(for: .payPainsSoftReviewPending)) { _ in
            if PayPainsSoftReviewPrompt.shouldPresent {
                showSoftReview = true
            }
        }
        .sheet(isPresented: $showVoiceNotes) {
            VoiceNotesScreen()
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .sheet(isPresented: $showChildDoor, onDismiss: {
            if let pending = pendingChildNavigation {
                pendingChildNavigation = nil
                DispatchQueue.main.async { pending() }
            }
        }) {
            payPainsChildDoorSheet
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .sheet(isPresented: $showWherePhone, onDismiss: {
            // Sticky pending_open_map must die if sheet closed before consume.
            FamilyPushDeepLink.clearMapPendingOnDismiss(reason: "simple_home_where_dismiss")
            if let pending = pendingWherePhoneNavigation {
                pendingWherePhoneNavigation = nil
                DispatchQueue.main.async { pending() }
            }
        }) {
            WherePhoneSheetHost(
                isPresented: $showWherePhone,
                onLeaveToNavigate: { screen in
                    pendingWherePhoneNavigation = {
                        navigationManager.navigateTo(screen)
                    }
                    showWherePhone = false
                }
            )
            .equatable()
            .environmentObject(localizationManager)
            .environmentObject(navigationManager)
            // P0.6 S14: map pan/swipe must NOT dismiss the hub sheet (X / isPresented only).
            .interactiveDismissDisabled(true)
        }
        .sheet(isPresented: $showPayPainsMenu, onDismiss: {
            if let pending = pendingMoreNavigation {
                pendingMoreNavigation = nil
                DispatchQueue.main.async { pending() }
            }
        }) {
            payPainsMenuSheet
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .onChange(of: navigationManager.currentScreen) { screen in
            // Leaving Convenient for Antifake: drop soft map intents (keep SOS/battery/ImOK).
            if screen == .antifakeHub {
                showWherePhone = false
                FamilyPushDeepLink.clearSoftMapPending(reason: "simple_home_to_antifake")
            }
            guard screen == .simpleHome, restorePayPainsMenuOnReturn else { return }
            restorePayPainsMenuOnReturn = false
            // После fade goBack — снова «Все разделы» (Меню). Не раньше конца root transition.
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.28) {
                guard navigationManager.currentScreen == .simpleHome else { return }
                showPayPainsMenu = true
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("NavigateToVoiceDayRecap"))) { _ in
            showVoiceNotes = true
        }
        .onReceive(NotificationCenter.default.publisher(for: .navigateToVoiceNotes)) { _ in
            showVoiceNotes = true
        }
        .onReceive(NotificationCenter.default.publisher(for: FamilyPushDeepLink.navigateToFamilyMapName)) { _ in
            presentWherePhoneFromPendingIfNeeded(reason: "simple_home_notify")
        }
        .onAppear {
            presentWherePhoneFromPendingIfNeeded(reason: "simple_home_appear")
        }
        .sheet(isPresented: $showMoreSheet, onDismiss: {
            if let pending = pendingMoreNavigation {
                pendingMoreNavigation = nil
                DispatchQueue.main.async {
                    pending()
                }
            }
        }) {
            moreSheet
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .accessibilityIdentifier("simple_home_root")
    }

    /// Закрыть sheet «Ребёнок», затем выполнить переход (как Меню / pendingMoreNavigation).
    private func leaveChildDoorThen(_ action: @escaping () -> Void) {
        pendingChildNavigation = action
        showChildDoor = false
    }

    /// SSOT: open family map only after atomic take (TTL + clear). Never raw UserDefaults bool.
    private func presentWherePhoneFromPendingIfNeeded(reason: String) {
        guard FamilyPushDeepLink.takeMapPresentationIfNeeded(reason: reason) != nil else { return }
        showWherePhone = true
    }

    // MARK: - Pay-pains home (F3 + HYBRID orbit MAX)

    private var payPainsHomeContent: some View {
        VStack(spacing: Spacing.l) {
            payPainsFamilyStrip
            if usesHybridOrbit {
                payPainsHybridOrbitBlock
            } else {
                payPainsListDoorsBlock
            }
            openFullMainButton
        }
    }

    /// Classic list doors + AI + Menu (fallback / Dynamic Type / hybrid flag off).
    private var payPainsListDoorsBlock: some View {
        VStack(spacing: Spacing.l) {
            payPainsDoor(
                titleKey: "pay_pains_door_check_title",
                subtitleKey: "pay_pains_door_check_subtitle",
                systemImage: "magnifyingglass",
                aliveIcon: .check,
                identifier: "pay_pains_door_check",
                prominent: true
            ) {
                navigationManager.navigateToAntifakeHub(tab: .text)
            }
            payPainsDoor(
                titleKey: "pay_pains_door_child_title",
                subtitleKey: "pay_pains_door_child_subtitle",
                systemImage: "person.2.fill",
                aliveIcon: .child,
                identifier: "pay_pains_door_child",
                prominent: false
            ) {
                showChildDoor = true
            }
            payPainsDoor(
                titleKey: "pay_pains_door_where_title",
                subtitleKey: "pay_pains_door_where_subtitle",
                systemImage: "map.fill",
                aliveIcon: .whereFamily,
                identifier: "pay_pains_door_where",
                prominent: false,
                subtitleOverride: whereDoorSubtitle()
            ) {
                showWherePhone = true
            }
            if AppConfig.isCompanionAvailable {
                payPainsAIFriendsRow
            }
            payPainsMenuRow
        }
    }

    /// HYBRID: hero 5811 + 3 glass doors + chips (same nav as list).
    /// W1: hero raised + X-centered; top sits just under «Проверить»; G: soft pulse.
    private var payPainsHybridOrbitBlock: some View {
        VStack(spacing: Spacing.l) {
            ZStack {
                Circle()
                    .stroke(
                        reduceMotion
                            ? Color.white.opacity(0.14)
                            : Color.secondaryGold.opacity(0.28),
                        lineWidth: reduceMotion ? 1 : 1.5
                    )
                    .frame(width: 318, height: 318)
                    .allowsHitTesting(false)

                hybridOrbitHeroView

                hybridGlassDoor(
                    titleKey: "pay_pains_door_check_title",
                    subtitleKey: "pay_pains_door_check_subtitle",
                    imageName: "SimpleHome_Door_Check",
                    identifier: "pay_pains_door_check",
                    restOffset: CGSize(width: 0, height: -168),
                    pulsePhase: 0
                ) {
                    navigationManager.navigateToAntifakeHub(tab: .text)
                }
                hybridGlassDoor(
                    titleKey: "pay_pains_door_child_title",
                    subtitleKey: "pay_pains_door_child_subtitle",
                    imageName: "SimpleHome_Door_Child",
                    identifier: "pay_pains_door_child",
                    restOffset: CGSize(width: -128, height: 78),
                    pulsePhase: 0.35
                ) {
                    showChildDoor = true
                }
                hybridGlassDoor(
                    titleKey: "pay_pains_door_where_title",
                    subtitleKey: "pay_pains_door_where_subtitle",
                    imageName: "SimpleHome_Door_Where",
                    identifier: "pay_pains_door_where",
                    restOffset: CGSize(width: 128, height: 78),
                    pulsePhase: 0.7
                ) {
                    showWherePhone = true
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 420)
            .padding(.top, Spacing.s)
            .accessibilityElement(children: .contain)
            .onAppear {
                startHybridDoorIntroSpinIfNeeded()
                preloadHybridHeroImagesIfNeeded()
                startHybridHeroRotationIfNeeded()
            }
            .onDisappear {
                // Do NOT cancel hero rotation here — brief remounts on device killed the carousel.
                // Allow clockwise intro again next time user opens Aladdin start orbit.
                hybridDoorIntroPlayed = false
                hybridDoorIntroSpinDegrees = 0
            }

            hybridChipsRow
        }
        .accessibilityIdentifier("pay_pains_hybrid_orbit")
    }

    /// P0.1+P0.2: one circular slot for all 6 heroes (~80% of orbit 318 → 254).
    /// No 5811 rounded chrome (S05 double-layer). CapCut assets untouched — scale is Swift only.
    private static let hybridHeroCircleDiameter: CGFloat = 254

    private var hybridOrbitHeroView: some View {
        let names = Self.hybridHeroAssetNames
        let idx = hybridHeroIndex % max(names.count, 1)
        let name = names[idx]
        let d = Self.hybridHeroCircleDiameter
        let preloaded: UIImage? = {
            guard idx < hybridHeroImages.count else { return nil }
            return hybridHeroImages[idx]
        }()
        return ZStack {
            // Keep previous frame under crossfade so device never shows an empty hole.
            Circle()
                .fill(Color.black.opacity(0.22))
                .frame(width: d, height: d)
            Group {
                if let preloaded {
                    Image(uiImage: preloaded)
                        .resizable()
                        .scaledToFit()
                } else if UIImage(named: name) != nil {
                    Image(name)
                        .resizable()
                        .scaledToFit()
                } else {
                    // Honest empty — never blank hole without a log trail.
                    Circle()
                        .fill(Color.secondaryGold.opacity(0.18))
                        .overlay(
                            Image(systemName: "photo")
                                .font(.title2)
                                .foregroundColor(.secondaryGold.opacity(0.7))
                        )
                }
            }
            .scaleEffect(Self.hybridHeroLayout(for: name).scale)
            .frame(width: d, height: d)
            .offset(y: Self.hybridHeroLayout(for: name).y)
            .frame(width: d, height: d)
            .clipShape(Circle())
            .id(name)
            .transition(.opacity)
        }
        .shadow(color: Color.black.opacity(0.35), radius: 14, y: 8)
        .animation(.easeInOut(duration: Self.hybridHeroCrossfade), value: hybridHeroIndex)
        .allowsHitTesting(false)
        .accessibilityHidden(true)
        .accessibilityIdentifier("pay_pains_hybrid_hero")
    }

    private func preloadHybridHeroImagesIfNeeded() {
        guard hybridHeroImages.count != Self.hybridHeroAssetNames.count else { return }
        hybridHeroImages = Self.hybridHeroAssetNames.map { name in
            let img = UIImage(named: name)
            if img == nil {
                print("HERO_ROTATE asset_nil name=\(name)")
            }
            return img
        }
        let loaded = hybridHeroImages.compactMap { $0 }.count
        print("HERO_ROTATE preload loaded=\(loaded)/\(Self.hybridHeroAssetNames.count)")
        if loaded != Self.hybridHeroAssetNames.count {
            print("SimpleHome hero preload partial \(loaded)/\(Self.hybridHeroAssetNames.count)")
        }
    }

    /// One clockwise lap on first enter only (Reduce Motion → skip).
    private func startHybridDoorIntroSpinIfNeeded() {
        guard !reduceMotion else {
            hybridDoorIntroSpinDegrees = 0
            hybridDoorIntroPlayed = true
            return
        }
        guard !hybridDoorIntroPlayed else { return }
        hybridDoorIntroPlayed = true
        // Start one full turn behind rest; animate to 0 = parked positions.
        hybridDoorIntroSpinDegrees = 360
        withAnimation(.easeOut(duration: 1.15)) {
            hybridDoorIntroSpinDegrees = 0
        }
    }

    /// Rest offset rotated by `hybridDoorIntroSpinDegrees` around orbit center.
    private func doorOrbitOffset(rest: CGSize) -> CGSize {
        let extra = hybridDoorIntroSpinDegrees * .pi / 180
        guard abs(extra) > 0.0001 else { return rest }
        let radius = hypot(rest.width, rest.height)
        guard radius > 1 else { return rest }
        // Rest angle from top, clockwise (x right, y down).
        let base = atan2(rest.width, -rest.height)
        let a = base + extra
        return CGSize(width: radius * sin(a), height: -radius * cos(a))
    }

    private func startHybridHeroRotationIfNeeded() {
        guard !reduceMotion else {
            let loaded = hybridHeroImages.compactMap { $0 }.count
            print("HERO_ROTATE skip_reduce_motion idx=\(hybridHeroIndex)/\(Self.hybridHeroAssetNames.count) loaded=\(loaded)")
            return
        }
        guard Self.hybridHeroAssetNames.count > 1 else { return }
        // Already running — keep it (device remounts used to cancel → single stuck frame).
        if let existing = hybridHeroRotationTask, !existing.isCancelled {
            return
        }
        hybridHeroRotationTask?.cancel()
        let loaded0 = hybridHeroImages.compactMap { $0 }.count
        print("HERO_ROTATE start idx=\(hybridHeroIndex)/\(Self.hybridHeroAssetNames.count) loaded=\(loaded0)")
        hybridHeroRotationTask = Task { @MainActor in
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: Self.hybridHeroRotationSeconds)
                if Task.isCancelled { break }
                guard !isHomeCoveredBySheet,
                      DecorativeMotionPolicy.allowsContinuousMotionNow(reduceMotion: false) else { continue }
                withAnimation(.easeInOut(duration: Self.hybridHeroCrossfade)) {
                    hybridHeroIndex = (hybridHeroIndex + 1) % Self.hybridHeroAssetNames.count
                }
                let loaded = hybridHeroImages.compactMap { $0 }.count
                let name = Self.hybridHeroAssetNames[hybridHeroIndex % Self.hybridHeroAssetNames.count]
                let ok = (hybridHeroIndex < hybridHeroImages.count && hybridHeroImages[hybridHeroIndex] != nil)
                    || UIImage(named: name) != nil
                print("HERO_ROTATE tick idx=\(hybridHeroIndex)/\(Self.hybridHeroAssetNames.count) loaded=\(loaded) frame_ok=\(ok) name=\(name)")
            }
        }
    }

    private func hybridGlassDoor(
        titleKey: String,
        subtitleKey: String,
        imageName: String,
        identifier: String,
        restOffset: CGSize,
        pulsePhase: Double,
        action: @escaping () -> Void
    ) -> some View {
        let title = localizationManager.localized(titleKey)
        let hint = localizationManager.localized(subtitleKey)
        let size: CGFloat = 88
        let offset = doorOrbitOffset(rest: restOffset)
        return Button {
            HapticFeedback.impact(reduceMotion ? .soft : .light)
            AnalyticsManager.shared.trackEvent(
                "pay_pains_door_tap",
                parameters: ["door": identifier, "ui": "hybrid_orbit"]
            )
            action()
        } label: {
            VStack(spacing: 8) {
                ZStack {
                    Circle()
                        .fill(.ultraThinMaterial)
                        .frame(width: size, height: size)
                    Circle()
                        .fill(Color.white.opacity(0.10))
                        .frame(width: size, height: size)
                    Circle()
                        .stroke(Color.white.opacity(0.28), lineWidth: 1.5)
                        .frame(width: size, height: size)
                    Image(imageName)
                        .resizable()
                        .scaledToFit()
                        // P0.1b: door icon fill 0.86–0.92 (was 0.72 — looked tiny vs hero).
                        .frame(width: size * 0.88, height: size * 0.88)
                        .clipShape(Circle())
                        .accessibilityHidden(true)
                }
                .frame(width: size, height: size)
                .contentShape(Circle())
                .shadow(color: Color.black.opacity(0.25), radius: 8, y: 4)
                .decorativePulse(delay: pulsePhase, isEnabled: !isHomeCoveredBySheet)

                Text(title)
                    .font(AladdinFamilyType.subheadline(weight: .semibold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.55)
                    .allowsTightening(true)
            }
            .frame(minWidth: size + 24, minHeight: size + 36)
        }
        .buttonStyle(.plain)
        .offset(offset)
        .accessibilityIdentifier(identifier)
        .accessibilityLabel(title)
        .accessibilityHint(hint)
        .accessibilityAddTraits(.isButton)
    }

    private var hybridChipsRow: some View {
        HStack(spacing: 12) {
            if AppConfig.isCompanionAvailable {
                hybridChip(
                    titleKey: "pay_pains_ai_friends_row",
                    systemImage: "person.2.wave.2.fill",
                    aliveIcon: .aiFriends,
                    identifier: "pay_pains_ai_friends"
                ) {
                    navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
                }
            }
            hybridChip(
                titleKey: "pay_pains_menu_button",
                systemImage: "line.3.horizontal",
                aliveIcon: .menu,
                identifier: "pay_pains_menu"
            ) {
                showPayPainsMenu = true
            }
        }
        .frame(maxWidth: .infinity)
    }

    private func hybridChip(
        titleKey: String,
        systemImage: String,
        aliveIcon: AliveIconID?,
        identifier: String,
        action: @escaping () -> Void
    ) -> some View {
        let title = localizationManager.localized(titleKey)
        return Button {
            HapticFeedback.impact(reduceMotion ? .soft : .light)
            AnalyticsManager.shared.trackEvent(
                "pay_pains_chip_tap",
                parameters: ["chip": identifier]
            )
            action()
        } label: {
            HStack(spacing: 8) {
                Group {
                    if let aliveIcon {
                        AliveGlyph(id: aliveIcon, size: 20) {
                            Image(systemName: systemImage)
                                .font(.subheadline.weight(.semibold))
                        }
                    } else {
                        Image(systemName: systemImage)
                            .font(.subheadline.weight(.semibold))
                    }
                }
                .accessibilityHidden(true)
                Text(title)
                    .font(AladdinFamilyType.subheadline(weight: .semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.55)
                    .allowsTightening(true)
            }
            .foregroundColor(.white)
            .padding(.horizontal, 14)
            .padding(.vertical, 12)
            .frame(maxWidth: .infinity)
            .frame(minHeight: 44)
            .background(
                Capsule()
                    .fill(.ultraThinMaterial)
                    .overlay(Capsule().fill(Color.white.opacity(0.08)))
                    .overlay(Capsule().stroke(Color.white.opacity(0.22), lineWidth: 1))
            )
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier(identifier)
        .accessibilityLabel(title)
    }

    private var payPainsAIFriendsRow: some View {
        Button {
            HapticFeedback.impact(.light)
            navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
        } label: {
            HStack {
                AliveGlyph(id: .aiFriends, size: 28) {
                    Image(systemName: "person.2.wave.2.fill")
                        .font(.subheadline.weight(.semibold))
                }
                Text(localizationManager.localized("pay_pains_ai_friends_row"))
                    .font(AladdinFamilyType.subheadline(weight: .semibold))
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
            }
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("pay_pains_ai_friends")
    }

    private var payPainsMenuRow: some View {
        Button {
            HapticFeedback.impact(.light)
            showPayPainsMenu = true
        } label: {
            HStack {
                AliveGlyph(id: .menu, size: 28) {
                    Image(systemName: "line.3.horizontal")
                        .font(.title3)
                }
                Text(localizationManager.localized("pay_pains_menu_button"))
                    .font(AladdinFamilyType.subheadline(weight: .bold))
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
            }
            .foregroundColor(.white)
            .padding(Spacing.m)
            .frame(maxWidth: .infinity)
            .aladdinProductCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("pay_pains_menu")
    }

    private func refreshFamilyStripSnapshot() {
        let members = FamilyLocalStore.loadPersistedMembers()
        if familyStripRosterCount != members.count {
            familyStripRosterCount = members.count
        }
        let firstName = members.first?.name
        if familyStripFirstName != firstName {
            familyStripFirstName = firstName
        }
    }

    private var payPainsFamilyStrip: some View {
        // Same SSOT as Main tariff card (`effectiveFamilyDisplay`) — never local roster alone.
        let familyDisplay = subscriptionManager.effectiveFamilyDisplay(localRosterCount: familyStripRosterCount)
        let slotsUsed = familyDisplay.slotsUsed
        let slotsMax = familyDisplay.slotsMax
        let isEmpty = slotsUsed == 0 && familyStripRosterCount == 0
        // Compact «Семья · N из M» — same numbers as Main; never truncate with «…человек».
        // LOCKED A★: always «Семья · N из M мест» — never naked «1 из 1» on iOS 15.
        let slotsFull = String(
            format: localizationManager.localized("pay_pains_family_strip_slots_fmt"),
            slotsUsed,
            slotsMax
        )
        let countLabel = isEmpty
            ? localizationManager.localized("pay_pains_family_strip_empty")
            : slotsFull
        let addFull = localizationManager.localized("pay_pains_family_strip_add_to_family")
        return HStack(spacing: 6) {
            Button {
                HapticFeedback.impact(.light)
                AnalyticsManager.shared.trackEvent("pay_pains_family_strip_tap")
                navigationManager.navigateTo(.family)
            } label: {
                HStack(spacing: 6) {
                    if isEmpty {
                        ZStack {
                            Circle()
                                .fill(Color.white.opacity(0.12))
                                .frame(width: 28, height: 28)
                            Image(systemName: "person.badge.plus")
                                .font(.caption2.weight(.semibold))
                                .foregroundColor(.white)
                        }
                    } else {
                        let name = familyStripFirstName ?? "A"
                        Text(PayPainsMemberInitials.from(name: name))
                            .font(AladdinFamilyType.caption2(weight: .bold))
                            .foregroundColor(.white)
                            .frame(width: 28, height: 28)
                            .background(Circle().fill(Color.secondaryGold.opacity(0.35)))
                            .overlay(Circle().stroke(Color.white.opacity(0.25), lineWidth: 1))
                            .accessibilityHidden(true)
                    }
                    Text(countLabel)
                        .font(AladdinFamilyType.caption(weight: .semibold))
                        .foregroundColor(.white)
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                        .allowsTightening(true)
                        .multilineTextAlignment(.leading)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("pay_pains_family_strip")
            .accessibilityLabel(countLabel)

            Button {
                HapticFeedback.impact(.light)
                AnalyticsManager.shared.trackEvent(
                    "pay_pains_chip_tap",
                    parameters: ["chip": "pay_pains_family_strip_add_to_family"]
                )
                _ = subscriptionManager.canAddFamilyMember(currentCount: slotsUsed)
                startFamilyAddOrCreateDirectly()
            } label: {
                Text(addFull)
                    .font(AladdinFamilyType.caption2(weight: .semibold))
                    .foregroundColor(Color.secondaryGold)
                    .lineLimit(2)
                    .minimumScaleFactor(0.75)
                    .allowsTightening(true)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)
                    .frame(minHeight: 28)
                    .frame(maxWidth: 150)
                    .background(
                        Capsule()
                            .fill(Color.secondaryGold.opacity(0.18))
                            .overlay(Capsule().stroke(Color.secondaryGold.opacity(0.75), lineWidth: 1))
                    )
            }
            .buttonStyle(.plain)
            .layoutPriority(1)
            .accessibilityIdentifier("pay_pains_family_strip_add_to_family")
            .accessibilityLabel(addFull)
        }
        .padding(.horizontal, Spacing.s)
        .padding(.vertical, 8)
        .frame(maxWidth: .infinity)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(
                    isEmpty ? Color.secondaryGold.opacity(0.85) : Color.clear,
                    lineWidth: 1.5
                )
        )
    }

    /// W11-A: skip AddMember hub + «Семья под защитой» when we can add/create directly.
    private func startFamilyAddOrCreateDirectly() {
        let members = FamilyLocalStore.loadPersistedMembers()
        let needsCreate = FamilyLocalStore.needsServerFamilyCreation(members: members)
        let canManage = FamilyRosterAccess.canManageRoster(
            members: members,
            myMemberId: UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey),
            currentUserRoleFallback: UserDefaults.standard.string(forKey: "current_user_role")
        )
        if !needsCreate && canManage {
            UserDefaults.standard.set(true, forKey: "admin_add_mode")
            UserDefaults.standard.set(true, forKey: "family_registration_auto_start")
            UserDefaults.standard.synchronize()
            navigationManager.navigateTo(.mainWithRegistration)
            return
        }
        if needsCreate {
            FamilyLocalStore.prepareCreateFamilyFlow()
            UserDefaults.standard.set(true, forKey: "family_registration_auto_start")
            UserDefaults.standard.synchronize()
            navigationManager.navigateTo(.mainWithRegistration)
            return
        }
        navigationManager.navigateTo(.addMemberOptions)
    }

    /// F6: only real Screen Time report minutes — never invent.
    private func minutesDoorSubtitle() -> String {
        guard let snap = ScreenTimeUsageStore.load(),
              snap.isTodayInStoredTimezone,
              !snap.isStale,
              snap.totalSeconds > 0 else {
            return localizationManager.localized("pay_pains_child_minutes_subtitle")
        }
        let mins = max(1, snap.totalSeconds / 60)
        return String(
            format: localizationManager.localized("pay_pains_child_minutes_real_fmt"),
            mins
        )
    }

    /// F7/F10: last real place event or travel minutes — empty stays honest default.
    private func whereDoorSubtitle() -> String {
        if let travel = WherePhoneTravel.minutesInTransitToday(), travel > 0 {
            return String(
                format: localizationManager.localized("pay_pains_where_travel_fmt"),
                travel
            )
        }
        if let event = GeofenceEventStore.todayEvents().first {
            let actionKey = event.isArrival ? "where_phone_signal_arrived" : "where_phone_signal_left"
            let action = String(
                format: localizationManager.localized(actionKey),
                event.regionName
            )
            return "\(event.time) · \(action)"
        }
        return localizationManager.localized("pay_pains_door_where_subtitle")
    }

    private func payPainsDoor(
        titleKey: String,
        subtitleKey: String,
        systemImage: String,
        aliveIcon: AliveIconID? = nil,
        identifier: String,
        prominent: Bool,
        subtitleOverride: String? = nil,
        action: @escaping () -> Void
    ) -> some View {
        let title = localizationManager.localized(titleKey)
        let subtitle = subtitleOverride ?? localizationManager.localized(subtitleKey)
        let glyphSize: CGFloat = prominent ? 36 : 32
        return Button {
            HapticFeedback.impact(reduceMotion ? .soft : .light)
            AnalyticsManager.shared.trackEvent(
                "pay_pains_door_tap",
                parameters: ["door": identifier]
            )
            action()
        } label: {
            HStack(alignment: .center, spacing: Spacing.m) {
                Group {
                    if let aliveIcon {
                        AliveGlyph(id: aliveIcon, size: glyphSize) {
                            Image(systemName: systemImage)
                                .font(prominent ? .title.weight(.semibold) : .title2.weight(.semibold))
                                .foregroundColor(.white)
                        }
                    } else {
                        Image(systemName: systemImage)
                            .font(prominent ? .title.weight(.semibold) : .title2.weight(.semibold))
                            .foregroundColor(.white)
                    }
                }
                .frame(width: 36)
                .accessibilityHidden(true)
                VStack(alignment: .leading, spacing: 6) {
                    // W4 / D1.5: New York на заголовке и подписи двери (AladdinFamilyType).
                    Text(title)
                        .font(prominent ? AladdinFamilyType.title2() : AladdinFamilyType.title3())
                        .foregroundColor(.white)
                        .lineLimit(1)
                        .minimumScaleFactor(0.55)
                        .allowsTightening(true)
                    Text(subtitle)
                        .font(AladdinFamilyType.subheadline())
                        .foregroundColor(Color.textSecondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.55)
                        .allowsTightening(true)
                }
                .frame(minWidth: 0, maxWidth: .infinity, alignment: .leading)
                Spacer(minLength: 0)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(Color.textSecondary)
                    .accessibilityHidden(true)
            }
            .padding(Spacing.l)
            .frame(maxWidth: .infinity, minHeight: prominent ? 108 : 88, alignment: .leading)
            .aladdinProductCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier(identifier)
        .accessibilityLabel(title)
        .accessibilityHint(subtitle)
        .accessibilityLabel(
            localizationManager.localized(titleKey)
                + ". "
                + localizationManager.localized(subtitleKey)
        )
    }

    /// Map visibility only (hide others). Not parental pause/limits.
    private func setFamilyAccessMode(_ mode: String) {
        guard mode == "full" || mode == "limited" else { return }
        guard familyAccessMode != mode else {
            print("ℹ️ family_access_mode already=\(mode)")
            return
        }
        familyAccessMode = mode
        print("✅ family_access_mode → \(mode) (map: \(mode == "limited" ? "hide others" : "show all"))")
        HapticFeedback.impact(.light)
        ToastManager.shared.showInfo(
            localizationManager.localized(
                mode == "limited" ? "family_access_toast_limited" : "family_access_toast_full"
            )
        )
    }

    /// Wave C CapCut hero · same slot size as Where Family (~320×220).
    private func childHeroCard(assetName: String) -> some View {
        Image(assetName)
            .resizable()
            .scaledToFit()
            .frame(maxWidth: .infinity)
            .frame(height: 220)
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .accessibilityHidden(true)
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, alignment: .leading)
            .aladdinProductCard(cornerRadius: CornerRadius.large)
    }

    private var familyMapVisibilityCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.s) {
                AliveGlyph(id: .mapVis, size: 28) {
                    Image(systemName: "map.fill")
                        .font(.title3.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .accessibilityHidden(true)
                Text(localizationManager.localized("family_access_section_title"))
                    .font(AladdinFamilyType.title3())
                    .foregroundColor(.white)
            }
            // Round2 S08: no “паузы и лимиты…” prose.
            let accessBody = localizationManager.localized("family_access_section_body")
            if !accessBody.isEmpty, accessBody != "family_access_section_body" {
                Text(accessBody)
                    .font(AladdinFamilyType.subheadline())
                    .foregroundColor(.white.opacity(0.8))
                    .fixedSize(horizontal: false, vertical: true)
            }
            Text(localizationManager.localized("family_access_hint"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.7))
            HStack(spacing: Spacing.s) {
                Button {
                    setFamilyAccessMode("full")
                    HapticFeedback.selection()
                } label: {
                    HStack(spacing: 6) {
                        AliveGlyph(id: .famGroups, size: 18) {
                            Image(systemName: "person.3.fill")
                                .font(.caption.weight(.semibold))
                        }
                        Text(localizationManager.localized("family_access_full"))
                            .font(.caption.weight(.semibold))
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                    }
                    .foregroundColor(familyAccessMode == "full" ? .backgroundDark : .white)
                    .frame(maxWidth: .infinity, minHeight: 36, alignment: .center)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.s)
                    .background(familyAccessMode == "full" ? Color.secondaryGold : Color.white.opacity(0.12))
                    .clipShape(Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("family_access_full")
                Button {
                    setFamilyAccessMode("limited")
                    HapticFeedback.selection()
                } label: {
                    HStack(spacing: 6) {
                        AliveGlyph(id: .mapMe, size: 18) {
                            Image(systemName: "person.fill")
                                .font(.caption.weight(.semibold))
                        }
                        Text(localizationManager.localized("family_access_limited"))
                            .font(.caption.weight(.semibold))
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                    }
                    .foregroundColor(familyAccessMode == "limited" ? .backgroundDark : .white)
                    .frame(maxWidth: .infinity, minHeight: 36, alignment: .center)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.s)
                    .background(familyAccessMode == "limited" ? Color.secondaryGold : Color.white.opacity(0.12))
                    .clipShape(Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("family_access_limited")
            }
            Text(
                localizationManager.localized(
                    familyAccessMode == "limited"
                        ? "family_access_effect_limited"
                        : "family_access_effect_full"
                )
            )
            .font(.caption.weight(.medium))
            .foregroundColor(.secondaryGold)
            .fixedSize(horizontal: false, vertical: true)
            .accessibilityIdentifier("family_access_effect")
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityElement(children: .contain)
    }

    private var payPainsChildDoorSheet: some View {
        WellnessNavigationStack {
            ZStack {
                StormMeshBackground(variant: .premium)
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        // Wave C hero · боль: телефон без контроля
                        childHeroCard(assetName: "ICON_ALIVE_HERO_ChildControl")
                            .accessibilityIdentifier("pay_pains_child_hero_control")

                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("child_overview_title"))
                                .font(AladdinFamilyType.title3())
                                .foregroundColor(.white)
                            Text(localizationManager.localized("child_overview_body"))
                                .font(AladdinFamilyType.subheadline())
                                .foregroundColor(.white.opacity(0.8))
                        }
                        .padding(Spacing.m)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .aladdinProductCard(cornerRadius: CornerRadius.large)

                        familyMapVisibilityCard

                        payPainsDoor(
                            titleKey: "pay_pains_child_pause_title",
                            subtitleKey: "pay_pains_child_pause_subtitle",
                            systemImage: "pause.circle.fill",
                            aliveIcon: .childPause,
                            identifier: "pay_pains_child_pause",
                            prominent: true
                        ) {
                            showChildPauseSheet = true
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_sites_title",
                            subtitleKey: "pay_pains_child_sites_subtitle",
                            systemImage: "globe",
                            aliveIcon: .childSites,
                            identifier: "pay_pains_child_sites",
                            prominent: false
                        ) {
                            leaveChildDoorThen { navigationManager.navigateTo(.parentalControl) }
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_limit_title",
                            subtitleKey: "pay_pains_child_limit_subtitle",
                            systemImage: "hourglass",
                            aliveIcon: .childLimit,
                            identifier: "pay_pains_child_limit",
                            prominent: false
                        ) {
                            // Лимит → модалка минут/времени, не «тот же» parental вслепую.
                            showChildMinutes = true
                        }
                        Text(localizationManager.localized("pay_pains_child_quiet_minutes_hint"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.75))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, Spacing.xs)

                        // Wave C hero · боль: ребёнка атакуют в сети
                        childHeroCard(assetName: "ICON_ALIVE_HERO_ChildThreats")
                            .accessibilityIdentifier("pay_pains_child_hero_threats")

                        Text(localizationManager.localized("pay_pains_child_more_heading"))
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.top, Spacing.s)

                        // F4: Время сна + закрытие телефона
                        payPainsDoor(
                            titleKey: "pay_pains_child_bedtime_title",
                            subtitleKey: "pay_pains_child_bedtime_subtitle",
                            systemImage: "moon.zzz.fill",
                            aliveIcon: .childBedtime,
                            identifier: "pay_pains_child_bedtime",
                            prominent: false
                        ) {
                            showBedtimeSettings = true
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_reward_title",
                            subtitleKey: "pay_pains_child_reward_subtitle",
                            systemImage: "gift.fill",
                            aliveIcon: .childReward,
                            identifier: "pay_pains_child_reward",
                            prominent: false
                        ) {
                            leaveChildDoorThen { navigationManager.navigateTo(.childRewards) }
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_minutes_title",
                            subtitleKey: "pay_pains_child_minutes_subtitle",
                            systemImage: "clock.fill",
                            aliveIcon: .childMinutes,
                            identifier: "pay_pains_child_minutes",
                            prominent: false,
                            subtitleOverride: minutesDoorSubtitle()
                        ) {
                            showChildMinutes = true
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_screen_title",
                            subtitleKey: "pay_pains_child_screen_subtitle",
                            systemImage: "gamecontroller.fill",
                            aliveIcon: .childScreen,
                            identifier: "pay_pains_child_screen",
                            prominent: false
                        ) {
                            leaveChildDoorThen { navigationManager.navigateTo(.childInterface) }
                        }
                    }
                    .padding(Spacing.l)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(localizationManager.localized("pay_pains_door_child_title"))
                        .font(.headline.weight(.bold))
                        .foregroundColor(.secondaryGold)
                        .accessibilityAddTraits(.isHeader)
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_done")) {
                        pendingChildNavigation = nil
                        showChildDoor = false
                    }
                }
            }
            .sheet(isPresented: $showBedtimeSettings) {
                SleepTimeSettingsModal(isPresented: $showBedtimeSettings)
                    .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showChildMinutes) {
                FamilyTimeControlModal(
                    isPresented: $showChildMinutes,
                    isEnabled: $childMinutesEnabled
                )
                .environmentObject(localizationManager)
            }
            .sheet(isPresented: $showChildPauseSheet) {
                payPainsChildPauseSheet
                    .environmentObject(localizationManager)
            }
        }
        .wellnessSheetDetents()
    }

    private var payPainsChildPauseSheet: some View {
        WellnessNavigationStack {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(
                    localizationManager.localized(
                        internetPaused
                            ? "pay_pains_child_pause_status_on"
                            : "pay_pains_child_pause_status_off"
                    )
                )
                .font(.headline)
                .foregroundColor(.white)

                Text(localizationManager.localized("pay_pains_child_pause_hint"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.8))

                if let pauseError {
                    Text(pauseError)
                        .font(.caption)
                        .foregroundColor(.orange)
                }

                Button {
                    guard !pauseBusy else { return }
                    pauseBusy = true
                    pauseError = nil
                    let next = !internetPaused
                    ParentalControlManager.shared.setInternetPaused(next) { result in
                        DispatchQueue.main.async {
                            pauseBusy = false
                            switch result {
                            case .success:
                                internetPaused = next
                                PayPainsSoftReviewPrompt.noteBenefitCompleted()
                            case .failure:
                                pauseError = localizationManager.localized("pay_pains_child_pause_error")
                            }
                        }
                    }
                } label: {
                    Text(
                        localizationManager.localized(
                            pauseBusy
                                ? "pay_pains_child_pause_saving"
                                : (internetPaused
                                    ? "pay_pains_child_pause_off"
                                    : "pay_pains_child_pause_on")
                        )
                    )
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(Color.secondaryGold.opacity(0.35))
                    .clipShape(Capsule())
                }
                .buttonStyle(.plain)
                .disabled(pauseBusy)
                .accessibilityIdentifier("pay_pains_child_pause_toggle")

                Spacer()
            }
            .padding(Spacing.l)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            .background(StormMeshBackground(variant: .premium))
            .navigationTitle(localizationManager.localized("pay_pains_child_pause_sheet_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_done")) {
                        showChildPauseSheet = false
                    }
                }
            }
        }
        .wellnessSheetDetents()
    }

    private var payPainsMenuSheet: some View {
        WellnessNavigationStack {
            ZStack {
                // Hub Calm Navy — same Family Hub canvas (readable glass rows).
                AladdinSnowballPalette.canvasGradient
                    .ignoresSafeArea()
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        // Отличается от белого List: тёмный glass + serif title (иконка/золото ALADDIN).
                        Text(localizationManager.localized("pay_pains_menu_title"))
                            .font(AladdinFamilyType.title2())
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.top, Spacing.s)

                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_plan",
                            systemImage: "creditcard.fill",
                            id: "pay_pains_menu_plan"
                        ) {
                            navigationManager.navigateTo(.tariffs)
                        }
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_settings",
                            systemImage: "gearshape.fill",
                            id: "pay_pains_menu_settings"
                        ) {
                            navigationManager.navigateTo(.settings)
                        }
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_protection",
                            systemImage: "shield.fill",
                            id: "pay_pains_menu_protection"
                        ) {
                            navigationManager.navigateTo(.networkProtection)
                        }
                        if AppConfig.isCompanionAvailable {
                            payPainsMenuGlassRow(
                                titleKey: "pay_pains_menu_ai_friends",
                                systemImage: "person.2.wave.2.fill",
                                id: "pay_pains_menu_ai_friends"
                            ) {
                                navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
                            }
                        }
                        if AppConfig.isAIAssistantAvailable {
                            payPainsMenuGlassRow(
                                titleKey: "pay_pains_menu_ai_helper",
                                systemImage: "brain.head.profile",
                                id: "pay_pains_menu_ai_helper"
                            ) {
                                navigationManager.navigateTo(.aiAssistant)
                            }
                        }
                        if AppConfig.isFamilyChatAvailable {
                            payPainsMenuGlassRow(
                                titleKey: "pay_pains_menu_family_chat",
                                systemImage: "message.fill",
                                id: "pay_pains_menu_family_chat"
                            ) {
                                navigationManager.navigateTo(.familyChat)
                            }
                        }
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_notifications_analytics",
                            systemImage: "bell.fill",
                            id: "pay_pains_menu_notifications_analytics"
                        ) {
                            navigationManager.navigateTo(.notifications)
                        }
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_full_screen",
                            systemImage: "rectangle.split.2x1",
                            id: "pay_pains_menu_full_screen"
                        ) {
                            navigationManager.navigateToRoot(.main)
                        }
                    }
                    .padding(Spacing.l)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_done")) {
                        HapticFeedback.selection()
                        pendingMoreNavigation = nil
                        restorePayPainsMenuOnReturn = false
                        showPayPainsMenu = false
                    }
                }
            }
        }
        .wellnessSheetDetents()
    }

    private func payPainsMenuGlassRow(
        titleKey: String,
        systemImage: String,
        id: String,
        action: @escaping () -> Void
    ) -> some View {
        Button {
            // REGRESSION GUARD (build 24 «navigate first» broke this):
            // navigateTo while sheet is up leaves «Все разделы» covering the
            // destination — user must swipe it down N times. Always dismiss
            // first; navigate in sheet onDismiss via pendingMoreNavigation.
            // Do NOT restore menu on goBack — back = SimpleHome only.
            restorePayPainsMenuOnReturn = false
            pendingMoreNavigation = action
            showPayPainsMenu = false
            showMoreSheet = false
        } label: {
            HStack(spacing: Spacing.m) {
                Image(systemName: systemImage)
                    .font(.title3.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(width: 28)
                Text(localizationManager.localized(titleKey))
                    .font(AladdinFamilyType.body(weight: .semibold))
                    .foregroundColor(.white)
                Spacer(minLength: 0)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.55))
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, minHeight: 56, alignment: .leading)
            .contentShape(Rectangle())
            .aladdinProductCard(cornerRadius: CornerRadius.large)
        }
        .aladdinTapFeedback(.light)
        .accessibilityIdentifier(id)
    }

    private var legacyHomeContent: some View {
        VStack(spacing: Spacing.l) {
            subtitleLabel
            VoiceSafetyNowChip {
                showVoiceNotes = true
            }
            .environmentObject(localizationManager)
            tilesGrid
            moreButton
            openFullMainButton
            preferredToggle
        }
    }

    // MARK: - Header

    private var headerBar: some View {
        ZStack {
            Text(localizationManager.localized("simple_home_title"))
                .font(AladdinFamilyType.title2())
                .foregroundColor(Color.secondaryGold)
                .lineLimit(1)
                .minimumScaleFactor(0.85)
                .frame(maxWidth: .infinity)
                .accessibilityAddTraits(.isHeader)
                .accessibilityIdentifier("simple_home_title")

            HStack {
                Button {
                    HapticFeedback.impact(.light)
                    // Q13: SimpleHome is often the launch root — goBack is a no-op. Always land on Main (full grid).
                    navigationManager.navigateToRoot(.main)
                } label: {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(width: 44, height: 44)
                        .contentShape(Circle())
                        .background(Circle().fill(Color.orange.opacity(0.2)))
                }
                .buttonStyle(.plain)
                .accessibilityLabel(localizationManager.localized("simple_home_a11y_back"))
                .accessibilityIdentifier("simple_home_back")
                Spacer()
            }
        }
        .padding(.horizontal, Spacing.l)
        .padding(.vertical, Spacing.m)
    }

    private var subtitleLabel: some View {
        Text(localizationManager.localized("simple_home_subtitle"))
            .font(.subheadline)
            .foregroundColor(.white.opacity(0.85))
            .frame(maxWidth: .infinity, alignment: .leading)
            .accessibilityIdentifier("simple_home_subtitle")
    }

    // MARK: - Tiles

    private var tilesGrid: some View {
        LazyVGrid(
            columns: [GridItem(.flexible()), GridItem(.flexible())],
            spacing: Spacing.m
        ) {
            tile(
                titleKey: "profile_security_title",
                subtitleKey: "network_protection_security_features",
                systemImage: "shield.fill",
                identifier: "simple_home_tile_protection"
            ) {
                navigationManager.navigateTo(.networkProtection)
            }
            tile(
                titleKey: "simple_home_tile_check_title",
                subtitleKey: "simple_home_tile_check_subtitle",
                systemImage: "magnifyingglass",
                identifier: "simple_home_tile_check"
            ) {
                navigationManager.navigateToAntifakeHub(tab: .text)
            }
            tile(
                titleKey: "simple_home_tile_family_title",
                subtitleKey: "simple_home_tile_family_subtitle",
                systemImage: "person.3.fill",
                identifier: "simple_home_tile_family"
            ) {
                navigationManager.navigateTo(.family)
            }
            tile(
                titleKey: "simple_home_tile_parents_title",
                subtitleKey: "simple_home_tile_parents_subtitle",
                systemImage: "person.2.fill",
                identifier: "simple_home_tile_parents"
            ) {
                FamilyScamCallFunnel.log(.mainParentsCTA, source: "simple_home")
                navigationManager.navigateTo(.family)
            }
            if AppConfig.isCompanionAvailable {
                tile(
                    titleKey: "simple_home_tile_hero_title",
                    subtitleKey: "simple_home_tile_hero_subtitle",
                    systemImage: "bubble.left.and.bubble.right.fill",
                    identifier: "simple_home_tile_hero"
                ) {
                    navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
                }
            }
            tile(
                titleKey: "simple_home_tile_say_title",
                subtitleKey: "simple_home_tile_say_subtitle",
                systemImage: "mic.fill",
                identifier: "simple_home_tile_say"
            ) {
                showVoiceNotes = true
            }
            // QA16 B3: одна «Защита» → networkProtection (расширенные блоки внутри экрана).
            // Отдельную плитку advancedProtection не показываем.
        }
    }

    private func tile(
        titleKey: String,
        subtitleKey: String,
        systemImage: String,
        identifier: String,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: {
            HapticFeedback.impact(.light)
            action()
        }) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                Image(systemName: systemImage)
                    .font(.title2.weight(.semibold))
                    .foregroundColor(.white)
                Text(localizationManager.localized(titleKey))
                    .font(AladdinFamilyType.subheadline(weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.55)
                    .allowsTightening(true)
                    .multilineTextAlignment(.leading)
                Text(localizationManager.localized(subtitleKey))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(Color.textSecondary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.55)
                    .allowsTightening(true)
                    .multilineTextAlignment(.leading)
                Spacer(minLength: 0)
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, minHeight: tileMinHeight, alignment: .topLeading)
            .aladdinProductCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier(identifier)
        .accessibilityLabel(
            localizationManager.localized(titleKey)
                + ". "
                + localizationManager.localized(subtitleKey)
        )
    }

    private var moreButton: some View {
        Button {
            HapticFeedback.impact(.light)
            showMoreSheet = true
        } label: {
            HStack {
                Image(systemName: "ellipsis.circle.fill")
                    .font(.title3)
                Text(localizationManager.localized("simple_home_more_title"))
                    .font(.subheadline.weight(.bold))
                Spacer()
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
            }
            .foregroundColor(.white)
            .padding(Spacing.m)
            .frame(maxWidth: .infinity)
            .aladdinProductCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("simple_home_more")
        .accessibilityLabel(localizationManager.localized("simple_home_a11y_more"))
    }

    private var openFullMainButton: some View {
        Button {
            HapticFeedback.impact(.light)
            // Явный переход на расширенный экран (не «назад» к Main в стеке).
            navigationManager.navigateToRoot(.main)
        } label: {
            HStack {
                AliveGlyph(id: .fullApp, size: 28) {
                    Image(systemName: "rectangle.split.2x1")
                        .font(.title3)
                }
                Text(localizationManager.localized("simple_home_open_full_main"))
                    .font(AladdinFamilyType.body(weight: .semibold))
                Spacer()
            }
            .foregroundColor(.white)
            .padding(Spacing.m)
            .frame(maxWidth: .infinity)
            .frame(minHeight: 44)
            .aladdinProductCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("simple_home_open_full_main")
    }

    private var preferredToggle: some View {
        Toggle(isOn: $simpleHomePreferred) {
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("simple_home_pref_open_title"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                Text(localizationManager.localized("simple_home_pref_open_subtitle"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.75))
            }
        }
        .tint(Color(hex: "C4B5FD"))
        .padding(Spacing.m)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("simple_home_pref_toggle")
    }

    // MARK: - More sheet

    private var moreSheet: some View {
        WellnessNavigationStack {
            List {
                moreRow(
                    titleKey: "main_protect_parents_cta",
                    systemImage: "heart.circle.fill",
                    id: "simple_home_more_protect_parents"
                ) {
                    FamilyScamCallFunnel.log(.mainParentsCTA, source: "simple_home_more")
                    navigationManager.navigateTo(.family)
                }
                moreRow(
                    titleKey: "nav_screen_settings",
                    systemImage: "gearshape.fill",
                    id: "simple_home_more_settings"
                ) {
                    navigationManager.navigateTo(.settings)
                }
                moreRow(
                    titleKey: "nav_screen_profile",
                    systemImage: "person.fill",
                    id: "simple_home_more_profile"
                ) {
                    navigationManager.navigateTo(.profile)
                }
                moreRow(
                    titleKey: "nav_screen_notifications",
                    systemImage: "bell.fill",
                    id: "simple_home_more_notifications"
                ) {
                    navigationManager.navigateTo(.notifications)
                }
                moreRow(
                    titleKey: "nav_screen_support",
                    systemImage: "questionmark.circle.fill",
                    id: "simple_home_more_support"
                ) {
                    navigationManager.navigateTo(.support)
                }
                if AppConfig.isFamilyChatAvailable {
                    moreRow(
                        titleKey: "nav_screen_family_chat",
                        systemImage: "message.fill",
                        id: "simple_home_more_family_chat"
                    ) {
                        navigationManager.navigateTo(.familyChat)
                    }
                }
                moreRow(
                    titleKey: "nav_screen_parental_control",
                    systemImage: "person.crop.circle.badge.checkmark",
                    id: "simple_home_more_parental"
                ) {
                    navigationManager.navigateTo(.parentalControl)
                }
                if FamilyFocusSessionFeature.isEnabled {
                    moreRow(
                        titleKey: "focus_session_title",
                        systemImage: "timer",
                        id: "simple_home_more_focus"
                    ) {
                        navigationManager.navigateTo(.focusSession)
                    }
                }
                if AppConfig.isAIAssistantAvailable {
                    moreRow(
                        titleKey: "nav_screen_ai_assistant",
                        systemImage: "brain.head.profile",
                        id: "simple_home_more_ai_assistant"
                    ) {
                        navigationManager.navigateTo(.aiAssistant)
                    }
                }

                if simpleHomePreferred {
                    Section {
                        moreRow(
                            titleKey: "main_tariffs",
                            systemImage: "creditcard.fill",
                            id: "simple_home_more_tariffs"
                        ) {
                            navigationManager.navigateTo(.tariffs)
                        }
                        moreRow(
                            titleKey: "nav_screen_devices",
                            systemImage: "iphone",
                            id: "simple_home_more_devices"
                        ) {
                            navigationManager.navigateTo(.devices)
                        }
                    }
                }
            }
            .navigationTitle(localizationManager.localized("simple_home_more_sheet_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_done")) {
                        pendingMoreNavigation = nil
                        showMoreSheet = false
                    }
                    .accessibilityIdentifier("simple_home_more_done")
                }
            }
        }
        .wellnessSheetDetents()
        .interactiveDismissDisabled(false)
    }

    private func moreRow(
        titleKey: String,
        systemImage: String,
        id: String,
        action: @escaping () -> Void
    ) -> some View {
        Button {
            // Same as payPainsMenuGlassRow: dismiss sheet, then navigate onDismiss.
            restorePayPainsMenuOnReturn = false
            pendingMoreNavigation = action
            showMoreSheet = false
            showPayPainsMenu = false
        } label: {
            Label(localizationManager.localized(titleKey), systemImage: systemImage)
        }
        .accessibilityIdentifier(id)
    }
}

/// «Где семья» sheet content is rebuilt by every SimpleHome render (orbit, subscription publishes).
/// `WhereIsPhoneScreen` stores a closure → never diffable → its whole body (incl. Day Journal)
/// re-ran on each parent tick. Inputs here are stable for the sheet's lifetime: the binding reads
/// live `@State` storage and the closure only touches `@State` / the shared NavigationManager.
private struct WherePhoneSheetHost: View, Equatable {
    let isPresented: Binding<Bool>
    let onLeaveToNavigate: (NavigationManager.ALADDINScreen) -> Void

    static func == (lhs: WherePhoneSheetHost, rhs: WherePhoneSheetHost) -> Bool { true }

    var body: some View {
        WhereIsPhoneScreen(isPresented: isPresented, onLeaveToNavigate: onLeaveToNavigate)
    }
}

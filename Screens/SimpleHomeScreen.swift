import SwiftUI

/// Hybrid Simple Home Shell — «Удобный режим».
/// Pay-pains F3: при `PayPainsUIFlags.usesNewPayPainsHome` — полоса семьи + 3 двери + Меню.
/// Иначе: прежняя сетка плиток. Канон: `docs/ML_HANDOFF_PAY_PAINS_2026-10-28.md` §18/§28.
struct SimpleHomeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.sizeCategory) private var sizeCategory

    @AppStorage("aladdin.simpleHomePreferred") private var simpleHomePreferred = false
    @State private var showMoreSheet = false
    @State private var showVoiceNotes = false
    @State private var showChildDoor = false
    @State private var showPayPainsMenu = false
    @State private var pendingMoreNavigation: (() -> Void)?
    /// Сначала закрыть sheet «Ребёнок», потом navigate — иначе переход под sheet и «ничего не видно».
    @State private var pendingChildNavigation: (() -> Void)?
    @State private var showSoftReview = false
    @State private var showBedtimeSettings = false
    @State private var showChildMinutes = false
    @State private var childMinutesEnabled = true
    @State private var showWherePhone = false
    @State private var showChildPauseSheet = false
    @AppStorage("parental_internet_paused") private var internetPaused = false
    @State private var pauseBusy = false
    @State private var pauseError: String?

    private let tileMinHeight: CGFloat = 120
    private var usesPayPainsHome: Bool { PayPainsUIFlags.usesNewPayPainsHome }

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
        .sheet(isPresented: $showWherePhone) {
            WhereIsPhoneScreen(isPresented: $showWherePhone)
                .environmentObject(localizationManager)
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
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("NavigateToVoiceDayRecap"))) { _ in
            showVoiceNotes = true
        }
        .onReceive(NotificationCenter.default.publisher(for: .navigateToVoiceNotes)) { _ in
            showVoiceNotes = true
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

    // MARK: - Pay-pains home (F3 + лёгкий D1)

    private var payPainsHomeContent: some View {
        VStack(spacing: Spacing.l) {
            payPainsFamilyStrip
            payPainsDoor(
                titleKey: "pay_pains_door_check_title",
                subtitleKey: "pay_pains_door_check_subtitle",
                systemImage: "magnifyingglass",
                identifier: "pay_pains_door_check",
                prominent: true
            ) {
                // Сразу в Antifake Hub — выбор звонок/текст внутри экрана, без лишнего popup.
                navigationManager.navigateToAntifakeHub(tab: .text)
            }
            payPainsDoor(
                titleKey: "pay_pains_door_child_title",
                subtitleKey: "pay_pains_door_child_subtitle",
                systemImage: "figure.and.child.holdinghands",
                identifier: "pay_pains_door_child",
                prominent: false
            ) {
                showChildDoor = true
            }
            payPainsDoor(
                titleKey: "pay_pains_door_where_title",
                subtitleKey: "pay_pains_door_where_subtitle",
                systemImage: "map.fill",
                identifier: "pay_pains_door_where",
                prominent: false,
                subtitleOverride: whereDoorSubtitle()
            ) {
                showWherePhone = true
            }
            Button {
                HapticFeedback.impact(.light)
                navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
            } label: {
                HStack {
                    Image(systemName: "person.2.wave.2.fill")
                        .font(.subheadline.weight(.semibold))
                    Text(localizationManager.localized("pay_pains_ai_friends_row"))
                        .font(.subheadline.weight(.semibold))
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption.weight(.semibold))
                        .opacity(0.7)
                }
                .foregroundColor(.white.opacity(0.92))
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("pay_pains_ai_friends")

            Button {
                HapticFeedback.impact(.light)
                showPayPainsMenu = true
            } label: {
                HStack {
                    Image(systemName: "line.3.horizontal")
                        .font(.title3)
                    Text(localizationManager.localized("pay_pains_menu_button"))
                        .font(.subheadline.weight(.bold))
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption.weight(.semibold))
                        .opacity(0.7)
                }
                .foregroundColor(.white)
                .padding(Spacing.m)
                .frame(maxWidth: .infinity)
                .stormGlassCard(cornerRadius: CornerRadius.large)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("pay_pains_menu")

            // Main = «Расширенный экран» из плана (§18 Меню).
            openFullMainButton
        }
    }

    private var payPainsFamilyStrip: some View {
        let members = FamilyLocalStore.loadPersistedMembers()
        let count = members.count
        return Button {
            HapticFeedback.impact(.light)
            AnalyticsManager.shared.trackEvent("pay_pains_family_strip_tap")
            navigationManager.navigateTo(.family)
        } label: {
            HStack(spacing: Spacing.m) {
                if count == 0 {
                    ZStack {
                        Circle()
                            .fill(Color.white.opacity(0.12))
                            .frame(width: 44, height: 44)
                        Image(systemName: "person.badge.plus")
                            .foregroundColor(.white)
                    }
                } else {
                    // D3.1: круги инициалов (не 3D) — до 4 человек
                    HStack(spacing: -8) {
                        ForEach(Array(members.prefix(4).enumerated()), id: \.offset) { _, member in
                            Text(PayPainsMemberInitials.from(name: member.name))
                                .font(.caption.weight(.bold))
                                .foregroundColor(.white)
                                .frame(width: 36, height: 36)
                                .background(Circle().fill(Color.secondaryGold.opacity(0.35)))
                                .overlay(Circle().stroke(Color.white.opacity(0.25), lineWidth: 1))
                                .accessibilityHidden(true)
                        }
                    }
                }
                VStack(alignment: .leading, spacing: 4) {
                    if count == 0 {
                        Text(localizationManager.localized("pay_pains_family_strip_empty"))
                            .font(.headline.weight(.semibold))
                            .foregroundColor(.white)
                    } else {
                        Text(payPainsFamilyStripCountLabel(count))
                            .font(.headline.weight(.semibold))
                            .foregroundColor(.white)
                    }
                }
                Spacer()
                Text(localizationManager.localized("pay_pains_family_strip_add"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(Color.secondaryGold)
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity)
            .stormGlassCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("pay_pains_family_strip")
        .accessibilityLabel(
            count == 0
                ? localizationManager.localized("pay_pains_family_strip_empty")
                : payPainsFamilyStripCountLabel(count)
        )
    }

    /// RU: 1 человек / 2 человека / 5 человек. EN: 1 person / N people.
    private func payPainsFamilyStripCountLabel(_ count: Int) -> String {
        let n = abs(count) % 100
        let n1 = n % 10
        let peopleKey: String
        if localizationManager.currentLanguage == .russian {
            if n > 10 && n < 20 {
                peopleKey = "pay_pains_family_strip_people_many"
            } else if n1 == 1 {
                peopleKey = "pay_pains_family_strip_people_one"
            } else if (2...4).contains(n1) {
                peopleKey = "pay_pains_family_strip_people_few"
            } else {
                peopleKey = "pay_pains_family_strip_people_many"
            }
        } else {
            peopleKey = count == 1
                ? "pay_pains_family_strip_people_one"
                : "pay_pains_family_strip_people_many"
        }
        return String(
            format: localizationManager.localized("pay_pains_family_strip_count_fmt"),
            count,
            localizationManager.localized(peopleKey)
        )
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
        identifier: String,
        prominent: Bool,
        subtitleOverride: String? = nil,
        action: @escaping () -> Void
    ) -> some View {
        let title = localizationManager.localized(titleKey)
        let subtitle = subtitleOverride ?? localizationManager.localized(subtitleKey)
        return Button {
            HapticFeedback.impact(reduceMotion ? .soft : .light)
            AnalyticsManager.shared.trackEvent(
                "pay_pains_door_tap",
                parameters: ["door": identifier]
            )
            action()
        } label: {
            HStack(alignment: .center, spacing: Spacing.m) {
                Image(systemName: systemImage)
                    .font(prominent ? .title.weight(.semibold) : .title2.weight(.semibold))
                    .foregroundColor(.white)
                    .frame(width: 36)
                    .accessibilityHidden(true)
                VStack(alignment: .leading, spacing: 6) {
                    // D1.5: New York (system serif) только на заголовке двери; подпись — sans.
                    Text(title)
                        .font(
                            prominent
                                ? Font.system(.title2, design: .serif).weight(.bold)
                                : Font.system(.title3, design: .serif).weight(.bold)
                        )
                        .foregroundColor(.white)
                        .minimumScaleFactor(sizeCategory.isAccessibilityCategory ? 0.85 : 1)
                    Text(subtitle)
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 0)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.65))
                    .accessibilityHidden(true)
            }
            .padding(Spacing.l)
            .frame(maxWidth: .infinity, minHeight: prominent ? 108 : 88, alignment: .leading)
            .stormGlassCard(cornerRadius: CornerRadius.large)
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

    private var payPainsChildDoorSheet: some View {
        WellnessNavigationStack {
            ZStack {
                StormMeshBackground(variant: .premium)
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        payPainsDoor(
                            titleKey: "pay_pains_child_pause_title",
                            subtitleKey: "pay_pains_child_pause_subtitle",
                            systemImage: "pause.circle.fill",
                            identifier: "pay_pains_child_pause",
                            prominent: true
                        ) {
                            showChildPauseSheet = true
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_sites_title",
                            subtitleKey: "pay_pains_child_sites_subtitle",
                            systemImage: "globe",
                            identifier: "pay_pains_child_sites",
                            prominent: false
                        ) {
                            leaveChildDoorThen { navigationManager.navigateTo(.parentalControl) }
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_limit_title",
                            subtitleKey: "pay_pains_child_limit_subtitle",
                            systemImage: "hourglass",
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
                            identifier: "pay_pains_child_bedtime",
                            prominent: false
                        ) {
                            showBedtimeSettings = true
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_reward_title",
                            subtitleKey: "pay_pains_child_reward_subtitle",
                            systemImage: "gift.fill",
                            identifier: "pay_pains_child_reward",
                            prominent: false
                        ) {
                            leaveChildDoorThen { navigationManager.navigateTo(.childRewards) }
                        }
                        payPainsDoor(
                            titleKey: "pay_pains_child_minutes_title",
                            subtitleKey: "pay_pains_child_minutes_subtitle",
                            systemImage: "clock.fill",
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
                            identifier: "pay_pains_child_screen",
                            prominent: false
                        ) {
                            leaveChildDoorThen { navigationManager.navigateTo(.childInterface) }
                        }
                    }
                    .padding(Spacing.l)
                }
            }
            .navigationTitle(localizationManager.localized("pay_pains_door_child_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
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
                StormMeshBackground(variant: .premium)
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        // Отличается от белого List: тёмный glass + serif title (иконка/золото ALADDIN).
                        Text(localizationManager.localized("pay_pains_menu_title"))
                            .font(Font.system(.title2, design: .serif).weight(.bold))
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
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_ai_friends",
                            systemImage: "person.2.wave.2.fill",
                            id: "pay_pains_menu_ai_friends"
                        ) {
                            navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
                        }
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_ai_helper",
                            systemImage: "brain.head.profile",
                            id: "pay_pains_menu_ai_helper"
                        ) {
                            navigationManager.navigateTo(.aiAssistant)
                        }
                        payPainsMenuGlassRow(
                            titleKey: "pay_pains_menu_family_chat",
                            systemImage: "message.fill",
                            id: "pay_pains_menu_family_chat"
                        ) {
                            navigationManager.navigateTo(.familyChat)
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
                        pendingMoreNavigation = nil
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
                    .font(Font.system(.body, design: .serif).weight(.semibold))
                    .foregroundColor(.white)
                Spacer(minLength: 0)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.55))
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, minHeight: 56, alignment: .leading)
            .stormGlassCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
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
        HStack {
            Button {
                navigationManager.goBackToPreviousScreen(reason: "SimpleHome.onBack")
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            .accessibilityLabel(localizationManager.localized("simple_home_a11y_back"))
            .accessibilityIdentifier("simple_home_back")

            Text(localizationManager.localized("simple_home_title"))
                .font(.headline.bold())
            Spacer()
        }
        .foregroundColor(.white)
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
            tile(
                titleKey: "simple_home_tile_hero_title",
                subtitleKey: "simple_home_tile_hero_subtitle",
                systemImage: "bubble.left.and.bubble.right.fill",
                identifier: "simple_home_tile_hero"
            ) {
                navigationManager.navigateToCompanionHome(returnTo: .simpleHome)
            }
            tile(
                titleKey: "simple_home_tile_say_title",
                subtitleKey: "simple_home_tile_say_subtitle",
                systemImage: "mic.fill",
                identifier: "simple_home_tile_say"
            ) {
                showVoiceNotes = true
            }
            tile(
                titleKey: "simple_home_tile_advanced_title",
                subtitleKey: "simple_home_tile_advanced_subtitle",
                systemImage: "slider.horizontal.3",
                identifier: "simple_home_tile_advanced"
            ) {
                navigationManager.navigateTo(.advancedProtection)
            }
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
                    .font(.subheadline.weight(.bold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.leading)
                Text(localizationManager.localized(subtitleKey))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .multilineTextAlignment(.leading)
                Spacer(minLength: 0)
            }
            .padding(Spacing.m)
            .frame(maxWidth: .infinity, minHeight: tileMinHeight, alignment: .topLeading)
            .stormGlassCard(cornerRadius: CornerRadius.large)
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
                    .opacity(0.7)
            }
            .foregroundColor(.white)
            .padding(Spacing.m)
            .frame(maxWidth: .infinity)
            .stormGlassCard(cornerRadius: CornerRadius.large)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("simple_home_more")
        .accessibilityLabel(localizationManager.localized("simple_home_a11y_more"))
    }

    private var openFullMainButton: some View {
        Button {
            HapticFeedback.impact(.light)
            navigationManager.goBackToPreviousScreen(reason: "SimpleHome.openFullMain")
        } label: {
            HStack {
                Image(systemName: "rectangle.split.2x1")
                    .font(.title3)
                Text(localizationManager.localized("simple_home_open_full_main"))
                    .font(.subheadline.weight(.semibold))
                Spacer()
            }
            .foregroundColor(.white)
            .padding(Spacing.m)
            .frame(maxWidth: .infinity)
            .stormGlassCard(cornerRadius: CornerRadius.large)
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
        .stormGlassCard(cornerRadius: CornerRadius.large)
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
                moreRow(
                    titleKey: "nav_screen_family_chat",
                    systemImage: "message.fill",
                    id: "simple_home_more_family_chat"
                ) {
                    navigationManager.navigateTo(.familyChat)
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
                moreRow(
                    titleKey: "nav_screen_ai_assistant",
                    systemImage: "brain.head.profile",
                    id: "simple_home_more_ai_assistant"
                ) {
                    navigationManager.navigateTo(.aiAssistant)
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
            pendingMoreNavigation = action
            showMoreSheet = false
            showPayPainsMenu = false
        } label: {
            Label(localizationManager.localized(titleKey), systemImage: systemImage)
        }
        .accessibilityIdentifier(id)
    }
}

import SwiftUI

/// Hybrid Simple Home Shell — «Простая версия».
/// Лаунчер: 4 крупные плитки + «Ещё…» → существующие экраны через NavigationManager.
/// Канон: `docs/PLAN_SIMPLE_HOME_SHELL_20260720.md`
struct SimpleHomeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @AppStorage("aladdin.simpleHomePreferred") private var simpleHomePreferred = false
    @State private var showMoreSheet = false
    @State private var showCheckChooser = false
    @State private var showVoiceNotes = false
    @State private var pendingMoreNavigation: (() -> Void)?

    private let tileMinHeight: CGFloat = 120

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .premium)
            VStack(spacing: 0) {
                headerBar
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: Spacing.l) {
                        subtitleLabel
                        tilesGrid
                        moreButton
                        openFullMainButton
                        preferredToggle
                    }
                    .padding(.horizontal, Spacing.l)
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xl)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showVoiceNotes) {
            VoiceNotesScreen()
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("NavigateToVoiceDayRecap"))) { _ in
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
        .confirmationDialog(
            localizationManager.localized("simple_home_check_chooser_title"),
            isPresented: $showCheckChooser,
            titleVisibility: .visible
        ) {
            Button(localizationManager.localized("simple_home_check_message")) {
                navigationManager.navigateToAntifakeHub(tab: .text)
            }
            Button(localizationManager.localized("simple_home_check_call")) {
                navigationManager.navigateToAntifakeHub(tab: .call)
            }
            Button(localizationManager.localized("wellness_done"), role: .cancel) {}
        }
        .accessibilityIdentifier("simple_home_root")
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
                titleKey: "simple_home_tile_protection_title",
                subtitleKey: "simple_home_tile_protection_subtitle",
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
                showCheckChooser = true
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
                        showMoreSheet = false
                    }
                }
            }
        }
        .wellnessSheetDetents()
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
        } label: {
            Label(localizationManager.localized(titleKey), systemImage: systemImage)
        }
        .accessibilityIdentifier(id)
    }
}

import SwiftUI

/// p1-12 — Wellness Hub: 4 столпа (child: 2).
struct WellnessHubScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var pillars: [WellnessPillar] = []
    @State private var ageBand = "parent"
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var isSelecting = false
    @State private var suggestPhq = false
    @State private var recap: WellnessSessionRecapResponse?
    @State private var idleNudge: WellnessTriggersResponse?
    @State private var reflectiveAvailable = false
    @State private var showOutcomeSheet = false
    @State private var showReferralSheet = false
    @State private var referralLevel = "L2"
    @State private var traumaBanner: WellnessTraumaCheckResponse?
    @State private var alliance: WellnessAllianceDTO?
    @State private var hubCopy: [String: WellnessHubCopyCard] = [:]
    @State private var streaks: WellnessStreaksPayload?
    @State private var weeklyMeaning: WellnessWeeklyMeaningResponse?
    @State private var familyThemes: WellnessFamilyThemesResponse?
    @State private var parentPlaybook: WellnessParentPlaybookResponse?
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""

    private var isChild: Bool { ageBand == "child" }
    private var teenUserIdForParent: String {
        if !selectedChildId.isEmpty { return selectedChildId }
        return legacySelectedChild
    }
    private var isTeenOrOlder: Bool { !isChild }

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(hex: "1E1B4B"), Color(hex: "4C1D95"), Color(hex: "312E81")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    suggestedPillarBanner
                    if idleNudge?.showIdleNudge == true,
                       let title = idleNudge?.nudgeTitle,
                       let body = idleNudge?.nudgeBody {
                        idleNudgeBanner(title: title, body: body)
                    }
                    if let recapMessage = hubRecapMessage, !recapMessage.isEmpty {
                        Text(recapMessage)
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))
                            .padding(10)
                            .background(Color.white.opacity(0.1))
                            .cornerRadius(12)
                    }
                    if recap?.outcomeDue == true, let reminder = recap?.outcomeReminder {
                        outcomeReminderBanner(reminder)
                    }
                    if recap?.pillarFatigue?.fatigued == true, let fatigue = recap?.pillarFatigue {
                        fatigueBanner(fatigue)
                    }
                    if traumaBanner?.triggered == true {
                        traumaReferralBanner()
                    }
                    if let alliance {
                        allianceChip(alliance)
                    }
                    if let streaks, streaks.checkinStreak > 0 {
                        streaksBanner(streaks)
                    }
                    if let weeklyMeaning, weeklyMeaning.show {
                        weeklyMeaningBanner(weeklyMeaning)
                    }
                    if let familyThemes, ageBand == "parent" || ageBand == "senior" {
                        familyThemesCard(familyThemes)
                    }
                    if let parentPlaybook, ageBand == "parent" || ageBand == "senior" {
                        parentPlaybookCard(parentPlaybook)
                    }
                    if isChild {
                        Text(localizationManager.localized("wellness_hub_child_hint"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.85))
                    }
                    if isLoading {
                        ProgressView().tint(.white).frame(maxWidth: .infinity)
                    } else if let errorText {
                        Text(errorText).foregroundColor(.orange)
                        Button(localizationManager.localized("wellness_retry")) {
                            Task { await loadPillars() }
                        }
                    } else {
                        pillarGrid
                    }
                    checkinButton
                    timelineButton
                    if WellnessSessionStore.activePillar != nil {
                        exerciseButton
                    }
                    if suggestPhq && isTeenOrOlder {
                        phqButton
                    }
                    if isTeenOrOlder {
                        dreamButton
                    }
                    if reflectiveAvailable && isTeenOrOlder {
                        reflectiveButton
                    }
                    if ageBand == "parent" || ageBand == "senior" {
                        togetherButton
                    }
                    companionButton
                    trustButton
                }
                .padding()
            }
        }
        .navigationBarHidden(true)
        .task {
            await loadPillars()
            await syncConsent()
            await loadTriggers()
            await loadRecap()
            await probeReflective()
            await loadAlliance()
            await loadHubCopy()
            await loadStreaks()
            await loadWeeklyMeaning()
            await loadFamilyThemesIfParent()
            await prefetchWellnessLoop()
        }
        .sheet(isPresented: $showReferralSheet) {
            WellnessReferralSheet(level: referralLevel)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showOutcomeSheet) {
            if let pillar = recap?.outcomeReminder?.pillar ?? recap?.suggestedPillar {
                WellnessOutcomeSheet(pillar: pillar) {
                    showOutcomeSheet = false
                    Task { await loadRecap() }
                }
                .environmentObject(localizationManager)
            }
        }
    }

    private var hubRecapMessage: String? {
        if let cont = recap?.continuityMessage, !cont.isEmpty { return cont }
        return recap?.message
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_hub_title", ageBand: ageBand))
                    .font(.headline.bold())
                Text(WellnessAgeL10n.text(localizationManager, key: "wellness_hub_subtitle", ageBand: ageBand))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
            }
            Spacer()
        }
        .foregroundColor(.white)
        .accessibilityIdentifier("wellness_hub_back")
    }

    @ViewBuilder
    private var suggestedPillarBanner: some View {
        if let pillarId = recap?.suggestedPillar,
           let pillar = WellnessPillar(rawValue: pillarId) {
            HStack {
                Text(
                    String(
                        format: localizationManager.localized("wellness_pillar_suggested_banner"),
                        localizationManager.localized(pillarTitleKey(pillar))
                    )
                )
                .font(.caption.bold())
                Spacer()
                Button {
                    Task { await selectPillar(pillar) }
                } label: {
                    Image(systemName: "arrow.right.circle.fill")
                }
            }
            .padding(12)
            .background(Color.cyan.opacity(0.2))
            .cornerRadius(12)
        }
    }

    private var pillarGrid: some View {
        let columns = [
            GridItem(.flexible(), spacing: 12),
            GridItem(.flexible(), spacing: 12),
        ]
        return LazyVGrid(columns: columns, spacing: 12) {
            ForEach(pillars) { pillar in
                pillarCard(pillar)
            }
        }
    }

    private func pillarTitleKey(_ pillar: WellnessPillar) -> String {
        hubCopy[pillar.rawValue]?.titleKey ?? pillar.titleKey
    }

    private func pillarSubtitleKey(_ pillar: WellnessPillar) -> String {
        hubCopy[pillar.rawValue]?.subtitleKey ?? pillar.subtitleKey
    }

    private func weeklyMeaningBanner(_ wm: WellnessWeeklyMeaningResponse) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("wellness_weekly_meaning_title")).font(.subheadline.bold())
            Text(localizationManager.localized("wellness_weekly_meaning_body")).font(.caption)
            Text(wm.prompt)
                .font(.caption)
                .italic()
                .foregroundColor(.white.opacity(0.85))
            HStack {
                Button {
                    Task {
                        try? await WellnessAPIService.shared.dismissWeeklyMeaning()
                        weeklyMeaning = nil
                        if let pillar = WellnessPillar(rawValue: wm.suggestedPillar) {
                            await selectPillar(pillar)
                        } else if reflectiveAvailable {
                            navigationManager.navigateTo(.wellnessReflective)
                        }
                    }
                } label: {
                    Text(localizationManager.localized("wellness_weekly_meaning_cta"))
                        .font(.caption.bold())
                }
                .buttonStyle(.borderedProminent)
                .tint(.purple)
                Spacer()
                Button {
                    Task {
                        try? await WellnessAPIService.shared.dismissWeeklyMeaning()
                        weeklyMeaning = nil
                    }
                } label: {
                    Text(localizationManager.localized("wellness_nudge_dismiss"))
                        .font(.caption)
                }
            }
        }
        .padding(12)
        .background(Color.purple.opacity(0.22))
        .cornerRadius(12)
        .accessibilityIdentifier("wellness_weekly_meaning_banner")
    }

    private func familyThemesCard(_ payload: WellnessFamilyThemesResponse) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("wellness_family_dashboard_title"))
                .font(.subheadline.bold())
            if !payload.shared {
                Text(localizationManager.localized("wellness_family_themes_opt_out"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
            } else {
                if let agg = payload.aggregate {
                    if let msg = agg.message {
                        Text(msg).font(.caption)
                    }
                    if let trend = agg.moodTrendLabel {
                        Text(trend).font(.caption2).foregroundColor(.orange)
                    }
                }
                Text(localizationManager.localized("wellness_family_no_transcript"))
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.7))
                if payload.themes.isEmpty {
                    Text(localizationManager.localized("wellness_family_themes_empty"))
                        .font(.caption)
                } else {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(payload.themes) { theme in
                                Text(familyThemeLabel(theme))
                                    .font(.caption2.bold())
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 5)
                                    .background(Color.mint.opacity(0.25))
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }
            }
        }
        .padding(12)
        .background(Color.white.opacity(0.1))
        .cornerRadius(12)
        .accessibilityIdentifier("wellness_family_themes_card")
    }

    private func parentPlaybookCard(_ payload: WellnessParentPlaybookResponse) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized(payload.titleKey))
                .font(.subheadline.bold())
            Text(localizationManager.localized(payload.subtitleKey))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
            ForEach(payload.phrases) { phrase in
                Text("• \(phrase.text)")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.9))
            }
        }
        .padding(12)
        .background(Color.indigo.opacity(0.18))
        .cornerRadius(12)
        .accessibilityIdentifier("wellness_parent_playbook_card")
    }

    private func familyThemeLabel(_ theme: WellnessFamilyThemeItem) -> String {
        if let key = theme.labelKey, !key.isEmpty {
            let text = localizationManager.localized(key)
            if text != key { return text }
        }
        return theme.label
    }

    private func streaksBanner(_ s: WellnessStreaksPayload) -> some View {
        HStack {
            Image(systemName: "flame.fill")
                .foregroundStyle(.orange)
            Text(s.message)
                .font(.caption)
            if let earned = s.badges.first(where: { $0.earned }) {
                Text(localizationManager.localized(earned.labelKey))
                    .font(.caption2.bold())
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.25))
                    .clipShape(Capsule())
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.1))
        .cornerRadius(12)
    }

    private var togetherButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessTogether)
        } label: {
            Label(
                localizationManager.localized("wellness_together_title"),
                systemImage: "figure.2.arms.open"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.cyan)
    }

    private func pillarCard(_ pillar: WellnessPillar) -> some View {
        Button {
            Task { await selectPillar(pillar) }
        } label: {
            VStack(alignment: .leading, spacing: 8) {
                Text(WellnessAgeL10n.text(localizationManager, key: pillarTitleKey(pillar), ageBand: ageBand))
                    .font(.subheadline.bold())
                    .multilineTextAlignment(.leading)
                Text(WellnessAgeL10n.text(localizationManager, key: pillarSubtitleKey(pillar), ageBand: ageBand))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
                    .multilineTextAlignment(.leading)
                if WellnessSessionStore.activePillar == pillar.rawValue {
                    Text(localizationManager.localized("wellness_pillar_active"))
                        .font(.caption2.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.white.opacity(0.2))
                        .clipShape(Capsule())
                }
            }
            .frame(maxWidth: .infinity, minHeight: 110, alignment: .topLeading)
            .padding(14)
            .background(Color.white.opacity(0.12))
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.white.opacity(0.25), lineWidth: 1)
            )
            .cornerRadius(16)
        }
        .buttonStyle(.plain)
        .disabled(isSelecting)
        .accessibilityIdentifier("wellness_pillar_\(pillar.rawValue)")
    }

    private var phqButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessAssessmentsHub)
        } label: {
            Label(
                localizationManager.localized("wellness_assessments_hub_title"),
                systemImage: "list.clipboard"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
        }
        .buttonStyle(.bordered)
        .tint(.orange)
    }

    private var trustButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessTrust)
        } label: {
            Label(
                localizationManager.localized("wellness_trust_title"),
                systemImage: "lock.shield"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.white.opacity(0.9))
    }

    private var timelineButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessTimeline)
        } label: {
            Label(
                localizationManager.localized("wellness_timeline_title"),
                systemImage: "calendar"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.white.opacity(0.85))
    }

    private var exerciseButton: some View {
        Button {
            WellnessSessionStore.setExercisePillar(WellnessSessionStore.activePillar)
            navigationManager.navigateTo(.wellnessExercise)
        } label: {
            Label(
                localizationManager.localized("wellness_exercise_title"),
                systemImage: "figure.mind.and.body"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.mint)
    }

    private var reflectiveButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessReflective)
        } label: {
            Label(
                localizationManager.localized("wellness_hub_reflective"),
                systemImage: "sparkles"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.purple.opacity(0.9))
    }

    private func outcomeReminderBanner(_ reminder: WellnessOutcomeReminderDTO) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            if let title = reminder.title {
                Text(title).font(.subheadline.bold())
            }
            if let body = reminder.body {
                Text(body).font(.caption)
            }
            HStack {
                Button {
                    showOutcomeSheet = true
                } label: {
                    Text(localizationManager.localized("wellness_outcome_recap_cta"))
                        .font(.caption.bold())
                }
                .buttonStyle(.borderedProminent)
                .tint(.mint)
                Spacer()
                Button {
                    Task {
                        try? await WellnessAPIService.shared.dismissOutcomePrompt()
                        await loadRecap()
                    }
                } label: {
                    Text(localizationManager.localized("wellness_nudge_dismiss"))
                        .font(.caption)
                }
            }
        }
        .padding(12)
        .background(Color.mint.opacity(0.2))
        .cornerRadius(12)
    }

    private func fatigueBanner(_ fatigue: WellnessPillarFatigueDTO) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            if let message = fatigue.message {
                Text(message).font(.subheadline)
            }
            if let suggested = fatigue.suggestedPillar {
                Button {
                    Task { await switchToFatiguePillar(suggested) }
                } label: {
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_fatigue_switch", ageBand: ageBand))
                        .font(.caption.bold())
                }
                .buttonStyle(.borderedProminent)
                .tint(.orange)
            }
        }
        .padding(12)
        .background(Color.orange.opacity(0.15))
        .cornerRadius(12)
    }

    private func switchToFatiguePillar(_ pillar: String) async {
        _ = try? await WellnessAPIService.shared.setSessionPillar(pillar)
        WellnessSessionStore.setActivePillar(pillar)
        await loadRecap()
    }

    private var dreamButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessDreamJournal)
        } label: {
            Label(
                localizationManager.localized("wellness_dream_title"),
                systemImage: "moon.stars"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.indigo.opacity(0.9))
    }

    private var companionButton: some View {
        Button {
            Task { await openCompanionAfterLoop() }
        } label: {
            Label(
                WellnessAgeL10n.text(localizationManager, key: "wellness_open_companion", ageBand: ageBand),
                systemImage: "bubble.left.and.bubble.right"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
        .tint(.cyan)
    }

    private var checkinButton: some View {
        Button {
            navigationManager.navigateTo(.wellnessCheckin)
        } label: {
            Label(
                localizationManager.localized("nav_screen_wellness_checkin"),
                systemImage: "face.smiling"
            )
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
        }
        .buttonStyle(.bordered)
        .tint(.white)
        .padding(.top, 8)
    }

    private func traumaReferralBanner() -> some View {
        VStack(alignment: .leading, spacing: 8) {
            if let message = traumaBanner?.message {
                Text(message).font(.subheadline)
            }
            if let note = traumaBanner?.specialistNote {
                Text(note).font(.caption).foregroundStyle(.white.opacity(0.85))
            }
            Button {
                showReferralSheet = true
            } label: {
                Text(localizationManager.localized("wellness_helpline_open"))
                    .font(.caption.bold())
            }
            .buttonStyle(.borderedProminent)
            .tint(.red.opacity(0.85))
        }
        .padding(12)
        .background(Color.red.opacity(0.15))
        .cornerRadius(12)
    }

    private func allianceChip(_ a: WellnessAllianceDTO) -> some View {
        HStack(spacing: 8) {
            Image(systemName: allianceIcon(a.heroEmotion))
            Text(
                String(
                    format: localizationManager.localized("wellness_alliance_score"),
                    a.allianceScore
                )
            )
            .font(.caption)
        }
        .foregroundColor(.white.opacity(0.9))
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(Color.white.opacity(0.12))
        .cornerRadius(20)
    }

    private func allianceIcon(_ emotion: String) -> String {
        switch emotion {
        case "celebrate": return "star.fill"
        case "concerned": return "heart.slash"
        case "calm": return "leaf"
        default: return "heart.fill"
        }
    }

    private func loadPillars() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let resp = try await WellnessAPIService.shared.fetchPillars()
            WellnessOfflineStore.savePillars(resp)
            ageBand = resp.ageBand
            WellnessSessionStore.setCachedAgeBand(resp.ageBand)
            let allowed = Set(resp.pillars)
            pillars = WellnessPillar.allowed(for: resp.ageBand).filter { allowed.contains($0.rawValue) }
        } catch {
            if let cached = WellnessOfflineStore.loadPillars() {
                ageBand = cached.ageBand
                let allowed = Set(cached.pillars)
                pillars = WellnessPillar.allowed(for: cached.ageBand).filter { allowed.contains($0.rawValue) }
                errorText = nil
            } else {
                let band = CompanionUserContext.companionAgeBand
                ageBand = band
                pillars = WellnessPillar.allowed(for: band)
                errorText = localizationManager.localized("wellness_error_offline_pillars")
            }
        }
    }

    private func syncConsent() async {
        if let c = try? await WellnessAPIService.shared.fetchConsent(), c.hasAccess == true {
            WellnessSessionStore.acceptConsent()
        }
    }

    private func loadTriggers() async {
        if let t = try? await WellnessAPIService.shared.fetchTriggers() {
            suggestPhq = t.suggestPhqLite
            idleNudge = t
        }
    }

    private func idleNudgeBanner(title: String, body: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.subheadline.bold())
            Text(body).font(.caption)
            HStack {
                Button {
                    navigationManager.navigateTo(.wellnessCheckin)
                } label: {
                    Text(localizationManager.localized("wellness_nudge_idle_cta"))
                        .font(.caption.bold())
                }
                .buttonStyle(.borderedProminent)
                .tint(.mint)
                Spacer()
                Button {
                    Task {
                        try? await WellnessAPIService.shared.dismissIdleNudge()
                        idleNudge = nil
                    }
                } label: {
                    Text(localizationManager.localized("wellness_nudge_dismiss"))
                        .font(.caption)
                }
            }
        }
        .padding(12)
        .background(Color.orange.opacity(0.2))
        .cornerRadius(12)
    }

    private func loadRecap() async {
        if let r = try? await WellnessAPIService.shared.fetchSessionRecap() {
            recap = r
            WellnessOfflineStore.saveRecap(r)
        } else {
            recap = WellnessOfflineStore.loadRecap()
        }
    }

    private func loadAlliance() async {
        if let a = try? await WellnessAPIService.shared.fetchAlliance() {
            alliance = a
            WellnessOfflineStore.saveAlliance(score: a.allianceScore, heroEmotion: a.heroEmotion)
        } else if let cached = WellnessOfflineStore.loadAlliance() {
            alliance = WellnessAllianceDTO(
                allianceScore: cached.score,
                heroEmotion: cached.heroEmotion,
                trustBand: nil
            )
        }
        await loadTraumaBannerIfNeeded()
    }

    private func loadHubCopy() async {
        if let copy = try? await WellnessAPIService.shared.fetchHubCopy() {
            hubCopy = Dictionary(uniqueKeysWithValues: copy.pillars.map { ($0.pillar, $0) })
        }
    }

    private func loadStreaks() async {
        streaks = try? await WellnessAPIService.shared.fetchStreaks()
    }

    private func loadWeeklyMeaning() async {
        guard isTeenOrOlder else { return }
        weeklyMeaning = try? await WellnessAPIService.shared.fetchWeeklyMeaning()
    }

    private func loadFamilyThemesIfParent() async {
        guard ageBand == "parent" || ageBand == "senior" else { return }
        parentPlaybook = try? await WellnessAPIService.shared.fetchParentPlaybook(
            topic: "support",
            useLlm: true
        )
        let teenId = teenUserIdForParent.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !teenId.isEmpty else { return }
        familyThemes = try? await WellnessAPIService.shared.fetchFamilyThemes(teenUserId: teenId)
    }

    private func loadTraumaBannerIfNeeded() async {
        if let settings = try? await WellnessAPIService.shared.fetchSettings(),
           settings.settings.escalationLevel == "L2" {
            traumaBanner = WellnessTraumaCheckResponse(
                triggered: true,
                level: "L2",
                reason: "trauma_keywords",
                message: localizationManager.localized("wellness_trauma_hub_hint"),
                blockJungDeep: true,
                redirectPillar: "humanistic",
                showReferral: true,
                specialistNote: localizationManager.localized("wellness_trauma_specialist_note"),
                referral: nil
            )
        }
    }

    private func probeReflective() async {
        if let r = try? await WellnessAPIService.shared.fetchReflectiveModes(), !r.modes.isEmpty {
            reflectiveAvailable = true
        }
    }

    private func selectPillar(_ pillar: WellnessPillar) async {
        isSelecting = true
        defer { isSelecting = false }
        switch await WellnessLoopCoordinator.runAndApply(
            message: "",
            requestedPillar: pillar.rawValue
        ) {
        case .crisisL3:
            referralLevel = "L3"
            showReferralSheet = true
            return
        case .guardBlocked(let reason):
            errorText = localizationManager.localized("wellness_error_pillar")
            #if DEBUG
            errorText = "\(errorText) (\(reason))"
            #endif
            return
        case .proceed(let suggestPhqFlag):
            if suggestPhqFlag { self.suggestPhq = true }
        }
        do {
            _ = try await WellnessAPIService.shared.setSessionPillar(pillar.rawValue)
            WellnessSessionStore.setActivePillar(pillar.rawValue)
            WellnessSessionStore.setExercisePillar(pillar.rawValue)
            navigationManager.navigateTo(.wellnessExercise)
        } catch {
            errorText = localizationManager.localized("wellness_error_pillar")
        }
    }

    private func prefetchWellnessLoop() async {
        switch await WellnessLoopCoordinator.runAndApply(
            message: "",
            requestedPillar: WellnessSessionStore.activePillar
        ) {
        case .crisisL3:
            referralLevel = "L3"
            showReferralSheet = true
        case .guardBlocked:
            break
        case .proceed(let suggestPhq):
            if suggestPhq { self.suggestPhq = true }
            await loadRecap()
        }
    }

    private func openCompanionAfterLoop() async {
        isSelecting = true
        defer { isSelecting = false }
        switch await WellnessLoopCoordinator.runAndApply(
            message: "",
            requestedPillar: WellnessSessionStore.activePillar
        ) {
        case .crisisL3:
            referralLevel = "L3"
            showReferralSheet = true
            return
        case .guardBlocked:
            errorText = localizationManager.localized("wellness_error_pillar")
            return
        case .proceed(let suggestPhqFlag):
            if suggestPhqFlag { self.suggestPhq = true }
        }
        if WellnessSessionStore.activePillar == nil {
            errorText = localizationManager.localized("wellness_hub_pick_pillar_first")
            return
        }
        navigationManager.navigateToCompanionHome(returnTo: .wellnessHub)
    }
}

/// Единая точка входа в wellness flow.
enum WellnessNavigation {
    @MainActor
    static func open(from navigationManager: NavigationManager) {
        if WellnessSessionStore.hasAcceptedConsent {
            navigationManager.navigateTo(.wellnessHub)
        } else {
            navigationManager.navigateTo(.wellnessConsent)
        }
    }
}

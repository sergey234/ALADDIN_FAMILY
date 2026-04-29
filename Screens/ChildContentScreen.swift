import SwiftUI

/// W4-4: загрузка, пусто, ошибка + rich progress (полоса, %, last opened)
private enum ChildContentLoadPhase: Equatable {
    case loading
    case ready
    case empty
    case error
}

private enum ChildDailyJourneyStep: Int {
    case discover = 0
    case practice = 1
    case reflect = 2
}

/// 👶 Child Content Screen
/// Универсальный экран контента для детей с адаптацией по возрасту
struct ChildContentScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    let category: String
    let ageGroup: ChildInterfaceScreen.AgeGroup
    @State private var loadPhase: ChildContentLoadPhase = .loading
    @State private var contentItems: [ContentItem] = []
    @State private var progressById: [String: ContentProgress] = [:]
    @State private var mascotEmotion: CharacterEmotion = .neutral
    @State private var mascotActivity: CharacterActivityState = .idle
    @State private var mascotResetToken: UUID = UUID()
    @State private var selectedExperience: ContentExperiencePresentation?
    @State private var dailyJourneyStep: ChildDailyJourneyStep = .discover
    @State private var consecutiveOpenErrors: Int = 0
    @State private var adaptiveHintVisible: Bool = false
    @State private var simplifiedModeEnabled: Bool = false
    @State private var dailyRewardPoints: Int = 0
    @State private var lastSkillRewardPoints: Int = 0
    @State private var surpriseVisible: Bool = false
    @State private var surpriseTitleKey: String = "child_surprise_title_default"
    @State private var sessionsUntilSurprise: Int = 0
    @State private var creativeOutputDone: Bool = false
    @State private var creativeReminderVisible: Bool = false
    @State private var schoolPacingKey: String = "child_daily_journey_v2_pacing_steady"
    @State private var schoolCorrectiveFeedbackVisible: Bool = false
    @State private var schoolCorrectiveFeedbackKey: String = "child_daily_journey_v2_feedback_keep_going"
    @State private var frustrationLevel: Int = 0
    @State private var frustrationPlanVisible: Bool = false
    @State private var recoveryBonusAttempts: Int = 0
    @State private var teenAutonomyFocusKey: String = "child_daily_journey_v3_focus_explore"
    @State private var teenReflectionPromptVisible: Bool = false
    @State private var teenReflectionCompleted: Bool = false
    @State private var teenArtifactCount: Int = 0
    @State private var teenArtifactTarget: Int = 2
    @State private var teenLastArtifactKey: String = "child_creative_output_v2_none"
    @State private var extensionRequestStatus: String?
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (адаптивный по возрасту)
            backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Заголовок
                contentHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 20) {
                        // Приветствие
                        greetingSection

                        if shouldShowTimeLimitBanner {
                            timeLimitBannerCard
                        }
                        
                        // Специфичный контент для каждой категории
                        categoryContent
                        
                        // Дополнительная информация
                        additionalInfoSection
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                }
            }
        }
        .sheet(item: $selectedExperience) { presentation in
            ChildContentExperienceScreen(
                item: presentation.item,
                route: presentation.route
            ) {
                await markContentCompleted(presentation.item)
            }
            .environmentObject(navigationManager)
            .environmentObject(localizationManager)
        }
        .accessibilityIdentifier("aladdin_root_child_content")
    }
    
    // MARK: - Background Gradient
    
    private var backgroundGradient: some View {
        LinearGradient(
            colors: gradientColors,
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
    
    private var gradientColors: [Color] {
        switch ageGroup {
        case .kids:
            return [Color.pink.opacity(0.8), Color.purple.opacity(0.6), Color.blue.opacity(0.4)]
        case .school:
            return [Color.green.opacity(0.8), Color.blue.opacity(0.6), Color.cyan.opacity(0.4)]
        case .teen:
            return [Color.blue.opacity(0.8), Color.purple.opacity(0.6), Color.indigo.opacity(0.4)]
        case .youngAdult:
            return [Color.indigo.opacity(0.8), Color.purple.opacity(0.6), Color.blue.opacity(0.4)]
        }
    }
    
    private var localizedCategoryTitle: String {
        localizationManager.localized(category)
    }

    // MARK: - Data Loading

    private func loadDataDrivenContent() async {
        await MainActor.run { loadPhase = .loading }
        let firstPass = await loadContentPass(forceRefresh: false)
        if firstPass == nil {
            await MainActor.run { loadPhase = .error }
            return
        }

        var finalItems = firstPass?.items ?? []
        var finalProgress = firstPass?.progressById ?? [:]

        // UX fix: do not flash empty state immediately.
        // If first pass returns empty, keep loading and run one forced refresh pass.
        if finalItems.isEmpty {
            try? await Task.sleep(nanoseconds: 900_000_000)
            if let secondPass = await loadContentPass(forceRefresh: true) {
                finalItems = secondPass.items
                finalProgress = secondPass.progressById
            }
        }

        await MainActor.run {
            contentItems = finalItems
            progressById = finalProgress
            loadPhase = finalItems.isEmpty ? .empty : .ready
            refreshDailyJourneyStep()
            loadDailyRewardPoints()
            loadSurpriseState()
            loadCreativeOutputState()
            loadTeenJourneyState()
            loadTeenCreativeOutputState()
        }
    }

    private func loadContentPass(forceRefresh: Bool) async -> (items: [ContentItem], progressById: [String: ContentProgress])? {
        do {
            try await ContentManager.shared.bootstrapLocalContentIfNeeded()
        } catch {
            return nil
        }

        await ContentManager.shared.runUnifiedLifecycle(forceRefresh: forceRefresh)
        let items = await ContentManager.shared.loadPersonalizedContent(
            for: category,
            ageBand: ageGroup.contentAgeBand
        )
        var map: [String: ContentProgress] = [:]
        for item in items {
            if let progress = await ContentManager.shared.loadProgress(contentId: item.id) {
                map[item.id] = progress
            }
        }
        return (items: items, progressById: map)
    }

    // MARK: - Header

    private var contentHeader: some View {
        HStack(spacing: 16) {
            // Кнопка назад
            Button(action: {
                // ✅ ПРОСТОЙ ПОДХОД: только dismiss() для NavigationView
                dismiss()
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.white.opacity(0.2))
                    )
            }
            .accessibilityLabel(localizationManager.localized("child_interface_back"))
            
            // Заголовок
            VStack(alignment: .leading, spacing: 4) {
                Text(ageGroup.title(localizationManager: localizationManager))
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.white.opacity(0.8))
                
                Text(localizedCategoryTitle)
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(.white)
            }
            
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.top, 16)
        .padding(.bottom, 12)
        .task {
            await loadDataDrivenContent()
        }
    }

    // MARK: - Greeting Section
    
    private var greetingSection: some View {
        HStack(alignment: .center, spacing: 16) {
            VStack(spacing: 12) {
                Text(greetingEmoji)
                    .font(.system(size: 60))
                
                Text(greetingText)
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)

            CharacterAvatarView(emotion: mascotEmotion, activity: mascotActivity)
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("child_mascot_accessibility_label"))
                .accessibilityHint(localizationManager.localized("child_mascot_accessibility_hint"))
                .onTapGesture {
                    mascotResetToken = UUID()
                    mascotEmotion = .happy
                    mascotActivity = .active
                    SoundEffectPlayer.shared.play(.reward, priority: .low)
                    scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.85)
                }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 24)
    }

    private func scheduleMascotReset(to emotion: CharacterEmotion, activity: CharacterActivityState, delay: TimeInterval) {
        let token = mascotResetToken
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            guard token == mascotResetToken else { return }
            mascotEmotion = emotion
            mascotActivity = activity
        }
    }
    
    private var greetingEmoji: String {
        // Используем только локализованные значения
        if category == ChildCategoryKey.toys {
            return "🧸"
        }
        if category == ChildCategoryKey.drawing {
            return "🎨"
        }
        if category == ChildCategoryKey.songs {
            return "🎵"
        }
        if category == ChildCategoryKey.stories {
            return "📖"
        }
        if category == ChildCategoryKey.games {
            return "🎮"
        }
        if category == ChildCategoryKey.study {
            return "📚"
        }
        if category == ChildCategoryKey.creativity {
            return "🎨"
        }
        if category == ChildCategoryKey.cartoons {
            return "📺"
        }
        // Fallback
        return "🌟"
    }
    
    private var greetingText: String {
        // Используем только локализованные значения
        if category == "child_interface_category_games" {
            return localizationManager.localized("child_game_greeting")
        }
        if category == "child_interface_category_study" {
            return localizationManager.localized("child_study_welcome")
        }
        if category == "child_interface_category_creativity" {
            return localizationManager.localized("child_creativity_welcome")
        }
        if category == "child_interface_category_cartoons" {
            return localizationManager.localized("child_cartoons_welcome")
        }
        if category == "child_interface_category_toys" {
            return localizationManager.localized("child_game_welcome")
        }
        if category == "child_interface_category_drawing" {
            return localizationManager.localized("child_creativity_welcome")
        }
        if category == "child_interface_category_songs" {
            return localizationManager.localized("child_game_welcome")
        }
        if category == "child_interface_category_stories" {
            return localizationManager.localized("child_game_welcome")
        }
        // Fallback только на локализованное значение
        return localizationManager.localized("child_game_welcome")
    }
    
    // MARK: - Category Content (W4-4)
    
    private var categoryContent: some View {
        VStack(spacing: 16) {
            switch loadPhase {
            case .loading:
                childContentLoadingView
            case .error:
                childContentErrorView
            case .empty:
                childContentEmptyView
            case .ready:
                VStack(spacing: 14) {
                    childDailyJourneyCard
                    if ageGroup == .school {
                        schoolJourneyPacingCard
                    }
                    if ageGroup == .teen || ageGroup == .youngAdult {
                        teenJourneyAutonomyCard
                    }
                    rewardProgressCard
                    if ageGroup == .kids {
                        creativeOutputCard
                    }
                    if ageGroup == .teen || ageGroup == .youngAdult {
                        teenCreativeOutputCard
                    }
                    if surpriseVisible {
                        surpriseEventCard
                    }
                    if adaptiveHintVisible {
                        adaptiveSupportCard
                    }
                    if frustrationPlanVisible {
                        frustrationRecoveryCard
                    }
                    if !contentItems.isEmpty {
                        childContentOverallProgressCard
                    }
                    dataDrivenContent
                }
            }
        }
        .id(contentIdentity)
        .appContentTransition(reduceMotion ? .fade : .scale, value: contentIdentity)
    }

    private var childContentLoadingView: some View {
        VStack(spacing: 12) {
            ProgressView()
                .tint(.white)
            Text(localizationManager.localized("child_content_loading"))
                .font(.system(size: 15, weight: .medium))
                .foregroundColor(.white.opacity(0.9))
        }
        .frame(maxWidth: .infinity)
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.12))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_content_loading")
    }

    private var childContentErrorView: some View {
        VStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 40))
                .foregroundColor(.orange)
            Text(localizationManager.localized("child_content_error_message"))
                .font(.system(size: 16, weight: .semibold))
                .multilineTextAlignment(.center)
                .foregroundColor(.white)
            Button {
                Task { await loadDataDrivenContent() }
            } label: {
                Text(localizationManager.localized("child_content_error_retry"))
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(RoundedRectangle(cornerRadius: 12).fill(Color.blue.opacity(0.5)))
            }
            .accessibilityLabel(localizationManager.localized("child_content_error_retry"))
            .accessibilityHint(localizationManager.localized("child_content_retry_accessibility_hint"))
            .accessibilityIdentifier("child_content_error_retry")
        }
        .frame(maxWidth: .infinity)
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.12))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_content_error")
    }

    private var childContentEmptyView: some View {
        VStack(spacing: 12) {
            Image(systemName: "sparkles")
                .font(.system(size: 44))
                .foregroundColor(.white.opacity(0.85))
            Text(localizationManager.localized("child_content_empty_title"))
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_content_empty_subtitle"))
                .font(.system(size: 15))
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.85))
            Button {
                Task { await loadDataDrivenContent() }
            } label: {
                Text(localizationManager.localized("child_content_empty_retry"))
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.2)))
            }
            .accessibilityLabel(localizationManager.localized("child_content_empty_retry"))
            .accessibilityHint(localizationManager.localized("child_content_retry_accessibility_hint"))
            .accessibilityIdentifier("child_content_empty_retry")
        }
        .frame(maxWidth: .infinity)
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_content_empty_state")
    }

    private var averageCategoryProgress: Double {
        guard !contentItems.isEmpty else { return 0 }
        let total = contentItems.reduce(0.0) { acc, item in
            acc + (progressById[item.id]?.completionPercent ?? 0)
        }
        return total / Double(contentItems.count)
    }

    private var childContentOverallProgressCard: some View {
        let value = min(100, max(0, averageCategoryProgress))
        return VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(localizationManager.localized("child_content_overall_progress"))
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(.white)
                Spacer()
                Text(String(format: "%.0f%%", value))
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(.white)
            }
            ChildContentProgressBar(
                value: value,
                track: Color.white.opacity(0.22),
                fill: Color.green.opacity(0.9)
            )
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.12))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("child_content_overall_progress"))
        .accessibilityValue(String(format: "%.0f%%", value))
        .accessibilityIdentifier("child_content_overall_progress")
    }

    private var childDailyJourneyCard: some View {
        let current = dailyJourneyStep.rawValue
        return VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_daily_journey_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_daily_journey_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.85))
            HStack(spacing: 8) {
                journeyBadge(for: .discover, index: 0, current: current)
                journeyBadge(for: .practice, index: 1, current: current)
                journeyBadge(for: .reflect, index: 2, current: current)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.12))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("child_daily_journey_title"))
        .accessibilityValue(localizationManager.localized(journeyKey(for: dailyJourneyStep)))
        .accessibilityIdentifier("child_daily_journey")
    }

    private var schoolJourneyPacingCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_daily_journey_v2_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized(schoolPacingKey))
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.9))
            if schoolCorrectiveFeedbackVisible {
                Text(localizationManager.localized(schoolCorrectiveFeedbackKey))
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.85))
                Button {
                    simplifiedModeEnabled = true
                    schoolCorrectiveFeedbackVisible = false
                    SoundEffectPlayer.shared.play(.success, priority: .medium)
                } label: {
                    Text(localizationManager.localized("child_daily_journey_v2_corrective_action"))
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.cyan.opacity(0.45))
                        )
                }
                .accessibilityLabel(localizationManager.localized("child_daily_journey_v2_corrective_action"))
                .accessibilityIdentifier("child_daily_journey_v2_corrective_action")
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.blue.opacity(0.22))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_daily_journey_v2_card")
    }

    private var teenJourneyAutonomyCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_daily_journey_v3_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized(teenAutonomyFocusKey))
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.9))
            if teenReflectionPromptVisible {
                Text(localizationManager.localized("child_daily_journey_v3_reflection_prompt"))
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.85))
                Button {
                    completeTeenReflection()
                } label: {
                    Text(localizationManager.localized(teenReflectionCompleted ? "child_daily_journey_v3_reflection_done" : "child_daily_journey_v3_reflection_action"))
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill((teenReflectionCompleted ? Color.green : Color.indigo).opacity(0.45))
                        )
                }
                .disabled(teenReflectionCompleted)
                .accessibilityLabel(localizationManager.localized("child_daily_journey_v3_reflection_action"))
                .accessibilityIdentifier("child_daily_journey_v3_reflection_action")
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.indigo.opacity(0.24))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_daily_journey_v3_card")
    }

    private var rewardProgressCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_reward_progress_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text("\(localizationManager.localized("child_reward_progress_total_prefix")) \(dailyRewardPoints)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.9))
            if lastSkillRewardPoints > 0 {
                Text("\(localizationManager.localized("child_reward_progress_last_prefix")) +\(lastSkillRewardPoints)")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.85))
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.yellow.opacity(0.22))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("child_reward_progress_title"))
        .accessibilityValue("\(dailyRewardPoints)")
        .accessibilityIdentifier("child_reward_progress_card")
    }

    private var creativeOutputCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_creative_output_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized(creativeOutputDone ? "child_creative_output_done" : "child_creative_output_required"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.9))
            if !creativeOutputDone {
                Button {
                    markCreativeOutputDone()
                } label: {
                    Text(localizationManager.localized("child_creative_output_action"))
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.green.opacity(0.45))
                        )
                }
                .accessibilityLabel(localizationManager.localized("child_creative_output_action"))
                .accessibilityIdentifier("child_creative_output_action")
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill((creativeOutputDone ? Color.green : Color.blue).opacity(0.2))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_creative_output_card")
    }

    private var teenCreativeOutputCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_creative_output_v2_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text("\(localizationManager.localized("child_creative_output_v2_progress_prefix")) \(teenArtifactCount)/\(teenArtifactTarget)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.9))
            Text(localizationManager.localized(teenLastArtifactKey))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.82))

            HStack(spacing: 8) {
                Button {
                    recordTeenArtifact(typeKey: "child_creative_output_v2_artifact_prototype")
                } label: {
                    Text(localizationManager.localized("child_creative_output_v2_action_prototype"))
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 9)
                        .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.45)))
                }
                .disabled(teenArtifactCount >= teenArtifactTarget)

                Button {
                    recordTeenArtifact(typeKey: "child_creative_output_v2_artifact_pitch")
                } label: {
                    Text(localizationManager.localized("child_creative_output_v2_action_pitch"))
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 9)
                        .background(RoundedRectangle(cornerRadius: 10).fill(Color.purple.opacity(0.45)))
                }
                .disabled(teenArtifactCount >= teenArtifactTarget)
            }

            if teenArtifactCount >= teenArtifactTarget {
                Text(localizationManager.localized("child_creative_output_v2_done"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.green)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill((teenArtifactCount >= teenArtifactTarget ? Color.green : Color.indigo).opacity(0.22))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_creative_output_v2_card")
    }

    private var surpriseEventCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_surprise_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized(surpriseTitleKey))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.9))
            Button {
                dismissSurprise()
            } label: {
                Text(localizationManager.localized("child_surprise_action"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.purple.opacity(0.45))
                    )
            }
            .accessibilityLabel(localizationManager.localized("child_surprise_action"))
            .accessibilityIdentifier("child_surprise_action")
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.purple.opacity(0.25))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_surprise_card")
    }

    private func journeyBadge(for step: ChildDailyJourneyStep, index: Int, current: Int) -> some View {
        let isReached = current >= index
        return Text(localizationManager.localized(journeyKey(for: step)))
            .font(.system(size: 12, weight: .semibold))
            .foregroundColor(isReached ? .white : .white.opacity(0.65))
            .padding(.horizontal, 10)
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(isReached ? Color.cyan.opacity(0.45) : Color.white.opacity(0.15))
            )
    }

    private func journeyKey(for step: ChildDailyJourneyStep) -> String {
        switch step {
        case .discover:
            return "child_daily_journey_step_discover"
        case .practice:
            return "child_daily_journey_step_practice"
        case .reflect:
            return "child_daily_journey_step_reflect"
        }
    }

    private var contentIdentity: String {
        return "\(category)|\(ageGroup)|\(String(describing: loadPhase))|\(contentItems.count)|\(adaptiveHintVisible)|\(simplifiedModeEnabled)|\(schoolPacingKey)|\(schoolCorrectiveFeedbackVisible)|\(teenArtifactCount)|\(teenLastArtifactKey)"
    }

    private var shouldShowTimeLimitBanner: Bool {
        TimeTracker.shared.remainingSecondsToday <= 0
    }

    private var timeLimitBannerCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_content_time_limit_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_content_time_limit_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.9))
            Text(String(format: localizationManager.localized("child_content_time_limit_remaining"), max(0, TimeTracker.shared.remainingSecondsToday / 60)))
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.white.opacity(0.85))
            Button {
                if ChildTimeExtensionRequestStore.shared.pendingRequest() == nil {
                    ChildTimeExtensionRequestStore.shared.submitRequest(
                        childId: activeChildID(),
                        requestedExtraMinutes: 15
                    )
                    extensionRequestStatus = localizationManager.localized("child_content_request_sent_status")
                    SoundEffectPlayer.shared.play(.success, priority: .medium)
                } else {
                    extensionRequestStatus = localizationManager.localized("child_content_request_already_pending_status")
                    SoundEffectPlayer.shared.play(.warning, priority: .medium)
                }
            } label: {
                Text(localizationManager.localized("child_content_request_more_time"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.cyan.opacity(0.45))
                    )
            }
            .accessibilityLabel(localizationManager.localized("child_content_request_more_time"))
            .accessibilityIdentifier("child_content_request_more_time")
            if let extensionRequestStatus, !extensionRequestStatus.isEmpty {
                Text(extensionRequestStatus)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.85))
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.red.opacity(0.25))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_content_time_limit_banner")
    }

    private var dataDrivenContent: some View {
        VStack(spacing: 12) {
            ForEach(displayedContentItems, id: \.id) { item in
                let pct = min(100, max(0, progressById[item.id]?.completionPercent ?? 0))
                let resolvedTitle = localizedContentTitle(for: item)
                AnimatedButton(tone: animatedTone(for: item), haptics: true, playsSound: true) {
                    let result = await trackContentOpen(item)
                    await MainActor.run {
                        switch result {
                        case .success:
                            mascotResetToken = UUID()
                            mascotEmotion = .happy
                            mascotActivity = .active
                            scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.75)
                        case .error:
                            mascotResetToken = UUID()
                            mascotEmotion = .supportive
                            mascotActivity = .active
                            SoundEffectPlayer.shared.play(.warning, priority: .medium)
                            scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.75)
                        case .none:
                            mascotActivity = .active
                            scheduleMascotReset(to: mascotEmotion, activity: .idle, delay: 0.45)
                        }
                        if result != .error,
                           let route = ContentExperienceResolver.shared.resolve(for: item) {
                            selectedExperience = ContentExperiencePresentation(
                                item: item,
                                route: route
                            )
                        }
                    }
                    return result
                } label: {
                    HStack(alignment: .top, spacing: 12) {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(resolvedTitle)
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.white)
                            Text(item.type.rawValue.capitalized)
                                .font(.system(size: 11, weight: .medium))
                                .foregroundColor(.white.opacity(0.6))
                            ChildContentProgressBar(
                                value: pct,
                                track: Color.white.opacity(0.2),
                                fill: Color.cyan.opacity(0.9)
                            )
                            .accessibilityIdentifier("child_content_item_progress_\(item.id)")
                            HStack {
                                Text(lastOpenedDescription(for: item.id))
                                    .font(.system(size: 12, weight: .medium))
                                    .foregroundColor(.white.opacity(0.72))
                                Spacer()
                                Text(progressText(for: item.id))
                                    .font(.system(size: 13, weight: .semibold))
                                    .foregroundColor(.white.opacity(0.9))
                            }
                            HStack(spacing: 6) {
                                Image(systemName: "hand.tap.fill")
                                    .font(.system(size: 11, weight: .semibold))
                                    .foregroundColor(.cyan)
                                Text(localizationManager.localized("child_content_tap_to_open"))
                                    .font(.system(size: 11, weight: .semibold))
                                    .foregroundColor(.cyan)
                            }
                        }
                        VStack(alignment: .trailing) {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 22))
                                .foregroundColor(isCompleted(item.id) ? .green : .white.opacity(0.4))
                            Image(systemName: "chevron.right.circle.fill")
                                .font(.system(size: 18, weight: .semibold))
                                .foregroundColor(.cyan.opacity(0.9))
                                .padding(.top, 8)
                        }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.white.opacity(0.16))
                    )
                }
                .accessibilityLabel(resolvedTitle)
                .accessibilityValue([progressText(for: item.id), lastOpenedDescription(for: item.id)].joined(separator: " · "))
                .accessibilityIdentifier("child_content_row_\(item.id)")
                .contextMenu {
                    Button(localizationManager.localized("child_interface_done")) {
                        Task {
                            await markContentCompleted(item)
                        }
                    }
                }
            }
        }
    }

    private func localizedContentTitle(for item: ContentItem) -> String {
        let localized = localizationManager.localized(item.metadata.title)
        return localized == item.metadata.title ? item.metadata.title : localized
    }

    private var displayedContentItems: [ContentItem] {
        guard simplifiedModeEnabled else { return contentItems }
        return contentItems.sorted { lhs, rhs in
            let lhsProgress = progressById[lhs.id]?.completionPercent ?? 0
            let rhsProgress = progressById[rhs.id]?.completionPercent ?? 0
            if lhsProgress != rhsProgress {
                return lhsProgress < rhsProgress
            }
            let lhsDuration = lhs.metadata.estimatedDurationSec ?? Int.max
            let rhsDuration = rhs.metadata.estimatedDurationSec ?? Int.max
            return lhsDuration < rhsDuration
        }
    }

    private var adaptiveSupportCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_adaptive_loop_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_adaptive_loop_hint"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.9))
            Button {
                simplifiedModeEnabled = true
                recoveryBonusAttempts = max(recoveryBonusAttempts, 2)
                frustrationPlanVisible = false
                SoundEffectPlayer.shared.play(.success, priority: .medium)
            } label: {
                Text(localizationManager.localized("child_adaptive_loop_simplify_action"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.cyan.opacity(0.45))
                    )
            }
            .accessibilityLabel(localizationManager.localized("child_adaptive_loop_simplify_action"))
            .accessibilityIdentifier("child_adaptive_loop_simplify")
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.orange.opacity(0.25))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_adaptive_loop_card")
    }

    private var frustrationRecoveryCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_adaptive_loop_v2_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_adaptive_loop_v2_confidence_message"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.9))
            Text(localizationManager.localized("child_adaptive_loop_v2_recovery_plan"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.85))
            Button {
                applyFrustrationRecoveryPlan()
            } label: {
                Text(localizationManager.localized("child_adaptive_loop_v2_action"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.green.opacity(0.45))
                    )
            }
            .accessibilityLabel(localizationManager.localized("child_adaptive_loop_v2_action"))
            .accessibilityIdentifier("child_adaptive_loop_v2_action")
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.red.opacity(0.25))
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_adaptive_loop_v2_card")
    }

    private func animatedTone(for item: ContentItem) -> AnimatedButtonTone {
        switch ageGroup {
        case .kids:
            return .playful
        case .school:
            if item.type == .lesson || item.type == .safety {
                return .study
            }
            return .playful
        case .teen, .youngAdult:
            return .calm
        }
    }

    private func trackContentOpen(_ item: ContentItem) async -> AnimatedButtonFlash {
        if !TimeTracker.shared.canStartSession() {
            if recoveryBonusAttempts > 0 {
                await MainActor.run {
                    recoveryBonusAttempts = max(0, recoveryBonusAttempts - 1)
                    adaptiveHintVisible = false
                    frustrationPlanVisible = false
                }
            } else {
                await MainActor.run {
                    registerAdaptiveError()
                }
                return .error
            }
        }

        var progress = await ContentManager.shared.loadProgress(contentId: item.id)
            ?? ContentProgress(contentId: item.id, completionPercent: 0, attempts: 0, lastOpenedAt: nil, completedAt: nil)
        let previousPercent = progress.completionPercent
        let wasCompleted = progress.completionPercent >= 100
        progress.attempts += 1
        progress.lastOpenedAt = Date()
        if progress.completionPercent < 100 {
            progress.completionPercent = min(100, progress.completionPercent + 20)
            if progress.completionPercent >= 100 {
                progress.completedAt = Date()
            }
        }
        if ageGroup == .kids, !creativeOutputDone, progress.completionPercent >= 100 {
            progress.completionPercent = 80
            progress.completedAt = nil
        }
        try? await ContentManager.shared.saveProgress(progress)
        ProgressTracker.shared.recordOpen(contentId: item.id)
        TimeTracker.shared.addUsage(seconds: max(60, item.metadata.estimatedDurationSec ?? 300))
        ContentManager.shared.recordPersonalizationInteraction(for: item)
        let completedNow = progress.completionPercent >= 100
        let deltaPercent = max(0, progress.completionPercent - previousPercent)
        let rewardDelta = rewardPoints(forDeltaPercent: deltaPercent, completedNow: completedNow, wasCompleted: wasCompleted)
        await MainActor.run {
            progressById[item.id] = progress
            refreshDailyJourneyStep()
            refreshSchoolJourneyPacing()
            refreshTeenJourneyAutonomy()
            clearAdaptiveErrorStreak()
            if ageGroup == .kids, !creativeOutputDone, progress.completionPercent >= 80 {
                creativeReminderVisible = true
            }
            if rewardDelta > 0 {
                awardSkillProgressPoints(rewardDelta)
            }
            registerSessionForSurprise()
        }
        if completedNow && !wasCompleted {
            return .success
        }
        return .none
    }

    private func markContentCompleted(_ item: ContentItem) async {
        if ageGroup == .kids, !creativeOutputDone {
            await MainActor.run {
                creativeReminderVisible = true
                mascotResetToken = UUID()
                mascotEmotion = .supportive
                mascotActivity = .active
                SoundEffectPlayer.shared.play(.warning, priority: .medium)
                scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.75)
            }
            return
        }
        var progress = await ContentManager.shared.loadProgress(contentId: item.id)
            ?? ContentProgress(contentId: item.id, completionPercent: 0, attempts: 0, lastOpenedAt: nil, completedAt: nil)
        let previousPercent = progress.completionPercent
        progress.completionPercent = 100
        progress.completedAt = Date()
        progress.lastOpenedAt = Date()
        try? await ContentManager.shared.saveProgress(progress)
        ProgressTracker.shared.recordCompletion(contentId: item.id)
        ContentManager.shared.recordPersonalizationInteraction(for: item)
        await MainActor.run {
            progressById[item.id] = progress
            refreshDailyJourneyStep()
            refreshSchoolJourneyPacing()
            refreshTeenJourneyAutonomy()
            clearAdaptiveErrorStreak()
            let deltaPercent = max(0, progress.completionPercent - previousPercent)
            let rewardDelta = rewardPoints(forDeltaPercent: deltaPercent, completedNow: true, wasCompleted: previousPercent >= 100)
            if rewardDelta > 0 {
                awardSkillProgressPoints(rewardDelta)
            }
            mascotResetToken = UUID()
            mascotEmotion = .happy
            mascotActivity = .active
            SoundEffectPlayer.shared.play(.complete, priority: .high)
            scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.85)
        }
    }

    private func progressText(for contentId: String) -> String {
        let percent = Int(progressById[contentId]?.completionPercent ?? 0)
        return "\(percent)%"
    }

    private func lastOpenedDescription(for contentId: String) -> String {
        if let d = progressById[contentId]?.lastOpenedAt {
            let fmt = RelativeDateTimeFormatter()
            fmt.locale = localizationManager.locale
            fmt.unitsStyle = .short
            return fmt.localizedString(for: d, relativeTo: Date())
        }
        return localizationManager.localized("child_content_last_opened_never")
    }

    private func isCompleted(_ contentId: String) -> Bool {
        (progressById[contentId]?.completionPercent ?? 0) >= 100
    }

    private func refreshDailyJourneyStep() {
        let computed = computeJourneyStep()
        let key = dailyJourneyStorageKey()
        let previousRaw = UserDefaults.standard.integer(forKey: key)
        let nextRaw = max(previousRaw, computed.rawValue)
        let next = ChildDailyJourneyStep(rawValue: nextRaw) ?? computed
        dailyJourneyStep = next
        UserDefaults.standard.set(nextRaw, forKey: key)
    }

    private func refreshSchoolJourneyPacing() {
        guard ageGroup == .school else { return }
        let attempts = progressById.values.reduce(0) { $0 + $1.attempts }
        let average = averageCategoryProgress
        if average >= 75 {
            schoolPacingKey = "child_daily_journey_v2_pacing_fast"
            schoolCorrectiveFeedbackVisible = false
            schoolCorrectiveFeedbackKey = "child_daily_journey_v2_feedback_keep_going"
            return
        }
        if average >= 35 {
            schoolPacingKey = "child_daily_journey_v2_pacing_steady"
            schoolCorrectiveFeedbackVisible = false
            schoolCorrectiveFeedbackKey = "child_daily_journey_v2_feedback_keep_going"
            return
        }
        schoolPacingKey = "child_daily_journey_v2_pacing_support"
        schoolCorrectiveFeedbackVisible = attempts >= 3
        schoolCorrectiveFeedbackKey = attempts >= 5
            ? "child_daily_journey_v2_feedback_retry"
            : "child_daily_journey_v2_feedback_hint"
    }

    private func refreshTeenJourneyAutonomy() {
        guard ageGroup == .teen || ageGroup == .youngAdult else { return }
        let attempts = progressById.values.reduce(0) { $0 + $1.attempts }
        let completions = progressById.values.filter { $0.completionPercent >= 100 }.count
        let average = averageCategoryProgress
        if completions >= 2 || average >= 85 {
            teenAutonomyFocusKey = "child_daily_journey_v3_focus_lead"
            teenReflectionPromptVisible = true
        } else if attempts >= 2 || average >= 45 {
            teenAutonomyFocusKey = "child_daily_journey_v3_focus_build"
            teenReflectionPromptVisible = true
        } else {
            teenAutonomyFocusKey = "child_daily_journey_v3_focus_explore"
            teenReflectionPromptVisible = false
        }
        UserDefaults.standard.set(teenAutonomyFocusKey, forKey: teenAutonomyStorageKey())
        UserDefaults.standard.set(teenReflectionPromptVisible, forKey: teenReflectionPromptStorageKey())
    }

    private func computeJourneyStep() -> ChildDailyJourneyStep {
        let attempts = progressById.values.reduce(0) { $0 + $1.attempts }
        let completions = progressById.values.filter { $0.completionPercent >= 100 }.count
        let average = averageCategoryProgress
        if completions > 0 || average >= 80 {
            return .reflect
        }
        if attempts >= 2 || average >= 30 {
            return .practice
        }
        return .discover
    }

    private func dailyJourneyStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.dailyJourney.\(child).\(category).\(day)"
    }

    private func loadTeenJourneyState() {
        guard ageGroup == .teen || ageGroup == .youngAdult else { return }
        let focus = UserDefaults.standard.string(forKey: teenAutonomyStorageKey()) ?? "child_daily_journey_v3_focus_explore"
        teenAutonomyFocusKey = focus
        teenReflectionPromptVisible = UserDefaults.standard.bool(forKey: teenReflectionPromptStorageKey())
        teenReflectionCompleted = UserDefaults.standard.bool(forKey: teenReflectionDoneStorageKey())
        refreshTeenJourneyAutonomy()
    }

    private func completeTeenReflection() {
        teenReflectionCompleted = true
        UserDefaults.standard.set(true, forKey: teenReflectionDoneStorageKey())
        awardSkillProgressPoints(3)
        MasterLogger.shared.business("P2-305 reflection_complete child=\(activeChildID()) category=\(category) focus=\(teenAutonomyFocusKey)")
    }

    private func teenAutonomyStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.dailyJourneyV3.focus.\(child).\(category).\(day)"
    }

    private func teenReflectionPromptStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.dailyJourneyV3.prompt.\(child).\(category).\(day)"
    }

    private func teenReflectionDoneStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.dailyJourneyV3.done.\(child).\(category).\(day)"
    }

    private func activeChildID() -> String {
        let raw = UserDefaults.standard.string(forKey: "active_child_profile_server_id")?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return raw.isEmpty ? "local-default-child" : raw
    }

    private func dayKey(for date: Date) -> String {
        let c = Calendar.current.dateComponents([.year, .month, .day], from: date)
        return String(format: "%04d-%02d-%02d", c.year ?? 0, c.month ?? 0, c.day ?? 0)
    }

    private func rewardPoints(forDeltaPercent delta: Double, completedNow: Bool, wasCompleted: Bool) -> Int {
        guard delta > 0 else { return 0 }
        var points = max(1, Int(delta / 10.0))
        if completedNow && !wasCompleted {
            points += 2
        }
        return points
    }

    private func awardSkillProgressPoints(_ points: Int) {
        guard points > 0 else { return }
        dailyRewardPoints += points
        lastSkillRewardPoints = points
        UserDefaults.standard.set(dailyRewardPoints, forKey: dailyRewardStorageKey())
        SoundEffectPlayer.shared.play(.reward, priority: .medium)
    }

    private func loadDailyRewardPoints() {
        dailyRewardPoints = UserDefaults.standard.integer(forKey: dailyRewardStorageKey())
        lastSkillRewardPoints = 0
    }

    private func dailyRewardStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.dailyReward.\(child).\(category).\(day)"
    }

    private func loadSurpriseState() {
        surpriseVisible = false
        sessionsUntilSurprise = UserDefaults.standard.integer(forKey: surpriseSessionsStorageKey())
        if sessionsUntilSurprise <= 0 {
            sessionsUntilSurprise = 3
            UserDefaults.standard.set(sessionsUntilSurprise, forKey: surpriseSessionsStorageKey())
        }
    }

    private func registerSessionForSurprise() {
        sessionsUntilSurprise -= 1
        if sessionsUntilSurprise <= 0 {
            triggerSurpriseEvent()
            sessionsUntilSurprise = 4
        }
        UserDefaults.standard.set(sessionsUntilSurprise, forKey: surpriseSessionsStorageKey())
    }

    private func triggerSurpriseEvent() {
        let keys = [
            "child_surprise_title_hero",
            "child_surprise_title_sticker",
            "child_surprise_title_mini_event"
        ]
        let index = Int.random(in: 0..<keys.count)
        surpriseTitleKey = keys[index]
        surpriseVisible = true
        mascotResetToken = UUID()
        mascotEmotion = .happy
        mascotActivity = .active
        SoundEffectPlayer.shared.play(.reward, priority: .high)
        scheduleMascotReset(to: .neutral, activity: .idle, delay: 1.1)
    }

    private func dismissSurprise() {
        surpriseVisible = false
    }

    private func surpriseSessionsStorageKey() -> String {
        let child = activeChildID()
        return "child.surprise.sessionsUntil.\(child).\(category)"
    }

    private func markCreativeOutputDone() {
        creativeOutputDone = true
        creativeReminderVisible = false
        UserDefaults.standard.set(true, forKey: creativeOutputStorageKey())
        awardSkillProgressPoints(2)
    }

    private func loadCreativeOutputState() {
        creativeOutputDone = UserDefaults.standard.bool(forKey: creativeOutputStorageKey())
        creativeReminderVisible = false
    }

    private func loadTeenCreativeOutputState() {
        guard ageGroup == .teen || ageGroup == .youngAdult else { return }
        teenArtifactCount = UserDefaults.standard.integer(forKey: teenCreativeOutputCountStorageKey())
        let last = UserDefaults.standard.string(forKey: teenCreativeOutputLastStorageKey()) ?? "child_creative_output_v2_none"
        teenLastArtifactKey = last
        teenArtifactTarget = 2
    }

    private func recordTeenArtifact(typeKey: String) {
        guard ageGroup == .teen || ageGroup == .youngAdult else { return }
        guard teenArtifactCount < teenArtifactTarget else { return }
        teenArtifactCount += 1
        teenLastArtifactKey = typeKey
        UserDefaults.standard.set(teenArtifactCount, forKey: teenCreativeOutputCountStorageKey())
        UserDefaults.standard.set(typeKey, forKey: teenCreativeOutputLastStorageKey())
        awardSkillProgressPoints(2)
        MasterLogger.shared.business("P2-306 artifact_recorded child=\(activeChildID()) category=\(category) artifact=\(typeKey) count=\(teenArtifactCount)")
    }

    private func creativeOutputStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.creativeOutput.done.\(child).\(category).\(day)"
    }

    private func teenCreativeOutputCountStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.creativeOutputV2.count.\(child).\(category).\(day)"
    }

    private func teenCreativeOutputLastStorageKey() -> String {
        let child = activeChildID()
        let day = dayKey(for: Date())
        return "child.creativeOutputV2.last.\(child).\(category).\(day)"
    }

    private func registerAdaptiveError() {
        consecutiveOpenErrors += 1
        frustrationLevel += 1
        if consecutiveOpenErrors >= 2 {
            adaptiveHintVisible = true
            mascotResetToken = UUID()
            mascotEmotion = .supportive
            mascotActivity = .active
            SoundEffectPlayer.shared.play(.warning, priority: .high)
            scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.9)
        }
        if frustrationLevel >= 3 {
            frustrationPlanVisible = true
        }
    }

    private func clearAdaptiveErrorStreak() {
        consecutiveOpenErrors = 0
        adaptiveHintVisible = false
        frustrationLevel = max(0, frustrationLevel - 1)
        if frustrationLevel == 0 {
            frustrationPlanVisible = false
        }
    }

    private func applyFrustrationRecoveryPlan() {
        simplifiedModeEnabled = true
        recoveryBonusAttempts = max(recoveryBonusAttempts, 3)
        frustrationLevel = 0
        frustrationPlanVisible = false
        adaptiveHintVisible = false
        mascotResetToken = UUID()
        mascotEmotion = .happy
        mascotActivity = .active
        SoundEffectPlayer.shared.play(.success, priority: .high)
        scheduleMascotReset(to: .neutral, activity: .idle, delay: 0.9)
    }
    
    #if false
    // W4-4: прежние off-line карточки (игрушки/сетки) отключены — пусто и ошибка через `childContentEmptyView` / `childContentErrorView`.
    // Код оставлен в #if false для удобства археологии; не удаляйте без product review.
    // MARK: - Kids Content (1-6 лет, legacy)
    
    private var kidsContent: some View {
        VStack(spacing: 16) {
            // Сравниваем с ключами локализации
            if category == "child_interface_category_toys" {
                toysContent
            } else if category == "child_interface_category_drawing" {
                drawingContent
            } else if category == "child_interface_category_songs" {
                songsContent
            } else if category == "child_interface_category_stories" {
                fairyTalesContent
            } else {
                defaultContent
            }
        }
    }
    
    private var toysContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "cube.box")
                .font(.system(size: 80))
                .foregroundColor(.pink)
            
            Text(localizationManager.localized("child_game_welcome"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Кнопки игр
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                toyButton(icon: "🧸", title: "Медвежонок")
                toyButton(icon: "🚗", title: "Машинка")
                toyButton(icon: "🎈", title: "Шарик")
                toyButton(icon: "🎁", title: "Сюрприз")
            }
        }
    }
    
    private func toyButton(icon: String, title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.pink.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.pink, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var drawingContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "paintbrush.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text(localizationManager.localized("child_creativity_create"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Цвета для рисования
            HStack(spacing: 16) {
                colorButton(color: .red)
                colorButton(color: .blue)
                colorButton(color: .yellow)
                colorButton(color: .green)
                colorButton(color: .purple)
            }
        }
    }
    
    private func colorButton(color: Color) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            Circle()
                .fill(color)
                .frame(width: 50, height: 50)
                .overlay(
                    Circle()
                        .stroke(Color.white, lineWidth: 3)
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var songsContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "music.note")
                .font(.system(size: 80))
                .foregroundColor(.purple)
            
            Text(localizationManager.localized("child_game_welcome"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Список песен
            VStack(spacing: 12) {
                songItem(title: "🐻 Песенка медведя")
                songItem(title: "🐰 Песенка зайки")
                songItem(title: "🐸 Песенка лягушки")
            }
        }
    }
    
    private func songItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.purple)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var fairyTalesContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "book.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text(localizationManager.localized("child_game_welcome"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Список сказок
            VStack(spacing: 12) {
                taleItem(title: "🧙‍♀️ Колобок")
                taleItem(title: "👑 Репка")
                taleItem(title: "🐷 Три поросёнка")
            }
        }
    }
    
    private func taleItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - School Content (7-12 лет)
    
    private var schoolContent: some View {
        VStack(spacing: 16) {
            // Сначала проверяем локализованные значения
            if category == "child_interface_category_games" {
                gamesContent
            } else if category == "child_interface_category_study" {
                studyContent
            } else if category == "child_interface_category_creativity" {
                creativityContent
            } else if category == "child_interface_category_cartoons" {
                cartoonsContent
            } else {
                defaultContent
            }
        }
    }
    
    private var gamesContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "gamecontroller.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)
            
            Text(localizationManager.localized("child_game_zone"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                gameButton(icon: "🎮", title: localizationManager.localized("child_game_adventures"))
                gameButton(icon: "🧩", title: localizationManager.localized("child_game_puzzles"))
                gameButton(icon: "🎯", title: localizationManager.localized("child_game_logic"))
                gameButton(icon: "⚡", title: localizationManager.localized("child_game_speed"))
            }
        }
    }
    
    private func gameButton(icon: String, title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.green.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.green, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var studyContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "book.closed.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text(localizationManager.localized("child_study_learning"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                studySubject(subject: localizationManager.localized("child_study_subject_russian"))
                studySubject(subject: localizationManager.localized("child_study_subject_math"))
                studySubject(subject: localizationManager.localized("child_study_subject_world"))
            }
        }
    }
    
    private func studySubject(subject: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(subject)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var creativityContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "paintpalette.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text(localizationManager.localized("child_creativity_create"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                creativityButton(icon: "✏️", title: localizationManager.localized("child_creativity_drawing"))
                creativityButton(icon: "✂️", title: localizationManager.localized("child_creativity_application"))
                creativityButton(icon: "🎨", title: localizationManager.localized("child_creativity_coloring"))
                creativityButton(icon: "🖼️", title: localizationManager.localized("child_creativity_photo"))
            }
        }
    }
    
    private func creativityButton(icon: String, title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.orange.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.orange, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var cartoonsContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "tv.fill")
                .font(.system(size: 80))
                .foregroundColor(.red)
            
            Text(localizationManager.localized("child_cartoons_favorites"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                cartoonItem(title: localizationManager.localized("child_cartoons_robots"))
                cartoonItem(title: localizationManager.localized("child_cartoons_adventures"))
                cartoonItem(title: localizationManager.localized("child_cartoons_fantasy"))
            }
        }
    }
    
    private func cartoonItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.red)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Teen Content (13-17 лет)
    
    private var teenContent: some View {
        VStack(spacing: 16) {
            // Используем только локализованные значения
            if category == "child_interface_category_programming" {
                programmingContent
            } else if category == "child_interface_category_social" {
                socialMediaContent
            } else if category == "child_interface_category_music" {
                musicContent
            } else if category == "child_interface_category_video" {
                videoContent
            } else {
                defaultContent
            }
        }
    }
    
    private var programmingContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "laptopcomputer")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text(localizationManager.localized("child_content_programming_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                programmingLanguage(language: "🐍 Python")
                programmingLanguage(language: "⚡ JavaScript")
                programmingLanguage(language: "☕ Java")
            }
        }
    }
    
    private func programmingLanguage(language: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(language)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var socialMediaContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "person.3.fill")
                .font(.system(size: 80))
                .foregroundColor(.purple)
            
            Text(localizationManager.localized("child_content_social_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                socialButton(title: "💬 Чат с друзьями")
                socialButton(title: "📷 Фото и видео")
                socialButton(title: "🎮 Игры вместе")
            }
        }
    }
    
    private func socialButton(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.purple)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var musicContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "music.note.list")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text(localizationManager.localized("child_content_music_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                musicGenre(genre: "🎸 Рок")
                musicGenre(genre: "🎤 Поп")
                musicGenre(genre: "🎹 Электронная")
            }
        }
    }
    
    private func musicGenre(genre: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(genre)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.orange)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var videoContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "play.rectangle.fill")
                .font(.system(size: 80))
                .foregroundColor(.red)
            
            Text(localizationManager.localized("child_content_video_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                videoCategory(category: "📺 Развлечения")
                videoCategory(category: "🎓 Обучение")
                videoCategory(category: "🎮 Игры")
            }
        }
    }
    
    private func videoCategory(category: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(category)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.red)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Young Adult Content (18-22 лет)
    
    private var youngAdultContent: some View {
        VStack(spacing: 16) {
            // Используем только локализованные значения
            if category == "child_interface_category_education" {
                educationContent
            } else if category == "child_interface_category_career" {
                careerContent
            } else if category == "child_interface_category_internet" {
                internetContent
            } else if category == "child_interface_category_movies" {
                cinemaContent
            } else {
                defaultContent
            }
        }
    }
    
    private var educationContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "graduationcap.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text(localizationManager.localized("child_content_education_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                courseItem(title: "🎓 Онлайн-курсы")
                courseItem(title: "📚 Книги")
                courseItem(title: "🎯 Навыки")
            }
        }
    }
    
    private func courseItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var careerContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "briefcase.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)
            
            Text(localizationManager.localized("child_content_career_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                careerOption(title: "💼 Вакансии")
                careerOption(title: "📈 Развитие")
                careerOption(title: "🤝 Сеть контактов")
            }
        }
    }
    
    private func careerOption(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.green)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var internetContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "globe")
                .font(.system(size: 80))
                .foregroundColor(.purple)
            
            Text(localizationManager.localized("child_content_internet_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                webResource(title: "🌐 Полезные сайты")
                webResource(title: "📰 Новости")
                webResource(title: "🔍 Поиск информации")
            }
        }
    }
    
    private func webResource(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.purple)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var cinemaContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "film.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text(localizationManager.localized("child_content_cinema_title"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                movieCategory(category: "🎬 Фильмы")
                movieCategory(category: "📺 Сериалы")
                movieCategory(category: "🎭 Документалистика")
            }
        }
    }
    
    private func movieCategory(category: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(category)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.orange)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    #endif

    // MARK: - Additional Info Section
    
    private var additionalInfoSection: some View {
        VStack(spacing: 12) {
            Text(localizationManager.localized("child_daily_tip_title"))
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white.opacity(0.8))
            
            Text(dailyTip)
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.7))
                .multilineTextAlignment(.center)
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.white.opacity(0.1))
                )
        }
        .padding(.top, 20)
        .padding(.bottom, 32)
    }
    
    private var dailyTip: String {
        switch ageGroup {
        case .kids:
            return localizationManager.localized("child_daily_tip_kids")
        case .school:
            return localizationManager.localized("child_daily_tip_school")
        case .teen:
            return localizationManager.localized("child_daily_tip_teen")
        case .youngAdult:
            return localizationManager.localized("child_daily_tip_young_adult")
        }
    }
    
    // MARK: - Default Content
    
    private var defaultContent: some View {
        VStack(spacing: 20) {
            Text("🌟")
                .font(.system(size: 80))
            
            Text(localizationManager.localized("child_game_content_coming_soon"))
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
        }
    }
}

private struct ChildContentProgressBar: View {
    let value: Double
    var track: Color
    var fill: Color

    var body: some View {
        GeometryReader { g in
            let w = g.size.width * CGFloat(min(100, max(0, value)) / 100.0)
            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 4, style: .continuous)
                    .fill(track)
                RoundedRectangle(cornerRadius: 4, style: .continuous)
                    .fill(fill)
                    .frame(width: max(3, w))
            }
        }
        .frame(height: 8)
        .accessibilityHidden(true)
    }
}

private struct ContentExperiencePresentation: Identifiable {
    let item: ContentItem
    let route: ContentExperienceRoute

    var id: String { item.id }
}

// MARK: - Preview

struct ChildContentScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildContentScreen(
            category: ChildCategoryKey.games,
            ageGroup: .kids
        )
        .environmentObject(NavigationManager())
        .environmentObject(LocalizationManager.shared)
    }
}

private extension ChildInterfaceScreen.AgeGroup {
    var contentAgeBand: ContentAgeBand {
        switch self {
        case .kids:
            return .kids_1_6
        case .school:
            return .school_7_12
        case .teen:
            return .teen_13_17
        case .youngAdult:
            return .youngAdult_18_22
        }
    }
}

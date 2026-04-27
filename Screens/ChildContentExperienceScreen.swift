import SwiftUI
import SceneKit
import PencilKit
import Combine

/// Экран запуска контент-экспириенса в детском интерфейсе (W2-1).
/// Для каждого `ContentItemType` есть реальный маршрут с отдельным представлением.
struct ChildContentExperienceScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let route: ContentExperienceRoute
    let onComplete: () async -> Void

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    headerCard

                    if route == .game {
                        if item.categoryId == ChildCategoryKey.toys {
                            Toys3DSceneHostView(item: item)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("child_experience_category_toys")
                                .accessibilityLabel(localizationManager.localized("child_accessibility_category_toys"))
                        } else if item.categoryId == ChildCategoryKey.games {
                            GamesChallengeEngineView(item: item, onComplete: onComplete)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("child_experience_category_games")
                                .accessibilityLabel(localizationManager.localized("child_accessibility_category_games"))
                        } else {
                            UnicornUniverseView()
                                .environmentObject(localizationManager)
                        }
                    } else if route == .drawing {
                        DrawingExperienceHostView(item: item)
                            .environmentObject(localizationManager)
                    } else if route == .lesson, item.categoryId == ChildCategoryKey.programming {
                        ProgrammingTaskProgressionView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_programming")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_programming"))
                    } else if route == .lesson, item.categoryId == ChildCategoryKey.social {
                        SocialLiteracyDrillsView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_social")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_social"))
                    } else if route == .song, item.categoryId == ChildCategoryKey.music {
                        MusicDrillsProgressionView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_music")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_music"))
                    } else if route == .career, item.categoryId == ChildCategoryKey.education {
                        EducationPathwaysMilestonesView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_education")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_education"))
                    } else if route == .lesson, item.categoryId == ChildCategoryKey.study {
                        StudyLessonTestExperienceView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_study")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_study"))
                    } else if route == .song {
                        KaraokeExperienceHostView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                    } else if route == .story {
                        StoryExperienceHostView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                    } else if route == .safety {
                        if item.categoryId == ChildCategoryKey.safety {
                            SafetyScenarioEngineView(item: item, onComplete: onComplete)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("child_experience_category_safety")
                                .accessibilityLabel(localizationManager.localized("child_accessibility_category_safety"))
                        } else {
                            YoungDefenderView()
                                .environmentObject(localizationManager)
                        }
                    } else if route == .video, item.categoryId == ChildCategoryKey.cartoons {
                        CartoonsActiveWatchExperienceView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_cartoons")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_cartoons"))
                    } else {
                        contentCard
                        actionCard
                    }
                }
                .padding(16)
            }
            .background(Color.black.opacity(0.03))
            .dynamicTypeSize(.small ... .accessibility3)
            .navigationTitle(item.metadata.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("child_interface_back")) {
                        dismiss()
                    }
                }
            }
        }
    }

    private var headerCard: some View {
        HStack(spacing: 12) {
            Image(systemName: route.systemImage)
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.white)
                .frame(width: 48, height: 48)
                .background(Circle().fill(color(for: route)))

            VStack(alignment: .leading, spacing: 4) {
                Text(item.metadata.title)
                    .font(.system(size: 18, weight: .bold))
                if let subtitle = item.metadata.subtitle, !subtitle.isEmpty {
                    Text(subtitle)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }
            Spacer()
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white)
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_experience_header_card")
    }

    private var contentCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(item.metadata.description ?? item.metadata.title)
                .font(.system(size: 16))
                .fixedSize(horizontal: false, vertical: true)

            if !item.metadata.tags.isEmpty {
                HStack {
                    ForEach(item.metadata.tags, id: \.self) { tag in
                        Text("#\(tag)")
                            .font(.system(size: 12, weight: .medium))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Capsule().fill(Color.secondary.opacity(0.12)))
                    }
                }
            }

            if item.isOfflineAvailable {
                Label("Offline ready", systemImage: "checkmark.icloud")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.green)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("child_experience_content_card")
    }

    private var actionCard: some View {
        VStack(spacing: 12) {
            Button {
                Task {
                    await onComplete()
                }
            } label: {
                Text(localizationManager.localized("child_interface_done"))
                    .font(.system(size: 16, weight: .bold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .foregroundColor(.white)
                    .background(RoundedRectangle(cornerRadius: 12).fill(color(for: route)))
            }

            if let url = item.payloadURL {
                Link(destination: url) {
                    Label("Open source", systemImage: "arrow.up.right.square")
                        .font(.system(size: 14, weight: .semibold))
                }
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("child_experience_action_card")
    }

    private func color(for route: ContentExperienceRoute) -> Color {
        switch route {
        case .game: return .purple
        case .lesson: return .blue
        case .video: return .orange
        case .story: return .indigo
        case .song: return .pink
        case .drawing: return .teal
        case .safety: return .green
        case .career: return .mint
        }
    }
}

private struct ProgrammingTaskStep: Identifiable {
    let id = UUID()
    let titleKey: String
    let promptKey: String
    let placeholderKey: String
    let expectedAnswer: String
    let successKey: String
}

private struct ProgrammingTaskProgressionView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var stepIndex: Int = 0
    @State private var answer: String = ""
    @State private var feedback: String = ""
    @State private var completedSteps: Int = 0
    @State private var isFinished: Bool = false

    private var steps: [ProgrammingTaskStep] {
        [
            ProgrammingTaskStep(
                titleKey: "child_programming_task_title_1",
                promptKey: "child_programming_task_prompt_1",
                placeholderKey: "child_programming_task_placeholder_1",
                expectedAnswer: "print(\"ALADDIN\")",
                successKey: "child_programming_task_success_1"
            ),
            ProgrammingTaskStep(
                titleKey: "child_programming_task_title_2",
                promptKey: "child_programming_task_prompt_2",
                placeholderKey: "child_programming_task_placeholder_2",
                expectedAnswer: "let x = 5",
                successKey: "child_programming_task_success_2"
            ),
            ProgrammingTaskStep(
                titleKey: "child_programming_task_title_3",
                promptKey: "child_programming_task_prompt_3",
                placeholderKey: "child_programming_task_placeholder_3",
                expectedAnswer: "if age >= 13",
                successKey: "child_programming_task_success_3"
            )
        ]
    }

    private var step: ProgrammingTaskStep {
        steps[stepIndex]
    }

    private var progress: Double {
        guard !steps.isEmpty else { return 0 }
        return Double(completedSteps) / Double(steps.count)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_programming_task_flow_title"))
                .font(.system(size: 17, weight: .bold))

            if !isFinished {
                Text(localizationManager.localized("child_programming_task_progress_prefix") + " \(stepIndex + 1)/\(steps.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                ProgressView(value: progress)
                    .tint(.blue)

                Text(localizationManager.localized(step.titleKey))
                    .font(.system(size: 15, weight: .bold))

                Text(localizationManager.localized(step.promptKey))
                    .font(.system(size: 14))
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.08)))

                TextField(localizationManager.localized(step.placeholderKey), text: $answer)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled(true)
                    .font(.system(size: 14, design: .monospaced))
                    .padding(10)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.gray.opacity(0.14)))

                if !feedback.isEmpty {
                    Text(feedback)
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.secondary)
                }

                HStack(spacing: 10) {
                    Button(localizationManager.localized("child_programming_task_check_action")) {
                        validateAnswer()
                    }
                    .buttonStyle(.borderedProminent)

                    Button(localizationManager.localized("child_programming_task_hint_action")) {
                        feedback = localizationManager.localized("child_programming_task_hint_prefix") + " \(step.expectedAnswer)"
                        SoundEffectPlayer.shared.play(.warning, priority: .low)
                    }
                    .buttonStyle(.bordered)
                }
            } else {
                Text(localizationManager.localized("child_programming_task_done"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.green)
                Text(localizationManager.localized("child_programming_task_score_prefix") + " \(completedSteps)/\(steps.count)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private func validateAnswer() {
        let normalized = answer.trimmingCharacters(in: .whitespacesAndNewlines)
        if normalized == step.expectedAnswer {
            completedSteps += 1
            feedback = localizationManager.localized(step.successKey)
            SoundEffectPlayer.shared.play(.success, priority: .medium)
            MasterLogger.shared.business("P2-301 step_pass contentId=\(item.id) step=\(stepIndex)")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                answer = ""
                feedback = ""
                if stepIndex < steps.count - 1 {
                    stepIndex += 1
                } else {
                    isFinished = true
                    MasterLogger.shared.business("P2-301 flow_complete contentId=\(item.id) steps=\(completedSteps)")
                }
            }
        } else {
            feedback = localizationManager.localized("child_programming_task_retry_feedback")
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
            MasterLogger.shared.business("P2-301 step_fail contentId=\(item.id) step=\(stepIndex)")
        }
    }
}

private struct SocialDrillScenario: Identifiable {
    let id = UUID()
    let promptKey: String
    let options: [String]
    let safeIndex: Int
    let explanationKey: String
}

private struct MusicDrill: Identifiable {
    let id = UUID()
    let titleKey: String
    let promptKey: String
    let options: [String]
    let correctIndex: Int
}

private struct EducationPathwayMilestone: Identifiable {
    let id = UUID()
    let titleKey: String
    let briefKey: String
    let actionKey: String
}

private struct EducationPathwaysMilestonesView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var milestoneIndex: Int = 0
    @State private var completedMilestones: Int = 0
    @State private var reflectionInput: String = ""
    @State private var showReflectionPrompt: Bool = false
    @State private var finished: Bool = false

    private var milestones: [EducationPathwayMilestone] {
        [
            EducationPathwayMilestone(
                titleKey: "child_education_milestone_title_1",
                briefKey: "child_education_milestone_brief_1",
                actionKey: "child_education_milestone_action_1"
            ),
            EducationPathwayMilestone(
                titleKey: "child_education_milestone_title_2",
                briefKey: "child_education_milestone_brief_2",
                actionKey: "child_education_milestone_action_2"
            ),
            EducationPathwayMilestone(
                titleKey: "child_education_milestone_title_3",
                briefKey: "child_education_milestone_brief_3",
                actionKey: "child_education_milestone_action_3"
            )
        ]
    }

    private var completionPercent: Int {
        guard !milestones.isEmpty else { return 0 }
        return Int((Double(completedMilestones) / Double(milestones.count)) * 100)
    }

    private var currentMilestone: EducationPathwayMilestone {
        milestones[milestoneIndex]
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_education_pathways_title"))
                .font(.system(size: 17, weight: .bold))

            if !finished {
                Text(localizationManager.localized("child_education_pathways_progress") + " \(milestoneIndex + 1)/\(milestones.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized(currentMilestone.titleKey))
                        .font(.system(size: 16, weight: .bold))
                    Text(localizationManager.localized(currentMilestone.briefKey))
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.secondary)
                    Text(localizationManager.localized(currentMilestone.actionKey))
                        .font(.system(size: 14, weight: .semibold))
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(RoundedRectangle(cornerRadius: 10).fill(Color.mint.opacity(0.14)))
                }

                metricRow

                if showReflectionPrompt {
                    TextField(localizationManager.localized("child_education_pathways_reflection_placeholder"), text: $reflectionInput)
                        .textFieldStyle(.roundedBorder)
                }

                Button(localizationManager.localized("child_education_pathways_next")) {
                    completeMilestone()
                }
                .buttonStyle(.borderedProminent)
                .disabled(showReflectionPrompt && reflectionInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            } else {
                Text(localizationManager.localized("child_education_pathways_done"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.green)
                metricRow

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .dynamicTypeSize(.small ... .accessibility3)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("child_education_pathways_card")
    }

    private var metricRow: some View {
        HStack(spacing: 14) {
            Text(localizationManager.localized("child_education_pathways_metric_completed") + " \(completedMilestones)")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
            Text(localizationManager.localized("child_education_pathways_metric_percent") + " \(completionPercent)%")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
        }
    }

    private func completeMilestone() {
        completedMilestones += 1
        let reflectionCaptured = !reflectionInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        MasterLogger.shared.business("P2-304 milestone_complete contentId=\(item.id) milestone=\(milestoneIndex) reflection=\(reflectionCaptured) progress=\(completionPercent)")

        if milestoneIndex < milestones.count - 1 {
            milestoneIndex += 1
            reflectionInput = ""
            showReflectionPrompt = milestoneIndex >= 1
        } else {
            finished = true
            MasterLogger.shared.business("P2-304 pathway_complete contentId=\(item.id) milestones=\(completedMilestones) completionPercent=\(completionPercent)")
        }
    }
}

private struct MusicDrillsProgressionView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var drillIndex: Int = 0
    @State private var selectedIndex: Int?
    @State private var correctCount: Int = 0
    @State private var streak: Int = 0
    @State private var bestStreak: Int = 0
    @State private var finished: Bool = false

    private var drills: [MusicDrill] {
        [
            MusicDrill(
                titleKey: "child_music_drill_title_1",
                promptKey: "child_music_drill_prompt_1",
                options: [
                    localizationManager.localized("child_music_drill_option_1a"),
                    localizationManager.localized("child_music_drill_option_1b"),
                    localizationManager.localized("child_music_drill_option_1c")
                ],
                correctIndex: 1
            ),
            MusicDrill(
                titleKey: "child_music_drill_title_2",
                promptKey: "child_music_drill_prompt_2",
                options: [
                    localizationManager.localized("child_music_drill_option_2a"),
                    localizationManager.localized("child_music_drill_option_2b"),
                    localizationManager.localized("child_music_drill_option_2c")
                ],
                correctIndex: 0
            ),
            MusicDrill(
                titleKey: "child_music_drill_title_3",
                promptKey: "child_music_drill_prompt_3",
                options: [
                    localizationManager.localized("child_music_drill_option_3a"),
                    localizationManager.localized("child_music_drill_option_3b"),
                    localizationManager.localized("child_music_drill_option_3c")
                ],
                correctIndex: 2
            )
        ]
    }

    private var drill: MusicDrill {
        drills[drillIndex]
    }

    private var accuracyPercent: Int {
        guard !drills.isEmpty else { return 0 }
        return Int((Double(correctCount) / Double(drills.count)) * 100)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_music_drill_title"))
                .font(.system(size: 17, weight: .bold))

            if !finished {
                Text(localizationManager.localized("child_music_drill_progress_prefix") + " \(drillIndex + 1)/\(drills.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                Text(localizationManager.localized(drill.titleKey))
                    .font(.system(size: 15, weight: .bold))

                Text(localizationManager.localized(drill.promptKey))
                    .font(.system(size: 15, weight: .semibold))
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.pink.opacity(0.1)))

                VStack(spacing: 8) {
                    ForEach(Array(drill.options.enumerated()), id: \.offset) { index, option in
                        Button {
                            selectAnswer(index)
                        } label: {
                            Text(option)
                                .font(.system(size: 15, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .foregroundColor(.white)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(answerColor(index))
                                )
                        }
                        .disabled(selectedIndex != nil)
                    }
                }

                metricRow
            } else {
                Text(localizationManager.localized("child_music_drill_done"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.green)
                metricRow

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .dynamicTypeSize(.small ... .accessibility3)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("child_music_drills_card")
    }

    private var metricRow: some View {
        HStack(spacing: 14) {
            Text(localizationManager.localized("child_music_drill_metric_accuracy") + " \(accuracyPercent)%")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
            Text(localizationManager.localized("child_music_drill_metric_streak") + " \(streak)")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
            Text(localizationManager.localized("child_music_drill_metric_best_streak") + " \(bestStreak)")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
        }
    }

    private func selectAnswer(_ index: Int) {
        guard selectedIndex == nil else { return }
        selectedIndex = index
        let isCorrect = index == drill.correctIndex
        if isCorrect {
            correctCount += 1
            streak += 1
            bestStreak = max(bestStreak, streak)
            SoundEffectPlayer.shared.play(.success, priority: .medium)
        } else {
            streak = 0
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
        }
        MasterLogger.shared.business("P2-303 drill_answer contentId=\(item.id) index=\(drillIndex) correct=\(isCorrect) streak=\(streak)")

        let transitionDelay: TimeInterval = reduceMotion ? 0.0 : 0.4
        DispatchQueue.main.asyncAfter(deadline: .now() + transitionDelay) {
            selectedIndex = nil
            if drillIndex < drills.count - 1 {
                drillIndex += 1
            } else {
                finished = true
                MasterLogger.shared.business("P2-303 drill_complete contentId=\(item.id) accuracy=\(accuracyPercent) bestStreak=\(bestStreak)")
            }
        }
    }

    private func answerColor(_ index: Int) -> Color {
        guard let selectedIndex else { return Color.pink.opacity(0.84) }
        if index == drill.correctIndex { return Color.green.opacity(0.85) }
        if selectedIndex == index { return Color.red.opacity(0.85) }
        return Color.gray.opacity(0.5)
    }
}

private struct SocialLiteracyDrillsView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var scenarioIndex: Int = 0
    @State private var selectedIndex: Int?
    @State private var safeChoices: Int = 0
    @State private var finished: Bool = false
    @State private var explanationText: String = ""

    private var scenarios: [SocialDrillScenario] {
        [
            SocialDrillScenario(
                promptKey: "child_social_drill_prompt_1",
                options: [
                    localizationManager.localized("child_social_drill_option_1a"),
                    localizationManager.localized("child_social_drill_option_1b"),
                    localizationManager.localized("child_social_drill_option_1c")
                ],
                safeIndex: 1,
                explanationKey: "child_social_drill_explanation_1"
            ),
            SocialDrillScenario(
                promptKey: "child_social_drill_prompt_2",
                options: [
                    localizationManager.localized("child_social_drill_option_2a"),
                    localizationManager.localized("child_social_drill_option_2b"),
                    localizationManager.localized("child_social_drill_option_2c")
                ],
                safeIndex: 2,
                explanationKey: "child_social_drill_explanation_2"
            ),
            SocialDrillScenario(
                promptKey: "child_social_drill_prompt_3",
                options: [
                    localizationManager.localized("child_social_drill_option_3a"),
                    localizationManager.localized("child_social_drill_option_3b"),
                    localizationManager.localized("child_social_drill_option_3c")
                ],
                safeIndex: 0,
                explanationKey: "child_social_drill_explanation_3"
            )
        ]
    }

    private var scenario: SocialDrillScenario {
        scenarios[scenarioIndex]
    }

    private var completionRate: Int {
        guard !scenarios.isEmpty else { return 0 }
        return Int((Double(safeChoices) / Double(scenarios.count)) * 100)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_social_drill_title"))
                .font(.system(size: 17, weight: .bold))

            if !finished {
                Text(localizationManager.localized("child_social_drill_progress_prefix") + " \(scenarioIndex + 1)/\(scenarios.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                Text(localizationManager.localized(scenario.promptKey))
                    .font(.system(size: 16, weight: .semibold))
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.mint.opacity(0.1)))

                VStack(spacing: 8) {
                    ForEach(Array(scenario.options.enumerated()), id: \.offset) { index, option in
                        Button {
                            select(index)
                        } label: {
                            Text(option)
                                .font(.system(size: 15, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .foregroundColor(.white)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(optionColor(index))
                                )
                        }
                        .disabled(selectedIndex != nil)
                    }
                }

                if !explanationText.isEmpty {
                    Text(explanationText)
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.secondary)
                }
            } else {
                Text(localizationManager.localized("child_social_drill_done"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.green)
                Text(localizationManager.localized("child_social_drill_metric_safe_choices") + " \(safeChoices)/\(scenarios.count)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)
                Text(localizationManager.localized("child_social_drill_metric_rate") + " \(completionRate)%")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .dynamicTypeSize(.small ... .accessibility3)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("child_social_drills_card")
    }

    private func select(_ index: Int) {
        guard selectedIndex == nil else { return }
        selectedIndex = index
        let safe = index == scenario.safeIndex
        if safe {
            safeChoices += 1
            SoundEffectPlayer.shared.play(.success, priority: .medium)
        } else {
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
        }
        explanationText = localizationManager.localized(scenario.explanationKey)
        MasterLogger.shared.business("P2-302 drill_answer contentId=\(item.id) index=\(scenarioIndex) safe=\(safe)")

        let transitionDelay: TimeInterval = reduceMotion ? 0.0 : 0.45
        DispatchQueue.main.asyncAfter(deadline: .now() + transitionDelay) {
            selectedIndex = nil
            explanationText = ""
            if scenarioIndex < scenarios.count - 1 {
                scenarioIndex += 1
            } else {
                finished = true
                MasterLogger.shared.business("P2-302 drill_complete contentId=\(item.id) safeChoices=\(safeChoices) rate=\(completionRate)")
            }
        }
    }

    private func optionColor(_ index: Int) -> Color {
        guard let selectedIndex else { return Color.mint.opacity(0.82) }
        if index == scenario.safeIndex { return Color.green.opacity(0.85) }
        if selectedIndex == index { return Color.red.opacity(0.85) }
        return Color.gray.opacity(0.5)
    }
}

private struct CartoonRecallQuestion: Identifiable {
    let id = UUID()
    let promptKey: String
    let options: [String]
    let correctIndex: Int
}

private struct CartoonsActiveWatchExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var watchProgress: Double = 0
    @State private var isPlaying: Bool = false
    @State private var checkpointUnlocked: Bool = false
    @State private var questionIndex: Int = 0
    @State private var selectedIndex: Int?
    @State private var recallCorrect: Int = 0
    @State private var recallFinished: Bool = false

    private let ticker = Timer.publish(every: 0.4, on: .main, in: .common).autoconnect()

    private var questions: [CartoonRecallQuestion] {
        [
            CartoonRecallQuestion(
                promptKey: "child_cartoons_recall_prompt_1",
                options: [
                    localizationManager.localized("child_cartoons_recall_option_1a"),
                    localizationManager.localized("child_cartoons_recall_option_1b"),
                    localizationManager.localized("child_cartoons_recall_option_1c")
                ],
                correctIndex: 0
            ),
            CartoonRecallQuestion(
                promptKey: "child_cartoons_recall_prompt_2",
                options: [
                    localizationManager.localized("child_cartoons_recall_option_2a"),
                    localizationManager.localized("child_cartoons_recall_option_2b"),
                    localizationManager.localized("child_cartoons_recall_option_2c")
                ],
                correctIndex: 2
            ),
            CartoonRecallQuestion(
                promptKey: "child_cartoons_recall_prompt_3",
                options: [
                    localizationManager.localized("child_cartoons_recall_option_3a"),
                    localizationManager.localized("child_cartoons_recall_option_3b"),
                    localizationManager.localized("child_cartoons_recall_option_3c")
                ],
                correctIndex: 1
            )
        ]
    }

    private var question: CartoonRecallQuestion {
        questions[questionIndex]
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_cartoons_active_watch_title"))
                .font(.system(size: 17, weight: .bold))

            if !checkpointUnlocked {
                activeWatchSection
            } else {
                recallSection
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onReceive(ticker) { _ in
            guard isPlaying, !checkpointUnlocked else { return }
            watchProgress = min(1.0, watchProgress + 0.03)
            if watchProgress >= 1.0 {
                isPlaying = false
                checkpointUnlocked = true
                MasterLogger.shared.business("P2-204 active watch completed contentId=\(item.id)")
            }
        }
    }

    private var activeWatchSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_cartoons_active_watch_hint"))
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.secondary)

            ProgressView(value: watchProgress)
                .tint(.orange)

            Text(localizationManager.localized("child_cartoons_active_watch_progress") + " \(Int(watchProgress * 100))%")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)

            HStack {
                Button(isPlaying ? localizationManager.localized("child_interface_back") : localizationManager.localized("child_interface_done")) {
                    isPlaying.toggle()
                    MasterLogger.shared.business("P2-204 watch toggle contentId=\(item.id) playing=\(isPlaying)")
                }
                .buttonStyle(.borderedProminent)

                Button(localizationManager.localized("child_content_empty_retry")) {
                    watchProgress = 0
                    isPlaying = false
                }
                .buttonStyle(.bordered)
            }
        }
    }

    private var recallSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            if !recallFinished {
                Text(localizationManager.localized("child_cartoons_recall_progress") + " \(questionIndex + 1)/\(questions.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                Text(localizationManager.localized(question.promptKey))
                    .font(.system(size: 16, weight: .semibold))
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.orange.opacity(0.08)))

                VStack(spacing: 8) {
                    ForEach(Array(question.options.enumerated()), id: \.offset) { index, option in
                        Button {
                            choose(index)
                        } label: {
                            Text(option)
                                .font(.system(size: 15, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .foregroundColor(.white)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(answerColor(index))
                                )
                        }
                        .disabled(selectedIndex != nil)
                    }
                }
            } else {
                Text(localizationManager.localized("child_cartoons_recall_done"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.green)
                Text(localizationManager.localized("child_cartoons_recall_score") + " \(recallCorrect)/\(questions.count)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
    }

    private func choose(_ index: Int) {
        guard selectedIndex == nil else { return }
        selectedIndex = index
        if index == question.correctIndex {
            recallCorrect += 1
            SoundEffectPlayer.shared.play(.success, priority: .medium)
        } else {
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
            selectedIndex = nil
            if questionIndex < questions.count - 1 {
                questionIndex += 1
            } else {
                recallFinished = true
                MasterLogger.shared.business("P2-204 recall finished contentId=\(item.id) correct=\(recallCorrect)")
            }
        }
    }

    private func answerColor(_ index: Int) -> Color {
        guard let selectedIndex else { return Color.orange.opacity(0.82) }
        if index == question.correctIndex { return Color.green.opacity(0.85) }
        if selectedIndex == index { return Color.red.opacity(0.85) }
        return Color.gray.opacity(0.5)
    }
}

private struct SafetyScenarioChoice: Identifiable {
    let id = UUID()
    let title: String
    let isSafe: Bool
    let feedbackKey: String
}

private struct SafetyScenario: Identifiable {
    let id = UUID()
    let promptKey: String
    let choices: [SafetyScenarioChoice]
}

private struct SafetyScenarioEngineView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var scenarioIndex: Int = 0
    @State private var selectedChoiceId: UUID?
    @State private var explainableFeedback: String?
    @State private var safeCount: Int = 0
    @State private var finished: Bool = false

    private var scenarios: [SafetyScenario] {
        [
            SafetyScenario(
                promptKey: "child_safety_scenario_prompt_1",
                choices: [
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_1a"), isSafe: true, feedbackKey: "child_safety_scenario_feedback_1a"),
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_1b"), isSafe: false, feedbackKey: "child_safety_scenario_feedback_1b"),
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_1c"), isSafe: false, feedbackKey: "child_safety_scenario_feedback_1c")
                ]
            ),
            SafetyScenario(
                promptKey: "child_safety_scenario_prompt_2",
                choices: [
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_2a"), isSafe: false, feedbackKey: "child_safety_scenario_feedback_2a"),
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_2b"), isSafe: true, feedbackKey: "child_safety_scenario_feedback_2b"),
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_2c"), isSafe: false, feedbackKey: "child_safety_scenario_feedback_2c")
                ]
            ),
            SafetyScenario(
                promptKey: "child_safety_scenario_prompt_3",
                choices: [
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_3a"), isSafe: false, feedbackKey: "child_safety_scenario_feedback_3a"),
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_3b"), isSafe: true, feedbackKey: "child_safety_scenario_feedback_3b"),
                    SafetyScenarioChoice(title: localizationManager.localized("child_safety_scenario_option_3c"), isSafe: false, feedbackKey: "child_safety_scenario_feedback_3c")
                ]
            )
        ]
    }

    private var scenario: SafetyScenario {
        scenarios[scenarioIndex]
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_safety_scenario_title"))
                .font(.system(size: 17, weight: .bold))

            if !finished {
                Text(localizationManager.localized("child_safety_scenario_progress") + " \(scenarioIndex + 1)/\(scenarios.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                Text(localizationManager.localized(scenario.promptKey))
                    .font(.system(size: 16, weight: .semibold))
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.green.opacity(0.08)))

                VStack(spacing: 8) {
                    ForEach(scenario.choices) { choice in
                        Button {
                            choose(choice)
                        } label: {
                            Text(choice.title)
                                .font(.system(size: 15, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .foregroundColor(.white)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(choiceBackground(choice))
                                )
                        }
                        .disabled(selectedChoiceId != nil)
                    }
                }

                if let explainableFeedback {
                    Text(explainableFeedback)
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.secondary)
                        .padding(.top, 2)
                }

                if selectedChoiceId != nil {
                    Button(localizationManager.localized("child_safety_scenario_next")) {
                        goNext()
                    }
                    .buttonStyle(.borderedProminent)
                }
            } else {
                Text(localizationManager.localized("child_safety_scenario_done"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.green)
                Text(localizationManager.localized("child_safety_scenario_result_prefix") + " \(safeCount)/\(scenarios.count)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private func choose(_ choice: SafetyScenarioChoice) {
        guard selectedChoiceId == nil else { return }
        selectedChoiceId = choice.id
        explainableFeedback = localizationManager.localized(choice.feedbackKey)
        if choice.isSafe {
            safeCount += 1
            SoundEffectPlayer.shared.play(.success, priority: .medium)
        } else {
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
        }
        MasterLogger.shared.business("P2-203 scenario answered contentId=\(item.id) index=\(scenarioIndex) safe=\(choice.isSafe)")
    }

    private func goNext() {
        if scenarioIndex < scenarios.count - 1 {
            scenarioIndex += 1
            selectedChoiceId = nil
            explainableFeedback = nil
        } else {
            finished = true
            MasterLogger.shared.business("P2-203 safety completed contentId=\(item.id) safeCount=\(safeCount)")
        }
    }

    private func choiceBackground(_ choice: SafetyScenarioChoice) -> Color {
        guard let selectedChoiceId else { return Color.green.opacity(0.8) }
        if selectedChoiceId == choice.id {
            return choice.isSafe ? Color.green.opacity(0.85) : Color.red.opacity(0.85)
        }
        return Color.gray.opacity(0.45)
    }
}

private struct StudyQuestion: Identifiable {
    let id = UUID()
    let prompt: String
    let options: [String]
    let correctIndex: Int
}

private struct StudyLessonTestExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var currentLessonIndex: Int = 0
    @State private var lessonDone: Bool = false
    @State private var testIndex: Int = 0
    @State private var selectedIndex: Int?
    @State private var correctAnswers: Int = 0
    @State private var testFinished: Bool = false
    @State private var passed: Bool = false

    private var lessonPages: [String] {
        [
            localizationManager.localized("child_study_lesson_page_1"),
            localizationManager.localized("child_study_lesson_page_2"),
            localizationManager.localized("child_study_lesson_page_3")
        ]
    }

    private var questions: [StudyQuestion] {
        [
            StudyQuestion(
                prompt: localizationManager.localized("child_study_test_prompt_1"),
                options: [
                    localizationManager.localized("child_study_test_option_1a"),
                    localizationManager.localized("child_study_test_option_1b"),
                    localizationManager.localized("child_study_test_option_1c")
                ],
                correctIndex: 1
            ),
            StudyQuestion(
                prompt: localizationManager.localized("child_study_test_prompt_2"),
                options: [
                    localizationManager.localized("child_study_test_option_2a"),
                    localizationManager.localized("child_study_test_option_2b"),
                    localizationManager.localized("child_study_test_option_2c")
                ],
                correctIndex: 0
            ),
            StudyQuestion(
                prompt: localizationManager.localized("child_study_test_prompt_3"),
                options: [
                    localizationManager.localized("child_study_test_option_3a"),
                    localizationManager.localized("child_study_test_option_3b"),
                    localizationManager.localized("child_study_test_option_3c")
                ],
                correctIndex: 2
            )
        ]
    }

    private var activeQuestion: StudyQuestion {
        questions[testIndex]
    }

    private var passThreshold: Int {
        2
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_study_lesson_test_title"))
                .font(.system(size: 17, weight: .bold))

            if !lessonDone {
                lessonSection
            } else {
                testSection
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var lessonSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_study_lesson_progress_prefix") + " \(currentLessonIndex + 1)/\(lessonPages.count)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)

            Text(lessonPages[currentLessonIndex])
                .font(.system(size: 16))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.08)))

            HStack {
                Button(localizationManager.localized("child_interface_back")) {
                    currentLessonIndex = max(0, currentLessonIndex - 1)
                }
                .buttonStyle(.bordered)
                .disabled(currentLessonIndex == 0)

                Spacer()

                Button(currentLessonIndex == lessonPages.count - 1
                       ? localizationManager.localized("child_study_start_test")
                       : localizationManager.localized("child_interface_done")) {
                    if currentLessonIndex < lessonPages.count - 1 {
                        currentLessonIndex += 1
                    } else {
                        lessonDone = true
                        MasterLogger.shared.business("P2-202 lesson completed contentId=\(item.id)")
                    }
                }
                .buttonStyle(.borderedProminent)
            }
        }
    }

    private var testSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            if !testFinished {
                Text(localizationManager.localized("child_study_test_progress_prefix") + " \(testIndex + 1)/\(questions.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                Text(activeQuestion.prompt)
                    .font(.system(size: 16, weight: .semibold))
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))

                VStack(spacing: 8) {
                    ForEach(Array(activeQuestion.options.enumerated()), id: \.offset) { index, option in
                        Button {
                            selectAnswer(index)
                        } label: {
                            Text(option)
                                .font(.system(size: 15, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .foregroundColor(.white)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(answerBackgroundColor(index: index))
                                )
                        }
                        .disabled(selectedIndex != nil)
                    }
                }
            } else {
                Text(localizationManager.localized(passed ? "child_study_checkpoint_passed" : "child_study_checkpoint_failed"))
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(passed ? .green : .red)

                Text(localizationManager.localized("child_study_score_prefix") + " \(correctAnswers)/\(questions.count)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)

                HStack {
                    if passed {
                        Button(localizationManager.localized("child_interface_done")) {
                            Task { await onComplete() }
                        }
                        .buttonStyle(.borderedProminent)
                    } else {
                        Button(localizationManager.localized("child_study_retry_test")) {
                            restartTest()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                }
            }
        }
    }

    private func selectAnswer(_ index: Int) {
        guard selectedIndex == nil else { return }
        selectedIndex = index
        if index == activeQuestion.correctIndex {
            correctAnswers += 1
            SoundEffectPlayer.shared.play(.success, priority: .medium)
        } else {
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
            proceedTestFlow()
        }
    }

    private func proceedTestFlow() {
        selectedIndex = nil
        if testIndex < questions.count - 1 {
            testIndex += 1
            return
        }
        testFinished = true
        passed = correctAnswers >= passThreshold
        MasterLogger.shared.business("P2-202 test finished contentId=\(item.id) correct=\(correctAnswers) passed=\(passed)")
    }

    private func restartTest() {
        testIndex = 0
        selectedIndex = nil
        correctAnswers = 0
        testFinished = false
        passed = false
    }

    private func answerBackgroundColor(index: Int) -> Color {
        guard let selectedIndex else { return Color.indigo.opacity(0.85) }
        if index == activeQuestion.correctIndex {
            return Color.green.opacity(0.85)
        }
        if selectedIndex == index {
            return Color.red.opacity(0.85)
        }
        return Color.gray.opacity(0.55)
    }
}

private enum GamesChallengeDomain: String, CaseIterable, Identifiable {
    case math
    case language

    var id: String { rawValue }
}

private struct GamesChallengeTask: Identifiable {
    let id = UUID()
    let prompt: String
    let options: [String]
    let correctIndex: Int
    let hint: String
}

private struct GamesChallengeEngineView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var domain: GamesChallengeDomain = .math
    @State private var currentIndex: Int = 0
    @State private var score: Int = 0
    @State private var selectedIndex: Int?
    @State private var showHint: Bool = false
    @State private var answeredCount: Int = 0

    private var tasks: [GamesChallengeTask] {
        switch domain {
        case .math:
            return [
                GamesChallengeTask(
                    prompt: localizationManager.localized("child_games_challenge_math_prompt_1"),
                    options: ["7", "8", "9"],
                    correctIndex: 1,
                    hint: localizationManager.localized("child_games_challenge_math_hint_1")
                ),
                GamesChallengeTask(
                    prompt: localizationManager.localized("child_games_challenge_math_prompt_2"),
                    options: ["12", "11", "10"],
                    correctIndex: 0,
                    hint: localizationManager.localized("child_games_challenge_math_hint_2")
                ),
                GamesChallengeTask(
                    prompt: localizationManager.localized("child_games_challenge_math_prompt_3"),
                    options: ["8", "9", "10"],
                    correctIndex: 2,
                    hint: localizationManager.localized("child_games_challenge_math_hint_3")
                )
            ]
        case .language:
            return [
                GamesChallengeTask(
                    prompt: localizationManager.localized("child_games_challenge_lang_prompt_1"),
                    options: [
                        localizationManager.localized("child_games_challenge_lang_option_cat"),
                        localizationManager.localized("child_games_challenge_lang_option_house"),
                        localizationManager.localized("child_games_challenge_lang_option_tree")
                    ],
                    correctIndex: 0,
                    hint: localizationManager.localized("child_games_challenge_lang_hint_1")
                ),
                GamesChallengeTask(
                    prompt: localizationManager.localized("child_games_challenge_lang_prompt_2"),
                    options: [
                        localizationManager.localized("child_games_challenge_lang_option_sun"),
                        localizationManager.localized("child_games_challenge_lang_option_book"),
                        localizationManager.localized("child_games_challenge_lang_option_frog")
                    ],
                    correctIndex: 1,
                    hint: localizationManager.localized("child_games_challenge_lang_hint_2")
                ),
                GamesChallengeTask(
                    prompt: localizationManager.localized("child_games_challenge_lang_prompt_3"),
                    options: [
                        localizationManager.localized("child_games_challenge_lang_option_plane"),
                        localizationManager.localized("child_games_challenge_lang_option_city"),
                        localizationManager.localized("child_games_challenge_lang_option_nose")
                    ],
                    correctIndex: 2,
                    hint: localizationManager.localized("child_games_challenge_lang_hint_3")
                )
            ]
        }
    }

    private var task: GamesChallengeTask {
        tasks[currentIndex]
    }

    private var progressValue: Double {
        guard !tasks.isEmpty else { return 0 }
        return Double(answeredCount) / Double(tasks.count)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_challenge_title"))
                .font(.system(size: 17, weight: .bold))

            Picker("", selection: $domain) {
                Text(localizationManager.localized("child_games_challenge_domain_math")).tag(GamesChallengeDomain.math)
                Text(localizationManager.localized("child_games_challenge_domain_language")).tag(GamesChallengeDomain.language)
            }
            .pickerStyle(.segmented)
            .onChange(of: domain) { _ in
                resetChallenge()
            }

            HStack {
                Text("\(localizationManager.localized("child_games_challenge_score")): \(score)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(answeredCount)/\(tasks.count)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)
            }

            ProgressView(value: progressValue)
                .tint(.purple)

            Text(task.prompt)
                .font(.system(size: 16, weight: .semibold))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.purple.opacity(0.08)))

            VStack(spacing: 8) {
                ForEach(Array(task.options.enumerated()), id: \.offset) { index, option in
                    Button {
                        selectOption(index)
                    } label: {
                        Text(option)
                            .font(.system(size: 15, weight: .semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(backgroundColor(forOption: index))
                            )
                            .foregroundColor(.white)
                    }
                    .disabled(selectedIndex != nil)
                }
            }

            if showHint {
                Text("\(localizationManager.localized("child_games_challenge_hint")): \(task.hint)")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
            }

            HStack(spacing: 10) {
                Button(localizationManager.localized("child_games_challenge_show_hint")) {
                    showHint = true
                    score = max(0, score - 1)
                    MasterLogger.shared.business("P2-201 hint used contentId=\(item.id) domain=\(domain.rawValue) index=\(currentIndex)")
                }
                .buttonStyle(.bordered)
                .disabled(showHint || selectedIndex != nil)

                Button(localizationManager.localized("child_content_empty_retry")) {
                    resetChallenge()
                }
                .buttonStyle(.bordered)

                Spacer()

                if answeredCount >= tasks.count {
                    Button(localizationManager.localized("child_interface_done")) {
                        Task { await onComplete() }
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private func selectOption(_ index: Int) {
        guard selectedIndex == nil else { return }
        selectedIndex = index
        answeredCount += 1
        if index == task.correctIndex {
            score += showHint ? 2 : 3
            SoundEffectPlayer.shared.play(.success, priority: .medium)
            MasterLogger.shared.business("P2-201 correct answer contentId=\(item.id) domain=\(domain.rawValue) index=\(currentIndex) score=\(score)")
        } else {
            score = max(0, score - 1)
            SoundEffectPlayer.shared.play(.warning, priority: .medium)
            MasterLogger.shared.business("P2-201 wrong answer contentId=\(item.id) domain=\(domain.rawValue) index=\(currentIndex) score=\(score)")
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            advance()
        }
    }

    private func advance() {
        showHint = false
        selectedIndex = nil
        if currentIndex < tasks.count - 1 {
            currentIndex += 1
        }
    }

    private func resetChallenge() {
        currentIndex = 0
        score = 0
        selectedIndex = nil
        showHint = false
        answeredCount = 0
    }

    private func backgroundColor(forOption index: Int) -> Color {
        guard let selectedIndex else { return Color.purple.opacity(0.85) }
        if index == task.correctIndex {
            return Color.green.opacity(0.85)
        }
        if selectedIndex == index {
            return Color.red.opacity(0.85)
        }
        return Color.gray.opacity(0.55)
    }
}

private struct StoryChoice: Identifiable, Hashable {
    let id = UUID()
    let title: String
    let nextPageId: String?
    let checkpointId: String?
}

private struct StoryPage: Identifiable, Hashable {
    let id: String
    let narration: String
    let choices: [StoryChoice]
    let checkpointId: String?
    let isEnding: Bool
}

private struct InteractiveStory: Identifiable, Hashable {
    let id: String
    let title: String
    let pages: [StoryPage]
    let startPageId: String

    func page(by id: String) -> StoryPage? {
        pages.first(where: { $0.id == id })
    }
}

private struct StoryExperienceHostView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var storyIndex: Int = 0
    @State private var pageId: String = "start"
    @State private var reachedCheckpoints: Set<String> = []
    @State private var narrationCount: Int = 0

    private var stories: [InteractiveStory] {
        [
            makeForestStory(),
            makeRobotStory(),
            makeKindnessStory(),
            makeStarStory(),
            makeLibraryStory()
        ]
    }

    private var story: InteractiveStory {
        stories[storyIndex]
    }

    private var page: StoryPage {
        story.page(by: pageId) ?? story.pages[0]
    }

    private var totalCheckpoints: Int {
        story.pages.compactMap { $0.checkpointId }.count
    }

    private var checkpointProgress: Double {
        guard totalCheckpoints > 0 else { return 0 }
        return Double(reachedCheckpoints.count) / Double(totalCheckpoints)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_story_library"))
                .font(.system(size: 17, weight: .bold))

            Picker("", selection: $storyIndex) {
                ForEach(Array(stories.enumerated()), id: \.offset) { index, s in
                    Text("\(index + 1)").tag(index)
                }
            }
            .pickerStyle(.segmented)
            .onChange(of: storyIndex) { _ in
                resetForStory()
            }

            Text(story.title)
                .font(.system(size: 15, weight: .semibold))
                .foregroundColor(.secondary)

            ProgressView(value: checkpointProgress)
                .tint(.indigo)

            Text(page.narration)
                .font(.system(size: 16, weight: .regular))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))

            Button(localizationManager.localized("child_game_welcome")) {
                narrationCount += 1
                SoundEffectPlayer.shared.playVoicePrompt(page.narration, languageCode: "ru-RU", priority: .high)
                MasterLogger.shared.business("P2-104 narration played contentId=\(item.id) story=\(story.id) page=\(page.id) count=\(narrationCount)")
            }
            .buttonStyle(.bordered)

            VStack(spacing: 8) {
                ForEach(page.choices) { choice in
                    Button {
                        handleChoice(choice)
                    } label: {
                        Text(choice.title)
                            .font(.system(size: 15, weight: .semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                    }
                    .buttonStyle(.borderedProminent)
                }
            }

            if page.isEnding {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onAppear {
            captureCheckpointIfNeeded(page)
        }
    }

    private func handleChoice(_ choice: StoryChoice) {
        if let checkpoint = choice.checkpointId {
            reachedCheckpoints.insert(checkpoint)
        }
        if let next = choice.nextPageId, story.page(by: next) != nil {
            pageId = next
            captureCheckpointIfNeeded(page)
            MasterLogger.shared.business("P2-104 choice selected contentId=\(item.id) story=\(story.id) page=\(page.id)")
        } else if page.isEnding {
            Task { await onComplete() }
        }
    }

    private func resetForStory() {
        pageId = story.startPageId
        reachedCheckpoints = []
        narrationCount = 0
        captureCheckpointIfNeeded(page)
    }

    private func captureCheckpointIfNeeded(_ currentPage: StoryPage) {
        if let checkpoint = currentPage.checkpointId {
            reachedCheckpoints.insert(checkpoint)
        }
    }
}

private func makeForestStory() -> InteractiveStory {
    InteractiveStory(
        id: "forest",
        title: "Лесные приключения",
        pages: [
            StoryPage(
                id: "start",
                narration: "Маша идёт по лесной тропинке и слышит тихий шорох у дерева.",
                choices: [
                    StoryChoice(title: "Подойти и посмотреть", nextPageId: "tree", checkpointId: "c1"),
                    StoryChoice(title: "Позвать друзей", nextPageId: "friends", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "tree",
                narration: "Под деревом сидит маленький ёжик, который потерял дорогу домой.",
                choices: [
                    StoryChoice(title: "Помочь ёжику", nextPageId: "home", checkpointId: "c2"),
                    StoryChoice(title: "Искать карту", nextPageId: "map", checkpointId: "c2")
                ],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "friends",
                narration: "Друзья быстро пришли и вместе придумали, как найти дом ёжика.",
                choices: [
                    StoryChoice(title: "Пойти по следам", nextPageId: "home", checkpointId: "c2"),
                    StoryChoice(title: "Спросить у совы", nextPageId: "map", checkpointId: "c2")
                ],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "map",
                narration: "Сова дала подсказку: нужно идти к большой поляне с ромашками.",
                choices: [
                    StoryChoice(title: "Бежать на поляну", nextPageId: "ending", checkpointId: "c3")
                ],
                checkpointId: "c3",
                isEnding: false
            ),
            StoryPage(
                id: "home",
                narration: "Ёжик радостно нашёл дом и поблагодарил Машу и её друзей.",
                choices: [
                    StoryChoice(title: "Слушать финал", nextPageId: "ending", checkpointId: "c3")
                ],
                checkpointId: "c3",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Все вместе устроили пикник и договорились всегда помогать друг другу.",
                choices: [],
                checkpointId: "c4",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeRobotStory() -> InteractiveStory {
    InteractiveStory(
        id: "robot",
        title: "Робот в мастерской",
        pages: [
            StoryPage(
                id: "start",
                narration: "Вика собирает робота и выбирает для него первый модуль.",
                choices: [
                    StoryChoice(title: "Модуль света", nextPageId: "light", checkpointId: "c1"),
                    StoryChoice(title: "Модуль движения", nextPageId: "move", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "light",
                narration: "Робот начал мигать лампочками и показывать сигналы.",
                choices: [
                    StoryChoice(title: "Добавить музыку", nextPageId: "music", checkpointId: "c2")
                ],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "move",
                narration: "Робот уверенно едет вперёд и объезжает препятствия.",
                choices: [
                    StoryChoice(title: "Добавить датчик", nextPageId: "music", checkpointId: "c2")
                ],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "music",
                narration: "Теперь робот поёт, танцует и дружелюбно приветствует детей.",
                choices: [
                    StoryChoice(title: "Показать проект", nextPageId: "ending", checkpointId: "c3")
                ],
                checkpointId: "c2",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Проект победил на школьной выставке, а Вика получила новые идеи для изобретений.",
                choices: [],
                checkpointId: "c4",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeKindnessStory() -> InteractiveStory {
    InteractiveStory(
        id: "kindness",
        title: "Добрые дела",
        pages: [
            StoryPage(
                id: "start",
                narration: "Артём замечает, что одноклассник расстроен перед контрольной.",
                choices: [
                    StoryChoice(title: "Поддержать словом", nextPageId: "talk", checkpointId: "c1"),
                    StoryChoice(title: "Помочь повторить", nextPageId: "study", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "talk",
                narration: "Тёплые слова помогли успокоиться и поверить в свои силы.",
                choices: [StoryChoice(title: "Продолжить", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "study",
                narration: "Вместе ребята быстро разобрали сложные задания и нашли решение.",
                choices: [StoryChoice(title: "Продолжить", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "После урока друзья решили чаще помогать друг другу и создали клуб поддержки.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeStarStory() -> InteractiveStory {
    InteractiveStory(
        id: "stars",
        title: "Звёздная команда",
        pages: [
            StoryPage(
                id: "start",
                narration: "Команда юных исследователей получает карту космической станции.",
                choices: [
                    StoryChoice(title: "Проверить двигатель", nextPageId: "engine", checkpointId: "c1"),
                    StoryChoice(title: "Проверить связь", nextPageId: "radio", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "engine",
                narration: "Двигатель готов, но нужно рассчитать безопасный маршрут полёта.",
                choices: [StoryChoice(title: "Проложить маршрут", nextPageId: "route", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "radio",
                narration: "Связь устойчивая, команда принимает сигнал от соседнего модуля.",
                choices: [StoryChoice(title: "Проложить маршрут", nextPageId: "route", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "route",
                narration: "Полет прошёл успешно, команда мягко стыкуется с орбитальной лабораторией.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeLibraryStory() -> InteractiveStory {
    InteractiveStory(
        id: "library",
        title: "Тайна библиотеки",
        pages: [
            StoryPage(
                id: "start",
                narration: "В старой библиотеке Лена находит загадочную записку между страницами книги.",
                choices: [
                    StoryChoice(title: "Искать подсказку в каталоге", nextPageId: "catalog", checkpointId: "c1"),
                    StoryChoice(title: "Спросить библиотекаря", nextPageId: "librarian", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "catalog",
                narration: "Каталог приводит к полке, где спрятана карта с маршрутом к тайной комнате.",
                choices: [StoryChoice(title: "Открыть тайную комнату", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "librarian",
                narration: "Библиотекарь подсказывает шифр и Лена разгадывает послание.",
                choices: [StoryChoice(title: "Открыть тайную комнату", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Внутри комнаты дети находят книги приключений и создают клуб юных читателей.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private struct KaraokeLyricLine: Identifiable, Hashable {
    let id = UUID()
    let startSec: TimeInterval
    let endSec: TimeInterval
    let text: String
}

private struct KaraokeTrack: Identifiable, Hashable {
    let id = UUID()
    let title: String
    let artist: String
    let lines: [KaraokeLyricLine]

    var duration: TimeInterval {
        lines.last?.endSec ?? 0
    }
}

private struct KaraokeExperienceHostView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var selectedTrackIndex: Int = 0
    @State private var currentTime: TimeInterval = 0
    @State private var isPlaying: Bool = false
    private let ticker = Timer.publish(every: 0.35, on: .main, in: .common).autoconnect()

    private var tracks: [KaraokeTrack] {
        [
            KaraokeTrack(
                title: "Солнечный день",
                artist: "ALADDIN Kids",
                lines: [
                    .init(startSec: 0, endSec: 3, text: "Солнечный день зовёт играть"),
                    .init(startSec: 3, endSec: 6, text: "Мы умеем вместе петь и танцевать"),
                    .init(startSec: 6, endSec: 10, text: "Улыбнись, дружок, и не скучай"),
                    .init(startSec: 10, endSec: 14, text: "Этот ритм сегодня выбирай")
                ]
            ),
            KaraokeTrack(
                title: "Буквы поют",
                artist: "ALADDIN Kids",
                lines: [
                    .init(startSec: 0, endSec: 3, text: "Буква А поёт: давай учить"),
                    .init(startSec: 3, endSec: 7, text: "Буква Б зовёт слова сложить"),
                    .init(startSec: 7, endSec: 11, text: "Каждый звук как маленький секрет"),
                    .init(startSec: 11, endSec: 15, text: "Мы запомним алфавит в момент")
                ]
            ),
            KaraokeTrack(
                title: "Считалочка друзей",
                artist: "ALADDIN Kids",
                lines: [
                    .init(startSec: 0, endSec: 3, text: "Раз и два, шагай смелей"),
                    .init(startSec: 3, endSec: 6, text: "Три и четыре, мы среди друзей"),
                    .init(startSec: 6, endSec: 10, text: "Пять и шесть, игра зовёт"),
                    .init(startSec: 10, endSec: 14, text: "Семь и восемь, песенка вперёд")
                ]
            ),
            KaraokeTrack(
                title: "Добрые слова",
                artist: "ALADDIN Kids",
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Скажем вместе: добрый день"),
                    .init(startSec: 4, endSec: 8, text: "И улыбка станет всем теплей"),
                    .init(startSec: 8, endSec: 12, text: "Пожалуйста и спасибо в ряд"),
                    .init(startSec: 12, endSec: 16, text: "С ними дружба крепнет во сто крат")
                ]
            ),
            KaraokeTrack(
                title: "Звёздный ритм",
                artist: "ALADDIN Kids",
                lines: [
                    .init(startSec: 0, endSec: 3, text: "В небе звёзды ярко так горят"),
                    .init(startSec: 3, endSec: 7, text: "Наши голоса в один момент звучат"),
                    .init(startSec: 7, endSec: 11, text: "Пой со мной, держи весёлый такт"),
                    .init(startSec: 11, endSec: 15, text: "Музыка ведёт нас в новый старт")
                ]
            )
        ]
    }

    private var selectedTrack: KaraokeTrack {
        tracks[selectedTrackIndex]
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_content_music_title"))
                .font(.system(size: 17, weight: .bold))

            Picker("", selection: $selectedTrackIndex) {
                ForEach(Array(tracks.enumerated()), id: \.offset) { index, track in
                    Text("\(index + 1)").tag(index)
                }
            }
            .pickerStyle(.segmented)
            .onChange(of: selectedTrackIndex) { _ in
                currentTime = 0
                isPlaying = false
                MasterLogger.shared.business("P2-103 karaoke track selected contentId=\(item.id) track=\(selectedTrack.title)")
            }

            Text("\(selectedTrack.title) • \(selectedTrack.artist)")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)

            ProgressView(value: min(1.0, selectedTrack.duration == 0 ? 0 : currentTime / selectedTrack.duration))
                .tint(.pink)

            ScrollView {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(selectedTrack.lines) { line in
                        Text(line.text)
                            .font(.system(size: 16, weight: isActive(line) ? .bold : .regular))
                            .foregroundColor(isActive(line) ? .pink : .primary)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 6)
                            .background(
                                RoundedRectangle(cornerRadius: 8, style: .continuous)
                                    .fill(isActive(line) ? Color.pink.opacity(0.14) : Color.clear)
                            )
                    }
                }
            }
            .frame(maxHeight: 220)

            HStack(spacing: 10) {
                Button(isPlaying ? localizationManager.localized("child_interface_back") : localizationManager.localized("child_interface_done")) {
                    isPlaying.toggle()
                    MasterLogger.shared.business("P2-103 karaoke play_toggle contentId=\(item.id) track=\(selectedTrack.title) playing=\(isPlaying)")
                }
                .buttonStyle(.borderedProminent)

                Button(localizationManager.localized("child_content_empty_retry")) {
                    currentTime = 0
                    isPlaying = false
                }
                .buttonStyle(.bordered)

                Spacer()

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onReceive(ticker) { _ in
            guard isPlaying else { return }
            let next = currentTime + 0.35
            if next >= selectedTrack.duration {
                currentTime = selectedTrack.duration
                isPlaying = false
                SoundEffectPlayer.shared.play(.success, priority: .high)
                MasterLogger.shared.business("P2-103 karaoke completed contentId=\(item.id) track=\(selectedTrack.title)")
            } else {
                currentTime = next
            }
        }
    }

    private func isActive(_ line: KaraokeLyricLine) -> Bool {
        currentTime >= line.startSec && currentTime < line.endSec
    }
}

private struct DrawingExperienceHostView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    @State private var drawing = PKDrawing()
    @State private var savedItems: [ChildSavedDrawing] = []
    @State private var selectedDrawingID: UUID?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_creativity_create"))
                .font(.system(size: 17, weight: .bold))

            DrawingCanvasRepresentable(drawing: $drawing)
                .frame(height: 300)
                .background(
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .fill(Color.white)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(Color.gray.opacity(0.25), lineWidth: 1)
                )

            HStack(spacing: 10) {
                Button(localizationManager.localized("child_interface_done")) {
                    saveCurrentDrawing()
                }
                .buttonStyle(.borderedProminent)

                Button(localizationManager.localized("child_content_empty_retry")) {
                    drawing = PKDrawing()
                }
                .buttonStyle(.bordered)
            }

            if savedItems.isEmpty {
                Text(localizationManager.localized("child_content_empty_subtitle"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
            } else {
                Text(localizationManager.localized("child_content_loading"))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(savedItems) { item in
                            Button {
                                loadDrawing(item)
                            } label: {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text(item.title)
                                        .font(.system(size: 12, weight: .semibold))
                                        .lineLimit(1)
                                    Text(item.createdAt.formatted(date: .abbreviated, time: .shortened))
                                        .font(.system(size: 10, weight: .regular))
                                        .foregroundColor(.secondary)
                                }
                                .padding(10)
                                .frame(width: 180, alignment: .leading)
                                .background(
                                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                                        .fill(selectedDrawingID == item.id ? Color.teal.opacity(0.2) : Color.white)
                                )
                            }
                        }
                    }
                }
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .task {
            refreshGallery()
        }
    }

    private func refreshGallery() {
        savedItems = ChildDrawingGalleryStore.shared.loadGallery(for: activeChildID())
            .sorted(by: { $0.createdAt > $1.createdAt })
    }

    private func saveCurrentDrawing() {
        let saved = ChildDrawingGalleryStore.shared.save(
            drawing: drawing,
            contentId: item.id,
            childId: activeChildID()
        )
        selectedDrawingID = saved.id
        MasterLogger.shared.business("P2-102 drawing saved contentId=\(item.id) childId=\(activeChildID()) drawingId=\(saved.id.uuidString)")
        refreshGallery()
    }

    private func loadDrawing(_ entry: ChildSavedDrawing) {
        guard let restored = ChildDrawingGalleryStore.shared.loadDrawing(entry, childId: activeChildID()) else { return }
        drawing = restored
        selectedDrawingID = entry.id
        MasterLogger.shared.business("P2-102 drawing loaded contentId=\(item.id) childId=\(activeChildID()) drawingId=\(entry.id.uuidString)")
    }

    private func activeChildID() -> String {
        let key = "active_child_profile_server_id"
        let raw = UserDefaults.standard.string(forKey: key)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return raw.isEmpty ? "local-default-child" : raw
    }
}

private struct DrawingCanvasRepresentable: UIViewRepresentable {
    @Binding var drawing: PKDrawing

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.delegate = context.coordinator
        canvas.drawingPolicy = .anyInput
        canvas.backgroundColor = .systemBackground
        canvas.tool = PKInkingTool(.marker, color: .systemBlue, width: 8)
        canvas.drawing = drawing
        return canvas
    }

    func updateUIView(_ uiView: PKCanvasView, context: Context) {
        if uiView.drawing != drawing {
            uiView.drawing = drawing
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(drawing: $drawing)
    }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        @Binding var drawing: PKDrawing

        init(drawing: Binding<PKDrawing>) {
            _drawing = drawing
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            drawing = canvasView.drawing
        }
    }
}

private struct ChildSavedDrawing: Codable, Identifiable, Hashable {
    let id: UUID
    let contentId: String
    let title: String
    let createdAt: Date
    let relativePath: String
}

private final class ChildDrawingGalleryStore {
    static let shared = ChildDrawingGalleryStore()

    private let fm = FileManager.default
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    private init() {
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    }

    func loadGallery(for childId: String) -> [ChildSavedDrawing] {
        let indexURL = indexFileURL(childId: childId)
        guard let data = try? Data(contentsOf: indexURL),
              let decoded = try? decoder.decode([ChildSavedDrawing].self, from: data) else {
            return []
        }
        return decoded
    }

    @discardableResult
    func save(drawing: PKDrawing, contentId: String, childId: String) -> ChildSavedDrawing {
        ensureDirectories(childId: childId)
        let id = UUID()
        let fileName = "\(id.uuidString).drawing"
        let relativePath = "children/\(childId)/gallery/\(fileName)"
        let fileURL = rootURL().appendingPathComponent(relativePath, isDirectory: false)
        let data = drawing.dataRepresentation()
        try? data.write(to: fileURL, options: .atomic)

        var index = loadGallery(for: childId)
        let item = ChildSavedDrawing(
            id: id,
            contentId: contentId,
            title: "\(contentId.prefix(18))",
            createdAt: Date(),
            relativePath: relativePath
        )
        index.append(item)
        persist(index: index, childId: childId)
        return item
    }

    func loadDrawing(_ item: ChildSavedDrawing, childId: String) -> PKDrawing? {
        let url = rootURL().appendingPathComponent(item.relativePath, isDirectory: false)
        guard let data = try? Data(contentsOf: url) else { return nil }
        return try? PKDrawing(data: data)
    }

    private func persist(index: [ChildSavedDrawing], childId: String) {
        let url = indexFileURL(childId: childId)
        guard let data = try? encoder.encode(index) else { return }
        try? data.write(to: url, options: .atomic)
    }

    private func ensureDirectories(childId: String) {
        let gallery = galleryDirectoryURL(childId: childId)
        try? fm.createDirectory(at: gallery, withIntermediateDirectories: true)
    }

    private func indexFileURL(childId: String) -> URL {
        galleryDirectoryURL(childId: childId).appendingPathComponent("index.json", isDirectory: false)
    }

    private func galleryDirectoryURL(childId: String) -> URL {
        rootURL().appendingPathComponent("children/\(childId)/gallery", isDirectory: true)
    }

    private func rootURL() -> URL {
        let appSupport = fm.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let root = appSupport.appendingPathComponent("child-content-drawings", isDirectory: true)
        try? fm.createDirectory(at: root, withIntermediateDirectories: true)
        return root
    }
}

extension Notification.Name {
    static let contentToyInteraction = Notification.Name("content.toyInteraction")
}

private enum ToySceneKind: String, CaseIterable, Identifiable {
    case robot
    case rocket
    case blocks

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .robot: return "🤖"
        case .rocket: return "🚀"
        case .blocks: return "🧱"
        }
    }
}

/// P2-101: reusable 3D scene host for toy interactions with telemetry hooks.
private struct Toys3DSceneHostView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    @State private var sceneKind: ToySceneKind = .robot
    @State private var interactionCount: Int = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(localizationManager.localized("child_game_zone"))
                    .font(.system(size: 17, weight: .bold))
                Spacer()
                Text("\(localizationManager.localized("parent_dashboard_metric_opens")): \(interactionCount)")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.secondary)
            }

            Picker("", selection: $sceneKind) {
                ForEach(ToySceneKind.allCases) { kind in
                    Text(kind.icon).tag(kind)
                }
            }
            .pickerStyle(.segmented)

            SceneView(
                scene: buildScene(for: sceneKind),
                options: [.allowsCameraControl, .autoenablesDefaultLighting]
            )
            .frame(height: 260)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(Color.white.opacity(0.4), lineWidth: 1)
            )
            .onTapGesture {
                interactionCount += 1
                MasterLogger.shared.business(
                    "P2-101 toy interaction item=\(item.id) scene=\(sceneKind.rawValue) count=\(interactionCount)"
                )
                NotificationCenter.default.post(
                    name: .contentToyInteraction,
                    object: nil,
                    userInfo: [
                        "contentId": item.id,
                        "scene": sceneKind.rawValue,
                        "interactionCount": interactionCount
                    ]
                )
            }

            Text(localizationManager.localized("child_game_welcome"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private func buildScene(for kind: ToySceneKind) -> SCNScene {
        let scene = SCNScene()
        configureBaseScene(scene)

        switch kind {
        case .robot:
            addRobotToy(to: scene)
        case .rocket:
            addRocketToy(to: scene)
        case .blocks:
            addBlocksToy(to: scene)
        }
        return scene
    }

    private func configureBaseScene(_ scene: SCNScene) {
        let camera = SCNNode()
        camera.camera = SCNCamera()
        camera.position = SCNVector3(0, 1.2, 5)
        scene.rootNode.addChildNode(camera)

        let omni = SCNNode()
        omni.light = SCNLight()
        omni.light?.type = .omni
        omni.position = SCNVector3(0, 6, 6)
        scene.rootNode.addChildNode(omni)

        let ambient = SCNNode()
        ambient.light = SCNLight()
        ambient.light?.type = .ambient
        ambient.light?.intensity = 220
        scene.rootNode.addChildNode(ambient)

        let floor = SCNNode(geometry: SCNFloor())
        floor.position = SCNVector3(0, -1.2, 0)
        floor.geometry?.firstMaterial?.diffuse.contents = UIColor.systemGray6
        scene.rootNode.addChildNode(floor)
    }

    private func addRobotToy(to scene: SCNScene) {
        let body = SCNNode(geometry: SCNCapsule(capRadius: 0.45, height: 1.3))
        body.geometry?.firstMaterial?.diffuse.contents = UIColor.systemTeal
        body.position = SCNVector3(0, -0.35, 0)
        body.runAction(.repeatForever(.rotateBy(x: 0, y: CGFloat.pi * 2, z: 0, duration: 5.0)))
        scene.rootNode.addChildNode(body)

        let head = SCNNode(geometry: SCNBox(width: 0.8, height: 0.6, length: 0.8, chamferRadius: 0.12))
        head.geometry?.firstMaterial?.diffuse.contents = UIColor.systemCyan
        head.position = SCNVector3(0, 0.8, 0)
        scene.rootNode.addChildNode(head)
    }

    private func addRocketToy(to scene: SCNScene) {
        let core = SCNNode(geometry: SCNCone(topRadius: 0.18, bottomRadius: 0.45, height: 2.0))
        core.geometry?.firstMaterial?.diffuse.contents = UIColor.systemOrange
        core.position = SCNVector3(0, -0.2, 0)
        core.runAction(.repeatForever(.sequence([
            .moveBy(x: 0, y: 0.25, z: 0, duration: 1.0),
            .moveBy(x: 0, y: -0.25, z: 0, duration: 1.0)
        ])))
        scene.rootNode.addChildNode(core)

        let ring = SCNNode(geometry: SCNTorus(ringRadius: 0.55, pipeRadius: 0.08))
        ring.geometry?.firstMaterial?.diffuse.contents = UIColor.systemYellow
        ring.position = SCNVector3(0, -0.95, 0)
        ring.runAction(.repeatForever(.rotateBy(x: CGFloat.pi * 2, y: 0, z: 0, duration: 2.2)))
        scene.rootNode.addChildNode(ring)
    }

    private func addBlocksToy(to scene: SCNScene) {
        let colors: [UIColor] = [.systemPink, .systemBlue, .systemGreen]
        for index in 0..<3 {
            let cube = SCNNode(geometry: SCNBox(width: 0.72, height: 0.72, length: 0.72, chamferRadius: 0.06))
            cube.geometry?.firstMaterial?.diffuse.contents = colors[index]
            cube.position = SCNVector3(Float(index) - 1, Float(index) * 0.55 - 0.9, 0)
            cube.runAction(.repeatForever(.rotateBy(x: 0, y: CGFloat.pi * 2, z: CGFloat.pi * 0.25, duration: 4.0 + Double(index))))
            scene.rootNode.addChildNode(cube)
        }
    }
}

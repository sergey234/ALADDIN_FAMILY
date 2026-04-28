import SwiftUI
import UIKit
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
                    } else if route == .lesson, item.categoryId == ChildCategoryKey.internet {
                        EducationPathwaysMilestonesView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_internet")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_internet"))
                    } else if route == .song, item.categoryId == ChildCategoryKey.music {
                        MusicDrillsProgressionView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_music")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_music"))
                    } else if route == .career,
                              (item.categoryId == ChildCategoryKey.education || item.categoryId == ChildCategoryKey.career) {
                        EducationPathwaysMilestonesView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier(
                                item.categoryId == ChildCategoryKey.career
                                ? "child_experience_category_career"
                                : "child_experience_category_education"
                            )
                            .accessibilityLabel(
                                localizationManager.localized(
                                    item.categoryId == ChildCategoryKey.career
                                    ? "child_accessibility_category_career"
                                    : "child_accessibility_category_education"
                                )
                            )
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
                    } else if route == .video, item.categoryId == ChildCategoryKey.movies {
                        MovieLiteracyExperienceView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_movies")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_movies"))
                    } else if route == .video, item.categoryId == ChildCategoryKey.video {
                        VideoProductionExperienceView(item: item, onComplete: onComplete)
                            .environmentObject(localizationManager)
                            .accessibilityIdentifier("child_experience_category_video")
                            .accessibilityLabel(localizationManager.localized("child_accessibility_category_video"))
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
        switch item.id {
        case "programming.01":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_swift_title_1",
                    promptKey: "child_programming_swift_prompt_1",
                    placeholderKey: "child_programming_swift_placeholder_1",
                    expectedAnswer: "import SwiftUI",
                    successKey: "child_programming_swift_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_swift_title_2",
                    promptKey: "child_programming_swift_prompt_2",
                    placeholderKey: "child_programming_swift_placeholder_2",
                    expectedAnswer: "struct ContentView: View",
                    successKey: "child_programming_swift_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_swift_title_3",
                    promptKey: "child_programming_swift_prompt_3",
                    placeholderKey: "child_programming_swift_placeholder_3",
                    expectedAnswer: "var body: some View",
                    successKey: "child_programming_swift_success_3"
                )
            ]
        case "programming.02":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_visual_title_1",
                    promptKey: "child_programming_visual_prompt_1",
                    placeholderKey: "child_programming_visual_placeholder_1",
                    expectedAnswer: "drag block",
                    successKey: "child_programming_visual_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_visual_title_2",
                    promptKey: "child_programming_visual_prompt_2",
                    placeholderKey: "child_programming_visual_placeholder_2",
                    expectedAnswer: "if condition",
                    successKey: "child_programming_visual_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_visual_title_3",
                    promptKey: "child_programming_visual_prompt_3",
                    placeholderKey: "child_programming_visual_placeholder_3",
                    expectedAnswer: "repeat loop",
                    successKey: "child_programming_visual_success_3"
                )
            ]
        case "programming.03":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_apps_title_1",
                    promptKey: "child_programming_apps_prompt_1",
                    placeholderKey: "child_programming_apps_placeholder_1",
                    expectedAnswer: "Button(\"Start\")",
                    successKey: "child_programming_apps_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_apps_title_2",
                    promptKey: "child_programming_apps_prompt_2",
                    placeholderKey: "child_programming_apps_placeholder_2",
                    expectedAnswer: "Text(\"Hello\")",
                    successKey: "child_programming_apps_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_apps_title_3",
                    promptKey: "child_programming_apps_prompt_3",
                    placeholderKey: "child_programming_apps_placeholder_3",
                    expectedAnswer: "Image(systemName: \"star\")",
                    successKey: "child_programming_apps_success_3"
                )
            ]
        case "programming.04":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_data_title_1",
                    promptKey: "child_programming_data_prompt_1",
                    placeholderKey: "child_programming_data_placeholder_1",
                    expectedAnswer: "let ages = [12, 13, 14]",
                    successKey: "child_programming_data_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_data_title_2",
                    promptKey: "child_programming_data_prompt_2",
                    placeholderKey: "child_programming_data_placeholder_2",
                    expectedAnswer: "ages.count",
                    successKey: "child_programming_data_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_data_title_3",
                    promptKey: "child_programming_data_prompt_3",
                    placeholderKey: "child_programming_data_placeholder_3",
                    expectedAnswer: "ages.first",
                    successKey: "child_programming_data_success_3"
                )
            ]
        case "programming.05":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_ux_title_1",
                    promptKey: "child_programming_ux_prompt_1",
                    placeholderKey: "child_programming_ux_placeholder_1",
                    expectedAnswer: "padding()",
                    successKey: "child_programming_ux_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_ux_title_2",
                    promptKey: "child_programming_ux_prompt_2",
                    placeholderKey: "child_programming_ux_placeholder_2",
                    expectedAnswer: "foregroundColor(.blue)",
                    successKey: "child_programming_ux_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_ux_title_3",
                    promptKey: "child_programming_ux_prompt_3",
                    placeholderKey: "child_programming_ux_placeholder_3",
                    expectedAnswer: "font(.headline)",
                    successKey: "child_programming_ux_success_3"
                )
            ]
        case "programming.07":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_debug_title_1",
                    promptKey: "child_programming_debug_prompt_1",
                    placeholderKey: "child_programming_debug_placeholder_1",
                    expectedAnswer: "print(state)",
                    successKey: "child_programming_debug_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_debug_title_2",
                    promptKey: "child_programming_debug_prompt_2",
                    placeholderKey: "child_programming_debug_placeholder_2",
                    expectedAnswer: "breakpoint",
                    successKey: "child_programming_debug_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_debug_title_3",
                    promptKey: "child_programming_debug_prompt_3",
                    placeholderKey: "child_programming_debug_placeholder_3",
                    expectedAnswer: "XCTest",
                    successKey: "child_programming_debug_success_3"
                )
            ]
        case "programming.08":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_versions_title_1",
                    promptKey: "child_programming_versions_prompt_1",
                    placeholderKey: "child_programming_versions_placeholder_1",
                    expectedAnswer: "git status",
                    successKey: "child_programming_versions_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_versions_title_2",
                    promptKey: "child_programming_versions_prompt_2",
                    placeholderKey: "child_programming_versions_placeholder_2",
                    expectedAnswer: "git commit -m \"init\"",
                    successKey: "child_programming_versions_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_versions_title_3",
                    promptKey: "child_programming_versions_prompt_3",
                    placeholderKey: "child_programming_versions_placeholder_3",
                    expectedAnswer: "git push",
                    successKey: "child_programming_versions_success_3"
                )
            ]
        case "programming.09":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_team_title_1",
                    promptKey: "child_programming_team_prompt_1",
                    placeholderKey: "child_programming_team_placeholder_1",
                    expectedAnswer: "git checkout -b feature",
                    successKey: "child_programming_team_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_team_title_2",
                    promptKey: "child_programming_team_prompt_2",
                    placeholderKey: "child_programming_team_placeholder_2",
                    expectedAnswer: "git merge feature",
                    successKey: "child_programming_team_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_team_title_3",
                    promptKey: "child_programming_team_prompt_3",
                    placeholderKey: "child_programming_team_placeholder_3",
                    expectedAnswer: "code review",
                    successKey: "child_programming_team_success_3"
                )
            ]
        case "programming.10":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_management_title_1",
                    promptKey: "child_programming_management_prompt_1",
                    placeholderKey: "child_programming_management_placeholder_1",
                    expectedAnswer: "backlog",
                    successKey: "child_programming_management_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_management_title_2",
                    promptKey: "child_programming_management_prompt_2",
                    placeholderKey: "child_programming_management_placeholder_2",
                    expectedAnswer: "sprint",
                    successKey: "child_programming_management_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_management_title_3",
                    promptKey: "child_programming_management_prompt_3",
                    placeholderKey: "child_programming_management_placeholder_3",
                    expectedAnswer: "retrospective",
                    successKey: "child_programming_management_success_3"
                )
            ]
        case "programming.11":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_ethics_title_1",
                    promptKey: "child_programming_ethics_prompt_1",
                    placeholderKey: "child_programming_ethics_placeholder_1",
                    expectedAnswer: "privacy",
                    successKey: "child_programming_ethics_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_ethics_title_2",
                    promptKey: "child_programming_ethics_prompt_2",
                    placeholderKey: "child_programming_ethics_placeholder_2",
                    expectedAnswer: "fairness",
                    successKey: "child_programming_ethics_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_ethics_title_3",
                    promptKey: "child_programming_ethics_prompt_3",
                    placeholderKey: "child_programming_ethics_placeholder_3",
                    expectedAnswer: "accessibility",
                    successKey: "child_programming_ethics_success_3"
                )
            ]
        case "programming.12":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_future_title_1",
                    promptKey: "child_programming_future_prompt_1",
                    placeholderKey: "child_programming_future_placeholder_1",
                    expectedAnswer: "ai assistant",
                    successKey: "child_programming_future_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_future_title_2",
                    promptKey: "child_programming_future_prompt_2",
                    placeholderKey: "child_programming_future_placeholder_2",
                    expectedAnswer: "robotics",
                    successKey: "child_programming_future_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_future_title_3",
                    promptKey: "child_programming_future_prompt_3",
                    placeholderKey: "child_programming_future_placeholder_3",
                    expectedAnswer: "green tech",
                    successKey: "child_programming_future_success_3"
                )
            ]
        case "programming.13":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_security_title_1",
                    promptKey: "child_programming_security_prompt_1",
                    placeholderKey: "child_programming_security_placeholder_1",
                    expectedAnswer: "input validation",
                    successKey: "child_programming_security_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_security_title_2",
                    promptKey: "child_programming_security_prompt_2",
                    placeholderKey: "child_programming_security_placeholder_2",
                    expectedAnswer: "least privilege",
                    successKey: "child_programming_security_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_security_title_3",
                    promptKey: "child_programming_security_prompt_3",
                    placeholderKey: "child_programming_security_placeholder_3",
                    expectedAnswer: "dependency update",
                    successKey: "child_programming_security_success_3"
                )
            ]
        case "programming.14":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_mobile_title_1",
                    promptKey: "child_programming_mobile_prompt_1",
                    placeholderKey: "child_programming_mobile_placeholder_1",
                    expectedAnswer: "NavigationStack",
                    successKey: "child_programming_mobile_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_mobile_title_2",
                    promptKey: "child_programming_mobile_prompt_2",
                    placeholderKey: "child_programming_mobile_placeholder_2",
                    expectedAnswer: "@State",
                    successKey: "child_programming_mobile_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_mobile_title_3",
                    promptKey: "child_programming_mobile_prompt_3",
                    placeholderKey: "child_programming_mobile_placeholder_3",
                    expectedAnswer: "onAppear",
                    successKey: "child_programming_mobile_success_3"
                )
            ]
        case "programming.15":
            return [
                ProgrammingTaskStep(
                    titleKey: "child_programming_web_title_1",
                    promptKey: "child_programming_web_prompt_1",
                    placeholderKey: "child_programming_web_placeholder_1",
                    expectedAnswer: "HTML",
                    successKey: "child_programming_web_success_1"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_web_title_2",
                    promptKey: "child_programming_web_prompt_2",
                    placeholderKey: "child_programming_web_placeholder_2",
                    expectedAnswer: "CSS",
                    successKey: "child_programming_web_success_2"
                ),
                ProgrammingTaskStep(
                    titleKey: "child_programming_web_title_3",
                    promptKey: "child_programming_web_prompt_3",
                    placeholderKey: "child_programming_web_placeholder_3",
                    expectedAnswer: "JavaScript",
                    successKey: "child_programming_web_success_3"
                )
            ]
        default:
            return [
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
        switch item.id {
        case "education.01":
            return makeEducationMilestones(prefix: "child_education_online")
        case "education.02":
            return makeEducationMilestones(prefix: "child_education_certificates")
        case "education.03":
            return makeEducationMilestones(prefix: "child_education_online")
        case "education.05":
            return makeEducationMilestones(prefix: "child_education_certificates")
        case "education.06":
            return makeEducationMilestones(prefix: "child_education_international")
        case "education.07":
            return makeEducationMilestones(prefix: "child_education_distance")
        case "education.08":
            return makeEducationMilestones(prefix: "child_education_reskilling")
        case "education.09":
            return makeEducationMilestones(prefix: "child_education_upskilling")
        case "education.10":
            return makeEducationMilestones(prefix: "child_education_science")
        case "education.11":
            return makeEducationMilestones(prefix: "child_education_research")
        case "education.12":
            return makeEducationMilestones(prefix: "child_education_academic_writing")
        case "education.13":
            return makeEducationMilestones(prefix: "child_education_presentation")
        case "education.14":
            return makeEducationMilestones(prefix: "child_education_presentation")
        case "education.15":
            return makeEducationMilestones(prefix: "child_education_global_programs")
        case "career.01":
            return makeEducationMilestones(prefix: "child_career_resume")
        case "career.02":
            return makeEducationMilestones(prefix: "child_career_resume")
        case "career.03":
            return makeEducationMilestones(prefix: "child_career_interview")
        case "career.04":
            return makeEducationMilestones(prefix: "child_career_growth")
        case "career.05":
            return makeEducationMilestones(prefix: "child_career_growth")
        case "career.06":
            return makeEducationMilestones(prefix: "child_career_networking")
        case "career.07":
            return makeEducationMilestones(prefix: "child_career_leadership")
        case "career.08":
            return makeEducationMilestones(prefix: "child_career_teamwork")
        case "career.09":
            return makeEducationMilestones(prefix: "child_career_time_management")
        case "career.10":
            return makeEducationMilestones(prefix: "child_career_time_management")
        case "career.11":
            return makeEducationMilestones(prefix: "child_career_entrepreneurship")
        case "career.12":
            return makeEducationMilestones(prefix: "child_career_freelance")
        case "career.13":
            return makeEducationMilestones(prefix: "child_career_change")
        case "career.14":
            return makeEducationMilestones(prefix: "child_career_work_life")
        case "career.15":
            return makeEducationMilestones(prefix: "child_career_ethics")
        case "internet.01":
            return makeEducationMilestones(prefix: "child_internet_cyber")
        case "internet.02":
            return makeEducationMilestones(prefix: "child_internet_cyber")
        case "internet.03":
            return makeEducationMilestones(prefix: "child_internet_payments")
        case "internet.04":
            return makeEducationMilestones(prefix: "child_internet_hacker_defense")
        case "internet.05":
            return makeEducationMilestones(prefix: "child_internet_cloud_security")
        case "internet.06":
            return makeEducationMilestones(prefix: "child_internet_device_security")
        case "internet.07":
            return makeEducationMilestones(prefix: "child_internet_phishing")
        case "internet.08":
            return makeEducationMilestones(prefix: "child_internet_phishing")
        case "internet.09":
            return makeEducationMilestones(prefix: "child_internet_email_security")
        case "internet.10":
            return makeEducationMilestones(prefix: "child_internet_virus")
        case "internet.11":
            return makeEducationMilestones(prefix: "child_internet_wifi")
        case "internet.12":
            return makeEducationMilestones(prefix: "child_internet_payments")
        case "internet.13":
            return makeEducationMilestones(prefix: "child_internet_travel_security")
        case "internet.14":
            return makeEducationMilestones(prefix: "child_internet_corporate")
        case "internet.15":
            return makeEducationMilestones(prefix: "child_internet_legal")
        default:
            return [
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
    }

    private func makeEducationMilestones(prefix: String) -> [EducationPathwayMilestone] {
        (1...3).map { i in
            EducationPathwayMilestone(
                titleKey: "\(prefix)_title_\(i)",
                briefKey: "\(prefix)_brief_\(i)",
                actionKey: "\(prefix)_action_\(i)"
            )
        }
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
        switch item.id {
        case "music.01":
            return makeMusicDrillSet(prefix: "child_music_creation_drill", correct: [0, 2, 1])
        case "music.02":
            return makeMusicDrillSet(prefix: "child_music_creation_drill", correct: [2, 1, 0])
        case "music.03":
            return makeMusicDrillSet(prefix: "child_music_instruments_drill", correct: [0, 2, 1])
        case "music.04":
            return makeMusicDrillSet(prefix: "child_music_instruments_drill", correct: [1, 0, 2])
        case "music.06":
            return makeMusicDrillSet(prefix: "child_music_history_drill", correct: [1, 0, 2])
        case "music.07":
            return makeMusicDrillSet(prefix: "child_music_psychology_drill", correct: [2, 0, 1])
        case "music.08":
            return makeMusicDrillSet(prefix: "child_music_psychology_drill", correct: [2, 1, 0])
        case "music.09":
            return makeMusicDrillSet(prefix: "child_music_focus_drill", correct: [1, 2, 0])
        case "music.10":
            return makeMusicDrillSet(prefix: "child_music_relax_drill", correct: [1, 2, 0])
        case "music.11":
            return makeMusicDrillSet(prefix: "child_music_soundtrack_drill", correct: [2, 1, 0])
        case "music.12":
            return makeMusicDrillSet(prefix: "child_music_cultures_drill", correct: [0, 2, 1])
        case "music.13":
            return makeMusicDrillSet(prefix: "child_music_modern_drill", correct: [1, 0, 2])
        case "music.14":
            return makeMusicDrillSet(prefix: "child_music_classic_drill", correct: [2, 0, 1])
        case "music.15":
            return makeMusicDrillSet(prefix: "child_music_experimental_drill", correct: [1, 0, 2])
        default:
            return [
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
    }

    private func makeMusicDrillSet(prefix: String, correct: [Int]) -> [MusicDrill] {
        (1...3).map { i in
            MusicDrill(
                titleKey: "\(prefix)_title_\(i)",
                promptKey: "\(prefix)_prompt_\(i)",
                options: [
                    localizationManager.localized("\(prefix)_option_\(i)a"),
                    localizationManager.localized("\(prefix)_option_\(i)b"),
                    localizationManager.localized("\(prefix)_option_\(i)c")
                ],
                correctIndex: correct[i - 1]
            )
        }
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
        switch item.id {
        case "social.03":
            return makeSocialDrillSet(prefix: "child_social_reputation_drill", safeIndexes: [1, 0, 2])
        case "social.04":
            return makeSocialDrillSet(prefix: "child_social_reputation_drill", safeIndexes: [1, 2, 0])
        case "social.05":
            return makeSocialDrillSet(prefix: "child_social_addiction_drill", safeIndexes: [2, 1, 0])
        case "social.07":
            return makeSocialDrillSet(prefix: "child_social_addiction_drill", safeIndexes: [2, 1, 0])
        case "social.08":
            return makeSocialDrillSet(prefix: "child_social_content_drill", safeIndexes: [1, 2, 0])
        case "social.09":
            return makeSocialDrillSet(prefix: "child_social_content_drill", safeIndexes: [1, 0, 2])
        case "social.10":
            return makeSocialDrillSet(prefix: "child_social_selfesteem_drill", safeIndexes: [1, 2, 0])
        case "social.11":
            return makeSocialDrillSet(prefix: "child_social_community_drill", safeIndexes: [2, 1, 0])
        case "social.12":
            return makeSocialDrillSet(prefix: "child_social_profnet_drill", safeIndexes: [1, 0, 2])
        case "social.13":
            return makeSocialDrillSet(prefix: "child_social_networking_drill", safeIndexes: [0, 2, 1])
        case "social.14":
            return makeSocialDrillSet(prefix: "child_social_branding_drill", safeIndexes: [2, 1, 0])
        case "social.15":
            return makeSocialDrillSet(prefix: "child_social_branding_drill", safeIndexes: [0, 2, 1])
        default:
            return [
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
    }

    private func makeSocialDrillSet(prefix: String, safeIndexes: [Int]) -> [SocialDrillScenario] {
        (1...3).map { i in
            SocialDrillScenario(
                promptKey: "\(prefix)_prompt_\(i)",
                options: [
                    localizationManager.localized("\(prefix)_option_\(i)a"),
                    localizationManager.localized("\(prefix)_option_\(i)b"),
                    localizationManager.localized("\(prefix)_option_\(i)c")
                ],
                safeIndex: safeIndexes[i - 1],
                explanationKey: "\(prefix)_explanation_\(i)"
            )
        }
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

private struct VideoProductionExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var progressValue: Int = 0

    private var cardPrefix: String {
        switch item.id {
        case "video.01": return "child_video_filming"
        case "video.02": return "child_video_editing"
        case "video.03": return "child_video_content"
        case "video.04": return "child_video_post"
        case "video.05": return "child_video_fx"
        case "video.06": return "child_video_color"
        case "video.07": return "child_video_sound"
        case "video.08": return "child_video_animation"
        case "video.09": return "child_video_social"
        case "video.10": return "child_video_documentary"
        case "video.11": return "child_video_clip"
        case "video.12": return "child_video_ad"
        case "video.13": return "child_video_content"
        case "video.14": return "child_video_vlog"
        case "video.15": return "child_video_stream"
        default: return "child_video_universal"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("\(cardPrefix)_title"))
                .font(.system(size: 17, weight: .bold))

            Text(localizationManager.localized("\(cardPrefix)_prompt"))
                .font(.system(size: 15, weight: .semibold))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.orange.opacity(0.1)))

            Text(localizationManager.localized("\(cardPrefix)_progress") + " \(progressValue)%")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)

            ProgressView(value: Double(progressValue), total: 100)
                .tint(.orange)

            HStack(spacing: 10) {
                Button(localizationManager.localized("\(cardPrefix)_action_step")) {
                    progressValue = min(progressValue + 20, 100)
                    SoundEffectPlayer.shared.play(.success, priority: .low)
                }
                .buttonStyle(.bordered)

                Button(localizationManager.localized("\(cardPrefix)_action_reset")) {
                    progressValue = 0
                    SoundEffectPlayer.shared.play(.warning, priority: .low)
                }
                .buttonStyle(.bordered)
            }

            if progressValue >= 100 {
                Text(localizationManager.localized("\(cardPrefix)_done"))
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.green)

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }
}

private struct MovieLiteracyExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var progressValue: Int = 0

    private var cardPrefix: String {
        switch item.id {
        case "movies.01": return "child_movies_classic"
        case "movies.02": return "child_movies_modern"
        case "movies.03": return "child_movies_genres"
        case "movies.04": return "child_movies_art"
        case "movies.05": return "child_movies_directors"
        case "movies.06": return "child_movies_acting"
        case "movies.07": return "child_movies_cinematography"
        case "movies.08": return "child_movies_screenwriting"
        case "movies.09": return "child_movies_producing"
        case "movies.10": return "child_movies_criticism"
        case "movies.11": return "child_movies_documentary"
        case "movies.12": return "child_movies_animation"
        case "movies.13": return "child_movies_shorts"
        case "movies.14": return "child_movies_festivals"
        case "movies.15": return "child_movies_international"
        default: return "child_movies_universal"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("\(cardPrefix)_title"))
                .font(.system(size: 17, weight: .bold))

            Text(localizationManager.localized("\(cardPrefix)_prompt"))
                .font(.system(size: 15, weight: .semibold))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.1)))

            Text(localizationManager.localized("\(cardPrefix)_progress") + " \(progressValue)%")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)

            ProgressView(value: Double(progressValue), total: 100)
                .tint(.indigo)

            HStack(spacing: 10) {
                Button(localizationManager.localized("\(cardPrefix)_action_step")) {
                    progressValue = min(progressValue + 20, 100)
                    SoundEffectPlayer.shared.play(.success, priority: .low)
                }
                .buttonStyle(.bordered)

                Button(localizationManager.localized("\(cardPrefix)_action_reset")) {
                    progressValue = 0
                    SoundEffectPlayer.shared.play(.warning, priority: .low)
                }
                .buttonStyle(.bordered)
            }

            if progressValue >= 100 {
                Text(localizationManager.localized("\(cardPrefix)_done"))
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.green)

                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
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
        switch item.id {
        case "cartoons.01":
            return makeCartoonRecallSet(prefix: "child_cartoons_educational_recall", correct: [0, 2, 1])
        case "cartoons.02":
            return [
                CartoonRecallQuestion(
                    promptKey: "child_cartoons_safety_recall_prompt_1",
                    options: [
                        localizationManager.localized("child_cartoons_safety_recall_option_1a"),
                        localizationManager.localized("child_cartoons_safety_recall_option_1b"),
                        localizationManager.localized("child_cartoons_safety_recall_option_1c")
                    ],
                    correctIndex: 0
                ),
                CartoonRecallQuestion(
                    promptKey: "child_cartoons_safety_recall_prompt_2",
                    options: [
                        localizationManager.localized("child_cartoons_safety_recall_option_2a"),
                        localizationManager.localized("child_cartoons_safety_recall_option_2b"),
                        localizationManager.localized("child_cartoons_safety_recall_option_2c")
                    ],
                    correctIndex: 1
                ),
                CartoonRecallQuestion(
                    promptKey: "child_cartoons_safety_recall_prompt_3",
                    options: [
                        localizationManager.localized("child_cartoons_safety_recall_option_3a"),
                        localizationManager.localized("child_cartoons_safety_recall_option_3b"),
                        localizationManager.localized("child_cartoons_safety_recall_option_3c")
                    ],
                    correctIndex: 2
                )
            ]
        case "cartoons.03":
            return makeCartoonRecallSet(prefix: "child_cartoons_friendship_recall", correct: [1, 0, 2])
        case "cartoons.04":
            return makeCartoonRecallSet(prefix: "child_cartoons_nature_recall", correct: [2, 1, 0])
        case "cartoons.05":
            return makeCartoonRecallSet(prefix: "child_cartoons_health_recall", correct: [0, 2, 1])
        case "cartoons.06":
            return makeCartoonRecallSet(prefix: "child_cartoons_sport_recall", correct: [1, 2, 0])
        case "cartoons.07":
            return makeCartoonRecallSet(prefix: "child_cartoons_art_recall", correct: [2, 0, 1])
        case "cartoons.08":
            return makeCartoonRecallSet(prefix: "child_cartoons_science_recall", correct: [1, 2, 0])
        case "cartoons.09":
            return makeCartoonRecallSet(prefix: "child_cartoons_history_recall", correct: [0, 1, 2])
        case "cartoons.10":
            return makeCartoonRecallSet(prefix: "child_cartoons_space_recall", correct: [2, 0, 1])
        case "cartoons.11":
            return makeCartoonRecallSet(prefix: "child_cartoons_animals_recall", correct: [1, 0, 2])
        case "cartoons.12":
            return makeCartoonRecallSet(prefix: "child_cartoons_transport_recall", correct: [0, 2, 1])
        case "cartoons.13":
            return makeCartoonRecallSet(prefix: "child_cartoons_food_recall", correct: [2, 1, 0])
        case "cartoons.14":
            return makeCartoonRecallSet(prefix: "child_cartoons_sleep_recall", correct: [1, 0, 2])
        case "cartoons.15":
            return makeCartoonRecallSet(prefix: "child_cartoons_emotions_recall", correct: [0, 2, 1])
        default:
            return [
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
    }

    private func makeCartoonRecallSet(prefix: String, correct: [Int]) -> [CartoonRecallQuestion] {
        [
            CartoonRecallQuestion(
                promptKey: "\(prefix)_prompt_1",
                options: [
                    localizationManager.localized("\(prefix)_option_1a"),
                    localizationManager.localized("\(prefix)_option_1b"),
                    localizationManager.localized("\(prefix)_option_1c")
                ],
                correctIndex: correct[0]
            ),
            CartoonRecallQuestion(
                promptKey: "\(prefix)_prompt_2",
                options: [
                    localizationManager.localized("\(prefix)_option_2a"),
                    localizationManager.localized("\(prefix)_option_2b"),
                    localizationManager.localized("\(prefix)_option_2c")
                ],
                correctIndex: correct[1]
            ),
            CartoonRecallQuestion(
                promptKey: "\(prefix)_prompt_3",
                options: [
                    localizationManager.localized("\(prefix)_option_3a"),
                    localizationManager.localized("\(prefix)_option_3b"),
                    localizationManager.localized("\(prefix)_option_3c")
                ],
                correctIndex: correct[2]
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
        switch item.id {
        case "safety.01":
            return makeScenarioSet(prefix: "child_safety_traffic")
        case "safety.15":
            return makeScenarioSet(prefix: "child_safety_psychological")
        case "safety.12":
            return makeScenarioSet(prefix: "child_safety_strangers")
        case "safety.03":
            return makeScenarioSet(prefix: "child_safety_fire")
        case "safety.04":
            return makeScenarioSet(prefix: "child_safety_water")
        case "safety.05":
            return makeScenarioSet(prefix: "child_safety_electric")
        case "safety.06":
            return makeScenarioSet(prefix: "child_safety_nature")
        case "safety.07":
            return makeScenarioSet(prefix: "child_safety_school")
        case "safety.08":
            return makeScenarioSet(prefix: "child_safety_home")
        case "safety.09":
            return makeScenarioSet(prefix: "child_safety_first_aid")
        case "safety.10":
            return makeScenarioSet(prefix: "child_safety_hazard")
        case "safety.11":
            return makeScenarioSet(prefix: "child_safety_public")
        case "safety.13":
            return makeScenarioSet(prefix: "child_safety_emergency")
        case "safety.14":
            return makeScenarioSet(prefix: "child_safety_gadget")
        case "teen_safety.01":
            return makeScenarioSet(prefix: "child_teen_safety_cyber")
        case "teen_safety.02":
            return makeScenarioSet(prefix: "child_teen_safety_data")
        case "teen_safety.03":
            return makeScenarioSet(prefix: "child_teen_safety_social")
        case "teen_safety.07":
            return makeScenarioSet(prefix: "child_teen_safety_psychological")
        case "teen_safety.09":
            return makeScenarioSet(prefix: "child_teen_safety_network")
        case "teen_safety.12":
            return makeScenarioSet(prefix: "child_teen_safety_fraud")
        case "teen_safety.04":
            return makeScenarioSet(prefix: "child_teen_safety_finance")
        case "teen_safety.05":
            return makeScenarioSet(prefix: "child_teen_safety_relationship")
        case "teen_safety.06":
            return makeScenarioSet(prefix: "child_teen_safety_manipulation")
        case "teen_safety.08":
            return makeScenarioSet(prefix: "child_teen_safety_physical")
        case "teen_safety.10":
            return makeScenarioSet(prefix: "child_teen_safety_harmful_content")
        case "teen_safety.11":
            return makeScenarioSet(prefix: "child_teen_safety_online_shopping")
        case "teen_safety.13":
            return makeScenarioSet(prefix: "child_teen_safety_travel")
        case "teen_safety.14":
            return makeScenarioSet(prefix: "child_teen_safety_emergency")
        case "teen_safety.15":
            return makeScenarioSet(prefix: "child_teen_safety_self_defense")
        default:
            return makeScenarioSet(prefix: "child_safety_scenario")
        }
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

    private func makeScenarioSet(prefix: String) -> [SafetyScenario] {
        [
            SafetyScenario(
                promptKey: "\(prefix)_prompt_1",
                choices: [
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_1a"), isSafe: true, feedbackKey: "\(prefix)_feedback_1a"),
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_1b"), isSafe: false, feedbackKey: "\(prefix)_feedback_1b"),
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_1c"), isSafe: false, feedbackKey: "\(prefix)_feedback_1c")
                ]
            ),
            SafetyScenario(
                promptKey: "\(prefix)_prompt_2",
                choices: [
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_2a"), isSafe: false, feedbackKey: "\(prefix)_feedback_2a"),
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_2b"), isSafe: true, feedbackKey: "\(prefix)_feedback_2b"),
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_2c"), isSafe: false, feedbackKey: "\(prefix)_feedback_2c")
                ]
            ),
            SafetyScenario(
                promptKey: "\(prefix)_prompt_3",
                choices: [
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_3a"), isSafe: false, feedbackKey: "\(prefix)_feedback_3a"),
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_3b"), isSafe: true, feedbackKey: "\(prefix)_feedback_3b"),
                    SafetyScenarioChoice(title: localizationManager.localized("\(prefix)_option_3c"), isSafe: false, feedbackKey: "\(prefix)_feedback_3c")
                ]
            )
        ]
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

    private struct StudyQuestionTemplate {
        let promptKey: String
        let optionKeys: [String]
        let correctIndex: Int
    }

    private var specializedLessonPageKeys: [String]? {
        switch item.id {
        case "study.01":
            return ["child_study_russian_page_1", "child_study_russian_page_2", "child_study_russian_page_3"]
        case "study.02":
            return ["child_study_math_page_1", "child_study_math_page_2", "child_study_math_page_3"]
        case "study.03":
            return ["child_study_world_page_1", "child_study_world_page_2", "child_study_world_page_3"]
        case "study.18":
            return ["child_study_informatics_page_1", "child_study_informatics_page_2", "child_study_informatics_page_3"]
        case "study.25":
            return ["child_study_exams_page_1", "child_study_exams_page_2", "child_study_exams_page_3"]
        case "study.28":
            return ["child_study_practice_page_1", "child_study_practice_page_2", "child_study_practice_page_3"]
        case "study.04":
            return ["child_study_history_page_1", "child_study_history_page_2", "child_study_history_page_3"]
        case "study.05":
            return ["child_study_geography_page_1", "child_study_geography_page_2", "child_study_geography_page_3"]
        case "study.06":
            return ["child_study_biology_page_1", "child_study_biology_page_2", "child_study_biology_page_3"]
        case "study.07":
            return ["child_study_physics_page_1", "child_study_physics_page_2", "child_study_physics_page_3"]
        case "study.08":
            return ["child_study_chemistry_page_1", "child_study_chemistry_page_2", "child_study_chemistry_page_3"]
        case "study.09":
            return ["child_study_literature_page_1", "child_study_literature_page_2", "child_study_literature_page_3"]
        case "study.10":
            return ["child_study_art_page_1", "child_study_art_page_2", "child_study_art_page_3"]
        case "study.11":
            return ["child_study_sport_page_1", "child_study_sport_page_2", "child_study_sport_page_3"]
        case "study.12":
            return ["child_study_labor_page_1", "child_study_labor_page_2", "child_study_labor_page_3"]
        case "study.13":
            return ["child_study_social_page_1", "child_study_social_page_2", "child_study_social_page_3"]
        case "study.14":
            return ["child_study_ecology_page_1", "child_study_ecology_page_2", "child_study_ecology_page_3"]
        case "study.15":
            return ["child_study_traffic_page_1", "child_study_traffic_page_2", "child_study_traffic_page_3"]
        case "study.16":
            return ["child_study_health_page_1", "child_study_health_page_2", "child_study_health_page_3"]
        case "study.17":
            return ["child_study_finance_page_1", "child_study_finance_page_2", "child_study_finance_page_3"]
        case "study.19":
            return ["child_study_language_page_1", "child_study_language_page_2", "child_study_language_page_3"]
        case "study.20":
            return ["child_study_creativity_page_1", "child_study_creativity_page_2", "child_study_creativity_page_3"]
        case "study.21":
            return ["child_study_project_page_1", "child_study_project_page_2", "child_study_project_page_3"]
        case "study.22":
            return ["child_study_research_page_1", "child_study_research_page_2", "child_study_research_page_3"]
        case "study.23":
            return ["child_study_groupwork_page_1", "child_study_groupwork_page_2", "child_study_groupwork_page_3"]
        case "study.24":
            return ["child_study_selfwork_page_1", "child_study_selfwork_page_2", "child_study_selfwork_page_3"]
        case "study.27":
            return ["child_study_lab_page_1", "child_study_lab_page_2", "child_study_lab_page_3"]
        case "study.29":
            return ["child_study_creative_project_page_1", "child_study_creative_project_page_2", "child_study_creative_project_page_3"]
        case "study.30":
            return ["child_study_portfolio_page_1", "child_study_portfolio_page_2", "child_study_portfolio_page_3"]
        default:
            return nil
        }
    }

    private var specializedQuestions: [StudyQuestionTemplate]? {
        switch item.id {
        case "study.01":
            return [
                .init(promptKey: "child_study_russian_test_prompt_1", optionKeys: ["child_study_russian_test_option_1a", "child_study_russian_test_option_1b", "child_study_russian_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_russian_test_prompt_2", optionKeys: ["child_study_russian_test_option_2a", "child_study_russian_test_option_2b", "child_study_russian_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_russian_test_prompt_3", optionKeys: ["child_study_russian_test_option_3a", "child_study_russian_test_option_3b", "child_study_russian_test_option_3c"], correctIndex: 2)
            ]
        case "study.02":
            return [
                .init(promptKey: "child_study_math_test_prompt_1", optionKeys: ["child_study_math_test_option_1a", "child_study_math_test_option_1b", "child_study_math_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_math_test_prompt_2", optionKeys: ["child_study_math_test_option_2a", "child_study_math_test_option_2b", "child_study_math_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_math_test_prompt_3", optionKeys: ["child_study_math_test_option_3a", "child_study_math_test_option_3b", "child_study_math_test_option_3c"], correctIndex: 0)
            ]
        case "study.03":
            return [
                .init(promptKey: "child_study_world_test_prompt_1", optionKeys: ["child_study_world_test_option_1a", "child_study_world_test_option_1b", "child_study_world_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_world_test_prompt_2", optionKeys: ["child_study_world_test_option_2a", "child_study_world_test_option_2b", "child_study_world_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_world_test_prompt_3", optionKeys: ["child_study_world_test_option_3a", "child_study_world_test_option_3b", "child_study_world_test_option_3c"], correctIndex: 2)
            ]
        case "study.18":
            return [
                .init(promptKey: "child_study_informatics_test_prompt_1", optionKeys: ["child_study_informatics_test_option_1a", "child_study_informatics_test_option_1b", "child_study_informatics_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_informatics_test_prompt_2", optionKeys: ["child_study_informatics_test_option_2a", "child_study_informatics_test_option_2b", "child_study_informatics_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_informatics_test_prompt_3", optionKeys: ["child_study_informatics_test_option_3a", "child_study_informatics_test_option_3b", "child_study_informatics_test_option_3c"], correctIndex: 1)
            ]
        case "study.25":
            return [
                .init(promptKey: "child_study_exams_test_prompt_1", optionKeys: ["child_study_exams_test_option_1a", "child_study_exams_test_option_1b", "child_study_exams_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_exams_test_prompt_2", optionKeys: ["child_study_exams_test_option_2a", "child_study_exams_test_option_2b", "child_study_exams_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_exams_test_prompt_3", optionKeys: ["child_study_exams_test_option_3a", "child_study_exams_test_option_3b", "child_study_exams_test_option_3c"], correctIndex: 0)
            ]
        case "study.28":
            return [
                .init(promptKey: "child_study_practice_test_prompt_1", optionKeys: ["child_study_practice_test_option_1a", "child_study_practice_test_option_1b", "child_study_practice_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_practice_test_prompt_2", optionKeys: ["child_study_practice_test_option_2a", "child_study_practice_test_option_2b", "child_study_practice_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_practice_test_prompt_3", optionKeys: ["child_study_practice_test_option_3a", "child_study_practice_test_option_3b", "child_study_practice_test_option_3c"], correctIndex: 0)
            ]
        case "study.04":
            return [
                .init(promptKey: "child_study_history_test_prompt_1", optionKeys: ["child_study_history_test_option_1a", "child_study_history_test_option_1b", "child_study_history_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_history_test_prompt_2", optionKeys: ["child_study_history_test_option_2a", "child_study_history_test_option_2b", "child_study_history_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_history_test_prompt_3", optionKeys: ["child_study_history_test_option_3a", "child_study_history_test_option_3b", "child_study_history_test_option_3c"], correctIndex: 2)
            ]
        case "study.05":
            return [
                .init(promptKey: "child_study_geography_test_prompt_1", optionKeys: ["child_study_geography_test_option_1a", "child_study_geography_test_option_1b", "child_study_geography_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_geography_test_prompt_2", optionKeys: ["child_study_geography_test_option_2a", "child_study_geography_test_option_2b", "child_study_geography_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_geography_test_prompt_3", optionKeys: ["child_study_geography_test_option_3a", "child_study_geography_test_option_3b", "child_study_geography_test_option_3c"], correctIndex: 2)
            ]
        case "study.06":
            return [
                .init(promptKey: "child_study_biology_test_prompt_1", optionKeys: ["child_study_biology_test_option_1a", "child_study_biology_test_option_1b", "child_study_biology_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_biology_test_prompt_2", optionKeys: ["child_study_biology_test_option_2a", "child_study_biology_test_option_2b", "child_study_biology_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_biology_test_prompt_3", optionKeys: ["child_study_biology_test_option_3a", "child_study_biology_test_option_3b", "child_study_biology_test_option_3c"], correctIndex: 0)
            ]
        case "study.07":
            return [
                .init(promptKey: "child_study_physics_test_prompt_1", optionKeys: ["child_study_physics_test_option_1a", "child_study_physics_test_option_1b", "child_study_physics_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_physics_test_prompt_2", optionKeys: ["child_study_physics_test_option_2a", "child_study_physics_test_option_2b", "child_study_physics_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_physics_test_prompt_3", optionKeys: ["child_study_physics_test_option_3a", "child_study_physics_test_option_3b", "child_study_physics_test_option_3c"], correctIndex: 1)
            ]
        case "study.08":
            return [
                .init(promptKey: "child_study_chemistry_test_prompt_1", optionKeys: ["child_study_chemistry_test_option_1a", "child_study_chemistry_test_option_1b", "child_study_chemistry_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_chemistry_test_prompt_2", optionKeys: ["child_study_chemistry_test_option_2a", "child_study_chemistry_test_option_2b", "child_study_chemistry_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_chemistry_test_prompt_3", optionKeys: ["child_study_chemistry_test_option_3a", "child_study_chemistry_test_option_3b", "child_study_chemistry_test_option_3c"], correctIndex: 2)
            ]
        case "study.09":
            return [
                .init(promptKey: "child_study_literature_test_prompt_1", optionKeys: ["child_study_literature_test_option_1a", "child_study_literature_test_option_1b", "child_study_literature_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_literature_test_prompt_2", optionKeys: ["child_study_literature_test_option_2a", "child_study_literature_test_option_2b", "child_study_literature_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_literature_test_prompt_3", optionKeys: ["child_study_literature_test_option_3a", "child_study_literature_test_option_3b", "child_study_literature_test_option_3c"], correctIndex: 0)
            ]
        case "study.10":
            return [
                .init(promptKey: "child_study_art_test_prompt_1", optionKeys: ["child_study_art_test_option_1a", "child_study_art_test_option_1b", "child_study_art_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_art_test_prompt_2", optionKeys: ["child_study_art_test_option_2a", "child_study_art_test_option_2b", "child_study_art_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_art_test_prompt_3", optionKeys: ["child_study_art_test_option_3a", "child_study_art_test_option_3b", "child_study_art_test_option_3c"], correctIndex: 2)
            ]
        case "study.11":
            return [
                .init(promptKey: "child_study_sport_test_prompt_1", optionKeys: ["child_study_sport_test_option_1a", "child_study_sport_test_option_1b", "child_study_sport_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_sport_test_prompt_2", optionKeys: ["child_study_sport_test_option_2a", "child_study_sport_test_option_2b", "child_study_sport_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_sport_test_prompt_3", optionKeys: ["child_study_sport_test_option_3a", "child_study_sport_test_option_3b", "child_study_sport_test_option_3c"], correctIndex: 0)
            ]
        case "study.12":
            return [
                .init(promptKey: "child_study_labor_test_prompt_1", optionKeys: ["child_study_labor_test_option_1a", "child_study_labor_test_option_1b", "child_study_labor_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_labor_test_prompt_2", optionKeys: ["child_study_labor_test_option_2a", "child_study_labor_test_option_2b", "child_study_labor_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_labor_test_prompt_3", optionKeys: ["child_study_labor_test_option_3a", "child_study_labor_test_option_3b", "child_study_labor_test_option_3c"], correctIndex: 1)
            ]
        case "study.13":
            return [
                .init(promptKey: "child_study_social_test_prompt_1", optionKeys: ["child_study_social_test_option_1a", "child_study_social_test_option_1b", "child_study_social_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_social_test_prompt_2", optionKeys: ["child_study_social_test_option_2a", "child_study_social_test_option_2b", "child_study_social_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_social_test_prompt_3", optionKeys: ["child_study_social_test_option_3a", "child_study_social_test_option_3b", "child_study_social_test_option_3c"], correctIndex: 2)
            ]
        case "study.14":
            return [
                .init(promptKey: "child_study_ecology_test_prompt_1", optionKeys: ["child_study_ecology_test_option_1a", "child_study_ecology_test_option_1b", "child_study_ecology_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_ecology_test_prompt_2", optionKeys: ["child_study_ecology_test_option_2a", "child_study_ecology_test_option_2b", "child_study_ecology_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_ecology_test_prompt_3", optionKeys: ["child_study_ecology_test_option_3a", "child_study_ecology_test_option_3b", "child_study_ecology_test_option_3c"], correctIndex: 0)
            ]
        case "study.15":
            return [
                .init(promptKey: "child_study_traffic_test_prompt_1", optionKeys: ["child_study_traffic_test_option_1a", "child_study_traffic_test_option_1b", "child_study_traffic_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_traffic_test_prompt_2", optionKeys: ["child_study_traffic_test_option_2a", "child_study_traffic_test_option_2b", "child_study_traffic_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_traffic_test_prompt_3", optionKeys: ["child_study_traffic_test_option_3a", "child_study_traffic_test_option_3b", "child_study_traffic_test_option_3c"], correctIndex: 2)
            ]
        case "study.16":
            return [
                .init(promptKey: "child_study_health_test_prompt_1", optionKeys: ["child_study_health_test_option_1a", "child_study_health_test_option_1b", "child_study_health_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_health_test_prompt_2", optionKeys: ["child_study_health_test_option_2a", "child_study_health_test_option_2b", "child_study_health_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_health_test_prompt_3", optionKeys: ["child_study_health_test_option_3a", "child_study_health_test_option_3b", "child_study_health_test_option_3c"], correctIndex: 1)
            ]
        case "study.17":
            return [
                .init(promptKey: "child_study_finance_test_prompt_1", optionKeys: ["child_study_finance_test_option_1a", "child_study_finance_test_option_1b", "child_study_finance_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_finance_test_prompt_2", optionKeys: ["child_study_finance_test_option_2a", "child_study_finance_test_option_2b", "child_study_finance_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_finance_test_prompt_3", optionKeys: ["child_study_finance_test_option_3a", "child_study_finance_test_option_3b", "child_study_finance_test_option_3c"], correctIndex: 0)
            ]
        case "study.19":
            return [
                .init(promptKey: "child_study_language_test_prompt_1", optionKeys: ["child_study_language_test_option_1a", "child_study_language_test_option_1b", "child_study_language_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_language_test_prompt_2", optionKeys: ["child_study_language_test_option_2a", "child_study_language_test_option_2b", "child_study_language_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_language_test_prompt_3", optionKeys: ["child_study_language_test_option_3a", "child_study_language_test_option_3b", "child_study_language_test_option_3c"], correctIndex: 2)
            ]
        case "study.20":
            return [
                .init(promptKey: "child_study_creativity_test_prompt_1", optionKeys: ["child_study_creativity_test_option_1a", "child_study_creativity_test_option_1b", "child_study_creativity_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_creativity_test_prompt_2", optionKeys: ["child_study_creativity_test_option_2a", "child_study_creativity_test_option_2b", "child_study_creativity_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_creativity_test_prompt_3", optionKeys: ["child_study_creativity_test_option_3a", "child_study_creativity_test_option_3b", "child_study_creativity_test_option_3c"], correctIndex: 1)
            ]
        case "study.21":
            return [
                .init(promptKey: "child_study_project_test_prompt_1", optionKeys: ["child_study_project_test_option_1a", "child_study_project_test_option_1b", "child_study_project_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_project_test_prompt_2", optionKeys: ["child_study_project_test_option_2a", "child_study_project_test_option_2b", "child_study_project_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_project_test_prompt_3", optionKeys: ["child_study_project_test_option_3a", "child_study_project_test_option_3b", "child_study_project_test_option_3c"], correctIndex: 1)
            ]
        case "study.22":
            return [
                .init(promptKey: "child_study_research_test_prompt_1", optionKeys: ["child_study_research_test_option_1a", "child_study_research_test_option_1b", "child_study_research_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_research_test_prompt_2", optionKeys: ["child_study_research_test_option_2a", "child_study_research_test_option_2b", "child_study_research_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_research_test_prompt_3", optionKeys: ["child_study_research_test_option_3a", "child_study_research_test_option_3b", "child_study_research_test_option_3c"], correctIndex: 0)
            ]
        case "study.23":
            return [
                .init(promptKey: "child_study_groupwork_test_prompt_1", optionKeys: ["child_study_groupwork_test_option_1a", "child_study_groupwork_test_option_1b", "child_study_groupwork_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_groupwork_test_prompt_2", optionKeys: ["child_study_groupwork_test_option_2a", "child_study_groupwork_test_option_2b", "child_study_groupwork_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_groupwork_test_prompt_3", optionKeys: ["child_study_groupwork_test_option_3a", "child_study_groupwork_test_option_3b", "child_study_groupwork_test_option_3c"], correctIndex: 2)
            ]
        case "study.24":
            return [
                .init(promptKey: "child_study_selfwork_test_prompt_1", optionKeys: ["child_study_selfwork_test_option_1a", "child_study_selfwork_test_option_1b", "child_study_selfwork_test_option_1c"], correctIndex: 2),
                .init(promptKey: "child_study_selfwork_test_prompt_2", optionKeys: ["child_study_selfwork_test_option_2a", "child_study_selfwork_test_option_2b", "child_study_selfwork_test_option_2c"], correctIndex: 1),
                .init(promptKey: "child_study_selfwork_test_prompt_3", optionKeys: ["child_study_selfwork_test_option_3a", "child_study_selfwork_test_option_3b", "child_study_selfwork_test_option_3c"], correctIndex: 0)
            ]
        case "study.27":
            return [
                .init(promptKey: "child_study_lab_test_prompt_1", optionKeys: ["child_study_lab_test_option_1a", "child_study_lab_test_option_1b", "child_study_lab_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_lab_test_prompt_2", optionKeys: ["child_study_lab_test_option_2a", "child_study_lab_test_option_2b", "child_study_lab_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_lab_test_prompt_3", optionKeys: ["child_study_lab_test_option_3a", "child_study_lab_test_option_3b", "child_study_lab_test_option_3c"], correctIndex: 2)
            ]
        case "study.29":
            return [
                .init(promptKey: "child_study_creative_project_test_prompt_1", optionKeys: ["child_study_creative_project_test_option_1a", "child_study_creative_project_test_option_1b", "child_study_creative_project_test_option_1c"], correctIndex: 0),
                .init(promptKey: "child_study_creative_project_test_prompt_2", optionKeys: ["child_study_creative_project_test_option_2a", "child_study_creative_project_test_option_2b", "child_study_creative_project_test_option_2c"], correctIndex: 2),
                .init(promptKey: "child_study_creative_project_test_prompt_3", optionKeys: ["child_study_creative_project_test_option_3a", "child_study_creative_project_test_option_3b", "child_study_creative_project_test_option_3c"], correctIndex: 1)
            ]
        case "study.30":
            return [
                .init(promptKey: "child_study_portfolio_test_prompt_1", optionKeys: ["child_study_portfolio_test_option_1a", "child_study_portfolio_test_option_1b", "child_study_portfolio_test_option_1c"], correctIndex: 1),
                .init(promptKey: "child_study_portfolio_test_prompt_2", optionKeys: ["child_study_portfolio_test_option_2a", "child_study_portfolio_test_option_2b", "child_study_portfolio_test_option_2c"], correctIndex: 0),
                .init(promptKey: "child_study_portfolio_test_prompt_3", optionKeys: ["child_study_portfolio_test_option_3a", "child_study_portfolio_test_option_3b", "child_study_portfolio_test_option_3c"], correctIndex: 2)
            ]
        default:
            return nil
        }
    }

    private var lessonPages: [String] {
        if let specializedLessonPageKeys {
            return specializedLessonPageKeys.map { localizationManager.localized($0) }
        }
        return [
            localizationManager.localized("child_study_lesson_page_1"),
            localizationManager.localized("child_study_lesson_page_2"),
            localizationManager.localized("child_study_lesson_page_3")
        ]
    }

    private var questions: [StudyQuestion] {
        if let specializedQuestions {
            return specializedQuestions.map { template in
                StudyQuestion(
                    prompt: localizationManager.localized(template.promptKey),
                    options: template.optionKeys.map { localizationManager.localized($0) },
                    correctIndex: template.correctIndex
                )
            }
        }
        return [
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

private struct GamesChallengeTemplate {
    let promptKey: String
    let optionKeys: [String]
    let correctIndex: Int
    let hintKey: String
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
    @State private var subjectQuizIndex: Int = 0
    @State private var subjectQuizScore: Int = 0
    @State private var subjectQuizSelected: Int?
    @State private var memorySequence: [Int] = []
    @State private var memoryGuess: [Int] = []
    @State private var memoryRound: Int = 1
    @State private var memorySolvedRounds: Int = 0
    @State private var memoryFeedbackKey: String?
    @State private var speedRound: Int = 1
    @State private var speedTarget: Int = Int.random(in: 1...9)
    @State private var speedScore: Int = 0
    @State private var teamTaskIndex: Int = 0
    @State private var teamHelpCount: Int = 0
    @State private var strategyStep: Int = 0
    @State private var strategyPlan: [String] = []
    @State private var sportDistance: Double = 0
    @State private var boardPosition: Int = 0
    @State private var boardRoll: Int = 0
    @State private var cardPairTarget: Int = Int.random(in: 1...6)
    @State private var cardScore: Int = 0
    @State private var arcadeCoins: Int = 0
    @State private var arcadeLives: Int = 3
    @State private var platformDistance: Int = 0
    @State private var raceProgress: Double = 0
    @State private var craftResources: Int = 0
    @State private var farmAnimalsFed: Int = 0
    @State private var sciencePoints: Int = 0
    @State private var mapProgress: Int = 0
    @State private var musicCombo: Int = 0

    private var specializedChallengePrefix: String? {
        switch item.id {
        case "games.01":
            return "child_games_math_focus"
        case "games.02":
            return "child_games_language_focus"
        case "games.09":
            return "child_games_adventure_quest"
        default:
            return nil
        }
    }

    private var specializedChallengeTitleKey: String? {
        guard let prefix = specializedChallengePrefix else { return nil }
        return "\(prefix)_title"
    }

    private var specializedChallengeTemplates: [GamesChallengeTemplate]? {
        guard let prefix = specializedChallengePrefix else { return nil }
        return [
            .init(
                promptKey: "\(prefix)_prompt_1",
                optionKeys: ["\(prefix)_option_1a", "\(prefix)_option_1b", "\(prefix)_option_1c"],
                correctIndex: 0,
                hintKey: "\(prefix)_hint_1"
            ),
            .init(
                promptKey: "\(prefix)_prompt_2",
                optionKeys: ["\(prefix)_option_2a", "\(prefix)_option_2b", "\(prefix)_option_2c"],
                correctIndex: 1,
                hintKey: "\(prefix)_hint_2"
            ),
            .init(
                promptKey: "\(prefix)_prompt_3",
                optionKeys: ["\(prefix)_option_3a", "\(prefix)_option_3b", "\(prefix)_option_3c"],
                correctIndex: 2,
                hintKey: "\(prefix)_hint_3"
            )
        ]
    }

    private var tasks: [GamesChallengeTask] {
        if let specializedChallengeTemplates {
            return specializedChallengeTemplates.map { template in
                GamesChallengeTask(
                    prompt: localizationManager.localized(template.promptKey),
                    options: template.optionKeys.map { localizationManager.localized($0) },
                    correctIndex: template.correctIndex,
                    hint: localizationManager.localized(template.hintKey)
                )
            }
        }
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

    private var isSubjectQuiz: Bool { item.id == "games.04" }
    private var isMemoryTraining: Bool { item.id == "games.05" }
    private var isSpeedGame: Bool { item.id == "games.06" }
    private var isTeamGame: Bool { item.id == "games.07" }
    private var isStrategyGame: Bool { item.id == "games.08" }
    private var isSportGame: Bool { item.id == "games.10" }
    private var isBoardGame: Bool { item.id == "games.11" }
    private var isCardGame: Bool { item.id == "games.12" }
    private var isArcadeGame: Bool { item.id == "games.13" }
    private var isPlatformGame: Bool { item.id == "games.14" }
    private var isRaceGame: Bool { item.id == "games.15" }
    private var isCraftGame: Bool { item.id == "games.16" }
    private var isFarmGame: Bool { item.id == "games.17" }
    private var isScienceGame: Bool { item.id == "games.18" }
    private var isHistoryGeoGame: Bool { item.id == "games.19" }
    private var isMusicGame: Bool { item.id == "games.20" }

    var body: some View {
        Group {
            if isSubjectQuiz {
                subjectQuizCard
            } else if isMemoryTraining {
                memoryCard
            } else if isSpeedGame {
                speedCard
            } else if isTeamGame {
                teamCard
            } else if isStrategyGame {
                strategyCard
            } else if isSportGame {
                sportCard
            } else if isBoardGame {
                boardCard
            } else if isCardGame {
                cardCard
            } else if isArcadeGame {
                arcadeCard
            } else if isPlatformGame {
                platformCard
            } else if isRaceGame {
                raceCard
            } else if isCraftGame {
                craftCard
            } else if isFarmGame {
                farmCard
            } else if isScienceGame {
                scienceCard
            } else if isHistoryGeoGame {
                historyGeoCard
            } else if isMusicGame {
                musicCard
            } else {
                challengeCard
            }
        }
    }

    private var challengeCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_challenge_title"))
                .font(.system(size: 17, weight: .bold))

            if let specializedChallengeTitleKey {
                Text(localizationManager.localized(specializedChallengeTitleKey))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)
            } else {
                Picker("", selection: $domain) {
                    Text(localizationManager.localized("child_games_challenge_domain_math")).tag(GamesChallengeDomain.math)
                    Text(localizationManager.localized("child_games_challenge_domain_language")).tag(GamesChallengeDomain.language)
                }
                .pickerStyle(.segmented)
                .onChange(of: domain) { _ in
                    resetChallenge()
                }
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

    private var subjectQuizTasks: [GamesChallengeTask] {
        [
            GamesChallengeTask(
                prompt: localizationManager.localized("child_games_subject_quiz_prompt_1"),
                options: [
                    localizationManager.localized("child_games_subject_quiz_option_math"),
                    localizationManager.localized("child_games_subject_quiz_option_music"),
                    localizationManager.localized("child_games_subject_quiz_option_dance")
                ],
                correctIndex: 0,
                hint: localizationManager.localized("child_games_subject_quiz_hint_1")
            ),
            GamesChallengeTask(
                prompt: localizationManager.localized("child_games_subject_quiz_prompt_2"),
                options: [
                    localizationManager.localized("child_games_subject_quiz_option_wolf"),
                    localizationManager.localized("child_games_subject_quiz_option_fox"),
                    localizationManager.localized("child_games_subject_quiz_option_cow")
                ],
                correctIndex: 1,
                hint: localizationManager.localized("child_games_subject_quiz_hint_2")
            ),
            GamesChallengeTask(
                prompt: localizationManager.localized("child_games_subject_quiz_prompt_3"),
                options: [
                    localizationManager.localized("child_games_subject_quiz_option_north"),
                    localizationManager.localized("child_games_subject_quiz_option_south"),
                    localizationManager.localized("child_games_subject_quiz_option_west")
                ],
                correctIndex: 0,
                hint: localizationManager.localized("child_games_subject_quiz_hint_3")
            )
        ]
    }

    private var activeSubjectQuizTask: GamesChallengeTask {
        subjectQuizTasks[min(subjectQuizIndex, subjectQuizTasks.count - 1)]
    }

    private var subjectQuizCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_subject_quiz_title"))
                .font(.system(size: 17, weight: .bold))
            Text(activeSubjectQuizTask.prompt)
                .font(.system(size: 15, weight: .semibold))
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.orange.opacity(0.1)))
            ForEach(Array(activeSubjectQuizTask.options.enumerated()), id: \.offset) { index, option in
                Button(option) {
                    guard subjectQuizSelected == nil else { return }
                    subjectQuizSelected = index
                    if index == activeSubjectQuizTask.correctIndex {
                        subjectQuizScore += 1
                    }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
                        if subjectQuizIndex < subjectQuizTasks.count - 1 {
                            subjectQuizIndex += 1
                            subjectQuizSelected = nil
                        }
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(subjectQuizSelected != nil)
            }
            Text("\(localizationManager.localized("child_games_subject_quiz_score")): \(subjectQuizScore)/\(subjectQuizTasks.count)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            if subjectQuizIndex >= subjectQuizTasks.count - 1, subjectQuizSelected != nil {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var memoryCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_memory_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_memory_round")) \(memoryRound)")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)
            if !memorySequence.isEmpty {
                Text(memorySequence.map(String.init).joined(separator: " • "))
                    .font(.system(size: 20, weight: .bold))
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(8)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.1)))
            }
            HStack {
                ForEach(Array(1...4), id: \.self) { n in
                    Button("\(n)") { appendMemoryGuess(n) }
                        .buttonStyle(.bordered)
                }
            }
            if let memoryFeedbackKey {
                Text(localizationManager.localized(memoryFeedbackKey))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(memoryFeedbackKey.contains("ok") ? .green : .orange)
            }
            Button(localizationManager.localized("child_games_memory_next")) {
                startMemoryRound()
            }
            .buttonStyle(.bordered)
            if memorySolvedRounds >= 3 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onAppear {
            if memorySequence.isEmpty {
                startMemoryRound()
            }
        }
    }

    private var speedCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_speed_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_speed_round")) \(speedRound)")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)
            Text("\(localizationManager.localized("child_games_speed_target")): \(speedTarget)")
                .font(.system(size: 26, weight: .bold))
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(8)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.red.opacity(0.1)))
            HStack {
                ForEach(Array(1...9), id: \.self) { number in
                    Button("\(number)") {
                        if number == speedTarget {
                            speedScore += 1
                            speedRound += 1
                            speedTarget = Int.random(in: 1...9)
                        }
                    }
                    .buttonStyle(.bordered)
                }
            }
            Text("\(localizationManager.localized("child_games_speed_score")): \(speedScore)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            if speedScore >= 5 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var teamTasks: [String] {
        [
            localizationManager.localized("child_games_team_task_1"),
            localizationManager.localized("child_games_team_task_2"),
            localizationManager.localized("child_games_team_task_3")
        ]
    }

    private var teamCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_team_title"))
                .font(.system(size: 17, weight: .bold))
            Text(teamTasks[min(teamTaskIndex, teamTasks.count - 1)])
                .font(.system(size: 15, weight: .semibold))
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.green.opacity(0.1)))
            HStack(spacing: 10) {
                Button(localizationManager.localized("child_games_team_help")) {
                    teamHelpCount += 1
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_games_team_next")) {
                    if teamTaskIndex < teamTasks.count - 1 {
                        teamTaskIndex += 1
                    }
                }
                .buttonStyle(.bordered)
            }
            Text("\(localizationManager.localized("child_games_team_score")): \(teamHelpCount)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            if teamTaskIndex >= teamTasks.count - 1, teamHelpCount >= 2 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var strategyCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_strategy_title"))
                .font(.system(size: 17, weight: .bold))
            Text(localizationManager.localized("child_games_strategy_goal"))
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                Button(localizationManager.localized("child_games_strategy_step_scout")) {
                    appendStrategyStep("scout")
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_games_strategy_step_build")) {
                    appendStrategyStep("build")
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_games_strategy_step_defend")) {
                    appendStrategyStep("defend")
                }
                .buttonStyle(.bordered)
            }
            Text(strategyPlan.joined(separator: " → "))
                .font(.system(size: 13, weight: .semibold))
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(8)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.purple.opacity(0.08)))
            if strategyStep >= 3 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var sportCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_sport_title"))
                .font(.system(size: 17, weight: .bold))
            ProgressView(value: sportDistance, total: 100)
                .tint(.blue)
            Text("\(localizationManager.localized("child_games_sport_distance")): \(Int(sportDistance))/100")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_games_sport_run")) {
                sportDistance = min(100, sportDistance + 20)
            }
            .buttonStyle(.borderedProminent)
            if sportDistance >= 100 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var boardCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_board_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_board_position")): \(boardPosition)")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)
            Text("\(localizationManager.localized("child_games_board_last_roll")): \(boardRoll)")
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_games_board_roll")) {
                boardRoll = Int.random(in: 1...6)
                boardPosition = min(20, boardPosition + boardRoll)
            }
            .buttonStyle(.borderedProminent)
            if boardPosition >= 20 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var cardCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_card_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_card_target")): \(cardPairTarget)")
                .font(.system(size: 18, weight: .semibold))
            HStack {
                ForEach(Array(1...6), id: \.self) { number in
                    Button("\(number)") {
                        if number == cardPairTarget {
                            cardScore += 1
                            cardPairTarget = Int.random(in: 1...6)
                        }
                    }
                    .buttonStyle(.bordered)
                }
            }
            Text("\(localizationManager.localized("child_games_card_score")): \(cardScore)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            if cardScore >= 5 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var arcadeCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_arcade_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_arcade_coins")): \(arcadeCoins)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Text("\(localizationManager.localized("child_games_arcade_lives")): \(arcadeLives)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            HStack(spacing: 10) {
                Button(localizationManager.localized("child_games_arcade_jump")) {
                    arcadeCoins += 1
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_games_arcade_avoid")) {
                    arcadeLives = max(0, arcadeLives - 1)
                }
                .buttonStyle(.bordered)
            }
            if arcadeCoins >= 8 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var platformCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_platform_title"))
                .font(.system(size: 17, weight: .bold))
            ProgressView(value: Double(platformDistance), total: 10)
                .tint(.mint)
            Text("\(localizationManager.localized("child_games_platform_distance")): \(platformDistance)/10")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_games_platform_move")) {
                platformDistance = min(10, platformDistance + 1)
            }
            .buttonStyle(.borderedProminent)
            if platformDistance >= 10 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var raceCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_race_title"))
                .font(.system(size: 17, weight: .bold))
            ProgressView(value: raceProgress, total: 100)
                .tint(.orange)
            Text("\(localizationManager.localized("child_games_race_progress")): \(Int(raceProgress))%")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_games_race_accelerate")) {
                raceProgress = min(100, raceProgress + Double(Int.random(in: 12...25)))
            }
            .buttonStyle(.borderedProminent)
            if raceProgress >= 100 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var craftCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_craft_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_craft_resources")): \(craftResources)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            HStack(spacing: 10) {
                Button(localizationManager.localized("child_games_craft_collect")) {
                    craftResources = min(12, craftResources + 2)
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_games_craft_build")) {
                    craftResources = max(0, craftResources - 3)
                }
                .buttonStyle(.bordered)
            }
            if craftResources >= 10 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var farmCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_farm_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_farm_fed")): \(farmAnimalsFed)/5")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_games_farm_feed")) {
                farmAnimalsFed = min(5, farmAnimalsFed + 1)
            }
            .buttonStyle(.borderedProminent)
            if farmAnimalsFed >= 5 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var scienceCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_science_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_science_points")): \(sciencePoints)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            HStack(spacing: 10) {
                Button(localizationManager.localized("child_games_science_space")) {
                    sciencePoints += 2
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_games_science_lab")) {
                    sciencePoints += 3
                }
                .buttonStyle(.bordered)
            }
            if sciencePoints >= 12 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var historyGeoCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_history_geo_title"))
                .font(.system(size: 17, weight: .bold))
            ProgressView(value: Double(mapProgress), total: 6)
                .tint(.indigo)
            Text("\(localizationManager.localized("child_games_history_geo_progress")): \(mapProgress)/6")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_games_history_geo_explore")) {
                mapProgress = min(6, mapProgress + 1)
            }
            .buttonStyle(.borderedProminent)
            if mapProgress >= 6 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
    }

    private var musicCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_games_music_title"))
                .font(.system(size: 17, weight: .bold))
            Text("\(localizationManager.localized("child_games_music_combo")): \(musicCombo)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            HStack(spacing: 10) {
                Button("♪") { musicCombo += 1 }
                    .buttonStyle(.bordered)
                Button("♫") { musicCombo += 1 }
                    .buttonStyle(.bordered)
                Button("♬") { musicCombo += 1 }
                    .buttonStyle(.bordered)
            }
            if musicCombo >= 7 {
                Button(localizationManager.localized("child_interface_done")) {
                    Task { await onComplete() }
                }
                .buttonStyle(.borderedProminent)
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

    private func startMemoryRound() {
        let count = min(2 + memoryRound, 5)
        memorySequence = (0..<count).map { _ in Int.random(in: 1...4) }
        memoryGuess = []
        memoryFeedbackKey = nil
    }

    private func appendMemoryGuess(_ value: Int) {
        guard memorySolvedRounds < 3 else { return }
        guard memoryGuess.count < memorySequence.count else { return }
        memoryGuess.append(value)
        if memoryGuess.count == memorySequence.count {
            if memoryGuess == memorySequence {
                memorySolvedRounds += 1
                memoryRound += 1
                memoryFeedbackKey = "child_games_memory_feedback_ok"
            } else {
                memoryFeedbackKey = "child_games_memory_feedback_retry"
            }
        }
    }

    private func appendStrategyStep(_ step: String) {
        guard strategyStep < 3 else { return }
        strategyPlan.append(step)
        strategyStep += 1
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
    @State private var narratorIndex: Int = 0
    @State private var readingTempo: String = "normal"
    @State private var bookmarks: Set<String> = []
    @State private var quizChoiceIndex: Int?
    @State private var quizAnswered = false
    @State private var quizCorrect = false

    private struct NarratorProfile: Identifiable {
        let id: Int
        let name: String
        let localeCode: String
    }

    private var narrators: [NarratorProfile] {
        [
            .init(id: 0, name: localizationManager.localized("child_story_narrator_actor_anna"), localeCode: "ru-RU"),
            .init(id: 1, name: localizationManager.localized("child_story_narrator_actor_ivan"), localeCode: "ru-RU"),
            .init(id: 2, name: localizationManager.localized("child_story_narrator_actor_elena"), localeCode: "ru-RU")
        ]
    }

    private var stories: [InteractiveStory] {
        [
            makeForestStory(),
            makeRobotStory(),
            makeKindnessStory(),
            makeStarStory(),
            makeLibraryStory(),
            makeKolobokStory(),
            makeAnimalTalesStory(),
            makeMagicStory(),
            makeWorldTalesStory(),
            makeModernStory()
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

            HStack(spacing: 8) {
                Text(localizationManager.localized("child_story_tempo_label"))
                    .font(.system(size: 13, weight: .semibold))
                Picker("", selection: $readingTempo) {
                    Text(localizationManager.localized("child_story_tempo_slow")).tag("slow")
                    Text(localizationManager.localized("child_story_tempo_normal")).tag("normal")
                    Text(localizationManager.localized("child_story_tempo_fast")).tag("fast")
                }
                .pickerStyle(.segmented)
            }

            HStack(spacing: 8) {
                Text(localizationManager.localized("child_story_voice_actor_label"))
                    .font(.system(size: 13, weight: .semibold))
                Picker("", selection: $narratorIndex) {
                    ForEach(narrators) { n in
                        Text(n.name).tag(n.id)
                    }
                }
                .pickerStyle(.menu)
            }

            ProgressView(value: checkpointProgress)
                .tint(.indigo)

            Text(page.narration)
                .font(.system(size: 16, weight: .regular))
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))

            Button(localizationManager.localized("child_game_welcome")) {
                narrationCount += 1
                let actor = narrators.first(where: { $0.id == narratorIndex }) ?? narrators[0]
                SoundEffectPlayer.shared.playVoicePrompt(
                    narratedTextWithTempo(page.narration),
                    languageCode: actor.localeCode,
                    priority: .high
                )
                MasterLogger.shared.business("P2-104 narration played contentId=\(item.id) story=\(story.id) page=\(page.id) count=\(narrationCount) tempo=\(readingTempo)")
            }
            .buttonStyle(.bordered)

            HStack(spacing: 10) {
                Button(
                    isBookmarkedCurrentPage
                    ? localizationManager.localized("child_story_bookmark_remove")
                    : localizationManager.localized("child_story_bookmark_add")
                ) {
                    toggleBookmarkCurrentPage()
                }
                .buttonStyle(.bordered)
                if !bookmarks.isEmpty {
                    Menu(localizationManager.localized("child_story_bookmark_open")) {
                        ForEach(Array(bookmarks).sorted(), id: \.self) { mark in
                            Button(mark) {
                                if let pageKey = mark.components(separatedBy: ":").last {
                                    pageId = pageKey
                                }
                            }
                        }
                    }
                }
            }

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
                storyQuizCard
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
            quizChoiceIndex = nil
            quizAnswered = false
            quizCorrect = false
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
        narratorIndex = 0
        readingTempo = "normal"
        bookmarks = []
        quizChoiceIndex = nil
        quizAnswered = false
        quizCorrect = false
        captureCheckpointIfNeeded(page)
    }

    private func captureCheckpointIfNeeded(_ currentPage: StoryPage) {
        if let checkpoint = currentPage.checkpointId {
            reachedCheckpoints.insert(checkpoint)
        }
    }

    private var quizAnswers: [String] {
        [
            localizationManager.localized("child_story_quiz_answer_help"),
            localizationManager.localized("child_story_quiz_answer_ignore"),
            localizationManager.localized("child_story_quiz_answer_laugh")
        ]
    }

    private var correctQuizIndex: Int { 0 }

    private var isBookmarkedCurrentPage: Bool {
        bookmarks.contains("\(story.id):\(page.id)")
    }

    private func toggleBookmarkCurrentPage() {
        let key = "\(story.id):\(page.id)"
        if bookmarks.contains(key) {
            bookmarks.remove(key)
        } else {
            bookmarks.insert(key)
        }
    }

    private func narratedTextWithTempo(_ text: String) -> String {
        switch readingTempo {
        case "slow": return text.replacingOccurrences(of: " ", with: "  ")
        case "fast": return text
        default: return text
        }
    }

    private var storyQuizCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_story_quiz_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_story_quiz_question"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
            ForEach(Array(quizAnswers.enumerated()), id: \.offset) { idx, title in
                Button {
                    quizChoiceIndex = idx
                    quizAnswered = true
                    quizCorrect = (idx == correctQuizIndex)
                } label: {
                    Text(title)
                        .font(.system(size: 13, weight: .semibold))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 8)
                        .padding(.horizontal, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill((quizChoiceIndex == idx) ? Color.indigo.opacity(0.2) : Color(.secondarySystemBackground))
                        )
                }
                .buttonStyle(.plain)
            }
            if quizAnswered {
                Text(localizationManager.localized(quizCorrect ? "child_story_quiz_feedback_ok" : "child_story_quiz_feedback_retry"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(quizCorrect ? .green : .orange)
            }
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.06)))
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

private func makeKolobokStory() -> InteractiveStory {
    InteractiveStory(
        id: "kolobok",
        title: "Колобок",
        pages: [
            StoryPage(
                id: "start",
                narration: "Колобок покатился по дорожке и встретил зайца.",
                choices: [
                    StoryChoice(title: "Спеть песенку", nextPageId: "song", checkpointId: "c1"),
                    StoryChoice(title: "Убежать быстрее", nextPageId: "road", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "song",
                narration: "Колобок спел весёлую песенку и покатился дальше.",
                choices: [StoryChoice(title: "К медведю", nextPageId: "bear", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "road",
                narration: "На дорожке Колобок встретил медведя, который хотел дружить.",
                choices: [StoryChoice(title: "Поговорить с медведем", nextPageId: "bear", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "bear",
                narration: "Медведь показал короткую тропинку к дому бабушки и дедушки.",
                choices: [StoryChoice(title: "Вернуться домой", nextPageId: "ending", checkpointId: "c3")],
                checkpointId: "c2",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Колобок вернулся домой и рассказал о своих приключениях.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeAnimalTalesStory() -> InteractiveStory {
    InteractiveStory(
        id: "animal_tales",
        title: "Сказки про животных",
        pages: [
            StoryPage(
                id: "start",
                narration: "Лисёнок и бельчонок решили помочь птицам найти зёрнышки.",
                choices: [
                    StoryChoice(title: "Идти к поляне", nextPageId: "field", checkpointId: "c1"),
                    StoryChoice(title: "Проверить у реки", nextPageId: "river", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "field",
                narration: "На поляне друзья нашли мешочек с зёрнами.",
                choices: [StoryChoice(title: "Позвать птиц", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "river",
                narration: "У реки бобр подсказал, где лежит мешочек с едой.",
                choices: [StoryChoice(title: "Позвать птиц", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Птицы поблагодарили друзей, и все вместе устроили праздник.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeMagicStory() -> InteractiveStory {
    InteractiveStory(
        id: "magic_story",
        title: "Волшебные истории",
        pages: [
            StoryPage(
                id: "start",
                narration: "Ночью в саду зажглись светлячки и открыли путь к волшебному дереву.",
                choices: [
                    StoryChoice(title: "Подойти к дереву", nextPageId: "tree", checkpointId: "c1"),
                    StoryChoice(title: "Попросить совета у феи", nextPageId: "fairy", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "tree",
                narration: "На дереве висел фонарик желаний. Нужно назвать доброе дело.",
                choices: [StoryChoice(title: "Загадать доброе желание", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "fairy",
                narration: "Фея подсказала: волшебство работает, когда мы помогаем другим.",
                choices: [StoryChoice(title: "Сделать доброе дело", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Сад засиял ярче, а друзья получили волшебные значки доброты.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeWorldTalesStory() -> InteractiveStory {
    InteractiveStory(
        id: "world_tales",
        title: "Сказки разных народов",
        pages: [
            StoryPage(
                id: "start",
                narration: "Дети нашли карту мира, где каждая страна прятала сказочную историю.",
                choices: [
                    StoryChoice(title: "Выбрать северную страну", nextPageId: "north", checkpointId: "c1"),
                    StoryChoice(title: "Выбрать южную страну", nextPageId: "south", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "north",
                narration: "На севере их встретил олень и рассказал легенду о храбром путешественнике.",
                choices: [StoryChoice(title: "Продолжить путь", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "south",
                narration: "На юге мудрая черепаха поделилась историей о дружбе и терпении.",
                choices: [StoryChoice(title: "Продолжить путь", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Вернувшись домой, дети собрали книгу сказок народов мира.",
                choices: [],
                checkpointId: "c3",
                isEnding: true
            )
        ],
        startPageId: "start"
    )
}

private func makeModernStory() -> InteractiveStory {
    InteractiveStory(
        id: "modern_story",
        title: "Современные сказки",
        pages: [
            StoryPage(
                id: "start",
                narration: "Робот Ри помогал ребятам в умном городе и искал потерянный дрон.",
                choices: [
                    StoryChoice(title: "Проверить парк", nextPageId: "park", checkpointId: "c1"),
                    StoryChoice(title: "Проверить школьный двор", nextPageId: "school", checkpointId: "c1")
                ],
                checkpointId: "c0",
                isEnding: false
            ),
            StoryPage(
                id: "park",
                narration: "В парке дрон запутался в ветках, и друзья аккуратно его освободили.",
                choices: [StoryChoice(title: "Вернуть дрон владельцу", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "school",
                narration: "Во дворе дрон подал сигнал, и ребята нашли его по карте.",
                choices: [StoryChoice(title: "Вернуть дрон владельцу", nextPageId: "ending", checkpointId: "c2")],
                checkpointId: "c1",
                isEnding: false
            ),
            StoryPage(
                id: "ending",
                narration: "Дрон снова летал, а робот Ри получил звание лучшего помощника.",
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
    let category: String
    let topics: [String]
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
    @State private var selectedCategory: String = "learning"
    @State private var accompanimentOn = true
    @State private var accompanimentLevel: Double = 0.65
    @State private var selectedTopic: String = "all"
    @State private var favoriteTitles: Set<String> = []
    @State private var favoritesLoaded = false
    private let ticker = Timer.publish(every: 0.35, on: .main, in: .common).autoconnect()

    private var tracks: [KaraokeTrack] {
        [
            KaraokeTrack(
                title: "Солнечный день",
                artist: "ALADDIN Kids",
                category: "play",
                topics: ["seasons"],
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
                category: "learning",
                topics: ["letters"],
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
                category: "learning",
                topics: ["numbers"],
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
                category: "lullaby",
                topics: ["friendship"],
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
                category: "play",
                topics: ["space"],
                lines: [
                    .init(startSec: 0, endSec: 3, text: "В небе звёзды ярко так горят"),
                    .init(startSec: 3, endSec: 7, text: "Наши голоса в один момент звучат"),
                    .init(startSec: 7, endSec: 11, text: "Пой со мной, держи весёлый такт"),
                    .init(startSec: 11, endSec: 15, text: "Музыка ведёт нас в новый старт")
                ]
            ),
            KaraokeTrack(
                title: "Цветные краски",
                artist: "ALADDIN Kids",
                category: "learning",
                topics: ["colors"],
                lines: [
                    .init(startSec: 0, endSec: 3, text: "Красный, синий, жёлтый свет"),
                    .init(startSec: 3, endSec: 7, text: "Каждый цвет нам шлёт привет"),
                    .init(startSec: 7, endSec: 11, text: "Зелёный лист и неба синь"),
                    .init(startSec: 11, endSec: 15, text: "Пой про краски и запомни")
                ]
            ),
            KaraokeTrack(
                title: "Зверята поют",
                artist: "ALADDIN Kids",
                category: "play",
                topics: ["animals"],
                lines: [
                    .init(startSec: 0, endSec: 3, text: "Кот мурлычет, пёс зовёт"),
                    .init(startSec: 3, endSec: 7, text: "Утка крякает, корова поёт"),
                    .init(startSec: 7, endSec: 11, text: "Вместе звери дружно в ряд"),
                    .init(startSec: 11, endSec: 15, text: "Песню дарят для ребят")
                ]
            ),
            KaraokeTrack(
                title: "Четыре времени года",
                artist: "ALADDIN Kids",
                category: "learning",
                topics: ["seasons"],
                lines: [
                    .init(startSec: 0, endSec: 3, text: "Весна пришла и тает лёд"),
                    .init(startSec: 3, endSec: 7, text: "Лето солнце в гости ждёт"),
                    .init(startSec: 7, endSec: 11, text: "Осень листьями кружит"),
                    .init(startSec: 11, endSec: 15, text: "Зима снежинками блестит")
                ]
            ),
            KaraokeTrack(
                title: "Песня про дружбу",
                artist: "ALADDIN Kids",
                category: "play",
                topics: ["friendship"],
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Если рядом друг, улыбка ярче"),
                    .init(startSec: 4, endSec: 8, text: "Вместе мы решим любую задачу"),
                    .init(startSec: 8, endSec: 12, text: "Поделись добром, протяни ладонь"),
                    .init(startSec: 12, endSec: 16, text: "Дружба нас ведёт в весёлый день")
                ]
            ),
            KaraokeTrack(
                title: "Песня про здоровье",
                artist: "ALADDIN Kids",
                category: "learning",
                topics: ["health"],
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Чистим зубы утром, моем руки"),
                    .init(startSec: 4, endSec: 8, text: "Фрукты и зарядка без разлуки"),
                    .init(startSec: 8, endSec: 12, text: "Сильным быть поможет каждый день"),
                    .init(startSec: 12, endSec: 16, text: "Здоровый ритм нам дарит вдохновенье")
                ]
            ),
            KaraokeTrack(
                title: "Народные песенки",
                artist: "ALADDIN Folk",
                category: "lullaby",
                topics: ["folk"],
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Во поле берёзка тихо пела"),
                    .init(startSec: 4, endSec: 8, text: "Колыбельный ветер к нам летел"),
                    .init(startSec: 8, endSec: 12, text: "Сохраним напевы старины"),
                    .init(startSec: 12, endSec: 16, text: "Пусть звучат народные мотивы")
                ]
            ),
            KaraokeTrack(
                title: "Современные детские песни",
                artist: "ALADDIN Pop Kids",
                category: "play",
                topics: ["modern"],
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Ритм в наушниках зовёт играть"),
                    .init(startSec: 4, endSec: 8, text: "Танец света будет помогать"),
                    .init(startSec: 8, endSec: 12, text: "Новый день и новый яркий бит"),
                    .init(startSec: 12, endSec: 16, text: "Современный трек для всех звучит")
                ]
            ),
            KaraokeTrack(
                title: "Песни разных стран",
                artist: "ALADDIN World Kids",
                category: "learning",
                topics: ["countries"],
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Bonjour, hola, hello — поём"),
                    .init(startSec: 4, endSec: 8, text: "Дружбу между странами найдём"),
                    .init(startSec: 8, endSec: 12, text: "Пусть мелодии летят вокруг"),
                    .init(startSec: 12, endSec: 16, text: "Музыка объединяет всех друзей")
                ]
            ),
            KaraokeTrack(
                title: "Ритмичные стишки",
                artist: "ALADDIN Rhythm Kids",
                category: "play",
                topics: ["rhythm"],
                lines: [
                    .init(startSec: 0, endSec: 4, text: "Топ-топ, хлоп-хлоп, ритм не устаёт"),
                    .init(startSec: 4, endSec: 8, text: "Шаг вперёд, прыжок назад, песенка зовёт"),
                    .init(startSec: 8, endSec: 12, text: "Слог за слогом, в ладоши в такт"),
                    .init(startSec: 12, endSec: 16, text: "Ритмичный стих звучит вот так")
                ]
            )
        ]
    }

    private var filteredTracks: [KaraokeTrack] {
        tracks.filter { track in
            track.category == selectedCategory
                && (selectedTopic == "all" || track.topics.contains(selectedTopic))
        }
    }

    private var selectedTrack: KaraokeTrack {
        let list = filteredTracks.isEmpty ? tracks : filteredTracks
        let i = min(max(0, selectedTrackIndex), max(0, list.count - 1))
        return list[i]
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_content_music_title"))
                .font(.system(size: 17, weight: .bold))

            Picker("", selection: $selectedCategory) {
                Text(localizationManager.localized("child_songs_category_learning")).tag("learning")
                Text(localizationManager.localized("child_songs_category_play")).tag("play")
                Text(localizationManager.localized("child_songs_category_lullaby")).tag("lullaby")
            }
            .pickerStyle(.segmented)
            .onChange(of: selectedCategory) { _ in
                selectedTrackIndex = 0
                currentTime = 0
                isPlaying = false
            }

            Picker("", selection: $selectedTopic) {
                Text(localizationManager.localized("child_songs_topic_all")).tag("all")
                Text(localizationManager.localized("child_songs_topic_numbers")).tag("numbers")
                Text(localizationManager.localized("child_songs_topic_colors")).tag("colors")
                Text(localizationManager.localized("child_songs_topic_animals")).tag("animals")
                Text(localizationManager.localized("child_songs_topic_seasons")).tag("seasons")
                Text(localizationManager.localized("child_songs_topic_rhythm")).tag("rhythm")
            }
            .pickerStyle(.menu)
            .onChange(of: selectedTopic) { _ in
                selectedTrackIndex = 0
                currentTime = 0
                isPlaying = false
            }

            Picker("", selection: $selectedTrackIndex) {
                let list = filteredTracks.isEmpty ? tracks : filteredTracks
                ForEach(Array(list.enumerated()), id: \.offset) { index, track in
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

            Button(
                favoriteTitles.contains(selectedTrack.title)
                    ? localizationManager.localized("child_songs_remove_favorite")
                    : localizationManager.localized("child_songs_add_favorite")
            ) {
                toggleFavorite(selectedTrack.title)
            }
            .buttonStyle(.bordered)

            if !favoriteTitles.isEmpty {
                Text(
                    String(
                        format: localizationManager.localized("child_songs_favorites_count"),
                        favoriteTitles.count
                    )
                )
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.secondary)
            }

            VStack(alignment: .leading, spacing: 6) {
                Toggle(localizationManager.localized("child_songs_accompaniment_toggle"), isOn: $accompanimentOn)
                HStack(spacing: 8) {
                    Text(localizationManager.localized("child_songs_accompaniment_level"))
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.secondary)
                    Slider(value: $accompanimentLevel, in: 0...1)
                        .disabled(!accompanimentOn)
                }
            }

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
                    if isPlaying && accompanimentOn {
                        SoundEffectPlayer.shared.play(.tapSoft, priority: .medium)
                    }
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
        .onAppear {
            loadFavoritesIfNeeded()
        }
    }

    private func isActive(_ line: KaraokeLyricLine) -> Bool {
        currentTime >= line.startSec && currentTime < line.endSec
    }

    private func favoritesKey() -> String {
        let childId = UserDefaults.standard.string(forKey: "active_child_profile_server_id") ?? "local-default-child"
        return "child.karaoke.favorites.\(childId)"
    }

    private func loadFavoritesIfNeeded() {
        guard !favoritesLoaded else { return }
        favoritesLoaded = true
        let arr = UserDefaults.standard.stringArray(forKey: favoritesKey()) ?? []
        favoriteTitles = Set(arr)
    }

    private func persistFavorites() {
        UserDefaults.standard.set(Array(favoriteTitles).sorted(), forKey: favoritesKey())
    }

    private func toggleFavorite(_ title: String) {
        if favoriteTitles.contains(title) {
            favoriteTitles.remove(title)
        } else {
            favoriteTitles.insert(title)
        }
        persistFavorites()
    }
}

/// Раскрашивание и контуры — `drawing.05`, геометрия — `drawing.06`.
private enum ChildDrawingColoringTemplate: String, CaseIterable, Identifiable {
    case none
    case circle
    case square
    case triangle
    case hexagon
    case animal
    case plant
    case family
    case vehicle
    case abstractPattern
    case house
    case sun
    var id: String { rawValue }
}

/// Генерация ч/б линеарта под размер вью; `none` = без сетки (белый фон).
private enum ChildDrawingLineArtFactory {
    static func lineArtImage(
        for template: ChildDrawingColoringTemplate,
        size: CGSize,
        displayScale: CGFloat
    ) -> UIImage? {
        guard size.width > 4, size.height > 4 else { return nil }
        if template == .none { return nil }
        let format = UIGraphicsImageRendererFormat()
        format.scale = max(1, displayScale)
        format.opaque = true
        let r = UIGraphicsImageRenderer(size: size, format: format)
        return r.image { rctx in
            let ctx = rctx.cgContext
            UIColor.white.setFill()
            ctx.fill(CGRect(origin: .zero, size: size))
            let stroke = UIColor.label.withAlphaComponent(0.82)
            let lw = max(1.5, min(size.width, size.height) * 0.012)
            ctx.setLineWidth(lw)
            ctx.setLineCap(.round)
            ctx.setLineJoin(.round)
            ctx.setStrokeColor(stroke.cgColor)
            switch template {
            case .none: break
            case .circle:
                let s = min(size.width, size.height) * 0.62
                let rIn = CGRect(
                    x: (size.width - s) * 0.5,
                    y: (size.height - s) * 0.5,
                    width: s,
                    height: s
                )
                ctx.strokeEllipse(in: rIn)
            case .square:
                let s = min(size.width, size.height) * 0.55
                let rct = CGRect(
                    x: (size.width - s) * 0.5,
                    y: (size.height - s) * 0.5,
                    width: s,
                    height: s
                )
                ctx.stroke(rct)
            case .triangle:
                let w = size.width, h = size.height
                let cx = w * 0.5, cy = h * 0.5
                let r = min(w, h) * 0.32
                let p = UIBezierPath()
                for i in 0..<3 {
                    let a = CGFloat(i) * 2 * .pi / 3 - .pi / 2
                    let x = cx + cos(a) * r * 1.15
                    let y = cy + sin(a) * r * 1.15
                    if i == 0 { p.move(to: CGPoint(x: x, y: y)) } else { p.addLine(to: CGPoint(x: x, y: y)) }
                }
                p.close()
                ctx.addPath(p.cgPath)
                ctx.drawPath(using: .stroke)
            case .hexagon:
                let w = size.width, h = size.height
                let cx = w * 0.5, cy = h * 0.5
                let rad = min(w, h) * 0.3
                let p = UIBezierPath()
                for i in 0..<6 {
                    let a = CGFloat(i) * .pi / 3 - .pi / 2
                    let x = cx + cos(a) * rad
                    let y = cy + sin(a) * rad
                    if i == 0 { p.move(to: CGPoint(x: x, y: y)) } else { p.addLine(to: CGPoint(x: x, y: y)) }
                }
                p.close()
                ctx.addPath(p.cgPath)
                ctx.drawPath(using: .stroke)
            case .animal:
                let w = size.width, h = size.height
                // simple cat-like face contour
                let faceRect = CGRect(x: w * 0.3, y: h * 0.34, width: w * 0.4, height: h * 0.38)
                ctx.strokeEllipse(in: faceRect)
                let earL = UIBezierPath()
                earL.move(to: CGPoint(x: w * 0.36, y: h * 0.38))
                earL.addLine(to: CGPoint(x: w * 0.3, y: h * 0.22))
                earL.addLine(to: CGPoint(x: w * 0.44, y: h * 0.33))
                earL.close()
                let earR = UIBezierPath()
                earR.move(to: CGPoint(x: w * 0.64, y: h * 0.38))
                earR.addLine(to: CGPoint(x: w * 0.7, y: h * 0.22))
                earR.addLine(to: CGPoint(x: w * 0.56, y: h * 0.33))
                earR.close()
                ctx.addPath(earL.cgPath)
                ctx.addPath(earR.cgPath)
                ctx.drawPath(using: .stroke)
            case .plant:
                let w = size.width, h = size.height
                ctx.beginPath()
                ctx.move(to: CGPoint(x: w * 0.5, y: h * 0.78))
                ctx.addLine(to: CGPoint(x: w * 0.5, y: h * 0.34))
                ctx.strokePath()
                for (cx, cy, ex, ey) in [(0.5,0.46,0.36,0.40),(0.5,0.58,0.64,0.52),(0.5,0.66,0.38,0.62)] {
                    let leaf = UIBezierPath()
                    leaf.move(to: CGPoint(x: w * cx, y: h * cy))
                    leaf.addQuadCurve(to: CGPoint(x: w * ex, y: h * ey), controlPoint: CGPoint(x: w * ((cx+ex)/2), y: h * (cy - 0.1)))
                    leaf.addQuadCurve(to: CGPoint(x: w * cx, y: h * cy), controlPoint: CGPoint(x: w * ((cx+ex)/2), y: h * (ey + 0.1)))
                    ctx.addPath(leaf.cgPath)
                    ctx.drawPath(using: .stroke)
                }
                ctx.stroke(CGRect(x: w * 0.42, y: h * 0.78, width: w * 0.16, height: h * 0.12))
            case .family:
                let w = size.width, h = size.height
                // two adults and one child (heads + body lines)
                for (x, y, r) in [(0.36,0.38,0.06),(0.64,0.38,0.06),(0.5,0.48,0.045)] {
                    let head = CGRect(x: w * (x-r), y: h * (y-r), width: w * (r*2), height: h * (r*2))
                    ctx.strokeEllipse(in: head)
                }
                ctx.beginPath()
                ctx.move(to: CGPoint(x: w * 0.36, y: h * 0.44)); ctx.addLine(to: CGPoint(x: w * 0.36, y: h * 0.74))
                ctx.move(to: CGPoint(x: w * 0.64, y: h * 0.44)); ctx.addLine(to: CGPoint(x: w * 0.64, y: h * 0.74))
                ctx.move(to: CGPoint(x: w * 0.50, y: h * 0.53)); ctx.addLine(to: CGPoint(x: w * 0.50, y: h * 0.74))
                ctx.strokePath()
            case .vehicle:
                let w = size.width, h = size.height
                let body = UIBezierPath(roundedRect: CGRect(x: w * 0.24, y: h * 0.48, width: w * 0.52, height: h * 0.2), cornerRadius: w * 0.03)
                ctx.addPath(body.cgPath)
                ctx.drawPath(using: .stroke)
                ctx.strokeEllipse(in: CGRect(x: w * 0.30, y: h * 0.65, width: w * 0.1, height: h * 0.1))
                ctx.strokeEllipse(in: CGRect(x: w * 0.60, y: h * 0.65, width: w * 0.1, height: h * 0.1))
            case .abstractPattern:
                let w = size.width, h = size.height
                for i in 0..<5 {
                    let inset = CGFloat(i) * min(w, h) * 0.05
                    ctx.stroke(CGRect(x: w * 0.2 + inset, y: h * 0.2 + inset, width: w * 0.6 - 2*inset, height: h * 0.6 - 2*inset))
                }
                ctx.beginPath()
                ctx.move(to: CGPoint(x: w * 0.2, y: h * 0.2))
                ctx.addLine(to: CGPoint(x: w * 0.8, y: h * 0.8))
                ctx.move(to: CGPoint(x: w * 0.8, y: h * 0.2))
                ctx.addLine(to: CGPoint(x: w * 0.2, y: h * 0.8))
                ctx.strokePath()
            case .house:
                let w = size.width, h = size.height
                let p = UIBezierPath()
                p.move(to: CGPoint(x: w * 0.22, y: h * 0.5))
                p.addLine(to: CGPoint(x: w * 0.5, y: h * 0.18))
                p.addLine(to: CGPoint(x: w * 0.78, y: h * 0.5))
                p.addLine(to: CGPoint(x: w * 0.78, y: h * 0.88))
                p.addLine(to: CGPoint(x: w * 0.22, y: h * 0.88))
                p.close()
                ctx.addPath(p.cgPath)
                ctx.drawPath(using: .stroke)
            case .sun:
                let cx = size.width * 0.5, cy = size.height * 0.48
                let rad = min(size.width, size.height) * 0.18
                let disc = UIBezierPath(
                    arcCenter: CGPoint(x: cx, y: cy), radius: rad, startAngle: 0, endAngle: .pi * 2, clockwise: true
                )
                ctx.addPath(disc.cgPath)
                ctx.drawPath(using: .stroke)
                let r1 = min(size.width, size.height) * 0.32
                for i in 0..<8 {
                    let a = CGFloat(i) * .pi * 0.25 - .pi * 0.5
                    let r0 = rad * 1.12
                    ctx.beginPath()
                    ctx.move(to: CGPoint(x: cx + cos(a) * r0, y: cy + sin(a) * r0))
                    ctx.addLine(to: CGPoint(x: cx + cos(a) * r1, y: cy + sin(a) * r1))
                    ctx.strokePath()
                }
            }
        }
    }
}

private final class TemplatedPencilContainerView: UIView {
    let imageView = UIImageView()
    let canvas = PKCanvasView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        imageView.translatesAutoresizingMaskIntoConstraints = false
        imageView.backgroundColor = .systemBackground
        imageView.contentMode = .scaleToFill
        imageView.clipsToBounds = true
        canvas.translatesAutoresizingMaskIntoConstraints = false
        canvas.backgroundColor = .clear
        canvas.isOpaque = false
        canvas.drawingPolicy = .anyInput
        addSubview(imageView)
        addSubview(canvas)
        NSLayoutConstraint.activate([
            imageView.leadingAnchor.constraint(equalTo: leadingAnchor),
            imageView.trailingAnchor.constraint(equalTo: trailingAnchor),
            imageView.topAnchor.constraint(equalTo: topAnchor),
            imageView.bottomAnchor.constraint(equalTo: bottomAnchor),
            canvas.leadingAnchor.constraint(equalTo: leadingAnchor),
            canvas.trailingAnchor.constraint(equalTo: trailingAnchor),
            canvas.topAnchor.constraint(equalTo: topAnchor),
            canvas.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { nil }

    func setTemplateImage(_ image: UIImage?) {
        if image == nil {
            imageView.image = nil
            imageView.backgroundColor = .systemBackground
        } else {
            imageView.image = image
            imageView.backgroundColor = .white
        }
    }
}

/// Разные кисти (тонкая / толстая) — PLAN matrix `drawing.03`.
private enum ChildDrawingBrushStyle: String, CaseIterable, Identifiable {
    case thin
    case thick
    var id: String { rawValue }
    /// `PKInkingTool` ширина линии в pt (детский рисунок).
    var lineWidth: CGFloat {
        switch self {
        case .thin: return 5
        case .thick: return 14
        }
    }
}

private struct DrawingExperienceHostView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    @State private var drawing = PKDrawing()
    @State private var brush: ChildDrawingBrushStyle = .thick
    @State private var coloringTemplate: ChildDrawingColoringTemplate = .none
    @State private var savedItems: [ChildSavedDrawing] = []
    @State private var selectedDrawingID: UUID?
    @State private var comicPanelIndex: Int = 0
    @State private var designScore: Int = 0
    @State private var photoShots: Int = 0
    @State private var videoClips: Int = 0
    @State private var musicBeats: Int = 0
    @State private var storyLines: Int = 0
    @State private var theaterScenes: Int = 0
    @State private var craftItems: Int = 0
    @State private var digitalLayers: Int = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_creativity_create"))
                .font(.system(size: 17, weight: .bold))

            VStack(alignment: .leading, spacing: 8) {
                Text(localizationManager.localized("child_drawing_template_label"))
                    .font(.system(size: 14, weight: .semibold))
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(ChildDrawingColoringTemplate.allCases) { tm in
                            let isOn = (coloringTemplate == tm)
                            Button {
                                coloringTemplate = tm
                            } label: {
                                Text(templateTitle(tm))
                                    .font(.system(size: 13, weight: .semibold))
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 8)
                                    .background(
                                        RoundedRectangle(cornerRadius: 8, style: .continuous)
                                            .fill(isOn ? Color.orange.opacity(0.2) : Color(.secondarySystemBackground))
                                    )
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("child_drawing_template_a11y"))
            }

            VStack(alignment: .leading, spacing: 8) {
                Text(localizationManager.localized("child_drawing_brush_label"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.primary)
                HStack(spacing: 10) {
                    ForEach(ChildDrawingBrushStyle.allCases) { style in
                        let isOn = (brush == style)
                        Button {
                            brush = style
                        } label: {
                            Text(brushTitle(style))
                                .font(.system(size: 14, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .background(
                                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                                        .fill(isOn ? Color.teal.opacity(0.25) : Color(.secondarySystemBackground))
                                )
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier(style == .thin ? "child_drawing_brush_thin" : "child_drawing_brush_thick")
                        .accessibilityAddTraits(isOn ? [.isSelected] : [])
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("child_drawing_brush_a11y"))
            }

            TemplatedDrawingCanvasRepresentable(
                drawing: $drawing,
                lineWidth: brush.lineWidth,
                template: coloringTemplate
            )
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

            if item.id == "creativity.01" {
                advancedDrawingCard
            } else if item.id == "creativity.02" {
                comicsCard
            } else if item.id == "creativity.03" {
                designCard
            } else if item.id == "creativity.04" {
                photoCard
            } else if item.id == "creativity.05" {
                videoCard
            } else if item.id == "creativity.06" {
                musicCard
            } else if item.id == "creativity.07" {
                literatureCard
            } else if item.id == "creativity.08" {
                theaterCard
            } else if item.id == "creativity.09" {
                handmadeCard
            } else if item.id == "creativity.10" {
                digitalArtCard
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
        .onChange(of: coloringTemplate) { _ in
            drawing = PKDrawing()
        }
    }

    private func templateTitle(_ tm: ChildDrawingColoringTemplate) -> String {
        switch tm {
        case .none: return localizationManager.localized("child_drawing_template_none")
        case .circle: return localizationManager.localized("child_drawing_template_circle")
        case .square: return localizationManager.localized("child_drawing_template_square")
        case .triangle: return localizationManager.localized("child_drawing_template_triangle")
        case .hexagon: return localizationManager.localized("child_drawing_template_hexagon")
        case .animal: return localizationManager.localized("child_drawing_template_animal")
        case .plant: return localizationManager.localized("child_drawing_template_plant")
        case .family: return localizationManager.localized("child_drawing_template_family")
        case .vehicle: return localizationManager.localized("child_drawing_template_vehicle")
        case .abstractPattern: return localizationManager.localized("child_drawing_template_abstract")
        case .house: return localizationManager.localized("child_drawing_template_house")
        case .sun: return localizationManager.localized("child_drawing_template_sun")
        }
    }

    private func brushTitle(_ style: ChildDrawingBrushStyle) -> String {
        switch style {
        case .thin: return localizationManager.localized("child_drawing_brush_thin")
        case .thick: return localizationManager.localized("child_drawing_brush_thick")
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

    private var comicsCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_comics_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_comics_panel") + " \(comicPanelIndex + 1)/4")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_comics_next_panel")) {
                comicPanelIndex = min(3, comicPanelIndex + 1)
            }
            .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.purple.opacity(0.08)))
    }

    private var advancedDrawingCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_advanced_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_advanced_layers") + " \(digitalLayers)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                Button(localizationManager.localized("child_creativity_advanced_action_detail")) { digitalLayers += 1 }
                    .buttonStyle(.bordered)
                Button(localizationManager.localized("child_creativity_advanced_action_shading")) { digitalLayers += 1 }
                    .buttonStyle(.bordered)
            }
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.teal.opacity(0.08)))
    }

    private var designCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_design_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_design_score") + " \(designScore)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                Button(localizationManager.localized("child_creativity_design_action_palette")) { designScore += 1 }
                    .buttonStyle(.bordered)
                Button(localizationManager.localized("child_creativity_design_action_layout")) { designScore += 1 }
                    .buttonStyle(.bordered)
            }
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.08)))
    }

    private var photoCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_photo_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_photo_shots") + " \(photoShots)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_photo_action_capture")) { photoShots += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.green.opacity(0.08)))
    }

    private var videoCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_video_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_video_clips") + " \(videoClips)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_video_action_add_clip")) { videoClips += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.red.opacity(0.08)))
    }

    private var musicCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_music_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_music_beats") + " \(musicBeats)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_music_action_add_beat")) { musicBeats += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.orange.opacity(0.08)))
    }

    private var literatureCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_literature_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_literature_lines") + " \(storyLines)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_literature_action_add_line")) { storyLines += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))
    }

    private var theaterCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_theater_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_theater_scenes") + " \(theaterScenes)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_theater_action_add_scene")) { theaterScenes += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.pink.opacity(0.08)))
    }

    private var handmadeCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_handmade_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_handmade_items") + " \(craftItems)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_handmade_action_add_item")) { craftItems += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.teal.opacity(0.08)))
    }

    private var digitalArtCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_creativity_digital_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_creativity_digital_layers") + " \(digitalLayers)")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_creativity_digital_action_add_layer")) { digitalLayers += 1 }
                .buttonStyle(.bordered)
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.cyan.opacity(0.08)))
    }
}

private struct TemplatedDrawingCanvasRepresentable: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    var lineWidth: CGFloat
    var template: ChildDrawingColoringTemplate

    func makeUIView(context: Context) -> TemplatedPencilContainerView {
        let v = TemplatedPencilContainerView()
        v.canvas.delegate = context.coordinator
        v.canvas.drawingPolicy = .anyInput
        v.canvas.tool = PKInkingTool(.marker, color: .systemBlue, width: lineWidth)
        v.canvas.drawing = drawing
        context.coordinator.lastLineWidth = lineWidth
        return v
    }

    func updateUIView(_ uiView: TemplatedPencilContainerView, context: Context) {
        let w = lineWidth
        if abs(context.coordinator.lastLineWidth - w) > 0.1 {
            uiView.canvas.tool = PKInkingTool(.marker, color: .systemBlue, width: w)
            context.coordinator.lastLineWidth = w
        }
        let b = uiView.bounds.size
        if b.width > 2, b.height > 2
            && (context.coordinator.lastSize != b || context.coordinator.lastTemplate != template) {
            let sc = uiView.traitCollection.displayScale
            let img = ChildDrawingLineArtFactory.lineArtImage(for: template, size: b, displayScale: sc)
            uiView.setTemplateImage(img)
            context.coordinator.lastSize = b
            context.coordinator.lastTemplate = template
        }
        if uiView.canvas.drawing != drawing {
            uiView.canvas.drawing = drawing
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator(drawing: $drawing) }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        @Binding var drawing: PKDrawing
        var lastLineWidth: CGFloat = 0
        var lastSize: CGSize = .zero
        var lastTemplate: ChildDrawingColoringTemplate?

        init(drawing: Binding<PKDrawing>) { _drawing = drawing }

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

private enum ToyShapeKind: String, CaseIterable, Identifiable {
    case circle
    case square
    case triangle

    var id: String { rawValue }
}

private enum ToyAnimalKind: String, CaseIterable, Identifiable {
    case cat
    case dog
    case cow
    case duck

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .cat: return "🐱"
        case .dog: return "🐶"
        case .cow: return "🐮"
        case .duck: return "🦆"
        }
    }
}

private enum ToyTransportKind: String, CaseIterable, Identifiable {
    case car
    case train
    case airplane
    case ship

    var id: String { rawValue }
}

private enum ToyInstrumentKind: String, CaseIterable, Identifiable {
    case piano
    case drum
    case guitar
    case flute

    var id: String { rawValue }
}

private enum ToyRolePlayScene: String, CaseIterable, Identifiable {
    case kitchen
    case shop

    var id: String { rawValue }
}

/// P2-101: reusable 3D scene host for toy interactions with telemetry hooks.
/// PLAN `toys.03`: мини-игра «Узнай цвет» (образец + 4 варианта).
private struct Toys3DSceneHostView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    @State private var sceneKind: ToySceneKind = .robot
    @State private var interactionCount: Int = 0
    @State private var colorTargetId: String = "red"
    @State private var colorShuffled: [String] = ["red", "blue", "yellow", "green"]
    @State private var colorHits: Int = 0
    @State private var colorLastWrong: Bool = false
    @State private var shapeTarget: ToyShapeKind = .circle
    @State private var shapeOptions: [ToyShapeKind] = ToyShapeKind.allCases
    @State private var shapeHits: Int = 0
    @State private var shapeLastWrong: Bool = false
    @State private var animalTarget: ToyAnimalKind = .cat
    @State private var animalOptions: [ToyAnimalKind] = ToyAnimalKind.allCases
    @State private var animalHits: Int = 0
    @State private var animalLastWrong: Bool = false
    @State private var transportKind: ToyTransportKind = .car
    @State private var transportStep: Int = 0
    @State private var instrumentHits: Int = 0
    @State private var puzzleOrder: [Int] = [1, 2, 3, 4]
    @State private var puzzleExpected: Int = 1
    @State private var puzzleSolved: Int = 0
    @State private var bookPageIndex: Int = 0
    @State private var rolePlayScene: ToyRolePlayScene = .kitchen
    @State private var rolePlayScore: Int = 0
    @State private var riddleIndex: Int = 0
    @State private var riddleSelected: Int?
    @State private var riddleSolved: Int = 0
    @State private var alphaTarget: String = "A"
    @State private var alphaOptions: [String] = ["A", "B", "1", "2"]
    @State private var alphaScore: Int = 0
    @State private var emotionTarget: String = "happy"
    @State private var emotionScore: Int = 0
    @State private var colorFormTarget: (color: String, shape: ToyShapeKind) = ("red", .circle)
    @State private var colorFormScore: Int = 0
    @State private var weekdayIndex: Int = 0
    @State private var seasonIndex: Int = 0

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

            toyColorMatchCard
            toyShapeMatchCard
            toyAnimalSoundCard
            toyTransportCard
            toyInstrumentsCard
            toyPuzzleCard
            toyBookCard
            toyRolePlayCard
            toyRiddlesCard
            toyNumbersLettersCard
            toyEmotionsCard
            toyColorsFormsCard
            toyCalendarCard

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
        .onAppear {
            startToyColorRound()
            startToyShapeRound()
            startToyAnimalRound()
            startToyPuzzleRound()
            startNumbersLettersRound()
            startEmotionRound()
            startColorFormRound()
        }
    }

    private var toyColorMatchCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_color_game_title"))
                .font(.system(size: 15, weight: .bold))
            Text(localizationManager.localized("child_toys_color_game_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(toyColorSwiftUI(colorTargetId))
                .frame(height: 52)
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .stroke(Color.black.opacity(0.1), lineWidth: 1)
                )
                .accessibilityIdentifier("child_toy_color_swatch")
                .accessibilityLabel(
                    String(
                        format: localizationManager.localized("child_toys_color_swatch_a11y"),
                        localeNameForToyColorId(colorTargetId)
                    )
                )

            HStack(spacing: 10) {
                ForEach(colorShuffled, id: \.self) { cid in
                    Button {
                        if cid == colorTargetId {
                            colorLastWrong = false
                            colorHits += 1
                            let gen = UINotificationFeedbackGenerator()
                            gen.notificationOccurred(.success)
                            MasterLogger.shared.business(
                                "P2-104 toys color match OK contentId=\(item.id) hits=\(colorHits) target=\(colorTargetId)"
                            )
                            startToyColorRound()
                        } else {
                            colorLastWrong = true
                            UINotificationFeedbackGenerator().notificationOccurred(.error)
                        }
                    } label: {
                        Circle()
                            .fill(toyColorSwiftUI(cid))
                            .frame(width: 44, height: 44)
                            .overlay(
                                Circle().stroke(Color.primary.opacity(0.15), lineWidth: 1)
                            )
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("child_toy_color_option_\(cid)")
                    .accessibilityLabel(
                        String(
                            format: localizationManager.localized("child_toys_color_option_a11y"),
                            localeNameForToyColorId(cid)
                        )
                    )
                }
            }
            if colorLastWrong {
                Text(localizationManager.localized("child_toys_color_game_wrong"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.orange)
            }
            Text(
                String(format: localizationManager.localized("child_toys_color_game_score"), colorHits)
            )
            .font(.system(size: 12, weight: .medium))
            .foregroundColor(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }

    private static let toyColorAllIds: [String] = ["red", "blue", "yellow", "green"]

    private func startToyColorRound() {
        colorTargetId = Self.toyColorAllIds.randomElement() ?? "red"
        colorShuffled = Self.toyColorAllIds.shuffled()
    }

    private func toyColorSwiftUI(_ id: String) -> Color {
        switch id {
        case "red": return .red
        case "blue": return .blue
        case "yellow": return .yellow
        case "green": return .green
        default: return .gray
        }
    }

    private func localeNameForToyColorId(_ id: String) -> String {
        let key: String
        switch id {
        case "red": key = "child_toys_color_name_red"
        case "blue": key = "child_toys_color_name_blue"
        case "yellow": key = "child_toys_color_name_yellow"
        case "green": key = "child_toys_color_name_green"
        default: key = "child_toys_color_name_red"
        }
        return localizationManager.localized(key)
    }

    private var toyShapeMatchCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_shape_game_title"))
                .font(.system(size: 15, weight: .bold))
            Text(localizationManager.localized("child_toys_shape_game_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            toyShapePreview(shapeTarget)
                .frame(height: 54)
                .accessibilityIdentifier("child_toy_shape_preview")
                .accessibilityLabel(
                    String(
                        format: localizationManager.localized("child_toys_shape_preview_a11y"),
                        localizedName(for: shapeTarget)
                    )
                )

            HStack(spacing: 10) {
                ForEach(shapeOptions) { shape in
                    Button {
                        if shape == shapeTarget {
                            shapeLastWrong = false
                            shapeHits += 1
                            UINotificationFeedbackGenerator().notificationOccurred(.success)
                            MasterLogger.shared.business(
                                "P2-105 toys shape match OK contentId=\(item.id) hits=\(shapeHits) target=\(shapeTarget.rawValue)"
                            )
                            startToyShapeRound()
                        } else {
                            shapeLastWrong = true
                            UINotificationFeedbackGenerator().notificationOccurred(.error)
                        }
                    } label: {
                        toyShapePreview(shape)
                            .frame(width: 54, height: 44)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("child_toy_shape_option_\(shape.rawValue)")
                    .accessibilityLabel(
                        String(
                            format: localizationManager.localized("child_toys_shape_option_a11y"),
                            localizedName(for: shape)
                        )
                    )
                }
            }
            if shapeLastWrong {
                Text(localizationManager.localized("child_toys_shape_game_wrong"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.orange)
            }
            Text(
                String(format: localizationManager.localized("child_toys_shape_game_score"), shapeHits)
            )
            .font(.system(size: 12, weight: .medium))
            .foregroundColor(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }

    @ViewBuilder
    private func toyShapePreview(_ shape: ToyShapeKind) -> some View {
        switch shape {
        case .circle:
            Circle()
                .fill(Color.purple.opacity(0.72))
                .overlay(Circle().stroke(Color.primary.opacity(0.15), lineWidth: 1))
        case .square:
            RoundedRectangle(cornerRadius: 4, style: .continuous)
                .fill(Color.blue.opacity(0.7))
                .overlay(RoundedRectangle(cornerRadius: 4).stroke(Color.primary.opacity(0.15), lineWidth: 1))
        case .triangle:
            TriangleShape()
                .fill(Color.green.opacity(0.72))
                .overlay(TriangleShape().stroke(Color.primary.opacity(0.15), lineWidth: 1))
        }
    }

    private func startToyShapeRound() {
        shapeTarget = ToyShapeKind.allCases.randomElement() ?? .circle
        shapeOptions = ToyShapeKind.allCases.shuffled()
    }

    private func localizedName(for shape: ToyShapeKind) -> String {
        let key: String
        switch shape {
        case .circle: key = "child_toys_shape_name_circle"
        case .square: key = "child_toys_shape_name_square"
        case .triangle: key = "child_toys_shape_name_triangle"
        }
        return localizationManager.localized(key)
    }

    private var toyAnimalSoundCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_animal_game_title"))
                .font(.system(size: 15, weight: .bold))
            Text(localizationManager.localized("child_toys_animal_game_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: 8) {
                Text(animalTarget.emoji).font(.system(size: 26))
                Text(localizationManager.localized("child_toys_animal_prompt"))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)
            }

            HStack(spacing: 10) {
                ForEach(animalOptions) { animal in
                    Button {
                        if animal == animalTarget {
                            animalLastWrong = false
                            animalHits += 1
                            UINotificationFeedbackGenerator().notificationOccurred(.success)
                            SoundEffectPlayer.shared.playVoicePrompt(
                                localizedAnimalSoundPhrase(for: animal),
                                languageCode: "ru-RU",
                                priority: .high
                            )
                            MasterLogger.shared.business(
                                "P2-106 toys animal sound OK contentId=\(item.id) hits=\(animalHits) animal=\(animal.rawValue)"
                            )
                            startToyAnimalRound()
                        } else {
                            animalLastWrong = true
                            UINotificationFeedbackGenerator().notificationOccurred(.error)
                        }
                    } label: {
                        VStack(spacing: 4) {
                            Text(animal.emoji).font(.system(size: 28))
                            Text(localizedAnimalName(animal))
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.primary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(RoundedRectangle(cornerRadius: 8).fill(Color(.secondarySystemBackground)))
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("child_toy_animal_option_\(animal.rawValue)")
                }
            }
            if animalLastWrong {
                Text(localizationManager.localized("child_toys_animal_game_wrong"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.orange)
            }
            Text(String(format: localizationManager.localized("child_toys_animal_game_score"), animalHits))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }

    private func startToyAnimalRound() {
        animalTarget = ToyAnimalKind.allCases.randomElement() ?? .cat
        animalOptions = ToyAnimalKind.allCases.shuffled()
    }

    private func localizedAnimalName(_ animal: ToyAnimalKind) -> String {
        let key: String
        switch animal {
        case .cat: key = "child_toys_animal_name_cat"
        case .dog: key = "child_toys_animal_name_dog"
        case .cow: key = "child_toys_animal_name_cow"
        case .duck: key = "child_toys_animal_name_duck"
        }
        return localizationManager.localized(key)
    }

    private func localizedAnimalSoundPhrase(for animal: ToyAnimalKind) -> String {
        let key: String
        switch animal {
        case .cat: key = "child_toys_animal_sound_cat"
        case .dog: key = "child_toys_animal_sound_dog"
        case .cow: key = "child_toys_animal_sound_cow"
        case .duck: key = "child_toys_animal_sound_duck"
        }
        return localizationManager.localized(key)
    }

    private var toyTransportCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_transport_title"))
                .font(.system(size: 15, weight: .bold))
            Picker("", selection: $transportKind) {
                Text(localizationManager.localized("child_toys_transport_car")).tag(ToyTransportKind.car)
                Text(localizationManager.localized("child_toys_transport_train")).tag(ToyTransportKind.train)
                Text(localizationManager.localized("child_toys_transport_airplane")).tag(ToyTransportKind.airplane)
                Text(localizationManager.localized("child_toys_transport_ship")).tag(ToyTransportKind.ship)
            }
            .pickerStyle(.segmented)
            Button(localizationManager.localized("child_toys_transport_move_action")) {
                transportStep = (transportStep + 1) % 6
                UINotificationFeedbackGenerator().notificationOccurred(.success)
            }
            .buttonStyle(.borderedProminent)
            Text(localizedTransportEmoji(transportKind))
                .font(.system(size: 34))
                .offset(x: CGFloat(transportStep) * 18)
                .frame(maxWidth: .infinity, alignment: .leading)
                .animation(.easeInOut(duration: 0.25), value: transportStep)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private func localizedTransportEmoji(_ kind: ToyTransportKind) -> String {
        switch kind {
        case .car: return "🚗"
        case .train: return "🚂"
        case .airplane: return "✈️"
        case .ship: return "🚢"
        }
    }

    private var toyInstrumentsCard: some View {
        let instruments: [ToyInstrumentKind] = [.piano, .drum, .guitar, .flute]
        return VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_instruments_title"))
                .font(.system(size: 15, weight: .bold))
            HStack(spacing: 8) {
                ForEach(instruments) { inst in
                    Button {
                        instrumentHits += 1
                        SoundEffectPlayer.shared.play(.tapSoft, priority: .high)
                        SoundEffectPlayer.shared.playVoicePrompt(localizedInstrumentPhrase(inst), languageCode: "ru-RU", priority: .medium)
                    } label: {
                        VStack(spacing: 4) {
                            Text(localizedInstrumentEmoji(inst)).font(.system(size: 24))
                            Text(localizedInstrumentName(inst))
                                .font(.system(size: 11, weight: .semibold))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(RoundedRectangle(cornerRadius: 8).fill(Color(.tertiarySystemBackground)))
                    }
                    .buttonStyle(.plain)
                }
            }
            Text(String(format: localizationManager.localized("child_toys_instruments_score"), instrumentHits))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private func localizedInstrumentEmoji(_ kind: ToyInstrumentKind) -> String {
        switch kind {
        case .piano: return "🎹"
        case .drum: return "🥁"
        case .guitar: return "🎸"
        case .flute: return "🪈"
        }
    }

    private func localizedInstrumentName(_ kind: ToyInstrumentKind) -> String {
        switch kind {
        case .piano: return localizationManager.localized("child_toys_instrument_piano")
        case .drum: return localizationManager.localized("child_toys_instrument_drum")
        case .guitar: return localizationManager.localized("child_toys_instrument_guitar")
        case .flute: return localizationManager.localized("child_toys_instrument_flute")
        }
    }

    private func localizedInstrumentPhrase(_ kind: ToyInstrumentKind) -> String {
        switch kind {
        case .piano: return localizationManager.localized("child_toys_instrument_phrase_piano")
        case .drum: return localizationManager.localized("child_toys_instrument_phrase_drum")
        case .guitar: return localizationManager.localized("child_toys_instrument_phrase_guitar")
        case .flute: return localizationManager.localized("child_toys_instrument_phrase_flute")
        }
    }

    private var toyPuzzleCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_puzzle_title"))
                .font(.system(size: 15, weight: .bold))
            Text(String(format: localizationManager.localized("child_toys_puzzle_prompt"), puzzleExpected))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                ForEach(puzzleOrder, id: \.self) { piece in
                    Button {
                        if piece == puzzleExpected {
                            puzzleSolved += 1
                            puzzleExpected += 1
                            UINotificationFeedbackGenerator().notificationOccurred(.success)
                            if puzzleExpected > 4 {
                                startToyPuzzleRound()
                            }
                        } else {
                            UINotificationFeedbackGenerator().notificationOccurred(.error)
                        }
                    } label: {
                        Text("\(piece)")
                            .font(.system(size: 18, weight: .bold))
                            .frame(width: 44, height: 44)
                            .background(RoundedRectangle(cornerRadius: 8).fill(Color.yellow.opacity(0.35)))
                    }
                    .buttonStyle(.plain)
                }
            }
            Text(String(format: localizationManager.localized("child_toys_puzzle_score"), puzzleSolved))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private func startToyPuzzleRound() {
        puzzleOrder = [1, 2, 3, 4].shuffled()
        puzzleExpected = 1
    }

    private var toyBookCard: some View {
        let pages: [(emoji: String, textKey: String)] = [
            ("📚", "child_toys_book_page_1"),
            ("🌈", "child_toys_book_page_2"),
            ("🦊", "child_toys_book_page_3")
        ]
        let idx = min(max(0, bookPageIndex), pages.count - 1)
        return VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_book_title"))
                .font(.system(size: 15, weight: .bold))
            Text(pages[idx].emoji).font(.system(size: 34))
            Text(localizationManager.localized(pages[idx].textKey))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
            HStack {
                Button(localizationManager.localized("child_toys_book_prev")) {
                    bookPageIndex = max(0, bookPageIndex - 1)
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_toys_book_next")) {
                    bookPageIndex = min(pages.count - 1, bookPageIndex + 1)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private var toyRolePlayCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_roleplay_title"))
                .font(.system(size: 15, weight: .bold))
            Picker("", selection: $rolePlayScene) {
                Text(localizationManager.localized("child_toys_roleplay_kitchen")).tag(ToyRolePlayScene.kitchen)
                Text(localizationManager.localized("child_toys_roleplay_shop")).tag(ToyRolePlayScene.shop)
            }
            .pickerStyle(.segmented)

            Text(rolePlayPromptText)
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
                .padding(.vertical, 2)

            HStack(spacing: 8) {
                ForEach(rolePlayActions, id: \.self) { action in
                    Button(action) {
                        rolePlayScore += 1
                        UINotificationFeedbackGenerator().notificationOccurred(.success)
                        SoundEffectPlayer.shared.play(.success, priority: .high)
                        MasterLogger.shared.business(
                            "P2-107 toys roleplay action contentId=\(item.id) scene=\(rolePlayScene.rawValue) action=\(action) score=\(rolePlayScore)"
                        )
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.purple.opacity(0.8))
                }
            }

            Text(String(format: localizationManager.localized("child_toys_roleplay_score"), rolePlayScore))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private var rolePlayPromptText: String {
        switch rolePlayScene {
        case .kitchen:
            return localizationManager.localized("child_toys_roleplay_kitchen_prompt")
        case .shop:
            return localizationManager.localized("child_toys_roleplay_shop_prompt")
        }
    }

    private var rolePlayActions: [String] {
        switch rolePlayScene {
        case .kitchen:
            return [
                localizationManager.localized("child_toys_roleplay_kitchen_action_cook"),
                localizationManager.localized("child_toys_roleplay_kitchen_action_serve")
            ]
        case .shop:
            return [
                localizationManager.localized("child_toys_roleplay_shop_action_buy"),
                localizationManager.localized("child_toys_roleplay_shop_action_pay")
            ]
        }
    }

    private struct ToyRiddle {
        let questionKey: String
        let optionsKeys: [String]
        let correctIndex: Int
    }

    private var riddles: [ToyRiddle] {
        [
            .init(
                questionKey: "child_toys_riddle_q1",
                optionsKeys: ["child_toys_riddle_q1_a1", "child_toys_riddle_q1_a2", "child_toys_riddle_q1_a3"],
                correctIndex: 0
            ),
            .init(
                questionKey: "child_toys_riddle_q2",
                optionsKeys: ["child_toys_riddle_q2_a1", "child_toys_riddle_q2_a2", "child_toys_riddle_q2_a3"],
                correctIndex: 1
            )
        ]
    }

    private var toyRiddlesCard: some View {
        let r = riddles[riddleIndex]
        return VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_riddles_title"))
                .font(.system(size: 15, weight: .bold))
            Text(localizationManager.localized(r.questionKey))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
            ForEach(Array(r.optionsKeys.enumerated()), id: \.offset) { idx, key in
                Button {
                    riddleSelected = idx
                    if idx == r.correctIndex {
                        riddleSolved += 1
                        UINotificationFeedbackGenerator().notificationOccurred(.success)
                        riddleIndex = (riddleIndex + 1) % riddles.count
                        riddleSelected = nil
                    } else {
                        UINotificationFeedbackGenerator().notificationOccurred(.error)
                    }
                } label: {
                    Text(localizationManager.localized(key))
                        .font(.system(size: 13, weight: .semibold))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 8)
                        .padding(.horizontal, 10)
                        .background(RoundedRectangle(cornerRadius: 8).fill(Color(.tertiarySystemBackground)))
                }
                .buttonStyle(.plain)
            }
            Text(String(format: localizationManager.localized("child_toys_riddles_score"), riddleSolved))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private var toyNumbersLettersCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_numbers_letters_title"))
                .font(.system(size: 15, weight: .bold))
            Text(String(format: localizationManager.localized("child_toys_numbers_letters_prompt"), alphaTarget))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                ForEach(alphaOptions, id: \.self) { opt in
                    Button {
                        if opt == alphaTarget {
                            alphaScore += 1
                            UINotificationFeedbackGenerator().notificationOccurred(.success)
                            startNumbersLettersRound()
                        } else {
                            UINotificationFeedbackGenerator().notificationOccurred(.error)
                        }
                    } label: {
                        Text(opt)
                            .font(.system(size: 20, weight: .bold))
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .background(RoundedRectangle(cornerRadius: 8).fill(Color.blue.opacity(0.2)))
                    }
                    .buttonStyle(.plain)
                }
            }
            Text(String(format: localizationManager.localized("child_toys_numbers_letters_score"), alphaScore))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private func startNumbersLettersRound() {
        let targets = ["A", "B", "1", "2", "3", "C"]
        alphaTarget = targets.randomElement() ?? "A"
        alphaOptions = Array(Set([alphaTarget, "A", "B", "1", "2", "3", "C"].shuffled().prefix(4))).shuffled()
        if !alphaOptions.contains(alphaTarget) {
            alphaOptions[0] = alphaTarget
        }
    }

    private var toyEmotionsCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_emotions_title"))
                .font(.system(size: 15, weight: .bold))
            Text(String(format: localizationManager.localized("child_toys_emotions_prompt"), localizedEmotionName(emotionTarget)))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                emotionButton("happy", emoji: "😄")
                emotionButton("sad", emoji: "😢")
                emotionButton("surprised", emoji: "😲")
                emotionButton("calm", emoji: "😌")
            }
            Text(String(format: localizationManager.localized("child_toys_emotions_score"), emotionScore))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private func emotionButton(_ key: String, emoji: String) -> some View {
        Button {
            if key == emotionTarget {
                emotionScore += 1
                UINotificationFeedbackGenerator().notificationOccurred(.success)
                startEmotionRound()
            } else {
                UINotificationFeedbackGenerator().notificationOccurred(.error)
            }
        } label: {
            Text(emoji)
                .font(.system(size: 28))
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(RoundedRectangle(cornerRadius: 8).fill(Color.orange.opacity(0.18)))
        }
        .buttonStyle(.plain)
    }

    private func startEmotionRound() {
        emotionTarget = ["happy", "sad", "surprised", "calm"].randomElement() ?? "happy"
    }

    private func localizedEmotionName(_ key: String) -> String {
        localizationManager.localized("child_toys_emotion_\(key)")
    }

    private var toyColorsFormsCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_colors_forms_title"))
                .font(.system(size: 15, weight: .bold))
            Text(
                String(
                    format: localizationManager.localized("child_toys_colors_forms_prompt"),
                    localeNameForToyColorId(colorFormTarget.color),
                    localizedName(for: colorFormTarget.shape)
                )
            )
            .font(.system(size: 13, weight: .medium))
            .foregroundColor(.secondary)
            HStack(spacing: 8) {
                ForEach(ToyShapeKind.allCases) { shape in
                    Button {
                        if shape == colorFormTarget.shape {
                            colorFormScore += 1
                            UINotificationFeedbackGenerator().notificationOccurred(.success)
                            startColorFormRound()
                        } else {
                            UINotificationFeedbackGenerator().notificationOccurred(.error)
                        }
                    } label: {
                        toyShapePreview(shape)
                            .frame(width: 54, height: 44)
                            .foregroundColor(toyColorSwiftUI(colorFormTarget.color))
                    }
                    .buttonStyle(.plain)
                }
            }
            Text(String(format: localizationManager.localized("child_toys_colors_forms_score"), colorFormScore))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
    }

    private func startColorFormRound() {
        let colors = ["red", "blue", "yellow", "green"]
        colorFormTarget = (colors.randomElement() ?? "red", ToyShapeKind.allCases.randomElement() ?? .circle)
    }

    private var toyCalendarCard: some View {
        let weekdays = [
            localizationManager.localized("child_toys_weekday_mon"),
            localizationManager.localized("child_toys_weekday_tue"),
            localizationManager.localized("child_toys_weekday_wed"),
            localizationManager.localized("child_toys_weekday_thu"),
            localizationManager.localized("child_toys_weekday_fri"),
            localizationManager.localized("child_toys_weekday_sat"),
            localizationManager.localized("child_toys_weekday_sun")
        ]
        let seasons = [
            localizationManager.localized("child_toys_season_spring"),
            localizationManager.localized("child_toys_season_summer"),
            localizationManager.localized("child_toys_season_autumn"),
            localizationManager.localized("child_toys_season_winter")
        ]
        return VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_toys_calendar_title"))
                .font(.system(size: 15, weight: .bold))
            HStack {
                Text(localizationManager.localized("child_toys_calendar_weekday_label"))
                    .font(.system(size: 12, weight: .semibold))
                Spacer()
                Text(weekdays[weekdayIndex])
                    .font(.system(size: 14, weight: .bold))
            }
            HStack(spacing: 8) {
                Button(localizationManager.localized("child_toys_calendar_prev")) {
                    weekdayIndex = (weekdayIndex + weekdays.count - 1) % weekdays.count
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_toys_calendar_next")) {
                    weekdayIndex = (weekdayIndex + 1) % weekdays.count
                }
                .buttonStyle(.borderedProminent)
            }
            HStack {
                Text(localizationManager.localized("child_toys_calendar_season_label"))
                    .font(.system(size: 12, weight: .semibold))
                Spacer()
                Text(seasons[seasonIndex])
                    .font(.system(size: 14, weight: .bold))
            }
            HStack(spacing: 8) {
                Button(localizationManager.localized("child_toys_calendar_prev")) {
                    seasonIndex = (seasonIndex + seasons.count - 1) % seasons.count
                }
                .buttonStyle(.bordered)
                Button(localizationManager.localized("child_toys_calendar_next")) {
                    seasonIndex = (seasonIndex + 1) % seasons.count
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.secondarySystemBackground)))
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

private struct TriangleShape: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: rect.midX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        p.closeSubpath()
        return p
    }
}

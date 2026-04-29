import SwiftUI

struct ParentDashboardView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool

    @State private var reports: [ActivityReportItem] = []
    @State private var allowedTypes: Set<ContentItemType> = Set(ContentItemType.allCases)
    @State private var filteredItemsCount: Int = 0
    @State private var dsarMessage: String?
    @State private var mirrorOverview = ParentMirrorOverview.empty
    @State private var trendWindow: ParentDashboardTrendWindow = .week
    @State private var trendPoints: [ParentDashboardDayPoint] = []
    @State private var shareDocument: ParentShareDocument?
    @State private var exportError: String?
    @State private var showUnifiedTimeLimits = false
    @State private var digestLines: [String] = []
    @State private var learnedSkillDeltas: [ParentSkillDelta] = []
    @State private var masteryTopics: [ParentMasteryTopic] = []
    @State private var roiRows: [ParentROIRow] = []
    @State private var digestAutoLines: [String] = []
    @State private var pendingExtensionRequestCount: Int = 0

    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 16) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("parent_dashboard_title"))
                        .font(.system(size: 24, weight: .bold))
                    Text(
                        localizationManager.localized(
                            "parent_dashboard_daily_limit_format",
                            TimeLimitsManager.shared.currentDailyLimitMinutes()
                        )
                    )
                    Text(
                        localizationManager.localized(
                            "parent_dashboard_remaining_format",
                            TimeLimitsManager.shared.currentRemainingMinutes()
                        )
                    )
                    Button(localizationManager.localized("parent_dashboard_open_unified_limits")) {
                        showUnifiedTimeLimits = true
                    }
                    .accessibilityLabel(localizationManager.localized("parent_dashboard_open_unified_limits"))
                    .accessibilityHint(localizationManager.localized("parent_dashboard_open_unified_limits_hint"))
                    .font(.system(size: 14, weight: .semibold))
                    .padding(.top, 4)
                    if pendingExtensionRequestCount > 0 {
                        Text(localizationManager.localized("parent_dashboard_pending_extension_requests", pendingExtensionRequestCount))
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.orange)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                .background(Color.white.opacity(0.08))
                .clipShape(RoundedRectangle(cornerRadius: 12))

                activityDigestSection
                learnedPanelSection
                masteryLevelsSection
                roiSection
                autoDigestSection

                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("parent_dashboard_content_filters"))
                        .font(.system(size: 18, weight: .semibold))
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(ContentItemType.allCases, id: \.rawValue) { type in
                                Button(localizationManager.localized(contentTypeLocalizationKey(type))) {
                                    toggleFilter(type)
                                }
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(allowedTypes.contains(type) ? Color.blue.opacity(0.3) : Color.gray.opacity(0.2))
                                .clipShape(Capsule())
                            }
                        }
                    }
                    Text(localizationManager.localized("parent_dashboard_filtered_visible_format", filteredItemsCount))
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.white.opacity(0.7))
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("parent_dashboard_data_rights"))
                        .font(.system(size: 18, weight: .semibold))
                    HStack(spacing: 10) {
                        Button(localizationManager.localized("parent_dashboard_export_child_package")) {
                            runSensitiveAction {
                                do {
                                    _ = try ProfileManager.shared.exportChildDataRightsPackage(
                                        familyId: UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
                                    )
                                    dsarMessage = localizationManager.localized("parent_dashboard_dsar_export_ok")
                                } catch {
                                    dsarMessage = localizationManager.localized(
                                        "parent_dashboard_dsar_export_fail",
                                        error.localizedDescription
                                    )
                                }
                            }
                        }
                        .buttonStyle(.borderedProminent)

                        Button(localizationManager.localized("parent_dashboard_delete_active_child")) {
                            runSensitiveAction {
                                let activeId = (UserDefaults.standard.string(forKey: "active_child_profile_server_id") ?? "")
                                    .trimmingCharacters(in: .whitespacesAndNewlines)
                                guard !activeId.isEmpty else {
                                    dsarMessage = localizationManager.localized("parent_dashboard_dsar_no_active_child")
                                    return
                                }
                                let deleted = ProfileManager.shared.deleteChildData(serverUserId: activeId)
                                dsarMessage = deleted
                                    ? localizationManager.localized("parent_dashboard_dsar_deleted_ok")
                                    : localizationManager.localized("parent_dashboard_dsar_delete_no_match")
                            }
                        }
                        .buttonStyle(.bordered)
                    }
                    if let dsarMessage, !dsarMessage.isEmpty {
                        Text(dsarMessage)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.82))
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(10)
                .background(Color.white.opacity(0.08))
                .clipShape(RoundedRectangle(cornerRadius: 12))

                mirrorOverviewSection

                ParentDashboardTrendSection(
                    localizationManager: localizationManager,
                    window: $trendWindow,
                    points: trendPoints
                )

                parentReportExportSection

                VStack(alignment: .leading, spacing: 0) {
                    ForEach(reports) { item in
                        HStack {
                            Text(reportRowTitle(item))
                            Spacer()
                            Text(item.value).fontWeight(.semibold)
                        }
                        .padding(.vertical, 8)
                        if item.id != reports.last?.id {
                            Divider().background(Color.white.opacity(0.12))
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .padding()
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button(localizationManager.localized("child_interface_back")) {
                        isPresented = false
                    }
                }
            }
            .onAppear {
                Task { await reloadReports() }
                pendingExtensionRequestCount = ChildTimeExtensionRequestStore.shared.pendingRequest() == nil ? 0 : 1
            }
            .onChange(of: trendWindow) { _ in
                Task { await reloadReports() }
            }
            .sheet(item: $shareDocument) { doc in
                ShareSheet(activityItems: [doc.url])
            }
            .sheet(isPresented: $showUnifiedTimeLimits) {
                UnifiedTimeLimitsScreen()
                    .environmentObject(localizationManager)
            }
            .onChange(of: showUnifiedTimeLimits) { isVisible in
                if !isVisible {
                    pendingExtensionRequestCount = ChildTimeExtensionRequestStore.shared.pendingRequest() == nil ? 0 : 1
                }
            }
            .accessibilityIdentifier("ParentDashboardView")
        }
    }

    private var activityDigestSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("activity_digest_title"))
                .font(.system(size: 16, weight: .semibold))
            ForEach(Array(digestLines.enumerated()), id: \.offset) { _, line in
                Text(line)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.88))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.white.opacity(0.06))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var parentReportExportSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("parent_dashboard_report_export_title"))
                .font(.system(size: 18, weight: .semibold))
            Text(localizationManager.localized("parent_dashboard_report_export_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.72))
            HStack(spacing: 10) {
                Button(localizationManager.localized("parent_dashboard_report_export_csv")) {
                    exportReport(.csv)
                }
                .buttonStyle(.borderedProminent)
                .accessibilityLabel(localizationManager.localized("parent_dashboard_report_export_csv"))
                .accessibilityHint(localizationManager.localized("parent_dashboard_report_export_csv_hint"))
                .accessibilityIdentifier("parent_dashboard_export_csv")

                Button(localizationManager.localized("parent_dashboard_report_export_pdf")) {
                    exportReport(.pdf)
                }
                .buttonStyle(.bordered)
                .accessibilityLabel(localizationManager.localized("parent_dashboard_report_export_pdf"))
                .accessibilityHint(localizationManager.localized("parent_dashboard_report_export_pdf_hint"))
                .accessibilityIdentifier("parent_dashboard_export_pdf")
            }
            if let exportError, !exportError.isEmpty {
                Text(exportError)
                    .font(.caption)
                    .foregroundColor(.orange.opacity(0.95))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var learnedPanelSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("parent_dashboard_learned_panel_title"))
                .font(.system(size: 18, weight: .semibold))
            Text(localizationManager.localized("parent_dashboard_learned_panel_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.74))
            if learnedSkillDeltas.isEmpty {
                Text(localizationManager.localized("parent_dashboard_learned_panel_empty"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
            } else {
                ForEach(learnedSkillDeltas) { delta in
                    HStack {
                        Text(localizationManager.localized(delta.categoryId))
                        Spacer()
                        Text("\(delta.deltaPercent >= 0 ? "+" : "")\(delta.deltaPercent)%")
                            .fontWeight(.semibold)
                    }
                    .font(.system(size: 13, weight: .medium))
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_learned_panel")
    }

    private var masteryLevelsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("parent_dashboard_mastery_title"))
                .font(.system(size: 18, weight: .semibold))
            if masteryTopics.isEmpty {
                Text(localizationManager.localized("parent_dashboard_mastery_empty"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
            } else {
                ForEach(masteryTopics) { row in
                    HStack {
                        Text(localizationManager.localized(row.categoryId))
                        Spacer()
                        Text(localizationManager.localized(row.level.localizationKey))
                            .font(.system(size: 12, weight: .semibold))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(Color.white.opacity(0.16))
                            .clipShape(Capsule())
                    }
                    .font(.system(size: 13, weight: .medium))
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_mastery_levels")
    }

    private var roiSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("parent_dashboard_roi_title"))
                .font(.system(size: 18, weight: .semibold))
            Text(localizationManager.localized("parent_dashboard_roi_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.72))
            if roiRows.isEmpty {
                Text(localizationManager.localized("parent_dashboard_roi_empty"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
            } else {
                ForEach(roiRows.prefix(4)) { row in
                    HStack {
                        Text(localizationManager.localized(row.categoryId))
                        Spacer()
                        Text(String(format: "%.2f", row.roiScore))
                            .fontWeight(.semibold)
                    }
                    .font(.system(size: 13, weight: .medium))
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_roi_filter")
    }

    private var autoDigestSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("parent_dashboard_auto_digest_title"))
                .font(.system(size: 18, weight: .semibold))
            Text(localizationManager.localized("parent_dashboard_auto_digest_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.72))
            ForEach(Array(digestAutoLines.enumerated()), id: \.offset) { _, line in
                Text(line)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.88))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_auto_digest")
    }

    private func toggleFilter(_ type: ContentItemType) {
        if allowedTypes.contains(type) {
            allowedTypes.remove(type)
        } else {
            allowedTypes.insert(type)
        }
        Task { await reloadReports() }
    }

    private func reportRowTitle(_ item: ActivityReportItem) -> String {
        localizationManager.localized(item.titleKey)
    }

    private func contentTypeLocalizationKey(_ type: ContentItemType) -> String {
        switch type {
        case .game: return "parent_dashboard_content_type_game"
        case .lesson: return "parent_dashboard_content_type_lesson"
        case .video: return "parent_dashboard_content_type_video"
        case .story: return "parent_dashboard_content_type_story"
        case .song: return "parent_dashboard_content_type_song"
        case .drawing: return "parent_dashboard_content_type_drawing"
        case .safety: return "parent_dashboard_content_type_safety"
        case .career: return "parent_dashboard_content_type_career"
        }
    }

    private func buildExportModel() -> ParentDashboardReportModel {
        let days = trendWindow.dayCount
        let trend = ParentActivityDailyAggregator.shared.trendPoints(lastCalendarDays: days)
        let dayFmt = DateFormatter()
        dayFmt.locale = Locale(identifier: "en_US_POSIX")
        dayFmt.timeZone = TimeZone.current
        dayFmt.dateFormat = "yyyy-MM-dd"
        let trendRows = trend.map { (dayFmt.string(from: $0.dayStart), $0.opens, $0.completions, max($0.usedSeconds / 60, 0)) }
        let summaryRows = reports.map { (reportRowTitle($0), $0.value) }
        return ParentDashboardReportModel(
            generatedAt: Date(),
            reportTitle: localizationManager.localized("parent_dashboard_report_file_title"),
            generatedLabel: localizationManager.localized("parent_dashboard_report_generated"),
            summarySectionTitle: localizationManager.localized("parent_dashboard_report_section_summary"),
            summaryRows: summaryRows,
            trendsSectionTitle: localizationManager.localized("parent_dashboard_report_section_trends"),
            trendWindowLabel: trendWindow == .week
                ? localizationManager.localized("parent_dashboard_trends_week")
                : localizationManager.localized("parent_dashboard_trends_month"),
            trendColumnDay: localizationManager.localized("parent_dashboard_report_col_day"),
            trendColumnOpens: localizationManager.localized("parent_dashboard_report_col_opens"),
            trendColumnCompletions: localizationManager.localized("parent_dashboard_report_col_completions"),
            trendColumnUsedMinutes: localizationManager.localized("parent_dashboard_report_col_used_minutes"),
            trendRows: trendRows
        )
    }

    private func exportReport(_ format: ParentDashboardReportFormat) {
        exportError = nil
        Task {
            let model = await MainActor.run { buildExportModel() }
            do {
                let url = try ParentDashboardReportExporter.buildTemporaryFile(model: model, format: format)
                await MainActor.run {
                    shareDocument = ParentShareDocument(url: url)
                }
            } catch {
                await MainActor.run {
                    exportError = localizationManager.localized(
                        "parent_dashboard_report_export_failed",
                        error.localizedDescription
                    )
                }
            }
        }
    }

    private func reloadReports() async {
        let windowDays = await MainActor.run { trendWindow.dayCount }
        let snapshot = ContentManager.shared.parentDashboardSnapshot()
        let feed = await ContentManager.shared.loadFeed(
            categoryIds: [ChildCategoryKey.games, ChildCategoryKey.study, ElderlyCategoryKey.health, ElderlyCategoryKey.safety],
            limit: 50
        )
        let filtered = ContentFilters.shared.filtered(items: feed, allowedTypes: allowedTypes)

        var base = ActivityReports.shared.build(from: snapshot)
        base.append(.init(id: "filtered_count", titleKey: "parent_dashboard_metric_filtered_items", value: "\(filtered.count)"))
        let mirror = buildMirrorOverview()
        let trend = ParentActivityDailyAggregator.shared.trendPoints(lastCalendarDays: windowDays)
        let insights = await buildParentInsights(feed: feed)

        await MainActor.run {
            filteredItemsCount = filtered.count
            reports = base
            mirrorOverview = mirror
            trendPoints = trend
            digestLines = ActivityDigestService.buildLiveDigestLines(localizationManager: localizationManager)
            learnedSkillDeltas = insights.learnedDeltas
            masteryTopics = insights.masteryTopics
            roiRows = insights.roiRows
            digestAutoLines = insights.autoDigest
        }
    }

    private func buildParentInsights(feed: [ContentItem]) async -> ParentInsightsBundle {
        let focusCategories = [
            ChildCategoryKey.games,
            ChildCategoryKey.study,
            ChildCategoryKey.safety,
            ChildCategoryKey.cartoons,
            ChildCategoryKey.programming,
            ChildCategoryKey.social,
            ChildCategoryKey.music,
            ChildCategoryKey.education
        ]

        var grouped: [String: [Double]] = [:]
        var roiByCategory: [String: Double] = [:]

        for item in feed where focusCategories.contains(item.categoryId) {
            let progress = await ContentManager.shared.loadProgress(contentId: item.id)
            let percent = progress?.completionPercent ?? 0
            grouped[item.categoryId, default: []].append(percent)
            let minutes = max(1.0, Double(item.metadata.estimatedDurationSec ?? 300) / 60.0)
            roiByCategory[item.categoryId, default: 0] += Double(percent) / minutes
        }

        var deltas: [ParentSkillDelta] = []
        var masteryRows: [ParentMasteryTopic] = []
        var roiRows: [ParentROIRow] = []

        for category in focusCategories {
            let values = grouped[category] ?? []
            let avg = values.isEmpty ? 0.0 : values.reduce(0, +) / Double(values.count)
            let baselineKey = "parent.learned.baseline.\(category)"
            let baseline = UserDefaults.standard.double(forKey: baselineKey)
            let delta = Int((avg - baseline).rounded())
            UserDefaults.standard.set(avg, forKey: baselineKey)
            deltas.append(.init(categoryId: category, deltaPercent: delta))
            masteryRows.append(.init(categoryId: category, level: ParentMasteryLevel.from(averagePercent: avg)))
            roiRows.append(.init(categoryId: category, roiScore: roiByCategory[category] ?? 0))
        }

        deltas.sort { $0.deltaPercent > $1.deltaPercent }
        masteryRows.sort { $0.categoryId < $1.categoryId }
        roiRows.sort { $0.roiScore > $1.roiScore }

        let achievements = deltas.prefix(3).map {
            "\(localizationManager.localized("parent_dashboard_auto_digest_achievement_prefix")) \(localizationManager.localized($0.categoryId)) (\($0.deltaPercent >= 0 ? "+" : "")\($0.deltaPercent)%)"
        }
        let risk = deltas.last.map {
            "\(localizationManager.localized("parent_dashboard_auto_digest_risk_prefix")) \(localizationManager.localized($0.categoryId))"
        } ?? localizationManager.localized("parent_dashboard_auto_digest_risk_fallback")
        let recommendationCategory = roiRows.first?.categoryId ?? ChildCategoryKey.study
        let recommendation = "\(localizationManager.localized("parent_dashboard_auto_digest_recommendation_prefix")) \(localizationManager.localized(recommendationCategory))"
        let autoDigest = achievements + [risk, recommendation]

        return ParentInsightsBundle(
            learnedDeltas: Array(deltas.prefix(6)),
            masteryTopics: masteryRows,
            roiRows: roiRows,
            autoDigest: autoDigest
        )
    }

    private func runSensitiveAction(_ action: @escaping () -> Void) {
        Task {
            let ok = await ParentSessionGate.confirmSensitiveAction()
            await MainActor.run {
                if ok {
                    action()
                } else {
                    dsarMessage = localizationManager.localized("parent_dashboard_dsar_verify_incomplete")
                }
            }
        }
    }

    private var mirrorOverviewSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("parent_dashboard_mirror_title"))
                .font(.system(size: 18, weight: .semibold))

            Text(localizationManager.localized("parent_dashboard_mirror_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.72))

            mirrorAudienceBlock(
                title: localizationManager.localized("parent_dashboard_mirror_child_title"),
                categories: mirrorOverview.childVisibleCategoryIds
            )
            mirrorAudienceBlock(
                title: localizationManager.localized("parent_dashboard_mirror_elderly_title"),
                categories: mirrorOverview.elderlyVisibleCategoryIds
            )

            HStack(spacing: 8) {
                Text(localizationManager.localized("parent_dashboard_mirror_permissions_title"))
                    .font(.system(size: 13, weight: .semibold))
                Text(permissionSummary(from: mirrorOverview.permissionSnapshot))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.86))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func mirrorAudienceBlock(title: String, categories: [String]) -> some View {
        let names = categories.map { localizationManager.localized($0) }
        return VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.system(size: 14, weight: .semibold))
            Text(names.joined(separator: " • "))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.86))
                .lineLimit(3)
                .minimumScaleFactor(0.8)
        }
    }

    private func buildMirrorOverview(defaults: UserDefaults = .standard) -> ParentMirrorOverview {
        let members = UnifiedFamilyRoster.load(defaults: defaults)
        let snapshot = FamilyPermissionLayer.snapshot(members: members, defaults: defaults)
        let child = [
            ChildCategoryKey.safety,
            ChildCategoryKey.games,
            ChildCategoryKey.study,
            ChildCategoryKey.education
        ]
        let elderly = FamilyContentSafetyBridge.resolvedElderlyCategories(defaults: defaults)
        return ParentMirrorOverview(
            childVisibleCategoryIds: child,
            elderlyVisibleCategoryIds: elderly,
            permissionSnapshot: snapshot
        )
    }

    private func permissionSummary(from snapshot: FamilyPermissionLayer.Snapshot) -> String {
        let states: [String] = [
            "\(localizationManager.localized("parent_dashboard_perm_contacts")): \(snapshot.canEditContacts ? localizationManager.localized("parent_dashboard_perm_allowed") : localizationManager.localized("parent_dashboard_perm_blocked"))",
            "\(localizationManager.localized("parent_dashboard_perm_limits")): \(snapshot.canManageFamilyLimits ? localizationManager.localized("parent_dashboard_perm_allowed") : localizationManager.localized("parent_dashboard_perm_blocked"))",
            "\(localizationManager.localized("parent_dashboard_perm_critical")): \(snapshot.canManageCriticalFamilySettings ? localizationManager.localized("parent_dashboard_perm_allowed") : localizationManager.localized("parent_dashboard_perm_blocked"))"
        ]
        return states.joined(separator: " • ")
    }
}

private enum ParentDashboardTrendWindow: String, CaseIterable, Identifiable {
    case week
    case month

    var id: String { rawValue }

    var dayCount: Int {
        switch self {
        case .week: return 7
        case .month: return 30
        }
    }
}

private struct ParentDashboardTrendSection: View {
    let localizationManager: LocalizationManager
    @Binding var window: ParentDashboardTrendWindow
    let points: [ParentDashboardDayPoint]

    private static let dayLabelFormatter: DateFormatter = {
        let f = DateFormatter()
        f.setLocalizedDateFormatFromTemplate("EEEd")
        return f
    }()

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("parent_dashboard_trends_title"))
                .font(.system(size: 18, weight: .semibold))

            Picker("", selection: $window) {
                Text(localizationManager.localized("parent_dashboard_trends_week")).tag(ParentDashboardTrendWindow.week)
                Text(localizationManager.localized("parent_dashboard_trends_month")).tag(ParentDashboardTrendWindow.month)
            }
            .pickerStyle(.segmented)
            .labelsHidden()

            HStack(spacing: 12) {
                legendDot(color: .blue, text: localizationManager.localized("parent_dashboard_trends_opens"))
                legendDot(color: .green, text: localizationManager.localized("parent_dashboard_trends_completions"))
                legendDot(color: .orange, text: localizationManager.localized("parent_dashboard_trends_time_min"))
            }
            .font(.system(size: 11, weight: .medium))
            .foregroundColor(.white.opacity(0.9))

            if points.allSatisfy({ $0.opens == 0 && $0.completions == 0 && $0.usedSeconds == 0 }) {
                Text(localizationManager.localized("parent_dashboard_trends_empty"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
                    .padding(.vertical, 6)
            }

            Group {
                if window == .month {
                    ScrollView(.horizontal, showsIndicators: false) {
                        trendBarRow(points: points, compact: true)
                            .frame(minWidth: CGFloat(max(points.count, 1)) * 22)
                    }
                } else {
                    trendBarRow(points: points, compact: false)
                }
            }
            .frame(minHeight: 118)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func legendDot(color: Color, text: String) -> some View {
        HStack(spacing: 6) {
            Circle()
                .fill(color.opacity(0.9))
                .frame(width: 8, height: 8)
            Text(text)
        }
    }

    private func trendBarRow(points: [ParentDashboardDayPoint], compact: Bool) -> some View {
        let chartH: CGFloat = 88
        let maxO = max(points.map(\.opens).max() ?? 0, 1)
        let maxC = max(points.map(\.completions).max() ?? 0, 1)
        let maxMin = max(points.map { max($0.usedSeconds / 60, 0) }.max() ?? 0, 1)
        let barW: CGFloat = compact ? 3.5 : 6

        return HStack(alignment: .bottom, spacing: compact ? 3 : 6) {
            ForEach(points) { p in
                let oRatio = CGFloat(p.opens) / CGFloat(maxO)
                let cRatio = CGFloat(p.completions) / CGFloat(maxC)
                let mRatio = CGFloat(max(p.usedSeconds / 60, 0)) / CGFloat(maxMin)
                VStack(spacing: 4) {
                    ZStack(alignment: .bottom) {
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.white.opacity(0.06))
                            .frame(height: chartH)
                        HStack(alignment: .bottom, spacing: 2) {
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.blue.opacity(0.88))
                                .frame(width: barW, height: max(2, chartH * oRatio))
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.green.opacity(0.88))
                                .frame(width: barW, height: max(2, chartH * cRatio))
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.orange.opacity(0.88))
                                .frame(width: barW, height: max(2, chartH * mRatio))
                        }
                        .padding(.bottom, 0)
                    }
                    .frame(height: chartH)

                    Text(Self.dayLabelFormatter.string(from: p.dayStart))
                        .font(.system(size: compact ? 8 : 9, weight: .medium))
                        .foregroundColor(.white.opacity(0.75))
                        .lineLimit(1)
                        .minimumScaleFactor(0.65)
                }
                .frame(maxWidth: .infinity)
            }
        }
    }
}

private struct ParentMirrorOverview {
    let childVisibleCategoryIds: [String]
    let elderlyVisibleCategoryIds: [String]
    let permissionSnapshot: FamilyPermissionLayer.Snapshot

    static let empty = ParentMirrorOverview(
        childVisibleCategoryIds: [],
        elderlyVisibleCategoryIds: [],
        permissionSnapshot: FamilyPermissionLayer.snapshot(members: [])
    )
}

private struct ParentSkillDelta: Identifiable {
    let id = UUID()
    let categoryId: String
    let deltaPercent: Int
}

private enum ParentMasteryLevel {
    case introduced
    case practicing
    case mastered

    var localizationKey: String {
        switch self {
        case .introduced: return "parent_dashboard_mastery_level_introduced"
        case .practicing: return "parent_dashboard_mastery_level_practicing"
        case .mastered: return "parent_dashboard_mastery_level_mastered"
        }
    }

    static func from(averagePercent: Double) -> ParentMasteryLevel {
        if averagePercent >= 75 { return .mastered }
        if averagePercent >= 30 { return .practicing }
        return .introduced
    }
}

private struct ParentMasteryTopic: Identifiable {
    let id = UUID()
    let categoryId: String
    let level: ParentMasteryLevel
}

private struct ParentROIRow: Identifiable {
    let id = UUID()
    let categoryId: String
    let roiScore: Double
}

private struct ParentInsightsBundle {
    let learnedDeltas: [ParentSkillDelta]
    let masteryTopics: [ParentMasteryTopic]
    let roiRows: [ParentROIRow]
    let autoDigest: [String]
}

private struct ParentShareDocument: Identifiable {
    let id = UUID()
    let url: URL
}


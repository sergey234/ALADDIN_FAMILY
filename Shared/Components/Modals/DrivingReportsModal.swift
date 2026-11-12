import SwiftUI
import UIKit
import CoreLocation
import CoreMotion
import MapKit

/**
 * 🚗 Driving Reports Modal
 * Модальное окно для просмотра детальных отчетов о вождении
 * Включает селектор пользователя, статистику, графики и историю поездок
 * Поддерживает выбор системы позиционирования (GPS/ГЛОНАСС/Galileo/BeiDou)
 */

struct DrivingReportsModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var analyticsViewModel: AnalyticsViewModel
    @StateObject private var positioningService = PositioningSystemService.shared
    @StateObject private var viewModel = DrivingReportsViewModel()
    
    // ✅ ИНТЕГРАЦИЯ LocationManager
    @StateObject private var locationManager = LocationManager.shared
    
    // Выбранный пользователь
    @AppStorage("driving_reports_selected_user_id") private var selectedUserId: String = ""
    @State private var users: [UserSelectorView.UserOption] = []
    @State private var currentUserId: String = "current"
    @State private var isLoadingUsers: Bool = false
    
    // Фильтры
    @AppStorage("driving_reports_period") private var selectedPeriod: String = "week"
    @State private var selectedFilter: FilterType = .all
    @State private var showPositioningSystemPicker: Bool = false
    @State private var explainKind: DriveIncidentKind?
    @State private var sharePDFItems: [Any] = []
    @State private var showSharePDF = false
    /// Play A — real trip metrics playback (no invented GPS points).
    @State private var playbackReport: DrivingReport?
    /// Wave B tip · Where→Езда→отчёты (strings `asc_tip_driving_reports_*`).
    @AppStorage("asc_tip_driving_reports_dismissed") private var drivingReportsTipDismissed = false
    
    enum FilterType: String, CaseIterable {
        case all = "all"
        case withViolations = "with_violations"
        case withoutViolations = "without_violations"
        
        func displayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .all: return localizationManager.localized("driving_reports_filter_all")
            case .withViolations: return localizationManager.localized("driving_reports_filter_with_violations")
            case .withoutViolations: return localizationManager.localized("driving_reports_filter_without_violations")
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            modalContent
            .navigationTitle(localizationManager.localized("driving_reports_modal_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isPresented = false
                    }) {
                        Text(localizationManager.localized("common_done"))
                            .foregroundColor(.primaryBlue)
                    }
                }
            }
        }
        .task {
            await loadUsers()
            await reloadDrivingData()
            // System Motion dialog — ALADDIN appears under Motion & Fitness once requested.
            _ = await SensitivePermissionCoordinator.requestMotionIfNeeded()
        }
        .onChange(of: selectedPeriod) { _ in
            Task { await reloadDrivingData() }
        }
        .onChange(of: selectedUserId) { _ in
            Task { await reloadDrivingData() }
        }
        .overlay(alignment: .center) {
            loadingOverlay
        }
        .overlay(alignment: .bottom) {
            errorOverlay
        }
        // ✅ ИСПРАВЛЕНИЕ: Добавляем VisualLogView на модальное окно
        .withVisualLogger()
        .sheet(isPresented: $showPositioningSystemPicker) {
            PositioningSystemPickerView(
                selectedSystem: Binding(
                    get: { positioningService.selectedSystem },
                    set: { newSystem in
                        positioningService.saveSelectedSystem(newSystem)
                    }
                ),
                currentSystem: positioningService.currentSystem,
                currentRegion: positioningService.currentRegionName
            )
            .environmentObject(localizationManager)
        }
        .sheet(item: $explainKind) { kind in
            driveIncidentExplainSheet(kind)
        }
        .sheet(isPresented: $showSharePDF) {
            ShareSheet(activityItems: sharePDFItems)
        }
        .sheet(item: $playbackReport) { report in
            DrivingTripPlaybackSheet(report: report)
                .environmentObject(localizationManager)
        }
    }

    private var selectedUserBinding: Binding<String?> {
        Binding(
            get: { selectedUserId.isEmpty ? nil : selectedUserId },
            set: { newValue in
                selectedUserId = newValue ?? currentUserId
                Task { await reloadDrivingData() }
            }
        )
    }

    private var resolvedMemberId: String {
        let id = selectedUserId.trimmingCharacters(in: .whitespacesAndNewlines)
        if !id.isEmpty { return id }
        return currentUserId
    }

    private var selectedMemberName: String {
        if let u = users.first(where: { $0.id == resolvedMemberId }) {
            return u.name
        }
        return FamilyDrivingTripLedger.currentDeviceMember().name
    }

    private var filteredReports: [DrivingReport] {
        switch selectedFilter {
        case .all:
            return viewModel.reports
        case .withViolations:
            return viewModel.reports.filter { !$0.violations.isEmpty }
        case .withoutViolations:
            return viewModel.reports.filter { $0.violations.isEmpty }
        }
    }

    private var isViewingOtherFamilyMember: Bool {
        let device = FamilyDrivingTripLedger.currentDeviceMember().id
        let selected = resolvedMemberId
        guard !selected.isEmpty, selected != "current" else { return false }
        guard !device.isEmpty, device != "current" else { return false }
        return selected != device
    }

    @MainActor
    private func reloadDrivingData() async {
        await viewModel.loadReports(userId: resolvedMemberId, period: selectedPeriod)
        // HUB-P1.7 — backfill street names for any leftover lat/lon labels, then refresh list.
        let needEnrich = viewModel.reports.filter {
            FamilyDrivingTripLedger.looksLikeCoordinatePair($0.startLocation)
                || FamilyDrivingTripLedger.looksLikeCoordinatePair($0.endLocation)
        }
        if !needEnrich.isEmpty {
            for report in needEnrich.prefix(12) {
                await FamilyDrivingTripLedger.enrichStreetLabels(for: report)
            }
            await viewModel.loadReports(userId: resolvedMemberId, period: selectedPeriod)
        }
    }

    private var modalContent: some View {
        ZStack {
            AladdinSnowballPalette.canvasGradient
                .ignoresSafeArea()

            ScrollView(.vertical, showsIndicators: false) {
                VStack(spacing: Spacing.l) {
                    if !users.isEmpty || currentUserId != "" {
                        UserSelectorView(
                            selectedUserId: selectedUserBinding,
                            users: users,
                            currentUserId: currentUserId,
                            showCurrentUser: true
                        )
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.m)
                    }

                    /// JOB03 CapCut · Gold SUV · UI 112×112 · Driving sheet hero (H18).
                    drivingHeroSUVRow
                        .padding(.horizontal, Spacing.screenPadding)

                    if !drivingReportsTipDismissed {
                        drivingReportsTipCard
                            .padding(.horizontal, Spacing.screenPadding)
                    }

                    positioningSystemSelector
                        .padding(.horizontal, Spacing.screenPadding)

                    if let stats = viewModel.stats {
                        statsSection(stats: stats)
                            .padding(.horizontal, Spacing.screenPadding)
                        weeklyIncidentStrip(stats: stats)
                            .padding(.horizontal, Spacing.screenPadding)
                        exportPDFButton(stats: stats)
                            .padding(.horizontal, Spacing.screenPadding)
                    } else if !viewModel.isLoading {
                        weeklyIncidentStrip(stats: nil)
                            .padding(.horizontal, Spacing.screenPadding)
                    }

                    filtersSection
                        .padding(.horizontal, Spacing.screenPadding)

                    if !filteredReports.isEmpty {
                        tripsHistorySection
                            .padding(.horizontal, Spacing.screenPadding)
                    } else if !viewModel.isLoading {
                        emptyStateView
                            .padding(.horizontal, Spacing.screenPadding)
                    }

                    Spacer(minLength: 100)
                }
                .padding(.top, Spacing.m)
            }
        }
    }

    @ViewBuilder
    private var loadingOverlay: some View {
        if viewModel.isLoading {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                .padding()
                .background(Color.backgroundMedium.opacity(0.85))
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
        }
    }

    @ViewBuilder
    private var errorOverlay: some View {
        if let error = viewModel.errorMessage {
            HStack {
                Text(error)
                    .font(.footnote)
                    .foregroundColor(.white)
                Spacer()
                Button(action: {
                    // Retry перезапускает общий orchestrator аналитики
                    analyticsViewModel.startLoad()
                }) {
                    Text(localizationManager.localized("common_retry"))
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                        .padding(.horizontal, Spacing.s)
                        .padding(.vertical, Spacing.xs)
                        .background(Color.white.opacity(0.2))
                        .clipShape(Capsule())
                }
            }
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
            .background(Color.dangerRed.opacity(0.9))
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .shadow(radius: 6)
            .padding(.bottom, Spacing.l)
        }
    }
    
    // MARK: - Positioning System Selector
    
    private var positioningSystemSelector: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("positioning_system_title"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            HStack {
                // Текущая система
                HStack(spacing: Spacing.xs) {
                    Image(systemName: positioningService.currentSystem.icon)
                        .font(.caption)
                    Text(positioningService.currentSystem.localizedDisplayName(localizationManager))
                        .font(.caption)
                }
                .foregroundColor(.textSecondary)
                .padding(.horizontal, Spacing.s)
                .padding(.vertical, Spacing.xs)
                .background(
                    Capsule()
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
                
                Spacer()
                
                // Кнопка изменения
                Button(action: {
                    showPositioningSystemPicker = true
                }) {
                    Text(localizationManager.localized("common_change"))
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                }
            }
            
            // Рекомендация
            if positioningService.selectedSystem == .auto {
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "info.circle.fill")
                        .font(.caption2)
                        .foregroundColor(.infoBlue)
                    Text(localizationManager.localized("positioning_system_recommended"))
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Stats Section
    
    private func statsSection(stats: DrivingStats) -> some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("driving_reports_stats_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)

            // QA-06 A: 2×2 grid, short labels; score shown in full (e.g. 4.0/10).
            LazyVGrid(
                columns: [
                    GridItem(.flexible(), spacing: Spacing.s),
                    GridItem(.flexible(), spacing: Spacing.s)
                ],
                spacing: Spacing.s
            ) {
                statCard(
                    icon: "🚗",
                    title: localizationManager.localized("driving_stat_trips_short"),
                    value: "\(stats.totalTrips)"
                )
                statCard(
                    icon: "⭐",
                    title: localizationManager.localized("driving_stat_score_short"),
                    value: stats.formattedAverageSafetyScore
                )
                statCard(
                    icon: "⚠️",
                    title: localizationManager.localized("driving_stat_risks_short"),
                    value: "\(stats.violationsCount)"
                )
                statCard(
                    icon: "🛣",
                    title: localizationManager.localized("driving_stat_km_short"),
                    value: String(format: "%.0f", stats.totalDistance)
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func statCard(icon: String, title: String, value: String) -> some View {
        VStack(spacing: Spacing.xs) {
            Text(icon)
                .font(.system(size: 22))
            
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .lineLimit(1)
                .minimumScaleFactor(0.75)
            
            Text(title)
                .font(.caption2.weight(.semibold))
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(1)
                .minimumScaleFactor(0.85)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Filters Section
    
    private var filtersSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("driving_reports_filter_period"))
                .font(AladdinFamilyType.subheadline(weight: .bold))
                .foregroundColor(.textPrimary)
            
            HStack(spacing: Spacing.s) {
                periodButton("today", title: localizationManager.localized("driving_reports_filter_today"))
                periodButton("week", title: localizationManager.localized("driving_reports_filter_week"))
                periodButton("month", title: localizationManager.localized("driving_reports_filter_month"))
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func periodButton(_ period: String, title: String) -> some View {
        Button(action: {
            selectedPeriod = period
            Task { await reloadDrivingData() }
        }) {
            Text(title)
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(selectedPeriod == period ? .white : .textPrimary)
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
                .background(
                    Capsule()
                        .fill(selectedPeriod == period ? Color.primaryBlue : Color.backgroundMedium)
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Trips History Section
    
    private var tripsHistorySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("driving_reports_history_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(spacing: Spacing.s) {
                ForEach(filteredReports) { report in
                    Button {
                        HapticFeedback.selection()
                        playbackReport = report
                    } label: {
                        tripRow(report: report)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("driving_trip_play_\(report.id)")
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func tripRow(report: DrivingReport) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack(spacing: Spacing.s) {
                Image(systemName: "car.fill")
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized("trip_drive_mode"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.secondaryGold)
                Spacer()
                Text(report.startTime, style: .date)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Text(report.formattedSafetyScore)
                    .font(.caption.weight(.bold))
                    .foregroundColor(safetyScoreColor(report.safetyScore))
            }

            // S19b/f densitiy: HH:mm – HH:mm from real trip timestamps only.
            Text(
                String(
                    format: localizationManager.localized("driving_reports_time_range"),
                    Self.tripClock(report.startTime),
                    Self.tripClock(report.endTime)
                )
            )
            .font(.caption.weight(.semibold))
            .foregroundColor(.textSecondary)
            
            HStack(alignment: .top) {
                Text(Self.streetTitleWithoutAtPrefix(report.startLocation))
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                
                Image(systemName: "arrow.right")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .padding(.top, 4)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(Self.streetTitleWithoutAtPrefix(report.endLocation))
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .lineLimit(2)
                    HStack(spacing: 4) {
                        Image(systemName: "flag.checkered")
                            .font(.caption2)
                        Text(localizationManager.localized("trip_arrived"))
                            .font(.caption2.weight(.semibold))
                    }
                    .foregroundColor(.secondaryGold)
                }
            }

            // Densitiy A / GPS track: real samples or endpoints only — never invent mid-points.
            if report.hasGPSTrack || report.hasRouteEndpoints {
                TripEndpointMapPreview(report: DrivingTripTrackStore.mergeInto(report))
                    .frame(height: 120)
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    .accessibilityIdentifier(report.hasGPSTrack ? "trip_map_gps_track" : "trip_map_endpoints")
                if report.hasGPSTrack || DrivingTripTrackStore.load(tripId: report.id).count >= 2 {
                    Text(localizationManager.localized("trip_route_track_ready"))
                        .font(.caption2)
                        .foregroundColor(.secondaryGold)
                }
            } else {
                Text(localizationManager.localized("trip_no_map_track"))
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            // QA-04 A: 2×2 short metrics (км / мин / макс. км/ч / риски).
            LazyVGrid(
                columns: [
                    GridItem(.flexible(), spacing: Spacing.s),
                    GridItem(.flexible(), spacing: Spacing.s)
                ],
                spacing: Spacing.xs
            ) {
                tripMetricChip(
                    value: String(format: "%.1f", report.distance),
                    label: localizationManager.localized("driving_stat_km_short")
                )
                tripMetricChip(
                    value: "\(report.durationMinutes)",
                    label: localizationManager.localized("driving_stat_min_short")
                )
                tripMetricChip(
                    value: report.maxSpeed > 0
                        ? String(format: "%.0f", min(report.maxSpeed, 140))
                        : "—",
                    label: localizationManager.localized("driving_stat_max_kmh_short")
                )
                tripMetricChip(
                    value: "\(report.violations.count)",
                    label: localizationManager.localized("driving_stat_risks_short"),
                    emphasize: report.violations.count > 0
                )
            }

            HStack(spacing: Spacing.xs) {
                Image(systemName: "play.circle.fill")
                    .foregroundColor(.secondaryGold)
                Text(localizationManager.localized("trip_open_detail"))
                    .font(.caption.weight(.bold))
                    .foregroundColor(.secondaryGold)
            }
            .padding(.top, 2)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func tripMetricChip(value: String, label: String, emphasize: Bool = false) -> some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.subheadline.weight(.bold))
                .foregroundColor(emphasize ? .dangerRed : .textPrimary)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
            Text(label)
                .font(.caption2)
                .foregroundColor(.textSecondary)
                .lineLimit(1)
                .minimumScaleFactor(0.85)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 6)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.backgroundMedium.opacity(0.25))
        )
    }

    private func safetyScoreColor(_ score: Double) -> Color {
        if score >= 8 {
            return .successGreen
        } else if score >= 5 {
            return .warningOrange
        } else {
            return .dangerRed
        }
    }

    /// S19b — wall-clock for real trip bounds.
    private static func tripClock(_ date: Date) -> String {
        let f = DateFormatter()
        f.locale = .current
        f.dateFormat = "HH:mm"
        return f.string(from: date)
    }

    /// C1 — drop Life360-style «В » / «At » before street names.
    private static func streetTitleWithoutAtPrefix(_ raw: String) -> String {
        var s = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        for p in ["В ", "в ", "At ", "at ", "On ", "on "] where s.hasPrefix(p) {
            s = String(s.dropFirst(p.count)).trimmingCharacters(in: .whitespacesAndNewlines)
            break
        }
        return s
    }
    
    /// HUB-P0.1 — explicit feedback; Simulator often has no Motion dialog.
    @MainActor
    private func handleMotionPermissionTap() async {
        let before = CMMotionActivityManager.authorizationStatus()
        print("WHERE_PHONE motion tap before=\(before.rawValue) available=\(CMMotionActivityManager.isActivityAvailable())")
        guard CMMotionActivityManager.isActivityAvailable() else {
            ToastManager.shared.showInfo(localizationManager.localized("driving_motion_unavailable"))
            print("WHERE_PHONE motion tap → unavailable")
            return
        }
        if before == .authorized {
            ToastManager.shared.showSuccess(localizationManager.localized("driving_motion_already"))
            print("WHERE_PHONE motion tap → already authorized")
            return
        }
        let ok = await SensitivePermissionCoordinator.requestMotionIfNeeded()
        let after = CMMotionActivityManager.authorizationStatus()
        print("WHERE_PHONE motion tap after=\(after.rawValue) ok=\(ok)")
        if ok || after == .authorized {
            ToastManager.shared.showSuccess(localizationManager.localized("driving_motion_granted"))
            return
        }
        if after == .denied || after == .restricted {
            ToastManager.shared.showInfo(localizationManager.localized("driving_motion_denied"))
            if let url = URL(string: UIApplication.openSettingsURLString) {
                _ = await UIApplication.shared.open(url)
            }
            return
        }
        ToastManager.shared.showInfo(localizationManager.localized("driving_motion_unavailable"))
    }

    // MARK: - Empty State
    
    /// JOB03a CapCut · Gold SUV · transparent PNG · Driving hero (not Places/Events).
    private var drivingHeroSUVRow: some View {
        HStack(alignment: .center, spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized("component_driving_reports_title"))
                    .font(AladdinFamilyType.title3())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("driving_reports_empty_lead"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 8)
            Image("ICON_ALIVE_HERO_H18_SUV_Gold")
                .resizable()
                .scaledToFit()
                .frame(width: 112, height: 112)
                .accessibilityHidden(true)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("driving_reports_hero_suv_gold")
    }

    /// Tip under hero · dismiss once · keys already in Localizable.strings.
    private var drivingReportsTipCard: some View {
        HStack(alignment: .top, spacing: Spacing.m) {
            Image(systemName: "lightbulb.fill")
                .font(.title3.weight(.semibold))
                .foregroundColor(.secondaryGold)
                .accessibilityHidden(true)
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized("asc_tip_driving_reports_title"))
                    .font(AladdinFamilyType.subheadline(weight: .semibold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("asc_tip_driving_reports_body"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
            Button {
                HapticFeedback.selection()
                drivingReportsTipDismissed = true
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.55))
            }
            .buttonStyle(.plain)
            .accessibilityLabel(localizationManager.localized("asc_tip_driving_reports_dismiss"))
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .aladdinProductCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("driving_reports_asc_tip")
        .accessibilityElement(children: .contain)
    }

    private var emptyStateView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("driving_reports_empty"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .center)
                .multilineTextAlignment(.center)

            Text(
                isViewingOtherFamilyMember
                    ? localizationManager.localized("driving_reports_empty_other_member", selectedMemberName)
                    : localizationManager.localized("driving_reports_empty_lead")
            )
                .font(AladdinFamilyType.subheadline())
                .foregroundColor(.white.opacity(0.92))
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("driving_reports_why_motion"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
                Text(localizationManager.localized("driving_reports_why_location"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
                Text(localizationManager.localized("driving_reports_why_trip"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
            }

            Button {
                HapticFeedback.selection()
                Task { @MainActor in
                    await handleMotionPermissionTap()
                }
            } label: {
                Text(localizationManager.localized("driving_reports_enable_motion"))
                    .font(AladdinFamilyType.subheadline(weight: .semibold))
                    .foregroundColor(.backgroundDark)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Spacing.s)
                    .background(Color.secondaryGold)
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium, style: .continuous))
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("driving_reports_enable_motion")

            Button {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            } label: {
                Text(localizationManager.localized("driving_reports_open_settings_motion"))
                    .font(AladdinFamilyType.caption(weight: .semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("driving_reports_open_settings_motion")
        }
        .padding(Spacing.l)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    // MARK: - Card Background
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Error Banner
    
    private func errorBanner(message: String) -> some View {
        Text(message)
            .font(.footnote)
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
            .background(Color.dangerRed.opacity(0.9))
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .shadow(radius: 6)
    }
    
    // MARK: - Data Loading
    
    private func loadUsers() async {
        isLoadingUsers = true
        defer { isLoadingUsers = false }
        
        print("🔍 DrivingReportsModal: Начинаем загрузку пользователей...")
        
        do {
            // Загружаем список членов семьи из API
            let familyMembers: [FamilyMemberResponse] = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getFamilyMembers { result in
                    continuation.resume(with: result)
                }
            }
            
            print("✅ DrivingReportsModal: Загружено \(familyMembers.count) членов семьи из API")
            
            // Преобразуем в UserOption
            users = familyMembers.map { member in
                UserSelectorView.UserOption(
                    id: member.id,
                    name: member.name,
                    role: member.role,
                    avatar: member.avatar
                )
            }
            
            print("✅ DrivingReportsModal: Создано \(users.count) опций пользователей")
            
            // Устанавливаем текущего пользователя (первый родитель или текущий пользователь)
            if let currentUser = familyMembers.first(where: { $0.role == "parent" }) {
                currentUserId = currentUser.id
                print("✅ DrivingReportsModal: Текущий пользователь установлен: \(currentUser.name) (ID: \(currentUser.id))")
            } else if let firstMember = familyMembers.first {
                // Если нет родителя, используем первого члена семьи
                currentUserId = firstMember.id
                print("✅ DrivingReportsModal: Текущий пользователь установлен (первый член): \(firstMember.name) (ID: \(firstMember.id))")
            } else {
                // Если список пуст, используем "current"
                currentUserId = "current"
                print("⚠️ DrivingReportsModal: Список членов семьи пуст, используем 'current'")
            }
            
            // ✅ ИСПРАВЛЕНИЕ: Всегда пробуем загрузить из UserDefaults для синхронизации
            // Это гарантирует, что локально добавленные участники семьи будут видны
            print("🔄 DrivingReportsModal: Синхронизируем с UserDefaults...")
            await loadUsersFromUserDefaults()
            
            // Если список все еще пуст после синхронизации, используем только текущего пользователя
            if users.isEmpty {
                print("⚠️ DrivingReportsModal: Список пользователей пуст после синхронизации")
            }
            
        } catch {
            let errorDescription = error.localizedDescription
            print("❌ DrivingReportsModal: Ошибка загрузки членов семьи из API: \(errorDescription)")
            print("   Тип ошибки: \(type(of: error))")
            
            // ✅ ИСПРАВЛЕНИЕ 4: Проверяем тип ошибки
            let networkError = NetworkError.from(error)
            if case .unauthorized = networkError {
                print("⚠️ DrivingReportsModal: Ошибка авторизации - используем только кэшированные данные")
                // Не показываем ошибку пользователю, просто используем fallback
            }
            
            // Пробуем загрузить из UserDefaults как fallback
            await loadUsersFromUserDefaults()
            
            // Если и из UserDefaults ничего не загрузилось, используем только текущего пользователя
            if users.isEmpty {
                currentUserId = "current"
                print("⚠️ DrivingReportsModal: Используем только текущего пользователя (fallback)")
            }
        }
        
        print("✅ DrivingReportsModal: Загрузка пользователей завершена. Всего: \(users.count), текущий: \(currentUserId)")
        
        // ✅ ИСПРАВЛЕНИЕ 3: Синхронизируем selectedUserId с currentUserId если он пустой (один раз в конце)
        if selectedUserId.isEmpty && !currentUserId.isEmpty {
            selectedUserId = currentUserId
            print("✅ DrivingReportsModal: selectedUserId синхронизирован с currentUserId: \(currentUserId)")
        }
    }
    
    /// Загрузка пользователей из UserDefaults как fallback
    private func loadUsersFromUserDefaults() async {
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Синхронизируем UserDefaults перед чтением
        UserDefaults.standard.synchronize()
        
        let familyMembersKey = "family_members_list"
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            
            print("✅ DrivingReportsModal: Загружено \(decoded.count) членов семьи из UserDefaults")
            
            // ✅ ИСПРАВЛЕНИЕ: Объединяем с существующими пользователями, избегая дубликатов
            let userDefaultsUsers: [UserSelectorView.UserOption] = decoded.map { member -> UserSelectorView.UserOption in
                // Преобразуем FamilyRole в строку для UserOption
                let roleString: String
                switch member.role {
                case .parent: roleString = "parent"
                case .child: roleString = "child"
                case .teenager: roleString = "teenager"
                case .elderly: roleString = "elderly"
                }
                
                return UserSelectorView.UserOption(
                    id: member.id,
                    name: member.name,
                    role: roleString,
                    avatar: member.avatar
                )
            }
            
            // Объединяем списки, избегая дубликатов по id
            let existingIds = Set(users.map { $0.id })
            let newUsers = userDefaultsUsers.filter { !existingIds.contains($0.id) }
            users.append(contentsOf: newUsers)
            
            print("✅ DrivingReportsModal: Добавлено \(newUsers.count) новых пользователей из UserDefaults. Всего: \(users.count)")
            
            // Устанавливаем текущего пользователя (первый родитель или первый член)
            if currentUserId == "current" || currentUserId.isEmpty {
            if let currentUser = decoded.first(where: { $0.role == .parent }) {
                currentUserId = currentUser.id
                print("✅ DrivingReportsModal: Текущий пользователь из UserDefaults: \(currentUser.name)")
            } else if let firstMember = decoded.first {
                currentUserId = firstMember.id
                print("✅ DrivingReportsModal: Текущий пользователь из UserDefaults (первый): \(firstMember.name)")
                }
            }
        } else {
            print("⚠️ DrivingReportsModal: Нет данных в UserDefaults")
        }
    }
    
    private func loadReports() {
        Task { await reloadDrivingData() }
    }

    // MARK: - W3 Q02–Q06 weekly strip + PDF

    private func weeklyIncidentStrip(stats: DrivingStats?) -> some View {
        let entitled = FamilyMapLiveAccess.isEntitled
        let counts = incidentCounts(from: stats, entitled: entitled)
        return VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("drive_weekly_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)

            // S58 densitiy: real trips/km when present (never invent).
            if let stats, stats.totalTrips > 0 {
                HStack(spacing: Spacing.s) {
                    weeklyStatChip(
                        title: String(
                            format: localizationManager.localized("drive_weekly_stats_trips"),
                            stats.totalTrips
                        ),
                        subtitle: String(
                            format: localizationManager.localized("drive_weekly_stats_km"),
                            stats.totalDistance
                        )
                    )
                    weeklyStatChip(
                        title: localizationManager.localized("drive_weekly_stats_max"),
                        subtitle: localizationManager.localized("drive_weekly_stats_max_na")
                    )
                }
                if entitled, stats.violationsCount > 0 {
                    Text(
                        String(
                            format: localizationManager.localized("drive_weekly_violations_total"),
                            stats.violationsCount
                        )
                    )
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                }
            } else {
                Text(localizationManager.localized("drive_no_trips"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
            }

            if !entitled {
                // S58 tariff gate — honest lock, no fake Life360 risk counts.
                // JOB04 CapCut · H16 GoldLock · UI 140×140 · Driving soft-paywall.
                Button {
                    HapticFeedback.selection()
                    navigationManager.navigateTo(.tariffs)
                } label: {
                    HStack(alignment: .center, spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(localizationManager.localized("drive_weekly_locked_title"))
                                .font(AladdinFamilyType.subheadline(weight: .semibold))
                                .foregroundColor(.textPrimary)
                            Text(localizationManager.localized("drive_weekly_locked_body"))
                                .font(AladdinFamilyType.caption())
                                .foregroundColor(.white.opacity(0.92))
                                .fixedSize(horizontal: false, vertical: true)
                            Text(localizationManager.localized("drive_weekly_locked_cta"))
                                .font(AladdinFamilyType.caption(weight: .bold))
                                .foregroundColor(.secondaryGold)
                                .padding(.top, 2)
                        }
                        Spacer(minLength: 8)
                        Image("ICON_ALIVE_HERO_H16_GoldLock")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 140, height: 140)
                            .accessibilityHidden(true)
                    }
                    .padding(Spacing.m)
                    .aladdinProductCard(cornerRadius: CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("drive_weekly_tariff_gate")
            }

            HStack(spacing: Spacing.s) {
                ForEach(DriveIncidentKind.allCases) { kind in
                    Button {
                        explainKind = kind
                    } label: {
                        VStack(spacing: 4) {
                            Text(kind.emoji)
                                .font(.title2)
                            if entitled {
                                Text("\(counts[kind] ?? 0)")
                                    .font(.headline.weight(.bold))
                                    .foregroundColor(.textPrimary)
                            } else {
                                Image(systemName: "lock.fill")
                                    .font(.headline)
                                    .foregroundColor(.secondaryGold)
                            }
                            Text(localizationManager.localized(kind.titleKey))
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.92))
                                .multilineTextAlignment(.center)
                                .lineLimit(2)
                                .minimumScaleFactor(0.8)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.s)
                        .stormGlassCard(cornerRadius: CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("drive_inc_\(kind.rawValue)")
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
        .accessibilityIdentifier("drive_weekly_incident_strip")
    }

    private func weeklyStatChip(title: String, subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundColor(.textPrimary)
                .lineLimit(2)
                .minimumScaleFactor(0.8)
            Text(subtitle)
                .font(.caption2)
                .foregroundColor(.textSecondary)
                .lineLimit(2)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    /// Honest counts: aggregate violations only on speed when entitled; never invent per-type splits.
    private func incidentCounts(from stats: DrivingStats?, entitled: Bool) -> [DriveIncidentKind: Int] {
        guard entitled, let stats else {
            return Dictionary(uniqueKeysWithValues: DriveIncidentKind.allCases.map { ($0, 0) })
        }
        return [
            .phone: 0,
            .speed: max(0, stats.violationsCount),
            .accel: 0,
            .brake: 0
        ]
    }

    private func exportPDFButton(stats: DrivingStats) -> some View {
        Button {
            let periodKey: String = {
                switch selectedPeriod {
                case "today": return "driving_reports_filter_today"
                case "month": return "driving_reports_filter_month"
                default: return "driving_reports_filter_week"
                }
            }()
            if let url = FamilyDrivingWeeklyReportPDF.write(
                stats: stats,
                trips: filteredReports,
                memberName: selectedMemberName,
                periodLabel: localizationManager.localized(periodKey),
                localization: localizationManager
            ) {
                sharePDFItems = [url]
                showSharePDF = true
            }
        } label: {
            HStack {
                Image(systemName: "square.and.arrow.up")
                Text(localizationManager.localized("drive_export_pdf"))
                    .fontWeight(.semibold)
            }
            .foregroundColor(.backgroundDark)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(Color.secondaryGold)
            .cornerRadius(CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .disabled(stats.totalTrips == 0 && filteredReports.isEmpty)
        .accessibilityIdentifier("drive_export_pdf")
    }

    private func driveIncidentExplainSheet(_ kind: DriveIncidentKind) -> some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(kind.emoji + " " + localizationManager.localized(kind.titleKey))
                    .font(AladdinFamilyType.title2())
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized(kind.explainKey))
                    .font(AladdinFamilyType.body())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                Text(localizationManager.localized("drive_inc_explain_data_note"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                Spacer()
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_done")) {
                explainKind = nil
            })
        }
    }
}

enum DriveIncidentKind: String, CaseIterable, Identifiable {
    case phone
    case speed
    case accel
    case brake

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .phone: return "📱"
        case .speed: return "🔴"
        case .accel: return "⚡️"
        case .brake: return "🟡"
        }
    }

    var titleKey: String {
        switch self {
        case .phone: return "drive_inc_phone_title"
        case .speed: return "drive_inc_speed_title"
        case .accel: return "drive_inc_accel_title"
        case .brake: return "drive_inc_brake_title"
        }
    }

    var explainKey: String {
        switch self {
        case .phone: return "drive_inc_phone_explain"
        case .speed: return "drive_inc_speed_explain"
        case .accel: return "drive_inc_accel_explain"
        case .brake: return "drive_inc_brake_explain"
        }
    }
}

enum FamilyDrivingWeeklyReportPDF {
    static func write(
        stats: DrivingStats,
        trips: [DrivingReport] = [],
        memberName: String = "",
        periodLabel: String,
        localization: LocalizationManager
    ) -> URL? {
        let renderer = UIGraphicsPDFRenderer(bounds: CGRect(x: 0, y: 0, width: 612, height: 792))
        let safeName = memberName
            .replacingOccurrences(of: "/", with: "-")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let fileStub = safeName.isEmpty ? "member" : safeName.replacingOccurrences(of: " ", with: "_")
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("aladdin_drive_\(fileStub)_\(Int(Date().timeIntervalSince1970)).pdf")
        do {
            try renderer.writePDF(to: url) { ctx in
                ctx.beginPage()
                let title = localization.localized("drive_weekly_title")
                let df = DateFormatter()
                df.dateStyle = .short
                df.timeStyle = .short
                var tripLines: [String] = []
                for (idx, trip) in trips.prefix(40).enumerated() {
                    tripLines.append(
                        "\(idx + 1). \(df.string(from: trip.startTime)) · \(String(format: "%.1f", trip.distance)) km · \(trip.formattedSafetyScore)"
                    )
                }
                if trips.isEmpty {
                    tripLines.append(localization.localized("drive_no_trips"))
                }
                let body = """
                \(memberName.isEmpty ? "" : memberName)
                \(periodLabel)

                \(localization.localized("drive_trips")): \(stats.totalTrips)
                \(localization.localized("drive_total_km")): \(String(format: "%.1f", stats.totalDistance))
                \(localization.localized("driving_reports_safety_score")): \(stats.formattedAverageSafetyScore)
                \(localization.localized("driving_reports_violations")): \(stats.violationsCount)

                \(localization.localized("driving_reports_history_title")):
                \(tripLines.joined(separator: "\n"))

                \(localization.localized("drive_pdf_disclaimer"))
                """
                let attrs: [NSAttributedString.Key: Any] = [
                    .font: UIFont.systemFont(ofSize: 18, weight: .bold)
                ]
                (title as NSString).draw(at: CGPoint(x: 48, y: 48), withAttributes: attrs)
                let bodyAttrs: [NSAttributedString.Key: Any] = [
                    .font: UIFont.systemFont(ofSize: 12)
                ]
                (body as NSString).draw(
                    in: CGRect(x: 48, y: 90, width: 516, height: 660),
                    withAttributes: bodyAttrs
                )
            }
            return url
        } catch {
            return nil
        }
    }
}

// MARK: - S61–62 play: real GPS / endpoints only (never invent mid points)

/// Layer 1 = GPS track · Layer 2 = start→end line. Interpolate only between real samples.
enum TripRoutePlaybackGeometry {
    static func coordinates(for report: DrivingReport) -> [CLLocationCoordinate2D] {
        var coords = report.routePoints.filter(\.isValid).map(\.coordinate)
        if coords.count < 2, report.hasRouteEndpoints {
            coords = [
                CLLocationCoordinate2D(latitude: report.startLatitude!, longitude: report.startLongitude!),
                CLLocationCoordinate2D(latitude: report.endLatitude!, longitude: report.endLongitude!)
            ]
        }
        return coords
    }

    static func coordinate(along coords: [CLLocationCoordinate2D], progress: Double) -> CLLocationCoordinate2D? {
        guard let first = coords.first else { return nil }
        guard coords.count >= 2 else { return first }
        let p = min(1, max(0, progress))
        var segmentLengths: [CLLocationDistance] = []
        var total: CLLocationDistance = 0
        for i in 1..<coords.count {
            let d = CLLocation(latitude: coords[i - 1].latitude, longitude: coords[i - 1].longitude)
                .distance(from: CLLocation(latitude: coords[i].latitude, longitude: coords[i].longitude))
            segmentLengths.append(d)
            total += d
        }
        if total <= 0 { return first }
        let target = total * p
        var acc: CLLocationDistance = 0
        for i in 0..<segmentLengths.count {
            let next = acc + segmentLengths[i]
            if target <= next {
                let t = segmentLengths[i] > 0 ? (target - acc) / segmentLengths[i] : 0
                let a = coords[i]
                let b = coords[i + 1]
                return CLLocationCoordinate2D(
                    latitude: a.latitude + (b.latitude - a.latitude) * t,
                    longitude: a.longitude + (b.longitude - a.longitude) * t
                )
            }
            acc = next
        }
        return coords.last
    }
}

final class TripPlayheadAnnotation: NSObject, MKAnnotation {
    @objc dynamic var coordinate: CLLocationCoordinate2D
    init(coordinate: CLLocationCoordinate2D) {
        self.coordinate = coordinate
        super.init()
    }
}

struct TripEndpointMapPreview: View {
    let report: DrivingReport
    /// 0…1 playhead along real samples / endpoint line.
    var progress: Double = 0

    var body: some View {
        TripRouteMapRepresentable(report: report, progress: progress)
            .allowsHitTesting(false)
            .accessibilityIdentifier(
                report.hasGPSTrack ? "trip_map_gps_track_play" : "trip_map_endpoints_play"
            )
    }
}

struct TripRouteMapRepresentable: UIViewRepresentable {
    let report: DrivingReport
    var progress: Double

    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView(frame: .zero)
        map.isScrollEnabled = false
        map.isZoomEnabled = false
        map.isRotateEnabled = false
        map.isPitchEnabled = false
        map.pointOfInterestFilter = .excludingAll
        context.coordinator.apply(report: report, progress: progress, on: map)
        return map
    }

    func updateUIView(_ map: MKMapView, context: Context) {
        context.coordinator.apply(report: report, progress: progress, on: map)
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator: NSObject, MKMapViewDelegate {
        private var appliedId: String?
        private var coords: [CLLocationCoordinate2D] = []
        private var playhead: TripPlayheadAnnotation?

        func apply(report: DrivingReport, progress: Double, on map: MKMapView) {
            let key = "\(report.id)-\(report.routePoints.count)-\(report.hasRouteEndpoints)"
            map.delegate = self
            if appliedId != key {
                appliedId = key
                map.removeOverlays(map.overlays)
                map.removeAnnotations(map.annotations)
                playhead = nil
                coords = TripRoutePlaybackGeometry.coordinates(for: report)
                guard coords.count >= 2 else { return }

                var path = coords
                let line = MKPolyline(coordinates: &path, count: path.count)
                map.addOverlay(line)

                let start = MKPointAnnotation()
                start.coordinate = coords.first!
                start.title = "start"
                let end = MKPointAnnotation()
                end.coordinate = coords.last!
                end.title = "end"
                map.addAnnotations([start, end])

                var rect = MKMapRect.null
                for c in coords {
                    let p = MKMapPoint(c)
                    rect = rect.union(MKMapRect(x: p.x, y: p.y, width: 0, height: 0))
                }
                map.setVisibleMapRect(
                    rect,
                    edgePadding: UIEdgeInsets(top: 18, left: 18, bottom: 18, right: 18),
                    animated: false
                )
            }
            updatePlayhead(progress: progress, on: map)
        }

        private func updatePlayhead(progress: Double, on map: MKMapView) {
            guard let point = TripRoutePlaybackGeometry.coordinate(along: coords, progress: progress) else {
                return
            }
            if let playhead {
                playhead.coordinate = point
            } else {
                let ann = TripPlayheadAnnotation(coordinate: point)
                playhead = ann
                map.addAnnotation(ann)
            }
        }

        func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
            if let line = overlay as? MKPolyline {
                let r = MKPolylineRenderer(polyline: line)
                // Trip path: soft violet (readable on Apple Maps, not gold-on-orange clash).
                r.strokeColor = UIColor(red: 0.55, green: 0.40, blue: 0.95, alpha: 1)
                r.lineWidth = 4
                return r
            }
            return MKOverlayRenderer(overlay: overlay)
        }

        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            if annotation is TripPlayheadAnnotation {
                let id = "trip_playhead"
                let view = mapView.dequeueReusableAnnotationView(withIdentifier: id)
                    ?? MKAnnotationView(annotation: annotation, reuseIdentifier: id)
                view.annotation = annotation
                view.canShowCallout = false
                view.centerOffset = .zero
                if view.viewWithTag(77) == nil {
                    let dot = UIView(frame: CGRect(x: 0, y: 0, width: 16, height: 16))
                    dot.backgroundColor = UIColor(Color.secondaryGold)
                    dot.layer.cornerRadius = 8
                    dot.layer.borderWidth = 2
                    dot.layer.borderColor = UIColor.white.cgColor
                    dot.tag = 77
                    view.addSubview(dot)
                    view.bounds = CGRect(x: 0, y: 0, width: 16, height: 16)
                    dot.center = CGPoint(x: 8, y: 8)
                }
                return view
            }
            if let point = annotation as? MKPointAnnotation {
                let id = "trip_endpoint"
                let view = mapView.dequeueReusableAnnotationView(withIdentifier: id) as? MKMarkerAnnotationView
                    ?? MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: id)
                view.annotation = annotation
                view.canShowCallout = false
                view.markerTintColor = point.title == "start"
                    ? UIColor(Color.secondaryGold)
                    : UIColor(Color.primaryBlue)
                view.glyphImage = UIImage(systemName: point.title == "start" ? "flag.fill" : "flag.checkered")
                view.displayPriority = .defaultLow
                return view
            }
            return nil
        }
    }
}

// MARK: - Play A (honest metrics scrubber — no mock map points)

private struct DrivingTripPlaybackSheet: View {
    let report: DrivingReport
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var progress: Double = 0
    @State private var isPlaying = false
    @State private var playTask: Task<Void, Never>?
    /// HUB-P1.6 — resolved street labels (fallback = report strings).
    @State private var startStreet: String = ""
    @State private var endStreet: String = ""

    private var durationSeconds: Double {
        max(report.duration, 1)
    }

    private var routeTitle: String {
        let a = Self.streetTitle(startStreet.isEmpty ? report.startLocation : startStreet)
        let b = Self.streetTitle(endStreet.isEmpty ? report.endLocation : endStreet)
        return "\(a) → \(b)"
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("driving_play_title"))
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(AladdinSnowballPalette.gold)

                    let merged = DrivingTripTrackStore.mergeInto(report)
                    if merged.hasGPSTrack || merged.hasRouteEndpoints {
                        TripEndpointMapPreview(report: merged, progress: progress)
                            .frame(height: 180)
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    } else {
                        Text(localizationManager.localized("driving_play_no_track"))
                            .font(AladdinFamilyType.caption())
                            .foregroundColor(AladdinSnowballPalette.inkMuted)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(routeTitle)
                            .font(AladdinFamilyType.subheadline(weight: .semibold))
                            .foregroundColor(AladdinSnowballPalette.ink)
                        HStack(spacing: Spacing.m) {
                            Label(report.localizedFormattedDistance(localizationManager), systemImage: "ruler")
                            Label("\(report.durationMinutes) \(localizationManager.localized("driving_reports_unit_min"))", systemImage: "clock")
                            if let maxSpeed = report.localizedFormattedMaxSpeed(localizationManager) {
                                Label(maxSpeed, systemImage: "speedometer")
                            }
                        }
                        .font(.caption)
                        .foregroundColor(AladdinSnowballPalette.inkMuted)
                    }
                    .padding(Spacing.m)
                    .background(AladdinSnowballPalette.glassCard())

                    Text(localizationManager.localized("driving_play_progress"))
                        .font(.caption.weight(.bold))
                        .foregroundColor(AladdinSnowballPalette.inkMuted)

                    Slider(
                        value: Binding(
                            get: { progress },
                            set: { newValue in
                                if isPlaying { stop() }
                                progress = newValue
                            }
                        ),
                        in: 0...1
                    )
                        .tint(AladdinSnowballPalette.gold)
                        .accessibilityIdentifier("driving_play_scrubber")

                    ProgressView(value: progress)
                        .tint(AladdinSnowballPalette.gold)

                    Text(elapsedLabel)
                        .font(.caption.monospacedDigit())
                        .foregroundColor(AladdinSnowballPalette.ink)

                    Button {
                        togglePlay()
                    } label: {
                        HStack {
                            Image(systemName: isPlaying ? "pause.fill" : "play.fill")
                            Text(localizationManager.localized(isPlaying ? "driving_play_pause" : "driving_play_resume"))
                                .font(.bodyBold)
                        }
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(AladdinSnowballPalette.gold)
                        .cornerRadius(CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("driving_play_toggle")

                    // S24/S25/S28 — chrono + risks from real trip data only.
                    Text(localizationManager.localized("trip_detail_chrono_title"))
                        .font(.caption.weight(.bold))
                        .foregroundColor(AladdinSnowballPalette.inkMuted)
                    if report.events.isEmpty {
                        Text(localizationManager.localized("trip_detail_chrono_empty"))
                            .font(.caption)
                            .foregroundColor(AladdinSnowballPalette.inkMuted)
                    } else {
                        ForEach(Array(report.events.prefix(8).enumerated()), id: \.offset) { _, event in
                            HStack(alignment: .top, spacing: Spacing.s) {
                                Text(Self.clock(event.timestamp))
                                    .font(.caption.monospacedDigit())
                                    .foregroundColor(AladdinSnowballPalette.gold)
                                    .frame(width: 44, alignment: .leading)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(event.type.localizedDisplayName(localizationManager))
                                        .font(.caption.weight(.semibold))
                                        .foregroundColor(AladdinSnowballPalette.ink)
                                    Text(event.localizedSeverityLevel(localizationManager))
                                        .font(.caption2)
                                        .foregroundColor(AladdinSnowballPalette.inkMuted)
                                }
                                Spacer(minLength: 0)
                            }
                        }
                    }

                    if !report.violations.isEmpty {
                        Text(localizationManager.localized("trip_detail_risk_title"))
                            .font(.caption.weight(.bold))
                            .foregroundColor(AladdinSnowballPalette.inkMuted)
                            .padding(.top, Spacing.xs)
                        ForEach(Array(report.violations.prefix(6).enumerated()), id: \.offset) { _, violation in
                            HStack(spacing: Spacing.s) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .font(.caption2)
                                    .foregroundColor(.dangerRed)
                                Text(violation.localizedDisplayName(localizationManager))
                                    .font(.caption)
                                    .foregroundColor(AladdinSnowballPalette.ink)
                                Spacer(minLength: 0)
                                Text(Self.clock(violation.timestamp))
                                    .font(.caption2.monospacedDigit())
                                    .foregroundColor(AladdinSnowballPalette.inkMuted)
                            }
                        }
                    }
                }
                .padding(Spacing.l)
            }
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("common_done")) {
                        stop()
                        dismiss()
                    }
                    .foregroundColor(AladdinSnowballPalette.gold)
                }
            }
            .onDisappear { stop() }
            .task {
                await resolveStreetLabels()
            }
        }
    }

    /// HUB-P1.6 — geocode for screen 14 when ledger still has lat/lon strings.
    private func resolveStreetLabels() async {
        startStreet = report.startLocation
        endStreet = report.endLocation
        if FamilyDrivingTripLedger.looksLikeCoordinatePair(report.startLocation)
            || FamilyDrivingTripLedger.looksLikeCoordinatePair(report.endLocation) {
            await FamilyDrivingTripLedger.enrichStreetLabels(for: report)
            if let fresh = FamilyDrivingTripLedger.loadAll().first(where: { $0.id == report.id }) {
                startStreet = fresh.startLocation
                endStreet = fresh.endLocation
                print("WHERE_PHONE trip detail streets → \(startStreet) → \(endStreet)")
            }
        }
    }

    private static func clock(_ date: Date) -> String {
        let f = DateFormatter()
        f.locale = .current
        f.dateFormat = "HH:mm"
        return f.string(from: date)
    }

    private var elapsedLabel: String {
        let elapsed = Int(progress * durationSeconds)
        let total = Int(durationSeconds)
        return String(format: "%d:%02d / %d:%02d", elapsed / 60, elapsed % 60, total / 60, total % 60)
    }

    private func togglePlay() {
        if isPlaying {
            stop()
            return
        }
        if progress >= 1 {
            progress = 0
        }
        isPlaying = true
        HapticFeedback.impact(.light)
        playTask = Task { @MainActor in
            while !Task.isCancelled && progress < 1 {
                try? await Task.sleep(nanoseconds: 250_000_000)
                guard !Task.isCancelled else { return }
                // ~4x realtime for short trips; still proportional to duration.
                let step = max(0.008, 0.25 / max(durationSeconds / 4.0, 1))
                progress = min(1, progress + step)
            }
            isPlaying = false
        }
    }

    private func stop() {
        isPlaying = false
        playTask?.cancel()
        playTask = nil
    }

    private static func streetTitle(_ raw: String) -> String {
        var t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        for prefix in ["В ", "в ", "At ", "at "] {
            if t.hasPrefix(prefix) {
                t = String(t.dropFirst(prefix.count))
            }
        }
        return t
    }
}

// MARK: - Preview

#if DEBUG
struct DrivingReportsModal_Previews: PreviewProvider {
    static var previews: some View {
        DrivingReportsModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
            .environmentObject(AnalyticsViewModel(service: RemoteAnalyticsService()))
    }
}
#endif


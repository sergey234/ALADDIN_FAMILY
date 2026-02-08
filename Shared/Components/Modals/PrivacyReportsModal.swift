import SwiftUI
import CoreLocation

/**
 * 🔒 Privacy Reports Modal
 * Модальное окно для просмотра отчетов приватности
 * Включает 3 вкладки: Location Bubble, Data Cleanup, Anti Tracker
 */

struct PrivacyReportsModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = PrivacyReportsViewModel()
    
    // ✅ ИНТЕГРАЦИЯ LocationManager
    @StateObject private var locationManager = LocationManager.shared
    
    @State private var selectedTab: PrivacyTabType = .location
    @State private var showAccuracySheet: Bool = false
    @State private var selectedRequestId: String? = nil
    @State private var showCleanupCategoriesSheet: Bool = false
    @State private var showTrackerWhitelistAlert: Bool = false
    @State private var selectedTrackerName: String? = nil
    
    enum PrivacyTabType: String, CaseIterable {
        case location = "location"
        case cleanup = "cleanup"
        case tracker = "tracker"
        
        func displayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .location: return localizationManager.localized("privacy_tab_location")
            case .cleanup: return localizationManager.localized("privacy_tab_cleanup")
            case .tracker: return localizationManager.localized("privacy_tab_tracker")
            }
        }
        
        var icon: String {
            switch self {
            case .location: return "location.fill"
            case .cleanup: return "trash.fill"
            case .tracker: return "eye.slash.fill"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Вкладки
                    tabsSection
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.m)
                    
                    // Контент
                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: Spacing.l) {
                            switch selectedTab {
                            case .location:
                                locationSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            case .cleanup:
                                cleanupSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            case .tracker:
                                trackerSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            }
                            
                            Spacer(minLength: 100)
                        }
                        .padding(.top, Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("privacy_reports_modal_title"))
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
            await loadDataForSelectedTab()
        }
        .onChange(of: selectedTab) { _ in
            Task {
                await loadDataForSelectedTab()
            }
        }
        .overlay(alignment: .center) {
            if viewModel.isLoading {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                    .padding()
                    .background(Color.backgroundMedium.opacity(0.85))
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
            }
        }
        .overlay(alignment: .bottom) {
            if let error = viewModel.errorMessage {
                errorBanner(message: error)
                    .padding(.bottom, Spacing.l)
            }
        }
        .confirmationDialog(
            localizationManager.localized("privacy_location_accuracy_title"),
            isPresented: $showAccuracySheet,
            presenting: selectedRequestId
        ) { requestId in
            Button(localizationManager.localized("privacy_location_accuracy_high")) {
                Task {
                    await viewModel.updateLocationAccuracy(requestId: requestId, accuracy: .high)
                }
            }
            Button(localizationManager.localized("privacy_location_accuracy_medium")) {
                Task {
                    await viewModel.updateLocationAccuracy(requestId: requestId, accuracy: .medium)
                }
            }
            Button(localizationManager.localized("privacy_location_accuracy_low")) {
                Task {
                    await viewModel.updateLocationAccuracy(requestId: requestId, accuracy: .low)
                }
            }
            Button(localizationManager.localized("common_cancel"), role: .cancel) {
                selectedRequestId = nil
            }
        } message: { _ in
            Text(localizationManager.localized("privacy_location_accuracy_message"))
        }
        .confirmationDialog(
            localizationManager.localized("privacy_cleanup_categories_title"),
            isPresented: $showCleanupCategoriesSheet
        ) {
            Button(localizationManager.localized("privacy_cleanup_category_cache")) {
                Task {
                    await viewModel.startCleanup(categories: ["cache"])
                }
            }
            Button(localizationManager.localized("privacy_cleanup_category_temp")) {
                Task {
                    await viewModel.startCleanup(categories: ["temp"])
                }
            }
            Button(localizationManager.localized("privacy_cleanup_category_duplicates")) {
                Task {
                    await viewModel.startCleanup(categories: ["duplicates"])
                }
            }
            Button(localizationManager.localized("privacy_cleanup_category_old")) {
                Task {
                    await viewModel.startCleanup(categories: ["old"])
                }
            }
            Button(localizationManager.localized("privacy_cleanup_category_all")) {
                Task {
                    await viewModel.startCleanup(categories: ["all"])
                }
            }
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
        } message: {
            Text(localizationManager.localized("privacy_cleanup_categories_message"))
        }
        .alert(
            localizationManager.localized("privacy_tracker_whitelist_confirm_title"),
            isPresented: $showTrackerWhitelistAlert,
            presenting: selectedTrackerName
        ) { trackerName in
            Button(localizationManager.localized("privacy_tracker_whitelist_confirm_button")) {
                Task {
                    await viewModel.addTrackerToWhitelist(trackerName: trackerName)
                }
            }
            Button(localizationManager.localized("common_cancel"), role: .cancel) {
                selectedTrackerName = nil
            }
        } message: { trackerName in
            Text(String(format: localizationManager.localized("privacy_tracker_whitelist_confirm_message"), trackerName))
        }
    }
    
    // MARK: - Data Loading
    
    private func loadDataForSelectedTab() async {
        switch selectedTab {
        case .location:
            await viewModel.loadLocationData()
        case .cleanup:
            await viewModel.loadCleanupData()
        case .tracker:
            await viewModel.loadTrackerData()
        }
    }
    
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
    
    // MARK: - Tabs Section
    
    private var tabsSection: some View {
        HStack(spacing: 0) {
            ForEach(PrivacyTabType.allCases, id: \.self) { tab in
                Button(action: {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                        selectedTab = tab
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: tab.icon)
                            .font(.caption)
                        Text(tab.displayName(localizationManager))
                            .font(.body)
                    }
                    .foregroundColor(selectedTab == tab ? .white : .textPrimary)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Spacing.s)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(selectedTab == tab ? Color.primaryBlue : Color.clear)
                    )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Location Section
    
    private var locationSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Статистика
            locationStatsSection
            
            // История запросов
            locationRequestsSection
        }
    }
    
    
    private var locationStatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_location_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: Spacing.s) {
                statCard(
                    icon: "hand.raised.fill",
                    title: localizationManager.localized("privacy_location_blocked"),
                    value: "\(viewModel.locationStats?.blockedRequests ?? 0)",
                    color: .successGreen
                )
                
                statCard(
                    icon: "checkmark.circle.fill",
                    title: localizationManager.localized("privacy_location_allowed"),
                    value: "\(viewModel.locationStats?.allowedRequests ?? 0)",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "location.fill",
                    title: localizationManager.localized("privacy_location_modified"),
                    value: "\(viewModel.locationStats?.modifiedRequests ?? 0)",
                    color: .warningOrange
                )
            }
            
            // Текущая точность
            HStack {
                Text(localizationManager.localized("privacy_location_current_accuracy"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                Spacer()
                Group {
                    if let stats = viewModel.locationStats {
                        Text(stats.currentAccuracy.localizedDisplayName(localizationManager))
                    } else {
                        Text("—")
                    }
                }
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private var locationRequestsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_location_requests_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            if viewModel.locationRequests.isEmpty {
                emptyLocationRequestsView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(viewModel.locationRequests) { request in
                        locationRequestRow(request: request)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func locationRequestRow(request: LocationRequest) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(request.appName)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(request.formattedTimestamp)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                actionBadge(request.action, localizationManager: localizationManager)
                
                if let accuracy = request.accuracy {
                    Text(accuracy.localizedDisplayName(localizationManager))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
            
            // Действия
            HStack(spacing: Spacing.s) {
                // Разрешить
                if request.action == .blocked {
                    Button(action: {
                        Task {
                            await viewModel.allowLocationRequest(requestId: request.id)
                        }
                    }) {
                        Label(localizationManager.localized("privacy_location_action_allow"), systemImage: "checkmark.circle")
                            .font(.caption)
                            .foregroundColor(.successGreen)
                    }
                }
                
                // Заблокировать
                if request.action == .allowed {
                    Button(action: {
                        Task {
                            await viewModel.blockLocationRequest(requestId: request.id)
                        }
                    }) {
                        Label(localizationManager.localized("privacy_location_action_block"), systemImage: "hand.raised.fill")
                            .font(.caption)
                            .foregroundColor(.dangerRed)
                    }
                }
                
                // Изменить точность
                Button(action: {
                    selectedRequestId = request.id
                    showAccuracySheet = true
                }) {
                    Label(localizationManager.localized("privacy_location_action_change_accuracy"), systemImage: "location.fill")
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                }
            }
            .padding(.top, Spacing.xs)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Cleanup Section
    
    private var cleanupSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Статистика
            cleanupStatsSection
            
            // История очисток
            cleanupHistorySection
        }
    }
    
    
    private var cleanupStatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("privacy_cleanup_stats_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Button(action: {
                    showCleanupCategoriesSheet = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "trash.fill")
                            .font(.caption)
                        Text(localizationManager.localized("privacy_cleanup_start"))
                            .font(.caption)
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        Capsule()
                            .fill(Color.primaryBlue)
                    )
                }
            }
            
            HStack(spacing: Spacing.s) {
                statCard(
                    icon: "trash.fill",
                    title: localizationManager.localized("privacy_cleanup_total_freed"),
                    value: viewModel.cleanupStats?.formattedTotalFreed ?? "0 Б",
                    color: .successGreen
                )
                
                statCard(
                    icon: "arrow.clockwise",
                    title: localizationManager.localized("privacy_cleanup_count"),
                    value: "\(viewModel.cleanupStats?.cleanupsCount ?? 0)",
                    color: .primaryBlue
                )
            }
            
            // Последняя очистка
            if let lastDate = viewModel.cleanupStats?.lastCleanupDate {
                HStack {
                    Text(localizationManager.localized("privacy_cleanup_last"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(lastDate, style: .relative)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private var cleanupHistorySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_cleanup_history_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            if viewModel.cleanupRecords.isEmpty {
                emptyCleanupHistoryView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(viewModel.cleanupRecords) { record in
                        cleanupRecordRow(record: record)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func cleanupRecordRow(record: DataCleanupRecord) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                Text(record.formattedFreedSpace)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.successGreen)
                
                Spacer()
                
                Text(record.formattedDate)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            // Категории
            ForEach(record.categories, id: \.name) { category in
                HStack {
                    Text(category.name)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(category.formattedSize)
                        .font(.captionBold)
                        .foregroundColor(.textPrimary)
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Tracker Section
    
    private var trackerSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Статистика
            trackerStatsSection
            
            // Топ трекеры
            topTrackersSection
        }
    }
    
    
    private var trackerStatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_tracker_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: Spacing.s) {
                statCard(
                    icon: "eye.slash.fill",
                    title: localizationManager.localized("privacy_tracker_total_blocked"),
                    value: "\(viewModel.trackerStats?.totalBlocked ?? 0)",
                    color: .successGreen
                )
                
                statCard(
                    icon: "calendar",
                    title: localizationManager.localized("privacy_tracker_this_week"),
                    value: "+\(viewModel.trackerStats?.blockedThisWeek ?? 0)",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "percent",
                    title: localizationManager.localized("privacy_tracker_effectiveness"),
                    value: viewModel.trackerStats?.formattedEffectiveness ?? "0%",
                    color: .successGreen
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private var topTrackersSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("privacy_tracker_top_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            if viewModel.topTrackers.isEmpty {
                emptyTopTrackersView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(viewModel.topTrackers) { tracker in
                        trackerRow(tracker: tracker)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func trackerRow(tracker: TrackerBlock) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(tracker.trackerName)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text("\(tracker.blockedCount) \(localizationManager.localized("privacy_tracker_blocked_times"))")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                if let lastBlocked = tracker.formattedLastBlocked {
                    Text(lastBlocked)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
            
            // Кнопка "В белый список"
            Button(action: {
                selectedTrackerName = tracker.trackerName
                showTrackerWhitelistAlert = true
            }) {
                Label(localizationManager.localized("privacy_tracker_whitelist_add"), systemImage: "plus.circle")
                    .font(.caption)
                    .foregroundColor(.primaryBlue)
            }
            .padding(.top, Spacing.xs)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Helper Views
    
    private func statCard(icon: String, title: String, value: String, color: Color) -> some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(color)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func actionBadge(_ action: LocationRequestAction, localizationManager: LocalizationManager) -> some View {
        HStack(spacing: Spacing.xs) {
            Text(action.icon)
                .font(.caption)
            Text(action.localizedDisplayName(localizationManager))
                .font(.caption2)
                .foregroundColor(.white)
        }
        .padding(.horizontal, Spacing.xs)
        .padding(.vertical, 2)
        .background(
            Capsule()
                .fill(action == .blocked ? Color.successGreen : action == .allowed ? Color.primaryBlue : Color.warningOrange)
        )
    }
    
    // MARK: - Empty States
    
    private var emptyLocationRequestsView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "location.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("privacy_location_no_requests"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
    }
    
    private var emptyCleanupHistoryView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "trash.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("privacy_cleanup_no_history"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
    }
    
    private var emptyTopTrackersView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "eye.slash.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("privacy_tracker_no_data"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
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
}

// MARK: - Preview

#if DEBUG
struct PrivacyReportsModal_Previews: PreviewProvider {
    static var previews: some View {
        PrivacyReportsModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif


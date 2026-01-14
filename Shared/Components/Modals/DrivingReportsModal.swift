import SwiftUI

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
    @StateObject private var positioningService = PositioningSystemService.shared
    @StateObject private var viewModel = DrivingReportsViewModel()
    
    // Выбранный пользователь
    @AppStorage("driving_reports_selected_user_id") private var selectedUserId: String = ""
    @State private var users: [UserSelectorView.UserOption] = []
    @State private var currentUserId: String = "current"
    @State private var isLoadingUsers: Bool = false
    
    // Фильтры
    @AppStorage("driving_reports_period") private var selectedPeriod: String = "week"
    @State private var selectedFilter: FilterType = .all
    
    enum FilterType: String, CaseIterable {
        case all = "all"
        case withViolations = "with_violations"
        case withoutViolations = "without_violations"
        
        var displayName: String {
            switch self {
            case .all: return "Все"
            case .withViolations: return "С нарушениями"
            case .withoutViolations: return "Без нарушений"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Селектор пользователя
                        if !users.isEmpty || currentUserId != "" {
                            UserSelectorView(
                                selectedUserId: Binding(
                                    get: { selectedUserId.isEmpty ? nil : selectedUserId },
                                    set: { newValue in
                                        selectedUserId = newValue ?? currentUserId
                                        loadReports()
                                    }
                                ),
                                users: users,
                                currentUserId: currentUserId,
                                showCurrentUser: true
                            )
                            .padding(.horizontal, Spacing.screenPadding)
                            .padding(.top, Spacing.m)
                        }
                        
                        // Система позиционирования
                        positioningSystemSelector
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        // Статистика
                        if let stats = viewModel.stats {
                            statsSection(stats: stats)
                                .padding(.horizontal, Spacing.screenPadding)
                        }
                        
                        // Фильтры
                        filtersSection
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        // История поездок
                        if !viewModel.reports.isEmpty {
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
            let userId = selectedUserId.isEmpty ? nil : selectedUserId
            await viewModel.loadReports(userId: userId, period: selectedPeriod)
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
                    Text(positioningService.currentSystem.displayName)
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
                    // TODO: Показать Picker для выбора системы
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
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: Spacing.s) {
                statCard(
                    icon: "🚗",
                    title: localizationManager.localized("driving_reports_trips_count"),
                    value: "\(stats.totalTrips)"
                )
                
                statCard(
                    icon: "⭐",
                    title: localizationManager.localized("driving_reports_safety_score"),
                    value: stats.formattedAverageSafetyScore
                )
                
                statCard(
                    icon: "⚠️",
                    title: localizationManager.localized("driving_reports_violations"),
                    value: "\(stats.violationsCount)"
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
                .font(.system(size: 24))
            
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
    
    // MARK: - Filters Section
    
    private var filtersSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("driving_reports_filter_period"))
                .font(.bodyBold)
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
            loadReports()
        }) {
            Text(title)
                .font(.body)
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
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(spacing: Spacing.s) {
                ForEach(viewModel.reports) { report in
                    tripRow(report: report)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func tripRow(report: DrivingReport) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                Text(report.formattedSafetyScore)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(safetyScoreColor(report.safetyScore))
                
                Spacer()
                
                Text(report.startTime, style: .date)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            HStack {
                Text(report.startLocation)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Image(systemName: "arrow.right")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Text(report.endLocation)
                    .font(.body)
                    .foregroundColor(.textPrimary)
            }
            
            HStack(spacing: Spacing.m) {
                Label(report.formattedDistance, systemImage: "ruler")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Label("\(report.durationMinutes) мин", systemImage: "clock")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                if !report.violations.isEmpty {
                    Label("\(report.violations.count)", systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundColor(.dangerRed)
                }
            }
            
            // Система позиционирования
            if let system = report.positioningSystem {
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "location.fill")
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                    Text(system)
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
    
    private func safetyScoreColor(_ score: Double) -> Color {
        if score >= 8 {
            return .successGreen
        } else if score >= 5 {
            return .warningOrange
        } else {
            return .dangerRed
        }
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "car.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("driving_reports_empty"))
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
        
        do {
            // Загружаем список членов семьи
            let familyMembers: [FamilyMemberResponse] = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getFamilyMembers { result in
                    continuation.resume(with: result)
                }
            }
            
            // Преобразуем в UserOption
            users = familyMembers.map { member in
                UserSelectorView.UserOption(
                    id: member.id,
                    name: member.name,
                    role: member.role,
                    avatar: member.avatar
                )
            }
            
            // Устанавливаем текущего пользователя (первый родитель или текущий пользователь)
            if let currentUser = familyMembers.first(where: { $0.role == "parent" }) {
                currentUserId = currentUser.id
            } else {
                currentUserId = "current"
            }
        } catch {
            // В случае ошибки используем пустой список
            users = []
            currentUserId = "current"
        }
    }
    
    private func loadReports() {
        Task {
            let userId = selectedUserId.isEmpty ? nil : selectedUserId
            await viewModel.loadReports(userId: userId, period: selectedPeriod)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct DrivingReportsModal_Previews: PreviewProvider {
    static var previews: some View {
        DrivingReportsModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif


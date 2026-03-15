import SwiftUI
import CoreLocation

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
            // ✅ ИСПРАВЛЕНИЕ 2: Проверяем токен перед загрузкой
            guard AppConfig.authToken != nil else {
                #if DEBUG
                print("⚠️ DrivingReportsModal: Токен отсутствует - требуется авторизация")
                #endif
                // Показываем сообщение об ошибке через ViewModel
                viewModel.errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра отчетов."
                return
            }
            
            await loadUsers()
            // ✅ ИСПРАВЛЕНИЕ 3: Синхронизация selectedUserId происходит в конце loadUsers()
            
            let userId = selectedUserId.isEmpty ? nil : (selectedUserId == "current" ? nil : selectedUserId)
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
                Label(report.localizedFormattedDistance(localizationManager), systemImage: "ruler")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Label("\(report.durationMinutes) \(localizationManager.localized("driving_reports_unit_min"))", systemImage: "clock")
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
            
            // Если список пуст после загрузки, пробуем загрузить из UserDefaults как fallback
            if users.isEmpty {
                print("⚠️ DrivingReportsModal: Список пользователей пуст, пробуем загрузить из UserDefaults...")
                await loadUsersFromUserDefaults()
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
        let familyMembersKey = "family_members_list"
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            
            print("✅ DrivingReportsModal: Загружено \(decoded.count) членов семьи из UserDefaults")
            
            users = decoded.map { member in
                // Преобразуем FamilyRole в строку для UserOption
                let roleString: String
                switch member.role {
                case .parent: roleString = "parent"
                case .child: roleString = "child"
                case .teenager: roleString = "teenager"
                case .elderly: roleString = "elderly"
                }
                
                return UserSelectorView.UserOption(
                    id: member.id.uuidString,
                    name: member.name,
                    role: roleString,
                    avatar: member.avatar
                )
            }
            
            // Устанавливаем текущего пользователя (первый родитель или первый член)
            if let currentUser = decoded.first(where: { $0.role == .parent }) {
                currentUserId = currentUser.id.uuidString
                print("✅ DrivingReportsModal: Текущий пользователь из UserDefaults: \(currentUser.name)")
            } else if let firstMember = decoded.first {
                currentUserId = firstMember.id.uuidString
                print("✅ DrivingReportsModal: Текущий пользователь из UserDefaults (первый): \(firstMember.name)")
            }
        } else {
            print("⚠️ DrivingReportsModal: Нет данных в UserDefaults")
        }
    }
    
    private func loadReports() {
        Task { @MainActor in
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


import SwiftUI
import UIKit
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
            // ✅ ИСПРАВЛЕНИЕ 3: Синхронизация selectedUserId происходит в конце loadUsers()
            
            // Первичное применение данных из объединённой аналитики (без сетевых запросов)
            viewModel.applyFrom(components: analyticsViewModel.componentsAnalytics, period: selectedPeriod)
        }
        // Обновляем при смене периода
        .onChange(of: selectedPeriod) { newValue in
            viewModel.applyFrom(components: analyticsViewModel.componentsAnalytics, period: newValue)
        }
        // И при поступлении свежих компонентных данных из AnalyticsViewModel
        .onReceive(analyticsViewModel.$componentsAnalytics) { components in
            viewModel.applyFrom(components: components, period: selectedPeriod)
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
    }

    private var selectedUserBinding: Binding<String?> {
        Binding(
            get: { selectedUserId.isEmpty ? nil : selectedUserId },
            set: { newValue in
                selectedUserId = newValue ?? currentUserId
                loadReports()
            }
        )
    }

    private var modalContent: some View {
        ZStack {
            LinearGradient.backgroundGradient
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
        // Сетевая загрузка больше не требуется: используем данные из AnalyticsViewModel.componentsAnalytics
        viewModel.applyFrom(components: analyticsViewModel.componentsAnalytics, period: selectedPeriod)
    }

    // MARK: - W3 Q02–Q06 weekly strip + PDF

    private func weeklyIncidentStrip(stats: DrivingStats?) -> some View {
        let counts = incidentCounts(from: stats)
        return VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("drive_weekly_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            if stats == nil || (stats?.totalTrips ?? 0) == 0 {
                Text(localizationManager.localized("drive_no_trips"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            HStack(spacing: Spacing.s) {
                ForEach(DriveIncidentKind.allCases) { kind in
                    Button {
                        explainKind = kind
                    } label: {
                        VStack(spacing: 4) {
                            Text(kind.emoji)
                                .font(.title2)
                            Text("\(counts[kind] ?? 0)")
                                .font(.headline.weight(.bold))
                                .foregroundColor(.textPrimary)
                            Text(localizationManager.localized(kind.titleKey))
                                .font(.caption2)
                                .foregroundColor(.textSecondary)
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

    private func incidentCounts(from stats: DrivingStats?) -> [DriveIncidentKind: Int] {
        _ = stats?.violationsCount
        return Dictionary(uniqueKeysWithValues: DriveIncidentKind.allCases.map { ($0, 0) })
    }

    private func exportPDFButton(stats: DrivingStats) -> some View {
        Button {
            if let url = FamilyDrivingWeeklyReportPDF.write(
                stats: stats,
                periodLabel: localizationManager.localized(
                    selectedPeriod == "month" ? "driving_reports_filter_month" : "drive_this_week"
                ),
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
        .accessibilityIdentifier("drive_export_pdf")
    }

    private func driveIncidentExplainSheet(_ kind: DriveIncidentKind) -> some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(kind.emoji + " " + localizationManager.localized(kind.titleKey))
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized(kind.explainKey))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Text(localizationManager.localized("drive_inc_explain_data_note"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Spacer()
            }
            .padding(Spacing.l)
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
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
        periodLabel: String,
        localization: LocalizationManager
    ) -> URL? {
        let renderer = UIGraphicsPDFRenderer(bounds: CGRect(x: 0, y: 0, width: 612, height: 792))
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("aladdin_drive_\(Int(Date().timeIntervalSince1970)).pdf")
        do {
            try renderer.writePDF(to: url) { ctx in
                ctx.beginPage()
                let title = localization.localized("drive_weekly_title")
                let body = """
                \(periodLabel)

                \(localization.localized("drive_trips")): \(stats.totalTrips)
                \(localization.localized("drive_total_km")): \(String(format: "%.1f", stats.totalDistance))
                \(localization.localized("driving_reports_safety_score")): \(stats.formattedAverageSafetyScore)
                \(localization.localized("driving_reports_violations")): \(stats.violationsCount)

                \(localization.localized("drive_pdf_disclaimer"))
                """
                let attrs: [NSAttributedString.Key: Any] = [
                    .font: UIFont.systemFont(ofSize: 18, weight: .bold)
                ]
                (title as NSString).draw(at: CGPoint(x: 48, y: 48), withAttributes: attrs)
                let bodyAttrs: [NSAttributedString.Key: Any] = [
                    .font: UIFont.systemFont(ofSize: 14)
                ]
                (body as NSString).draw(
                    in: CGRect(x: 48, y: 90, width: 516, height: 600),
                    withAttributes: bodyAttrs
                )
            }
            return url
        } catch {
            return nil
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


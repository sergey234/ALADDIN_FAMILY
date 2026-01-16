import SwiftUI
import UIKit

/**
 * 🌑 Dark Web Monitoring Modal
 * Модальное окно для просмотра утечек данных из Dark Web
 * Включает список утечек, историю сканирований и действия
 */

struct DarkWebMonitoringModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = DarkWebMonitoringViewModel()
    
    // Фильтры
    @AppStorage("dark_web_filter_status") private var filterStatus: String = "all"
    @AppStorage("dark_web_filter_severity") private var filterSeverity: String = "all"
    @State private var selectedTab: TabType = .leaks
    @State private var showDataInput: Bool = false
    
    enum TabType: String, CaseIterable {
        case leaks = "leaks"
        case scans = "scans"
        
        func displayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .leaks: return localizationManager.localized("dark_web_tab_leaks")
            case .scans: return localizationManager.localized("dark_web_tab_scans")
            }
        }
        
        var icon: String {
            switch self {
            case .leaks: return "exclamationmark.triangle.fill"
            case .scans: return "magnifyingglass"
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
                    // Статистика
                    if let stats = viewModel.stats {
                        statsSection(stats: stats)
                            .padding(.horizontal, Spacing.screenPadding)
                            .padding(.top, Spacing.m)
                    }
                    
                    // Вкладки
                    tabsSection
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.m)
                    
                    // Контент
                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: Spacing.l) {
                            if selectedTab == .leaks {
                                leaksSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            } else {
                                scansSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            }
                            
                            Spacer(minLength: 100)
                        }
                        .padding(.top, Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("dark_web_modal_title"))
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
            await loadData()
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
        .sheet(isPresented: $showDataInput) {
            DarkWebDataInputView(isPresented: $showDataInput, viewModel: viewModel)
                .environmentObject(localizationManager)
        }
    }
    
    // MARK: - Stats Section
    
    private func statsSection(stats: DarkWebStats) -> some View {
        HStack(spacing: Spacing.s) {
            statCard(
                icon: "exclamationmark.triangle.fill",
                title: localizationManager.localized("dark_web_total_leaks"),
                value: "\(stats.totalLeaks)",
                color: .dangerRed
            )
            
            statCard(
                icon: "bell.badge.fill",
                title: localizationManager.localized("dark_web_new_leaks"),
                value: "\(stats.newLeaks)",
                color: stats.newLeaks > 0 ? .dangerRed : .textSecondary
            )
            
            statCard(
                icon: "checkmark.circle.fill",
                title: localizationManager.localized("dark_web_resolved"),
                value: "\(stats.resolvedLeaks)",
                color: .successGreen
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
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
    
    // MARK: - Tabs Section
    
    private var tabsSection: some View {
        HStack(spacing: 0) {
            ForEach(TabType.allCases, id: \.self) { tab in
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
    
    // MARK: - Leaks Section
    
    private var leaksSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Кнопка добавления данных для сканирования
            Button(action: {
                showDataInput = true
            }) {
                HStack {
                    Image(systemName: "plus.circle.fill")
                    Text(localizationManager.localized("dark_web_scan_add_data"))
                }
                .font(.body)
                .foregroundColor(.primaryBlue)
                .frame(maxWidth: .infinity)
                .padding(.vertical, Spacing.s)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.primaryBlue.opacity(0.1))
                )
            }
            .buttonStyle(PlainButtonStyle())
            
            // Фильтры
            filtersSection
            
            // Список утечек
            if viewModel.leaks.isEmpty {
                emptyLeaksView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(viewModel.leaks) { leak in
                        leakRow(leak: leak)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private var filtersSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("dark_web_filters"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            HStack(spacing: Spacing.s) {
                // Фильтр по статусу
                Menu {
                    Button(action: { filterStatus = "all" }) {
                        Label(localizationManager.localized("dark_web_filter_all"), systemImage: filterStatus == "all" ? "checkmark" : "")
                    }
                    Button(action: { filterStatus = "new" }) {
                        Label(localizationManager.localized("dark_web_filter_new"), systemImage: filterStatus == "new" ? "checkmark" : "")
                    }
                    Button(action: { filterStatus = "resolved" }) {
                        Label(localizationManager.localized("dark_web_filter_resolved"), systemImage: filterStatus == "resolved" ? "checkmark" : "")
                    }
                } label: {
                    HStack {
                        Text(filterStatus == "all" ? localizationManager.localized("dark_web_filter_all_statuses") : filterStatus == "new" ? localizationManager.localized("dark_web_filter_new") : localizationManager.localized("dark_web_filter_resolved"))
                            .font(.caption)
                        Image(systemName: "chevron.down")
                            .font(.caption2)
                    }
                    .foregroundColor(.textPrimary)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        Capsule()
                            .fill(Color.backgroundMedium)
                    )
                }
                
                // Фильтр по критичности
                Menu {
                    Button(action: { filterSeverity = "all" }) {
                        Label(localizationManager.localized("dark_web_filter_all"), systemImage: filterSeverity == "all" ? "checkmark" : "")
                    }
                    Button(action: { filterSeverity = "critical" }) {
                        Label(localizationManager.localized("dark_web_severity_critical"), systemImage: filterSeverity == "critical" ? "checkmark" : "")
                    }
                    Button(action: { filterSeverity = "high" }) {
                        Label(localizationManager.localized("dark_web_severity_high"), systemImage: filterSeverity == "high" ? "checkmark" : "")
                    }
                } label: {
                    HStack {
                        Text(filterSeverity == "all" ? localizationManager.localized("dark_web_filter_all_severity") : filterSeverity == "critical" ? localizationManager.localized("dark_web_severity_critical") : localizationManager.localized("dark_web_severity_high"))
                            .font(.caption)
                        Image(systemName: "chevron.down")
                            .font(.caption2)
                    }
                    .foregroundColor(.textPrimary)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        Capsule()
                            .fill(Color.backgroundMedium)
                    )
                }
            }
        }
    }
    
    private func leakRow(leak: DarkWebLeak) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                // Тип данных
                HStack(spacing: Spacing.xs) {
                    Text(leak.dataType.icon)
                        .font(.caption)
                    Text(leak.dataType.localizedDisplayName(localizationManager))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                // Статус
                statusBadge(leak.status)
                
                // Критичность
                severityBadge(leak.severity)
            }
            
            // Значение (замаскированное)
            Text(leak.maskedValue)
                .font(.body)
                .foregroundColor(.textSecondary)
            
            // Источник
            HStack(spacing: Spacing.xs) {
                Image(systemName: "database.fill")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                Text(leak.source)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            // Дата обнаружения
            HStack(spacing: Spacing.xs) {
                Image(systemName: "calendar")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                Text(leak.discoveryDate, style: .date)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            // Действия
            HStack(spacing: Spacing.m) {
                if leak.status != .resolved {
                    Button(action: {
                        Task {
                            do {
                                try await viewModel.resolveLeak(leakId: leak.id)
                            } catch {
                                // Ошибка уже обработана в ViewModel
                            }
                        }
                    }) {
                        Label(localizationManager.localized("dark_web_action_resolved"), systemImage: "checkmark.circle")
                            .font(.caption)
                            .foregroundColor(.successGreen)
                    }
                }
                
                Button(action: {
                    // Открываем системные настройки для смены пароля
                    if let url = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(url)
                    }
                }) {
                    Label(localizationManager.localized("dark_web_action_change_password"), systemImage: "key.fill")
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
    
    private func statusBadge(_ status: LeakStatus) -> some View {
        Text(status.localizedDisplayName(localizationManager))
            .font(.caption2)
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.xs)
            .padding(.vertical, 2)
            .background(
                Capsule()
                    .fill(status == .new ? Color.dangerRed : status == .resolved ? Color.successGreen : Color.textSecondary)
            )
    }
    
    private func severityBadge(_ severity: LeakSeverity) -> some View {
        Text(severity.localizedDisplayName(localizationManager))
            .font(.caption2)
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.xs)
            .padding(.vertical, 2)
            .background(
                Capsule()
                    .fill(severity == .critical || severity == .high ? Color.dangerRed : Color.warningOrange)
            )
    }
    
    // MARK: - Scans Section
    
    private var scansSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("dark_web_scans_history"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                // Кнопка запуска сканирования
                Button(action: {
                    Task {
                        await viewModel.startScan()
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "magnifyingglass")
                            .font(.caption)
                        Text(localizationManager.localized("dark_web_scan_start"))
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
                .disabled(viewModel.isScanning)
            }
            
            if viewModel.scans.isEmpty {
                emptyScansView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(viewModel.scans) { scan in
                        scanRow(scan: scan)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func scanRow(scan: DarkWebScan) -> some View {
        HStack {
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(scan.formattedScanDate)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                HStack(spacing: Spacing.m) {
                    Label("\(scan.databasesScanned)", systemImage: "database.fill")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Label("\(scan.newLeaksFound)", systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundColor(scan.newLeaksFound > 0 ? .dangerRed : .textSecondary)
                }
            }
            
            Spacer()
            
            Text(scan.status.localizedDisplayName(localizationManager))
                .font(.caption2)
                .foregroundColor(.white)
                .padding(.horizontal, Spacing.xs)
                .padding(.vertical, 2)
                .background(
                    Capsule()
                        .fill(scan.status == .completed ? Color.successGreen : scan.status == .inProgress ? Color.primaryBlue : Color.dangerRed)
                )
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Empty States
    
    private var emptyLeaksView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "checkmark.shield.fill")
                .font(.system(size: 48))
                .foregroundColor(.successGreen)
            
            Text(localizationManager.localized("dark_web_no_leaks"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
    }
    
    private var emptyScansView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("dark_web_no_scans"))
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
    
    private func loadData() async {
        let status = filterStatus == "all" ? nil : filterStatus
        let severity = filterSeverity == "all" ? nil : filterSeverity
        await viewModel.loadData(status: status, severity: severity)
    }
}

// MARK: - Preview

#if DEBUG
struct DarkWebMonitoringModal_Previews: PreviewProvider {
    static var previews: some View {
        DarkWebMonitoringModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif


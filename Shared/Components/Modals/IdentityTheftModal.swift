import SwiftUI

/**
 * 🛡️ Identity Theft Protection Modal
 * Модальное окно для просмотра попыток кражи личности
 * Включает историю попыток, заблокированные запросы и статистику
 */

struct IdentityTheftModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = IdentityTheftViewModel()
    
    // Фильтры
    @AppStorage("identity_theft_filter_action") private var filterAction: String = "all"
    @AppStorage("identity_theft_filter_severity") private var filterSeverity: String = "all"
    @State private var selectedTab: TabType = .attempts
    
    enum TabType: String, CaseIterable {
        case attempts = "attempts"
        case blocked = "blocked"
        case suspicious = "suspicious"
        
        var displayName: String {
            switch self {
            case .attempts: return "Попытки"
            case .blocked: return "Заблокировано"
            case .suspicious: return "Подозрительные"
            }
        }
        
        var icon: String {
            switch self {
            case .attempts: return "exclamationmark.shield.fill"
            case .blocked: return "hand.raised.fill"
            case .suspicious: return "eye.fill"
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
                            if selectedTab == .attempts {
                                attemptsSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            } else if selectedTab == .blocked {
                                blockedSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            } else {
                                suspiciousSection
                                    .padding(.horizontal, Spacing.screenPadding)
                            }
                            
                            Spacer(minLength: 100)
                        }
                        .padding(.top, Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("identity_theft_modal_title"))
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
    }
    
    // MARK: - Stats Section
    
    private func statsSection(stats: IdentityTheftStats) -> some View {
        HStack(spacing: Spacing.s) {
            statCard(
                icon: "exclamationmark.shield.fill",
                title: localizationManager.localized("identity_theft_total_attempts"),
                value: "\(stats.totalAttempts)",
                color: .dangerRed
            )
            
            statCard(
                icon: "hand.raised.fill",
                title: localizationManager.localized("identity_theft_blocked"),
                value: "\(stats.blockedAttempts)",
                color: .successGreen
            )
            
            statCard(
                icon: "eye.fill",
                title: localizationManager.localized("identity_theft_suspicious"),
                value: "\(stats.suspiciousActivities)",
                color: .warningOrange
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
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: Spacing.s) {
                ForEach(TabType.allCases, id: \.self) { tab in
                    Button(action: {
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                            selectedTab = tab
                        }
                    }) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: tab.icon)
                                .font(.caption)
                            Text(tab.displayName)
                                .font(.body)
                        }
                        .foregroundColor(selectedTab == tab ? .white : .textPrimary)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.s)
                        .background(
                            Capsule()
                                .fill(selectedTab == tab ? Color.primaryBlue : Color.backgroundMedium)
                        )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Attempts Section
    
    private var attemptsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Фильтры
            filtersSection
            
            // Список попыток
            if viewModel.attempts.isEmpty {
                emptyAttemptsView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(viewModel.attempts) { attempt in
                        attemptRow(attempt: attempt)
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
            Text(localizationManager.localized("identity_theft_filters"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            HStack(spacing: Spacing.s) {
                // Фильтр по действию
                Menu {
                    Button(action: { filterAction = "all" }) {
                        Label("Все", systemImage: filterAction == "all" ? "checkmark" : "")
                    }
                    Button(action: { filterAction = "blocked" }) {
                        Label("Заблокировано", systemImage: filterAction == "blocked" ? "checkmark" : "")
                    }
                    Button(action: { filterAction = "allowed" }) {
                        Label("Разрешено", systemImage: filterAction == "allowed" ? "checkmark" : "")
                    }
                } label: {
                    HStack {
                        Text(filterAction == "all" ? "Все действия" : filterAction == "blocked" ? "Заблокировано" : "Разрешено")
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
                        Label("Все", systemImage: filterSeverity == "all" ? "checkmark" : "")
                    }
                    Button(action: { filterSeverity = "critical" }) {
                        Label("Критично", systemImage: filterSeverity == "critical" ? "checkmark" : "")
                    }
                    Button(action: { filterSeverity = "high" }) {
                        Label("Высокая", systemImage: filterSeverity == "high" ? "checkmark" : "")
                    }
                } label: {
                    HStack {
                        Text(filterSeverity == "all" ? "Вся критичность" : filterSeverity == "critical" ? "Критично" : "Высокая")
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
    
    private func attemptRow(attempt: IdentityTheftAttempt) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                // Тип данных
                HStack(spacing: Spacing.xs) {
                    Text(attempt.dataType.icon)
                        .font(.caption)
                    Text(attempt.dataType.displayName)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                // Действие
                actionBadge(attempt.action)
                
                // Критичность
                severityBadge(attempt.severity)
            }
            
            // Источник запроса
            HStack(spacing: Spacing.xs) {
                Image(systemName: "globe")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                Text(attempt.requestSource)
                    .font(.body)
                    .foregroundColor(.textPrimary)
            }
            
            // Дата и время
            Text(attempt.formattedTimestamp)
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            // Детали
            if let details = attempt.details {
                Text(details)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .padding(.top, Spacing.xs)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func actionBadge(_ action: AttemptAction) -> some View {
        HStack(spacing: Spacing.xs) {
            Text(action.icon)
                .font(.caption)
            Text(action.displayName)
                .font(.caption2)
                .foregroundColor(.white)
        }
        .padding(.horizontal, Spacing.xs)
        .padding(.vertical, 2)
        .background(
            Capsule()
                .fill(action == .blocked ? Color.successGreen : action == .suspicious ? Color.warningOrange : Color.primaryBlue)
        )
    }
    
    private func severityBadge(_ severity: AttemptSeverity) -> some View {
        Text(severity.displayName)
            .font(.caption2)
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.xs)
            .padding(.vertical, 2)
            .background(
                Capsule()
                    .fill(severity == .critical || severity == .high ? Color.dangerRed : Color.warningOrange)
            )
    }
    
    // MARK: - Blocked Section
    
    private var blockedSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("identity_theft_blocked_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            let blockedAttempts = viewModel.attempts.filter { $0.action == AttemptAction.blocked }
            
            if blockedAttempts.isEmpty {
                emptyBlockedView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(blockedAttempts) { attempt in
                        attemptRow(attempt: attempt)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Suspicious Section
    
    private var suspiciousSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("identity_theft_suspicious_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            let suspiciousAttempts = viewModel.attempts.filter { $0.action == AttemptAction.suspicious }
            
            if suspiciousAttempts.isEmpty {
                emptySuspiciousView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(suspiciousAttempts) { attempt in
                        attemptRow(attempt: attempt)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Empty States
    
    private var emptyAttemptsView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "checkmark.shield.fill")
                .font(.system(size: 48))
                .foregroundColor(.successGreen)
            
            Text(localizationManager.localized("identity_theft_no_attempts"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
    }
    
    private var emptyBlockedView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "hand.raised.fill")
                .font(.system(size: 48))
                .foregroundColor(.successGreen)
            
            Text(localizationManager.localized("identity_theft_no_blocked"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
    }
    
    private var emptySuspiciousView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "eye.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("identity_theft_no_suspicious"))
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
        let action = filterAction == "all" ? nil : filterAction
        let severity = filterSeverity == "all" ? nil : filterSeverity
        await viewModel.loadData(action: action, severity: severity)
    }
}

// MARK: - Preview

#if DEBUG
struct IdentityTheftModal_Previews: PreviewProvider {
    static var previews: some View {
        IdentityTheftModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif


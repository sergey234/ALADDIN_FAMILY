import SwiftUI

/**
 * 🤖 AI Categories Modal
 * Модальное окно для просмотра статистики AI категоризации контента
 * Включает селектор ребенка, статистику по категориям и заблокированный контент
 */

struct AICategoriesModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = AICategoriesViewModel()
    
    // Выбранный ребенок
    @AppStorage("ai_categories_selected_child_id") private var selectedChildId: String = ""
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Селектор ребенка (только для родителей)
                        if !viewModel.children.isEmpty {
                            UserSelectorView(
                                selectedUserId: Binding(
                                    get: { selectedChildId.isEmpty ? nil : selectedChildId },
                                    set: { newValue in
                                        selectedChildId = newValue ?? ""
                                        loadReports()
                                    }
                                ),
                                users: viewModel.children,
                                currentUserId: "",
                                showCurrentUser: false
                            )
                            .padding(.horizontal, Spacing.screenPadding)
                            .padding(.top, Spacing.m)
                        }
                        
                        // Статистика
                        if let stats = viewModel.stats {
                            statsSection(stats: stats)
                                .padding(.horizontal, Spacing.screenPadding)
                        }
                        
                        // Категории
                        categoriesSection
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        // Заблокированный контент
                        blockedContentSection
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
            }
            .navigationTitle(localizationManager.localized("ai_categories_modal_title"))
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
            await loadChildren()
            await loadReports()
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
    
    private func statsSection(stats: AICategoriesStats) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("ai_categories_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: Spacing.s) {
                statCard(
                    icon: "globe",
                    title: localizationManager.localized("ai_categories_categorized"),
                    value: "\(stats.totalCategorized)",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "hand.raised.fill",
                    title: localizationManager.localized("ai_categories_blocked"),
                    value: "\(stats.totalBlocked)",
                    color: .dangerRed
                )
                
                statCard(
                    icon: "percent",
                    title: localizationManager.localized("ai_categories_accuracy"),
                    value: stats.formattedAccuracy,
                    color: .successGreen
                )
            }
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
    
    // MARK: - Categories Section
    
    private var categoriesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("ai_categories_by_category_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            if let stats = viewModel.stats {
                VStack(spacing: Spacing.s) {
                    ForEach(ContentCategory.allCases, id: \.self) { category in
                        if let count = stats.byCategory[category.rawValue], count > 0 {
                            categoryRow(
                                category: category,
                                count: count,
                                blocked: stats.blockedByCategory[category.rawValue] ?? 0
                            )
                        }
                    }
                }
            } else {
                emptyCategoriesView
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func categoryRow(category: ContentCategory, count: Int, blocked: Int) -> some View {
        HStack {
            // Иконка категории
            Text(category.icon)
                .font(.title2)
                .frame(width: 40)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(category.displayName)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                HStack(spacing: Spacing.m) {
                    Label("\(count)", systemImage: "globe")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    if blocked > 0 {
                        Label("\(blocked) заблокировано", systemImage: "hand.raised.fill")
                            .font(.caption)
                            .foregroundColor(.dangerRed)
                    }
                }
            }
            
            Spacer()
            
            // Процент заблокированного
            if count > 0 {
                let percentage = Double(blocked) / Double(count) * 100
                Text("\(Int(percentage))%")
                    .font(.captionBold)
                    .foregroundColor(percentage > 50 ? .dangerRed : percentage > 20 ? .warningOrange : .textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Blocked Content Section
    
    private var blockedContentSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("ai_categories_blocked_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            let blockedReports = viewModel.reports.filter { $0.blockedCount > 0 }
            
            if blockedReports.isEmpty {
                emptyBlockedContentView
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(blockedReports.prefix(10)) { report in
                        blockedContentRow(report: report)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func blockedContentRow(report: AICategoryReport) -> some View {
        HStack {
            Text(report.category.icon)
                .font(.title3)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(report.category.displayName)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                if let childName = report.childName {
                    Text("Для: \(childName)")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: Spacing.xs) {
                Text("\(report.blockedCount)")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.dangerRed)
                
                Text("заблокировано")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Empty States
    
    private var emptyCategoriesView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "chart.bar.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            
            Text(localizationManager.localized("ai_categories_no_data"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.xxl)
    }
    
    private var emptyBlockedContentView: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "checkmark.shield.fill")
                .font(.system(size: 48))
                .foregroundColor(.successGreen)
            
            Text(localizationManager.localized("ai_categories_no_blocked"))
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
    
    private func loadChildren() async {
        await viewModel.loadChildren()
    }
    
    private func loadReports() {
        Task {
            let childId = selectedChildId.isEmpty ? nil : selectedChildId
            await viewModel.loadReports(childId: childId)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct AICategoriesModal_Previews: PreviewProvider {
    static var previews: some View {
        AICategoriesModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif


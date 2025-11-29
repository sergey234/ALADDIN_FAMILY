import SwiftUI
import Foundation

/// 📊 Упрощённый экран аналитики: главные карточки + разбивка угроз + уровень защиты
struct AnalyticsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = AnalyticsScreen.makeViewModel()
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("analytics_accessibility_background"))
            
            VStack(spacing: 0) {
                navigationHeader
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        mainStats
                        threatBreakdown
                        protectionBlock
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("analytics_accessibility_summary"))
            }
        }
        .navigationBarHidden(true)
        .task { await viewModel.load() }
        .id("analytics_lang_\(localizationManager.currentLanguage.rawValue)")
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
    
    // MARK: - Header
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("analytics_title"),
            subtitle: localizationManager.localized("analytics_subtitle"),
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            rightButtons: [],
            onBack: { navigationManager.goBack() }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("analytics_accessibility_navbar"))
    }
    
    // MARK: - Main stats
    private var mainStats: some View {
        HStack(spacing: Spacing.s) {
            compactStatCard(
                icon: "shield.fill",
                value: "\(viewModel.threatsBlocked)",
                label: localizationManager.localized("analytics_blocked_short")
            )
            compactStatCard(
                icon: "magnifyingglass",
                value: "\(viewModel.itemsScanned)",
                label: localizationManager.localized("analytics_scanned_short")
            )
            compactStatCard(
                icon: "exclamationmark.triangle.fill",
                value: "\(viewModel.threatsDetected)",
                label: localizationManager.localized("analytics_detected_short")
            )
            compactStatCard(
                icon: "percent",
                value: effectivenessText,
                label: localizationManager.localized("analytics_effectiveness_short")
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Threat breakdown
    private var threatBreakdown: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_detailed_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                if viewModel.threatCategories.isEmpty {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.vertical, Spacing.l)
                } else {
                    ForEach(Array(viewModel.threatCategories.enumerated()), id: \.element.id) { index, category in
                        threatRow(for: category, color: colorForThreat(at: index))
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Protection block
    private var protectionBlock: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_protection"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                ProgressView(value: min(max(viewModel.protectionLevel / 100.0, 0), 1))
                    .progressViewStyle(.linear)
                    .tint(.primaryBlue)
                
                HStack {
                    Text(localizationManager.localized("analytics_protected"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text("\(Int(viewModel.protectionLevel))%")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helpers
    private func compactStatCard(icon: String, value: String, label: String) -> some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 18))
                .foregroundColor(.primaryBlue)
            Text(value)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.textPrimary)
                .lineLimit(1)
            Text(label)
                .font(.system(size: 10))
                .foregroundColor(.textSecondary)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: localizationManager.localized("analytics_accessibility_stat_value"),
                label,
                value
            )
        )
    }
    
    private func threatRow(for category: ThreatTypeCount, color: Color) -> some View {
        detailRow(
            icon: category.icon ?? iconName(for: category.type),
            title: localizedThreatTitle(for: category.type),
            value: "\(category.count)",
            color: color
        )
    }
    
    private func detailRow(icon: String, title: String, value: String, color: Color) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(color)
                .frame(width: 24)
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: localizationManager.localized("analytics_accessibility_stat_value"),
                title,
                value
            )
        )
    }
    
    private func iconName(for type: String) -> String {
        switch type.lowercased() {
        case "web": return "globe"
        case "file": return "doc"
        case "app": return "iphone"
        case "network": return "shield"
        default: return "shield"
        }
    }
    
    private func localizedThreatTitle(for type: String) -> String {
        switch type.lowercased() {
        case "web": return localizationManager.localized("analytics_web_threats")
        case "file": return localizationManager.localized("analytics_file_threats")
        case "network": return localizationManager.localized("analytics_network_threats")
        case "app": return localizationManager.localized("analytics_app_threats")
        default: return type.capitalized
        }
    }
    
    private func colorForThreat(at index: Int) -> Color {
        let palette: [Color] = [.dangerRed, .warningOrange, .primaryBlue, .successGreen]
        return index < palette.count ? palette[index] : .primaryBlue
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    private var effectivenessText: String {
        guard viewModel.threatsDetected > 0 else { return "0%" }
        let ratio = Double(viewModel.threatsBlocked) / Double(viewModel.threatsDetected)
        let percent = Int(max(0, min(100, round(ratio * 100))))
        return "\(percent)%"
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
}

private extension AnalyticsScreen {
    static func makeViewModel() -> AnalyticsViewModel {
        let baseURL = URL(string: AppConfig.baseURL) ?? URL(string: "https://api.aladdin.family/api")!
        let service = RemoteAnalyticsService(
            baseURL: baseURL,
            authTokenProvider: makeTokenProvider()
        )
        return AnalyticsViewModel(service: service)
    }
    
    private static func makeTokenProvider() -> () -> String? {
        return {
            if let token = KeychainManager.shared.loadString(forKey: .authToken) {
                return token
            }
            return AppConfig.authToken
        }
    }
}

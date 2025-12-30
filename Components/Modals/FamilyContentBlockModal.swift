import SwiftUI

/**
 * 🔒 Family Content Block Modal
 * Модальное окно для настройки блокировки контента в Safari
 */

struct FamilyContentBlockModal: View {
    
    // MARK: - Dependencies
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    // MARK: - Binding
    
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    
    // MARK: - State
    
    @StateObject private var contentBlockerManager = ContentBlockerManager.shared
    @State private var selectedCategories: Set<ContentBlockerCategory> = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var showSettingsAlert: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Заголовок
                        headerSection
                        
                        // Описание
                        descriptionSection
                        
                        // Список категорий
                        categoriesSection
                        
                        // Инструкция по активации
                        activationInstructionSection
                        
                        // Кнопки действий
                        actionButtonsSection
                    }
                    .padding(Spacing.screenPadding)
                }
            }
            .navigationTitle(localizationManager.localized("family_content_block_modal_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        HapticFeedback.selection()
                        dismiss()
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
        .onAppear {
            loadSettings()
        }
        .alert(localizationManager.localized("content_block_alert_title"), isPresented: $showSettingsAlert) {
            Button(localizationManager.localized("content_block_alert_open_settings")) {
                contentBlockerManager.openSettings()
            }
            Button(localizationManager.localized("content_block_alert_cancel"), role: .cancel) {}
        } message: {
            Text(localizationManager.localized("content_block_alert_message"))
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: Spacing.s) {
            Image(systemName: "hand.raised.fill")
                .font(.system(size: 48))
                .foregroundColor(.primaryBlue)
            
            Text(localizationManager.localized("content_block_header_title"))
                .font(.h2)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
        }
        .padding(.top, Spacing.l)
    }
    
    // MARK: - Description Section
    
    private var descriptionSection: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(localizationManager.localized("content_block_description"))
                .font(.body)
                .foregroundColor(.textSecondary)
            
            if let errorMessage = errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
                    .padding(.top, Spacing.xs)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, Spacing.s)
    }
    
    // MARK: - Categories Section
    
    private var categoriesSection: some View {
        VStack(spacing: Spacing.s) {
            ForEach(ContentBlockerCategory.allCases, id: \.self) { category in
                CategoryToggleRow(
                    category: category,
                    isSelected: selectedCategories.contains(category),
                    onToggle: {
                        HapticFeedback.selection()
                        if selectedCategories.contains(category) {
                            selectedCategories.remove(category)
                        } else {
                            selectedCategories.insert(category)
                        }
                    }
                )
                .environmentObject(localizationManager)
            }
        }
        .padding(.vertical, Spacing.m)
    }
    
    // MARK: - Activation Instruction Section
    
    private var activationInstructionSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.s) {
                Image(systemName: "info.circle.fill")
                    .foregroundColor(.warningOrange)
                Text(localizationManager.localized("content_block_instructions_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                ContentBlockerInstructionStep(number: 1, text: localizationManager.localized("content_block_step_1"))
                ContentBlockerInstructionStep(number: 2, text: localizationManager.localized("content_block_step_2"))
                ContentBlockerInstructionStep(number: 3, text: localizationManager.localized("content_block_step_3"))
                ContentBlockerInstructionStep(number: 4, text: localizationManager.localized("content_block_step_4"))
            }
            .padding(.leading, Spacing.m)
        }
        .padding(Spacing.m)
        .background(Color.warningOrange.opacity(0.1))
        .cornerRadius(CornerRadius.medium)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(Color.warningOrange.opacity(0.3), lineWidth: 1)
        )
    }
    
    // MARK: - Action Buttons Section
    
    private var actionButtonsSection: some View {
        VStack(spacing: Spacing.m) {
            // Кнопка "Открыть настройки iOS"
            Button(action: {
                HapticFeedback.impact(.medium)
                showSettingsAlert = true
            }) {
                HStack {
                    Image(systemName: "gear")
                    Text(localizationManager.localized("content_block_open_settings"))
                }
                .font(.bodyBold)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(Color.primaryBlue)
                .cornerRadius(CornerRadius.medium)
            }
            
            // Кнопка "Применить правила"
            Button(action: {
                HapticFeedback.impact(.medium)
                applyRules()
            }) {
                HStack {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(.circular)
                            .tint(.white)
                    } else {
                        Image(systemName: "checkmark.circle.fill")
                    }
                    Text(localizationManager.localized("content_block_apply_rules"))
                }
                .font(.bodyBold)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(selectedCategories.isEmpty ? Color.gray : Color.successGreen)
                .cornerRadius(CornerRadius.medium)
            }
            .disabled(isLoading || selectedCategories.isEmpty)
            
            // Статус блокировки
            if case .enabled = contentBlockerManager.status {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.successGreen)
                    Text(String(format: localizationManager.localized("content_block_status_active"), contentBlockerManager.blockedSitesCount))
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
                .padding(.top, Spacing.s)
            } else if case .needsActivation = contentBlockerManager.status {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.warningOrange)
                    Text(localizationManager.localized("content_block_status_needs_activation"))
                        .font(.caption)
                        .foregroundColor(.warningOrange)
                }
                .padding(.top, Spacing.s)
            }
        }
        .padding(.top, Spacing.l)
    }
    
    // MARK: - Methods
    
    private func loadSettings() {
        contentBlockerManager.loadActiveCategories()
        selectedCategories = Set(contentBlockerManager.activeCategories)
        
        Task {
            await contentBlockerManager.checkBlockingStatus()
        }
    }
    
    private func applyRules() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let categories = Array(selectedCategories)
                try await contentBlockerManager.enableContentBlocker(categories: categories)
                
                await MainActor.run {
                    isEnabled = true
                    isLoading = false
                    
                    // Показать успешное сообщение
                    HapticFeedback.notification(.success)
                }
                
                // Обновить статус
                await contentBlockerManager.checkBlockingStatus()
                
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = error.localizedDescription
                    
                    if let blockerError = error as? ContentBlockerError,
                       blockerError == .needsActivation {
                        showSettingsAlert = true
                    }
                }
            }
        }
    }
}

// MARK: - Category Toggle Row

struct CategoryToggleRow: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let category: ContentBlockerCategory
    let isSelected: Bool
    let onToggle: () -> Void
    
    private var localizedCategoryName: String {
        switch category {
        case .adult: return localizationManager.localized("content_category_adult")
        case .violence: return localizationManager.localized("content_category_violence")
        case .gambling: return localizationManager.localized("content_category_gambling")
        case .socialMedia: return localizationManager.localized("content_category_social_media")
        case .video: return localizationManager.localized("content_category_video")
        case .games: return localizationManager.localized("content_category_games")
        case .shopping: return localizationManager.localized("content_category_shopping")
        case .news: return localizationManager.localized("content_category_news")
        case .forums: return localizationManager.localized("content_category_forums")
        case .fileSharing: return localizationManager.localized("content_category_file_sharing")
        case .proxy: return localizationManager.localized("content_category_proxy")
        case .vpn: return localizationManager.localized("content_category_vpn")
        }
    }
    
    var body: some View {
        Button(action: onToggle) {
            HStack(spacing: Spacing.m) {
                // Иконка категории
                Text(category.icon)
                    .font(.title2)
                
                // Название категории
                Text(localizedCategoryName)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                // Переключатель
                Image(systemName: isSelected ? "checkmark.circle.fill" : "circle")
                    .font(.title3)
                    .foregroundColor(isSelected ? .successGreen : .textSecondary)
            }
            .padding(Spacing.m)
            .background(isSelected ? Color.successGreen.opacity(0.1) : Color.clear)
            .cornerRadius(CornerRadius.medium)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(isSelected ? Color.successGreen.opacity(0.5) : Color.textSecondary.opacity(0.2), lineWidth: 1)
            )
        }
    }
}

// MARK: - Instruction Step

struct ContentBlockerInstructionStep: View {
    let number: Int
    let text: String
    
    var body: some View {
        HStack(spacing: Spacing.s) {
            Text("\(number).")
                .font(.bodyBold)
                .foregroundColor(.warningOrange)
                .frame(width: 24)
            
            Text(text)
                .font(.body)
                .foregroundColor(.textPrimary)
        }
    }
}


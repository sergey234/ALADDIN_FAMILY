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
        .alert("Включить блокировку в Safari", isPresented: $showSettingsAlert) {
            Button("Открыть настройки") {
                contentBlockerManager.openSettings()
            }
            Button("Отмена", role: .cancel) {}
        } message: {
            Text("Для работы блокировки контента необходимо:\n\n1. Открыть Настройки iOS\n2. Перейти в Safari\n3. Выбрать Content Blockers\n4. Включить ALADDIN")
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: Spacing.s) {
            Image(systemName: "hand.raised.fill")
                .font(.system(size: 48))
                .foregroundColor(.primaryBlue)
            
            Text("Блокировка контента в Safari")
                .font(.h2)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
        }
        .padding(.top, Spacing.l)
    }
    
    // MARK: - Description Section
    
    private var descriptionSection: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text("Выберите категории контента, которые будут заблокированы в Safari:")
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
                Text("Для работы блокировки необходимо:")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                ContentBlockerInstructionStep(number: 1, text: "Открыть Настройки iOS")
                ContentBlockerInstructionStep(number: 2, text: "Перейти в Safari")
                ContentBlockerInstructionStep(number: 3, text: "Выбрать Content Blockers")
                ContentBlockerInstructionStep(number: 4, text: "Включить ALADDIN")
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
                    Text("Открыть настройки iOS")
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
                    Text("Применить правила")
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
                    Text("Блокировка активна: \(contentBlockerManager.blockedSitesCount) сайтов")
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
                .padding(.top, Spacing.s)
            } else if case .needsActivation = contentBlockerManager.status {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.warningOrange)
                    Text("Требуется активация в настройках iOS")
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
    let category: ContentBlockerCategory
    let isSelected: Bool
    let onToggle: () -> Void
    
    var body: some View {
        Button(action: onToggle) {
            HStack(spacing: Spacing.m) {
                // Иконка категории
                Text(category.icon)
                    .font(.title2)
                
                // Название категории
                Text(category.displayName)
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


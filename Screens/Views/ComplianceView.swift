import SwiftUI

/**
 * ⚖️ Compliance View
 * Экран настройки соответствия требованиям (152-ФЗ, защита детей)
 * Компоненты: russian_child_protection_manager, russian_data_protection_manager
 */

struct ComplianceView: View {
    
    enum ComplianceSection {
        case childProtection
        case dataProtection
    }
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var configurationService = ComponentConfigurationService.shared
    @StateObject private var toastManager = ToastManager.shared
    
    let section: ComplianceSection
    
    // Child Protection
    @State private var childLegalProfile: String = "children"
    @State private var selectedRegions: Set<String> = []
    @State private var deletionPolicy: String = "automatic"
    
    // Data Protection
    @State private var dataSelectedRegions: Set<String> = []
    @State private var dataDeletionPolicy: String = "automatic"
    @State private var encryptionEnabled: Bool = true
    
    var russianRegions: [(key: String, localized: String)] {
        [
            ("moscow", localizationManager.localized("compliance_region_moscow")),
            ("spb", localizationManager.localized("compliance_region_spb")),
            ("moscow_oblast", localizationManager.localized("compliance_region_moscow_oblast")),
            ("leningrad_oblast", localizationManager.localized("compliance_region_leningrad_oblast"))
        ]
    }
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: section == .childProtection
                        ? localizationManager.localized("component_russian_child_protection_manager_title")
                        : localizationManager.localized("component_russian_data_protection_manager_title"),
                    subtitle: section == .childProtection
                        ? localizationManager.localized("component_russian_child_protection_manager_description")
                        : localizationManager.localized("component_russian_data_protection_manager_description"),
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        if section == .childProtection {
                            childProtectionContent
                        } else {
                            dataProtectionContent
                        }
                        
                        saveButton
                            .padding(.top, Spacing.m)
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Child Protection Content
    
    private var childProtectionContent: some View {
        VStack(spacing: Spacing.l) {
            // Legal Profile
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_legal_profile_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                Picker("", selection: $childLegalProfile) {
                    Text(localizationManager.localized("compliance_profile_children")).tag("children")
                    Text(localizationManager.localized("compliance_profile_adults")).tag("adults")
                }
                .pickerStyle(.segmented)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            
            // Regions
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_regions_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                ForEach(russianRegions, id: \.key) { region in
                    Toggle(
                        region.localized,
                        isOn: Binding(
                            get: { selectedRegions.contains(region.key) },
                            set: { isOn in
                                if isOn {
                                    selectedRegions.insert(region.key)
                                } else {
                                    selectedRegions.remove(region.key)
                                }
                            }
                        )
                    )
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            
            // Storage Policy (Fixed values according to privacy policy)
            storagePolicyInfoCards
            
            // Deletion Policy
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_deletion_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                Picker("", selection: $deletionPolicy) {
                    Text(localizationManager.localized("compliance_deletion_automatic")).tag("automatic")
                    Text(localizationManager.localized("compliance_deletion_manual")).tag("manual")
                }
                .pickerStyle(.segmented)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
    }
    
    // MARK: - Data Protection Content
    
    private var dataProtectionContent: some View {
        VStack(spacing: Spacing.l) {
            // Info Card: We don't collect personal data
            infoCardNoPersonalData
            
            // Regions
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_regions_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                ForEach(russianRegions, id: \.key) { region in
                    Toggle(
                        region.localized,
                        isOn: Binding(
                            get: { dataSelectedRegions.contains(region.key) },
                            set: { isOn in
                                if isOn {
                                    dataSelectedRegions.insert(region.key)
                                } else {
                                    dataSelectedRegions.remove(region.key)
                                }
                            }
                        )
                    )
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            
            // Storage Policy (Fixed values according to privacy policy)
            storagePolicyInfoCards
            
            // Encryption
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_encryption_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                Toggle(
                    localizationManager.localized("compliance_encryption_enabled"),
                    isOn: $encryptionEnabled
                )
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            
            // Deletion Policy
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_deletion_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                Picker("", selection: $dataDeletionPolicy) {
                    Text(localizationManager.localized("compliance_deletion_automatic")).tag("automatic")
                    Text(localizationManager.localized("compliance_deletion_manual")).tag("manual")
                }
                .pickerStyle(.segmented)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
    }
    
    // MARK: - Info Cards
    
    private var infoCardNoPersonalData: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Image(systemName: "info.circle.fill")
                    .foregroundColor(.primaryBlue)
                Text(localizationManager.localized("compliance_no_personal_data_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            Text(localizationManager.localized("compliance_no_personal_data_text"))
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.primaryBlue.opacity(0.1))
        )
    }
    
    private var storagePolicyInfoCards: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("compliance_storage_title"))
                .font(.title3)
                .foregroundColor(.textPrimary)
            
            // Анонимные сессии: 24 часа
            storageInfoCard(
                title: localizationManager.localized("compliance_storage_sessions_title"),
                value: localizationManager.localized("compliance_storage_sessions_value")
            )
            
            // Статистика угроз: 30 дней
            storageInfoCard(
                title: localizationManager.localized("compliance_storage_statistics_title"),
                value: localizationManager.localized("compliance_storage_statistics_value")
            )
            
            // Агрегированная аналитика: 1 год
            storageInfoCard(
                title: localizationManager.localized("compliance_storage_analytics_title"),
                value: localizationManager.localized("compliance_storage_analytics_value")
            )
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func storageInfoCard(title: String, value: String) -> some View {
        HStack {
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.primaryBlue)
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.2))
        )
    }
    
    private var saveButton: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            saveSettings()
        }) {
            Text(localizationManager.localized("common_save"))
                .font(.bodyBold)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.primaryBlue)
                .cornerRadius(CornerRadius.medium)
        }
        .buttonStyle(PlainButtonStyle())
        .accessibilityLabel(localizationManager.localized("common_save"))
    }
    
    // MARK: - Methods
    
    private func saveSettings() {
        // Тактильная обратная связь
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        Task {
            // TODO: Сохранить настройки через API
            await MainActor.run {
                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                // Закрыть окно после сохранения
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    dismiss()
                }
            }
        }
    }
}


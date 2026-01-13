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
    @State private var storagePolicy: Int = 90 // дней
    @State private var deletionPolicy: String = "automatic"
    
    // Data Protection
    @State private var dataLegalProfile: String = "individual"
    @State private var dataSelectedRegions: Set<String> = []
    @State private var dataStoragePolicy: Int = 365 // дней
    @State private var dataDeletionPolicy: String = "automatic"
    @State private var encryptionEnabled: Bool = true
    
    let russianRegions = ["Москва", "Санкт-Петербург", "Московская область", "Ленинградская область"]
    
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
                
                ForEach(russianRegions, id: \.self) { region in
                    Toggle(
                        region,
                        isOn: Binding(
                            get: { selectedRegions.contains(region) },
                            set: { isOn in
                                if isOn {
                                    selectedRegions.insert(region)
                                } else {
                                    selectedRegions.remove(region)
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
            
            // Storage Policy
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_storage_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                HStack {
                    Text("\(storagePolicy)")
                        .font(.headline)
                    Text(localizationManager.localized("compliance_storage_days"))
                        .font(.body)
                    Spacer()
                }
                
                Slider(value: Binding(
                    get: { Double(storagePolicy) },
                    set: { storagePolicy = Int($0) }
                ), in: 30...365, step: 1)
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
            // Legal Profile
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_legal_profile_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                Picker("", selection: $dataLegalProfile) {
                    Text(localizationManager.localized("compliance_profile_individual")).tag("individual")
                    Text(localizationManager.localized("compliance_profile_legal")).tag("legal")
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
                
                ForEach(russianRegions, id: \.self) { region in
                    Toggle(
                        region,
                        isOn: Binding(
                            get: { dataSelectedRegions.contains(region) },
                            set: { isOn in
                                if isOn {
                                    dataSelectedRegions.insert(region)
                                } else {
                                    dataSelectedRegions.remove(region)
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
            
            // Storage Policy
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("compliance_storage_title"))
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                
                HStack {
                    Text("\(dataStoragePolicy)")
                        .font(.headline)
                    Text(localizationManager.localized("compliance_storage_days"))
                        .font(.body)
                    Spacer()
                }
                
                Slider(value: Binding(
                    get: { Double(dataStoragePolicy) },
                    set: { dataStoragePolicy = Int($0) }
                ), in: 90...1095, step: 1)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            
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
    
    private var saveButton: some View {
        Button(action: saveSettings) {
            Text(localizationManager.localized("common.save"))
                .font(.bodyBold)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.primaryBlue)
                .cornerRadius(CornerRadius.medium)
        }
    }
    
    // MARK: - Methods
    
    private func saveSettings() {
        Task {
            // TODO: Сохранить настройки через API
            toastManager.showSuccess("Настройки сохранены")
        }
    }
}


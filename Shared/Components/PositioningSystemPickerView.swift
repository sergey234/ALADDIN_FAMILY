import SwiftUI

/**
 * 🛰️ Positioning System Picker View
 * Модальное окно для выбора системы позиционирования
 */

struct PositioningSystemPickerView: View {
    
    @Binding var selectedSystem: PositioningSystem
    let currentSystem: PositioningSystem
    let currentRegion: String
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Информация о текущей системе
                        currentSystemInfo
                            .padding(.horizontal, Spacing.screenPadding)
                            .padding(.top, Spacing.m)
                        
                        // Список систем
                        systemsList
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
            }
            .navigationTitle(localizationManager.localized("positioning_system_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        VisualLogger.shared.log(
                            "✅ Positioning saved = \(selectedSystem.rawValue)",
                            level: .success,
                            category: "SETTINGS.POSITIONING"
                        )
                        dismiss()
                    }) {
                        Text(localizationManager.localized("common_done"))
                            .foregroundColor(.primaryBlue)
                    }
                }
            }
        }
        .withVisualLogger()
    }
    
    // MARK: - Current System Info
    
    private var currentSystemInfo: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("positioning_system_current"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            HStack {
                Image(systemName: currentSystem.icon)
                    .font(.title2)
                    .foregroundColor(.primaryBlue)
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(currentSystem.localizedDisplayName(localizationManager))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(currentSystem.localizedDescription(localizationManager))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            
            if selectedSystem == .auto {
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "info.circle.fill")
                        .font(.caption2)
                        .foregroundColor(.infoBlue)
                    Text("\(localizationManager.localized("positioning_system_recommended")) \(currentRegion)")
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Systems List
    
    private var systemsList: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("positioning_system_subtitle"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(spacing: Spacing.s) {
                ForEach(PositioningSystem.allCases, id: \.self) { system in
                    systemRow(system: system)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func systemRow(system: PositioningSystem) -> some View {
        Button(action: {
            VisualLogger.shared.log(
                "🛰️ Positioning select = \(system.rawValue)",
                level: .info,
                category: "SETTINGS.POSITIONING"
            )
            selectedSystem = system
        }) {
            HStack {
                Image(systemName: system.icon)
                    .font(.title3)
                    .foregroundColor(.primaryBlue)
                    .frame(width: 40)
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(system.localizedDisplayName(localizationManager))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(system.localizedDescription(localizationManager))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                if selectedSystem == system {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title3)
                        .foregroundColor(.primaryBlue)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(selectedSystem == system ? Color.primaryBlue.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
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
}

// MARK: - Preview

#if DEBUG
struct PositioningSystemPickerView_Previews: PreviewProvider {
    static var previews: some View {
        PositioningSystemPickerView(
            selectedSystem: .constant(.auto),
            currentSystem: .glonass,
            currentRegion: "Россия"
        )
        .environmentObject(LocalizationManager())
    }
}
#endif


import SwiftUI

/// ⚙️ Единый экран настроек защиты от угроз
/// Управление всеми категориями защиты с группировкой и переключателями
struct ThreatProtectionSettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var settingsManager = ProtectionSettingsManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .shield)
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("protection_settings_title"),
                    subtitle: localizationManager.localized("protection_settings_subtitle"),
                    showBackButton: true,
                    onBack: {
                        navigationManager.goBack()
                    }
                )
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Группы категорий
                        ForEach(ProtectionGroup.allCases, id: \.self) { group in
                            ProtectionGroupSection(
                                group: group,
                                settingsManager: settingsManager,
                                tariffManager: tariffManager
                            )
                            .padding(.horizontal, Spacing.screenPadding)
                        }
                    }
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xxl)
                }
            }
            .onAppear {
                settingsManager.loadSettingsFromServer { _ in }
            }
        }
        .navigationBarHidden(true)
        .id("protection_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct ThreatProtectionSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        ThreatProtectionSettingsScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif


import SwiftUI

struct ThreatProtectionScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var isExpanded: Bool = true
    @State private var expandedCategory: ThreatProtectionCategory? = .cyberThreats
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("protection_catalog_title"),
                    subtitle: localizationManager.localized("protection_catalog_subtitle"),
                    showBackButton: true, // Всегда показываем кнопку "Назад" для возврата на главный экран
                    showProfileButton: false, // Убираем кнопку профиля
                    showListButton: false, // Убираем кнопку списка экранов
                    onBack: {
                        // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                        // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                        dismiss()
                        
                        // Дополнительно синхронизируем NavigationManager для корректной работы стека
                        DispatchQueue.main.async {
                            if navigationManager.canGoBack {
                                navigationManager.goBack(reason: "ThreatProtection.onBack")
                            } else {
                                // Если стек пустой, возвращаемся на главный экран
                                navigationManager.navigateTo(.main)
                            }
                        }
                    }
                )
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // ✅ НОВАЯ ГАЛЕРЕЯ: Карточки тарифов с полным функционалом
                        TariffFeaturesGallery()
                            .padding(.top, Spacing.m)
                        
                        // Основная карточка с категориями
                        ThreatProtectionCard(
                            icon: "🤖",
                            title: localizationManager.localized("protection_catalog_title"),
                            subtitle: localizationManager.localized("protection_catalog_subtitle"),
                            isExpanded: $isExpanded,
                            expandedCategory: $expandedCategory
                        )
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.bottom, Spacing.xxl)
                    }
                }
            }
        }
        .navigationBarHidden(true)
        .id("protection_catalog_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct ThreatProtectionScreen_Previews: PreviewProvider {
    static var previews: some View {
        ThreatProtectionScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif

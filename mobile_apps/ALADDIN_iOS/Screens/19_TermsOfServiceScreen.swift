import SwiftUI
import WebKit

/**
 * 📜 Terms of Service Screen
 * Условия использования
 * ОБЯЗАТЕЛЬНЫ для App Store!
 */

struct TermsOfServiceScreen: View {
    
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: "Условия использования",
                    subtitle: "Правила пользования сервисом",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                // Web View
                WebView(url: URL(string: "https://aladdin.family/terms")!)
                    .cornerRadius(CornerRadius.large)
                    .padding(Spacing.screenPadding)
            }
        }
        .navigationBarHidden(true)
    }
}

// MARK: - Preview

struct TermsOfServiceScreen_Previews: PreviewProvider {
    static var previews: some View {
        TermsOfServiceScreen()
    }
}




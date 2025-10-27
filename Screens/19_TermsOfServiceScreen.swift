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
            LinearGradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана условий использования")
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar()
                
                // Web View
                WebView(url: URL(string: "https://aladdin.family/terms")!)
                    .cornerRadius(12)
                    .padding(20)
                    .accessibilityElement(children: .contain)
                    .accessibilityLabel("Веб-страница условий использования")
            }
        }
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: 12)
        }
        .task {
            print("🚨 TermsOfServiceScreen загружен!")
        }
    }
}

// MARK: - Preview

struct TermsOfServiceScreen_Previews: PreviewProvider {
    static var previews: some View {
        TermsOfServiceScreen()
    }
}




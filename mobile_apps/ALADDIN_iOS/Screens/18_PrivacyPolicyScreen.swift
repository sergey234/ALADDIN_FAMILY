import SwiftUI
import WebKit

/**
 * 📋 Privacy Policy Screen
 * Политика конфиденциальности
 * ОБЯЗАТЕЛЬНА для App Store!
 */

struct PrivacyPolicyScreen: View {
    
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: "Политика конфиденциальности",
                    subtitle: "Как мы защищаем ваши данные",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                // Web View
                WebView(url: URL(string: "https://aladdin.family/privacy")!)
                    .cornerRadius(CornerRadius.large)
                    .padding(Spacing.screenPadding)
            }
        }
        .navigationBarHidden(true)
    }
}

/**
 * 🌐 Web View Wrapper
 * UIKit WebView обёрнутый в SwiftUI
 */

struct WebView: UIViewRepresentable {
    
    let url: URL
    
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.backgroundColor = .clear
        webView.isOpaque = false
        webView.load(URLRequest(url: url))
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {
        // No updates needed
    }
}

// MARK: - Preview

struct PrivacyPolicyScreen_Previews: PreviewProvider {
    static var previews: some View {
        PrivacyPolicyScreen()
    }
}




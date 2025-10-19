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
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    
                    Spacer()
                    
                    VStack {
                        Text("Политика конфиденциальности")
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Text("Как мы защищаем ваши данные")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                    
                    Color.clear
                        .frame(width: 40, height: 40)
                }
                .padding()
                .background(Color.black.opacity(0.5))
                
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




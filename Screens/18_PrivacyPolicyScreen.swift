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
            LinearGradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel("Фон экрана политики конфиденциальности")
            
            VStack(spacing: 0) {
                // Navigation Bar
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel("Назад")
                    .accessibilityHint("Нажмите для возврата к предыдущему экрану")
                    
                    Spacer()
                    
                    VStack {
                        Text("Политика конфиденциальности")
                            .font(.headline)
                            .foregroundColor(.white)
                            .accessibilityLabel("Политика конфиденциальности")
                            .accessibilityAddTraits(.isHeader)
                        
                        Text("Как мы защищаем ваши данные")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .accessibilityLabel("Как мы защищаем ваши данные")
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Заголовок политики конфиденциальности")
                    
                    Spacer()
                    
                    Color.clear
                        .frame(width: 40, height: 40)
                }
                .padding()
                .background(Color.black.opacity(0.5))
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Навигационная панель политики конфиденциальности")
                
                // Web View
                WebView(url: URL(string: "https://aladdin.family/privacy")!)
                    .cornerRadius(12)
                    .padding(20)
                    .accessibilityElement(children: .contain)
                    .accessibilityLabel("Веб-страница политики конфиденциальности")
            }
        }
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: 12)
        }
        .task {
            print("🚨 PrivacyPolicyScreen загружен!")
        }
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
        webView.accessibilityLabel = "Веб-страница политики конфиденциальности"
        webView.accessibilityHint = "Прокрутите для просмотра содержимого политики конфиденциальности"
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




import SwiftUI

/// Простая версия ShareSheet для iPhone (без поддержки iPad)
/// Используется для системного Share Sheet без специальной обработки iPad
struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}


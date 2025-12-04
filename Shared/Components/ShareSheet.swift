import SwiftUI
import UIKit

/**
 * 📤 ShareSheet Component
 * Компонент для поделиться контентом с поддержкой iPad (popover)
 * 
 * ИСПРАВЛЕНИЕ КРАША НА IPAD:
 * - На iPad UIActivityViewController должен отображаться как popover
 * - Нужно указать sourceView или barButtonItem
 */

struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]
    var sourceView: UIView? = nil
    var barButtonItem: UIBarButtonItem? = nil
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        let controller = UIActivityViewController(
            activityItems: activityItems,
            applicationActivities: nil
        )
        
        // Для iPad - настройка popover
        if UIDevice.current.userInterfaceIdiom == .pad {
            if let popover = controller.popoverPresentationController {
                // Приоритет: barButtonItem > sourceView > центр экрана
                if let barButtonItem = barButtonItem {
                    popover.barButtonItem = barButtonItem
                } else if let sourceView = sourceView {
                    popover.sourceView = sourceView
                    popover.sourceRect = sourceView.bounds
                } else {
                    // Fallback: центр экрана
                    if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                       let window = windowScene.windows.first {
                        popover.sourceView = window
                        popover.sourceRect = CGRect(
                            x: window.bounds.midX,
                            y: window.bounds.midY,
                            width: 0,
                            height: 0
                        )
                    }
                }
                popover.permittedArrowDirections = .any
            }
        }
        
        return controller
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

// MARK: - SwiftUI Wrapper для удобного использования

extension View {
    /// Показать ShareSheet с автоматической настройкой для iPad
    func shareSheet(
        isPresented: Binding<Bool>,
        activityItems: [Any],
        sourceView: UIView? = nil,
        barButtonItem: UIBarButtonItem? = nil
    ) -> some View {
        self.sheet(isPresented: isPresented) {
            ShareSheet(
                activityItems: activityItems,
                sourceView: sourceView,
                barButtonItem: barButtonItem
            )
        }
    }
}


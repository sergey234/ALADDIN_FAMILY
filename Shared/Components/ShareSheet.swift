import SwiftUI

/// Системный Share Sheet (`UIActivityViewController`).
/// Настраивает popover для iPad (без anchor шторка часто пустая / не открывается).
/// Для «шит поверх шита» (например, логи из настроек) экран-родитель должен открывать share через `fullScreenCover` или передавать файл `URL`.
struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]
    var onDismiss: (() -> Void)? = nil

    func makeCoordinator() -> Coordinator {
        Coordinator(onDismiss: onDismiss)
    }

    func makeUIViewController(context: Context) -> UIActivityViewController {
        let controller = UIActivityViewController(
            activityItems: activityItems,
            applicationActivities: nil
        )
        controller.completionWithItemsHandler = { _, _, _, _ in
            context.coordinator.onDismiss?()
        }
        Self.configurePopover(for: controller)
        return controller
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}

    /// iPad / multitasking: без `popoverPresentationController` UIActivityViewController не показывает интерфейс.
    private static func configurePopover(for controller: UIActivityViewController) {
        guard let popover = controller.popoverPresentationController else { return }
        popover.permittedArrowDirections = []
        let scenes = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
        let scene = scenes.first(where: { $0.activationState == .foregroundActive }) ?? scenes.first
        if let keyWin = scene?.keyWindow ?? scene?.windows.first(where: { $0.isKeyWindow }) ?? scene?.windows.first {
            let v = keyWin.rootViewController?.view ?? keyWin
            popover.sourceView = v
            let b = v.bounds
            popover.sourceRect = CGRect(x: b.midX, y: b.midY, width: 1, height: 1)
        } else if let windowScene = scenes.first, let w = windowScene.windows.first {
            popover.sourceView = w
            let b = w.bounds
            popover.sourceRect = CGRect(x: b.midX, y: b.midY, width: 1, height: 1)
        }
    }

    final class Coordinator {
        let onDismiss: (() -> Void)?
        init(onDismiss: (() -> Void)?) {
            self.onDismiss = onDismiss
        }
    }
}

private extension UIWindowScene {
    var keyWindow: UIWindow? {
        windows.first { $0.isKeyWindow }
    }
}


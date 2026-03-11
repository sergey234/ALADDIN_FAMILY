import SwiftUI

/// 🔔 Toast Notification View
/// Красивое уведомление типа toast/banner

struct Toast: View {
    let message: String
    let type: ToastType
    @Binding var isShowing: Bool
    
    enum ToastType {
        case success
        case warning
        case error
        case info
        
        var color: Color {
            switch self {
            case .success: return .green
            case .warning: return .orange
            case .error: return .red
            case .info: return .blue
            }
        }
        
        var icon: String {
            switch self {
            case .success: return "checkmark.circle.fill"
            case .warning: return "exclamationmark.triangle.fill"
            case .error: return "xmark.circle.fill"
            case .info: return "info.circle.fill"
            }
        }
    }
    
    var body: some View {
        if isShowing {
            HStack(spacing: Spacing.s) {
                Image(systemName: type.icon)
                    .font(.system(size: 20))
                    .foregroundColor(.white)
                
                Text(message)
                    .font(.body)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.leading)
                
                Spacer()
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(type.color)
                    .shadow(color: Color.black.opacity(0.3), radius: 10, x: 0, y: 5)
            )
            .padding(.horizontal, Spacing.m)
            .transition(.move(edge: .top).combined(with: .opacity))
            .zIndex(1000)
            .onAppear {
                // Автоматически скрываем через 3 секунды
                DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                    withAnimation {
                        isShowing = false
                    }
                }
            }
        }
    }
}

/// 🔔 Toast Manager
/// Менеджер для управления toast уведомлениями
/// ✅ BUILD 106: Добавлен @MainActor для гарантии main thread (требуется для @Published свойств)

@MainActor
class ToastManager: ObservableObject {
    static let shared = ToastManager()
    
    @Published var message: String = ""
    @Published var type: Toast.ToastType = .info
    @Published var isShowing: Bool = false
    
    private init() {}
    
    func show(message: String, type: Toast.ToastType = .info) {
        self.message = message
        self.type = type
        withAnimation {
            self.isShowing = true
        }
    }
    
    func hide() {
        withAnimation {
            self.isShowing = false
        }
    }
    
    // MARK: - Convenience Methods
    
    /// Показать успешное сообщение
    func showSuccess(_ message: String) {
        show(message: message, type: .success)
    }
    
    /// Показать сообщение об ошибке
    func showError(_ message: String) {
        show(message: message, type: .error)
    }
    
    /// Показать информационное сообщение
    func showInfo(_ message: String) {
        show(message: message, type: .info)
    }
    
    /// Показать предупреждение
    func showWarning(_ message: String) {
        show(message: message, type: .warning)
    }
}

/// 🔔 Toast View Modifier
/// SwiftUI modifier для добавления toast уведомлений

struct ToastModifier: ViewModifier {
    @ObservedObject private var toastManager = ToastManager.shared
    
    func body(content: Content) -> some View {
        ZStack(alignment: .top) {
            content
            
            if toastManager.isShowing {
                Toast(
                    message: toastManager.message,
                    type: toastManager.type,
                    isShowing: $toastManager.isShowing
                )
                .padding(.top, 60)
                .animation(.spring(response: 0.3, dampingFraction: 0.7), value: toastManager.isShowing)
            }
        }
    }
}

extension View {
    /// Добавляет поддержку toast уведомлений к view
    func withToast() -> some View {
        modifier(ToastModifier())
    }
}

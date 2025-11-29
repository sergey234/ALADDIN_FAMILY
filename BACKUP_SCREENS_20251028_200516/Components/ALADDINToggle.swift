import SwiftUI

/// 🔘 ALADDIN Custom Toggle
/// Кастомный переключатель в стиле приложения
struct ALADDINToggle: View {
    @Binding var isOn: Bool
    let title: String?
    let subtitle: String?
    
    // Простой инициализатор для новых файлов
    init(isOn: Binding<Bool>) {
        self._isOn = isOn
        self.title = nil
        self.subtitle = nil
    }
    
    // Полный инициализатор для совместимости
    init(_ title: String, subtitle: String? = nil, isOn: Binding<Bool>) {
        self.title = title
        self.subtitle = subtitle
        self._isOn = isOn
    }
    
    var body: some View {
        HStack {
            if let title = title {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.body)
                        .foregroundColor(.primary)
                    
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
            }
            
            Toggle("", isOn: $isOn)
                .toggleStyle(SwitchToggleStyle(tint: .blue))
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

import SwiftUI

/// 📊 Info Row Component
/// Универсальный компонент для отображения информации в строке
struct InfoRow: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(color == .primary ? .secondaryGold : color)
                .frame(width: 20)
            
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary.opacity(0.85))
                .lineLimit(1)
                .minimumScaleFactor(0.85)
            
            Spacer(minLength: 8)
            
            Text(value)
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.secondaryGold)
                .multilineTextAlignment(.trailing)
                .lineLimit(2)
                .minimumScaleFactor(0.8)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
}

#if DEBUG
struct InfoRow_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 16) {
            InfoRow(icon: "wifi", title: "Соединение", value: "Активно", color: .green)
            InfoRow(icon: "shield", title: "Защита", value: "Включена", color: .blue)
            InfoRow(icon: "clock", title: "Время", value: "2ч 15м", color: .orange)
        }
        .padding()
    }
}
#endif

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
                .foregroundColor(color)
                .frame(width: 20)
            
            Text(title)
                .font(.body)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(value)
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.primary)
        }
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

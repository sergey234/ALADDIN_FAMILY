import SwiftUI

/// 📈 Stat Item Component
/// Универсальный компонент для отображения статистики
struct StatItem: View {
    let icon: String
    let value: String
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            Text(icon)
                .font(.system(size: 24))
            
            Text(value)
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.blue)
            
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
    }
}

#if DEBUG
struct StatItem_Previews: PreviewProvider {
    static var previews: some View {
        HStack(spacing: 20) {
            StatItem(icon: "📊", value: "1.2K", label: "Заблокировано")
            StatItem(icon: "🛡️", value: "99.9%", label: "Защита")
            StatItem(icon: "⚡", value: "45ms", label: "Пинг")
        }
        .padding()
    }
}
#endif

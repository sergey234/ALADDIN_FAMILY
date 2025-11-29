import SwiftUI

/// 📊 Member Stats Modal
/// Статистика участника семьи
struct MemberStatsModalView: View {
    
    let memberName: String
    let memberRole: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        // Заголовок
                        VStack(spacing: Spacing.xs) {
                            Text("📊")
                                .font(.system(size: 64))
                            
                            Text("Статистика")
                                .font(.h1)
                                .foregroundColor(.textPrimary)
                            
                            Text(memberName)
                                .font(.h3)
                                .foregroundColor(.primaryBlue)
                            
                            Text(memberRole)
                                .font(.body)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(.top, Spacing.xxl)
                        
                        // Статистика в зависимости от роли
                        if memberRole == "Администратор" || memberRole == "Папа" {
                            administratorStats
                        } else if memberRole == "Родитель" || memberRole == "Мама" {
                            parentStats
                        } else if memberRole == "Подросток" {
                            teenagerStats
                        } else if memberRole == "Ребёнок" {
                            childStats
                        } else if memberRole == "Люди 60+" || memberRole == "Дедушка" {
                            elderlyStats
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                }
            }
            .navigationTitle("Статистика")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    // MARK: - Administrator Stats
    
    private var administratorStats: some View {
        VStack(spacing: Spacing.m) {
            // Общая защита семьи
            StatsSection(title: "🛡️ Общая защита семьи") {
                StatCard(icon: "🚫", label: "Всего угроз заблокировано", value: "47")
                StatCard(icon: "📱", label: "Активные устройства", value: "8")
                StatCard(icon: "⭐", label: "Рейтинг безопасности", value: "95%")
            }
            
            // Активность
            StatsSection(title: "📈 Активность") {
                StatCard(icon: "⏰", label: "Часы использования", value: "24/7")
                StatCard(icon: "🔐", label: "Защищённые действия", value: "1,245")
                StatCard(icon: "🌐", label: "Безопасные сайты", value: "342")
            }
        }
    }
    
    // MARK: - Parent Stats
    
    private var parentStats: some View {
        VStack(spacing: Spacing.m) {
            // Мои дети
            StatsSection(title: "👨‍👩‍👧‍👦 Мои дети") {
                StatCard(icon: "📊", label: "Активность детей", value: "Онлайн")
                StatCard(icon: "🚫", label: "Заблокированные угрозы", value: "23")
                StatCard(icon: "⏰", label: "Время использования", value: "2ч 30м")
            }
            
            // Моя активность
            StatsSection(title: "👤 Моя активность") {
                StatCard(icon: "🛡️", label: "Защищённые действия", value: "32")
                StatCard(icon: "🚫", label: "Заблокированные угрозы", value: "32")
                StatCard(icon: "⏰", label: "Часы использования", value: "1ч 15м")
            }
        }
    }
    
    // MARK: - Teenager Stats
    
    private var teenagerStats: some View {
        VStack(spacing: Spacing.m) {
            // Моя защита
            StatsSection(title: "🛡️ Моя защита") {
                StatCard(icon: "🚫", label: "Заблокированные угрозы", value: "23")
                StatCard(icon: "🔐", label: "Защищённые данные", value: "156")
                StatCard(icon: "📧", label: "Спам заблокирован", value: "89")
            }
            
            // Активность
            StatsSection(title: "📊 Активность") {
                StatCard(icon: "⏰", label: "Часы использования", value: "3ч 45м")
                StatCard(icon: "📱", label: "Популярные приложения", value: "12")
                StatCard(icon: "🌐", label: "Безопасные сайты", value: "234")
            }
        }
    }
    
    // MARK: - Child Stats
    
    private var childStats: some View {
        VStack(spacing: Spacing.m) {
            // Награды
            StatsSection(title: "🦄 Награды") {
                StatCard(icon: "🦄", label: "Количество единорогов", value: "24")
                StatCard(icon: "✅", label: "Задания выполнено", value: "15")
                StatCard(icon: "⭐", label: "Уровни пройдено", value: "5")
            }
            
            // Активность
            StatsSection(title: "🎮 Активность") {
                StatCard(icon: "🛡️", label: "Часы защиты", value: "2ч")
                StatCard(icon: "✅", label: "Правильных действий", value: "42")
                StatCard(icon: "🔓", label: "Открытых функций", value: "8")
            }
        }
    }
    
    // MARK: - Elderly Stats
    
    private var elderlyStats: some View {
        VStack(spacing: Spacing.m) {
            // Защита
            StatsSection(title: "🛡️ Защита") {
                StatCard(icon: "🚫", label: "Заблокированные мошенники", value: "8")
                StatCard(icon: "🛒", label: "Защищённые покупки", value: "12")
                StatCard(icon: "📞", label: "Безопасные звонки", value: "34")
            }
            
            // Активность
            StatsSection(title: "📊 Активность") {
                StatCard(icon: "🔧", label: "Использованные функции", value: "6")
                StatCard(icon: "📞", label: "Вызовы родных", value: "15")
                StatCard(icon: "🔗", label: "Открытые ссылки", value: "23")
            }
        }
    }
}

// MARK: - Helper Views

struct StatsSection<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(title)
                .font(.h3)
                .foregroundColor(.primaryBlue)
                .padding(.horizontal, Spacing.s)
            
            VStack(spacing: Spacing.s) {
                content
            }
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
        }
    }
}

struct StatCard: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(icon)
                .font(.system(size: 32))
            
            VStack(alignment: .leading, spacing: 2) {
                Text(label)
                    .font(.body)
                    .foregroundColor(.textSecondary)
                
                Text(value)
                    .font(.h2)
                    .foregroundColor(.primaryBlue)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.white.opacity(0.05))
        )
    }
}

// MARK: - Preview

#if DEBUG
struct MemberStatsModalView_Previews: PreviewProvider {
    static var previews: some View {
        MemberStatsModalView(memberName: "Сергей", memberRole: "Администратор")
    }
}
#endif

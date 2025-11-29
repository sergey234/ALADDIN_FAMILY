import SwiftUI

/// 🦄 Rewards Modal View
/// Модальное окно управления вознаграждениями ребёнка
/// Источник дизайна: /mobile/wireframes/14_parental_control_screen.html (модальное окно)
struct RewardsModalView: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) private var dismiss
    @Binding var unicornBalance: Int
    @Binding var weeklyRewarded: Int
    @Binding var weeklyPunished: Int
    
    @State private var showRewardInput: Bool = false
    @State private var showPunishInput: Bool = false
    @State private var rewardAmount: String = "10"
    @State private var punishAmount: String = "10"
    @State private var rewardReason: String = ""
    @State private var punishReason: String = ""
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel("Фон модального окна вознаграждений")
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Баланс единорогов
                        balanceCard
                        
                        // Быстрые действия
                        quickActions
                        
                        // Как заработать
                        earningWaysSection
                        
                        // За что можно наказать
                        punishmentReasonsSection
                        
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое модального окна вознаграждений")
        }
        .navigationBarTitleDisplayMode(.inline)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 RewardsModalView загружен!")
        }
        .toolbar {
                ToolbarItem(placement: .principal) {
                    HStack(spacing: Spacing.xs) {
                        Text("🦄")
                            .font(.system(size: 20))
                            .accessibilityLabel("Единорог")
                        Text("Вознаграждение ребёнка")
                            .font(.h3)
                            .foregroundColor(Color(hex: "C084FC"))
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Вознаграждение ребёнка")
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        dismiss()
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.textSecondary)
                    }
                    .accessibilityLabel("Закрыть")
                    .accessibilityHint("Нажмите для закрытия модального окна")
                }
            }
        }
    }
    
    // MARK: - Balance Card
    
    private var balanceCard: some View {
        VStack(spacing: Spacing.m) {
            // Иконка
            Text("🦄")
                .font(.system(size: 56))
                .accessibilityLabel("Единорог")
            
            // Баланс
            Text("\(unicornBalance)")
                .font(.system(size: 36, weight: .bold))
                .foregroundColor(Color(hex: "C084FC"))
                .accessibilityLabel("Баланс: \(unicornBalance) единорогов")
            
            Text("Единорогов на счету")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .accessibilityLabel("Единорогов на счету")
            
            // Статистика за неделю
            Divider()
                .background(Color.textSecondary.opacity(0.3))
                .padding(.vertical, Spacing.s)
                .accessibilityElement(children: .ignore)
            
            HStack(spacing: Spacing.xxl) {
                VStack(spacing: Spacing.xs) {
                    Text("+\(weeklyRewarded)")
                        .font(.h2)
                        .foregroundColor(.successGreen)
                    Text("Вознаграждено\nза неделю")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Вознаграждено за неделю: \(weeklyRewarded) единорогов")
                
                VStack(spacing: Spacing.xs) {
                    Text("-\(weeklyPunished)")
                        .font(.h2)
                        .foregroundColor(.dangerRed)
                    Text("Наказано\nза неделю")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Наказано за неделю: \(weeklyPunished) единорогов")
            }
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            Color(hex: "A855F7").opacity(0.12),
                            Color(hex: "EC4899").opacity(0.18)
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color(hex: "A855F7").opacity(0.4), lineWidth: 2)
                )
        )
        .cardShadow()
        .appGlassmorphism()
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Карточка баланса единорогов")
    }
    
    // MARK: - Quick Actions
    
    private var quickActions: some View {
        HStack(spacing: Spacing.m) {
            // Кнопка "Вознаградить"
            Button(action: {
                rewardChild()
            }) {
                VStack(spacing: Spacing.xs) {
                    Text("✅")
                        .font(.system(size: 24))
                        .accessibilityLabel("Галочка")
                    Text("Вознаградить")
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.successGreen.opacity(0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.successGreen, lineWidth: 2)
                        )
                )
            }
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel("Вознаградить ребёнка")
            .accessibilityHint("Нажмите для вознаграждения ребёнка единорогами")
            
            // Кнопка "Наказать"
            Button(action: {
                punishChild()
            }) {
                VStack(spacing: Spacing.xs) {
                    Text("❌")
                        .font(.system(size: 24))
                        .accessibilityLabel("Крестик")
                    Text("Наказать")
                        .font(.caption)
                        .foregroundColor(.dangerRed)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.dangerRed.opacity(0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.dangerRed, lineWidth: 2)
                        )
                )
            }
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel("Наказать ребёнка")
            .accessibilityHint("Нажмите для наказания ребёнка единорогами")
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Earning Ways Section
    
    private var earningWaysSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("✅")
                    .font(.system(size: 18))
                    .accessibilityLabel("Галочка")
                Text("Как заработать:")
                    .font(.h3)
                    .foregroundColor(.successGreen)
            }
            .padding(.horizontal, Spacing.screenPadding)
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Как заработать единорогов")
            .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                earningWayRow(icon: "📚", title: "Домашнее задание", subtitle: "+10 единорогов за задание", amount: "+10 🦄")
                earningWayRow(icon: "🧹", title: "Домашние обязанности", subtitle: "+5 единорогов за дело", amount: "+5 🦄")
                earningWayRow(icon: "😊", title: "Хорошее поведение", subtitle: "+15 единорогов за день", amount: "+15 🦄")
                earningWayRow(icon: "📖", title: "Чтение книг", subtitle: "+20 единорогов за книгу", amount: "+20 🦄")
                earningWayRow(icon: "🏆", title: "Достижения в учёбе", subtitle: "+50 единорогов за 5", amount: "+50 🦄")
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func earningWayRow(icon: String, title: String, subtitle: String, amount: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
                .accessibilityLabel("Иконка: \(icon)")
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(subtitle)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(title): \(subtitle)")
            
            Spacer()
            
            Text(amount)
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(.successGreen)
                .accessibilityLabel("Награда: \(amount)")
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle), награда \(amount)")
    }
    
    // MARK: - Punishment Reasons Section
    
    private var punishmentReasonsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("❌")
                    .font(.system(size: 18))
                    .accessibilityLabel("Крестик")
                Text("За что можно наказать:")
                    .font(.h3)
                    .foregroundColor(.dangerRed)
            }
            .padding(.horizontal, Spacing.screenPadding)
            .accessibilityElement(children: .combine)
            .accessibilityLabel("За что можно наказать единорогами")
            .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                punishmentReasonRow(icon: "📚", title: "Не сделал ДЗ", subtitle: "Забыл или отказался делать", amount: "-10 🦄")
                punishmentReasonRow(icon: "😡", title: "Плохое поведение", subtitle: "Грубость, ссоры, непослушание", amount: "-15 🦄")
                punishmentReasonRow(icon: "⏰", title: "Нарушение лимитов", subtitle: "Превышение экранного времени", amount: "-5 🦄")
                punishmentReasonRow(icon: "🚫", title: "Обход блокировок", subtitle: "Попытка обойти контроль", amount: "-20 🦄")
                punishmentReasonRow(icon: "😤", title: "Своя причина", subtitle: "Родители указывают сами", amount: "-1 до -50 🦄")
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.dangerRed.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.dangerRed.opacity(0.3), lineWidth: 1)
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func punishmentReasonRow(icon: String, title: String, subtitle: String, amount: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
                .accessibilityLabel("Иконка: \(icon)")
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(subtitle)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(title): \(subtitle)")
            
            Spacer()
            
            Text(amount)
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(.dangerRed)
                .accessibilityLabel("Штраф: \(amount)")
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle), штраф \(amount)")
    }
    
    // MARK: - Actions
    
    private func rewardChild() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        unicornBalance += 10
        weeklyRewarded += 10
        
        print("✅ Вознаградили ребёнка: +10 🦄")
    }
    
    private func punishChild() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        unicornBalance -= 10
        weeklyPunished += 10
        
        print("❌ Наказали ребёнка: -10 🦄")
    }
}

// MARK: - Preview

#if DEBUG
struct RewardsModalView_Previews: PreviewProvider {
    static var previews: some View {
        RewardsModalView(
            unicornBalance: .constant(245),
            weeklyRewarded: .constant(128),
            weeklyPunished: .constant(45)
        )
    }
}
#endif




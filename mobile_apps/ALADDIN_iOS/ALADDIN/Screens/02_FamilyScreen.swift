import SwiftUI

/// 👨‍👩‍👧‍👦 Family Screen
/// Экран управления семьёй - список всех членов семьи
/// Источник дизайна: /mobile/wireframes/03_family_screen.html
struct FamilyScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var showRewardsQuickModal: Bool = false
    @State private var unicornBalance: Int = 245
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "СЕМЬЯ",
                    subtitle: "4 члена под защитой",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    },
                    rightButtons: [
                        .init(icon: "plus") {
                            print("Добавить члена семьи")
                        }
                    ]
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.m) {
                        // Обзор семьи
                        familyOverview
                        
                        // Заголовок секции
                        HStack {
                            Text("ЧЛЕНЫ СЕМЬИ")
                                .font(.h3)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        // Список членов семьи
                        familyMembersList
                        
                        // НОВОЕ: Карточка вознаграждений 🦄
                        rewardsQuickCard
                        
                        // Кнопка добавить
                        addFamilyMemberButton
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Family Overview
    
    private var familyOverview: some View {
        VStack(spacing: Spacing.m) {
            // Иконка семьи
            Text("👨‍👩‍👧‍👦")
                .font(.system(size: 64))
            
            // Текст
            VStack(spacing: Spacing.xs) {
                Text("Ваша семья")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                
                Text("4 члена • Все под защитой")
                    .font(.body)
                    .foregroundColor(.textSecondary)
            }
            
            // Статистика
            HStack(spacing: Spacing.xl) {
                statItem(icon: "🛡️", value: "47", label: "Угроз блокировано")
                
                Rectangle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 1, height: 40)
                
                statItem(icon: "⏰", value: "24/7", label: "Защита активна")
                
                Rectangle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 1, height: 40)
                
                statItem(icon: "📱", value: "8", label: "Устройств")
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func statItem(icon: String, value: String, label: String) -> some View {
        VStack(spacing: Spacing.xxs) {
            Text(icon)
                .font(.system(size: 24))
            
            Text(value)
                .font(.h3)
                .foregroundColor(.primaryBlue)
            
            Text(label)
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Family Members List
    
    private var familyMembersList: some View {
        VStack(spacing: Spacing.m) {
            // Родитель 1
            FamilyMemberCard(
                name: "Сергей",
                role: .parent,
                avatar: "👨",
                status: .protected,
                threatsBlocked: 47,
                lastActive: "Сейчас"
            ) {
                print("Открыть профиль Сергея")
            }
            
            // Родитель 2
            FamilyMemberCard(
                name: "Мария",
                role: .parent,
                avatar: "👩",
                status: .protected,
                threatsBlocked: 32,
                lastActive: "5 мин назад"
            ) {
                print("Открыть профиль Марии")
            }
            
            // Ребёнок
            FamilyMemberCard(
                name: "Маша",
                role: .child,
                avatar: "👧",
                status: .warning,
                threatsBlocked: 23,
                lastActive: "10 мин назад"
            ) {
                print("Открыть профиль Маши")
            }
            
            // Пожилой родственник
            FamilyMemberCard(
                name: "Бабушка",
                role: .elderly,
                avatar: "👵",
                status: .offline,
                threatsBlocked: 12,
                lastActive: "2 часа назад"
            ) {
                print("Открыть профиль Бабушки")
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Rewards Quick Card (НОВОЕ! 🦄)
    
    private var rewardsQuickCard: some View {
        Button(action: {
            showRewardsQuickModal = true
        }) {
            VStack(spacing: Spacing.m) {
                // Иконка единорога с анимацией
                Text("🦄")
                    .font(.system(size: 36))
                
                // Заголовок
                Text("Вознаграждение ребёнка")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(Color(hex: "C084FC"))
                
                // Статистика
                HStack(spacing: Spacing.l) {
                    VStack(spacing: Spacing.xxs) {
                        Text("\(unicornBalance)")
                            .font(.h2)
                            .foregroundColor(Color(hex: "C084FC"))
                        Text("Баланс 🦄")
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Rectangle()
                        .fill(Color.textSecondary.opacity(0.3))
                        .frame(width: 1, height: 30)
                    
                    VStack(spacing: Spacing.xxs) {
                        Text("+128")
                            .font(.h2)
                            .foregroundColor(.successGreen)
                        Text("За неделю")
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.cardPadding)
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
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .sheet(isPresented: $showRewardsQuickModal) {
            RewardsQuickModal(unicornBalance: $unicornBalance)
        }
    }
    
    // MARK: - Add Family Member Button
    
    private var addFamilyMemberButton: some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            print("Добавить члена семьи")
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                Image(systemName: "plus.circle.fill")
                    .font(.system(size: 32))
                    .foregroundColor(.primaryBlue)
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text("Добавить члена семьи")
                        .font(.body)
                        .foregroundColor(.textPrimary)
                    
                    Text("Пригласите близких под защиту ALADDIN")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                // Стрелка
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.cardPadding)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(
                        LinearGradient(
                            colors: [Color.primaryBlue.opacity(0.5), Color.secondaryBlue.opacity(0.3)],
                            startPoint: .leading,
                            endPoint: .trailing
                        ),
                        lineWidth: 2
                    )
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.top, Spacing.s)
    }
}

// MARK: - Preview

#Preview {
    FamilyScreen()
}


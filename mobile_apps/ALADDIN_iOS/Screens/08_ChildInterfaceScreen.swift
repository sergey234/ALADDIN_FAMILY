import SwiftUI

/// 👶 Child Interface Screen
/// Детский интерфейс - упрощённый экран для детей
/// Источник дизайна: /mobile/wireframes/06_child_interface.html
struct ChildInterfaceScreen: View {
    
    // MARK: - State
    
    @State private var selectedTab: Int = 0
    @State private var selectedAge: AgeGroup = .school
    @State private var showChildRewards: Bool = false
    
    enum AgeGroup {
        case kids, school, teen
        
        var title: String {
            switch self {
            case .kids: return "👶 1-6 лет"
            case .school: return "🎒 7-12 лет"
            case .teen: return "🎓 13-17 лет"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (более яркий для детей)
            LinearGradient(
                colors: [
                    Color(hex: "#1e3a8a"),
                    Color(hex: "#3b82f6"),
                    Color(hex: "#60a5fa")
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Простая навигация для детей
                childHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.xl) {
                        // Приветствие
                        greetingCard
                        
                        // НОВОЕ: Возрастные табы
                        ageTabs
                        
                        // Большие кнопки для детей
                        bigButtonsGrid
                        
                        // Время экрана
                        screenTimeCard
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.l)
                }
            }
        }
    }
    
    // MARK: - Child Header
    
    private var childHeader: some View {
        HStack(spacing: Spacing.m) {
            // Аватар (НОВОЕ: клик открывает награды)
            Button(action: {
                showChildRewards = true
            }) {
                Text("👧")
                    .font(.system(size: 40))
                    .frame(width: 60, height: 60)
                    .background(
                        Circle()
                            .fill(Color.white.opacity(0.2))
                    )
            }
            .buttonStyle(PlainButtonStyle())
            .sheet(isPresented: $showChildRewards) {
                ChildRewardsScreen()
            }
            
            // Приветствие
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text("Привет, Маша!")
                    .font(.h2)
                    .foregroundColor(.white)
                
                Text("Ты под защитой 🛡️")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))
            }
            
            Spacer()
        }
        .padding(Spacing.cardPadding)
        .background(
            Color.white.opacity(0.1)
        )
    }
    
    // MARK: - Greeting Card
    
    private var greetingCard: some View {
        VStack(spacing: Spacing.m) {
            Text("🎮")
                .font(.system(size: 64))
            
            Text("Что будем делать?")
                .font(.h1)
                .foregroundColor(.white)
            
            Text("Выбери занятие")
                .font(.body)
                .foregroundColor(.white.opacity(0.8))
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.xlarge)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Age Tabs (НОВОЕ!)
    
    private var ageTabs: some View {
        VStack(spacing: Spacing.m) {
            Text("🎯 Выбери свой возраст")
                .font(.h3)
                .foregroundColor(.white)
            
            HStack(spacing: Spacing.s) {
                ForEach([AgeGroup.kids, .school, .teen], id: \.self) { age in
                    Button(action: {
                        selectedAge = age
                    }) {
                        Text(age.title)
                            .font(.caption)
                            .fontWeight(selectedAge == age ? .bold : .regular)
                            .foregroundColor(selectedAge == age ? .white : .white.opacity(0.7))
                            .padding(.horizontal, Spacing.m)
                            .padding(.vertical, Spacing.s)
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(selectedAge == age ? Color.primaryBlue : Color.white.opacity(0.1))
                            )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Big Buttons Grid
    
    private var bigButtonsGrid: some View {
        VStack(spacing: Spacing.m) {
            HStack(spacing: Spacing.m) {
                bigChildButton(icon: "🎮", title: "ИГРЫ", color: Color(hex: "#10B981"))
                bigChildButton(icon: "📚", title: "УЧЁБА", color: Color(hex: "#3B82F6"))
            }
            
            HStack(spacing: Spacing.m) {
                bigChildButton(icon: "🎨", title: "ТВОРЧЕСТВО", color: Color(hex: "#F59E0B"))
                bigChildButton(icon: "📺", title: "ВИДЕО", color: Color(hex: "#EF4444"))
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func bigChildButton(icon: String, title: String, color: Color) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            print(title)
        }) {
            VStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 56))
                
                Text(title)
                    .font(.h3)
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 140)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(color.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .stroke(color, lineWidth: 3)
                    )
            )
            .shadow(color: color.opacity(0.3), radius: 12, x: 0, y: 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Screen Time Card
    
    private var screenTimeCard: some View {
        VStack(spacing: Spacing.m) {
            Text("⏰")
                .font(.system(size: 48))
            
            Text("Осталось времени")
                .font(.h3)
                .foregroundColor(.white)
            
            Text("45 минут")
                .font(.system(size: 40, weight: .bold))
                .foregroundColor(.successGreen)
            
            // Прогресс бар
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.white.opacity(0.2))
                        .frame(height: 12)
                    
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.successGreen)
                        .frame(width: geometry.size.width * 0.25, height: 12)
                }
            }
            .frame(height: 12)
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Preview

#Preview {
    ChildInterfaceScreen()
}


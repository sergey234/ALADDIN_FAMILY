import SwiftUI

/// 👶 Child Interface Screen
/// Детский интерфейс - упрощённый экран для детей
/// Источник дизайна: /mobile/wireframes/06_child_interface.html
struct ChildInterfaceScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var selectedTab: Int = 0
    @State private var selectedAge: AgeGroup = .school
    @State private var showChildRewards: Bool = false
    
    enum AgeGroup {
        case kids, school, teen, youngAdult
        
        var title: String {
            switch self {
            case .kids: return "👶 1-6 лет"
            case .school: return "🎒 7-12 лет"
            case .teen: return "🎓 13-17 лет"
            case .youngAdult: return "🎓 18-22 лет"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (более яркий для детей)
            LinearGradient(
                colors: [
                    Color.blue,
                    Color.blue.opacity(0.8),
                    Color.blue.opacity(0.6)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Яркий фон детского интерфейса")
            
            VStack(spacing: 0) {
                // Простая навигация для детей
                childHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 16) {
                        // Приветствие
                        greetingCard
                        
                        // НОВОЕ: Возрастные табы
                        ageTabs
                        
                        // Большие кнопки для детей
                        bigButtonsGrid
                        
                        // Время экрана
                        screenTimeCard
                        
                        // Адаптивный отступ (Apple HIG)
                        Spacer(minLength: 0)
                            .frame(maxHeight: 32)
                    }
                    .padding(.top, 16)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое детского интерфейса")
            }
        }
    }
    
    // MARK: - Child Header
    
    private var childHeader: some View {
        HStack(spacing: 12) {
            // Кнопка назад
            Button(action: {
                print("🔍 DEBUG: Кнопка 'Назад' нажата в ChildInterfaceScreen")
                navigationManager.goBack()
                print("🔍 DEBUG: NavigationManager.goBack() вызван")
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.blue.opacity(0.2))
                    )
            }
            .accessibilityLabel("Назад")
            
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
                Text("Детские награды")
                    .font(.title)
                    .padding()
            }
            
            // Приветствие
            VStack(alignment: .leading, spacing: 2) {
                Text("Привет, Маша!")
                    .font(.title)
                    .foregroundColor(.white)
                
                Text("Ты под защитой 🛡️")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))
            }
            
            Spacer()
        }
        .padding(16)
        .background(
            Color.white.opacity(0.1)
        )
    }
    
    // MARK: - Greeting Card
    
    private var greetingCard: some View {
        VStack(spacing: 12) {
            Text("🎮")
                .font(.system(size: 64))
            
            Text("Что будем делать?")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Выбери занятие")
                .font(.body)
                .foregroundColor(.white.opacity(0.8))
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, 20)
    }
    
    // MARK: - Age Tabs (НОВОЕ!)
    
    private var ageTabs: some View {
        VStack(spacing: 12) {
            Text("🎯 Выбери свой возраст")
                .font(.title2)
                .foregroundColor(.white)
            
            HStack(spacing: 8) {
                ForEach([AgeGroup.kids, .school, .teen, .youngAdult], id: \.self) { age in
                    Button(action: {
                        selectedAge = age
                    }) {
                        Text(age.title)
                            .font(.caption)
                            .fontWeight(selectedAge == age ? .bold : .regular)
                            .foregroundColor(selectedAge == age ? .white : .white.opacity(0.7))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(selectedAge == age ? Color.blue : Color.white.opacity(0.1))
                            )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
        }
        .padding(.horizontal, 20)
    }
    
    // MARK: - Big Buttons Grid
    
    private var bigButtonsGrid: some View {
        VStack(spacing: 12) {
            HStack(spacing: 12) {
                bigChildButton(icon: "🎮", title: "ИГРЫ", color: Color.green)
                bigChildButton(icon: "📚", title: "УЧЁБА", color: Color.blue)
            }
            
            HStack(spacing: 12) {
                bigChildButton(icon: "🎨", title: "ТВОРЧЕСТВО", color: Color.orange)
                bigChildButton(icon: "📺", title: "ВИДЕО", color: Color.red)
            }
        }
        .padding(.horizontal, 20)
    }
    
    private func bigChildButton(icon: String, title: String, color: Color) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            print(title)
        }) {
            VStack(spacing: 12) {
                Text(icon)
                    .font(.system(size: 56))
                
                Text(title)
                    .font(.title2)
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 140)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(color.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color, lineWidth: 3)
                    )
            )
            .shadow(color: color.opacity(0.3), radius: 12, x: 0, y: 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Screen Time Card
    
    private var screenTimeCard: some View {
        VStack(spacing: 12) {
            Text("⏰")
                .font(.system(size: 48))
            
            Text("Осталось времени")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("45 минут")
                .font(.system(size: 40, weight: .bold))
                .foregroundColor(.green)
            
            // Прогресс бар
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.white.opacity(0.2))
                        .frame(height: 12)
                    
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.green)
                        .frame(width: geometry.size.width * 0.25, height: 12)
                }
            }
            .frame(height: 12)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, 20)
    }
}

// MARK: - Preview

#if DEBUG
struct ChildInterfaceScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildInterfaceScreen()
    }
}
#endif


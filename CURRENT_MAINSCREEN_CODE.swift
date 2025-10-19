// ТЕКУЩИЙ КОД MainScreen.swift (НЕ РАБОТАЕТ)
// Проблема: layout не исправлен - элементы в неправильных позициях

import SwiftUI

struct MainScreen: View {
    @State private var selectedTab: Int = 0
    @State private var isVPNEnabled: Bool = true
    @State private var isFamilyProtectionEnabled: Bool = true
    @State private var aiQuestion: String = ""
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Фон (точно как в HTML)
                LinearGradient(
                    colors: [
                        Color(red: 0.04, green: 0.07, blue: 0.16), // #0a1128
                        Color(red: 0.12, green: 0.23, blue: 0.37), // #1e3a5f
                        Color(red: 0.18, green: 0.31, blue: 0.56)  // #2e5090
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Верхняя часть с логотипом и профилем
                    topSection
                    
                    // Основной контент
                    mainContent
                    
                    // Spacer для прижатия навигации к низу
                    Spacer()
                    
                    // Нижняя навигация в самом низу экрана
                    bottomNavigation
                        .padding(.bottom, geometry.safeAreaInsets.bottom)
                }
            }
        }
        .onAppear {
            print("🚨 MainScreen загружен! Layout должен работать!")
        }
    }
    
    // MARK: - Top Section (Status Bar + Header)
    
    private var topSection: some View {
        VStack(spacing: 0) {
            // Статус бар
            HStack {
                // Левая часть
                HStack(spacing: 5) {
                    Text("9:41")
                        .font(.system(size: 12))
                        .foregroundColor(.white)
                }
                
                Spacer()
                
                // Правая часть
                HStack(spacing: 5) {
                    Text("📶")
                        .font(.system(size: 12))
                    Text("🔋")
                        .font(.system(size: 12))
                }
            }
            .padding(.horizontal, 20)
            .padding(.top, 8)
            .padding(.bottom, 8)
            
            // Заголовок с логотипом и профилем
            HStack {
                // Логотип и контент (точно как в HTML)
                HStack(spacing: 10) {
                    // Логотип изображение
                    Circle()
                        .fill(Color.orange)
                        .frame(width: 36, height: 36)
                        .overlay(
                            Text("👁️")
                                .font(.system(size: 20))
                        )
                        .shadow(color: Color.orange.opacity(0.4), radius: 15)
                        .overlay(
                            Circle()
                                .stroke(Color.orange.opacity(0.3), lineWidth: 2)
                        )
                    
                    // Заголовок и подзаголовок
                    VStack(alignment: .leading, spacing: 2) {
                        Text("ALADDIN")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.orange)
                            .shadow(color: Color.orange.opacity(0.3), radius: 10)
                        
                        Text("AI Защита семьи")
                            .font(.system(size: 8))
                            .foregroundColor(.white.opacity(0.7))
                            .lineLimit(2)
                    }
                }
                
                Spacer()
                
                // Кнопка профиля (точно как в HTML)
                Button(action: {
                    print("Открыть профиль")
                }) {
                    Circle()
                        .fill(Color.orange)
                        .frame(width: 44, height: 44)
                        .overlay(
                            Text("👤")
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(.black)
                        )
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 20)
        }
    }
    
    // MARK: - Main Content
    
    private var mainContent: some View {
        VStack(spacing: 20) {
            // Карточки функций (точно как в HTML)
            functionsGrid
            
            // FAMILY Статус (точно как в HTML)
            familyStatusCard
            
            // AI Помощник (точно как в HTML)
            aiAssistantCard
        }
        .padding(.horizontal, 20)
    }
    
    // MARK: - Functions Grid
    
    private var functionsGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible(), spacing: 15),
            GridItem(.flexible(), spacing: 15)
        ], spacing: 15) {
            // VPN карточка (точно как в HTML)
            Button(action: {
                print("Открыть VPN")
            }) {
                VStack(spacing: 6) {
                    HStack(spacing: 8) {
                        Text("🛡️")
                            .font(.system(size: 20))
                        Text(isVPNEnabled ? "🟢" : "🔴")
                            .font(.system(size: 24))
                            .foregroundColor(isVPNEnabled ? .green : .red)
                    }
                    Text("ALADDIN VPN")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.white)
                    Text("VPN • Защита")
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.8))
                }
                .frame(maxWidth: .infinity)
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.white.opacity(0.1))
                        .overlay(
                            RoundedRectangle(cornerRadius: 10)
                                .stroke(isVPNEnabled ? Color.green : Color.white.opacity(0.2), lineWidth: 2)
                        )
                )
            }
            .buttonStyle(PlainButtonStyle())
            
            // Остальные карточки...
        }
    }
    
    // MARK: - Family Status Card
    
    private var familyStatusCard: some View {
        VStack(spacing: 8) {
            // Заголовок (точно как в HTML)
            HStack {
                Text("👨‍👩‍👧‍👦")
                    .font(.system(size: 18))
                Text("ALADDIN FAMILY")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.black)
                Spacer()
                
                // Toggle переключатель (точно как в HTML)
                Button(action: {
                    withAnimation(.spring()) {
                        isFamilyProtectionEnabled.toggle()
                    }
                }) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 18)
                            .fill(isFamilyProtectionEnabled ? .black : .black.opacity(0.3))
                            .frame(width: 35, height: 18)
                        
                        Circle()
                            .fill(isFamilyProtectionEnabled ? .orange : .black)
                            .frame(width: 14, height: 14)
                            .offset(x: isFamilyProtectionEnabled ? 8.5 : -8.5)
                    }
                }
            }
            
            // Информация о семье (точно как в HTML)
            VStack(spacing: 3) {
                Text("👤 6 членов семьи • 4 устройства")
                    .font(.system(size: 9))
                    .foregroundColor(.black)
                
                Text("🛡️ Защита 98% • Все возрасты")
                    .font(.system(size: 9))
                    .foregroundColor(.black)
                
                HStack {
                    Text("🟢")
                        .font(.system(size: 9))
                    Text("VPN 100 Мбит/с • Защищено от 2,847 угроз")
                        .font(.system(size: 9))
                        .foregroundColor(.black)
                }
            }
            
            // Кнопки действий (точно как в HTML)
            HStack(spacing: 8) {
                Button(action: {
                    print("Управление семьей")
                }) {
                    Text("Управление семьей")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.orange)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(.black)
                        )
                }
                
                Button(action: {
                    print("Добавить члена семьи")
                }) {
                    Text("Добавить члена семьи")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(.black.opacity(0.2))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(.black, lineWidth: 2)
                                )
                        )
                }
            }
        }
        .padding(12)
        .background(
            LinearGradient(
                colors: [.orange, Color(red: 0.85, green: 0.47, blue: 0.02)], // #D97706
                startPoint: .leading,
                endPoint: .trailing
            )
        )
        .cornerRadius(10)
        .shadow(color: .orange.opacity(0.3), radius: 20, x: 0, y: 8)
    }
    
    // MARK: - AI Assistant Card
    
    private var aiAssistantCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Заголовок (точно как в HTML)
            Text("🤖 AI Помощник ALADDIN")
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.orange)
            
            // Сообщение (точно как в HTML)
            Text("\"Привет! Я помогу настроить защиту для вашей семьи. Чем могу помочь?\"")
                .font(.system(size: 10))
                .foregroundColor(.white.opacity(0.9))
            
            // Поле ввода (точно как в HTML)
            TextField("Задайте вопрос...", text: $aiQuestion)
                .font(.system(size: 11))
                .foregroundColor(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.white.opacity(0.1))
                        .overlay(
                            RoundedRectangle(cornerRadius: 16)
                                .stroke(Color.white.opacity(0.3), lineWidth: 1)
                        )
                )
                .onTapGesture {
                    if !aiQuestion.isEmpty {
                        print("AI вопрос: \(aiQuestion)")
                        aiQuestion = ""
                    }
                }
        }
        .padding(10)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(.orange.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(.orange, lineWidth: 2)
                )
        )
    }
    
    // MARK: - Bottom Navigation
    
    private var bottomNavigation: some View {
        HStack(spacing: 0) {
            navButton(icon: "house.fill", label: "Главная", index: 0)
            navButton(icon: "shield.fill", label: "Защита", index: 1)
            navButton(icon: "bell.fill", label: "Уведомления", index: 2)
            navButton(icon: "person.fill", label: "Профиль", index: 3)
            navButton(icon: "iphone", label: "Устройства", index: 4)
        }
        .padding(.vertical, 20)
        .padding(.horizontal, 16)
        .background(
            RoundedRectangle(cornerRadius: 30)
                .fill(Color.black.opacity(0.9))
                .overlay(
                    RoundedRectangle(cornerRadius: 30)
                        .stroke(Color.white.opacity(0.4), lineWidth: 2)
                )
        )
        .padding(.horizontal, 20)
    }
    
    private func navButton(icon: String, label: String, index: Int) -> some View {
        Button(action: {
            withAnimation(.easeInOut(duration: 0.2)) {
                selectedTab = index
            }
            print("🚨 КНОПКА НАЖАТА: \(label) (индекс: \(index))")
        }) {
            VStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 18, weight: .medium))
                    .foregroundColor(selectedTab == index ? .white : .white.opacity(0.7))
                    .scaleEffect(selectedTab == index ? 1.2 : 1.0)
                
                Text(label)
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(selectedTab == index ? .white : .white.opacity(0.7))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 15)
                    .fill(selectedTab == index ? Color.white.opacity(0.3) : Color.clear)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .contentShape(Rectangle()) // Увеличиваем область нажатия
    }
}

// MARK: - Preview

struct MainScreen_Previews: PreviewProvider {
    static var previews: some View {
        MainScreen()
    }
}


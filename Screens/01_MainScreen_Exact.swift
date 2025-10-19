import SwiftUI

struct MainScreenExact: View {
    @State private var isFamilyProtectionEnabled: Bool = true
    @State private var aiQuestion: String = ""
    @State private var vpnConnected: Bool = false
    
    var body: some View {
        ZStack {
            // Фон - точно как в HTML
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
                // Статус бар
                HStack {
                    Text("9:41")
                        .font(.system(size: 12))
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    HStack(spacing: 5) {
                        Text("📶")
                            .font(.system(size: 12))
                        Text("🔋")
                            .font(.system(size: 12))
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
                .padding(.bottom, 20)
                
                // Заголовок - логотип слева, профиль справа
                HStack {
                    // Логотип и контент - ЛЕВЫЙ УГОЛ
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
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text("ALADDIN")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.orange)
                                .shadow(color: Color.orange.opacity(0.3), radius: 10)
                            
                            Text("AI Защита семьи")
                                .font(.system(size: 8))
                                .foregroundColor(.white.opacity(0.7))
                        }
                    }
                    
                    Spacer()
                    
                    // Кнопка профиля - ПРАВЫЙ УГОЛ
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
                
                // Основной контент
                ScrollView {
                    VStack(spacing: 20) {
                        // Карточки функций - сетка 2x2
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 15) {
                            // VPN карточка
                            Button(action: {
                                print("Открыть VPN")
                            }) {
                                VStack(spacing: 8) {
                                    HStack(spacing: 8) {
                                        Text("🛡️")
                                            .font(.system(size: 20))
                                        Text(vpnConnected ? "🟢" : "🔴")
                                            .font(.system(size: 24))
                                    }
                                    
                                    Text("ALADDIN VPN")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text("VPN • Защита")
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            
                            // Тарифы карточка
                            Button(action: {
                                print("Открыть тарифы")
                            }) {
                                VStack(spacing: 8) {
                                    Text("💎")
                                        .font(.system(size: 20))
                                    
                                    Text("Тарифы")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text("Выбор плана")
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            
                            // Аналитика карточка
                            Button(action: {
                                print("Открыть аналитику")
                            }) {
                                VStack(spacing: 8) {
                                    Text("📊")
                                        .font(.system(size: 20))
                                    
                                    Text("Аналитика")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text("Статистика")
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            
                            // Настройки карточка
                            Button(action: {
                                print("Открыть настройки")
                            }) {
                                VStack(spacing: 8) {
                                    Text("⚙️")
                                        .font(.system(size: 20))
                                    
                                    Text("Настройки")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text("Параметры")
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                        }
                        .padding(.horizontal, 20)
                        
                        // FAMILY статус - большая карточка
                        VStack(spacing: 12) {
                            // Заголовок с переключателем
                            HStack {
                                Text("👨‍👩‍👧‍👦")
                                    .font(.system(size: 18))
                                
                                Text("ALADDIN FAMILY")
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                // Переключатель
                                Button(action: {
                                    isFamilyProtectionEnabled.toggle()
                                }) {
                                    ZStack {
                                        RoundedRectangle(cornerRadius: 18)
                                            .fill(isFamilyProtectionEnabled ? Color.black : Color.black.opacity(0.3))
                                            .frame(width: 35, height: 18)
                                        
                                        Circle()
                                            .fill(isFamilyProtectionEnabled ? Color.orange : Color.black)
                                            .frame(width: 14, height: 14)
                                            .offset(x: isFamilyProtectionEnabled ? 8.5 : -8.5)
                                    }
                                }
                            }
                            
                            // Информация о семье
                            VStack(alignment: .leading, spacing: 3) {
                                Text("👤 6 членов семьи • 4 устройства")
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text("🛡️ Защита 98% • Все возрасты")
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text("🟢 VPN 100 Мбит/с • Защищено от 2,847 угроз")
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                            }
                            
                            // Кнопки действий
                            HStack(spacing: 8) {
                                Button(action: {
                                    print("Управление семьей")
                                }) {
                                    Text("Управление семьей")
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.orange)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black)
                                        )
                                }
                                
                                Button(action: {
                                    print("Добавить члена семьи")
                                }) {
                                    Text("Добавить члена семьи")
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.black)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black.opacity(0.2))
                                                .overlay(
                                                    RoundedRectangle(cornerRadius: 8)
                                                        .stroke(Color.black, lineWidth: 2)
                                                )
                                        )
                                }
                            }
                        }
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(
                                    LinearGradient(
                                        colors: [Color.orange, Color.orange.opacity(0.8)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.orange, lineWidth: 2)
                                )
                        )
                        .shadow(color: Color.orange.opacity(0.3), radius: 8)
                        .padding(.horizontal, 20)
                        
                        // AI помощник
                        VStack(alignment: .leading, spacing: 8) {
                            Text("🤖 AI Помощник ALADDIN")
                                .font(.system(size: 12, weight: .bold))
                                .foregroundColor(.orange)
                            
                            Text("\"Привет! Я помогу настроить защиту для вашей семьи. Чем могу помочь?\"")
                                .font(.system(size: 10))
                                .foregroundColor(.white.opacity(0.9))
                            
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
                        }
                        .padding(10)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.orange.opacity(0.1))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.orange, lineWidth: 2)
                                )
                        )
                        .padding(.horizontal, 20)
                    }
                }
                
                // Нижняя навигация - ПРИЖАТА К НИЗУ
                HStack(spacing: 0) {
                    navButton(icon: "house.fill", label: "Главная", index: 0, isActive: true)
                    navButton(icon: "shield.fill", label: "Защита", index: 1)
                    navButton(icon: "bell.fill", label: "Уведомления", index: 2)
                    navButton(icon: "person.fill", label: "Профиль", index: 3)
                    navButton(icon: "iphone", label: "Устройства", index: 4)
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 2)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color.black.opacity(0.4))
                )
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
            }
        }
        .onAppear {
            print("🚨 MainScreen Exact загружен! Точная копия HTML!")
        }
    }
    
    // MARK: - Navigation Button
    
    private func navButton(icon: String, label: String, index: Int, isActive: Bool = false) -> some View {
        Button(action: {
            print("Навигация: \(label)")
        }) {
            VStack(spacing: 2) {
                Image(systemName: icon)
                    .font(.system(size: 14))
                    .foregroundColor(isActive ? .white : .white.opacity(0.7))
                
                Text(label)
                    .font(.system(size: 8, weight: .bold))
                    .foregroundColor(isActive ? .white : .white.opacity(0.7))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 4)
        }
    }
}

#Preview {
    MainScreenExact()
}
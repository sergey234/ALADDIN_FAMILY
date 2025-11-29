import SwiftUI

struct FamilyScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    
    @State private var showAddMemberModal = false
    @State private var showContentFilterModal = false
    @State private var showTimeControlModal = false
    @State private var showMonitoringModal = false
    @State private var showSafetyModal = false
    @State private var showRewardsModal = false
    
    // MARK: - Navigation Helper
    
    private func navigateToMemberScreen(role: FamilyMemberCard.FamilyRole) {
        print("🔍 DEBUG: navigateToMemberScreen вызван с role: \(role)")
        
        // Haptic feedback
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Navigate based on role
        switch role {
        case .parent:
            print("🔍 DEBUG: Переход к .parentalControl")
            navigationManager.navigateTo(.parentalControl)
            print("🔍 DEBUG: Текущий экран: \(navigationManager.currentScreen)")
        case .child:
            print("🔍 DEBUG: Переход к .childInterface")
            navigationManager.navigateTo(.childInterface)
            print("🔍 DEBUG: Текущий экран: \(navigationManager.currentScreen)")
        case .teenager:
            print("🔍 DEBUG: Переход к .childInterface (teenager)")
            navigationManager.navigateTo(.childInterface) // Simplified interface
            print("🔍 DEBUG: Текущий экран: \(navigationManager.currentScreen)")
        case .elderly:
            print("🔍 DEBUG: Переход к .elderlyInterface")
            navigationManager.navigateTo(.elderlyInterface)
            print("🔍 DEBUG: Текущий экран: \(navigationManager.currentScreen)")
        }
    }
    
    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [Color(red: 0.04, green: 0.07, blue: 0.16), Color(red: 0.12, green: 0.23, blue: 0.37), Color(red: 0.18, green: 0.31, blue: 0.56)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Button(action: {
                        print("🔍 DEBUG: Кнопка 'Назад' нажата в FamilyScreen")
                        navigationManager.goBack()
                        print("🔍 DEBUG: NavigationManager.goBack() вызван")
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 20, weight: .medium))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(Color.white.opacity(0.1))
                            .clipShape(Circle())
                    }
                    .accessibilityLabel("Назад")
                    .accessibilityHint("Нажмите для возврата к предыдущему экрану")
                    
                    Spacer()
                    
                    Text("👨‍👩‍👧‍👦 ALADDIN Family")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                        .accessibilityLabel("ALADDIN Family - Семейная защита")
                        .accessibilityAddTraits(.isHeader)
                    
                    Spacer()
                    
                    Button(action: { showAddMemberModal = true }) {
                        Image(systemName: "plus")
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(Color(red: 0.04, green: 0.07, blue: 0.16))
                            .frame(width: 40, height: 40)
                            .background(Color(red: 0.96, green: 0.62, blue: 0.04))
                            .clipShape(Circle())
                    }
                    .accessibilityLabel("Добавить участника")
                    .accessibilityHint("Нажмите для добавления нового участника семьи")
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Family Overview
                        VStack(spacing: 20) {
                            Text("Семейная защита")
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                                .accessibilityLabel("Семейная защита")
                                .accessibilityAddTraits(.isHeader)
                            
                            // Stats
                            HStack(spacing: 15) {
                                StatItem(icon: "👥", value: "4", label: "Участников")
                                    .accessibilityElement(children: .combine)
                                    .accessibilityLabel("Участников: 4")
                                
                                StatItem(icon: "👶", value: "1", label: "Ребёнок")
                                    .accessibilityElement(children: .combine)
                                    .accessibilityLabel("Ребёнок: 1")
                                
                                StatItem(icon: "🛡️", value: "100%", label: "Защита")
                                    .accessibilityElement(children: .combine)
                                    .accessibilityLabel("Защита: 100%")
                            }
                            .accessibilityElement(children: .contain)
                            .accessibilityLabel("Статистика семьи")
                            
                            Button(action: { showAddMemberModal = true }) {
                                Text("Добавить участника")
                                    .font(.system(size: 16, weight: .bold))
                                    .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(
                                        LinearGradient(
                                            colors: [Color(red: 0.96, green: 0.62, blue: 0.04), Color(red: 0.85, green: 0.47, blue: 0.02)],
                                            startPoint: .leading,
                                            endPoint: .trailing
                                        )
                                    )
                                    .clipShape(Capsule())
                            }
                            .accessibilityLabel("Добавить участника")
                            .accessibilityHint("Нажмите для добавления нового участника в семью")
                        }
                        .padding(25)
                        .background(Color.white.opacity(0.1))
                        .background(.ultraThinMaterial)
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                        )
                        
                        // Family Members
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Участники семьи")
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                                .accessibilityLabel("Участники семьи")
                                .accessibilityAddTraits(.isHeader)
                            
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                                FamilyMemberCard(
                                    name: "Папа",
                                    role: .parent,
                                    avatar: "👨",
                                    status: .protected,
                                    threatsBlocked: 15,
                                    lastActive: "2 мин назад",
                                    action: {
                                        navigateToMemberScreen(role: .parent)
                                    }
                                )
                                
                                FamilyMemberCard(
                                    name: "Мама",
                                    role: .parent,
                                    avatar: "👩",
                                    status: .protected,
                                    threatsBlocked: 12,
                                    lastActive: "5 мин назад",
                                    action: {
                                        navigateToMemberScreen(role: .parent)
                                    }
                                )
                                
                                FamilyMemberCard(
                                    name: "Маша",
                                    role: .child,
                                    avatar: "👧",
                                    status: .protected,
                                    threatsBlocked: 5,
                                    lastActive: "30 мин назад",
                                    action: {
                                        navigateToMemberScreen(role: .child)
                                    }
                                )
                                
                                FamilyMemberCard(
                                    name: "Бабушка",
                                    role: .elderly,
                                    avatar: "👵",
                                    status: .protected,
                                    threatsBlocked: 3,
                                    lastActive: "1 час назад",
                                    action: {
                                        navigateToMemberScreen(role: .elderly)
                                    }
                                )
                            }
                        }
                        .padding(25)
                        .background(Color.white.opacity(0.1))
                        .background(.ultraThinMaterial)
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                        )
                        
                        // Parental Controls
                        VStack(alignment: .leading, spacing: 20) {
                            HStack {
                                Text("Родительский контроль")
                                    .font(.system(size: 18, weight: .bold))
                                    .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                                
                                Spacer()
                                
                                Button(action: {}) {
                                    Image(systemName: "gearshape")
                                        .font(.system(size: 18))
                                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                                }
                            }
                            
                            // Control Cards Grid
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                                ControlCard(
                                    icon: "📱",
                                    title: "Контент-фильтр",
                                    info: "12 категорий",
                                    status: .green,
                                    action: { showContentFilterModal = true }
                                )
                                
                                ControlCard(
                                    icon: "⏰",
                                    title: "Время",
                                    info: "2ч 30 мин",
                                    status: .green,
                                    action: { showTimeControlModal = true }
                                )
                                
                                ControlCard(
                                    icon: "👁️",
                                    title: "Мониторинг",
                                    info: "WhatsApp",
                                    status: .green,
                                    action: { showMonitoringModal = true }
                                )
                                
                                ControlCard(
                                    icon: "🛡️",
                                    title: "Безопасность",
                                    info: "5 угроз",
                                    status: .red,
                                    action: { showSafetyModal = true }
                                )
                            }
                            
                            // Rewards Card
                            Button(action: { showRewardsModal = true }) {
                                HStack(spacing: 12) {
                                    Text("🦄")
                                        .font(.system(size: 36))
                                        .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: showRewardsModal)
                                    
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text("Вознаграждение ребёнка")
                                            .font(.system(size: 15, weight: .semibold))
                                            .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
                                        
                                        Text("245 единорогов • +128 за неделю")
                                            .font(.system(size: 11))
                                            .foregroundColor(.white.opacity(0.7))
                                    }
                                    
                                    Spacer()
                                    
                                    HStack(spacing: 8) {
                                        Text("+128 🦄")
                                            .font(.system(size: 11, weight: .semibold))
                                            .foregroundColor(Color(red: 0.06, green: 0.73, blue: 0.51))
                                            .padding(.horizontal, 12)
                                            .padding(.vertical, 6)
                                            .background(Color(red: 0.06, green: 0.73, blue: 0.51).opacity(0.2))
                                            .clipShape(Capsule())
                                        
                                        Image(systemName: "chevron.right")
                                            .font(.system(size: 18))
                                            .foregroundColor(.white.opacity(0.5))
                                    }
                                }
                                .padding(15)
                                .background(
                                    LinearGradient(
                                        colors: [Color(red: 0.66, green: 0.33, blue: 0.97).opacity(0.15), Color(red: 0.93, green: 0.28, blue: 0.6).opacity(0.15)],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 15)
                                        .stroke(Color(red: 0.66, green: 0.33, blue: 0.97).opacity(0.4), lineWidth: 2)
                                )
                                .clipShape(RoundedRectangle(cornerRadius: 15))
                            }
                        }
                        .padding(15)
                        .background(Color.white.opacity(0.1))
                        .background(.ultraThinMaterial)
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                        )
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 100)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Семейный контент")
                
                Spacer()
            }
        }
        .sheet(isPresented: $showAddMemberModal) {
            AddMemberOptionsModal(isPresented: $showAddMemberModal)
        }
        .sheet(isPresented: $showContentFilterModal) {
            ContentFilterModal(isPresented: $showContentFilterModal)
        }
        .sheet(isPresented: $showTimeControlModal) {
            TimeControlModal(isPresented: $showTimeControlModal)
        }
        .sheet(isPresented: $showMonitoringModal) {
            MonitoringModal(isPresented: $showMonitoringModal)
        }
        .sheet(isPresented: $showSafetyModal) {
            SafetyModal(isPresented: $showSafetyModal)
        }
        .sheet(isPresented: $showRewardsModal) {
            RewardsModal(isPresented: $showRewardsModal)
        }
    }
}

// MARK: - Supporting Views



struct ControlCard: View {
    let icon: String
    let title: String
    let info: String
    let status: ControlStatus
    let action: () -> Void
    
    enum ControlStatus {
        case green, red
    }
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Text(icon)
                        .font(.system(size: 16))
                    
                    Text(title)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                }
                
                Text(info)
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.9))
                
                Spacer()
                
                Text(status == .green ? "🟢" : "🔴")
                    .font(.system(size: 28))
                    .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: status)
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(8)
            .background(Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.96, green: 0.62, blue: 0.04), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Modals

struct AddMemberModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Добавить участника")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Сканируйте QR-код или введите код приглашения")
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct ContentFilterModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("📱 Контент-фильтр")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Настройки фильтрации контента")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct TimeControlModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("⏰ Управление временем")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Настройки времени использования")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct MonitoringModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("👁️ Мониторинг активности")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Настройки мониторинга")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct SafetyModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🛡️ Безопасность")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Настройки безопасности")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct RewardsModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🦄 Вознаграждение ребёнка")
                .font(.title2)
                .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
            
            Text("245 единорогов на счету")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct FamilyScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyScreen()
    }
}
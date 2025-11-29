import SwiftUI

struct ALADDINNavigationBar: View {
    @EnvironmentObject var navigationManager: NavigationManager
    @State private var showingScreenList = false
    
    // MARK: - Properties
    let title: String
    let subtitle: String?
    let showBackButton: Bool
    let showAddButton: Bool
    let showProfileButton: Bool
    let showListButton: Bool
    let rightButtons: [NavigationActionButton]
    let onBack: (() -> Void)?
    let onAdd: (() -> Void)?
    
    // MARK: - Initializers
    
    // Старый инициализатор для совместимости
    init() {
        self.title = "ALADDIN"
        self.subtitle = "AI Защита семьи"
        self.showBackButton = false
        self.showAddButton = false
        self.showProfileButton = true
        self.showListButton = true
        self.rightButtons = []
        self.onBack = nil
        self.onAdd = nil
    }
    
    // Новый инициализатор с параметрами
    init(
        title: String,
        subtitle: String? = nil,
        showBackButton: Bool = false,
        showAddButton: Bool = false,
        showProfileButton: Bool = true,
        showListButton: Bool = true,
        rightButtons: [NavigationActionButton] = [],
        onBack: (() -> Void)? = nil,
        onAdd: (() -> Void)? = nil
    ) {
        self.title = title
        self.subtitle = subtitle
        self.showBackButton = showBackButton
        self.showAddButton = showAddButton
        self.showProfileButton = showProfileButton
        self.showListButton = showListButton
        self.rightButtons = rightButtons
        self.onBack = onBack
        self.onAdd = onAdd
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Верхняя панель с заголовком и кнопками (оптимизированная)
            HStack {
                // Левая сторона - кнопка назад или логотип
                if showBackButton {
                    Button(action: {
                        onBack?()
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(
                                Circle()
                                    .fill(Color.orange.opacity(0.2))
                            )
                    }
                    .accessibilityLabel("Назад")
                } else {
                    // Логотип ALADDIN
                    HStack(spacing: 8) {
                        Circle()
                            .fill(Color.orange)
                            .frame(width: 32, height: 32)
                            .overlay(
                                Text("👁️")
                                    .font(.system(size: 18))
                            )
                            .shadow(color: Color.orange.opacity(0.4), radius: 10)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(title)
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(.orange)
                                .dynamicTypeSize(.medium ... .large)
                            
                            if let subtitle = subtitle {
                                Text(subtitle)
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.white.opacity(0.7))
                                    .dynamicTypeSize(.small ... .medium)
                            }
                        }
                    }
                    .onTapGesture {
                        if navigationManager.isManuallyClosingPaymentQR {
                            navigationManager.appendLog("⚠️ ALADDINNavigationBar: tap по логотипу заблокирован (manual close)")
                            return
                        }
                        navigationManager.appendLog("🧭 ALADDINNavigationBar: navigateToRoot(.main)")
                        navigationManager.navigateToRoot(.main)
                    }
                }
                
                Spacer()
                
                // Правая сторона - кнопки
                HStack(spacing: 8) {
                    // Кнопка добавления
                    if showAddButton {
                        Button(action: {
                            onAdd?()
                        }) {
                            Image(systemName: "plus")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(
                                    Circle()
                                        .fill(Color.orange.opacity(0.2))
                                )
                        }
                        .accessibilityLabel("Добавить")
                    }
                    
                    // Дополнительные кнопки
                    ForEach(rightButtons.indices, id: \.self) { index in
                        Button(action: {
                            rightButtons[index].action()
                        }) {
                            Image(systemName: rightButtons[index].icon)
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(
                                    Circle()
                                        .fill(Color.orange.opacity(0.2))
                                )
                        }
                        .accessibilityLabel(rightButtons[index].accessibilityLabel)
                    }
                    
                    // Кнопка списка экранов
                    if showListButton {
                        Button(action: {
                            showingScreenList.toggle()
                        }) {
                            Image(systemName: "list.bullet")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(
                                    Circle()
                                        .fill(Color.orange.opacity(0.2))
                                )
                        }
                        .accessibilityLabel("Список экранов")
                    }
                    
                    // Кнопка профиля
                    if showProfileButton {
                        Button(action: {
                            // Переходим в профиль через NavigationManager
                            navigationManager.navigateTo(.profile)
                        }) {
                            Circle()
                                .fill(Color.orange)
                                .frame(width: 32, height: 32)
                                .overlay(
                                    Text("👤")
                                        .font(.system(size: 16, weight: .bold))
                                        .foregroundColor(.black)
                                )
                        }
                        .accessibilityLabel("Профиль")
                    }
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(
                LinearGradient(
                    colors: [
                        Color(red: 0.04, green: 0.07, blue: 0.16),
                        Color(red: 0.12, green: 0.23, blue: 0.37)
                    ],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            
            // Список экранов (если показан)
            if showingScreenList {
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(NavigationManager.ALADDINScreen.allCases, id: \.self) { screen in
                            NavigationScreenButton(
                                screen: screen,
                                isActive: navigationManager.currentScreen == screen
                            ) {
                                navigationManager.navigateTo(screen)
                                showingScreenList = false
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 12)
                }
                .frame(maxHeight: 300)
                .background(
                    Color.black.opacity(0.9)
                        .cornerRadius(12)
                )
                .padding(.horizontal, 20)
                .transition(.opacity.combined(with: .scale))
            }
        }
        .animation(.easeInOut(duration: 0.3), value: showingScreenList)
    }
}

// MARK: - Navigation Button Models

struct NavigationActionButton {
    let icon: String
    let accessibilityLabel: String
    let action: () -> Void
    
    init(icon: String, accessibilityLabel: String, action: @escaping () -> Void) {
        self.icon = icon
        self.accessibilityLabel = accessibilityLabel
        self.action = action
    }
}

struct NavigationScreenButton: View {
    let screen: NavigationManager.ALADDINScreen
    let isActive: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: screen.icon)
                    .font(.system(size: 16))
                    .foregroundColor(isActive ? .orange : .white)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(screen.displayName)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(isActive ? .orange : .white)
                    
                    // ✅ УБРАНО: Английское название (rawValue) - оставлены только русские названия
                    // Text(screen.rawValue)
                    //     .font(.system(size: 10))
                    //     .foregroundColor(.white.opacity(0.6))
                }
                
                Spacer()
                
                if isActive {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 16))
                        .foregroundColor(.orange)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isActive ? Color.orange.opacity(0.2) : Color.clear)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(isActive ? Color.orange : Color.white.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct ALADDINNavigationBar_Previews: PreviewProvider {
    static var previews: some View {
        ALADDINNavigationBar()
            .environmentObject(NavigationManager())
            .background(Color.black)
    }
}
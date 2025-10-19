import SwiftUI

struct ALADDINNavigationBar: View {
    @EnvironmentObject var navigationManager: NavigationManager
    @State private var showingScreenList = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Верхняя панель с логотипом и профилем
            HStack {
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
                        Text("ALADDIN")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(.orange)
                        
                        Text("AI Защита семьи")
                            .font(.system(size: 8))
                            .foregroundColor(.white.opacity(0.7))
                    }
                }
                .onTapGesture {
                    navigationManager.navigateToRoot()
                }
                
                Spacer()
                
                // Кнопка списка экранов
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
                
                // Кнопка профиля
                Button(action: {
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
                            NavigationButton(
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

struct NavigationButton: View {
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
                    
                    Text(screen.rawValue)
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.6))
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
            .environmentObject(NavigationManager.shared)
            .background(Color.black)
    }
}
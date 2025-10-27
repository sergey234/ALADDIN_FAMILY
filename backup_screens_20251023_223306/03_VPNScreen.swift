import SwiftUI

/**
 * 🔒 VPN Protection Screen
 * Полноценный экран VPN защиты
 * Источник: 02_protection_screen.html (38KB)
 */

struct VPNScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = VPNViewModel()
    @State private var showingServerSelection = false
    @State private var showingSettings = false
    
    // MARK: - Helper Views
    
    private var backgroundShape: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(Color.gray.opacity(0.3))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar()
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Навигационная панель VPN экрана")
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 20) {
                        
                        // VPN Status Card
                        vpnStatusCard
                        
                        // Connection Info
                        connectionInfoCard
                        
                        // Server Selection
                        serverSelectionCard
                        
                        // Security Features
                        securityFeaturesCard
                        
                        // Statistics
                        statisticsCard
                        
                        // Quick Actions
                        quickActionsCard
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, 16)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список карточек VPN информации")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showingServerSelection) {
            ServerSelectionView(selectedServer: .constant(VPNServer(id: "1", country: "RU", city: "Москва", flag: "🇷🇺", ping: 12, load: 45, status: .optimal)))
        }
        .sheet(isPresented: $showingSettings) {
            VPNSettingsView()
        }
    }
    
    // MARK: - VPN Status Card
    
    private var vpnStatusCard: some View {
        VStack(spacing: 16) {
            // Status Icon
            ZStack {
                Circle()
                    .fill(viewModel.isVPNEnabled ? Color.green : Color.red)
                    .frame(width: 120, height: 120)
                    .opacity(0.2)
                
                Image(systemName: viewModel.isVPNEnabled ? "shield.fill" : "shield.slash.fill")
                    .font(.system(size: 48))
                    .foregroundColor(viewModel.isVPNEnabled ? .green : .red)
            }
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(viewModel.isVPNEnabled ? "VPN защита активна" : "VPN защита неактивна")
            .accessibilityHint("Статус VPN соединения")
            
            // Status Text
            VStack(spacing: 8) {
                Text(viewModel.isVPNEnabled ? "ЗАЩИЩЕНО" : "НЕ ЗАЩИЩЕНО")
                    .font(.system(size: 32, weight: .bold))
                    .fontWeight(.bold)
                    .foregroundColor(viewModel.isVPNEnabled ? .green : .red)
                    .accessibilityLabel(viewModel.isVPNEnabled ? "Статус: Защищено" : "Статус: Не защищено")
                
                Text(viewModel.isVPNEnabled ? "Ваше соединение защищено" : "Подключитесь к VPN для защиты")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .accessibilityLabel(viewModel.isVPNEnabled ? "Ваше соединение защищено" : "Подключитесь к VPN для защиты")
            }
            
            // Connection Button
            Button(action: {
                viewModel.toggleVPN()
            }) {
                HStack(spacing: 8) {
                    Image(systemName: viewModel.isVPNEnabled ? "stop.fill" : "play.fill")
                        .font(.title2)
                    
                    Text(viewModel.isVPNEnabled ? "ОТКЛЮЧИТЬ" : "ПОДКЛЮЧИТЬ")
                        .font(.headline)
                        .fontWeight(.semibold)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(viewModel.isConnected ? Color.red : Color.green)
                )
            }
            .accessibilityLabel(viewModel.isVPNEnabled ? "Отключить VPN" : "Подключить VPN")
            .accessibilityHint("Нажмите для переключения VPN соединения")
            .accessibilityAddTraits(.isButton)
            .buttonStyle(PlainButtonStyle())
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(red: 1.0, green: 1.0, blue: 1.0).opacity(0.1), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, 20)
    }
    
    // MARK: - Connection Info Card
    
    private var connectionInfoCard: some View {
        VStack(spacing: 16) {
            HStack {
                Text("ИНФОРМАЦИЯ О СОЕДИНЕНИИ")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.primary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: 8) {
                HStack {
                    Image(systemName: "globe")
                        .font(.system(size: 16))
                        .foregroundColor(.blue)
                    Text("Сервер")
                        .font(.body)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(viewModel.selectedServer.name)
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.primary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Сервер: \(viewModel.selectedServer.name)")
                
                HStack {
                    Image(systemName: "speedometer")
                        .font(.system(size: 16))
                        .foregroundColor(.green)
                    Text("Скорость")
                        .font(.body)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("100 Мбит/с")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.primary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Скорость: 100 Мбит в секунду")
                
                HStack {
                    Image(systemName: "clock")
                        .font(.system(size: 16))
                        .foregroundColor(.secondary)
                    Text("Время подключения")
                        .font(.body)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(viewModel.connectionTime)
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.primary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Время подключения: \(viewModel.connectionTime)")
                
                HStack {
                    Image(systemName: "arrow.up.arrow.down")
                        .font(.system(size: 16))
                        .foregroundColor(.secondary)
                    Text("Передано данных")
                        .font(.body)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("\(viewModel.downloadedToday) / \(viewModel.uploadedToday)")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.primary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Передано данных: \(viewModel.downloadedToday) / \(viewModel.uploadedToday)")
            }
        }
        .padding(16)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, 20)
    }
    
    // MARK: - Server Selection Card
    
    private var serverSelectionCard: some View {
        VStack(spacing: 16) {
            serverSelectionHeader
            serverSelectionContent
        }
        .padding(16)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, 20)
    }
    
    private var serverSelectionHeader: some View {
        HStack {
            Text("ВЫБОР СЕРВЕРА")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.primary)
                .accessibilityAddTraits(.isHeader)
            
            Spacer()
            
            Button(action: {
                showingServerSelection = true
            }) {
                Text("Изменить")
                    .font(.body)
                    .foregroundColor(.blue)
            }
            .accessibilityLabel("Изменить сервер")
            .accessibilityHint("Нажмите для выбора другого VPN сервера")
            .accessibilityAddTraits(.isButton)
        }
    }
    
    private var serverSelectionContent: some View {
        HStack(spacing: 16) {
            // Flag
            Text(viewModel.selectedServer.flag)
                .font(.system(size: 32))
                .accessibilityLabel("Флаг страны \(viewModel.selectedServer.name)")
            
            serverInfoStack
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.system(size: 14))
                    .foregroundColor(.secondary)
        }
        .padding(16)
        .background(serverInfoBackground)
    }
    
    private var serverInfoStack: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(viewModel.selectedServer.name)
                .font(.headline)
                    .foregroundColor(.primary)
                .accessibilityLabel("Название сервера: \(viewModel.selectedServer.name)")
            
            Text(viewModel.selectedServer.location)
                .font(.body)
                    .foregroundColor(.secondary)
                .accessibilityLabel("Местоположение: \(viewModel.selectedServer.location)")
            
            serverStatusIndicator
        }
    }
    
    private var serverStatusIndicator: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(serverStatusColor)
                .frame(width: 8, height: 8)
                .accessibilityLabel(serverStatusAccessibilityLabel)
            
            Text(serverStatusText)
                .font(.caption)
                    .foregroundColor(.secondary)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(serverStatusAccessibilityLabel)
    }
    
    private var serverStatusColor: Color {
        viewModel.selectedServer.status == .optimal ? Color.green : Color.orange
    }
    
    private var serverStatusText: String {
        viewModel.selectedServer.status == .optimal ? "Оптимальный" : "Загружен"
    }
    
    private var serverStatusAccessibilityLabel: String {
        "Статус сервера: \(serverStatusText)"
    }
    
    private var serverInfoBackground: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(Color.gray.opacity(0.3))
    }
    
    // MARK: - Security Features Card
    
    private var securityFeaturesCard: some View {
        VStack(spacing: 16) {
            HStack {
                Text("ФУНКЦИИ БЕЗОПАСНОСТИ")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.primary)
                
                Spacer()
            }
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 16) {
                
                SecurityFeatureCard(
                    icon: "shield.fill",
                    title: "Блокировка рекламы",
                    isEnabled: true,
                    color: .green
                )
                
                SecurityFeatureCard(
                    icon: "eye.slash.fill",
                    title: "Антитрекинг",
                    isEnabled: true,
                    color: .green
                )
                
                SecurityFeatureCard(
                    icon: "lock.fill",
                    title: "Шифрование",
                    isEnabled: true,
                    color: .green
                )
                
                SecurityFeatureCard(
                    icon: "exclamationmark.triangle.fill",
                    title: "Защита от угроз",
                    isEnabled: true,
                    color: .green
                )
            }
        }
        .padding(16)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, 20)
    }
    
    // MARK: - Statistics Card
    
    private var statisticsCard: some View {
        VStack(spacing: 16) {
            HStack {
                Text("СТАТИСТИКА")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.primary)
                
                Spacer()
            }
            
            HStack(spacing: 20) {
                VStack(spacing: 5) {
                    Text("🛡️")
                        .font(.system(size: 24))
                    Text("\(viewModel.threatsBlocked)")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    Text("Угроз блокировано")
                        .font(.system(size: 12))
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Rectangle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 1, height: 40)
                
                VStack(spacing: 5) {
                    Text("📊")
                        .font(.system(size: 24))
                    Text("2.4 GB")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    Text("Данных сэкономлено")
                        .font(.system(size: 12))
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Rectangle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 1, height: 40)
                
                VStack(spacing: 5) {
                    Text("⏰")
                        .font(.system(size: 24))
                    Text("24:00:00")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    Text("Время защиты")
                        .font(.system(size: 12))
                        .foregroundColor(.white.opacity(0.8))
                }
            }
        }
        .padding(16)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, 20)
    }
    
    // MARK: - Quick Actions Card
    
    private var quickActionsCard: some View {
        VStack(spacing: 16) {
            HStack {
                Text("БЫСТРЫЕ ДЕЙСТВИЯ")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.primary)
                
                Spacer()
            }
            
            HStack(spacing: 16) {
                QuickActionButton(
                    icon: "gearshape.fill",
                    title: "Настройки",
                    action: { showingSettings = true }
                )
                
                QuickActionButton(
                    icon: "chart.bar.fill",
                    title: "Статистика",
                    action: { /* Navigate to stats */ }
                )
                
                QuickActionButton(
                    icon: "questionmark.circle.fill",
                    title: "Помощь",
                    action: { /* Navigate to help */ }
                )
            }
        }
        .padding(16)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, 20)
    }
}

// MARK: - Supporting Views


struct SecurityFeatureCard: View {
    let icon: String
    let title: String
    let isEnabled: Bool
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                    .foregroundColor(.primary)
                .multilineTextAlignment(.center)
            
            Circle()
                .fill(isEnabled ? color : Color.secondary)
                .frame(width: 12, height: 12)
        }
        .frame(maxWidth: .infinity)
        .padding(8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.3))
        )
    }
}


struct QuickActionButton: View {
    let icon: String
    let title: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.blue)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Placeholder Views

struct ServerSelectionView: View {
    @Binding var selectedServer: VPNServer
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack {
                Text("Выбор сервера")
                    .font(.title)
                Text("Здесь будет список серверов")
                    .foregroundColor(.secondary)
                Spacer()
            }
            .navigationTitle("Серверы")
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
}

struct VPNSettingsView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack {
                Text("Настройки VPN")
                    .font(.title)
                Text("Здесь будут настройки")
                    .foregroundColor(.secondary)
                Spacer()
            }
            .navigationTitle("Настройки")
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
}

#if DEBUG
struct VPNScreen_Previews: PreviewProvider {
    static var previews: some View {
        VPNScreen()
    }
}
#endif

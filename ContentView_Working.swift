import SwiftUI

/// 🎯 Working Content View
/// Рабочая версия приложения без ошибок
struct ContentView_Working: View {
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Логотип
                VStack(spacing: 16) {
                    Circle()
                        .fill(Color.orange)
                        .frame(width: 80, height: 80)
                        .overlay(
                            Text("👁️")
                                .font(.system(size: 40))
                        )
                    
                    Text("ALADDIN")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.orange)
                    
                    Text("AI Защита семьи")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                // Основные кнопки
                VStack(spacing: 16) {
                    NavigationLink(destination: VPNScreen_Working()) {
                        HStack {
                            Image(systemName: "shield.fill")
                                .font(.title2)
                            Text("VPN Защита")
                                .font(.headline)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                        }
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(12)
                    }
                    
                    NavigationLink(destination: FamilyScreen_Working()) {
                        HStack {
                            Image(systemName: "person.3.fill")
                                .font(.title2)
                            Text("Семья")
                                .font(.headline)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                        }
                        .padding()
                        .background(Color.green.opacity(0.1))
                        .cornerRadius(12)
                    }
                    
                    NavigationLink(destination: SettingsScreen_Working()) {
                        HStack {
                            Image(systemName: "gear")
                                .font(.title2)
                            Text("Настройки")
                                .font(.headline)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                    }
                }
                
                Spacer()
                
                // Статус
                Text("Приложение готово к работе!")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .navigationTitle("ALADDIN")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

/// 🛡️ Working VPN Screen
struct VPNScreen_Working: View {
    @State private var isConnected = false
    
    var body: some View {
        VStack(spacing: 30) {
            // Статус
            VStack(spacing: 16) {
                Circle()
                    .fill(isConnected ? Color.green : Color.red)
                    .frame(width: 120, height: 120)
                    .overlay(
                        Image(systemName: isConnected ? "shield.fill" : "shield.slash.fill")
                            .font(.system(size: 48))
                            .foregroundColor(.white)
                    )
                
                Text(isConnected ? "Подключено" : "Отключено")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Россия • Москва")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            // Кнопка подключения
            Button(action: {
                isConnected.toggle()
            }) {
                Text(isConnected ? "Отключить VPN" : "Подключить VPN")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(isConnected ? Color.red : Color.blue)
                    .cornerRadius(12)
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("VPN")
        .navigationBarTitleDisplayMode(.inline)
    }
}

/// 👨‍👩‍👧‍👦 Working Family Screen
struct FamilyScreen_Working: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("👨‍👩‍👧‍👦")
                .font(.system(size: 80))
            
            Text("Семья")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("Управление семейными устройствами")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            Spacer()
        }
        .padding()
        .navigationTitle("Семья")
        .navigationBarTitleDisplayMode(.inline)
    }
}

/// ⚙️ Working Settings Screen
struct SettingsScreen_Working: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("⚙️")
                .font(.system(size: 80))
            
            Text("Настройки")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("Конфигурация приложения")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            Spacer()
        }
        .padding()
        .navigationTitle("Настройки")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#if DEBUG
struct ContentView_Working_Previews: PreviewProvider {
    static var previews: some View {
        ContentView_Working()
    }
}
#endif

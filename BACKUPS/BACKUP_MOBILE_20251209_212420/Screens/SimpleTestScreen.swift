import SwiftUI

// MARK: - Простой тестовый экран для проверки базовой функциональности
struct SimpleTestScreen: View {
    @State private var buttonPressed = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("ПРОСТОЙ ТЕСТ")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            Button(action: {
                print("🚨 ПРОСТАЯ КНОПКА НАЖАТА!")
                buttonPressed.toggle()
            }) {
                Text("ТЕСТ КНОПКА")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .padding()
                    .background(buttonPressed ? Color.green : Color.red)
                    .cornerRadius(15)
            }
            
            if buttonPressed {
                Text("КНОПКА РАБОТАЕТ!")
                    .font(.headline)
                    .foregroundColor(.green)
                    .padding()
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(10)
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            LinearGradient(
                colors: [Color.blue, Color.purple],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .onAppear {
            print("🚨 SimpleTestScreen загружен!")
        }
    }
}



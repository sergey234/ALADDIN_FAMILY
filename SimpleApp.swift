import SwiftUI

@main
struct SimpleApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 30) {
                Image(systemName: "house.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.white)
                
                Text("ALADDIN Family")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                
                Text("Семейная защита")
                    .font(.title2)
                    .foregroundColor(.white.opacity(0.8))
                
                VStack(spacing: 20) {
                    HStack(spacing: 20) {
                        FamilyCard(title: "Мама", status: "Онлайн", isProtected: true)
                        FamilyCard(title: "Папа", status: "Офлайн", isProtected: true)
                    }
                    
                    HStack(spacing: 20) {
                        FamilyCard(title: "Дочка", status: "Онлайн", isProtected: true)
                        FamilyCard(title: "Сын", status: "Онлайн", isProtected: false)
                    }
                }
                
                Button(action: {}) {
                    HStack {
                        Image(systemName: "shield.checkered")
                        Text("Защита активна")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.green.opacity(0.3))
                    .cornerRadius(15)
                }
            }
            .padding()
        }
    }
}

struct FamilyCard: View {
    let title: String
    let status: String
    let isProtected: Bool
    
    var body: some View {
        VStack(spacing: 10) {
            Circle()
                .fill(isProtected ? Color.green : Color.red)
                .frame(width: 20, height: 20)
            
            Text(title)
                .font(.headline)
                .foregroundColor(.white)
            
            Text(status)
                .font(.caption)
                .foregroundColor(.white.opacity(0.7))
            
            Image(systemName: isProtected ? "checkmark.shield" : "exclamationmark.triangle")
                .foregroundColor(isProtected ? .green : .red)
        }
        .frame(width: 120, height: 100)
        .background(
            RoundedRectangle(cornerRadius: 15)
                .fill(Color.white.opacity(0.1))
        )
    }
}

#if DEBUG
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
#endif


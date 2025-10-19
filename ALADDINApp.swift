import SwiftUI

@main
struct ALADDINApp: App {
    var body: some Scene {
        WindowGroup {
            VStack {
                Text("🚀 ALADDIN РАБОТАЕТ!")
                    .font(.largeTitle)
                    .foregroundColor(.white)
                
                Text("Если вы видите этот текст - приложение работает!")
                    .font(.headline)
                    .foregroundColor(.green)
                    .multilineTextAlignment(.center)
                    .padding()
                
                Button("Тест кнопки") {
                    print("Кнопка нажата!")
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color.black)
            .onAppear {
                print("🚀 ALADDIN App запущен с тестовым экраном!")
            }
        }
    }
}

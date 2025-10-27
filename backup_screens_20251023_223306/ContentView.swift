import SwiftUI

struct ContentView: View {
    var body: some View {
        // Основной интерфейс приложения с навигацией
        NavigationView {
            MainScreen()
                .navigationBarHidden(true) // Скрываем стандартную навигационную панель
        }
        .navigationViewStyle(StackNavigationViewStyle()) // Используем Stack стиль для iPhone
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
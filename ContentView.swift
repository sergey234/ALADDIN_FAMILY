import SwiftUI

struct ContentView: View {
    var body: some View {
        MainScreen()
            .environmentObject(MainViewModel())
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager.shared)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

import SwiftUI

struct SettingsScreen: View {
    var body: some View {
        VStack {
            Text("Settings Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Settings functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreen()
    }
}
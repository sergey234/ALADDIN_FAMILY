import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "shield.fill")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("ALADDIN Family Security")
                .font(.title)
                .fontWeight(.bold)
            Text("Защита вашей семьи")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
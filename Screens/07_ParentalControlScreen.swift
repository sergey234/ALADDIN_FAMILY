import SwiftUI

struct ParentalControlScreen: View {
    var body: some View {
        VStack {
            Text("Parental Control Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Parental Control functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct ParentalControlScreen_Previews: PreviewProvider {
    static var previews: some View {
        ParentalControlScreen()
    }
}
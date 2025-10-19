import SwiftUI

struct TariffsScreen: View {
    var body: some View {
        VStack {
            Text("Tariffs Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Tariffs functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct TariffsScreen_Previews: PreviewProvider {
    static var previews: some View {
        TariffsScreen()
    }
}
import SwiftUI

struct FamilyScreen: View {
    var body: some View {
        VStack {
            Text("Family Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Family functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct FamilyScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyScreen()
    }
}

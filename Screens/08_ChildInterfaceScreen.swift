import SwiftUI

struct ChildInterfaceScreen: View {
    var body: some View {
        VStack {
            Text("Child Interface Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Child Interface functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct ChildInterfaceScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildInterfaceScreen()
    }
}
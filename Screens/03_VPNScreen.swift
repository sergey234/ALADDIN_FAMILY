import SwiftUI

struct VPNScreen: View {
    var body: some View {
        VStack {
            Text("VPN Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("VPN functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct VPNScreen_Previews: PreviewProvider {
    static var previews: some View {
        VPNScreen()
    }
}
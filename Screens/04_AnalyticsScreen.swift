import SwiftUI

struct AnalyticsScreen: View {
    var body: some View {
        VStack {
            Text("Analytics Screen")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Analytics functionality will be implemented here")
                .foregroundColor(.gray)
                .padding()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct AnalyticsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AnalyticsScreen()
    }
}
import SwiftUI

struct RewardsQuickModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🎁 Rewards")
                .font(.title)
                .foregroundColor(.white)
            
            Text("You have earned rewards!")
                .foregroundColor(.gray)
            
            Button("Close") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
        .background(Color.black)
        .cornerRadius(16)
    }
}

struct RewardsQuickModal_Previews: PreviewProvider {
    static var previews: some View {
        RewardsQuickModal(isPresented: .constant(true))
    }
}

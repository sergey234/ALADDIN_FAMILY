import SwiftUI

struct ConsentModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Consent Required")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Please provide your consent to continue")
                .foregroundColor(.gray)
            
            Button("I Agree") {
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

struct ConsentModal_Previews: PreviewProvider {
    static var previews: some View {
        ConsentModal(isPresented: .constant(true))
    }
}
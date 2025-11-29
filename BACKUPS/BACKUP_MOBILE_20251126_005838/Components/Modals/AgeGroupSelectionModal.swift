import SwiftUI

struct AgeGroupSelectionModal: View {
    @Binding var isPresented: Bool
    @State private var selectedAgeGroup: AgeGroup = .adult
    
    enum AgeGroup: String, CaseIterable {
        case child = "Child"
        case teen = "Teen"
        case adult = "Adult"
        case elderly = "Elderly"
    }
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Select Age Group")
                .font(.title2)
                .foregroundColor(.white)
            
            ForEach(AgeGroup.allCases, id: \.self) { ageGroup in
                Button(action: {
                    selectedAgeGroup = ageGroup
                }) {
                    HStack {
                        Text(ageGroup.rawValue)
                            .foregroundColor(.white)
                        Spacer()
                        if selectedAgeGroup == ageGroup {
                            Image(systemName: "checkmark")
                                .foregroundColor(.blue)
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(8)
                }
            }
            
            Button("Confirm") {
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

struct AgeGroupSelectionModal_Previews: PreviewProvider {
    static var previews: some View {
        AgeGroupSelectionModal(isPresented: .constant(true))
    }
}
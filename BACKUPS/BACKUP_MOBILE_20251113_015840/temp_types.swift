// MARK: - Missing Types
struct FamilyScreen: View {
    var body: some View {
        Text("Family Screen")
    }
}

struct AgeGroupSelectionModal: View {
    @Binding var isPresented: Bool
    var body: some View {
        Text("Age Group Selection Modal")
    }
}

import SwiftUI

/**
 * 🔤 Letter Selection Modal
 * Модальное окно выбора персональной буквы
 * Окно #3 в процессе регистрации
 */

struct LetterSelectionModal: View {
    
    @Binding var isPresented: Bool
    @Binding var selectedLetter: String?
    
    var onLetterSelected: (String) -> Void
    
    // MARK: - Russian Alphabet
    
    private let russianAlphabet = [
        ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И"],
        ["К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У"],
        ["Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ы", "Э", "Ю", "Я"]
    ]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Backdrop blur
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .blur(radius: 20)
            
            // Modal content
            VStack(spacing: Spacing.xl) {
                // Header
                VStack(spacing: Spacing.m) {
                    Text("🔤")
                        .font(.system(size: 40))
                    
                    Text("Ваша персональная буква")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(Color(hex: "#FCD34D"))  // Яркое золото из иконки!
                        .multilineTextAlignment(.center)
                    
                    Text("(Вместо имени, для анонимности)")
                        .font(.system(size: 14))
                        .foregroundColor(.textSecondary)
                }
                
                // Letter grid (проверено - помещается!)
                VStack(spacing: 3) {  // Исправлено: 3 вместо 6
                    ForEach(russianAlphabet, id: \.self) { row in
                        HStack(spacing: 3) {  // Исправлено: 3 вместо 6
                            ForEach(row, id: \.self) { letter in
                                LetterButton(
                                    letter: letter,
                                    isSelected: selectedLetter == letter
                                ) {
                                    selectLetter(letter)
                                }
                            }
                        }
                    }
                }
                
                // Selected letter display
                if let letter = selectedLetter {
                    HStack(spacing: Spacing.s) {
                        Text("Выбрана буква:")
                            .font(.system(size: 14))
                            .foregroundColor(.textSecondary)
                        
                        Text(letter)
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(Color(hex: "#60A5FA"))  // Электрический синий!
                    }
                    .padding(Spacing.m)
                    .background(Color(hex: "#60A5FA").opacity(0.1))  // Электрический синий!
                    .cornerRadius(12)
                }
            }
            .padding(Spacing.xl)
            .frame(width: 340)
            .background(
                LinearGradient(
                    colors: [
                        Color(hex: "#0F172A"),  // Космический тёмный
                        Color(hex: "#1E3A8A"),  // Глубокий синий
                        Color(hex: "#3B82F6"),  // Электрический синий
                        Color(hex: "#1E40AF")   // Королевский синий
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(24)
            .shadow(color: .black.opacity(0.5), radius: 30, x: 0, y: 20)
        }
        .transition(.asymmetric(
            insertion: .scale(scale: 0.8).combined(with: .opacity),
            removal: .scale(scale: 0.8).combined(with: .opacity)
        ))
        .animation(.spring(response: 0.4, dampingFraction: 0.8), value: isPresented)
    }
    
    // MARK: - Actions
    
    private func selectLetter(_ letter: String) {
        selectedLetter = letter
        HapticFeedback.selection()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            onLetterSelected(letter)
        }
    }
}

// MARK: - Letter Button Component

struct LetterButton: View {
    let letter: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(letter)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white)
                .frame(width: 25, height: 25)  // Исправлено: 25 вместо 28 (безопасный размер!)
                .background(
                    isSelected
                        ? Color(hex: "#60A5FA")  // Электрический синий из иконки!
                        : Color.white.opacity(0.1)
                )
                .cornerRadius(8)
                .shadow(
                    color: isSelected ? Color(hex: "#60A5FA").opacity(0.5) : .clear,  // Электрическое свечение!
                    radius: isSelected ? 10 : 0
                )
                .scaleEffect(isSelected ? 1.1 : 1.0)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

struct LetterSelectionModal_Previews: PreviewProvider {
    static var previews: some View {
        LetterSelectionModal(
            isPresented: .constant(true),
            selectedLetter: .constant("А"),
            onLetterSelected: { _ in }
        )
    }
}


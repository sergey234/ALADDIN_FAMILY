import SwiftUI

/// 🎰 Wheel of Fortune View
/// Колесо удачи с анимацией вращения
/// Источник дизайна: /mobile/wireframes/wheel_of_fortune_component.html
struct WheelOfFortuneView: View {
    
    // MARK: - State
    
    @State private var rotation: Double = 0
    @State private var isSpinning: Bool = false
    @State private var wonPrize: Int = 0
    @State private var showPrizeAlert: Bool = false
    @State private var canSpin: Bool = true
    @State private var timeUntilNextSpin: Int = 0
    @State private var totalSpins: Int = 0
    @State private var totalWon: Int = 0
    
    let prizes = [5, 10, 20, 50, 100, 500]
    let probabilities = [0.4, 0.3, 0.15, 0.1, 0.04, 0.01]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: Spacing.l) {
                // Заголовок
                Text("🎰 КОЛЕСО УДАЧИ")
                    .font(.h1)
                    .foregroundColor(.textPrimary)
                
                // Колесо
                wheelView
                
                // Кнопка вращения
                spinButton
                
                // Таймер
                if !canSpin {
                    timerView
                }
                
                // Статистика
                statsView
                
                Spacer()
            }
            .padding(.top, Spacing.xxl)
        }
        .alert("🎉 ПРИЗ!", isPresented: $showPrizeAlert) {
            Button("OK") {
                showPrizeAlert = false
            }
        } message: {
            Text("Ты выиграл \(wonPrize) 🦄!")
        }
    }
    
    // MARK: - Wheel View
    
    private var wheelView: some View {
        ZStack {
            // Колесо
            Circle()
                .fill(
                    LinearGradient(
                        colors: [Color(hex: "A855F7"), Color(hex: "EC4899")],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .frame(width: 280, height: 280)
                .overlay(
                    ZStack {
                        ForEach(0..<6, id: \.self) { index in
                            sectorView(index: index)
                        }
                    }
                )
                .rotationEffect(.degrees(rotation))
                .animation(.easeInOut(duration: 3.0), value: rotation)
            
            // Центр
            Circle()
                .fill(Color(hex: "0a1128"))
                .frame(width: 60, height: 60)
                .overlay(
                    Text("🦄")
                        .font(.system(size: 30))
                )
            
            // Указатель
            VStack {
                Image(systemName: "arrowtriangle.down.fill")
                    .font(.system(size: 30))
                    .foregroundColor(.dangerRed)
                    .offset(y: -150)
                Spacer()
            }
        }
    }
    
    private func sectorView(index: Int) -> some View {
        let angle = 60.0 * Double(index)
        
        return ZStack {
            // Сектор (упрощённый - используем текст)
            VStack {
                Text("\(index + 1)️⃣")
                    .font(.title2)
                    .foregroundColor(.white)
                
                Text("\(prizes[index])")
                    .font(.h2)
                    .foregroundColor(.white)
                
                Text("🦄")
                    .font(.body)
            }
            .offset(y: -100)
            .rotationEffect(.degrees(angle))
        }
        .rotationEffect(.degrees(-angle))
    }
    
    // MARK: - Spin Button
    
    private var spinButton: some View {
        Button(action: spinWheel) {
            Text(canSpin ? "🎰 КРУТИТЬ!" : "⏰ Подожди...")
                .font(.h2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity)
                .padding(Spacing.l)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.xlarge)
                        .fill(
                            canSpin ?
                            LinearGradient(colors: [.successGreen, .successGreen.opacity(0.8)], startPoint: .leading, endPoint: .trailing) :
                            LinearGradient(colors: [.textSecondary, .textSecondary.opacity(0.8)], startPoint: .leading, endPoint: .trailing)
                        )
                )
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(!canSpin)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Timer View
    
    private var timerView: some View {
        VStack(spacing: Spacing.xs) {
            Text("⏰ Следующее вращение через:")
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            Text("\(timeUntilNextSpin) ч")
                .font(.h2)
                .foregroundColor(.primaryBlue)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Stats View
    
    private var statsView: some View {
        HStack(spacing: Spacing.xl) {
            VStack(spacing: Spacing.xs) {
                Text("\(totalSpins)")
                    .font(.h2)
                    .foregroundColor(.primaryBlue)
                Text("Вращений")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Rectangle()
                .fill(Color.textSecondary.opacity(0.3))
                .frame(width: 1, height: 40)
            
            VStack(spacing: Spacing.xs) {
                Text("\(totalWon) 🦄")
                    .font(.h2)
                    .foregroundColor(.successGreen)
                Text("Выиграно")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Actions
    
    private func spinWheel() {
        guard canSpin && !isSpinning else { return }
        
        isSpinning = true
        canSpin = false
        
        // Weighted random
        let random = Double.random(in: 0...1)
        var cumulative = 0.0
        var selectedIndex = 0
        
        for (index, prob) in probabilities.enumerated() {
            cumulative += prob
            if random <= cumulative {
                selectedIndex = index
                break
            }
        }
        
        wonPrize = prizes[selectedIndex]
        
        // Анимация вращения
        let spins = 5.0
        let targetRotation = rotation + (360 * spins) + (60 * Double(selectedIndex))
        
        withAnimation(.easeOut(duration: 3.0)) {
            rotation = targetRotation
        }
        
        // Показать приз через 3 секунды
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
            isSpinning = false
            totalSpins += 1
            totalWon += wonPrize
            showPrizeAlert = true
            timeUntilNextSpin = 24
            
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.success)
        }
    }
}

// MARK: - Preview

#Preview {
    WheelOfFortuneView()
}




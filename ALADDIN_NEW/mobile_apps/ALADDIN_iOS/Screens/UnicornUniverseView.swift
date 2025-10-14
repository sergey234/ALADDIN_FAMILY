import SwiftUI

/// 🌳 Unicorn Universe View
/// Единорог-вселенная (сад + коллекция)
/// Источник дизайна: /mobile/wireframes/unicorn_universe_component.html
struct UnicornUniverseView: View {
    
    @State private var unicornBalance = 245
    @State private var gardenCount = 25
    
    let unicornSpecies = [
        ("🦄", "Базовый", "Обычный единорог"),
        ("⭐", "Звёздный", "Сияет в ночи"),
        ("🌈", "Радужный", "Все цвета"),
        ("💎", "Алмазный", "Редкий и ценный")
    ]
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("🌳 ЕДИНОРОГ-ВСЕЛЕННАЯ")
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                    
                    // Сад единорогов
                    gardenView
                    
                    // Коллекция
                    collectionView
                    
                    Spacer()
                }
                .padding(.top, Spacing.xxl)
            }
        }
    }
    
    private var gardenView: some View {
        VStack(spacing: Spacing.m) {
            Text("🌳 МОЙ САД")
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            Text("\(gardenCount) единорогов")
                .font(.h3)
                .foregroundColor(.successGreen)
            
            // Визуализация сада (упрощённая)
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 5), spacing: 8) {
                ForEach(0..<gardenCount, id: \.self) { _ in
                    Text("🦄")
                        .font(.system(size: 24))
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.successGreen.opacity(0.1))
            )
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private var collectionView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("📚 КОЛЛЕКЦИЯ")
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                ForEach(unicornSpecies, id: \.0) { species in
                    speciesCard(icon: species.0, name: species.1, desc: species.2)
                }
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func speciesCard(icon: String, name: String, desc: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 40))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Text(desc)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
}

#Preview {
    UnicornUniverseView()
}




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
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана единорог-вселенной")
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("🌳 ЕДИНОРОГ-ВСЕЛЕННАЯ")
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                        .accessibilityAddTraits(.isHeader)
                        .accessibilityLabel("Единорог-вселенная")
                    
                    // Сад единорогов
                    gardenView
                    
                    // Коллекция
                    collectionView
                    
                    Spacer()
                }
                .padding(.top, Spacing.xxl)
            }
            .accessibilityElement(children: .contain)
            .accessibilityLabel("Содержимое экрана единорог-вселенной")
        }
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 UnicornUniverseView загружен!")
        }
    }
    
    private var gardenView: some View {
        VStack(spacing: Spacing.m) {
            Text("🌳 МОЙ САД")
                .font(.h2)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
                .accessibilityLabel("Мой сад единорогов")
            
            Text("\(gardenCount) единорогов")
                .font(.h3)
                .foregroundColor(.successGreen)
                .accessibilityLabel("Количество единорогов в саду: \(gardenCount)")
            
            // Визуализация сада (упрощённая)
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 5), spacing: 8) {
                ForEach(0..<gardenCount, id: \.self) { _ in
                    Text("🦄")
                        .font(.system(size: 24))
                        .accessibilityLabel("Единорог")
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.successGreen.opacity(0.1))
            )
            .accessibilityElement(children: .contain)
            .accessibilityLabel("Сад с \(gardenCount) единорогами")
        }
        .padding(.horizontal, Spacing.screenPadding)
        .cardShadow()
        .appGlassmorphism()
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Карточка сада единорогов")
    }
    
    private var collectionView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("📚 КОЛЛЕКЦИЯ")
                .font(.h2)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
                .accessibilityLabel("Коллекция видов единорогов")
            
            VStack(spacing: Spacing.s) {
                ForEach(unicornSpecies, id: \.0) { species in
                    speciesCard(icon: species.0, name: species.1, desc: species.2)
                }
            }
            .accessibilityElement(children: .contain)
            .accessibilityLabel("Список видов единорогов")
        }
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Секция коллекции единорогов")
    }
    
    private func speciesCard(icon: String, name: String, desc: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 40))
                .accessibilityLabel("Иконка: \(icon)")
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Text(desc)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(name): \(desc)")
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Вид единорога: \(name) - \(desc)")
    }
}

#if DEBUG
struct UnicornUniverseView_Previews: PreviewProvider {
    static var previews: some View {
        UnicornUniverseView()
    }
}
#endif




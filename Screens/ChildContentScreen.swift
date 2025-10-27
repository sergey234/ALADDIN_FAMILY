import SwiftUI

/// 👶 Child Content Screen
/// Универсальный экран контента для детей с адаптацией по возрасту
struct ChildContentScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    let category: String
    let ageGroup: ChildInterfaceScreen.AgeGroup
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (адаптивный по возрасту)
            backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Заголовок
                contentHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 20) {
                        // Приветствие
                        greetingSection
                        
                        // Специфичный контент для каждой категории
                        categoryContent
                        
                        // Дополнительная информация
                        additionalInfoSection
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                }
            }
        }
    }
    
    // MARK: - Background Gradient
    
    private var backgroundGradient: some View {
        LinearGradient(
            colors: gradientColors,
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
    
    private var gradientColors: [Color] {
        switch ageGroup {
        case .kids:
            return [Color.pink.opacity(0.8), Color.purple.opacity(0.6), Color.blue.opacity(0.4)]
        case .school:
            return [Color.green.opacity(0.8), Color.blue.opacity(0.6), Color.cyan.opacity(0.4)]
        case .teen:
            return [Color.blue.opacity(0.8), Color.purple.opacity(0.6), Color.indigo.opacity(0.4)]
        case .youngAdult:
            return [Color.indigo.opacity(0.8), Color.purple.opacity(0.6), Color.blue.opacity(0.4)]
        }
    }
    
    // MARK: - Header
    
    private var contentHeader: some View {
        HStack(spacing: 16) {
            // Кнопка назад
            Button(action: {
                navigationManager.goBack()
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.white.opacity(0.2))
                    )
            }
            .accessibilityLabel("Назад")
            
            // Заголовок
            VStack(alignment: .leading, spacing: 4) {
                Text(ageGroup.title)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.white.opacity(0.8))
                
                Text(category)
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(.white)
            }
            
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.top, 16)
        .padding(.bottom, 12)
    }
    
    // MARK: - Greeting Section
    
    private var greetingSection: some View {
        VStack(spacing: 12) {
            Text(greetingEmoji)
                .font(.system(size: 60))
            
            Text(greetingText)
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.white)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 24)
    }
    
    private var greetingEmoji: String {
        switch category {
        case "ИГРУШКИ": return "🧸"
        case "РИСОВАНИЕ": return "🎨"
        case "ПЕСЕНКИ": return "🎵"
        case "СКАЗКИ": return "📖"
        case "ИГРЫ": return "🎮"
        case "УЧЁБА": return "📚"
        case "ТВОРЧЕСТВО": return "🎨"
        case "МУЛЬТИКИ": return "📺"
        case "ПРОГРАММИРОВАНИЕ": return "💻"
        case "СОЦИАЛЬНЫЕ СЕТИ": return "📱"
        case "МУЗЫКА": return "🎵"
        case "ВИДЕО": return "📺"
        case "ОБРАЗОВАНИЕ": return "🎓"
        case "КАРЬЕРА": return "💼"
        case "ИНТЕРНЕТ": return "🌐"
        case "КИНО": return "🎬"
        default: return "🌟"
        }
    }
    
    private var greetingText: String {
        switch category {
        case "ИГРУШКИ": return "Давай играть!"
        case "РИСОВАНИЕ": return "Творчество начинается здесь!"
        case "ПЕСЕНКИ": return "Музыка для маленьких!"
        case "СКАЗКИ": return "Волшебные истории!"
        case "ИГРЫ": return "Игровая зона!"
        case "УЧЁБА": return "Учимся с удовольствием!"
        case "ТВОРЧЕСТВО": return "Креативим вместе!"
        case "МУЛЬТИКИ": return "Любимые мультики!"
        case "ПРОГРАММИРОВАНИЕ": return "Кодируем и творим!"
        case "СОЦИАЛЬНЫЕ СЕТИ": return "Общение и друзья!"
        case "МУЗЫКА": return "Твоя музыка!"
        case "ВИДЕО": return "Развлекайся!"
        case "ОБРАЗОВАНИЕ": return "Развивайся!"
        case "КАРЬЕРА": return "Строй будущее!"
        case "ИНТЕРНЕТ": return "Изучай мир!"
        case "КИНО": return "Смотри и наслаждайся!"
        default: return "Добро пожаловать!"
        }
    }
    
    // MARK: - Category Content
    
    private var categoryContent: some View {
        VStack(spacing: 16) {
            switch ageGroup {
            case .kids:
                kidsContent
            case .school:
                schoolContent
            case .teen:
                teenContent
            case .youngAdult:
                youngAdultContent
            }
        }
    }
    
    // MARK: - Kids Content (1-6 лет)
    
    private var kidsContent: some View {
        VStack(spacing: 16) {
            switch category {
            case "ИГРУШКИ":
                toysContent
            case "РИСОВАНИЕ":
                drawingContent
            case "ПЕСЕНКИ":
                songsContent
            case "СКАЗКИ":
                fairyTalesContent
            default:
                defaultContent
            }
        }
    }
    
    private var toysContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "cube.box")
                .font(.system(size: 80))
                .foregroundColor(.pink)
            
            Text("Выбери игрушку для игры")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Кнопки игр
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                toyButton(icon: "🧸", title: "Медвежонок")
                toyButton(icon: "🚗", title: "Машинка")
                toyButton(icon: "🎈", title: "Шарик")
                toyButton(icon: "🎁", title: "Сюрприз")
            }
        }
    }
    
    private func toyButton(icon: String, title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.pink.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.pink, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var drawingContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "paintbrush.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text("Нарисуй что угодно!")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Цвета для рисования
            HStack(spacing: 16) {
                colorButton(color: .red)
                colorButton(color: .blue)
                colorButton(color: .yellow)
                colorButton(color: .green)
                colorButton(color: .purple)
            }
        }
    }
    
    private func colorButton(color: Color) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            Circle()
                .fill(color)
                .frame(width: 50, height: 50)
                .overlay(
                    Circle()
                        .stroke(Color.white, lineWidth: 3)
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var songsContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "music.note")
                .font(.system(size: 80))
                .foregroundColor(.purple)
            
            Text("Песни для малышей")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Список песен
            VStack(spacing: 12) {
                songItem(title: "🐻 Песенка медведя")
                songItem(title: "🐰 Песенка зайки")
                songItem(title: "🐸 Песенка лягушки")
            }
        }
    }
    
    private func songItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.purple)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var fairyTalesContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "book.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text("Волшебные сказки")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            // Список сказок
            VStack(spacing: 12) {
                taleItem(title: "🧙‍♀️ Колобок")
                taleItem(title: "👑 Репка")
                taleItem(title: "🐷 Три поросёнка")
            }
        }
    }
    
    private func taleItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - School Content (7-12 лет)
    
    private var schoolContent: some View {
        VStack(spacing: 16) {
            switch category {
            case "ИГРЫ":
                gamesContent
            case "УЧЁБА":
                studyContent
            case "ТВОРЧЕСТВО":
                creativityContent
            case "МУЛЬТИКИ":
                cartoonsContent
            default:
                defaultContent
            }
        }
    }
    
    private var gamesContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "gamecontroller.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)
            
            Text("Игровая зона")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                gameButton(icon: "🎮", title: "Приключения")
                gameButton(icon: "🧩", title: "Пазлы")
                gameButton(icon: "🎯", title: "Логика")
                gameButton(icon: "⚡", title: "Скорость")
            }
        }
    }
    
    private func gameButton(icon: String, title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.green.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.green, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var studyContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "book.closed.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text("Учимся с удовольствием!")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                studySubject(subject: "📖 Русский язык")
                studySubject(subject: "🔢 Математика")
                studySubject(subject: "🌍 Окружающий мир")
            }
        }
    }
    
    private func studySubject(subject: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(subject)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var creativityContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "paintpalette.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text("Твори и создавай!")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                creativityButton(icon: "✏️", title: "Рисование")
                creativityButton(icon: "✂️", title: "Аппликация")
                creativityButton(icon: "🎨", title: "Раскраска")
                creativityButton(icon: "🖼️", title: "Фото")
            }
        }
    }
    
    private func creativityButton(icon: String, title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.orange.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.orange, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var cartoonsContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "tv.fill")
                .font(.system(size: 80))
                .foregroundColor(.red)
            
            Text("Любимые мультики")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                cartoonItem(title: "🤖 Роботы")
                cartoonItem(title: "🐾 Приключения")
                cartoonItem(title: "🌟 Фантазия")
            }
        }
    }
    
    private func cartoonItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.red)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Teen Content (13-17 лет)
    
    private var teenContent: some View {
        VStack(spacing: 16) {
            switch category {
            case "ПРОГРАММИРОВАНИЕ":
                programmingContent
            case "СОЦИАЛЬНЫЕ СЕТИ":
                socialMediaContent
            case "МУЗЫКА":
                musicContent
            case "ВИДЕО":
                videoContent
            default:
                defaultContent
            }
        }
    }
    
    private var programmingContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "laptopcomputer")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text("Учись программированию")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                programmingLanguage(language: "🐍 Python")
                programmingLanguage(language: "⚡ JavaScript")
                programmingLanguage(language: "☕ Java")
            }
        }
    }
    
    private func programmingLanguage(language: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(language)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var socialMediaContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "person.3.fill")
                .font(.system(size: 80))
                .foregroundColor(.purple)
            
            Text("Общайся безопасно")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                socialButton(title: "💬 Чат с друзьями")
                socialButton(title: "📷 Фото и видео")
                socialButton(title: "🎮 Игры вместе")
            }
        }
    }
    
    private func socialButton(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.purple)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var musicContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "music.note.list")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text("Твоя музыка")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                musicGenre(genre: "🎸 Рок")
                musicGenre(genre: "🎤 Поп")
                musicGenre(genre: "🎹 Электронная")
            }
        }
    }
    
    private func musicGenre(genre: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(genre)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.orange)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var videoContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "play.rectangle.fill")
                .font(.system(size: 80))
                .foregroundColor(.red)
            
            Text("Интересные видео")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                videoCategory(category: "📺 Развлечения")
                videoCategory(category: "🎓 Обучение")
                videoCategory(category: "🎮 Игры")
            }
        }
    }
    
    private func videoCategory(category: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(category)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.red)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Young Adult Content (18-22 лет)
    
    private var youngAdultContent: some View {
        VStack(spacing: 16) {
            switch category {
            case "ОБРАЗОВАНИЕ":
                educationContent
            case "КАРЬЕРА":
                careerContent
            case "ИНТЕРНЕТ":
                internetContent
            case "КИНО":
                cinemaContent
            default:
                defaultContent
            }
        }
    }
    
    private var educationContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "graduationcap.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            Text("Развивайся и учись")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                courseItem(title: "🎓 Онлайн-курсы")
                courseItem(title: "📚 Книги")
                courseItem(title: "🎯 Навыки")
            }
        }
    }
    
    private func courseItem(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.blue)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var careerContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "briefcase.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)
            
            Text("Строй карьеру")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                careerOption(title: "💼 Вакансии")
                careerOption(title: "📈 Развитие")
                careerOption(title: "🤝 Сеть контактов")
            }
        }
    }
    
    private func careerOption(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.green)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var internetContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "globe")
                .font(.system(size: 80))
                .foregroundColor(.purple)
            
            Text("Изучай мир онлайн")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                webResource(title: "🌐 Полезные сайты")
                webResource(title: "📰 Новости")
                webResource(title: "🔍 Поиск информации")
            }
        }
    }
    
    private func webResource(title: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.purple)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var cinemaContent: some View {
        VStack(spacing: 20) {
            Image(systemName: "film.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text("Смотри и наслаждайся")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                movieCategory(category: "🎬 Фильмы")
                movieCategory(category: "📺 Сериалы")
                movieCategory(category: "🎭 Документалистика")
            }
        }
    }
    
    private func movieCategory(category: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        }) {
            HStack {
                Text(category)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.orange)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Additional Info Section
    
    private var additionalInfoSection: some View {
        VStack(spacing: 12) {
            Text("💡 Совет дня")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white.opacity(0.8))
            
            Text(dailyTip)
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.7))
                .multilineTextAlignment(.center)
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.white.opacity(0.1))
                )
        }
        .padding(.top, 20)
        .padding(.bottom, 32)
    }
    
    private var dailyTip: String {
        switch ageGroup {
        case .kids:
            return "Играй и учись каждый день! Это поможет тебе стать умнее и счастливее!"
        case .school:
            return "Не забывай делать перерывы! Отдых так же важен, как и учёба!"
        case .teen:
            return "Помни о безопасности в интернете. Доверяй, но проверяй!"
        case .youngAdult:
            return "Инвестируй в себя! Каждый день развивай новые навыки!"
        }
    }
    
    // MARK: - Default Content
    
    private var defaultContent: some View {
        VStack(spacing: 20) {
            Text("🌟")
                .font(.system(size: 80))
            
            Text("Контент скоро появится!")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
        }
    }
}

// MARK: - Preview

struct ChildContentScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildContentScreen(
            category: "ИГРУШКИ",
            ageGroup: .kids
        )
        .environmentObject(NavigationManager())
    }
}

import SwiftUI

/// 👶 Child Interface Screen
/// Детский интерфейс - упрощённый экран для детей
/// Источник дизайна: /mobile/wireframes/06_child_interface.html
struct ChildInterfaceScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var selectedTab: Int = 0
    @State private var selectedAge: AgeGroup = .school
    @State private var showChildRewards: Bool = false
    @State private var selectedCategory: String = ""
    @State private var showingContent: Bool = false
    @State private var showImagePicker: Bool = false
    @State private var selectedImage: UIImage?
    @State private var showChildInstructions: Bool = false
    @State private var showChildSettings: Bool = false
    
    // MARK: - Navigation Function
    
    private func navigateToContent(category: String) {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        selectedCategory = category
        showingContent = true
    }
    
    enum AgeGroup {
        case kids, school, teen, youngAdult
        
        var title: String {
            switch self {
            case .kids: return "👶 1-6 лет"
            case .school: return "🎒 7-12 лет"
            case .teen: return "🎓 13-17 лет"
            case .youngAdult: return "🎓 18-22 лет"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (более яркий для детей)
            LinearGradient(
                colors: [
                    Color.blue,
                    Color.blue.opacity(0.8),
                    Color.blue.opacity(0.6)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Яркий фон детского интерфейса")
            
            VStack(spacing: 0) {
                // Простая навигация для детей
                childHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 16) {
                        // Приветствие
                        greetingCard
                        
                        // НОВОЕ: Возрастные табы
                        ageTabs
                        
                        // 🦄 Мои единороги
                        unicornBalanceCard
                        
                        // Большие кнопки для детей
                        bigButtonsGrid
                        
                        // Время экрана
                        screenTimeCard
                        
                        // Адаптивный отступ (Apple HIG)
                        Spacer(minLength: 0)
                            .frame(maxHeight: 32)
                    }
                    .padding(.top, 16)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое детского интерфейса")
            }
        }
        .sheet(isPresented: $showingContent) {
            if !selectedCategory.isEmpty {
                ChildContentScreen(
                    category: selectedCategory,
                    ageGroup: selectedAge
                )
                .environmentObject(navigationManager)
            }
        }
        .sheet(isPresented: $showImagePicker) {
            ProfileImagePicker(selectedImage: $selectedImage)
        }
        .sheet(isPresented: $showChildInstructions) {
            ChildSafetyInstructionsModal(isPresented: $showChildInstructions)
        }
        .sheet(isPresented: $showChildSettings) {
            ChildSettingsModal(isPresented: $showChildSettings)
        }
    }
    
    // MARK: - Child Header
    
    private var childHeader: some View {
        HStack(spacing: 12) {
            // Кнопка назад
            Button(action: {
                print("🔍 DEBUG: Кнопка 'Назад' нажата в ChildInterfaceScreen")
                navigationManager.goBack()
                print("🔍 DEBUG: NavigationManager.goBack() вызван")
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.blue.opacity(0.2))
                    )
            }
            .accessibilityLabel("Назад")
            
            // Аватар с возможностью загрузки фото
            Button(action: {
                showImagePicker = true
            }) {
                ZStack {
                    if let selectedImage = selectedImage {
                        Image(uiImage: selectedImage)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 80, height: 80)
                            .clipShape(Circle())
                    } else {
                        Text("👧")
                            .font(.system(size: 50))
                            .frame(width: 80, height: 80)
                            .background(
                                Circle()
                                    .fill(Color.white.opacity(0.2))
                            )
                    }
                    
                    // Иконка камеры
                    VStack {
                        Spacer()
                        HStack {
                            Spacer()
                            Circle()
                                .fill(Color.secondaryGold)
                                .frame(width: 22, height: 22)
                                .overlay(
                                    Image(systemName: "camera.fill")
                                        .font(.system(size: 11))
                                        .foregroundColor(.white)
                                )
                                .offset(x: 3, y: 3)
                        }
                    }
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            // Приветствие
            VStack(alignment: .leading, spacing: 2) {
                Text("Привет, Маша!")
                    .font(.title)
                    .foregroundColor(.white)
                
                Text("Ты под защитой 🛡️")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))
            }
            
            Spacer()
            
            // Кнопка настроек
            Button(action: {
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
                showChildSettings = true
            }) {
                Image(systemName: "gearshape.fill")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.white.opacity(0.2))
                    )
            }
            .accessibilityLabel("Настройки")
        }
        .padding(16)
        .background(
            Color.white.opacity(0.1)
        )
    }
    
    // MARK: - Greeting Card
    
    private var greetingCard: some View {
        VStack(spacing: 12) {
            Text("🎮")
                .font(.system(size: 64))
            
            Text("Что будем делать?")
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text("Выбери занятие")
                .font(.body)
                .foregroundColor(.white.opacity(0.8))
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, 20)
    }
    
    // MARK: - 🦄 Unicorn Balance Card
    
    private var unicornBalanceCard: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            navigationManager.navigateTo(.childRewards)
        }) {
            HStack(spacing: Spacing.m) {
                Text("🦄")
                    .font(.system(size: 40))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Мои единороги")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                    Text("\(getUnicornBalance()) 🦄 накоплено")
                        .font(.captionSmall)
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Spacer()
                
                Image(systemName: "arrow.right.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.white.opacity(0.7))
            }
            .padding(Spacing.l)
            .background(
                LinearGradient(
                    colors: [
                        Color(hex: "A855F7"),
                        Color(hex: "EC4899")
                    ],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(CornerRadius.large)
            .shadow(color: Color(hex: "A855F7").opacity(0.4), radius: 10, x: 0, y: 5)
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func getUnicornBalance() -> Int {
        UserDefaults.standard.integer(forKey: "child_unicorn_balance")
    }
    
    // MARK: - Age Tabs (НОВОЕ!)
    
    private var ageTabs: some View {
        VStack(spacing: 12) {
            Text("🎯 Выбери свой возраст")
                .font(.title2)
                .foregroundColor(.white)
            
            HStack(spacing: 8) {
                ForEach([AgeGroup.kids, .school, .teen, .youngAdult], id: \.self) { age in
                    Button(action: {
                        selectedAge = age
                    }) {
                        Text(age.title)
                            .font(.caption)
                            .fontWeight(selectedAge == age ? .bold : .regular)
                            .foregroundColor(selectedAge == age ? .white : .white.opacity(0.7))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(selectedAge == age ? Color.blue : Color.white.opacity(0.1))
                            )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
        }
        .padding(.horizontal, 20)
    }
    
    // MARK: - Big Buttons Grid
    
    private var bigButtonsGrid: some View {
        VStack(spacing: 12) {
            // Адаптивный контент в зависимости от возраста
            switch selectedAge {
            case .kids:
                // Для малышей 1-6 лет: простые игры
                HStack(spacing: 12) {
                    bigChildButton(icon: "🧸", title: "ИГРУШКИ", color: Color.pink) {
                        navigateToContent(category: "ИГРУШКИ")
                    }
                    bigChildButton(icon: "🎨", title: "РИСОВАНИЕ", color: Color.orange) {
                        navigateToContent(category: "РИСОВАНИЕ")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎵", title: "ПЕСЕНКИ", color: Color.purple) {
                        navigateToContent(category: "ПЕСЕНКИ")
                    }
                    bigChildButton(icon: "📖", title: "СКАЗКИ", color: Color.blue) {
                        navigateToContent(category: "СКАЗКИ")
                    }
                }
            case .school:
                // Для школьников 7-12 лет: учёба и развлечения
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎮", title: "ИГРЫ", color: Color.green) {
                        navigateToContent(category: "ИГРЫ")
                    }
                    bigChildButton(icon: "📚", title: "УЧЁБА", color: Color.blue) {
                        navigateToContent(category: "УЧЁБА")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🛡️", title: "БЕЗОПАСНОСТЬ", color: Color.cyan) {
                        showChildInstructions = true
                    }
                    bigChildButton(icon: "📺", title: "МУЛЬТИКИ", color: Color.red) {
                        navigateToContent(category: "МУЛЬТИКИ")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎨", title: "ТВОРЧЕСТВО", color: Color.orange) {
                        navigateToContent(category: "ТВОРЧЕСТВО")
                    }
                    Spacer()
                }
            case .teen:
                // Для подростков 13-17 лет: развитие и развлечения
                HStack(spacing: 12) {
                    bigChildButton(icon: "🛡️", title: "БЕЗОПАСНОСТЬ", color: Color.cyan) {
                        navigationManager.navigateTo(.securityEducation)
                    }
                    bigChildButton(icon: "💻", title: "ПРОГРАММИРОВАНИЕ", color: Color.blue) {
                        navigateToContent(category: "ПРОГРАММИРОВАНИЕ")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "📱", title: "СОЦИАЛЬНЫЕ СЕТИ", color: Color.purple) {
                        navigateToContent(category: "СОЦИАЛЬНЫЕ СЕТИ")
                    }
                    bigChildButton(icon: "🎵", title: "МУЗЫКА", color: Color.orange) {
                        navigateToContent(category: "МУЗЫКА")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "📺", title: "ВИДЕО", color: Color.red) {
                        navigateToContent(category: "ВИДЕО")
                    }
                    Spacer()
                }
            case .youngAdult:
                // Для молодых взрослых 18-22 лет: образование и карьера
                HStack(spacing: 12) {
                    bigChildButton(icon: "🛡️", title: "БЕЗОПАСНОСТЬ", color: Color.cyan) {
                        navigationManager.navigateTo(.securityEducation)
                    }
                    bigChildButton(icon: "🎓", title: "ОБРАЗОВАНИЕ", color: Color.blue) {
                        navigateToContent(category: "ОБРАЗОВАНИЕ")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "💼", title: "КАРЬЕРА", color: Color.green) {
                        navigateToContent(category: "КАРЬЕРА")
                    }
                    bigChildButton(icon: "🌐", title: "ИНТЕРНЕТ", color: Color.purple) {
                        navigateToContent(category: "ИНТЕРНЕТ")
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎬", title: "КИНО", color: Color.orange) {
                        navigateToContent(category: "КИНО")
                    }
                    Spacer()
                }
            }
        }
        .padding(.horizontal, 20)
    }
    
    private func bigChildButton(icon: String, title: String, color: Color, action: @escaping () -> Void = {}) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            action()
        }) {
            VStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 40))
                
                Text(title)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.white)
                    .lineLimit(2)
                    .minimumScaleFactor(0.8)
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 130)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(color.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color, lineWidth: 3)
                    )
            )
            .shadow(color: color.opacity(0.3), radius: 12, x: 0, y: 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Screen Time Card
    
    private var screenTimeCard: some View {
        VStack(spacing: 12) {
            Text("⏰")
                .font(.system(size: 48))
            
            Text("Осталось времени")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("45 минут")
                .font(.system(size: 40, weight: .bold))
                .foregroundColor(.green)
            
            // Прогресс бар
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.white.opacity(0.2))
                        .frame(height: 12)
                    
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.green)
                        .frame(width: geometry.size.width * 0.25, height: 12)
                }
            }
            .frame(height: 12)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, 20)
    }
}

// MARK: - Preview

// MARK: - Child Safety Instructions Modal

struct ChildSafetyInstructionsModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("🛡️ Правила безопасности")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Защита от мошенников
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🚫 НЕ ВЕРИТЕ звонкам от:")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("• Сотрудников ФСБ, Прокуратуры, Начальства")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("• Банков, Соцсетей, Незнакомцев")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("✅ ПРАВИЛЬНО:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text("• Никогда не называйте пароли\n• Не переводите деньги\n• Не устанавливайте программы\n• Сразу кладите трубку")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Опасные ссылки
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🔗 Опасные ссылки")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("❌ НЕ НАЖИМАЙТЕ на: Ссылки в SMS, WhatsApp, письмах, неизвестные сайты")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("✅ ПРАВИЛЬНО:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text("• Используйте кнопку 'Проверить сайт'\n• Спрашивайте у родителей\n• Проверяйте адрес сайта")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Как пользоваться приложением
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("📱 Как пользоваться приложением")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("📞 Звонки: Нажмите 'ЗВОНОК' для быстрого набора, выберите нужного родственника")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("🛡️ Безопасность: Используйте 'Проверить сайт', включите защиту от мошенников")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("🚨 Экстренная помощь: Нажмите красную кнопку SOS, выберите службу (103, 101, 102)")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Правила для детей
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("👶 Особые правила для детей")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("• Всегда спрашивайте разрешения у родителей\n• Не общайтесь с незнакомцами в интернете\n• Не выкладывайте личные фото\n• Рассказывайте родителям о подозрительных сообщениях")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("🎮 Игры и развлечения:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.purple)
                            .padding(.top, Spacing.s)
                        
                        Text("• Играйте только в разрешенные игры\n• Соблюдайте время экрана\n• Делайте перерывы каждые 30 минут")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

// MARK: - Child Settings Modal

struct ChildSettingsModal: View {
    @Binding var isPresented: Bool
    @State private var fontSize: Double = 18
    @State private var soundEnabled: Bool = true
    @State private var vibrationEnabled: Bool = true
    @State private var showAddPhoneModal: Bool = false
    @State private var showEditContactsModal: Bool = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("⚙️ Мои настройки")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Размер шрифта
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("📝 Размер букв")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text("Маленькие")
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                            
                            Slider(value: $fontSize, in: 14...28, step: 2)
                                .accentColor(.blue)
                            
                            Text("Большие")
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                        }
                        
                        Text("Сейчас: \(Int(fontSize))")
                            .font(.system(size: 16))
                            .foregroundColor(.blue)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Звуки и вибрация
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🔊 Звуки и вибрация")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text("🔊 Звуки")
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $soundEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                        
                        HStack {
                            Text("📳 Вибрация")
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $vibrationEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Моя семья
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("👨‍👩‍👧‍👦 Моя семья")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Button(action: {
                            showAddPhoneModal = true
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                    .foregroundColor(.blue)
                                Text("Добавить номер мамы/папы")
                                    .foregroundColor(.primary)
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color.white)
                            .cornerRadius(CornerRadius.small)
                        }
                        
                        Button(action: {
                            showEditContactsModal = true
                        }) {
                            HStack {
                                Image(systemName: "pencil.circle.fill")
                                    .foregroundColor(.orange)
                                Text("Изменить номера")
                                    .foregroundColor(.primary)
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color.white)
                            .cornerRadius(CornerRadius.small)
                        }
                    }
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Игры и развлечения
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🎮 Игры и развлечения")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Text("• Время игр: 2 часа в день")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("• Перерывы каждые 30 минут")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("• Только разрешенные игры")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
        .sheet(isPresented: $showAddPhoneModal) {
            ChildAddPhoneModal(isPresented: $showAddPhoneModal)
        }
        .sheet(isPresented: $showEditContactsModal) {
            ChildEditContactsModal(isPresented: $showEditContactsModal)
        }
    }
}

// MARK: - Child Add Phone Modal

struct ChildAddPhoneModal: View {
    @Binding var isPresented: Bool
    @State private var contactName: String = ""
    @State private var phoneNumber: String = ""
    @State private var selectedRelation: String = "Мама"
    
    let relations = ["Мама", "Папа", "Бабушка", "Дедушка", "Брат", "Сестра", "Друг", "Другое"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("📞 Добавить номер")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Имя")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField("Введите имя", text: $contactName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Номер телефона")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField("+7 (999) 123-45-67", text: $phoneNumber)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.phonePad)
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Кто это?")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Picker("Кто это?", selection: $selectedRelation) {
                            ForEach(relations, id: \.self) { relation in
                                Text(relation).tag(relation)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(CornerRadius.small)
                    }
                }
                
                Button(action: {
                    isPresented = false
                }) {
                    Text("Сохранить")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(contactName.isEmpty || phoneNumber.isEmpty)
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

// MARK: - Child Edit Contacts Modal

struct ChildEditContactsModal: View {
    @Binding var isPresented: Bool
    @State private var familyContacts: [ChildFamilyContact] = [
        ChildFamilyContact(name: "Мама", phone: "+7 (999) 123-45-67", relation: "Мама"),
        ChildFamilyContact(name: "Папа", phone: "+7 (999) 234-56-78", relation: "Папа"),
        ChildFamilyContact(name: "Бабушка", phone: "+7 (999) 345-67-89", relation: "Бабушка")
    ]
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("📋 Мои контакты")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                ScrollView {
                    LazyVStack(spacing: Spacing.s) {
                        ForEach(familyContacts.indices, id: \.self) { index in
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(familyContacts[index].name)
                                        .font(.system(size: 18, weight: .semibold))
                                        .foregroundColor(.primary)
                                    
                                    Text(familyContacts[index].phone)
                                        .font(.system(size: 16))
                                        .foregroundColor(.secondary)
                                    
                                    Text(familyContacts[index].relation)
                                        .font(.system(size: 14))
                                        .foregroundColor(.blue)
                                }
                                
                                Spacer()
                                
                                Button(action: {
                                    // Логика редактирования
                                }) {
                                    Image(systemName: "pencil")
                                        .foregroundColor(.blue)
                                }
                                
                                Button(action: {
                                    familyContacts.remove(at: index)
                                }) {
                                    Image(systemName: "trash")
                                        .foregroundColor(.red)
                                }
                            }
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(CornerRadius.small)
                        }
                    }
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct ChildFamilyContact: Identifiable {
    let id = UUID()
    var name: String
    var phone: String
    var relation: String
}

#if DEBUG
struct ChildInterfaceScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildInterfaceScreen()
    }
}
#endif


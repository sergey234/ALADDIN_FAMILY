import SwiftUI

/// 👶 Child Interface Screen
/// Детский интерфейс - упрощённый экран для детей
/// Источник дизайна: /mobile/wireframes/06_child_interface.html
struct ChildInterfaceScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
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
        
        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .kids: return localizationManager.localized("child_interface_age_kids")
            case .school: return localizationManager.localized("child_interface_age_school")
            case .teen: return localizationManager.localized("child_interface_age_teen")
            case .youngAdult: return localizationManager.localized("child_interface_age_young_adult")
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
            .accessibilityLabel(localizationManager.localized("child_interface_background"))
            
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
                .accessibilityLabel(localizationManager.localized("child_interface_content"))
            }
        }
        .id("child_interface_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showingContent) {
            if !selectedCategory.isEmpty {
                ChildContentScreen(
                    category: selectedCategory,
                    ageGroup: selectedAge
                )
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
            }
        }
        .sheet(isPresented: $showImagePicker) {
            ProfileImagePicker(selectedImage: $selectedImage)
        }
        .onAppear {
            loadProfileImage()
        }
        .onChange(of: selectedImage) { newImage in
            if let image = newImage {
                saveProfileImage(image)
            }
        }
        .sheet(isPresented: $showChildInstructions) {
            ChildSafetyInstructionsModal(isPresented: $showChildInstructions)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showChildSettings) {
            ChildSettingsModal(isPresented: $showChildSettings)
                .environmentObject(localizationManager)
        }
    }
    
    // MARK: - Child Header
    
    private var childHeader: some View {
        HStack(spacing: 12) {
            // Кнопка назад
            Button(action: {
                // ✅ ПРОСТОЙ ПОДХОД: только dismiss() для NavigationView
                dismiss()
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
            .accessibilityLabel(localizationManager.localized("child_interface_back"))
            
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
                Text(String(format: localizationManager.localized("child_interface_hello"), getUserName()))
                    .font(.title)
                    .foregroundColor(.white)
                
                Text(localizationManager.localized("child_interface_protected"))
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
            .accessibilityLabel(localizationManager.localized("child_interface_settings"))
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
            
            Text(localizationManager.localized("child_interface_what_to_do"))
                .font(.largeTitle)
                .foregroundColor(.white)
            
            Text(localizationManager.localized("child_interface_choose_activity"))
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
                    Text(localizationManager.localized("child_interface_my_unicorns"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                    Text(localizationManager.localized("child_interface_unicorns_saved", getUnicornBalance()))
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
            Text(localizationManager.localized("child_interface_select_age"))
                .font(.title2)
                .foregroundColor(.white)
            
            HStack(spacing: 8) {
                ForEach([AgeGroup.kids, .school, .teen, .youngAdult], id: \.self) { age in
                    Button(action: {
                        selectedAge = age
                    }) {
                        Text(age.title(localizationManager: localizationManager))
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
                    bigChildButton(icon: "🧸", title: localizationManager.localized("child_interface_category_toys"), color: Color.pink) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_toys"))
                    }
                    bigChildButton(icon: "🎨", title: localizationManager.localized("child_interface_category_drawing"), color: Color.orange) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_drawing"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎵", title: localizationManager.localized("child_interface_category_songs"), color: Color.purple) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_songs"))
                    }
                    bigChildButton(icon: "📖", title: localizationManager.localized("child_interface_category_stories"), color: Color.blue) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_stories"))
                    }
                }
            case .school:
                // Для школьников 7-12 лет: учёба и развлечения
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎮", title: localizationManager.localized("child_interface_category_games"), color: Color.green) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_games"))
                    }
                    bigChildButton(icon: "📚", title: localizationManager.localized("child_interface_category_study"), color: Color.blue) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_study"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🛡️", title: localizationManager.localized("child_interface_category_safety"), color: Color.cyan) {
                        showChildInstructions = true
                    }
                    bigChildButton(icon: "📺", title: localizationManager.localized("child_interface_category_cartoons"), color: Color.red) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_cartoons"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎨", title: localizationManager.localized("child_interface_category_creativity"), color: Color.orange) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_creativity"))
                    }
                    Spacer()
                }
            case .teen:
                // Для подростков 13-17 лет: развитие и развлечения
                HStack(spacing: 12) {
                    bigChildButton(icon: "🛡️", title: localizationManager.localized("child_interface_category_safety"), color: Color.cyan) {
                        navigationManager.navigateTo(.securityEducation)
                    }
                    bigChildButton(icon: "💻", title: localizationManager.localized("child_interface_category_programming"), color: Color.blue) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_programming"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "📱", title: localizationManager.localized("child_interface_category_social"), color: Color.purple) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_social"))
                    }
                    bigChildButton(icon: "🎵", title: localizationManager.localized("child_interface_category_music"), color: Color.orange) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_music"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "📺", title: localizationManager.localized("child_interface_category_video"), color: Color.red) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_video"))
                    }
                    Spacer()
                }
            case .youngAdult:
                // Для молодых взрослых 18-22 лет: образование и карьера
                HStack(spacing: 12) {
                    bigChildButton(icon: "🛡️", title: localizationManager.localized("child_interface_category_safety"), color: Color.cyan) {
                        navigationManager.navigateTo(.securityEducation)
                    }
                    bigChildButton(icon: "🎓", title: localizationManager.localized("child_interface_category_education"), color: Color.blue) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_education"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "💼", title: localizationManager.localized("child_interface_category_career"), color: Color.green) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_career"))
                    }
                    bigChildButton(icon: "🌐", title: localizationManager.localized("child_interface_category_internet"), color: Color.purple) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_internet"))
                    }
                }
                HStack(spacing: 12) {
                    bigChildButton(icon: "🎬", title: localizationManager.localized("child_interface_category_movies"), color: Color.orange) {
                        navigateToContent(category: localizationManager.localized("child_interface_category_movies"))
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
            
            Text(localizationManager.localized("child_interface_time_left"))
                .font(.title2)
                .foregroundColor(.white)
            
            Text(localizationManager.localized("child_interface_time_minutes", 45))
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

    // MARK: - User Name Management

    private func getUserName() -> String {
        // Используем UserProfileManager для получения имени пользователя
        // Менеджер автоматически загружает и кеширует профиль
        return UserProfileManager.shared.displayName
    }

    // MARK: - Profile Image Management
    
    private func loadProfileImage() {
        selectedImage = ProfileImageManager.shared.loadProfileImage(for: .child)
    }
    
    private func saveProfileImage(_ image: UIImage) {
        _ = ProfileImageManager.shared.saveProfileImage(image, for: .child)
    }
}

// MARK: - Preview

// MARK: - Child Safety Instructions Modal

struct ChildSafetyInstructionsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text(localizationManager.localized("child_interface_safety_title"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Защита от мошенников
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("child_interface_dont_trust_calls"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("child_interface_dont_trust_authorities"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_dont_trust_services"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_correct"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("child_interface_safety_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Опасные ссылки
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("child_interface_dangerous_links"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("child_interface_dont_click"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_correct_links"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("child_interface_link_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Как пользоваться приложением
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("child_interface_app_usage"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("child_interface_calls_info"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_security_info"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_emergency_info"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Правила для детей
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("child_interface_kids_rules"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("child_interface_kids_rules_text"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_games_title"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.purple)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("child_interface_games_rules"))
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
                    Button(localizationManager.localized("child_interface_done")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("child_font_size") private var fontSize: Double = 18
    @AppStorage("child_sound_enabled") private var soundEnabled: Bool = true
    @AppStorage("child_vibration_enabled") private var vibrationEnabled: Bool = true
    @State private var showAddPhoneModal: Bool = false
    @State private var showEditContactsModal: Bool = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text(localizationManager.localized("child_interface_my_settings"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Размер шрифта
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("child_interface_font_size"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text(localizationManager.localized("child_interface_font_small"))
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                            
                            Slider(value: $fontSize, in: 14...28, step: 2)
                                .accentColor(.blue)
                            
                            Text(localizationManager.localized("child_interface_font_big"))
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                        }
                        
                        Text(localizationManager.localized("child_interface_font_current", Int(fontSize)))
                            .font(.system(size: 16))
                            .foregroundColor(.blue)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Звуки и вибрация
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("child_interface_sound_vibration"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text(localizationManager.localized("child_interface_sounds"))
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $soundEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("child_interface_vibration"))
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
                        Text(localizationManager.localized("child_interface_my_family"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Button(action: {
                            showAddPhoneModal = true
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                    .foregroundColor(.blue)
                                Text(localizationManager.localized("child_interface_add_phone"))
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
                                Text(localizationManager.localized("child_interface_edit_numbers"))
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
                        Text(localizationManager.localized("child_interface_games_entertainment"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("child_interface_game_time"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_breaks"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("child_interface_allowed_games"))
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
                    Button(localizationManager.localized("child_interface_done")) {
                        isPresented = false
                    }
                }
            }
        }
        .sheet(isPresented: $showAddPhoneModal) {
            ChildAddPhoneModal(isPresented: $showAddPhoneModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEditContactsModal) {
            ChildEditContactsModal(isPresented: $showEditContactsModal)
                .environmentObject(localizationManager)
        }
    }
}

// MARK: - Child Add Phone Modal

struct ChildAddPhoneModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var contactName: String = ""
    @State private var phoneNumber: String = ""
    @State private var selectedRelation: String = ""
    
    var relations: [String] {
        [
            localizationManager.localized("child_interface_relation_mom"),
            localizationManager.localized("child_interface_relation_dad"),
            localizationManager.localized("child_interface_relation_grandma"),
            localizationManager.localized("child_interface_relation_grandpa"),
            localizationManager.localized("child_interface_relation_brother"),
            localizationManager.localized("child_interface_relation_sister"),
            localizationManager.localized("child_interface_relation_friend"),
            localizationManager.localized("child_interface_relation_other")
        ]
    }
    
    init(isPresented: Binding<Bool>) {
        self._isPresented = isPresented
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("child_interface_add_number"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("child_interface_name"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField(localizationManager.localized("child_interface_enter_name"), text: $contactName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("child_interface_phone_number"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField("+7 (999) 123-45-67", text: $phoneNumber)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.phonePad)
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("child_interface_who_is"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Picker(localizationManager.localized("child_interface_who_is"), selection: $selectedRelation) {
                            ForEach(relations, id: \.self) { relation in
                                Text(relation).tag(relation)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(CornerRadius.small)
                        .onAppear {
                            if selectedRelation.isEmpty {
                                selectedRelation = relations.first ?? ""
                            }
                        }
                    }
                }
                
                Button(action: {
                    isPresented = false
                }) {
                    Text(localizationManager.localized("child_interface_save"))
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
                    Button(localizationManager.localized("child_interface_cancel")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var familyContacts: [ChildFamilyContact] = []
    @State private var editingContact: ChildFamilyContact?
    @State private var editingContactIndex: Int?
    @State private var showDeleteAlert: Bool = false
    @State private var contactToDelete: Int?
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("child_interface_my_contacts"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                if familyContacts.isEmpty {
                    EmptyStateView(
                        icon: "📞",
                        title: localizationManager.localized("child_interface_no_contacts"),
                        description: localizationManager.localized("child_interface_ask_parents"),
                        actionTitle: nil,
                        action: nil
                    )
                    .padding()
                } else {
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
                                        editingContact = familyContacts[index]
                                        editingContactIndex = index
                                    }) {
                                        Image(systemName: "pencil")
                                            .foregroundColor(.blue)
                                    }
                                    
                                    Button(action: {
                                        contactToDelete = index
                                        showDeleteAlert = true
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
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("child_interface_cancel")) {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("child_interface_done")) {
                        saveContacts() // Сохраняем перед закрытием
                        isPresented = false
                    }
                }
            }
        }
        .onAppear {
            // ✅ КРИТИЧНО: Устанавливаем роль ребёнка при входе в экран
            // ДОЛЖНО БЫТЬ В САМОМ НАЧАЛЕ .onAppear!
            UserDefaults.standard.set("child", forKey: "current_user_role")
            UserDefaults.standard.synchronize() // Принудительная синхронизация
            print("✅ ChildInterfaceScreen: Роль установлена как 'child'")
            print("   Проверка: UserDefaults['current_user_role'] = '\(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")'")
            
            loadContacts()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadContacts() // Синхронизируем при изменении family_members_list
        }
        .sheet(item: $editingContact) { contact in
            ChildEditContactModal(
                contact: contact,
                contactIndex: editingContactIndex,
                isPresented: Binding(
                    get: { editingContact != nil },
                    set: { if !$0 { editingContact = nil } }
                ),
                onSave: { updatedContact, index in
                    if let index = index {
                        familyContacts[index] = updatedContact
                        saveContacts()
                    }
                }
            )
            .environmentObject(localizationManager)
        }
        .alert(localizationManager.localized("child_contact_delete_confirmation"), isPresented: $showDeleteAlert) {
            Button(localizationManager.localized("child_interface_cancel"), role: .cancel) {
                contactToDelete = nil
            }
            Button(localizationManager.localized("child_contact_edit_delete"), role: .destructive) {
                if let index = contactToDelete {
                    familyContacts.remove(at: index)
                    saveContacts()
                }
                contactToDelete = nil
            }
        }
    }
    
    // MARK: - Data Loading and Saving
    
    private func loadContacts() {
        // Сначала пытаемся загрузить из child_family_contacts_list (сохраненные изменения)
        if let savedContactsData = UserDefaults.standard.data(forKey: "child_family_contacts_list"),
           let savedContacts = try? JSONDecoder().decode([ChildFamilyContact].self, from: savedContactsData) {
            familyContacts = savedContacts
            print("✅ Загружено контактов из child_family_contacts_list: \(familyContacts.count)")
            return
        }
        
        // Если нет сохраненных контактов, загружаем из family_members_list и преобразуем в ChildFamilyContact
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            familyContacts = []
            print("⚠️ Нет данных о членах семьи в UserDefaults")
            return
        }
        
        // Преобразуем FamilyMemberData в ChildFamilyContact
        familyContacts = decoded.map { member in
            // Определяем роль (преобразуем FamilyMemberCard.FamilyRole в строку)
            let relationString: String
            switch member.role {
            case .parent: relationString = localizationManager.localized("elderly_family_role_parent")
            case .child: relationString = localizationManager.localized("elderly_family_role_child")
            case .teenager: relationString = localizationManager.localized("elderly_family_role_teenager")
            case .elderly: relationString = localizationManager.localized("family_role_elderly_label")
            }
            
            return ChildFamilyContact(
                name: member.name,
                phone: "+7 (999) 000-00-00", // TODO: Добавить телефон в FamilyMemberData
                relation: relationString
            )
        }
        
        print("✅ Загружено контактов из family_members_list: \(familyContacts.count)")
    }
    
    private func saveContacts() {
        // Сохраняем в child_family_contacts_list для синхронизации
        guard let encoded = try? JSONEncoder().encode(familyContacts) else {
            print("❌ Ошибка кодирования контактов")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: "child_family_contacts_list")
        UserDefaults.standard.synchronize() // Принудительная синхронизация
        print("✅ Сохранено контактов: \(familyContacts.count) в child_family_contacts_list")
        
        // Уведомляем другие экраны об изменении
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
}
// MARK: - Child Edit Contact Modal

struct ChildEditContactModal: View {
    let contact: ChildFamilyContact
    let contactIndex: Int?
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var name: String
    @State private var phone: String
    @State private var relation: String
    
    var onSave: (ChildFamilyContact, Int?) -> Void
    
    init(contact: ChildFamilyContact, contactIndex: Int?, isPresented: Binding<Bool>, onSave: @escaping (ChildFamilyContact, Int?) -> Void) {
        self.contact = contact
        self.contactIndex = contactIndex
        _isPresented = isPresented
        _name = State(initialValue: contact.name)
        _phone = State(initialValue: contact.phone)
        _relation = State(initialValue: contact.relation)
        self.onSave = onSave
    }
    
    var relations: [String] {
        [
            localizationManager.localized("child_interface_relation_mom"),
            localizationManager.localized("child_interface_relation_dad"),
            localizationManager.localized("child_interface_relation_grandma"),
            localizationManager.localized("child_interface_relation_grandpa"),
            localizationManager.localized("child_interface_relation_brother"),
            localizationManager.localized("child_interface_relation_sister"),
            localizationManager.localized("child_interface_relation_friend"),
            localizationManager.localized("child_interface_relation_other")
        ]
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(localizationManager.localized("child_contact_edit_name"))) {
                    TextField(localizationManager.localized("child_interface_enter_name"), text: $name)
                }
                
                Section(header: Text(localizationManager.localized("child_contact_edit_phone"))) {
                    TextField("+7 (999) 123-45-67", text: $phone)
                        .keyboardType(.phonePad)
                }
                
                Section(header: Text(localizationManager.localized("child_contact_edit_relation"))) {
                    Picker(localizationManager.localized("child_interface_who_is"), selection: $relation) {
                        ForEach(relations, id: \.self) { rel in
                            Text(rel).tag(rel)
                        }
                    }
                    .pickerStyle(MenuPickerStyle())
                }
            }
            .navigationTitle(localizationManager.localized("child_contact_edit_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("child_interface_cancel")) {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("child_contact_edit_save")) {
                        let updatedContact = ChildFamilyContact(id: contact.id, name: name, phone: phone, relation: relation)
                        onSave(updatedContact, contactIndex)
                        isPresented = false
                    }
                }
            }
        }
    }
}


#if DEBUG
struct ChildInterfaceScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildInterfaceScreen()
    }
}
#endif


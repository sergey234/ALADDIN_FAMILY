# 📚 ALADDIN Mobile App - Information Sections Mobile Adaptation

**Эксперт:** Content Manager + Mobile Developer  
**Дата:** 2025-01-27  
**Цель:** Адаптация информационных разделов из MOBILE_APP_INFO_SECTIONS.md для мобильного приложения

---

## 🎯 **ОБЩАЯ СТРУКТУРА МОБИЛЬНОЙ ИНФОРМАЦИИ**

### 📱 **ПРИНЦИПЫ АДАПТАЦИИ:**
- **Progressive Disclosure** - постепенное раскрытие информации
- **Contextual Help** - помощь в контексте
- **Personalization** - персонализация по ролям
- **Smart Filtering** - умная фильтрация контента
- **Quick Access** - быстрый доступ к важному

### 🎨 **ДИЗАЙН ПРИНЦИПЫ:**
- **Карточный интерфейс** - информация в карточках
- **Иконки и эмодзи** - визуальное восприятие
- **Краткие описания** - без лишних слов
- **Интерактивность** - кликабельные элементы
- **Адаптивность** - под разные экраны

---

## 🍎 **iOS ИНФОРМАЦИОННЫЕ РАЗДЕЛЫ**

### 📋 **1. InformationViewController.swift:**
```swift
import UIKit
import Combine

// MARK: - Information View Controller
class InformationViewController: UIViewController {
    
    // MARK: - UI Elements
    private lazy var searchBar: UISearchBar = {
        let searchBar = UISearchBar()
        searchBar.placeholder = "Поиск по базе знаний..."
        searchBar.searchBarStyle = .minimal
        searchBar.delegate = self
        searchBar.translatesAutoresizingMaskIntoConstraints = false
        return searchBar
    }()
    
    private lazy var categoriesCollectionView: UICollectionView = {
        let layout = UICollectionViewFlowLayout()
        layout.scrollDirection = .horizontal
        layout.estimatedItemSize = UICollectionViewFlowLayout.automaticSize
        
        let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.backgroundColor = .clear
        collectionView.showsHorizontalScrollIndicator = false
        collectionView.register(InformationCategoryCell.self, forCellWithReuseIdentifier: "InformationCategoryCell")
        collectionView.delegate = self
        collectionView.dataSource = self
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        return collectionView
    }()
    
    private lazy var contentTableView: UITableView = {
        let tableView = UITableView()
        tableView.backgroundColor = .clear
        tableView.separatorStyle = .none
        tableView.register(InformationItemCell.self, forCellReuseIdentifier: "InformationItemCell")
        tableView.delegate = self
        tableView.dataSource = self
        tableView.translatesAutoresizingMaskIntoConstraints = false
        return tableView
    }()
    
    // MARK: - Properties
    private let informationManager = InformationManager.shared
    private var cancellables = Set<AnyCancellable>()
    private var filteredItems: [InformationItem] = []
    private var selectedCategory: InformationCategory = .all
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupGradientBackground()
        bindViewModel()
        loadInformation()
    }
    
    // MARK: - Setup
    private func setupUI() {
        title = "📚 Информация"
        navigationController?.navigationBar.prefersLargeTitles = true
        
        view.addSubview(searchBar)
        view.addSubview(categoriesCollectionView)
        view.addSubview(contentTableView)
        
        setupConstraints()
    }
    
    private func setupGradientBackground() {
        GradientUtils.applyGradientBackground(
            to: view,
            colors: StormSkyColors.backgroundGradient
        )
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Search Bar
            searchBar.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            searchBar.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            searchBar.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Categories Collection
            categoriesCollectionView.topAnchor.constraint(equalTo: searchBar.bottomAnchor, constant: 20),
            categoriesCollectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            categoriesCollectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            categoriesCollectionView.heightAnchor.constraint(equalToConstant: 50),
            
            // Content Table
            contentTableView.topAnchor.constraint(equalTo: categoriesCollectionView.bottomAnchor, constant: 20),
            contentTableView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            contentTableView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            contentTableView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20)
        ])
    }
    
    private func bindViewModel() {
        informationManager.$items
            .receive(on: DispatchQueue.main)
            .sink { [weak self] items in
                self?.filterContent()
            }
            .store(in: &cancellables)
    }
    
    private func loadInformation() {
        Task {
            await informationManager.loadInformation()
        }
    }
    
    private func filterContent() {
        let items = informationManager.items
        
        if selectedCategory == .all {
            filteredItems = items
        } else {
            filteredItems = items.filter { $0.category == selectedCategory }
        }
        
        contentTableView.reloadData()
    }
}

// MARK: - UISearchBarDelegate
extension InformationViewController: UISearchBarDelegate {
    func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
        if searchText.isEmpty {
            filterContent()
        } else {
            filteredItems = informationManager.items.filter { item in
                item.title.localizedCaseInsensitiveContains(searchText) ||
                item.content.localizedCaseInsensitiveContains(searchText)
            }
            contentTableView.reloadData()
        }
    }
}

// MARK: - UICollectionViewDataSource
extension InformationViewController: UICollectionViewDataSource {
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        return InformationCategory.allCases.count
    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "InformationCategoryCell", for: indexPath) as! InformationCategoryCell
        let category = InformationCategory.allCases[indexPath.row]
        cell.configure(with: category, isSelected: category == selectedCategory)
        return cell
    }
}

// MARK: - UICollectionViewDelegate
extension InformationViewController: UICollectionViewDelegate {
    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        selectedCategory = InformationCategory.allCases[indexPath.row]
        collectionView.reloadData()
        filterContent()
    }
}

// MARK: - UITableViewDataSource
extension InformationViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return filteredItems.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "InformationItemCell", for: indexPath) as! InformationItemCell
        cell.configure(with: filteredItems[indexPath.row])
        return cell
    }
}

// MARK: - UITableViewDelegate
extension InformationViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let item = filteredItems[indexPath.row]
        let detailVC = InformationDetailViewController(item: item)
        navigationController?.pushViewController(detailVC, animated: true)
    }
}
```

### 📋 **2. InformationManager.swift:**
```swift
import Foundation
import Combine

// MARK: - Information Manager
class InformationManager: ObservableObject {
    static let shared = InformationManager()
    
    @Published var items: [InformationItem] = []
    @Published var categories: [InformationCategory] = []
    @Published var isLoading = false
    
    private init() {
        loadInformation()
    }
    
    func loadInformation() async {
        await MainActor.run {
            isLoading = true
        }
        
        // Load information from local data
        let informationData = InformationDataProvider.shared.getInformationData()
        
        await MainActor.run {
            items = informationData
            categories = InformationCategory.allCases
            isLoading = false
        }
    }
    
    func searchItems(query: String) -> [InformationItem] {
        return items.filter { item in
            item.title.localizedCaseInsensitiveContains(query) ||
            item.content.localizedCaseInsensitiveContains(query) ||
            item.tags.contains { $0.localizedCaseInsensitiveContains(query) }
        }
    }
    
    func getItemsForCategory(_ category: InformationCategory) -> [InformationItem] {
        if category == .all {
            return items
        }
        return items.filter { $0.category == category }
    }
}

// MARK: - Information Item Model
struct InformationItem: Identifiable, Codable {
    let id: String
    let title: String
    let content: String
    let category: InformationCategory
    let icon: String
    let tags: [String]
    let priority: InformationPriority
    let lastUpdated: Date
    let relatedItems: [String]
    
    init(id: String = UUID().uuidString, title: String, content: String, category: InformationCategory, icon: String, tags: [String] = [], priority: InformationPriority = .medium, lastUpdated: Date = Date(), relatedItems: [String] = []) {
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.icon = icon
        self.tags = tags
        self.priority = priority
        self.lastUpdated = lastUpdated
        self.relatedItems = relatedItems
    }
}

// MARK: - Information Category
enum InformationCategory: String, CaseIterable, Codable {
    case all = "all"
    case systemStats = "system_stats"
    case protectionGuides = "protection_guides"
    case faq = "faq"
    case threatProtection = "threat_protection"
    case ageGroups = "age_groups"
    case gamification = "gamification"
    case tariffPlans = "tariff_plans"
    case contacts = "contacts"
    case aiAssistant = "ai_assistant"
    case technicalSupport = "technical_support"
    
    var displayName: String {
        switch self {
        case .all:
            return "Все"
        case .systemStats:
            return "Статистика"
        case .protectionGuides:
            return "Руководства"
        case .faq:
            return "FAQ"
        case .threatProtection:
            return "Защита"
        case .ageGroups:
            return "Возрасты"
        case .gamification:
            return "Игры"
        case .tariffPlans:
            return "Тарифы"
        case .contacts:
            return "Контакты"
        case .aiAssistant:
            return "AI Помощник"
        case .technicalSupport:
            return "Поддержка"
        }
    }
    
    var iconName: String {
        switch self {
        case .all:
            return "list.bullet"
        case .systemStats:
            return "chart.bar"
        case .protectionGuides:
            return "book"
        case .faq:
            return "questionmark.circle"
        case .threatProtection:
            return "shield"
        case .ageGroups:
            return "person.3"
        case .gamification:
            return "gamecontroller"
        case .tariffPlans:
            return "creditcard"
        case .contacts:
            return "phone"
        case .aiAssistant:
            return "brain.head.profile"
        case .technicalSupport:
            return "wrench"
        }
    }
}

// MARK: - Information Priority
enum InformationPriority: String, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
    
    var color: UIColor {
        switch self {
        case .low:
            return StormSkyColors.lightningBlue
        case .medium:
            return StormSkyColors.goldMain
        case .high:
            return StormSkyColors.warningYellow
        case .critical:
            return StormSkyColors.errorRed
        }
    }
}
```

### 📋 **3. InformationDataProvider.swift:**
```swift
import Foundation

// MARK: - Information Data Provider
class InformationDataProvider {
    static let shared = InformationDataProvider()
    
    private init() {}
    
    func getInformationData() -> [InformationItem] {
        return [
            // System Statistics
            InformationItem(
                title: "🛡️ Общая статистика системы",
                content: "26 модулей семейной безопасности • 44 файла с 28,993 строками кода • 100+ типов угроз под защитой • 5 возрастных групп • 6 ролей",
                category: .systemStats,
                icon: "chart.bar.fill",
                tags: ["статистика", "модули", "защита"],
                priority: .high
            ),
            
            // Protection Guides
            InformationItem(
                title: "🎮 Родительский контроль",
                content: "Ваш цифровой помощник для защиты детей в интернете. Контроль времени, фильтрация контента, управление приложениями, отслеживание местоположения.",
                category: .protectionGuides,
                icon: "person.3.fill",
                tags: ["родители", "дети", "контроль"],
                priority: .high
            ),
            
            InformationItem(
                title: "🔒 VPN защита",
                content: "Защищает ваши данные в интернете, скрывает IP-адрес, блокирует рекламу и трекеры, обеспечивает безопасность в общественных сетях.",
                category: .protectionGuides,
                icon: "shield.lefthalf.filled",
                tags: ["vpn", "интернет", "безопасность"],
                priority: .high
            ),
            
            InformationItem(
                title: "🤖 AI помощник",
                content: "Умный помощник, который отвечает на вопросы, помогает с настройками, объясняет функции системы и дает советы по безопасности.",
                category: .protectionGuides,
                icon: "brain.head.profile",
                tags: ["ai", "помощник", "чат"],
                priority: .medium
            ),
            
            // FAQ
            InformationItem(
                title: "❓ Как настроить родительский контроль?",
                content: "1. Откройте раздел 'Семья' 2. Выберите ребенка 3. Настройте ограничения по времени 4. Выберите разрешенные приложения 5. Включите фильтрацию контента",
                category: .faq,
                icon: "questionmark.circle.fill",
                tags: ["faq", "настройка", "родители"],
                priority: .high
            ),
            
            InformationItem(
                title: "❓ Что такое VPN и зачем он нужен?",
                content: "VPN (Virtual Private Network) - это виртуальная частная сеть, которая шифрует ваше интернет-соединение и скрывает вашу активность от посторонних глаз.",
                category: .faq,
                icon: "questionmark.circle.fill",
                tags: ["faq", "vpn", "безопасность"],
                priority: .medium
            ),
            
            InformationItem(
                title: "❓ Как работает AI помощник?",
                content: "AI помощник использует искусственный интеллект для понимания ваших вопросов и предоставления точных ответов. Он обучается на ваших предпочтениях и становится умнее со временем.",
                category: .faq,
                icon: "questionmark.circle.fill",
                tags: ["faq", "ai", "помощник"],
                priority: .medium
            ),
            
            // Threat Protection
            InformationItem(
                title: "🚫 Защита от мошенничества",
                content: "Система блокирует подозрительные звонки, SMS, сайты и приложения. Анализирует поведение и предупреждает о потенциальных угрозах.",
                category: .threatProtection,
                icon: "exclamationmark.triangle.fill",
                tags: ["мошенничество", "звонки", "блокировка"],
                priority: .critical
            ),
            
            InformationItem(
                title: "🛡️ Защита от вирусов",
                content: "Антивирусная защита в реальном времени сканирует файлы, приложения и веб-сайты на наличие вредоносного ПО и блокирует угрозы.",
                category: .threatProtection,
                icon: "ant",
                tags: ["вирусы", "антивирус", "сканирование"],
                priority: .critical
            ),
            
            InformationItem(
                title: "🔍 Защита от фишинга",
                content: "Система распознает поддельные сайты и письма, которые пытаются украсть ваши личные данные, и блокирует их автоматически.",
                category: .threatProtection,
                icon: "fish",
                tags: ["фишинг", "сайты", "данные"],
                priority: .high
            ),
            
            // Age Groups
            InformationItem(
                title: "👶 Дети 1-6 лет",
                content: "Простой интерфейс с большими кнопками, игровые элементы, блокировка всех опасных сайтов, ограничение времени использования.",
                category: .ageGroups,
                icon: "figure.child",
                tags: ["дети", "1-6", "игры"],
                priority: .high
            ),
            
            InformationItem(
                title: "🧒 Дети 7-9 лет",
                content: "Образовательный контент, безопасные игры, родительский контроль, обучение основам безопасности в интернете.",
                category: .ageGroups,
                icon: "figure.child",
                tags: ["дети", "7-9", "образование"],
                priority: .high
            ),
            
            InformationItem(
                title: "👦 Подростки 10-13 лет",
                content: "Расширенные настройки, социальные сети под контролем, обучение кибербезопасности, мониторинг активности.",
                category: .ageGroups,
                icon: "figure.and.child.holdinghands",
                tags: ["подростки", "10-13", "соцсети"],
                priority: .high
            ),
            
            InformationItem(
                title: "👨‍🎓 Молодежь 14-18 лет",
                content: "Полная функциональность, настройка уведомлений, обучение работе с AI, подготовка к взрослой жизни.",
                category: .ageGroups,
                icon: "graduationcap",
                tags: ["молодежь", "14-18", "обучение"],
                priority: .medium
            ),
            
            InformationItem(
                title: "👴 Пожилые люди 50+ лет",
                content: "Упрощенный интерфейс, крупные шрифты, голосовое управление, защита от мошенников, экстренные контакты.",
                category: .ageGroups,
                icon: "figure.walk",
                tags: ["пожилые", "50+", "простота"],
                priority: .high
            ),
            
            // Gamification
            InformationItem(
                title: "🏆 Система достижений",
                content: "Зарабатывайте очки за изучение безопасности, получайте награды за правильное поведение, соревнуйтесь с семьей.",
                category: .gamification,
                icon: "trophy.fill",
                tags: ["достижения", "очки", "награды"],
                priority: .medium
            ),
            
            InformationItem(
                title: "🎮 Обучающие игры",
                content: "Игры по кибербезопасности, квесты по безопасности, викторины, интерактивные уроки для всех возрастов.",
                category: .gamification,
                icon: "gamecontroller.fill",
                tags: ["игры", "обучение", "квесты"],
                priority: .medium
            ),
            
            // Tariff Plans
            InformationItem(
                title: "🆓 Freemium - 0₽/месяц",
                content: "Базовые функции безопасности, ограниченная защита, 1 устройство, поддержка по email.",
                category: .tariffPlans,
                icon: "gift.fill",
                tags: ["бесплатно", "базовый", "1 устройство"],
                priority: .low
            ),
            
            InformationItem(
                title: "💎 Basic - 290₽/месяц",
                content: "Полная защита, 3 устройства, родительский контроль, VPN, поддержка 24/7.",
                category: .tariffPlans,
                icon: "diamond.fill",
                tags: ["базовый", "3 устройства", "vpn"],
                priority: .medium
            ),
            
            InformationItem(
                title: "👨‍👩‍👧‍👦 Family - 490₽/месяц",
                content: "Все функции Basic + до 6 устройств, AI помощник, расширенная аналитика, приоритетная поддержка.",
                category: .tariffPlans,
                icon: "person.3.fill",
                tags: ["семья", "6 устройств", "ai"],
                priority: .high
            ),
            
            InformationItem(
                title: "⭐ Premium - 900₽/месяц",
                content: "Все функции Family + неограниченные устройства, персональный менеджер, кастомные настройки, белый лейбл.",
                category: .tariffPlans,
                icon: "star.fill",
                tags: ["премиум", "неограниченно", "менеджер"],
                priority: .high
            ),
            
            // Contacts
            InformationItem(
                title: "📞 Техническая поддержка",
                content: "8 (800) 555-0123 • support@aladdin-security.com • Онлайн-чат 24/7 • Ответ в течение 5 минут",
                category: .contacts,
                icon: "phone.fill",
                tags: ["поддержка", "телефон", "чат"],
                priority: .high
            ),
            
            InformationItem(
                title: "💬 AI Помощник",
                content: "Умный чат-бот, который отвечает на вопросы 24/7, помогает с настройками, объясняет функции системы.",
                category: .aiAssistant,
                icon: "brain.head.profile",
                tags: ["ai", "чат", "помощь"],
                priority: .medium
            ),
            
            InformationItem(
                title: "📧 Email поддержка",
                content: "support@aladdin-security.com • Ответ в течение 2 часов • Приоритет для Premium пользователей",
                category: .technicalSupport,
                icon: "envelope.fill",
                tags: ["email", "поддержка", "ответ"],
                priority: .medium
            )
        ]
    }
}
```

### 📋 **4. InformationCategoryCell.swift:**
```swift
import UIKit

// MARK: - Information Category Cell
class InformationCategoryCell: UICollectionViewCell {
    
    private lazy var containerView: UIView = {
        let view = UIView()
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        view.layer.borderWidth = 1
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private lazy var iconImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private lazy var titleLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.caption
        label.textAlignment = .center
        label.numberOfLines = 1
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        contentView.addSubview(containerView)
        containerView.addSubview(iconImageView)
        containerView.addSubview(titleLabel)
        
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Container View
            containerView.topAnchor.constraint(equalTo: contentView.topAnchor),
            containerView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            containerView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            containerView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor),
            
            // Icon Image View
            iconImageView.topAnchor.constraint(equalTo: containerView.topAnchor, constant: 8),
            iconImageView.centerXAnchor.constraint(equalTo: containerView.centerXAnchor),
            iconImageView.widthAnchor.constraint(equalToConstant: 20),
            iconImageView.heightAnchor.constraint(equalToConstant: 20),
            
            // Title Label
            titleLabel.topAnchor.constraint(equalTo: iconImageView.bottomAnchor, constant: 4),
            titleLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 4),
            titleLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -4),
            titleLabel.bottomAnchor.constraint(equalTo: containerView.bottomAnchor, constant: -8)
        ])
    }
    
    func configure(with category: InformationCategory, isSelected: Bool) {
        titleLabel.text = category.displayName
        iconImageView.image = UIImage(systemName: category.iconName)
        
        if isSelected {
            containerView.backgroundColor = StormSkyColors.goldMain
            containerView.layer.borderColor = StormSkyColors.goldMain.cgColor
            titleLabel.textColor = StormSkyColors.stormSkyDark
            iconImageView.tintColor = StormSkyColors.stormSkyDark
        } else {
            containerView.backgroundColor = StormSkyColors.stormSkyMain80
            containerView.layer.borderColor = StormSkyColors.goldMain30.cgColor
            titleLabel.textColor = StormSkyColors.white
            iconImageView.tintColor = StormSkyColors.goldMain
        }
    }
}
```

### 📋 **5. InformationItemCell.swift:**
```swift
import UIKit

// MARK: - Information Item Cell
class InformationItemCell: UITableViewCell {
    
    private lazy var containerView: UIView = {
        let view = UIView()
        view.backgroundColor = StormSkyColors.stormSkyMain80
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.lg
        view.layer.borderWidth = 1
        view.layer.borderColor = StormSkyColors.goldMain30.cgColor
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private lazy var iconImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.tintColor = StormSkyColors.goldMain
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private lazy var titleLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.h3
        label.textColor = StormSkyColors.white
        label.numberOfLines = 2
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var contentLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.body
        label.textColor = StormSkyColors.lightningBlue
        label.numberOfLines = 3
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var priorityIndicator: UIView = {
        let view = UIView()
        view.layer.cornerRadius = 4
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private lazy var categoryLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.small
        label.textColor = StormSkyColors.goldMain
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        backgroundColor = .clear
        selectionStyle = .none
        
        contentView.addSubview(containerView)
        containerView.addSubview(iconImageView)
        containerView.addSubview(titleLabel)
        containerView.addSubview(contentLabel)
        containerView.addSubview(priorityIndicator)
        containerView.addSubview(categoryLabel)
        
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Container View
            containerView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 8),
            containerView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            containerView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            containerView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -8),
            
            // Icon Image View
            iconImageView.topAnchor.constraint(equalTo: containerView.topAnchor, constant: 16),
            iconImageView.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 16),
            iconImageView.widthAnchor.constraint(equalToConstant: 24),
            iconImageView.heightAnchor.constraint(equalToConstant: 24),
            
            // Priority Indicator
            priorityIndicator.topAnchor.constraint(equalTo: containerView.topAnchor, constant: 16),
            priorityIndicator.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -16),
            priorityIndicator.widthAnchor.constraint(equalToConstant: 8),
            priorityIndicator.heightAnchor.constraint(equalToConstant: 8),
            
            // Title Label
            titleLabel.topAnchor.constraint(equalTo: containerView.topAnchor, constant: 16),
            titleLabel.leadingAnchor.constraint(equalTo: iconImageView.trailingAnchor, constant: 12),
            titleLabel.trailingAnchor.constraint(equalTo: priorityIndicator.leadingAnchor, constant: -8),
            
            // Content Label
            contentLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            contentLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 16),
            contentLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -16),
            
            // Category Label
            categoryLabel.topAnchor.constraint(equalTo: contentLabel.bottomAnchor, constant: 8),
            categoryLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 16),
            categoryLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -16),
            categoryLabel.bottomAnchor.constraint(equalTo: containerView.bottomAnchor, constant: -16)
        ])
    }
    
    func configure(with item: InformationItem) {
        titleLabel.text = item.title
        contentLabel.text = item.content
        categoryLabel.text = item.category.displayName
        iconImageView.image = UIImage(systemName: item.icon)
        
        // Set priority indicator color
        priorityIndicator.backgroundColor = item.priority.color
    }
}
```

---

## 🤖 **ANDROID ИНФОРМАЦИОННЫЕ РАЗДЕЛЫ**

### 📋 **1. InformationActivity.kt:**
```kotlin
package com.aladdin.information

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.aladdin.databinding.ActivityInformationBinding
import com.aladdin.ui.theme.StormSkyTheme

class InformationActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityInformationBinding
    private lateinit var viewModel: InformationViewModel
    private lateinit var categoriesAdapter: InformationCategoriesAdapter
    private lateinit var itemsAdapter: InformationItemsAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityInformationBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        setupViewModel()
        setupRecyclerViews()
        setupSearch()
    }
    
    private fun setupUI() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.title = "📚 Информация"
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        
        // Apply gradient background
        StormSkyTheme.applyTheme(binding.root)
    }
    
    private fun setupViewModel() {
        viewModel = ViewModelProvider(this)[InformationViewModel::class.java]
        
        viewModel.items.observe(this) { items ->
            itemsAdapter.submitList(items)
        }
        
        viewModel.categories.observe(this) { categories ->
            categoriesAdapter.submitList(categories)
        }
    }
    
    private fun setupRecyclerViews() {
        // Categories RecyclerView
        categoriesAdapter = InformationCategoriesAdapter { category ->
            viewModel.selectCategory(category)
        }
        binding.categoriesRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@InformationActivity, LinearLayoutManager.HORIZONTAL, false)
            adapter = categoriesAdapter
        }
        
        // Items RecyclerView
        itemsAdapter = InformationItemsAdapter { item ->
            // Navigate to detail
            val intent = InformationDetailActivity.newIntent(this, item)
            startActivity(intent)
        }
        binding.itemsRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@InformationActivity)
            adapter = itemsAdapter
        }
    }
    
    private fun setupSearch() {
        binding.searchView.setOnQueryTextListener(object : androidx.appcompat.widget.SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean {
                query?.let { viewModel.searchItems(it) }
                return true
            }
            
            override fun onQueryTextChange(newText: String?): Boolean {
                if (newText.isNullOrEmpty()) {
                    viewModel.clearSearch()
                } else {
                    viewModel.searchItems(newText)
                }
                return true
            }
        })
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
```

### 📋 **2. InformationViewModel.kt:**
```kotlin
package com.aladdin.information

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

class InformationViewModel : ViewModel() {
    
    private val _items = MutableLiveData<List<InformationItem>>()
    val items: LiveData<List<InformationItem>> = _items
    
    private val _categories = MutableLiveData<List<InformationCategory>>()
    val categories: LiveData<List<InformationCategory>> = _categories
    
    private val _selectedCategory = MutableLiveData<InformationCategory>()
    val selectedCategory: LiveData<InformationCategory> = _selectedCategory
    
    private val informationRepository = InformationRepository()
    
    init {
        loadInformation()
        loadCategories()
    }
    
    private fun loadInformation() {
        viewModelScope.launch {
            val informationData = informationRepository.getInformationData()
            _items.value = informationData
        }
    }
    
    private fun loadCategories() {
        _categories.value = InformationCategory.values().toList()
        _selectedCategory.value = InformationCategory.ALL
    }
    
    fun selectCategory(category: InformationCategory) {
        _selectedCategory.value = category
        filterItems()
    }
    
    fun searchItems(query: String) {
        val allItems = informationRepository.getInformationData()
        val filteredItems = allItems.filter { item ->
            item.title.contains(query, ignoreCase = true) ||
            item.content.contains(query, ignoreCase = true) ||
            item.tags.any { tag -> tag.contains(query, ignoreCase = true) }
        }
        _items.value = filteredItems
    }
    
    fun clearSearch() {
        filterItems()
    }
    
    private fun filterItems() {
        val allItems = informationRepository.getInformationData()
        val category = _selectedCategory.value ?: InformationCategory.ALL
        
        val filteredItems = if (category == InformationCategory.ALL) {
            allItems
        } else {
            allItems.filter { it.category == category }
        }
        
        _items.value = filteredItems
    }
}

// MARK: - Data Classes
data class InformationItem(
    val id: String,
    val title: String,
    val content: String,
    val category: InformationCategory,
    val icon: String,
    val tags: List<String>,
    val priority: InformationPriority,
    val lastUpdated: Long,
    val relatedItems: List<String>
)

enum class InformationCategory(val displayName: String, val iconName: String) {
    ALL("Все", "list"),
    SYSTEM_STATS("Статистика", "chart_bar"),
    PROTECTION_GUIDES("Руководства", "book"),
    FAQ("FAQ", "help_circle"),
    THREAT_PROTECTION("Защита", "shield"),
    AGE_GROUPS("Возрасты", "people"),
    GAMIFICATION("Игры", "gamepad"),
    TARIFF_PLANS("Тарифы", "credit_card"),
    CONTACTS("Контакты", "phone"),
    AI_ASSISTANT("AI Помощник", "psychology"),
    TECHNICAL_SUPPORT("Поддержка", "build")
}

enum class InformationPriority(val color: Int) {
    LOW(0xFF60A5FA),      // Lightning Blue
    MEDIUM(0xFFF59E0B),   // Gold Main
    HIGH(0xFFFCD34D),     // Warning Yellow
    CRITICAL(0xFFEF4444)  // Error Red
}
```

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Реализовать информационные разделы** в обоих проектах
2. **Создать красивые экраны** с карточками
3. **Добавить поиск и фильтрацию**
4. **Интегрировать с AI помощником**
5. **Протестировать навигацию**
6. **Оптимизировать производительность**

**🎯 ИНФОРМАЦИОННЫЕ РАЗДЕЛЫ ГОТОВЫ К АДАПТАЦИИ!**

**📱 ПЕРЕХОДИМ К СПЕЦИАЛИЗИРОВАННЫМ ИНТЕРФЕЙСАМ!**


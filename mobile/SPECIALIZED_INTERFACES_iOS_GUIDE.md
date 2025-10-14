# 👶 ALADDIN Mobile App - Specialized Interfaces iOS Guide

**Эксперт:** UI/UX Designer + iOS Developer  
**Дата:** 2025-01-27  
**Цель:** Реализация специализированных интерфейсов для iOS (ChildInterfaceManager, ElderlyInterfaceManager, ParentControlPanel)

---

## 🎯 **ОБЩАЯ АРХИТЕКТУРА СПЕЦИАЛИЗИРОВАННЫХ ИНТЕРФЕЙСОВ**

### 👥 **ТИПЫ ПОЛЬЗОВАТЕЛЕЙ:**
1. **👶 Дети (1-18 лет)** - игровой интерфейс с персонажами
2. **👴 Пожилые (50+ лет)** - упрощенный интерфейс с крупными элементами
3. **👨‍👩‍👧‍👦 Родители** - полный функционал с детальным контролем

### 🎨 **ПРИНЦИПЫ ДИЗАЙНА:**
- **Адаптивность** - под разные возрастные группы
- **Доступность** - для людей с ограниченными возможностями
- **Интуитивность** - понятный интерфейс без обучения
- **Безопасность** - защита от случайных действий

---

## 👶 **ДЕТСКИЙ ИНТЕРФЕЙС (ChildInterfaceManager)**

### 📋 **1. ChildInterfaceViewController.swift:**
```swift
import UIKit
import Combine

// MARK: - Child Interface View Controller
class ChildInterfaceViewController: UIViewController {
    
    // MARK: - UI Elements
    private lazy var characterImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private lazy var greetingLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.h1
        label.textColor = StormSkyColors.white
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var levelProgressView: UIProgressView = {
        let progressView = UIProgressView(progressViewStyle: .default)
        progressView.progressTintColor = StormSkyColors.goldMain
        progressView.trackTintColor = StormSkyColors.stormSkyMain80
        progressView.layer.cornerRadius = 4
        progressView.clipsToBounds = true
        progressView.translatesAutoresizingMaskIntoConstraints = false
        return progressView
    }()
    
    private lazy var levelLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.h3
        label.textColor = StormSkyColors.goldMain
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var gamesCollectionView: UICollectionView = {
        let layout = UICollectionViewFlowLayout()
        layout.scrollDirection = .vertical
        layout.estimatedItemSize = CGSize(width: 150, height: 120)
        
        let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.backgroundColor = .clear
        collectionView.register(ChildGameCell.self, forCellWithReuseIdentifier: "ChildGameCell")
        collectionView.delegate = self
        collectionView.dataSource = self
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        return collectionView
    }()
    
    private lazy var achievementsCollectionView: UICollectionView = {
        let layout = UICollectionViewFlowLayout()
        layout.scrollDirection = .horizontal
        layout.estimatedItemSize = CGSize(width: 80, height: 80)
        
        let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.backgroundColor = .clear
        collectionView.showsHorizontalScrollIndicator = false
        collectionView.register(ChildAchievementCell.self, forCellWithReuseIdentifier: "ChildAchievementCell")
        collectionView.delegate = self
        collectionView.dataSource = self
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        return collectionView
    }()
    
    private lazy var charactersCollectionView: UICollectionView = {
        let layout = UICollectionViewFlowLayout()
        layout.scrollDirection = .horizontal
        layout.estimatedItemSize = CGSize(width: 100, height: 100)
        
        let collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.backgroundColor = .clear
        collectionView.showsHorizontalScrollIndicator = false
        collectionView.register(ChildCharacterCell.self, forCellWithReuseIdentifier: "ChildCharacterCell")
        collectionView.delegate = self
        collectionView.dataSource = self
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        return collectionView
    }()
    
    // MARK: - Properties
    private let childManager = ChildInterfaceManager.shared
    private var cancellables = Set<AnyCancellable>()
    private var games: [ChildGame] = []
    private var achievements: [ChildAchievement] = []
    private var characters: [ChildCharacter] = []
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupGradientBackground()
        bindViewModel()
        loadChildData()
    }
    
    // MARK: - Setup
    private func setupUI() {
        title = "🎮 ALADDIN KIDS"
        navigationController?.navigationBar.prefersLargeTitles = true
        
        view.addSubview(characterImageView)
        view.addSubview(greetingLabel)
        view.addSubview(levelProgressView)
        view.addSubview(levelLabel)
        view.addSubview(gamesCollectionView)
        view.addSubview(achievementsCollectionView)
        view.addSubview(charactersCollectionView)
        
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
            // Character Image
            characterImageView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            characterImageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            characterImageView.widthAnchor.constraint(equalToConstant: 100),
            characterImageView.heightAnchor.constraint(equalToConstant: 100),
            
            // Greeting Label
            greetingLabel.topAnchor.constraint(equalTo: characterImageView.bottomAnchor, constant: 20),
            greetingLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            greetingLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Level Progress
            levelProgressView.topAnchor.constraint(equalTo: greetingLabel.bottomAnchor, constant: 20),
            levelProgressView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            levelProgressView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            levelProgressView.heightAnchor.constraint(equalToConstant: 8),
            
            // Level Label
            levelLabel.topAnchor.constraint(equalTo: levelProgressView.bottomAnchor, constant: 8),
            levelLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            levelLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Games Collection
            gamesCollectionView.topAnchor.constraint(equalTo: levelLabel.bottomAnchor, constant: 30),
            gamesCollectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            gamesCollectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            gamesCollectionView.heightAnchor.constraint(equalToConstant: 200),
            
            // Achievements Collection
            achievementsCollectionView.topAnchor.constraint(equalTo: gamesCollectionView.bottomAnchor, constant: 20),
            achievementsCollectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            achievementsCollectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            achievementsCollectionView.heightAnchor.constraint(equalToConstant: 100),
            
            // Characters Collection
            charactersCollectionView.topAnchor.constraint(equalTo: achievementsCollectionView.bottomAnchor, constant: 20),
            charactersCollectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            charactersCollectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            charactersCollectionView.heightAnchor.constraint(equalToConstant: 120)
        ])
    }
    
    private func bindViewModel() {
        childManager.$userProfile
            .receive(on: DispatchQueue.main)
            .sink { [weak self] profile in
                self?.updateUI(with: profile)
            }
            .store(in: &cancellables)
    }
    
    private func loadChildData() {
        games = childManager.getAvailableGames()
        achievements = childManager.getAchievements()
        characters = childManager.getCharacters()
        
        gamesCollectionView.reloadData()
        achievementsCollectionView.reloadData()
        charactersCollectionView.reloadData()
    }
    
    private func updateUI(with profile: ChildUserProfile) {
        greetingLabel.text = "Привет, \(profile.name)!"
        levelLabel.text = "Уровень: \(profile.level) (\(profile.points) очков)"
        levelProgressView.progress = Float(profile.levelProgress) / 100.0
        
        // Update character based on level
        let character = characters.first { $0.minLevel <= profile.level && $0.maxLevel >= profile.level }
        characterImageView.image = UIImage(named: character?.imageName ?? "default_character")
    }
}

// MARK: - UICollectionViewDataSource
extension ChildInterfaceViewController: UICollectionViewDataSource {
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        if collectionView == gamesCollectionView {
            return games.count
        } else if collectionView == achievementsCollectionView {
            return achievements.count
        } else {
            return characters.count
        }
    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        if collectionView == gamesCollectionView {
            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "ChildGameCell", for: indexPath) as! ChildGameCell
            cell.configure(with: games[indexPath.row])
            return cell
        } else if collectionView == achievementsCollectionView {
            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "ChildAchievementCell", for: indexPath) as! ChildAchievementCell
            cell.configure(with: achievements[indexPath.row])
            return cell
        } else {
            let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "ChildCharacterCell", for: indexPath) as! ChildCharacterCell
            cell.configure(with: characters[indexPath.row])
            return cell
        }
    }
}

// MARK: - UICollectionViewDelegate
extension ChildInterfaceViewController: UICollectionViewDelegate {
    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        if collectionView == gamesCollectionView {
            let game = games[indexPath.row]
            startGame(game)
        } else if collectionView == achievementsCollectionView {
            let achievement = achievements[indexPath.row]
            showAchievementDetails(achievement)
        } else {
            let character = characters[indexPath.row]
            selectCharacter(character)
        }
    }
    
    private func startGame(_ game: ChildGame) {
        let gameVC = ChildGameViewController(game: game)
        present(gameVC, animated: true)
    }
    
    private func showAchievementDetails(_ achievement: ChildAchievement) {
        let alert = UIAlertController(title: achievement.title, message: achievement.description, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    private func selectCharacter(_ character: ChildCharacter) {
        childManager.selectCharacter(character)
        characterImageView.image = UIImage(named: character.imageName)
    }
}
```

### 📋 **2. ChildInterfaceManager.swift:**
```swift
import Foundation
import Combine

// MARK: - Child Interface Manager
class ChildInterfaceManager: ObservableObject {
    static let shared = ChildInterfaceManager()
    
    @Published var userProfile: ChildUserProfile
    @Published var currentCharacter: ChildCharacter?
    @Published var games: [ChildGame] = []
    @Published var achievements: [ChildAchievement] = []
    @Published var characters: [ChildCharacter] = []
    
    private init() {
        self.userProfile = ChildUserProfile(
            name: "Маша",
            age: 8,
            ageCategory: .child,
            level: 3,
            points: 150,
            levelProgress: 75,
            totalPlayTime: 120,
            gamesCompleted: 5,
            achievementsUnlocked: 12
        )
        loadInitialData()
    }
    
    private func loadInitialData() {
        loadGames()
        loadAchievements()
        loadCharacters()
    }
    
    private func loadGames() {
        games = [
            ChildGame(
                id: "1",
                title: "🛡️ Защитник Семьи",
                description: "Защити семью от злых хакеров!",
                icon: "shield.fill",
                difficulty: .easy,
                minLevel: 1,
                maxLevel: 5,
                stars: 3,
                isCompleted: false
            ),
            ChildGame(
                id: "2",
                title: "🎯 Кибер-Квест",
                description: "Пройди квест по безопасности!",
                icon: "target",
                difficulty: .medium,
                minLevel: 2,
                maxLevel: 8,
                stars: 4,
                isCompleted: false
            ),
            ChildGame(
                id: "3",
                title: "🚀 Космическая Безопасность",
                description: "Исследуй космос и изучай безопасность!",
                icon: "airplane",
                difficulty: .hard,
                minLevel: 3,
                maxLevel: 10,
                stars: 2,
                isCompleted: false
            )
        ]
    }
    
    private func loadAchievements() {
        achievements = [
            ChildAchievement(
                id: "1",
                title: "🥇 Золотой Защитник",
                description: "Заверши 10 игр",
                icon: "trophy.fill",
                isUnlocked: true,
                points: 100
            ),
            ChildAchievement(
                id: "2",
                title: "🎯 Снайпер",
                description: "Попади в цель 50 раз",
                icon: "target",
                isUnlocked: true,
                points: 50
            ),
            ChildAchievement(
                id: "3",
                title: "🛡️ Щит",
                description: "Заблокируй 100 угроз",
                icon: "shield",
                isUnlocked: false,
                points: 200
            ),
            ChildAchievement(
                id: "4",
                title: "⭐ Звезда",
                description: "Получи 5 звезд в игре",
                icon: "star.fill",
                isUnlocked: true,
                points: 75
            )
        ]
    }
    
    private func loadCharacters() {
        characters = [
            ChildCharacter(
                id: "1",
                name: "Супер-Защитница",
                imageName: "super_protector",
                minLevel: 1,
                maxLevel: 5,
                description: "Добрая защитница семьи",
                isUnlocked: true
            ),
            ChildCharacter(
                id: "2",
                name: "Кибер-Герой",
                imageName: "cyber_hero",
                minLevel: 3,
                maxLevel: 8,
                description: "Отважный герой интернета",
                isUnlocked: true
            ),
            ChildCharacter(
                id: "3",
                name: "Космический Страж",
                imageName: "space_guardian",
                minLevel: 5,
                maxLevel: 10,
                description: "Страж космической безопасности",
                isUnlocked: false
            )
        ]
    }
    
    func getAvailableGames() -> [ChildGame] {
        return games.filter { game in
            game.minLevel <= userProfile.level && game.maxLevel >= userProfile.level
        }
    }
    
    func getAchievements() -> [ChildAchievement] {
        return achievements
    }
    
    func getCharacters() -> [ChildCharacter] {
        return characters
    }
    
    func selectCharacter(_ character: ChildCharacter) {
        currentCharacter = character
    }
    
    func completeGame(_ game: ChildGame, stars: Int) {
        if let index = games.firstIndex(where: { $0.id == game.id }) {
            games[index].isCompleted = true
            games[index].stars = stars
            
            // Update user profile
            userProfile.points += stars * 10
            userProfile.gamesCompleted += 1
            
            // Check for level up
            checkLevelUp()
        }
    }
    
    func unlockAchievement(_ achievement: ChildAchievement) {
        if let index = achievements.firstIndex(where: { $0.id == achievement.id }) {
            achievements[index].isUnlocked = true
            userProfile.achievementsUnlocked += 1
            userProfile.points += achievement.points
        }
    }
    
    private func checkLevelUp() {
        let requiredPoints = userProfile.level * 100
        if userProfile.points >= requiredPoints {
            userProfile.level += 1
            userProfile.levelProgress = 0
            
            // Show level up animation
            showLevelUpAnimation()
        } else {
            userProfile.levelProgress = (userProfile.points % 100)
        }
    }
    
    private func showLevelUpAnimation() {
        // Implement level up animation
        print("🎉 Level Up! New level: \(userProfile.level)")
    }
}

// MARK: - Data Models
struct ChildUserProfile {
    let name: String
    let age: Int
    let ageCategory: ChildAgeCategory
    var level: Int
    var points: Int
    var levelProgress: Int
    var totalPlayTime: Int
    var gamesCompleted: Int
    var achievementsUnlocked: Int
}

enum ChildAgeCategory: String, CaseIterable {
    case toddler = "1-6"
    case child = "7-9"
    case preteen = "10-13"
    case teenager = "14-18"
    case youngAdult = "19-24"
    
    var displayName: String {
        switch self {
        case .toddler:
            return "Малыши-Исследователи"
        case .child:
            return "Юные Защитники"
        case .preteen:
            return "Подростки-Герои"
        case .teenager:
            return "Молодые Стражи"
        case .youngAdult:
            return "Взрослые Защитники"
        }
    }
}

struct ChildGame: Identifiable {
    let id: String
    let title: String
    let description: String
    let icon: String
    let difficulty: GameDifficulty
    let minLevel: Int
    let maxLevel: Int
    var stars: Int
    var isCompleted: Bool
}

enum GameDifficulty: String, CaseIterable {
    case easy = "easy"
    case medium = "medium"
    case hard = "hard"
    
    var displayName: String {
        switch self {
        case .easy:
            return "Легко"
        case .medium:
            return "Средне"
        case .hard:
            return "Сложно"
        }
    }
    
    var color: UIColor {
        switch self {
        case .easy:
            return StormSkyColors.successGreen
        case .medium:
            return StormSkyColors.warningYellow
        case .hard:
            return StormSkyColors.errorRed
        }
    }
}

struct ChildAchievement: Identifiable {
    let id: String
    let title: String
    let description: String
    let icon: String
    var isUnlocked: Bool
    let points: Int
}

struct ChildCharacter: Identifiable {
    let id: String
    let name: String
    let imageName: String
    let minLevel: Int
    let maxLevel: Int
    let description: String
    let isUnlocked: Bool
}
```

### 📋 **3. ChildGameCell.swift:**
```swift
import UIKit

// MARK: - Child Game Cell
class ChildGameCell: UICollectionViewCell {
    
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
        label.textAlignment = .center
        label.numberOfLines = 2
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var difficultyLabel: UILabel = {
        let label = UILabel()
        label.font = StormSkyTheme.Typography.small
        label.textAlignment = .center
        label.layer.cornerRadius = 8
        label.clipsToBounds = true
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var starsStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 2
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
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
        containerView.addSubview(difficultyLabel)
        containerView.addSubview(starsStackView)
        
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
            iconImageView.topAnchor.constraint(equalTo: containerView.topAnchor, constant: 16),
            iconImageView.centerXAnchor.constraint(equalTo: containerView.centerXAnchor),
            iconImageView.widthAnchor.constraint(equalToConstant: 40),
            iconImageView.heightAnchor.constraint(equalToConstant: 40),
            
            // Title Label
            titleLabel.topAnchor.constraint(equalTo: iconImageView.bottomAnchor, constant: 8),
            titleLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 8),
            titleLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -8),
            
            // Difficulty Label
            difficultyLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            difficultyLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 8),
            difficultyLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -8),
            difficultyLabel.heightAnchor.constraint(equalToConstant: 16),
            
            // Stars Stack View
            starsStackView.topAnchor.constraint(equalTo: difficultyLabel.bottomAnchor, constant: 8),
            starsStackView.centerXAnchor.constraint(equalTo: containerView.centerXAnchor),
            starsStackView.bottomAnchor.constraint(equalTo: containerView.bottomAnchor, constant: -16),
            starsStackView.widthAnchor.constraint(equalToConstant: 60),
            starsStackView.heightAnchor.constraint(equalToConstant: 20)
        ])
    }
    
    func configure(with game: ChildGame) {
        titleLabel.text = game.title
        iconImageView.image = UIImage(systemName: game.icon)
        
        // Configure difficulty
        difficultyLabel.text = game.difficulty.displayName
        difficultyLabel.backgroundColor = game.difficulty.color
        difficultyLabel.textColor = StormSkyColors.white
        
        // Configure stars
        setupStars(count: game.stars)
    }
    
    private func setupStars(count: Int) {
        // Clear existing stars
        starsStackView.arrangedSubviews.forEach { $0.removeFromSuperview() }
        
        for i in 0..<5 {
            let starImageView = UIImageView()
            starImageView.image = UIImage(systemName: i < count ? "star.fill" : "star")
            starImageView.tintColor = StormSkyColors.goldMain
            starImageView.contentMode = .scaleAspectFit
            starsStackView.addArrangedSubview(starImageView)
        }
    }
}
```

---

## 👴 **ИНТЕРФЕЙС ДЛЯ ПОЖИЛЫХ (ElderlyInterfaceManager)**

### 📋 **4. ElderlyInterfaceViewController.swift:**
```swift
import UIKit
import Combine

// MARK: - Elderly Interface View Controller
class ElderlyInterfaceViewController: UIViewController {
    
    // MARK: - UI Elements
    private lazy var greetingLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 32, weight: .bold)
        label.textColor = StormSkyColors.white
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var statusLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 24, weight: .semibold)
        label.textColor = StormSkyColors.goldMain
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private lazy var emergencyContactsStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private lazy var protectionStatusStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 12
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private lazy var remindersStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 12
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private lazy var voiceControlButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("🎤 Голосовое управление", for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 20, weight: .semibold)
        button.setTitleColor(StormSkyColors.stormSkyDark, for: .normal)
        button.backgroundColor = StormSkyColors.goldMain
        button.layer.cornerRadius = 25
        button.addTarget(self, action: #selector(voiceControlButtonTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    // MARK: - Properties
    private let elderlyManager = ElderlyInterfaceManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupGradientBackground()
        bindViewModel()
        loadElderlyData()
    }
    
    // MARK: - Setup
    private func setupUI() {
        title = "🛡️ ALADDIN"
        navigationController?.navigationBar.prefersLargeTitles = true
        
        view.addSubview(greetingLabel)
        view.addSubview(statusLabel)
        view.addSubview(emergencyContactsStackView)
        view.addSubview(protectionStatusStackView)
        view.addSubview(remindersStackView)
        view.addSubview(voiceControlButton)
        
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
            // Greeting Label
            greetingLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            greetingLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            greetingLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Status Label
            statusLabel.topAnchor.constraint(equalTo: greetingLabel.bottomAnchor, constant: 20),
            statusLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            statusLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Emergency Contacts Stack
            emergencyContactsStackView.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 30),
            emergencyContactsStackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            emergencyContactsStackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Protection Status Stack
            protectionStatusStackView.topAnchor.constraint(equalTo: emergencyContactsStackView.bottomAnchor, constant: 30),
            protectionStatusStackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            protectionStatusStackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Reminders Stack
            remindersStackView.topAnchor.constraint(equalTo: protectionStatusStackView.bottomAnchor, constant: 30),
            remindersStackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            remindersStackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            // Voice Control Button
            voiceControlButton.topAnchor.constraint(equalTo: remindersStackView.bottomAnchor, constant: 30),
            voiceControlButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            voiceControlButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            voiceControlButton.heightAnchor.constraint(equalToConstant: 60),
            voiceControlButton.bottomAnchor.constraint(lessThanOrEqualTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20)
        ])
    }
    
    private func bindViewModel() {
        elderlyManager.$userProfile
            .receive(on: DispatchQueue.main)
            .sink { [weak self] profile in
                self?.updateUI(with: profile)
            }
            .store(in: &cancellables)
    }
    
    private func loadElderlyData() {
        setupEmergencyContacts()
        setupProtectionStatus()
        setupReminders()
    }
    
    private func setupEmergencyContacts() {
        let contacts = elderlyManager.getEmergencyContacts()
        
        for contact in contacts {
            let contactView = createEmergencyContactView(contact: contact)
            emergencyContactsStackView.addArrangedSubview(contactView)
        }
    }
    
    private func setupProtectionStatus() {
        let status = elderlyManager.getProtectionStatus()
        
        let blockedCallsView = createStatusView(
            icon: "🚫",
            title: "Заблокировано звонков",
            value: "\(status.blockedCalls)",
            color: StormSkyColors.errorRed
        )
        
        let safeCallsView = createStatusView(
            icon: "✅",
            title: "Безопасных звонков",
            value: "\(status.safeCalls)",
            color: StormSkyColors.successGreen
        )
        
        let suspiciousView = createStatusView(
            icon: "⚠️",
            title: "Подозрительных",
            value: "\(status.suspiciousCalls)",
            color: StormSkyColors.warningYellow
        )
        
        protectionStatusStackView.addArrangedSubview(blockedCallsView)
        protectionStatusStackView.addArrangedSubview(safeCallsView)
        protectionStatusStackView.addArrangedSubview(suspiciousView)
    }
    
    private func setupReminders() {
        let reminders = elderlyManager.getReminders()
        
        for reminder in reminders {
            let reminderView = createReminderView(reminder: reminder)
            remindersStackView.addArrangedSubview(reminderView)
        }
    }
    
    private func createEmergencyContactView(contact: EmergencyContact) -> UIView {
        let view = UIView()
        view.backgroundColor = StormSkyColors.stormSkyMain80
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.lg
        view.layer.borderWidth = 1
        view.layer.borderColor = StormSkyColors.goldMain30.cgColor
        
        let nameLabel = UILabel()
        nameLabel.text = contact.name
        nameLabel.font = UIFont.systemFont(ofSize: 20, weight: .semibold)
        nameLabel.textColor = StormSkyColors.white
        
        let phoneLabel = UILabel()
        phoneLabel.text = contact.phoneNumber
        phoneLabel.font = UIFont.systemFont(ofSize: 18, weight: .regular)
        phoneLabel.textColor = StormSkyColors.lightningBlue
        
        let callButton = UIButton(type: .system)
        callButton.setTitle("📞 Позвонить", for: .normal)
        callButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        callButton.setTitleColor(StormSkyColors.stormSkyDark, for: .normal)
        callButton.backgroundColor = StormSkyColors.goldMain
        callButton.layer.cornerRadius = 20
        callButton.addTarget(self, action: #selector(callButtonTapped(_:)), for: .touchUpInside)
        callButton.tag = contact.id.hashValue
        
        [nameLabel, phoneLabel, callButton].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview($0)
        }
        
        NSLayoutConstraint.activate([
            nameLabel.topAnchor.constraint(equalTo: view.topAnchor, constant: 16),
            nameLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            nameLabel.trailingAnchor.constraint(equalTo: callButton.leadingAnchor, constant: -8),
            
            phoneLabel.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 4),
            phoneLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            phoneLabel.trailingAnchor.constraint(equalTo: callButton.leadingAnchor, constant: -8),
            
            callButton.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            callButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            callButton.widthAnchor.constraint(equalToConstant: 120),
            callButton.heightAnchor.constraint(equalToConstant: 40),
            
            view.heightAnchor.constraint(equalToConstant: 80)
        ])
        
        return view
    }
    
    private func createStatusView(icon: String, title: String, value: String, color: UIColor) -> UIView {
        let view = UIView()
        view.backgroundColor = StormSkyColors.stormSkyMain80
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        
        let iconLabel = UILabel()
        iconLabel.text = icon
        iconLabel.font = UIFont.systemFont(ofSize: 24)
        
        let titleLabel = UILabel()
        titleLabel.text = title
        titleLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        titleLabel.textColor = StormSkyColors.white
        
        let valueLabel = UILabel()
        valueLabel.text = value
        valueLabel.font = UIFont.systemFont(ofSize: 20, weight: .bold)
        valueLabel.textColor = color
        
        [iconLabel, titleLabel, valueLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview($0)
        }
        
        NSLayoutConstraint.activate([
            iconLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            iconLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            
            titleLabel.leadingAnchor.constraint(equalTo: iconLabel.trailingAnchor, constant: 12),
            titleLabel.topAnchor.constraint(equalTo: view.topAnchor, constant: 12),
            
            valueLabel.leadingAnchor.constraint(equalTo: iconLabel.trailingAnchor, constant: 12),
            valueLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            valueLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            valueLabel.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -12),
            
            view.heightAnchor.constraint(equalToConstant: 60)
        ])
        
        return view
    }
    
    private func createReminderView(reminder: ElderlyReminder) -> UIView {
        let view = UIView()
        view.backgroundColor = StormSkyColors.stormSkyMain80
        view.layer.cornerRadius = StormSkyTheme.CornerRadius.md
        
        let iconLabel = UILabel()
        iconLabel.text = reminder.icon
        iconLabel.font = UIFont.systemFont(ofSize: 20)
        
        let titleLabel = UILabel()
        titleLabel.text = reminder.title
        titleLabel.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        titleLabel.textColor = StormSkyColors.white
        
        let timeLabel = UILabel()
        timeLabel.text = reminder.time
        timeLabel.font = UIFont.systemFont(ofSize: 14, weight: .regular)
        timeLabel.textColor = StormSkyColors.lightningBlue
        
        [iconLabel, titleLabel, timeLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview($0)
        }
        
        NSLayoutConstraint.activate([
            iconLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            iconLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            
            titleLabel.leadingAnchor.constraint(equalTo: iconLabel.trailingAnchor, constant: 12),
            titleLabel.topAnchor.constraint(equalTo: view.topAnchor, constant: 12),
            
            timeLabel.leadingAnchor.constraint(equalTo: iconLabel.trailingAnchor, constant: 12),
            timeLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            timeLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            timeLabel.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -12),
            
            view.heightAnchor.constraint(equalToConstant: 50)
        ])
        
        return view
    }
    
    private func updateUI(with profile: ElderlyUserProfile) {
        greetingLabel.text = "Добро пожаловать!"
        statusLabel.text = "🛡️ ВЫ ЗАЩИЩЕНЫ ОТ МОШЕННИКОВ"
    }
    
    // MARK: - Actions
    @objc private func voiceControlButtonTapped() {
        let voiceVC = ElderlyVoiceControlViewController()
        present(voiceVC, animated: true)
    }
    
    @objc private func callButtonTapped(_ sender: UIButton) {
        // Handle call button tap
        print("Call button tapped for contact: \(sender.tag)")
    }
}

// MARK: - Data Models
struct ElderlyUserProfile {
    let name: String
    let age: Int
    let ageCategory: ElderlyAgeCategory
    let interfaceComplexity: InterfaceComplexity
    let accessibilityLevel: AccessibilityLevel
    let emergencyContacts: [EmergencyContact]
    let medicalReminders: [ElderlyReminder]
    let protectionSettings: ProtectionSettings
}

enum ElderlyAgeCategory: String, CaseIterable {
    case activeElderly = "60-70"
    case middleElderly = "71-80"
    case seniorElderly = "81+"
    
    var displayName: String {
        switch self {
        case .activeElderly:
            return "Активные пожилые"
        case .middleElderly:
            return "Средний возраст"
        case .seniorElderly:
            return "Пожилые с ограничениями"
        }
    }
}

enum InterfaceComplexity: String, CaseIterable {
    case simple = "simple"
    case moderate = "moderate"
    case advanced = "advanced"
    
    var displayName: String {
        switch self {
        case .simple:
            return "Простой"
        case .moderate:
            return "Умеренный"
        case .advanced:
            return "Продвинутый"
        }
    }
}

enum AccessibilityLevel: String, CaseIterable {
    case basic = "basic"
    case enhanced = "enhanced"
    case maximum = "maximum"
    
    var displayName: String {
        switch self {
        case .basic:
            return "Базовый"
        case .enhanced:
            return "Улучшенный"
        case .maximum:
            return "Максимальный"
        }
    }
}

struct EmergencyContact {
    let id: String
    let name: String
    let phoneNumber: String
    let relationship: String
    let isPrimary: Bool
}

struct ElderlyReminder {
    let id: String
    let title: String
    let time: String
    let icon: String
    let isActive: Bool
}

struct ProtectionSettings {
    let blockedCalls: Int
    let safeCalls: Int
    let suspiciousCalls: Int
    let autoBlock: Bool
    let voiceAlerts: Bool
}
```

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Реализовать детский интерфейс** с играми и персонажами
2. **Создать интерфейс для пожилых** с упрощенным дизайном
3. **Добавить родительский контроль** с полным функционалом
4. **Интегрировать голосовое управление**
5. **Протестировать на разных устройствах**
6. **Оптимизировать для доступности**

**🎯 СПЕЦИАЛИЗИРОВАННЫЕ ИНТЕРФЕЙСЫ iOS ГОТОВЫ К РЕАЛИЗАЦИИ!**

**📱 ПЕРЕХОДИМ К ANDROID ВЕРСИИ!**


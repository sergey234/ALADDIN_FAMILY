import UIKit
import Combine

// MARK: - Support Main Interface для iOS
class SupportMainInterface: UIViewController {
    
    // MARK: - UI Components
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    private let headerView = UIView()
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    private let statusView = UIView()
    private let statusLabel = UILabel()
    private let statusIndicator = UIView()
    
    // Quick Actions
    private let quickActionsStackView = UIStackView()
    private let chatButton = SupportActionButton()
    private let faqButton = SupportActionButton()
    private let contactButton = SupportActionButton()
    private let emergencyButton = SupportActionButton()
    
    // Support Categories
    private let categoriesStackView = UIStackView()
    private let categoriesLabel = UILabel()
    
    // Recent Activity
    private let recentActivityView = UIView()
    private let recentActivityLabel = UILabel()
    private let recentActivityTableView = UITableView()
    
    // Properties
    private var cancellables = Set<AnyCancellable>()
    private let supportAPI = UnifiedSupportAPIManager()
    private var recentTickets: [SupportTicket] = []
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupBindings()
        loadData()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        view.backgroundColor = StormSkyColors.backgroundPrimary
        
        // Navigation
        navigationItem.title = "Поддержка"
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            title: "Настройки",
            style: .plain,
            target: self,
            action: #selector(settingsButtonTapped)
        )
        
        // Header View
        setupHeaderView()
        
        // Quick Actions
        setupQuickActions()
        
        // Categories
        setupCategories()
        
        // Recent Activity
        setupRecentActivity()
        
        // Add subviews
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        contentView.addSubview(headerView)
        contentView.addSubview(quickActionsStackView)
        contentView.addSubview(categoriesStackView)
        contentView.addSubview(recentActivityView)
    }
    
    private func setupHeaderView() {
        headerView.backgroundColor = StormSkyColors.backgroundSecondary
        headerView.layer.cornerRadius = 16
        headerView.layer.borderWidth = 1
        headerView.layer.borderColor = StormSkyColors.accent.cgColor
        
        // Title
        titleLabel.text = "AI Помощник ALADDIN"
        titleLabel.font = UIFont.boldSystemFont(ofSize: 24)
        titleLabel.textColor = StormSkyColors.textPrimary
        titleLabel.textAlignment = .center
        
        // Subtitle
        subtitleLabel.text = "Ваш персональный помощник по безопасности"
        subtitleLabel.font = UIFont.systemFont(ofSize: 16)
        subtitleLabel.textColor = StormSkyColors.textSecondary
        subtitleLabel.textAlignment = .center
        subtitleLabel.numberOfLines = 0
        
        // Status
        statusIndicator.backgroundColor = StormSkyColors.success
        statusIndicator.layer.cornerRadius = 6
        statusIndicator.layer.borderWidth = 2
        statusIndicator.layer.borderColor = StormSkyColors.accent.cgColor
        
        statusLabel.text = "Онлайн"
        statusLabel.font = UIFont.systemFont(ofSize: 14)
        statusLabel.textColor = StormSkyColors.textPrimary
        
        [titleLabel, subtitleLabel, statusView].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            headerView.addSubview($0)
        }
        
        [statusIndicator, statusLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            statusView.addSubview($0)
        }
    }
    
    private func setupQuickActions() {
        quickActionsStackView.axis = .vertical
        quickActionsStackView.spacing = 16
        quickActionsStackView.distribution = .fillEqually
        
        // Chat Button
        chatButton.configure(
            title: "💬 Чат с AI",
            subtitle: "Задайте вопрос помощнику",
            action: { [weak self] in self?.openChat() }
        )
        
        // FAQ Button
        faqButton.configure(
            title: "❓ Частые вопросы",
            subtitle: "Быстрые ответы на популярные вопросы",
            action: { [weak self] in self?.openFAQ() }
        )
        
        // Contact Button
        contactButton.configure(
            title: "📞 Связаться с нами",
            subtitle: "Техническая поддержка и консультации",
            action: { [weak self] in self?.openContact() }
        )
        
        // Emergency Button
        emergencyButton.configure(
            title: "🚨 Экстренная помощь",
            subtitle: "Критические ситуации и срочная поддержка",
            action: { [weak self] in self?.openEmergency() }
        )
        emergencyButton.setEmergencyStyle()
        
        [chatButton, faqButton, contactButton, emergencyButton].forEach {
            quickActionsStackView.addArrangedSubview($0)
        }
    }
    
    private func setupCategories() {
        categoriesLabel.text = "Категории поддержки"
        categoriesLabel.font = UIFont.boldSystemFont(ofSize: 20)
        categoriesLabel.textColor = StormSkyColors.textPrimary
        
        categoriesStackView.axis = .vertical
        categoriesStackView.spacing = 12
        
        let categories = [
            ("🛡️ Безопасность", "security", "Защита семьи и устройств"),
            ("👨‍👩‍👧‍👦 Семья", "family", "Родительский контроль и детская безопасность"),
            ("🔧 Настройки", "settings", "Конфигурация приложения"),
            ("💳 Платежи", "payments", "Подписки и оплата"),
            ("📱 Устройства", "devices", "Подключение и синхронизация"),
            ("🔐 Безопасность данных", "privacy", "Конфиденциальность и шифрование")
        ]
        
        categories.forEach { (title, category, description) in
            let categoryView = SupportCategoryView()
            categoryView.configure(title: title, description: description, category: category)
            categoryView.onTap = { [weak self] in
                self?.openCategory(category)
            }
            categoriesStackView.addArrangedSubview(categoryView)
        }
        
        [categoriesLabel, categoriesStackView].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            categoriesStackView.addArrangedSubview($0)
        }
    }
    
    private func setupRecentActivity() {
        recentActivityLabel.text = "Недавние обращения"
        recentActivityLabel.font = UIFont.boldSystemFont(ofSize: 20)
        recentActivityLabel.textColor = StormSkyColors.textPrimary
        
        recentActivityTableView.delegate = self
        recentActivityTableView.dataSource = self
        recentActivityTableView.backgroundColor = .clear
        recentActivityTableView.separatorStyle = .none
        recentActivityTableView.register(SupportTicketCell.self, forCellReuseIdentifier: "TicketCell")
        recentActivityTableView.isScrollEnabled = false
        
        [recentActivityLabel, recentActivityTableView].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            recentActivityView.addSubview($0)
        }
    }
    
    private func setupConstraints() {
        [scrollView, contentView, headerView, titleLabel, subtitleLabel, statusView, statusIndicator, statusLabel, quickActionsStackView, categoriesStackView, recentActivityView, recentActivityLabel, recentActivityTableView].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
        }
        
        NSLayoutConstraint.activate([
            // Scroll View
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            // Content View
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            // Header View
            headerView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 16),
            headerView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            headerView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            // Title
            titleLabel.topAnchor.constraint(equalTo: headerView.topAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            // Subtitle
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            subtitleLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            subtitleLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            // Status View
            statusView.topAnchor.constraint(equalTo: subtitleLabel.bottomAnchor, constant: 16),
            statusView.centerXAnchor.constraint(equalTo: headerView.centerXAnchor),
            statusView.bottomAnchor.constraint(equalTo: headerView.bottomAnchor, constant: -20),
            statusView.heightAnchor.constraint(equalToConstant: 24),
            
            // Status Indicator
            statusIndicator.leadingAnchor.constraint(equalTo: statusView.leadingAnchor),
            statusIndicator.centerYAnchor.constraint(equalTo: statusView.centerYAnchor),
            statusIndicator.widthAnchor.constraint(equalToConstant: 12),
            statusIndicator.heightAnchor.constraint(equalToConstant: 12),
            
            // Status Label
            statusLabel.leadingAnchor.constraint(equalTo: statusIndicator.trailingAnchor, constant: 8),
            statusLabel.trailingAnchor.constraint(equalTo: statusView.trailingAnchor),
            statusLabel.centerYAnchor.constraint(equalTo: statusView.centerYAnchor),
            
            // Quick Actions
            quickActionsStackView.topAnchor.constraint(equalTo: headerView.bottomAnchor, constant: 24),
            quickActionsStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            quickActionsStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            // Categories
            categoriesStackView.topAnchor.constraint(equalTo: quickActionsStackView.bottomAnchor, constant: 32),
            categoriesStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            categoriesStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            // Recent Activity
            recentActivityView.topAnchor.constraint(equalTo: categoriesStackView.bottomAnchor, constant: 32),
            recentActivityView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            recentActivityView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            recentActivityView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -32),
            
            // Recent Activity Label
            recentActivityLabel.topAnchor.constraint(equalTo: recentActivityView.topAnchor),
            recentActivityLabel.leadingAnchor.constraint(equalTo: recentActivityView.leadingAnchor),
            recentActivityLabel.trailingAnchor.constraint(equalTo: recentActivityView.trailingAnchor),
            
            // Recent Activity Table View
            recentActivityTableView.topAnchor.constraint(equalTo: recentActivityLabel.bottomAnchor, constant: 16),
            recentActivityTableView.leadingAnchor.constraint(equalTo: recentActivityView.leadingAnchor),
            recentActivityTableView.trailingAnchor.constraint(equalTo: recentActivityView.trailingAnchor),
            recentActivityTableView.bottomAnchor.constraint(equalTo: recentActivityView.bottomAnchor),
            recentActivityTableView.heightAnchor.constraint(equalToConstant: 200)
        ])
    }
    
    private func setupBindings() {
        // Load data when view appears
        NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
            .sink { [weak self] _ in
                self?.loadData()
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Data Loading
    private func loadData() {
        loadRecentTickets()
        checkSupportStatus()
    }
    
    private func loadRecentTickets() {
        supportAPI.getRecentTickets()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] tickets in
                    self?.recentTickets = tickets
                    self?.recentActivityTableView.reloadData()
                }
            )
            .store(in: &cancellables)
    }
    
    private func checkSupportStatus() {
        supportAPI.getSupportStatus()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] status in
                    self?.updateStatusIndicator(status)
                }
            )
            .store(in: &cancellables)
    }
    
    private func updateStatusIndicator(_ status: SupportStatus) {
        switch status {
        case .online:
            statusIndicator.backgroundColor = StormSkyColors.success
            statusLabel.text = "Онлайн"
        case .busy:
            statusIndicator.backgroundColor = StormSkyColors.warning
            statusLabel.text = "Занят"
        case .offline:
            statusIndicator.backgroundColor = StormSkyColors.error
            statusLabel.text = "Офлайн"
        }
    }
    
    // MARK: - Actions
    @objc private func settingsButtonTapped() {
        let settingsVC = SupportSettingsViewController()
        let navController = UINavigationController(rootViewController: settingsVC)
        present(navController, animated: true)
    }
    
    private func openChat() {
        let chatVC = SupportChatInterface()
        let navController = UINavigationController(rootViewController: chatVC)
        present(navController, animated: true)
    }
    
    private func openFAQ() {
        let faqVC = SupportFAQViewController()
        let navController = UINavigationController(rootViewController: faqVC)
        present(navController, animated: true)
    }
    
    private func openContact() {
        let contactVC = SupportContactViewController()
        let navController = UINavigationController(rootViewController: contactVC)
        present(navController, animated: true)
    }
    
    private func openEmergency() {
        let emergencyVC = SupportEmergencyViewController()
        let navController = UINavigationController(rootViewController: emergencyVC)
        present(navController, animated: true)
    }
    
    private func openCategory(_ category: String) {
        let categoryVC = SupportCategoryViewController(category: category)
        let navController = UINavigationController(rootViewController: categoryVC)
        present(navController, animated: true)
    }
}

// MARK: - Table View Data Source & Delegate
extension SupportMainInterface: UITableViewDataSource, UITableViewDelegate {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return min(recentTickets.count, 3) // Show max 3 recent tickets
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "TicketCell", for: indexPath) as! SupportTicketCell
        cell.configure(with: recentTickets[indexPath.row])
        return cell
    }
    
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return 60
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let ticket = recentTickets[indexPath.row]
        openTicketDetails(ticket)
    }
    
    private func openTicketDetails(_ ticket: SupportTicket) {
        let detailsVC = SupportTicketDetailsViewController(ticket: ticket)
        let navController = UINavigationController(rootViewController: detailsVC)
        present(navController, animated: true)
    }
}

// MARK: - Support Action Button
class SupportActionButton: UIView {
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    private let iconLabel = UILabel()
    private var action: (() -> Void)?
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        backgroundColor = StormSkyColors.backgroundSecondary
        layer.cornerRadius = 16
        layer.borderWidth = 1
        layer.borderColor = StormSkyColors.accent.cgColor
        
        // Icon
        iconLabel.font = UIFont.systemFont(ofSize: 24)
        iconLabel.textAlignment = .center
        
        // Title
        titleLabel.font = UIFont.boldSystemFont(ofSize: 18)
        titleLabel.textColor = StormSkyColors.textPrimary
        
        // Subtitle
        subtitleLabel.font = UIFont.systemFont(ofSize: 14)
        subtitleLabel.textColor = StormSkyColors.textSecondary
        subtitleLabel.numberOfLines = 0
        
        [iconLabel, titleLabel, subtitleLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            addSubview($0)
        }
        
        NSLayoutConstraint.activate([
            iconLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            iconLabel.centerYAnchor.constraint(equalTo: centerYAnchor),
            iconLabel.widthAnchor.constraint(equalToConstant: 40),
            
            titleLabel.leadingAnchor.constraint(equalTo: iconLabel.trailingAnchor, constant: 12),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            titleLabel.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            
            subtitleLabel.leadingAnchor.constraint(equalTo: titleLabel.leadingAnchor),
            subtitleLabel.trailingAnchor.constraint(equalTo: titleLabel.trailingAnchor),
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            subtitleLabel.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])
        
        // Tap gesture
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(buttonTapped))
        addGestureRecognizer(tapGesture)
    }
    
    func configure(title: String, subtitle: String, action: @escaping () -> Void) {
        let components = title.components(separatedBy: " ")
        if let emoji = components.first {
            iconLabel.text = emoji
            titleLabel.text = components.dropFirst().joined(separator: " ")
        } else {
            titleLabel.text = title
        }
        subtitleLabel.text = subtitle
        self.action = action
    }
    
    func setEmergencyStyle() {
        backgroundColor = StormSkyColors.error.withAlphaComponent(0.1)
        layer.borderColor = StormSkyColors.error.cgColor
        titleLabel.textColor = StormSkyColors.error
    }
    
    @objc private func buttonTapped() {
        action?()
    }
}

// MARK: - Support Models
struct SupportTicket {
    let id: String
    let title: String
    let status: TicketStatus
    let category: String
    let createdAt: Date
    let lastMessage: String?
}

enum TicketStatus {
    case open
    case inProgress
    case resolved
    case closed
}

enum SupportStatus {
    case online
    case busy
    case offline
}


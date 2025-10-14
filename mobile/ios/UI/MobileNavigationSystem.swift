//
//  MobileNavigationSystem.swift
//  ALADDIN Mobile Security
//
//  Mobile Navigation System for iOS
//  Adaptive navigation with bottom bar for mobile and desktop navigation
//
//  Created by ALADDIN Security Team
//  Date: 2025-01-27
//  Version: 1.0
//

import UIKit

// MARK: - Navigation Item Model
struct NavigationItem {
    let title: String
    let icon: String
    let selectedIcon: String?
    let identifier: String
    let badge: String?
    let isEnabled: Bool
    
    init(title: String, icon: String, selectedIcon: String? = nil, identifier: String, badge: String? = nil, isEnabled: Bool = true) {
        self.title = title
        self.icon = icon
        self.selectedIcon = selectedIcon
        self.identifier = identifier
        self.badge = badge
        self.isEnabled = isEnabled
    }
}

// MARK: - Navigation Delegate
protocol MobileNavigationDelegate: AnyObject {
    func didSelectNavigationItem(_ item: NavigationItem)
    func didTapNavigationBadge(_ item: NavigationItem)
}

// MARK: - Mobile Navigation Controller
class MobileNavigationController: UIViewController {
    
    // MARK: - Properties
    weak var delegate: MobileNavigationDelegate?
    private var navigationItems: [NavigationItem] = []
    private var selectedIndex: Int = 0
    private var isMobileLayout: Bool = true
    
    // MARK: - UI Components
    private var containerView: UIView!
    private var bottomNavigationView: UIView!
    private var topNavigationView: UIView!
    private var navigationStackView: UIStackView!
    private var contentViewController: UIViewController?
    
    // MARK: - Configuration
    private let config = NavigationConfig()
    
    // MARK: - Initialization
    init(navigationItems: [NavigationItem], contentViewController: UIViewController? = nil) {
        self.navigationItems = navigationItems
        self.contentViewController = contentViewController
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
    }
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupNavigationSystem()
        setupConstraints()
        updateLayoutForCurrentSize()
    }
    
    override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
        super.viewWillTransition(to: size, with: coordinator)
        
        coordinator.animate(alongsideTransition: { _ in
            self.updateLayoutForCurrentSize()
        })
    }
    
    // MARK: - Setup
    private func setupNavigationSystem() {
        // Create container view
        containerView = UIView()
        containerView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(containerView)
        
        // Create navigation views
        setupBottomNavigationView()
        setupTopNavigationView()
        
        // Add content view controller
        if let contentVC = contentViewController {
            addChild(contentVC)
            containerView.addSubview(contentVC.view)
            contentVC.view.translatesAutoresizingMaskIntoConstraints = false
            contentVC.didMove(toParent: self)
        }
    }
    
    private func setupBottomNavigationView() {
        bottomNavigationView = UIView()
        bottomNavigationView.translatesAutoresizingMaskIntoConstraints = false
        bottomNavigationView.backgroundColor = UIColor.black.withAlphaComponent(0.8)
        bottomNavigationView.layer.cornerRadius = 20
        bottomNavigationView.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]
        
        // Add blur effect
        let blurEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        let blurEffectView = UIVisualEffectView(effect: blurEffect)
        blurEffectView.translatesAutoresizingMaskIntoConstraints = false
        bottomNavigationView.addSubview(blurEffectView)
        
        NSLayoutConstraint.activate([
            blurEffectView.topAnchor.constraint(equalTo: bottomNavigationView.topAnchor),
            blurEffectView.leadingAnchor.constraint(equalTo: bottomNavigationView.leadingAnchor),
            blurEffectView.trailingAnchor.constraint(equalTo: bottomNavigationView.trailingAnchor),
            blurEffectView.bottomAnchor.constraint(equalTo: bottomNavigationView.bottomAnchor)
        ])
        
        // Create navigation stack view
        navigationStackView = UIStackView()
        navigationStackView.translatesAutoresizingMaskIntoConstraints = false
        navigationStackView.axis = .horizontal
        navigationStackView.distribution = .fillEqually
        navigationStackView.spacing = 0
        bottomNavigationView.addSubview(navigationStackView)
        
        // Add navigation items
        setupNavigationItems()
        
        view.addSubview(bottomNavigationView)
    }
    
    private func setupTopNavigationView() {
        topNavigationView = UIView()
        topNavigationView.translatesAutoresizingMaskIntoConstraints = false
        topNavigationView.backgroundColor = UIColor.clear
        
        // Add blur effect
        let blurEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        let blurEffectView = UIVisualEffectView(effect: blurEffect)
        blurEffectView.translatesAutoresizingMaskIntoConstraints = false
        topNavigationView.addSubview(blurEffectView)
        
        NSLayoutConstraint.activate([
            blurEffectView.topAnchor.constraint(equalTo: topNavigationView.topAnchor),
            blurEffectView.leadingAnchor.constraint(equalTo: topNavigationView.leadingAnchor),
            blurEffectView.trailingAnchor.constraint(equalTo: topNavigationView.trailingAnchor),
            blurEffectView.bottomAnchor.constraint(equalTo: topNavigationView.bottomAnchor)
        ])
        
        // Create horizontal navigation stack
        let horizontalStackView = UIStackView()
        horizontalStackView.translatesAutoresizingMaskIntoConstraints = false
        horizontalStackView.axis = .horizontal
        horizontalStackView.distribution = .fillEqually
        horizontalStackView.spacing = 20
        topNavigationView.addSubview(horizontalStackView)
        
        // Add navigation items for desktop
        for (index, item) in navigationItems.enumerated() {
            let button = createDesktopNavigationButton(for: item, at: index)
            horizontalStackView.addArrangedSubview(button)
        }
        
        view.addSubview(topNavigationView)
    }
    
    private func setupNavigationItems() {
        for (index, item) in navigationItems.enumerated() {
            let button = createMobileNavigationButton(for: item, at: index)
            navigationStackView.addArrangedSubview(button)
        }
    }
    
    private func createMobileNavigationButton(for item: NavigationItem, at index: Int) -> UIButton {
        let button = UIButton(type: .custom)
        button.translatesAutoresizingMaskIntoConstraints = false
        button.tag = index
        
        // Configure button
        button.setTitle(item.title, for: .normal)
        button.setTitleColor(.white.withAlphaComponent(0.6), for: .normal)
        button.setTitleColor(.white, for: .selected)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 12, weight: .medium)
        button.titleLabel?.textAlignment = .center
        
        // Set icon
        let iconImage = UIImage(systemName: item.icon)
        button.setImage(iconImage, for: .normal)
        button.tintColor = .white.withAlphaComponent(0.6)
        
        if let selectedIcon = item.selectedIcon {
            let selectedIconImage = UIImage(systemName: selectedIcon)
            button.setImage(selectedIconImage, for: .selected)
        }
        
        // Configure image and title layout
        button.imageView?.contentMode = .scaleAspectFit
        button.titleLabel?.numberOfLines = 1
        button.titleLabel?.adjustsFontSizeToFitWidth = true
        
        // Set image and title insets
        button.imageEdgeInsets = UIEdgeInsets(top: -8, left: 0, bottom: 8, right: 0)
        button.titleEdgeInsets = UIEdgeInsets(top: 8, left: 0, bottom: -8, right: 0)
        
        // Add badge if needed
        if let badge = item.badge {
            addBadge(to: button, text: badge)
        }
        
        // Add action
        button.addTarget(self, action: #selector(navigationButtonTapped(_:)), for: .touchUpInside)
        
        // Set initial state
        button.isSelected = (index == selectedIndex)
        button.isEnabled = item.isEnabled
        
        // Set constraints
        NSLayoutConstraint.activate([
            button.heightAnchor.constraint(equalToConstant: 60)
        ])
        
        return button
    }
    
    private func createDesktopNavigationButton(for item: NavigationItem, at index: Int) -> UIButton {
        let button = UIButton(type: .custom)
        button.translatesAutoresizingMaskIntoConstraints = false
        button.tag = index
        
        // Configure button
        button.setTitle(item.title, for: .normal)
        button.setTitleColor(.white.withAlphaComponent(0.8), for: .normal)
        button.setTitleColor(.white, for: .selected)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        button.titleLabel?.textAlignment = .center
        
        // Set icon
        let iconImage = UIImage(systemName: item.icon)
        button.setImage(iconImage, for: .normal)
        button.tintColor = .white.withAlphaComponent(0.8)
        
        if let selectedIcon = item.selectedIcon {
            let selectedIconImage = UIImage(systemName: selectedIcon)
            button.setImage(selectedIconImage, for: .selected)
        }
        
        // Configure image and title layout
        button.imageView?.contentMode = .scaleAspectFit
        button.titleLabel?.numberOfLines = 1
        
        // Set image and title insets
        button.imageEdgeInsets = UIEdgeInsets(top: 0, left: -8, bottom: 0, right: 8)
        button.titleEdgeInsets = UIEdgeInsets(top: 0, left: 8, bottom: 0, right: -8)
        
        // Add badge if needed
        if let badge = item.badge {
            addBadge(to: button, text: badge)
        }
        
        // Add action
        button.addTarget(self, action: #selector(navigationButtonTapped(_:)), for: .touchUpInside)
        
        // Set initial state
        button.isSelected = (index == selectedIndex)
        button.isEnabled = item.isEnabled
        
        // Set constraints
        NSLayoutConstraint.activate([
            button.heightAnchor.constraint(equalToConstant: 44)
        ])
        
        return button
    }
    
    private func addBadge(to button: UIButton, text: String) {
        let badgeLabel = UILabel()
        badgeLabel.translatesAutoresizingMaskIntoConstraints = false
        badgeLabel.text = text
        badgeLabel.font = UIFont.systemFont(ofSize: 10, weight: .bold)
        badgeLabel.textColor = .white
        badgeLabel.textAlignment = .center
        badgeLabel.backgroundColor = UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 1.0) // Golden
        badgeLabel.layer.cornerRadius = 8
        badgeLabel.clipsToBounds = true
        
        button.addSubview(badgeLabel)
        
        NSLayoutConstraint.activate([
            badgeLabel.topAnchor.constraint(equalTo: button.topAnchor, constant: 8),
            badgeLabel.trailingAnchor.constraint(equalTo: button.trailingAnchor, constant: -8),
            badgeLabel.widthAnchor.constraint(greaterThanOrEqualToConstant: 16),
            badgeLabel.heightAnchor.constraint(equalToConstant: 16)
        ])
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Container view
            containerView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            containerView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            containerView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            containerView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
            
            // Bottom navigation view
            bottomNavigationView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            bottomNavigationView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            bottomNavigationView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -16),
            bottomNavigationView.heightAnchor.constraint(equalToConstant: 80),
            
            // Navigation stack view
            navigationStackView.topAnchor.constraint(equalTo: bottomNavigationView.topAnchor, constant: 8),
            navigationStackView.leadingAnchor.constraint(equalTo: bottomNavigationView.leadingAnchor, constant: 16),
            navigationStackView.trailingAnchor.constraint(equalTo: bottomNavigationView.trailingAnchor, constant: -16),
            navigationStackView.bottomAnchor.constraint(equalTo: bottomNavigationView.bottomAnchor, constant: -8),
            
            // Top navigation view
            topNavigationView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            topNavigationView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            topNavigationView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            topNavigationView.heightAnchor.constraint(equalToConstant: 60)
        ])
        
        // Content view controller constraints
        if let contentVC = contentViewController {
            NSLayoutConstraint.activate([
                contentVC.view.topAnchor.constraint(equalTo: containerView.topAnchor),
                contentVC.view.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
                contentVC.view.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
                contentVC.view.bottomAnchor.constraint(equalTo: containerView.bottomAnchor)
            ])
        }
    }
    
    // MARK: - Layout Updates
    private func updateLayoutForCurrentSize() {
        let isCompact = view.bounds.width < 768 // iPad compact width
        
        if isCompact != isMobileLayout {
            isMobileLayout = isCompact
            updateNavigationVisibility()
        }
    }
    
    private func updateNavigationVisibility() {
        UIView.animate(withDuration: 0.3) {
            self.bottomNavigationView.alpha = self.isMobileLayout ? 1.0 : 0.0
            self.topNavigationView.alpha = self.isMobileLayout ? 0.0 : 1.0
        }
    }
    
    // MARK: - Actions
    @objc private func navigationButtonTapped(_ sender: UIButton) {
        let index = sender.tag
        guard index < navigationItems.count else { return }
        
        let item = navigationItems[index]
        
        // Update selection
        updateSelection(to: index)
        
        // Notify delegate
        delegate?.didSelectNavigationItem(item)
        
        // Haptic feedback
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
            impactFeedback.impactOccurred()
        }
    }
    
    private func updateSelection(to index: Int) {
        selectedIndex = index
        
        // Update mobile navigation
        for (buttonIndex, button) in navigationStackView.arrangedSubviews.enumerated() {
            if let button = button as? UIButton {
                button.isSelected = (buttonIndex == index)
            }
        }
        
        // Update desktop navigation
        for (buttonIndex, button) in topNavigationView.subviews.first?.subviews ?? [] {
            if let button = button as? UIButton {
                button.isSelected = (buttonIndex == index)
            }
        }
    }
    
    // MARK: - Public Methods
    func setSelectedIndex(_ index: Int, animated: Bool = true) {
        guard index < navigationItems.count else { return }
        
        if animated {
            UIView.animate(withDuration: 0.3) {
                self.updateSelection(to: index)
            }
        } else {
            updateSelection(to: index)
        }
    }
    
    func updateBadge(for identifier: String, badge: String?) {
        guard let index = navigationItems.firstIndex(where: { $0.identifier == identifier }) else { return }
        
        // Update model
        navigationItems[index] = NavigationItem(
            title: navigationItems[index].title,
            icon: navigationItems[index].icon,
            selectedIcon: navigationItems[index].selectedIcon,
            identifier: navigationItems[index].identifier,
            badge: badge,
            isEnabled: navigationItems[index].isEnabled
        )
        
        // Update UI
        updateBadgeInUI(for: index, badge: badge)
    }
    
    private func updateBadgeInUI(for index: Int, badge: String?) {
        // Update mobile navigation
        if index < navigationStackView.arrangedSubviews.count {
            let button = navigationStackView.arrangedSubviews[index] as? UIButton
            updateBadgeInButton(button, badge: badge)
        }
        
        // Update desktop navigation
        if index < topNavigationView.subviews.first?.subviews.count ?? 0 {
            let button = topNavigationView.subviews.first?.subviews[index] as? UIButton
            updateBadgeInButton(button, badge: badge)
        }
    }
    
    private func updateBadgeInButton(_ button: UIButton?, badge: String?) {
        // Remove existing badge
        button?.subviews.forEach { subview in
            if subview is UILabel {
                subview.removeFromSuperview()
            }
        }
        
        // Add new badge if needed
        if let badge = badge {
            addBadge(to: button!, text: badge)
        }
    }
}

// MARK: - Navigation Configuration
struct NavigationConfig {
    let bottomBarHeight: CGFloat = 80
    let topBarHeight: CGFloat = 60
    let cornerRadius: CGFloat = 20
    let blurOpacity: CGFloat = 0.8
    let animationDuration: TimeInterval = 0.3
    let hapticFeedbackEnabled: Bool = true
}

// MARK: - Navigation Factory
class NavigationFactory {
    
    static func createALADDINNavigation() -> [NavigationItem] {
        return [
            NavigationItem(
                title: "Главная",
                icon: "house.fill",
                selectedIcon: "house.fill",
                identifier: "home"
            ),
            NavigationItem(
                title: "Защита",
                icon: "shield.fill",
                selectedIcon: "shield.fill",
                identifier: "security"
            ),
            NavigationItem(
                title: "Семья",
                icon: "person.3.fill",
                selectedIcon: "person.3.fill",
                identifier: "family"
            ),
            NavigationItem(
                title: "Аналитика",
                icon: "chart.bar.fill",
                selectedIcon: "chart.bar.fill",
                identifier: "analytics"
            ),
            NavigationItem(
                title: "Настройки",
                icon: "gearshape.fill",
                selectedIcon: "gearshape.fill",
                identifier: "settings"
            )
        ]
    }
    
    static func createVPNNavigation() -> [NavigationItem] {
        return [
            NavigationItem(
                title: "Подключение",
                icon: "wifi",
                selectedIcon: "wifi",
                identifier: "connection"
            ),
            NavigationItem(
                title: "Серверы",
                icon: "server.rack",
                selectedIcon: "server.rack",
                identifier: "servers"
            ),
            NavigationItem(
                title: "Статистика",
                icon: "chart.line.uptrend.xyaxis",
                selectedIcon: "chart.line.uptrend.xyaxis",
                identifier: "statistics"
            ),
            NavigationItem(
                title: "Настройки",
                icon: "gearshape.fill",
                selectedIcon: "gearshape.fill",
                identifier: "settings"
            )
        ]
    }
}

// MARK: - Navigation Extensions
extension MobileNavigationController {
    
    func addNavigationItem(_ item: NavigationItem) {
        navigationItems.append(item)
        
        // Add to mobile navigation
        let mobileButton = createMobileNavigationButton(for: item, at: navigationItems.count - 1)
        navigationStackView.addArrangedSubview(mobileButton)
        
        // Add to desktop navigation
        let desktopButton = createDesktopNavigationButton(for: item, at: navigationItems.count - 1)
        if let horizontalStackView = topNavigationView.subviews.first as? UIStackView {
            horizontalStackView.addArrangedSubview(desktopButton)
        }
    }
    
    func removeNavigationItem(with identifier: String) {
        guard let index = navigationItems.firstIndex(where: { $0.identifier == identifier }) else { return }
        
        navigationItems.remove(at: index)
        
        // Remove from mobile navigation
        if index < navigationStackView.arrangedSubviews.count {
            navigationStackView.arrangedSubviews[index].removeFromSuperview()
        }
        
        // Remove from desktop navigation
        if let horizontalStackView = topNavigationView.subviews.first as? UIStackView,
           index < horizontalStackView.arrangedSubviews.count {
            horizontalStackView.arrangedSubviews[index].removeFromSuperview()
        }
        
        // Update tags
        updateButtonTags()
    }
    
    private func updateButtonTags() {
        for (index, button) in navigationStackView.arrangedSubviews.enumerated() {
            if let button = button as? UIButton {
                button.tag = index
            }
        }
        
        if let horizontalStackView = topNavigationView.subviews.first as? UIStackView {
            for (index, button) in horizontalStackView.arrangedSubviews.enumerated() {
                if let button = button as? UIButton {
                    button.tag = index
                }
            }
        }
    }
}


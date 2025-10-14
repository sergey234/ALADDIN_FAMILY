//
//  GlassmorphismEffects.swift
//  ALADDIN Mobile Security
//
//  Glassmorphism UI Effects for iOS
//  Modern glass-like visual effects with blur and transparency
//
//  Created by ALADDIN Security Team
//  Date: 2025-01-27
//  Version: 1.0
//

import UIKit

// MARK: - Glassmorphism Effect Types
enum GlassmorphismStyle {
    case light      // Light glass effect
    case medium     // Medium glass effect
    case heavy      // Heavy glass effect
    case frosted    // Frosted glass effect
    case crystal    // Crystal clear effect
    case storm      // Storm sky themed effect
}

// MARK: - Glassmorphism Configuration
struct GlassmorphismConfig {
    let style: GlassmorphismStyle
    let blurRadius: CGFloat
    let opacity: CGFloat
    let cornerRadius: CGFloat
    let borderWidth: CGFloat
    let borderColor: UIColor
    let shadowRadius: CGFloat
    let shadowOpacity: Float
    let shadowOffset: CGSize
    let shadowColor: UIColor
    
    static let light = GlassmorphismConfig(
        style: .light,
        blurRadius: 10,
        opacity: 0.1,
        cornerRadius: 12,
        borderWidth: 1,
        borderColor: UIColor.white.withAlphaComponent(0.2),
        shadowRadius: 8,
        shadowOpacity: 0.1,
        shadowOffset: CGSize(width: 0, height: 4),
        shadowColor: UIColor.black
    )
    
    static let medium = GlassmorphismConfig(
        style: .medium,
        blurRadius: 20,
        opacity: 0.15,
        cornerRadius: 16,
        borderWidth: 1.5,
        borderColor: UIColor.white.withAlphaComponent(0.3),
        shadowRadius: 12,
        shadowOpacity: 0.15,
        shadowOffset: CGSize(width: 0, height: 6),
        shadowColor: UIColor.black
    )
    
    static let heavy = GlassmorphismConfig(
        style: .heavy,
        blurRadius: 30,
        opacity: 0.2,
        cornerRadius: 20,
        borderWidth: 2,
        borderColor: UIColor.white.withAlphaComponent(0.4),
        shadowRadius: 16,
        shadowOpacity: 0.2,
        shadowOffset: CGSize(width: 0, height: 8),
        shadowColor: UIColor.black
    )
    
    static let frosted = GlassmorphismConfig(
        style: .frosted,
        blurRadius: 25,
        opacity: 0.25,
        cornerRadius: 18,
        borderWidth: 1.5,
        borderColor: UIColor.white.withAlphaComponent(0.5),
        shadowRadius: 14,
        shadowOpacity: 0.18,
        shadowOffset: CGSize(width: 0, height: 7),
        shadowColor: UIColor.black
    )
    
    static let crystal = GlassmorphismConfig(
        style: .crystal,
        blurRadius: 15,
        opacity: 0.08,
        cornerRadius: 14,
        borderWidth: 0.5,
        borderColor: UIColor.white.withAlphaComponent(0.6),
        shadowRadius: 10,
        shadowOpacity: 0.12,
        shadowOffset: CGSize(width: 0, height: 5),
        shadowColor: UIColor.black
    )
    
    static let storm = GlassmorphismConfig(
        style: .storm,
        blurRadius: 22,
        opacity: 0.18,
        cornerRadius: 16,
        borderWidth: 1.5,
        borderColor: UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 0.3), // Golden accent
        shadowRadius: 13,
        shadowOpacity: 0.16,
        shadowOffset: CGSize(width: 0, height: 6),
        shadowColor: UIColor(red: 0.04, green: 0.07, blue: 0.16, alpha: 0.3) // Storm sky color
    )
}

// MARK: - Glassmorphism View
class GlassmorphismView: UIView {
    
    private var blurEffectView: UIVisualEffectView?
    private var config: GlassmorphismConfig
    
    init(config: GlassmorphismConfig = .medium) {
        self.config = config
        super.init(frame: .zero)
        setupGlassmorphismEffect()
    }
    
    required init?(coder: NSCoder) {
        self.config = .medium
        super.init(coder: coder)
        setupGlassmorphismEffect()
    }
    
    private func setupGlassmorphismEffect() {
        // Create blur effect
        let blurEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        blurEffectView = UIVisualEffectView(effect: blurEffect)
        
        guard let blurEffectView = blurEffectView else { return }
        
        // Configure blur view
        blurEffectView.translatesAutoresizingMaskIntoConstraints = false
        addSubview(blurEffectView)
        
        // Set constraints
        NSLayoutConstraint.activate([
            blurEffectView.topAnchor.constraint(equalTo: topAnchor),
            blurEffectView.leadingAnchor.constraint(equalTo: leadingAnchor),
            blurEffectView.trailingAnchor.constraint(equalTo: trailingAnchor),
            blurEffectView.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
        
        // Apply glassmorphism styling
        applyGlassmorphismStyle()
    }
    
    private func applyGlassmorphismStyle() {
        // Background
        backgroundColor = UIColor.clear
        
        // Corner radius
        layer.cornerRadius = config.cornerRadius
        clipsToBounds = true
        
        // Border
        layer.borderWidth = config.borderWidth
        layer.borderColor = config.borderColor.cgColor
        
        // Shadow
        layer.shadowRadius = config.shadowRadius
        layer.shadowOpacity = config.shadowOpacity
        layer.shadowOffset = config.shadowOffset
        layer.shadowColor = config.shadowColor.cgColor
        
        // Blur effect opacity
        blurEffectView?.alpha = config.opacity
    }
    
    func updateConfig(_ newConfig: GlassmorphismConfig) {
        self.config = newConfig
        applyGlassmorphismStyle()
    }
    
    func animateGlassmorphism(to newConfig: GlassmorphismConfig, duration: TimeInterval = 0.3) {
        UIView.animate(withDuration: duration, delay: 0, options: [.curveEaseInOut], animations: {
            self.updateConfig(newConfig)
        })
    }
}

// MARK: - Glassmorphism Button
class GlassmorphismButton: UIButton {
    
    private var config: GlassmorphismConfig
    private var glassmorphismView: GlassmorphismView?
    
    init(config: GlassmorphismConfig = .medium) {
        self.config = config
        super.init(frame: .zero)
        setupGlassmorphismButton()
    }
    
    required init?(coder: NSCoder) {
        self.config = .medium
        super.init(coder: coder)
        setupGlassmorphismButton()
    }
    
    private func setupGlassmorphismButton() {
        // Create glassmorphism view
        glassmorphismView = GlassmorphismView(config: config)
        
        guard let glassmorphismView = glassmorphismView else { return }
        
        // Add as background
        insertSubview(glassmorphismView, at: 0)
        glassmorphismView.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            glassmorphismView.topAnchor.constraint(equalTo: topAnchor),
            glassmorphismView.leadingAnchor.constraint(equalTo: leadingAnchor),
            glassmorphismView.trailingAnchor.constraint(equalTo: trailingAnchor),
            glassmorphismView.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
        
        // Button styling
        setTitleColor(.white, for: .normal)
        titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        
        // Add touch effects
        addTarget(self, action: #selector(touchDown), for: .touchDown)
        addTarget(self, action: #selector(touchUp), for: [.touchUpInside, .touchUpOutside, .touchCancel])
    }
    
    @objc private func touchDown() {
        UIView.animate(withDuration: 0.1) {
            self.transform = CGAffineTransform(scaleX: 0.95, y: 0.95)
            self.alpha = 0.8
        }
    }
    
    @objc private func touchUp() {
        UIView.animate(withDuration: 0.1) {
            self.transform = .identity
            self.alpha = 1.0
        }
    }
    
    func updateGlassmorphismConfig(_ newConfig: GlassmorphismConfig) {
        glassmorphismView?.updateConfig(newConfig)
    }
}

// MARK: - Glassmorphism Card
class GlassmorphismCard: UIView {
    
    private var config: GlassmorphismConfig
    private var glassmorphismView: GlassmorphismView?
    private var contentView: UIView = UIView()
    
    init(config: GlassmorphismConfig = .medium) {
        self.config = config
        super.init(frame: .zero)
        setupGlassmorphismCard()
    }
    
    required init?(coder: NSCoder) {
        self.config = .medium
        super.init(coder: coder)
        setupGlassmorphismCard()
    }
    
    private func setupGlassmorphismCard() {
        // Create glassmorphism view
        glassmorphismView = GlassmorphismView(config: config)
        
        guard let glassmorphismView = glassmorphismView else { return }
        
        // Add glassmorphism as background
        insertSubview(glassmorphismView, at: 0)
        glassmorphismView.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            glassmorphismView.topAnchor.constraint(equalTo: topAnchor),
            glassmorphismView.leadingAnchor.constraint(equalTo: leadingAnchor),
            glassmorphismView.trailingAnchor.constraint(equalTo: trailingAnchor),
            glassmorphismView.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
        
        // Setup content view
        contentView.translatesAutoresizingMaskIntoConstraints = false
        addSubview(contentView)
        
        NSLayoutConstraint.activate([
            contentView.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            contentView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            contentView.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            contentView.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])
    }
    
    func addContent(_ view: UIView) {
        contentView.addSubview(view)
        view.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            view.topAnchor.constraint(equalTo: contentView.topAnchor),
            view.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            view.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            view.bottomAnchor.constraint(equalTo: contentView.bottomAnchor)
        ])
    }
    
    func updateGlassmorphismConfig(_ newConfig: GlassmorphismConfig) {
        glassmorphismView?.updateConfig(newConfig)
    }
}

// MARK: - Glassmorphism Navigation Bar
extension UINavigationBar {
    
    func applyGlassmorphism(config: GlassmorphismConfig = .light) {
        // Make navigation bar transparent
        setBackgroundImage(UIImage(), for: .default)
        shadowImage = UIImage()
        isTranslucent = true
        
        // Create glassmorphism effect
        let blurEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        let blurEffectView = UIVisualEffectView(effect: blurEffect)
        blurEffectView.alpha = config.opacity
        blurEffectView.translatesAutoresizingMaskIntoConstraints = false
        
        // Add blur effect to navigation bar
        insertSubview(blurEffectView, at: 0)
        
        NSLayoutConstraint.activate([
            blurEffectView.topAnchor.constraint(equalTo: topAnchor),
            blurEffectView.leadingAnchor.constraint(equalTo: leadingAnchor),
            blurEffectView.trailingAnchor.constraint(equalTo: trailingAnchor),
            blurEffectView.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
        
        // Apply styling
        layer.cornerRadius = config.cornerRadius
        layer.borderWidth = config.borderWidth
        layer.borderColor = config.borderColor.cgColor
    }
}

// MARK: - Glassmorphism Tab Bar
extension UITabBar {
    
    func applyGlassmorphism(config: GlassmorphismConfig = .light) {
        // Make tab bar transparent
        backgroundImage = UIImage()
        shadowImage = UIImage()
        isTranslucent = true
        
        // Create glassmorphism effect
        let blurEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        let blurEffectView = UIVisualEffectView(effect: blurEffect)
        blurEffectView.alpha = config.opacity
        blurEffectView.translatesAutoresizingMaskIntoConstraints = false
        
        // Add blur effect to tab bar
        insertSubview(blurEffectView, at: 0)
        
        NSLayoutConstraint.activate([
            blurEffectView.topAnchor.constraint(equalTo: topAnchor),
            blurEffectView.leadingAnchor.constraint(equalTo: leadingAnchor),
            blurEffectView.trailingAnchor.constraint(equalTo: trailingAnchor),
            blurEffectView.bottomAnchor.constraint(equalTo: bottomAnchor)
        ])
        
        // Apply styling
        layer.cornerRadius = config.cornerRadius
        layer.borderWidth = config.borderWidth
        layer.borderColor = config.borderColor.cgColor
    }
}

// MARK: - Glassmorphism Utility Functions
class GlassmorphismUtils {
    
    static func createGlassmorphismBackground(for view: UIView, config: GlassmorphismConfig = .medium) {
        let glassmorphismView = GlassmorphismView(config: config)
        view.insertSubview(glassmorphismView, at: 0)
        
        glassmorphismView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            glassmorphismView.topAnchor.constraint(equalTo: view.topAnchor),
            glassmorphismView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            glassmorphismView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            glassmorphismView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }
    
    static func animateGlassmorphismTransition(from view1: UIView, to view2: UIView, duration: TimeInterval = 0.5) {
        UIView.transition(from: view1, to: view2, duration: duration, options: [.transitionCrossDissolve], completion: nil)
    }
    
    static func createGradientGlassmorphism(for view: UIView, colors: [UIColor], config: GlassmorphismConfig = .medium) {
        // Create gradient layer
        let gradientLayer = CAGradientLayer()
        gradientLayer.colors = colors.map { $0.cgColor }
        gradientLayer.locations = [0.0, 1.0]
        gradientLayer.startPoint = CGPoint(x: 0, y: 0)
        gradientLayer.endPoint = CGPoint(x: 1, y: 1)
        
        // Create glassmorphism view
        let glassmorphismView = GlassmorphismView(config: config)
        glassmorphismView.layer.insertSublayer(gradientLayer, at: 0)
        
        view.insertSubview(glassmorphismView, at: 0)
        glassmorphismView.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            glassmorphismView.topAnchor.constraint(equalTo: view.topAnchor),
            glassmorphismView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            glassmorphismView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            glassmorphismView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
        
        // Update gradient frame
        DispatchQueue.main.async {
            gradientLayer.frame = glassmorphismView.bounds
        }
    }
}

// MARK: - Storm Sky Glassmorphism Theme
extension GlassmorphismConfig {
    
    static let stormSkyLight = GlassmorphismConfig(
        style: .storm,
        blurRadius: 15,
        opacity: 0.12,
        cornerRadius: 12,
        borderWidth: 1,
        borderColor: UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 0.2),
        shadowRadius: 8,
        shadowOpacity: 0.1,
        shadowOffset: CGSize(width: 0, height: 4),
        shadowColor: UIColor(red: 0.04, green: 0.07, blue: 0.16, alpha: 0.2)
    )
    
    static let stormSkyMedium = GlassmorphismConfig(
        style: .storm,
        blurRadius: 22,
        opacity: 0.18,
        cornerRadius: 16,
        borderWidth: 1.5,
        borderColor: UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 0.3),
        shadowRadius: 13,
        shadowOpacity: 0.16,
        shadowOffset: CGSize(width: 0, height: 6),
        shadowColor: UIColor(red: 0.04, green: 0.07, blue: 0.16, alpha: 0.3)
    )
    
    static let stormSkyHeavy = GlassmorphismConfig(
        style: .storm,
        blurRadius: 30,
        opacity: 0.25,
        cornerRadius: 20,
        borderWidth: 2,
        borderColor: UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 0.4),
        shadowRadius: 18,
        shadowOpacity: 0.22,
        shadowOffset: CGSize(width: 0, height: 8),
        shadowColor: UIColor(red: 0.04, green: 0.07, blue: 0.16, alpha: 0.4)
    )
}


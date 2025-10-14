//
//  TouchFriendlyElements.swift
//  ALADDIN Mobile Security
//
//  Touch-Friendly UI Elements for iOS
//  Optimized for mobile touch interaction with proper sizing and feedback
//
//  Created by ALADDIN Security Team
//  Date: 2025-01-27
//  Version: 1.0
//

import UIKit

// MARK: - Touch-Friendly Configuration
struct TouchFriendlyConfig {
    let minimumTouchSize: CGFloat = 44.0  // Apple's minimum recommended size
    let preferredTouchSize: CGFloat = 50.0  // Preferred size for better UX
    let largeTouchSize: CGFloat = 60.0  // For important actions
    let touchPadding: CGFloat = 8.0  // Padding around touch targets
    let touchFeedbackDuration: TimeInterval = 0.1  // Haptic feedback duration
    let animationDuration: TimeInterval = 0.2  // Touch animation duration
    let scaleFactor: CGFloat = 0.95  // Scale factor for touch feedback
    let alphaFactor: CGFloat = 0.8  // Alpha factor for touch feedback
}

// MARK: - Touch-Friendly Button
class TouchFriendlyButton: UIButton {
    
    private let config = TouchFriendlyConfig()
    private var originalTransform: CGAffineTransform = .identity
    private var originalAlpha: CGFloat = 1.0
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupTouchFriendlyButton()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTouchFriendlyButton()
    }
    
    private func setupTouchFriendlyButton() {
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
        
        // Add touch feedback
        addTarget(self, action: #selector(touchDown), for: .touchDown)
        addTarget(self, action: #selector(touchUp), for: [.touchUpInside, .touchUpOutside, .touchCancel])
        
        // Configure button appearance
        configureAppearance()
    }
    
    private func configureAppearance() {
        // Set title color
        setTitleColor(.white, for: .normal)
        setTitleColor(.white.withAlphaComponent(0.7), for: .highlighted)
        setTitleColor(.white.withAlphaComponent(0.5), for: .disabled)
        
        // Set title font
        titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        titleLabel?.textAlignment = .center
        
        // Set content insets for better touch area
        contentEdgeInsets = UIEdgeInsets(
            top: config.touchPadding,
            left: config.touchPadding,
            bottom: config.touchPadding,
            right: config.touchPadding
        )
        
        // Set image insets
        imageEdgeInsets = UIEdgeInsets(
            top: 0,
            left: -8,
            bottom: 0,
            right: 8
        )
        
        titleEdgeInsets = UIEdgeInsets(
            top: 0,
            left: 8,
            bottom: 0,
            right: -8
        )
    }
    
    @objc private func touchDown() {
        // Store original values
        originalTransform = transform
        originalAlpha = alpha
        
        // Animate touch feedback
        UIView.animate(withDuration: config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
            self.transform = CGAffineTransform(scaleX: self.config.scaleFactor, y: self.config.scaleFactor)
            self.alpha = self.config.alphaFactor
        })
        
        // Haptic feedback
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
            impactFeedback.impactOccurred()
        }
    }
    
    @objc private func touchUp() {
        // Animate back to original state
        UIView.animate(withDuration: config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
            self.transform = self.originalTransform
            self.alpha = self.originalAlpha
        })
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
    }
}

// MARK: - Touch-Friendly Card
class TouchFriendlyCard: UIView {
    
    private let config = TouchFriendlyConfig()
    private var originalTransform: CGAffineTransform = .identity
    private var originalAlpha: CGFloat = 1.0
    private var tapGesture: UITapGestureRecognizer?
    
    var onTap: (() -> Void)?
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupTouchFriendlyCard()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTouchFriendlyCard()
    }
    
    private func setupTouchFriendlyCard() {
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
        
        // Add tap gesture
        tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap))
        addGestureRecognizer(tapGesture!)
        
        // Configure appearance
        configureAppearance()
    }
    
    private func configureAppearance() {
        // Set background
        backgroundColor = UIColor.white.withAlphaComponent(0.1)
        
        // Set corner radius
        layer.cornerRadius = 12
        clipsToBounds = true
        
        // Set border
        layer.borderWidth = 1
        layer.borderColor = UIColor.white.withAlphaComponent(0.2).cgColor
        
        // Set shadow
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 2)
        layer.shadowRadius = 8
        layer.shadowOpacity = 0.1
        
        // Set padding
        layoutMargins = UIEdgeInsets(
            top: config.touchPadding,
            left: config.touchPadding,
            bottom: config.touchPadding,
            right: config.touchPadding
        )
    }
    
    @objc private func handleTap() {
        // Animate touch feedback
        UIView.animate(withDuration: config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
            self.transform = CGAffineTransform(scaleX: self.config.scaleFactor, y: self.config.scaleFactor)
            self.alpha = self.config.alphaFactor
        }) { _ in
            // Animate back
            UIView.animate(withDuration: self.config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
                self.transform = self.originalTransform
                self.alpha = self.originalAlpha
            })
        }
        
        // Haptic feedback
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
            impactFeedback.impactOccurred()
        }
        
        // Call completion
        onTap?()
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
    }
}

// MARK: - Touch-Friendly Switch
class TouchFriendlySwitch: UISwitch {
    
    private let config = TouchFriendlyConfig()
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupTouchFriendlySwitch()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTouchFriendlySwitch()
    }
    
    private func setupTouchFriendlySwitch() {
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
        
        // Add touch feedback
        addTarget(self, action: #selector(valueChanged), for: .valueChanged)
        
        // Configure appearance
        configureAppearance()
    }
    
    private func configureAppearance() {
        // Set colors
        onTintColor = UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 1.0) // Golden
        thumbTintColor = .white
        
        // Set scale
        transform = CGAffineTransform(scaleX: 1.2, y: 1.2)
    }
    
    @objc private func valueChanged() {
        // Haptic feedback
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
            impactFeedback.impactOccurred()
        }
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
    }
}

// MARK: - Touch-Friendly Slider
class TouchFriendlySlider: UISlider {
    
    private let config = TouchFriendlyConfig()
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupTouchFriendlySlider()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTouchFriendlySlider()
    }
    
    private func setupTouchFriendlySlider() {
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
        
        // Add touch feedback
        addTarget(self, action: #selector(valueChanged), for: .valueChanged)
        
        // Configure appearance
        configureAppearance()
    }
    
    private func configureAppearance() {
        // Set colors
        minimumTrackTintColor = UIColor(red: 0.96, green: 0.58, blue: 0.04, alpha: 1.0) // Golden
        maximumTrackTintColor = UIColor.white.withAlphaComponent(0.3)
        thumbTintColor = .white
        
        // Set thumb image for better touch area
        let thumbSize = CGSize(width: 30, height: 30)
        let thumbImage = createThumbImage(size: thumbSize)
        setThumbImage(thumbImage, for: .normal)
        setThumbImage(thumbImage, for: .highlighted)
    }
    
    private func createThumbImage(size: CGSize) -> UIImage? {
        UIGraphicsBeginImageContextWithOptions(size, false, 0)
        defer { UIGraphicsEndImageContext() }
        
        let context = UIGraphicsGetCurrentContext()
        context?.setFillColor(UIColor.white.cgColor)
        context?.fillEllipse(in: CGRect(origin: .zero, size: size))
        
        return UIGraphicsGetImageFromCurrentImageContext()
    }
    
    @objc private func valueChanged() {
        // Haptic feedback
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
            impactFeedback.impactOccurred()
        }
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
    }
}

// MARK: - Touch-Friendly Text Field
class TouchFriendlyTextField: UITextField {
    
    private let config = TouchFriendlyConfig()
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupTouchFriendlyTextField()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTouchFriendlyTextField()
    }
    
    private func setupTouchFriendlyTextField() {
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
        
        // Configure appearance
        configureAppearance()
    }
    
    private func configureAppearance() {
        // Set background
        backgroundColor = UIColor.white.withAlphaComponent(0.1)
        
        // Set border
        layer.borderWidth = 1
        layer.borderColor = UIColor.white.withAlphaComponent(0.2).cgColor
        layer.cornerRadius = 8
        
        // Set text color
        textColor = .white
        attributedPlaceholder = NSAttributedString(
            string: placeholder ?? "",
            attributes: [NSAttributedString.Key.foregroundColor: UIColor.white.withAlphaComponent(0.6)]
        )
        
        // Set font
        font = UIFont.systemFont(ofSize: 16)
        
        // Set padding
        leftView = UIView(frame: CGRect(x: 0, y: 0, width: 12, height: 0))
        leftViewMode = .always
        rightView = UIView(frame: CGRect(x: 0, y: 0, width: 12, height: 0))
        rightViewMode = .always
        
        // Set keyboard type
        keyboardType = .default
        returnKeyType = .done
        autocorrectionType = .no
        autocapitalizationType = .none
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
    }
}

// MARK: - Touch-Friendly Collection View Cell
class TouchFriendlyCollectionViewCell: UICollectionViewCell {
    
    private let config = TouchFriendlyConfig()
    private var originalTransform: CGAffineTransform = .identity
    private var originalAlpha: CGFloat = 1.0
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupTouchFriendlyCell()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTouchFriendlyCell()
    }
    
    private func setupTouchFriendlyCell() {
        // Configure appearance
        configureAppearance()
    }
    
    private func configureAppearance() {
        // Set background
        backgroundColor = UIColor.white.withAlphaComponent(0.1)
        
        // Set corner radius
        layer.cornerRadius = 12
        clipsToBounds = true
        
        // Set border
        layer.borderWidth = 1
        layer.borderColor = UIColor.white.withAlphaComponent(0.2).cgColor
        
        // Set shadow
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 2)
        layer.shadowRadius = 8
        layer.shadowOpacity = 0.1
        
        // Set padding
        layoutMargins = UIEdgeInsets(
            top: config.touchPadding,
            left: config.touchPadding,
            bottom: config.touchPadding,
            right: config.touchPadding
        )
    }
    
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesBegan(touches, with: event)
        
        // Store original values
        originalTransform = transform
        originalAlpha = alpha
        
        // Animate touch feedback
        UIView.animate(withDuration: config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
            self.transform = CGAffineTransform(scaleX: self.config.scaleFactor, y: self.config.scaleFactor)
            self.alpha = self.config.alphaFactor
        })
        
        // Haptic feedback
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
            impactFeedback.impactOccurred()
        }
    }
    
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesEnded(touches, with: event)
        
        // Animate back to original state
        UIView.animate(withDuration: config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
            self.transform = self.originalTransform
            self.alpha = self.originalAlpha
        })
    }
    
    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesCancelled(touches, with: event)
        
        // Animate back to original state
        UIView.animate(withDuration: config.animationDuration, delay: 0, options: [.curveEaseInOut], animations: {
            self.transform = self.originalTransform
            self.alpha = self.originalAlpha
        })
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        // Ensure minimum touch size
        frame.size = CGSize(
            width: max(frame.width, config.minimumTouchSize),
            height: max(frame.height, config.minimumTouchSize)
        )
    }
}

// MARK: - Touch-Friendly Utility Functions
class TouchFriendlyUtils {
    
    static func ensureMinimumTouchSize(for view: UIView, minimumSize: CGFloat = 44.0) {
        view.frame.size = CGSize(
            width: max(view.frame.width, minimumSize),
            height: max(view.frame.height, minimumSize)
        )
    }
    
    static func addTouchFeedback(to view: UIView, scaleFactor: CGFloat = 0.95, alphaFactor: CGFloat = 0.8) {
        let originalTransform = view.transform
        let originalAlpha = view.alpha
        
        // Add touch down effect
        let touchDownGesture = UILongPressGestureRecognizer(target: self, action: #selector(handleTouchDown(_:)))
        touchDownGesture.minimumPressDuration = 0
        view.addGestureRecognizer(touchDownGesture)
    }
    
    @objc private static func handleTouchDown(_ gesture: UILongPressGestureRecognizer) {
        guard let view = gesture.view else { return }
        
        switch gesture.state {
        case .began:
            UIView.animate(withDuration: 0.1, delay: 0, options: [.curveEaseInOut], animations: {
                view.transform = CGAffineTransform(scaleX: 0.95, y: 0.95)
                view.alpha = 0.8
            })
        case .ended, .cancelled:
            UIView.animate(withDuration: 0.1, delay: 0, options: [.curveEaseInOut], animations: {
                view.transform = .identity
                view.alpha = 1.0
            })
        default:
            break
        }
    }
    
    static func addHapticFeedback(to view: UIView, style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
        if #available(iOS 10.0, *) {
            let impactFeedback = UIImpactFeedbackGenerator(style: style)
            impactFeedback.impactOccurred()
        }
    }
}

// MARK: - Touch-Friendly Extensions
extension UIView {
    
    func makeTouchFriendly(minimumSize: CGFloat = 44.0) {
        TouchFriendlyUtils.ensureMinimumTouchSize(for: self, minimumSize: minimumSize)
    }
    
    func addTouchFeedback(scaleFactor: CGFloat = 0.95, alphaFactor: CGFloat = 0.8) {
        TouchFriendlyUtils.addTouchFeedback(to: self, scaleFactor: scaleFactor, alphaFactor: alphaFactor)
    }
    
    func addHapticFeedback(style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
        TouchFriendlyUtils.addHapticFeedback(to: self, style: style)
    }
}

// MARK: - Touch-Friendly Constants
struct TouchFriendlyConstants {
    static let minimumTouchSize: CGFloat = 44.0
    static let preferredTouchSize: CGFloat = 50.0
    static let largeTouchSize: CGFloat = 60.0
    static let touchPadding: CGFloat = 8.0
    static let animationDuration: TimeInterval = 0.2
    static let scaleFactor: CGFloat = 0.95
    static let alphaFactor: CGFloat = 0.8
}


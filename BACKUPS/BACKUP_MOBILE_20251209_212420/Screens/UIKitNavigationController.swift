import UIKit
import SwiftUI

// MARK: - UIKit Navigation Controller для решения проблемы навигации
class UIKitNavigationController: UINavigationController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    private func setupUI() {
        // Создаем простой тестовый view controller
        let testViewController = UIViewController()
        testViewController.view.backgroundColor = UIColor.systemBlue
        
        // Добавляем кнопку
        let button = UIButton(type: .system)
        button.setTitle("ТЕСТ UIKit КНОПКА", for: .normal)
        button.titleLabel?.font = UIFont.boldSystemFont(ofSize: 18)
        button.backgroundColor = UIColor.red
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 10
        button.frame = CGRect(x: 50, y: 200, width: 200, height: 50)
        button.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)
        
        testViewController.view.addSubview(button)
        
        // Устанавливаем root view controller
        self.setViewControllers([testViewController], animated: false)
    }
    
    @objc private func buttonTapped() {
        print("🚨 UIKit кнопка нажата!")
        
        // Создаем alert
        let alert = UIAlertController(title: "UIKit Test", message: "UIKit кнопка работает!", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        
        self.present(alert, animated: true)
    }
}

// MARK: - SwiftUI Wrapper для UIKit
struct UIKitNavigationView: UIViewControllerRepresentable {
    
    func makeUIViewController(context: Context) -> UIKitNavigationController {
        return UIKitNavigationController()
    }
    
    func updateUIViewController(_ uiViewController: UIKitNavigationController, context: Context) {
        // Обновления не нужны
    }
}



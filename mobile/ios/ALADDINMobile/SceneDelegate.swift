import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        // Use this method to optionally configure and attach the UIWindow `window` to the provided UIWindowScene `scene`.
        // If using a storyboard, the `window` property will automatically be set and attached to the scene.
        // This delegate does not imply the connecting scene or session are new (see `application:configurationForConnectingSceneSession` instead).
        guard let windowScene = (scene as? UIWindowScene) else { return }
        
        window = UIWindow(windowScene: windowScene)
        
        // Создание главного контроллера с навигацией
        let mainViewController = createMainViewController()
        window?.rootViewController = mainViewController
        window?.makeKeyAndVisible()
        
        // Настройка окна с цветовой схемой "Грозовое небо"
        setupWindowAppearance()
    }

    func sceneDidDisconnect(_ scene: UIScene) {
        // Called as the scene is being released by the system.
        // This occurs shortly after the scene enters the background, or when its session is discarded.
        // Release any resources associated with this scene that can be re-created the next time the scene connects.
        // The scene may re-connect later, as its session was not necessarily discarded (see `application:didDiscardSceneSessions` instead).
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
        // Called when the scene has moved from an inactive state to an active state.
        // Use this method to restart any tasks that were paused (or not yet started) when the scene was inactive.
        
        // Проверка безопасности при активации
        checkSecurityStatus()
    }

    func sceneWillResignActive(_ scene: UIScene) {
        // Called when the scene will move from an active state to an inactive state.
        // This may occur due to temporary interruptions (e.g. an incoming phone call).
        
        // Сохранение состояния безопасности
        saveSecurityState()
    }

    func sceneWillEnterForeground(_ scene: UIScene) {
        // Called as the scene transitions from the background to the foreground.
        // Use this method to undo the changes made on entering the background.
        
        // Обновление статуса защиты
        updateProtectionStatus()
    }

    func sceneDidEnterBackground(_ scene: UIScene) {
        // Called as the scene transitions from the foreground to the background.
        // Use this method to save data, release shared resources, and store enough scene-specific state information
        // to restore the scene back to its current state.
        
        // Активация фоновой защиты
        activateBackgroundProtection()
    }
    
    // MARK: - Private Methods
    
    private func createMainViewController() -> UIViewController {
        // Создание главного контроллера с TabBar навигацией
        let tabBarController = UITabBarController()
        
        // Главный экран
        let mainVC = createMainScreenViewController()
        mainVC.tabBarItem = UITabBarItem(title: "Главная", image: UIImage(systemName: "house.fill"), tag: 0)
        
        // Экран защиты
        let protectionVC = createProtectionViewController()
        protectionVC.tabBarItem = UITabBarItem(title: "Защита", image: UIImage(systemName: "shield.fill"), tag: 1)
        
        // Экран семьи
        let familyVC = createFamilyViewController()
        familyVC.tabBarItem = UITabBarItem(title: "Семья", image: UIImage(systemName: "person.3.fill"), tag: 2)
        
        // Экран аналитики
        let analyticsVC = createAnalyticsViewController()
        analyticsVC.tabBarItem = UITabBarItem(title: "Аналитика", image: UIImage(systemName: "chart.bar.fill"), tag: 3)
        
        // AI Помощник
        let aiVC = createAIAssistantViewController()
        aiVC.tabBarItem = UITabBarItem(title: "AI", image: UIImage(systemName: "brain.head.profile"), tag: 4)
        
        tabBarController.viewControllers = [mainVC, protectionVC, familyVC, analyticsVC, aiVC]
        
        return tabBarController
    }
    
    private func createMainScreenViewController() -> UIViewController {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        return storyboard.instantiateViewController(withIdentifier: "MainViewController")
    }
    
    private func createProtectionViewController() -> UIViewController {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        return storyboard.instantiateViewController(withIdentifier: "ProtectionViewController")
    }
    
    private func createFamilyViewController() -> UIViewController {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        return storyboard.instantiateViewController(withIdentifier: "FamilyViewController")
    }
    
    private func createAnalyticsViewController() -> UIViewController {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        return storyboard.instantiateViewController(withIdentifier: "AnalyticsViewController")
    }
    
    private func createAIAssistantViewController() -> UIViewController {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        return storyboard.instantiateViewController(withIdentifier: "AIAssistantViewController")
    }
    
    private func setupWindowAppearance() {
        // Настройка внешнего вида окна с цветовой схемой "Грозовое небо"
        window?.backgroundColor = StormSkyColors.primaryBackground
        window?.tintColor = StormSkyColors.accentColor
    }
    
    private func checkSecurityStatus() {
        // Проверка статуса безопасности при активации приложения
        print("🛡️ Checking security status...")
    }
    
    private func saveSecurityState() {
        // Сохранение состояния безопасности при деактивации
        print("💾 Saving security state...")
    }
    
    private func updateProtectionStatus() {
        // Обновление статуса защиты при возвращении в foreground
        print("🔄 Updating protection status...")
    }
    
    private func activateBackgroundProtection() {
        // Активация фоновой защиты
        print("🌙 Activating background protection...")
    }
}


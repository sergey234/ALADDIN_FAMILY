import Foundation
import UIKit

/**
 * 📸 Profile Image Manager
 * Управление сохранением и загрузкой фото профиля
 * Сохраняет изображение в файловую систему приложения
 * Поддерживает разные категории пользователей (main, child, elderly)
 */

enum UserCategory {
    case main
    case child
    case elderly
}

class ProfileImageManager {
    static let shared = ProfileImageManager()
    
    private func fileURL(for category: UserCategory) -> URL {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileName: String
        switch category {
        case .main:
            fileName = "profile_image_main.jpg"
        case .child:
            fileName = "profile_image_child.jpg"
        case .elderly:
            fileName = "profile_image_elderly.jpg"
        }
        return documentsPath.appendingPathComponent(fileName)
    }
    
    private init() {}
    
    /**
     * Сохранить изображение профиля для указанной категории пользователя
     */
    func saveProfileImage(_ image: UIImage, for category: UserCategory) -> Bool {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            print("❌ ProfileImageManager: Failed to convert image to JPEG data")
            return false
        }
        
        let url = fileURL(for: category)
        do {
            try imageData.write(to: url)
            print("✅ ProfileImageManager: Profile image saved successfully for category: \(category)")
            return true
        } catch {
            print("❌ ProfileImageManager: Failed to save profile image: \(error)")
            return false
        }
    }
    
    /**
     * Загрузить изображение профиля для указанной категории пользователя
     */
    func loadProfileImage(for category: UserCategory) -> UIImage? {
        let url = fileURL(for: category)
        guard FileManager.default.fileExists(atPath: url.path) else {
            print("ℹ️ ProfileImageManager: Profile image file does not exist for category: \(category)")
            return nil
        }
        
        guard let imageData = try? Data(contentsOf: url),
              let image = UIImage(data: imageData) else {
            print("❌ ProfileImageManager: Failed to load profile image for category: \(category)")
            return nil
        }
        
        print("✅ ProfileImageManager: Profile image loaded successfully for category: \(category)")
        return image
    }
    
    /**
     * Удалить изображение профиля для указанной категории пользователя
     */
    func deleteProfileImage(for category: UserCategory) -> Bool {
        let url = fileURL(for: category)
        guard FileManager.default.fileExists(atPath: url.path) else {
            return true // Уже удалено
        }
        
        do {
            try FileManager.default.removeItem(at: url)
            print("✅ ProfileImageManager: Profile image deleted successfully for category: \(category)")
            return true
        } catch {
            print("❌ ProfileImageManager: Failed to delete profile image: \(error)")
            return false
        }
    }
    
    /**
     * Проверить, существует ли сохраненное изображение для указанной категории пользователя
     */
    func hasSavedImage(for category: UserCategory) -> Bool {
        let url = fileURL(for: category)
        return FileManager.default.fileExists(atPath: url.path)
    }
}














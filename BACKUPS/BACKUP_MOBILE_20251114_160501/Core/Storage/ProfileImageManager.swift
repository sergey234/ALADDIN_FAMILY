import Foundation
import UIKit

/**
 * 📸 Profile Image Manager
 * Управление сохранением и загрузкой фото профиля
 * Сохраняет изображение в файловую систему приложения
 */

class ProfileImageManager {
    static let shared = ProfileImageManager()
    
    private let fileName = "profile_image.jpg"
    private var fileURL: URL {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return documentsPath.appendingPathComponent(fileName)
    }
    
    private init() {}
    
    /**
     * Сохранить изображение профиля
     */
    func saveProfileImage(_ image: UIImage) -> Bool {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            print("❌ ProfileImageManager: Failed to convert image to JPEG data")
            return false
        }
        
        do {
            try imageData.write(to: fileURL)
            print("✅ ProfileImageManager: Profile image saved successfully")
            return true
        } catch {
            print("❌ ProfileImageManager: Failed to save profile image: \(error)")
            return false
        }
    }
    
    /**
     * Загрузить изображение профиля
     */
    func loadProfileImage() -> UIImage? {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            print("ℹ️ ProfileImageManager: Profile image file does not exist")
            return nil
        }
        
        guard let imageData = try? Data(contentsOf: fileURL),
              let image = UIImage(data: imageData) else {
            print("❌ ProfileImageManager: Failed to load profile image")
            return nil
        }
        
        print("✅ ProfileImageManager: Profile image loaded successfully")
        return image
    }
    
    /**
     * Удалить изображение профиля
     */
    func deleteProfileImage() -> Bool {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            return true // Уже удалено
        }
        
        do {
            try FileManager.default.removeItem(at: fileURL)
            print("✅ ProfileImageManager: Profile image deleted successfully")
            return true
        } catch {
            print("❌ ProfileImageManager: Failed to delete profile image: \(error)")
            return false
        }
    }
    
    /**
     * Проверить, существует ли сохраненное изображение
     */
    func hasSavedImage() -> Bool {
        return FileManager.default.fileExists(atPath: fileURL.path)
    }
}











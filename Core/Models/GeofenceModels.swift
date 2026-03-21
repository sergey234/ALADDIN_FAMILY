import Foundation
import CoreLocation

/**
 * 🗺️ Geofence Models
 * Модели данных для работы с геозонами
 * Расширяет существующий GeofenceItem координатами
 */

struct GeofenceItem: Identifiable, Codable {
    var id: UUID = UUID()
    var name: String
    var address: String = ""
    var radius: Double
    var isActive: Bool = true
}

struct GeofenceItemCodable: Codable {
    var id: UUID = UUID()
    var name: String
    var address: String = ""
    var radius: Double
    var isActive: Bool = true
}

/// Тип геозоны для различных целей
enum GeofenceType: String, Codable {
    case crashDetection
    case home
    case work
    case school
    case custom
}

/// Расширенный GeofenceItem с координатами и типом для Crash Detection
struct CrashDetectionGeofenceItem: Identifiable, Codable {
    let id: UUID
    let identifier: String
    let center: CLLocationCoordinate2D
    let radius: Double
    let type: GeofenceType
    
    init(identifier: String, center: CLLocationCoordinate2D, radius: Double, type: GeofenceType = .crashDetection) {
        self.id = UUID()
        self.identifier = identifier
        self.center = center
        self.radius = radius
        self.type = type
    }
    
    // Codable поддержка для CLLocationCoordinate2D
    enum CodingKeys: String, CodingKey {
        case id, identifier, latitude, longitude, radius, type
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(UUID.self, forKey: .id)
        identifier = try container.decode(String.self, forKey: .identifier)
        let latitude = try container.decode(Double.self, forKey: .latitude)
        let longitude = try container.decode(Double.self, forKey: .longitude)
        center = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        radius = try container.decode(Double.self, forKey: .radius)
        type = try container.decode(GeofenceType.self, forKey: .type)
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(identifier, forKey: .identifier)
        try container.encode(center.latitude, forKey: .latitude)
        try container.encode(center.longitude, forKey: .longitude)
        try container.encode(radius, forKey: .radius)
        try container.encode(type, forKey: .type)
    }
}

/// Геозона с координатами для мониторинга
struct GeofenceWithCoordinates: Identifiable, Codable {
    let id: UUID
    let name: String
    let address: String
    let radius: Double
    let latitude: Double
    let longitude: Double
    
    /// Центр геозоны
    var center: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
    
    /// Создать из GeofenceItem с координатами
    init(geofence: GeofenceItem, latitude: Double, longitude: Double) {
        self.id = geofence.id
        self.name = geofence.name
        self.address = geofence.address
        self.radius = geofence.radius
        self.latitude = latitude
        self.longitude = longitude
    }
    
    /// Создать новый
    init(id: UUID = UUID(), name: String, address: String, radius: Double, latitude: Double, longitude: Double) {
        self.id = id
        self.name = name
        self.address = address
        self.radius = radius
        self.latitude = latitude
        self.longitude = longitude
    }
    
    /// Преобразовать в GeofenceItem (без координат)
    func toGeofenceItem() -> GeofenceItem {
        GeofenceItem(id: id, name: name, address: address, radius: radius)
    }
}

/// Расширение GeofenceItem для работы с координатами
extension GeofenceItem {
    /// Создать GeofenceWithCoordinates из текущего GeofenceItem
    func withCoordinates(latitude: Double, longitude: Double) -> GeofenceWithCoordinates {
        GeofenceWithCoordinates(geofence: self, latitude: latitude, longitude: longitude)
    }
}

/// Codable версия для сохранения в UserDefaults
struct GeofenceWithCoordinatesCodable: Codable {
    let id: String
    let name: String
    let address: String
    let radius: Double
    let latitude: Double
    let longitude: Double
    
    init(from geofence: GeofenceWithCoordinates) {
        self.id = geofence.id.uuidString
        self.name = geofence.name
        self.address = geofence.address
        self.radius = geofence.radius
        self.latitude = geofence.latitude
        self.longitude = geofence.longitude
    }
    
    func toGeofenceWithCoordinates() -> GeofenceWithCoordinates? {
        guard let uuid = UUID(uuidString: id) else { return nil }
        return GeofenceWithCoordinates(
            id: uuid,
            name: name,
            address: address,
            radius: radius,
            latitude: latitude,
            longitude: longitude
        )
    }
}

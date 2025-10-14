import Foundation
import SwiftUI

/**
 * 📦 API Models
 * Модели данных для API запросов и ответов
 * Соответствуют структуре вашего Python backend
 */

// MARK: - VPN Models

struct VPNStatusResponse: Codable {
    let isConnected: Bool
    let serverLocation: String
    let ipAddress: String
    let ping: Int
    let downloadSpeed: String
    let uploadSpeed: String
    let sessionTime: String
    let threatsBlocked: Int
}

struct VPNServer: Codable, Identifiable {
    let id: String
    let country: String
    let city: String
    let flag: String
    let ping: Int
    let load: Int // 0-100%
}

// MARK: - Family Models

struct FamilyMemberResponse: Codable, Identifiable {
    let id: String
    let name: String
    let role: String // "parent", "child", "teenager", "elderly"
    let avatar: String
    let status: String // "protected", "warning", "danger", "offline"
    let threatsBlocked: Int
    let lastActive: String
    let devices: Int
}

struct FamilyStatsResponse: Codable {
    let totalMembers: Int
    let totalDevices: Int
    let totalThreats: Int
    let protectionLevel: Int
}

// MARK: - Analytics Models

struct AnalyticsResponse: Codable {
    let period: String // "day", "week", "month"
    let threatsDetected: Int
    let threatsBlocked: Int
    let itemsScanned: Int
    let protectionLevel: Int
    let topThreats: [ThreatItem]
    let threatsByType: [ThreatByType]
}

struct ThreatItem: Codable, Identifiable {
    let id: String
    let name: String
    let count: Int
    let icon: String
    let severity: String // "low", "medium", "high", "critical"
}

struct ThreatByType: Codable {
    let type: String // "web", "app", "network", "file"
    let count: Int
    let percentage: Double
}

// MARK: - AI Assistant Models

struct ChatMessageRequest: Codable {
    let message: String
    let userId: String
    let timestamp: Date
}

struct ChatMessageResponse: Codable {
    let message: String
    let timestamp: Date
    let suggestions: [String]?
}

// MARK: - User Models

struct UserProfile: Codable {
    let id: String
    let name: String
    let email: String
    let phone: String?
    let registrationDate: String
    let subscriptionType: String
    let subscriptionEndDate: String?
    let threatsBlocked: Int
    let familyMembers: Int
    let devices: Int
}

struct UpdateProfileRequest: Codable {
    let name: String?
    let email: String?
    let phone: String?
}

// MARK: - Parental Control Models

struct ParentalControlSettings: Codable {
    let childId: String
    let isContentFilterEnabled: Bool
    let isAppBlockingEnabled: Bool
    let screenTimeLimitHours: Int
    let allowedApps: [String]
    let blockedWebsites: [String]
    let bedtime: String? // "22:00"
}

struct ChildStatsResponse: Codable {
    let screenTimeToday: String
    let blockedSitesToday: Int
    let allowedAppsCount: Int
    let timeRemaining: String
}

// MARK: - Notifications Models

struct NotificationResponse: Codable, Identifiable {
    let id: String
    let icon: String
    let title: String
    let message: String
    let timestamp: Date
    let isRead: Bool
    let type: String // "threat", "success", "info", "warning"
}

// MARK: - Subscription Models

struct TariffResponse: Codable, Identifiable {
    let id: String
    let name: String
    let price: Int
    let period: String
    let features: [String]
    let isRecommended: Bool
}

struct SubscriptionStatus: Codable {
    let isActive: Bool
    let tariffId: String
    let startDate: Date
    let endDate: Date
    let autoRenew: Bool
}

// MARK: - Auth Models

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct LoginResponse: Codable {
    let token: String
    let userId: String
    let expiresAt: Date
}

struct RegisterRequest: Codable {
    let name: String
    let email: String
    let password: String
    let phone: String?
}

// MARK: - Generic Response

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let message: String?
    let error: String?
}





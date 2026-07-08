import Foundation

struct AntifakeSettingsResponse: Codable {
    let ok: Bool?
    let voiceFraudThresholdPercent: Int
    let minThresholdPercent: Int
    let maxThresholdPercent: Int
    let defaultThresholdPercent: Int

    enum CodingKeys: String, CodingKey {
        case ok
        case voiceFraudThresholdPercent = "voice_fraud_threshold_percent"
        case minThresholdPercent = "min_threshold_percent"
        case maxThresholdPercent = "max_threshold_percent"
        case defaultThresholdPercent = "default_threshold_percent"
    }
}

struct AntifakeSettingsUpdateBody: Codable {
    let voiceFraudThresholdPercent: Int

    enum CodingKeys: String, CodingKey {
        case voiceFraudThresholdPercent = "voice_fraud_threshold_percent"
    }
}

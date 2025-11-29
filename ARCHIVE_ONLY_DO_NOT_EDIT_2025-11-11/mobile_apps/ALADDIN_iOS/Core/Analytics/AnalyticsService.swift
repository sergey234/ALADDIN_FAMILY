struct ThreatTypeCount: Codable, Identifiable {
    let id: UUID
    let type: String // код категории (web, file, network, app)
    let count: Int
    let icon: String?
    
    init(id: UUID = UUID(), type: String, count: Int, icon: String? = nil) {
        self.id = id
        self.type = type
        self.count = count
        self.icon = icon
    }
    
    private enum CodingKeys: String, CodingKey {
        case type
        case count
        case icon
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = UUID()
        self.type = try container.decode(String.self, forKey: .type)
        self.count = try container.decode(Int.self, forKey: .count)
        self.icon = try container.decodeIfPresent(String.self, forKey: .icon)
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(type, forKey: .type)
        try container.encode(count, forKey: .count)
        try container.encodeIfPresent(icon, forKey: .icon)
    }
}

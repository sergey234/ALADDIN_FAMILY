//
//  StormSkyColors.swift
//  ALADDIN Mobile App
//
//  Unified Color Scheme - "Грозовое небо с золотыми акцентами"
//  Для iOS приложения ALADDIN
//
//  Created: 2025-01-27
//  Version: 2.0.0
//

import SwiftUI

/// Единая цветовая схема "Грозовое небо" для всего приложения ALADDIN
struct StormSkyColors {
    
    // MARK: - Storm Sky Colors (Грозовое небо)
    
    /// Темно-синий глубокий - верх и низ неба
    static let stormSkyDark = Color(hex: "#0a1128")
    
    /// Синий грозового неба - основной цвет
    static let stormSkyMain = Color(hex: "#1e3a5f")
    
    /// Средний синий - центр неба
    static let stormSkyMid = Color(hex: "#2e5090")
    
    // MARK: - Gold Accents (Золотые акценты)
    
    /// Золотой основной - заголовки, кнопки, акценты
    static let goldMain = Color(hex: "#F59E0B")
    
    /// Золотой светлый - hover эффекты
    static let goldLight = Color(hex: "#FCD34D")
    
    /// Золотой темный - тени, градиенты
    static let goldDark = Color(hex: "#D97706")
    
    // MARK: - Status Colors (Цвета статусов)
    
    /// Изумрудный успех - статус "Подключено"
    static let successGreen = Color(hex: "#10B981")
    
    /// Рубиновый ошибка - статус "Отключено"
    static let errorRed = Color(hex: "#EF4444")
    
    /// Голубой молнии - эффекты, анимации
    static let lightningBlue = Color(hex: "#60A5FA")
    
    // MARK: - Text Colors (Цвета текста)
    
    /// Белый чистый - основной текст
    static let white = Color.white
    
    /// Белый полупрозрачный - вторичный текст
    static let whiteSecondary = Color.white.opacity(0.8)
    
    /// Темно-серый - текст на светлом фоне
    static let darkGray = Color(hex: "#1F2937")
    
    // MARK: - Background Colors (Цвета фона)
    
    /// Основной фон - грозовое небо
    static let backgroundPrimary = stormSkyMain
    
    /// Карточки - белый с прозрачностью
    static let cardBackground = Color.white.opacity(0.95)
    
    /// Вторичный фон
    static let backgroundSecondary = stormSkyDark
    
    // MARK: - Gradients (Градиенты)
    
    /// Градиент грозового неба
    static let stormSkyGradient = LinearGradient(
        gradient: Gradient(colors: [stormSkyDark, stormSkyMain, stormSkyMid, stormSkyMain, stormSkyDark]),
        startPoint: .top,
        endPoint: .bottom
    )
    
    /// Золотой градиент
    static let goldGradient = LinearGradient(
        gradient: Gradient(colors: [goldMain, goldLight, goldDark]),
        startPoint: .leading,
        endPoint: .trailing
    )
    
    /// Градиент успеха
    static let successGradient = LinearGradient(
        gradient: Gradient(colors: [successGreen, Color(hex: "#059669")]),
        startPoint: .leading,
        endPoint: .trailing
    )
    
    /// Градиент ошибки
    static let errorGradient = LinearGradient(
        gradient: Gradient(colors: [errorRed, Color(hex: "#DC2626")]),
        startPoint: .leading,
        endPoint: .trailing
    )
    
    // MARK: - Shadows (Тени)
    
    /// Золотая тень
    static let goldShadow = Color.black.opacity(0.3)
    
    /// Синяя тень
    static let blueShadow = lightningBlue.opacity(0.3)
    
    /// Зеленая тень
    static let greenShadow = successGreen.opacity(0.3)
    
    /// Красная тень
    static let redShadow = errorRed.opacity(0.3)
}

// MARK: - Color Extensions

extension Color {
    /// Инициализация цвета из HEX строки
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - View Modifiers

extension View {
    /// Применение золотого акцента
    func goldAccent() -> some View {
        self.foregroundColor(StormSkyColors.goldMain)
            .shadow(color: StormSkyColors.goldShadow, radius: 2, x: 0, y: 1)
    }
    
    /// Применение грозового неба фона
    func stormSkyBackground() -> some View {
        self.background(StormSkyColors.stormSkyGradient)
    }
    
    /// Применение карточки в стиле грозового неба
    func stormCard() -> some View {
        self.background(StormSkyColors.cardBackground)
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(StormSkyColors.goldMain.opacity(0.3), lineWidth: 2)
            )
            .cornerRadius(20)
            .shadow(color: StormSkyColors.goldShadow, radius: 10, x: 0, y: 5)
    }
    
    /// Применение золотой кнопки
    func goldButton() -> some View {
        self.background(StormSkyColors.goldGradient)
            .foregroundColor(.white)
            .cornerRadius(25)
            .shadow(color: StormSkyColors.goldShadow, radius: 5, x: 0, y: 3)
    }
}

// MARK: - Previews

#if DEBUG
struct StormSkyColors_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            // Storm Sky Gradient
            Rectangle()
                .fill(StormSkyColors.stormSkyGradient)
                .frame(height: 100)
                .overlay(
                    Text("Грозовое небо")
                        .foregroundColor(.white)
                        .font(.title)
                        .bold()
                )
            
            // Gold Gradient
            Rectangle()
                .fill(StormSkyColors.goldGradient)
                .frame(height: 60)
                .overlay(
                    Text("Золотые акценты")
                        .foregroundColor(.white)
                        .font(.headline)
                        .bold()
                )
            
            // Color Palette
            HStack(spacing: 10) {
                Circle()
                    .fill(StormSkyColors.stormSkyDark)
                    .frame(width: 40, height: 40)
                
                Circle()
                    .fill(StormSkyColors.stormSkyMain)
                    .frame(width: 40, height: 40)
                
                Circle()
                    .fill(StormSkyColors.stormSkyMid)
                    .frame(width: 40, height: 40)
                
                Circle()
                    .fill(StormSkyColors.goldMain)
                    .frame(width: 40, height: 40)
                
                Circle()
                    .fill(StormSkyColors.successGreen)
                    .frame(width: 40, height: 40)
                
                Circle()
                    .fill(StormSkyColors.errorRed)
                    .frame(width: 40, height: 40)
            }
            
            // Storm Card Example
            VStack {
                Text("Пример карточки")
                    .font(.headline)
                    .goldAccent()
                
                Text("В стиле грозового неба")
                    .foregroundColor(StormSkyColors.darkGray)
            }
            .padding()
            .stormCard()
            
            // Gold Button Example
            Button("Золотая кнопка") {
                // Action
            }
            .padding()
            .goldButton()
        }
        .padding()
        .stormSkyBackground()
    }
}
#endif


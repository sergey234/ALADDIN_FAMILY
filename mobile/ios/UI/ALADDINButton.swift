//
//  ALADDINButton.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import SwiftUI

// MARK: - ALADDIN Button Styles
struct ALADDINButton: View {
    let title: String
    let style: ButtonStyle
    let action: () -> Void
    
    enum ButtonStyle {
        case primary
        case secondary
        case danger
        case ghost
        case glassmorphism
        case neumorphism
    }
    
    var body: some View {
        Button(action: action) {
            HStack {
                Text(title)
                    .font(.headline)
                    .fontWeight(.semibold)
            }
            .foregroundColor(foregroundColor)
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .background(backgroundView)
            .overlay(overlayView)
            .cornerRadius(16)
        }
        .buttonStyle(ALADDINButtonStyle())
    }
    
    // MARK: - Computed Properties
    
    private var foregroundColor: Color {
        switch style {
        case .primary, .danger:
            return .white
        case .secondary, .ghost, .glassmorphism, .neumorphism:
            return stormSkyColors.goldenAccent
        }
    }
    
    private var backgroundView: some View {
        Group {
            switch style {
            case .primary:
                LinearGradient(
                    colors: [stormSkyColors.goldenAccent, stormSkyColors.goldenAccent.opacity(0.8)],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            case .secondary:
                LinearGradient(
                    colors: [stormSkyColors.stormSkyBlue, stormSkyColors.stormSkyMedium],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            case .danger:
                LinearGradient(
                    colors: [.red, .red.opacity(0.8)],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            case .ghost:
                Color.clear
            case .glassmorphism:
                Color.clear
            case .neumorphism:
                LinearGradient(
                    colors: [stormSkyColors.stormSkyBlue, stormSkyColors.stormSkyMedium],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            }
        }
    }
    
    private var overlayView: some View {
        Group {
            switch style {
            case .ghost:
                RoundedRectangle(cornerRadius: 16)
                    .stroke(stormSkyColors.goldenAccent, lineWidth: 2)
            case .glassmorphism:
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                    )
            case .neumorphism:
                RoundedRectangle(cornerRadius: 16)
                    .fill(.clear)
                    .shadow(color: .black.opacity(0.3), radius: 8, x: 8, y: 8)
                    .shadow(color: .white.opacity(0.05), radius: 8, x: -8, y: -8)
            default:
                EmptyView()
            }
        }
    }
}

// MARK: - ALADDIN Button Style
struct ALADDINButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

// MARK: - ALADDIN Card
struct ALADDINCard<Content: View>: View {
    let content: Content
    let style: CardStyle
    
    enum CardStyle {
        case glassmorphism
        case neumorphism
        case solid
        case gradient
    }
    
    init(style: CardStyle = .glassmorphism, @ViewBuilder content: () -> Content) {
        self.style = style
        self.content = content()
    }
    
    var body: some View {
        content
            .padding(20)
            .background(backgroundView)
            .overlay(overlayView)
            .cornerRadius(20)
    }
    
    private var backgroundView: some View {
        Group {
            switch style {
            case .glassmorphism:
                Color.clear
            case .neumorphism:
                LinearGradient(
                    colors: [stormSkyColors.stormSkyBlue, stormSkyColors.stormSkyMedium],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            case .solid:
                stormSkyColors.stormSkyBlue.opacity(0.8)
            case .gradient:
                LinearGradient(
                    colors: [
                        stormSkyColors.stormSkyDark.opacity(0.8),
                        stormSkyColors.stormSkyBlue.opacity(0.6)
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            }
        }
    }
    
    private var overlayView: some View {
        Group {
            switch style {
            case .glassmorphism:
                RoundedRectangle(cornerRadius: 20)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 20)
                            .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                    )
            case .neumorphism:
                RoundedRectangle(cornerRadius: 20)
                    .fill(.clear)
                    .shadow(color: .black.opacity(0.3), radius: 12, x: 12, y: 12)
                    .shadow(color: .white.opacity(0.05), radius: 12, x: -12, y: -12)
            case .solid:
                RoundedRectangle(cornerRadius: 20)
                    .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
            case .gradient:
                RoundedRectangle(cornerRadius: 20)
                    .stroke(
                        LinearGradient(
                            colors: [stormSkyColors.goldenAccent, stormSkyColors.goldenAccent.opacity(0.3)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1
                    )
            }
        }
    }
}

// MARK: - ALADDIN Text Field
struct ALADDINTextField: View {
    @Binding var text: String
    let placeholder: String
    let style: TextFieldStyle
    
    enum TextFieldStyle {
        case glassmorphism
        case neumorphism
        case solid
    }
    
    var body: some View {
        TextField(placeholder, text: $text)
            .font(.headline)
            .foregroundColor(.white)
            .padding(16)
            .background(backgroundView)
            .overlay(overlayView)
            .cornerRadius(12)
    }
    
    private var backgroundView: some View {
        Group {
            switch style {
            case .glassmorphism:
                Color.clear
            case .neumorphism:
                LinearGradient(
                    colors: [stormSkyColors.stormSkyBlue, stormSkyColors.stormSkyMedium],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            case .solid:
                stormSkyColors.stormSkyBlue.opacity(0.6)
            }
        }
    }
    
    private var overlayView: some View {
        Group {
            switch style {
            case .glassmorphism:
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                    )
            case .neumorphism:
                RoundedRectangle(cornerRadius: 12)
                    .fill(.clear)
                    .shadow(color: .black.opacity(0.3), radius: 6, x: 6, y: 6)
                    .shadow(color: .white.opacity(0.05), radius: 6, x: -6, y: -6)
            case .solid:
                RoundedRectangle(cornerRadius: 12)
                    .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
            }
        }
    }
}

// MARK: - ALADDIN Status Indicator
struct ALADDINStatusIndicator: View {
    let status: Status
    let size: CGFloat
    
    enum Status {
        case connected
        case connecting
        case disconnected
        case error
        
        var color: Color {
            switch self {
            case .connected: return .green
            case .connecting: return .yellow
            case .disconnected: return .gray
            case .error: return .red
            }
        }
        
        var animation: Animation? {
            switch self {
            case .connecting: return .easeInOut(duration: 1.0).repeatForever(autoreverses: true)
            default: return nil
            }
        }
    }
    
    var body: some View {
        Circle()
            .fill(status.color)
            .frame(width: size, height: size)
            .overlay(
                Circle()
                    .stroke(.white, lineWidth: 2)
            )
            .scaleEffect(status == .connecting ? 1.2 : 1.0)
            .animation(status.animation, value: status)
    }
}

// MARK: - ALADDIN Loading View
struct ALADDINLoadingView: View {
    let message: String
    @State private var isAnimating = false
    
    var body: some View {
        VStack(spacing: 20) {
            ZStack {
                Circle()
                    .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 4)
                    .frame(width: 60, height: 60)
                
                Circle()
                    .trim(from: 0, to: 0.7)
                    .stroke(stormSkyColors.goldenAccent, lineWidth: 4)
                    .frame(width: 60, height: 60)
                    .rotationEffect(.degrees(isAnimating ? 360 : 0))
                    .animation(.linear(duration: 1.0).repeatForever(autoreverses: false), value: isAnimating)
            }
            
            Text(message)
                .font(.headline)
                .foregroundColor(.white)
                .multilineTextAlignment(.center)
        }
        .onAppear {
            isAnimating = true
        }
    }
}

// MARK: - ALADDIN Bottom Navigation
struct ALADDINBottomNavigation: View {
    @Binding var selectedTab: Tab
    
    enum Tab: CaseIterable {
        case vpn
        case family
        case analytics
        case settings
        case ai
        
        var icon: String {
            switch self {
            case .vpn: return "shield.fill"
            case .family: return "person.2.fill"
            case .analytics: return "chart.bar.fill"
            case .settings: return "gearshape.fill"
            case .ai: return "brain.head.profile"
            }
        }
        
        var title: String {
            switch self {
            case .vpn: return "VPN"
            case .family: return "Семья"
            case .analytics: return "Аналитика"
            case .settings: return "Настройки"
            case .ai: return "AI"
            }
        }
    }
    
    var body: some View {
        HStack(spacing: 0) {
            ForEach(Tab.allCases, id: \.self) { tab in
                Button(action: { selectedTab = tab }) {
                    VStack(spacing: 4) {
                        Image(systemName: tab.icon)
                            .font(.title3)
                            .foregroundColor(selectedTab == tab ? stormSkyColors.goldenAccent : .white.opacity(0.7))
                        
                        Text(tab.title)
                            .font(.caption2)
                            .foregroundColor(selectedTab == tab ? stormSkyColors.goldenAccent : .white.opacity(0.7))
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
                }
                .buttonStyle(ScaleButtonStyle())
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                )
        )
        .padding(.horizontal, 16)
        .padding(.bottom, 20)
    }
}

// MARK: - Preview
#Preview {
    VStack(spacing: 20) {
        ALADDINButton(title: "Primary Button", style: .primary) { }
        ALADDINButton(title: "Secondary Button", style: .secondary) { }
        ALADDINButton(title: "Glassmorphism Button", style: .glassmorphism) { }
        ALADDINButton(title: "Neumorphism Button", style: .neumorphism) { }
        
        ALADDINCard(style: .glassmorphism) {
            Text("Glassmorphism Card")
                .foregroundColor(.white)
        }
        
        ALADDINTextField(text: .constant(""), placeholder: "Enter text", style: .glassmorphism)
        
        HStack {
            ALADDINStatusIndicator(status: .connected, size: 20)
            ALADDINStatusIndicator(status: .connecting, size: 20)
            ALADDINStatusIndicator(status: .disconnected, size: 20)
            ALADDINStatusIndicator(status: .error, size: 20)
        }
    }
    .padding()
    .background(
        LinearGradient(
            colors: [stormSkyColors.stormSkyDark, stormSkyColors.stormSkyBlue],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )
}


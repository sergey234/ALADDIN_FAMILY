//
//  VPNInterfaceView.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import SwiftUI
import UIKit

// MARK: - VPN Interface View
struct VPNInterfaceView: View {
    @StateObject private var vpnClient: ALADDINVPNClient
    @State private var selectedServer: VPNServer?
    @State private var showingServerList = false
    @State private var showingSettings = false
    
    // MARK: - Storm Sky Color Scheme
    private let stormSkyColors = StormSkyColors()
    
    init(apiClient: ALADDINAPIClient) {
        _vpnClient = StateObject(wrappedValue: ALADDINVPNClient(apiClient: apiClient))
    }
    
    var body: some View {
        ZStack {
            // MARK: - Storm Sky Background
            stormSkyBackground
            
            ScrollView {
                VStack(spacing: 20) {
                    // MARK: - Header
                    headerView
                    
                    // MARK: - VPN Status Card
                    vpnStatusCard
                    
                    // MARK: - Quick Connect
                    quickConnectView
                    
                    // MARK: - Server List
                    serverListView
                    
                    // MARK: - Connection Stats
                    if vpnClient.status == .connected {
                        connectionStatsView
                    }
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 100) // Space for bottom navigation
            }
            
            // MARK: - Bottom Navigation
            VStack {
                Spacer()
                bottomNavigationView
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showingServerList) {
            serverSelectionView
        }
        .sheet(isPresented: $showingSettings) {
            vpnSettingsView
        }
    }
    
    // MARK: - Storm Sky Background
    private var stormSkyBackground: some View {
        LinearGradient(
            colors: [
                stormSkyColors.stormSkyDark,
                stormSkyColors.stormSkyBlue,
                stormSkyColors.stormSkyMedium,
                stormSkyColors.stormSkyBlue,
                stormSkyColors.stormSkyDark
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .ignoresSafeArea()
        .overlay(
            // Magical particles effect
            ParticleEffectView()
        )
    }
    
    // MARK: - Header View
    private var headerView: some View {
        VStack(spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("ALADDIN VPN")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .shadow(color: stormSkyColors.goldenAccent.opacity(0.5), radius: 10)
                    
                    Text("Защищенное подключение")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Spacer()
                
                Button(action: { showingSettings = true }) {
                    Image(systemName: "gearshape.fill")
                        .font(.title2)
                        .foregroundColor(stormSkyColors.goldenAccent)
                        .frame(width: 44, height: 44)
                        .background(
                            Circle()
                                .fill(.ultraThinMaterial)
                                .overlay(
                                    Circle()
                                        .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                                )
                        )
                }
            }
        }
        .padding(.top, 20)
    }
    
    // MARK: - VPN Status Card
    private var vpnStatusCard: some View {
        VStack(spacing: 16) {
            // Status indicator
            HStack {
                Circle()
                    .fill(vpnClient.status.color)
                    .frame(width: 12, height: 12)
                    .overlay(
                        Circle()
                            .stroke(.white, lineWidth: 2)
                    )
                
                Text(vpnClient.status.displayName)
                    .font(.headline)
                    .foregroundColor(.white)
                
                Spacer()
            }
            
            // Connection button
            Button(action: toggleConnection) {
                HStack {
                    if vpnClient.isConnecting {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .scaleEffect(0.8)
                    } else {
                        Image(systemName: vpnClient.status == .connected ? "shield.fill" : "shield")
                            .font(.title2)
                    }
                    
                    Text(connectionButtonText)
                        .font(.headline)
                        .fontWeight(.semibold)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 56)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(
                            LinearGradient(
                                colors: [
                                    stormSkyColors.goldenAccent,
                                    stormSkyColors.goldenAccent.opacity(0.8)
                                ],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 16)
                                .stroke(.white.opacity(0.2), lineWidth: 1)
                        )
                )
                .scaleEffect(vpnClient.isConnecting ? 1.05 : 1.0)
                .animation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true), 
                          value: vpnClient.isConnecting)
            }
            .disabled(vpnClient.isConnecting)
            
            // Current server info
            if let connection = vpnClient.currentConnection {
                currentServerInfo(connection)
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Quick Connect View
    private var quickConnectView: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Быстрое подключение")
                .font(.headline)
                .foregroundColor(.white)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(vpnClient.getQuickConnectServers()) { server in
                        quickConnectButton(server)
                    }
                }
                .padding(.horizontal, 4)
            }
        }
    }
    
    // MARK: - Server List View
    private var serverListView: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Все серверы")
                    .font(.headline)
                    .foregroundColor(.white)
                
                Spacer()
                
                Button("Показать все") {
                    showingServerList = true
                }
                .font(.subheadline)
                .foregroundColor(stormSkyColors.goldenAccent)
            }
            
            LazyVStack(spacing: 8) {
                ForEach(Array(vpnClient.availableServers.prefix(3))) { server in
                    serverRow(server)
                }
            }
        }
    }
    
    // MARK: - Connection Stats View
    private var connectionStatsView: some View {
        VStack(spacing: 16) {
            Text("Статистика подключения")
                .font(.headline)
                .foregroundColor(.white)
            
            if let connection = vpnClient.currentConnection {
                HStack(spacing: 20) {
                    statItem(
                        title: "Время",
                        value: formatTime(connection.connectionTime),
                        icon: "clock"
                    )
                    
                    statItem(
                        title: "Скачивание",
                        value: "\(Int(connection.speed.download)) KB/s",
                        icon: "arrow.down"
                    )
                    
                    statItem(
                        title: "Загрузка",
                        value: "\(Int(connection.speed.upload)) KB/s",
                        icon: "arrow.up"
                    )
                }
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Bottom Navigation View
    private var bottomNavigationView: some View {
        HStack(spacing: 0) {
            navItem(icon: "shield.fill", title: "VPN", isSelected: true)
            navItem(icon: "person.2.fill", title: "Семья", isSelected: false)
            navItem(icon: "chart.bar.fill", title: "Аналитика", isSelected: false)
            navItem(icon: "gearshape.fill", title: "Настройки", isSelected: false)
            navItem(icon: "brain.head.profile", title: "AI", isSelected: false)
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
    
    // MARK: - Helper Views
    
    private func currentServerInfo(_ connection: ConnectionInfo) -> some View {
        HStack {
            Text(connection.server.flag)
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(connection.server.name)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                
                Text(connection.server.statusText)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            }
            
            Spacer()
        }
        .padding(.top, 8)
    }
    
    private func quickConnectButton(_ server: VPNServer) -> some View {
        Button(action: { connectToServer(server) }) {
            VStack(spacing: 8) {
                Text(server.flag)
                    .font(.title)
                
                Text(server.name)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                
                Text("\(server.ping)ms")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.7))
            }
            .frame(width: 80, height: 80)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(stormSkyColors.goldenAccent.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(ScaleButtonStyle())
    }
    
    private func serverRow(_ server: VPNServer) -> some View {
        Button(action: { connectToServer(server) }) {
            HStack {
                Text(server.flag)
                    .font(.title2)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(server.name)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                    
                    Text(server.statusText)
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\(Int(server.performanceScore))%")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(stormSkyColors.goldenAccent)
                    
                    Circle()
                        .fill(server.isAvailable ? .green : .red)
                        .frame(width: 8, height: 8)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(stormSkyColors.goldenAccent.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(ScaleButtonStyle())
    }
    
    private func statItem(title: String, value: String, icon: String) -> some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(stormSkyColors.goldenAccent)
            
            Text(value)
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(.white)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.white.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
    }
    
    private func navItem(icon: String, title: String, isSelected: Bool) -> some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(isSelected ? stormSkyColors.goldenAccent : .white.opacity(0.7))
            
            Text(title)
                .font(.caption2)
                .foregroundColor(isSelected ? stormSkyColors.goldenAccent : .white.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
        .frame(height: 44)
    }
    
    // MARK: - Actions
    
    private func toggleConnection() {
        Task {
            if vpnClient.status == .connected {
                await vpnClient.disconnect()
            } else {
                await vpnClient.connect(to: selectedServer)
            }
        }
    }
    
    private func connectToServer(_ server: VPNServer) {
        selectedServer = server
        Task {
            await vpnClient.connect(to: server)
        }
    }
    
    // MARK: - Computed Properties
    
    private var connectionButtonText: String {
        switch vpnClient.status {
        case .disconnected:
            return "Подключиться"
        case .connecting:
            return "Подключение..."
        case .connected:
            return "Отключиться"
        case .disconnecting:
            return "Отключение..."
        case .error:
            return "Повторить"
        }
    }
    
    // MARK: - Sheet Views
    
    private var serverSelectionView: some View {
        NavigationView {
            List(vpnClient.availableServers) { server in
                serverRow(server)
            }
            .navigationTitle("Выбор сервера")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private var vpnSettingsView: some View {
        NavigationView {
            VStack {
                Text("Настройки VPN")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(stormSkyBackground)
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    // MARK: - Helper Functions
    
    private func formatTime(_ timeInterval: TimeInterval) -> String {
        let hours = Int(timeInterval) / 3600
        let minutes = Int(timeInterval) % 3600 / 60
        let seconds = Int(timeInterval) % 60
        
        if hours > 0 {
            return String(format: "%d:%02d:%02d", hours, minutes, seconds)
        } else {
            return String(format: "%d:%02d", minutes, seconds)
        }
    }
}

// MARK: - Scale Button Style
struct ScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

// MARK: - Particle Effect View
struct ParticleEffectView: View {
    @State private var particles: [Particle] = []
    
    var body: some View {
        ZStack {
            ForEach(particles) { particle in
                Circle()
                    .fill(Color.yellow.opacity(0.6))
                    .frame(width: particle.size, height: particle.size)
                    .position(particle.position)
                    .animation(.linear(duration: particle.duration).repeatForever(autoreverses: false), value: particle.position)
            }
        }
        .onAppear {
            createParticles()
        }
    }
    
    private func createParticles() {
        for _ in 0..<20 {
            let particle = Particle(
                position: CGPoint(
                    x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                    y: CGFloat.random(in: 0...UIScreen.main.bounds.height)
                ),
                size: CGFloat.random(in: 2...4),
                duration: Double.random(in: 3...6)
            )
            particles.append(particle)
        }
    }
}

struct Particle: Identifiable {
    let id = UUID()
    var position: CGPoint
    let size: CGFloat
    let duration: Double
}

// MARK: - Storm Sky Colors
struct StormSkyColors {
    let stormSkyDark = Color(red: 0.06, green: 0.07, blue: 0.16)      // #0f172a
    let stormSkyBlue = Color(red: 0.12, green: 0.23, blue: 0.54)      // #1E3A8A
    let stormSkyMedium = Color(red: 0.23, green: 0.51, blue: 0.96)    // #3B82F6
    let goldenAccent = Color(red: 0.96, green: 0.62, blue: 0.04)      // #F59E0B
}

#Preview {
    VPNInterfaceView(apiClient: MockAPIClient())
}

// MARK: - Mock API Client
class MockAPIClient: ALADDINAPIClient {
    func getVPNServers() async throws -> [VPNServer] {
        return []
    }
}


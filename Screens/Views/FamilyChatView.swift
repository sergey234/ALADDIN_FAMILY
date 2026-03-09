//
//  FamilyChatView.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2025 ALADDIN. All rights reserved.
//
//  💬 Family Chat - Premium Feature
//  Secure family messaging and communication
//

import SwiftUI

struct FamilyChatView: View {

    // MARK: - Environment

    @EnvironmentObject private var localizationManager: LocalizationManager

    // MARK: - State

    @State private var messageText = ""
    @State private var messages: [FamilyMessage] = [
        FamilyMessage(text: "Good morning family! ☀️", isFromCurrentUser: false, sender: "Mom", timestamp: Date().addingTimeInterval(-3600)),
        FamilyMessage(text: "Morning! Ready for school 🚌", isFromCurrentUser: true, sender: "You", timestamp: Date().addingTimeInterval(-1800)),
        FamilyMessage(text: "Don't forget your lunch! 🥪", isFromCurrentUser: false, sender: "Dad", timestamp: Date().addingTimeInterval(-900)),
        FamilyMessage(text: "Love you all! ❤️", isFromCurrentUser: true, sender: "You", timestamp: Date().addingTimeInterval(-300))
    ]
    @State private var isOnline = true

    // MARK: - Types

    struct FamilyMessage: Identifiable {
        let id = UUID()
        let text: String
        let isFromCurrentUser: Bool
        let sender: String
        let timestamp: Date

        // ✅ ИСПРАВЛЕНИЕ BUILD 90: Статический форматтер для предотвращения рекурсии
        private static let timeFormatter: DateFormatter = {
            let formatter = DateFormatter()
            formatter.timeStyle = .short
            formatter.locale = Locale(identifier: "ru_RU") // Статический locale
            return formatter
        }()

        var timeString: String {
            // ✅ Используем статический formatter вместо создания нового каждый раз
            return Self.timeFormatter.string(from: timestamp)
        }
    }

    // MARK: - Body

    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: Spacing.s) {
                HStack {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        HStack(spacing: Spacing.s) {
                            Text("👨‍👩‍👧‍👦 Family Chat")
                                .font(.h3)
                                .foregroundColor(.primary)

                            Circle()
                                .fill(isOnline ? Color.green : Color.gray)
                                .frame(width: 8, height: 8)
                        }

                        Text(isOnline ? "Everyone is online" : "Some family members offline")
                            .font(.caption)
                            .foregroundColor(isOnline ? .green : .textSecondary)
                    }

                    Spacer()

                    // Family members indicator
                    HStack(spacing: -8) {
                        ForEach(0..<4) { index in
                            Circle()
                                .fill(Color.blue.opacity(0.8))
                                .frame(width: 24, height: 24)
                                .overlay(
                                    Text(["👩", "👨", "👦", "👧"][index])
                                        .font(.caption)
                                )
                        }
                    }
                }
            }
            .padding(Spacing.m)
            .background(Color.cardBackground)

            Divider()

            // Messages list
            ScrollView {
                LazyVStack(spacing: Spacing.s) {
                    ForEach(messages) { message in
                        MessageBubble(message: message)
                    }
                }
                .padding(.vertical, Spacing.m)
            }

            // Message input
            HStack(spacing: Spacing.s) {
                TextField("Type a message...", text: $messageText)
                    .font(.body)
                    .padding(Spacing.m)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(20)
                    .frame(maxWidth: .infinity)

                Button(action: sendMessage) {
                    Image(systemName: "paperplane.fill")
                        .font(.title2)
                        .foregroundColor(.white)
                        .frame(width: 44, height: 44)
                        .background(Color.blue)
                        .clipShape(Circle())
                        .shadow(color: Color.blue.opacity(0.3), radius: 4)
                }
                .disabled(messageText.isEmpty)
                .opacity(messageText.isEmpty ? 0.5 : 1.0)
            }
            .padding(Spacing.m)
            .background(Color.cardBackground)
        }
        .background(Color.backgroundPrimary)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.1), radius: 8)
        .frame(height: 400)
    }

    // MARK: - Actions

    private func sendMessage() {
        guard !messageText.isEmpty else { return }

        let newMessage = FamilyMessage(
            text: messageText,
            isFromCurrentUser: true,
            sender: "You",
            timestamp: Date()
        )

        messages.append(newMessage)
        messageText = ""

        HapticFeedback.selection()

        // Simulate family response
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            let responses = ["Got it! 👍", "Love you too! ❤️", "See you later! 👋", "Have fun! 🎉"]
            let randomResponse = responses.randomElement() ?? "Okay!"

            let familyResponse = FamilyMessage(
                text: randomResponse,
                isFromCurrentUser: false,
                sender: ["Mom", "Dad", "Sister", "Brother"].randomElement() ?? "Family",
                timestamp: Date()
            )

            messages.append(familyResponse)
        }
    }
}

// MARK: - Subviews

struct MessageBubble: View {
    let message: FamilyChatView.FamilyMessage

    var body: some View {
        HStack(alignment: .bottom, spacing: Spacing.s) {
            if message.isFromCurrentUser {
                Spacer()
            }

            VStack(alignment: message.isFromCurrentUser ? .trailing : .leading, spacing: Spacing.xs) {
                // Sender name (only for others)
                if !message.isFromCurrentUser {
                    Text(message.sender)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .padding(.horizontal, Spacing.s)
                }

                // Message bubble
                Text(message.text)
                    .font(.body)
                    .foregroundColor(message.isFromCurrentUser ? .white : .primary)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(message.isFromCurrentUser ? Color.blue : Color.gray.opacity(0.2))
                    )
                    .frame(maxWidth: 250, alignment: message.isFromCurrentUser ? .trailing : .leading)

                // Timestamp
                Text(message.timeString)
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                    .padding(.horizontal, Spacing.s)
            }

            if !message.isFromCurrentUser {
                Spacer()
            }
        }
        .padding(.horizontal, Spacing.m)
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyChatView_Previews: PreviewProvider {
    static var previews: some View {
        FamilyChatView()
            .environmentObject(LocalizationManager())
            .padding()
            .background(Color.backgroundPrimary)
            .previewDisplayName("Family Chat")
    }
}
#endif
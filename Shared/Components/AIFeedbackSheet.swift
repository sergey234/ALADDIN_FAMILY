import SwiftUI

/// Общий лист оценки приложения ALADDIN (тот же API, что из AI Assistant).
struct AIFeedbackSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    @State private var rating: Int = 5
    @State private var comment: String = ""
    @State private var isSubmitting = false
    @State private var showSuccess = false
    @State private var showSubmitError = false
    @State private var submitErrorDetail: String = ""

    let apiService: APIService
    /// Пробрасывается в `resolved_by` на бэкенде / Telegram (например `feedback_sheet`, `family_chat_feedback_sheet`).
    let resolvedBy: String

    private var trimmedFeedbackDescription: String {
        localizationManager.localized("ai_assistant_feedback_description")
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text(localizationManager.localized("ai_assistant_feedback_title"))
                    .font(.title2)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)

                if !trimmedFeedbackDescription.isEmpty {
                    Text(trimmedFeedbackDescription)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }

                VStack(spacing: 12) {
                    Text(localizationManager.localized("ai_assistant_feedback_rating"))
                        .font(.headline)

                    HStack(spacing: 8) {
                        ForEach(1...5, id: \.self) { star in
                            Image(systemName: star <= rating ? "star.fill" : "star")
                                .font(.system(size: 30))
                                .foregroundColor(star <= rating ? .yellow : .gray)
                                .onTapGesture {
                                    rating = star
                                }
                        }
                    }
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("ai_assistant_feedback_comment"))
                        .font(.headline)

                    TextEditor(text: $comment)
                        .frame(height: 100)
                        .padding(8)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                        )
                }

                Spacer()

                HStack(spacing: 12) {
                    Button(localizationManager.localized("common_cancel")) {
                        isPresented = false
                    }
                    .buttonStyle(.bordered)
                    .tint(.gray)

                    Button(action: submitFeedback) {
                        if isSubmitting {
                            ProgressView()
                                .tint(.white)
                        } else {
                            Text(localizationManager.localized("ai_assistant_feedback_submit"))
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isSubmitting)
                }
            }
            .padding()
            .navigationBarHidden(true)
            .alert(localizationManager.localized("ai_assistant_feedback_thanks_title"), isPresented: $showSuccess) {
                Button(localizationManager.localized("common_ok")) {
                    isPresented = false
                }
            } message: {
                Text(localizationManager.localized("ai_assistant_feedback_success"))
            }
            .alert(localizationManager.localized("ai_assistant_feedback_error"), isPresented: $showSubmitError) {
                Button(localizationManager.localized("common_ok"), role: .cancel) {}
            } message: {
                Text(submitErrorDetail.isEmpty ? localizationManager.localized("ai_assistant_feedback_error") : submitErrorDetail)
            }
        }
        .aladdinSheetPresentation()
    }

    private func submitFeedback() {
        isSubmitting = true
        let queryText = comment.isEmpty ? nil : comment

        apiService.sendAIFeedback(
            rating: rating,
            comment: comment.isEmpty ? nil : comment,
            messageId: nil,
            queryText: queryText,
            resolvedBy: resolvedBy,
            faqId: nil,
            confidence: nil,
            sessionId: currentFeedbackSessionId()
        ) { result in
            DispatchQueue.main.async {
                isSubmitting = false

                switch result {
                case .success:
                    showSuccess = true
                case .failure(let error):
                    submitErrorDetail = error.localizedDescription
                    showSubmitError = true
                }
            }
        }
    }

    private func currentFeedbackSessionId() -> String {
        if let existing = UserDefaults.standard.string(forKey: "jwt_session_id"), !existing.isEmpty {
            return existing
        }
        let generated = UUID().uuidString
        UserDefaults.standard.set(generated, forKey: "jwt_session_id")
        return generated
    }
}

import SwiftUI
import WebKit

/// Parent guide — local HTML from `parent_mnemo_guide_*` keys (B14-T02, §T).
enum MnemoParentGuideHTMLBuilder {
    static func build(localizationManager: LocalizationManager) -> String {
        func t(_ key: String) -> String { escapeHTML(localizationManager.localized(key)) }

        let techniqueBlocks = MnemonicTechnique.allCases.map { technique in
            """
            <div class="technique">
              <h4>\(t(technique.localizationKey))</h4>
              <p>\(t(technique.parentGuideLocalizationKey))</p>
            </div>
            """
        }.joined()

        let srsTips = MnemoParentGuideContent.srsKeys.dropFirst(2).map { key in
            "<li>\(t(key))</li>"
        }.joined()

        let aimItems = MnemoParentGuideContent.introKeys.dropFirst(3).prefix(3).map { key in
            "<li>\(t(key))</li>"
        }.joined()

        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, sans-serif;
              margin: 0;
              padding: 20px 18px 32px;
              background: #1a1035;
              color: #f5f5f7;
              line-height: 1.45;
              -webkit-text-size-adjust: 100%;
            }
            h1 { font-size: 1.35rem; margin: 0 0 8px; }
            .lead { color: rgba(255,255,255,0.78); margin: 0 0 20px; font-size: 0.95rem; }
            section { margin-bottom: 22px; }
            h2 { font-size: 1.05rem; margin: 0 0 8px; color: #f0c14b; }
            h4 { font-size: 0.95rem; margin: 0 0 4px; }
            p { margin: 0 0 10px; color: rgba(255,255,255,0.88); font-size: 0.92rem; }
            ul { margin: 8px 0 0; padding-left: 1.1rem; }
            li { margin-bottom: 6px; color: rgba(255,255,255,0.86); font-size: 0.9rem; }
            .technique { margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); }
            .technique:last-child { border-bottom: none; }
          </style>
        </head>
        <body>
          <h1>\(t("parent_mnemo_guide_title"))</h1>
          <p class="lead">\(t("parent_mnemo_guide_subtitle"))</p>

          <section>
            <h2>\(t("parent_mnemo_guide_intro_title"))</h2>
            <p>\(t("parent_mnemo_guide_intro_lead"))</p>
            <h2>\(t("parent_mnemo_guide_intro_aim_title"))</h2>
            <ul>\(aimItems)</ul>
            <h2>\(t("parent_mnemo_guide_intro_4d_title"))</h2>
            <p>\(t("parent_mnemo_guide_intro_4d_body"))</p>
          </section>

          <section>
            <h2>\(t("parent_mnemo_guide_srs_title"))</h2>
            <p>\(t("parent_mnemo_guide_srs_lead"))</p>
            <ul>\(srsTips)</ul>
          </section>

          <section>
            <h2>\(t("parent_mnemo_guide_mq_title"))</h2>
            <p>\(t("parent_mnemo_guide_mq_lead"))</p>
            <p>\(t("parent_mnemo_guide_mq_scale"))</p>
            <p>\(t("parent_mnemo_guide_mq_quarterly"))</p>
          </section>

          <section>
            \(techniqueBlocks)
          </section>
        </body>
        </html>
        """
    }

    private static func escapeHTML(_ raw: String) -> String {
        raw
            .replacingOccurrences(of: "&", with: "&amp;")
            .replacingOccurrences(of: "<", with: "&lt;")
            .replacingOccurrences(of: ">", with: "&gt;")
            .replacingOccurrences(of: "\"", with: "&quot;")
    }
}

private struct MnemoParentGuideHTMLWebView: UIViewRepresentable {
    let html: String

    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.backgroundColor = .clear
        webView.loadHTMLString(html, baseURL: nil)
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        uiView.loadHTMLString(html, baseURL: nil)
    }
}

struct MnemoParentGuideSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    private var html: String {
        MnemoParentGuideHTMLBuilder.build(localizationManager: localizationManager)
    }

    var body: some View {
        NavigationView {
            MnemoParentGuideHTMLWebView(html: html)
                .background(LinearGradient.backgroundGradient.ignoresSafeArea())
                .navigationTitle(localizationManager.localized("parent_mnemo_guide_open_cta"))
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button(localizationManager.localized("child_interface_back")) {
                            dismiss()
                        }
                    }
                }
                .accessibilityIdentifier("parent_mnemo_guide_webview")
        }
    }
}

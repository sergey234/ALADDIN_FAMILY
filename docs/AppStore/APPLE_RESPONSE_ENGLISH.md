RESPONSE TO APPLE REGARDING 5 REJECTION POINTS

1. GUIDELINE 2.1 - PERFORMANCE (CRASH ON SUBSCRIBE)

Apple's Concern: The app crashes when users tap Subscribe.

Our Response - Fixed:

Added protective checks in StoreManager.swift before purchase
Check for product loading from App Store before purchase attempt
Check for product validity and loading state
Added check for product loading before purchase to avoid crash when metadata is missing
Added error handling with clear messages for users instead of crash
Added error handling: storeNotReady, purchaseInProgress
Improved check in TariffsViewModel before calling purchase

Result: The app no longer crashes when Subscribe is tapped. All checks are performed before purchase attempt, which prevents crash when products are missing or StoreKit is unavailable.

---

2. GUIDELINE 2.1 - APP COMPLETENESS (IAP PRODUCTS)

Apple's Concern: In-app purchase products have not been submitted for review.

Our Response - Fixed:

Prepared Product IDs for 4 subscription products according to app code
All 4 products created in App Store Connect with correct Product IDs
Created in App Store Connect: Basic, Individual, Family, Premium
Prepared descriptions for each product in Russian and English
Added localized descriptions (Russian and English) and screenshots for App Review for each product
Prepared screenshots for App Review

Status: All products are created and ready for submission!

---

3. GUIDELINE 3.1.1 - PAYMENTS (EXTERNAL LINKS)

Apple's Concern: The app includes external payment links.

Our Response - Fixed:

Removed all mentions of external payment systems from app code
Removed links to aladdin-ai.ru from localization texts
Hidden the "how it works" card with instructions for payment on website

---

4. GUIDELINE 3.1.2 - SUBSCRIPTIONS (PRIVACY POLICY AND TERMS)

Apple's Concern: Missing functional EULA and Privacy Policy links.

Our Response - Fixed:

Added links to Privacy Policy and Terms of Use in tariffs screen before Subscribe button
Consent text: "By tapping 'Subscribe', you agree to [Terms of Use] and [Privacy Policy]"
Links open full screens with policies inside the app
Added all missing translations for Privacy Policy sections

---

5. GUIDELINE 5.4 - VPN APPS

Apple's Concern: VPN app submitted from individual account.

Our Response - Fixed:

Completely removed ALADDINPacketTunnel target from Xcode project
Removed import NetworkExtension from VPNManager.swift
Removed VPN capabilities from project Entitlements file

Result: The app no longer uses NetworkExtension. VPN functionality has been removed.

---

Best regards,
Sergey Khlystov
ALADDIN

Date: December 12, 2025

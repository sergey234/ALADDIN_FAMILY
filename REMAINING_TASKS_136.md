# 🔄 ОСТАВШИЕСЯ 136 ЗАДАЧ ИЗ 169 (80.5%)

## PHASE 2: BACKEND DEVELOPMENT (30 задач)
2.1 Create Pydantic models for subscription data
2.2 Update JWT payload structure with subscription fields
2.3 Implement JWT generation with subscription data
2.4 Add subscription data validation on server
2.5 Create unit tests for JWT generation/validation
2.6 Implement POST /api/auth/register-device endpoint with trial
2.7 Implement GET /api/subscription/status endpoint
2.8 Implement POST /api/subscription/upgrade endpoint
2.9 Implement POST /api/subscription/cancel endpoint
2.10 Implement PUT /api/subscription/limits endpoint
2.11 Create middleware for subscription checking on protected endpoints
2.12 Implement usage tracking for limits (AI messages, scans, etc.)
2.13 Add rate limiting based on subscription levels
2.14 Implement error responses for limit exceeded
2.15 Implement trial activation logic (14 days from first launch)
2.16 Implement trial expiration handling (switch to free tariff)
2.17 Add trial extension for special cases
2.18 Implement trial analytics (engagement tracking)
2.19 Create subscription database table with level, limits, expires_at
2.20 Create usage tracking database table
2.21 Create migration scripts for existing users
2.22 Implement backup/restore for subscription data
2.23 Add JWT signature validation on all endpoints
2.24 Implement subscription tampering protection
2.25 Add audit logging for subscription changes
2.26 Implement rate limiting to prevent abuse
2.27 Create unit tests for subscription functions
2.28 Create integration tests for API endpoints
2.29 Perform load testing for subscription system
2.30 Conduct security testing for JWT implementation

## PHASE 4: INTEGRATION TESTING (24 задачи)
4.1 Test trial activation flow from first launch to expiration
4.2 Test subscription upgrade through App Store
4.3 Test feature gating on all premium functions
4.4 Test offline/online transitions with state preservation
4.5 Test on different iPhone sizes (SE, Pro, Pro Max)
4.6 Test on different iOS versions (17, 18, latest beta)
4.7 Test under different network conditions (WiFi, Cellular, No network)
4.8 Test different device orientations
4.9 Test sandbox purchases for all tariff levels
4.10 Test receipt validation on server
4.11 Test subscription renewal simulation
4.12 Test restore purchases flow
4.13 Measure app launch time with trial activation
4.14 Measure JWT parsing performance for large payloads
4.15 Measure feature checks speed (should be <100ms)
4.16 Monitor memory usage during active subscription use
4.17 Test JWT tampering attempts (should fail)
4.18 Test subscription spoofing protection
4.19 Verify rate limiting effectiveness
4.20 Test data encryption validation
4.21 Test trial onboarding clarity
4.22 Test upgrade prompts effectiveness
4.23 Test error messages comprehensibility
4.24 Test subscription management ease of use

## PHASE 5: LAUNCH & MONITORING (28 задач)
5.1 Prepare App Store submission with new permissions
5.2 Update privacy policy for subscription data
5.3 Update terms of service for subscriptions
5.4 Prepare marketing materials for new subscription system
5.5 Setup beta testing with limited user group (100-500 users)
5.6 Configure crash monitoring (Crashlytics)
5.7 Setup analytics dashboards for subscription metrics
5.8 Setup support channels for beta testers
5.9 Monitor trial conversion rates (target: 20-25%)
5.10 Monitor subscription retention (target: 85%+)
5.11 Monitor feature usage by subscription levels
5.12 Monitor payment success rates (target: 95%+)
5.13 Run A/B testing for price variations
5.14 Run A/B testing for trial duration (14 vs 21 days)
5.15 Run A/B testing for UI variations in upgrade prompts
5.16 Run A/B testing for feature gating aggressiveness
5.17 Optimize app size impact from new subscription features
5.18 Optimize battery usage for subscription checks
5.19 Optimize network requests for subscription system
5.20 Fix memory leaks in subscription implementation
5.21 Fix critical bugs (P0, P1 priority)
5.22 Polish UI (animations, transitions, visual improvements)
5.23 Complete localization for subscription features
5.24 Improve accessibility for subscription screens
5.25 Prepare production deployment for backend + mobile
5.26 Launch marketing campaign for new subscription system
5.27 Train support team on subscription system
5.28 Create emergency response plan for launch issues

## PHASE 1: ОСТАВШИЕСЯ ПОДГОТОВИТЕЛЬНЫЕ (11 задач)
1.2 Check API endpoints for subscription fields
1.3 Analyze current JWT structure (if exists)
1.4 Finalize JWT structure with subscription fields
1.5 Define feature mapping for each tariff level
1.6 Plan trial logic (14 days, 80% functions)
1.7 Plan migration strategy for existing users
1.8 Setup test server for subscription API
1.9 Create App Store Connect test accounts
1.10 Setup CI/CD pipeline for testing
1.11 Configure analytics (Mixpanel/Firebase)
1.12 Create detailed API specification for subscription endpoints
1.13 Create wireframes for trial screens and upgrade prompts
1.14 Design database schema for subscription data
1.13.1 Создать Security Audit Checklist - JWT vulnerability assessment
1.13.2 Разработать Риск-Менеджмент План - технические, бизнес, операционные риски
1.13.3 Создать Коммуникационный План - ежедневные standups, еженедельные отчеты
1.13.8 Определить JWT структуры для каждого уровня подписки (разные payload)
1.13.9 Внедрить Swift Concurrency (async/await everywhere) - упростить код
1.13.10 Использовать SwiftData для локального кэша (iOS 17+) - заменить CoreData

## PHASE 3: ОСТАВШИЕСЯ МОБИЛЬНЫЕ (16 задач)
3.4 Implement secure token storage in Keychain - уже частично реализовано
3.5 Implement trial activation on first app launch (14 days)
3.6 Add trial countdown display in UI
3.7 Implement trial expiration handling (switch to free)
3.8 Add trial notifications (7, 3, 1 day warnings)
3.18 Implement product loading from App Store
3.19 Implement purchase flow with receipt validation
3.24 Add graceful degradation for offline scenarios
3.28 Add A/B testing framework for tariff variations
3.29 Implement error handling for payment failures
3.30 Add subscription expired notifications
3.31 Implement network issues handling
3.32 Add recovery flows for failed payments
3.33 Create unit tests for subscription logic
3.34 Create UI tests for tariff screens
3.35 Create integration tests with backend
3.36 Test payment flows on sandbox environment

---

## 📋 СТАТИСТИКА ПО ФАЗАМ:
- **PHASE 2 (Backend):** 30 задач - КРИТИЧНО (без этого ничего не заработает)
- **PHASE 4 (Testing):** 24 задачи - ВАЖНО (E2E и performance)
- **PHASE 5 (Launch):** 28 задач - ФИНАЛЬНО (production готовность)
- **PHASE 1 (Planning):** 11 задач - ПАРАЛЛЕЛЬНО
- **PHASE 3 (Mobile):** 16 задач - ПАРАЛЛЕЛЬНО

## 🎯 ПРИОРИТЕТЫ:
1. **PHASE 2** - Backend (30 задач) - начать НЕМЕДЛЕННО
2. **PHASE 4** - Testing (24 задачи) - параллельно с разработкой
3. **PHASE 3 + PHASE 1** - остальное (27 задач) - параллельно

## 📅 ПРОГНОЗ СРОКОВ:
- **MVP:** 4-6 недель (backend + basic testing)
- **Production:** 8-10 недель (full testing + launch)
- **Budget:** $15,000-25,000

---
**Создано:** 29 февраля 2026
**Осталось задач:** 136 из 169
**Выполнено:** 33 задачи (19.5%)
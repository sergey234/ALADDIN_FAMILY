# PROOF PACKET: Points #2-#8 + Mini-Gate (`/api/v1/parental-control/*`)

Дата: 2026-03-21  
Scope: закрытие P0-цепочки по legacy/v1 parental-control endpoint family (точки #2-#8)  
Критерий mini-gate:  
- no-auth -> `403 Not authenticated`  
- auth -> `200` + контрактный payload  
- отсутствие `sfm_mock` / `mock_fallback` маркеров в ответах

---

## A. Covered endpoints (Points #2-#8)

1. `POST /api/v1/parental-control/rules` (Point #2)  
2. `GET /api/v1/parental-control/blocking` (Point #3)  
3. `GET /api/v1/parental-control/access-requests` (Point #4)  
4. `GET /api/v1/parental-control/location/geofences` (Point #5)  
5. `POST /api/v1/parental-control/location/track` (Point #6)  
6. `GET /api/v1/parental-control/stats` (Point #7)  
7. `POST /api/v1/parental-control/access-requests` (Point #8)

---

## B. Mini-gate execution snapshot

Тестовый auth токен: зарегистрирован runtime user, `token_len=237`.

### B1. `GET /api/v1/parental-control/stats?childId=1`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200` + `ParentalControlStatsResponse` JSON (content_blocked/screen_time/location/monitoring)

### B2. `GET /api/v1/parental-control/blocking`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200 {"success":true,"data":true,"message":"Blocking is enabled","error":null}`

### B3. `GET /api/v1/parental-control/access-requests`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200 []`

### B4. `GET /api/v1/parental-control/location/geofences`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200 []`

### B5. `POST /api/v1/parental-control/rules`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200 {"success":true,"data":true,"message":"Rules applied","error":null}`

### B6. `POST /api/v1/parental-control/location/track`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200 {"success":true,"data":true,"message":"Location tracked","error":null}`

### B7. `POST /api/v1/parental-control/access-requests`
- no-auth: `403 {"detail":"Not authenticated"}`
- auth: `200 {"success":true,"data":true,"message":"Access request handled","error":null}`

---

## C. Point #8 specific closure note

Для `POST /api/v1/parental-control/access-requests` добавлен compat handler:
- route: `@legacy_router.post("/access-requests", response_model=ApiBoolResponse)`
- model: `LegacyHandleAccessRequest(requestId, action, reason?)`
- validation: `action in {"accept","reject"}`
- behavior: auth `200` `ApiBoolResponse`, no-auth `403`

Итог Point #8: `BusinessOK`.

---

## D. Mini-gate verdict for endpoint family

Статус: **PASS** для выбранного P0-семейства `/api/v1/parental-control/*` (Points #2-#8).  
Текущее состояние truth-state: `BusinessOK` на уровне покрытых маршрутов.

Оставшиеся шаги до полного release gate по всей системе:
- full-run по всем endpoint families (включая gamification/family/profile/referral)
- проверка нулевого JWT leakage в URL/path/query в полном прогоне
- E2E сценарии (2+ children, switch child, DNS on/off, offline/online, restart)

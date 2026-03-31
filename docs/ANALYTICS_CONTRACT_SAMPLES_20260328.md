# Analytics Contracts — Samples (2026‑03‑28)

Нормализованный DTO v1 для компонентов (возвращается gateway):

```json
{
  "componentId": "darkweb",
  "metrics": {
    "leaks_found": "0",
    "new_leaks": "0",
    "new_events": "0"
  }
}
```

Поддерживаемые компоненты и ключи:
- driving/driving_reports_agent:
  - trips_total, distance_km_total, duration_sec_total, avg_safety_score, violations_total, positioning
- darkweb/dark_web_monitoring_agent:
  - leaks_found, new_leaks, new_events
- identity/russian_identity_theft_protection_agent:
  - attempts, blocked
- location/location_bubble_agent:
  - blocked, accuracy
- cleanup/personal_data_cleanup_agent:
  - freed_space_gb, last_cleanup_hours_ago
- tracker/anti_tracker_agent:
  - blocked_total, blocked_this_week
- ai/ai_categories_agent:
  - categorized, blocked, accuracy

Примеры:

```json
{
  "componentId": "driving",
  "metrics": {
    "trips_total": "3",
    "distance_km_total": "125.6",
    "duration_sec_total": "7320",
    "avg_safety_score": "8.4",
    "violations_total": "1",
    "positioning": "GPS"
  }
}
```

```json
{
  "componentId": "ai",
  "metrics": {
    "categorized": "120",
    "blocked": "14",
    "accuracy": "92.0"
  }
}
```

Family Members — Sample (клиент допускает опциональные поля):

```json
[
  {
    "id": "MEM_216B1F83",
    "name": "Родитель A",
    "role": "parent",
    "avatar": "👨",
    "status": "protected",
    "threatsBlocked": 12,
    "lastActive": "2026-03-28T15:30:12Z",
    "devices": 2
  },
  {
    "id": "MEM_91DAE002",
    "name": "Подросток Q",
    "role": "teenager",
    "avatar": "🧒",
    "status": "warning",
    "threatsBlocked": 0,
    "lastActive": "",
    "devices": 1
  },
  {
    "id": "MEM_55CC9933",
    "name": "Ребёнок B",
    "role": "child"
    // avatar/status/threatsBlocked/lastActive/devices — могут отсутствовать
  }
]
```

Примечания:
- Любые «mock»/«sfm_fallback» на сервере преобразуются в 503 и не доходят до клиента.
- Клиент использует componentsAnalytics как единый источник для UI; прямые GET допускаются, но должны возвращать совместимую схему.


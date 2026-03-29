# Спецификации JSON ответов списков (дополнение к stats)

## Dark Web — leaks
```json
{
  "items": [
    {
      "id": "uuid",
      "data_type": "email",
      "leak_date": "2026-03-27T12:41:33Z",
      "source": "haveibeenpwned",
      "severity": "high",
      "status": "new"
    }
  ],
  "next_cursor": null
}
```

## Identity — attempts
```json
{
  "items": [
    {
      "id": "uuid",
      "data_type": "email",
      "action": "login_attempt",
      "severity": "medium",
      "timestamp": "2026-03-29T12:41:33Z",
      "details": {}
    }
  ],
  "next_cursor": null
}
```

## Tracker — top
```json
{
  "items": [
    {
      "tracker_name": "facebook_pixel",
      "blocked_count": 42,
      "last_blocked_at": "2026-03-29T12:41:33Z"
    }
  ],
  "next_cursor": null
}
```

## Location — requests
```json
{
  "items": [
    {
      "id": "uuid",
      "app_name": "Maps",
      "action": "request",
      "accuracy": "high",
      "timestamp": "2026-03-29T12:41:33Z"
    }
  ],
  "next_cursor": null
}
```

## Cleanup — records
```json
{
  "items": [
    {
      "id": "uuid",
      "cleanup_date": "2026-03-28T12:41:33Z",
      "freed_space_bytes": 123456789,
      "categories_json": {}
    }
  ],
  "next_cursor": null
}
```


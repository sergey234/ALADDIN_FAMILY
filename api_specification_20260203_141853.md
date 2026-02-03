# 🚀 ALADDIN API SPECIFICATION v2.1.0-PROD

**Дата экспорта:** 2026-02-03T14:18:53.837908
**Статус:** ЗАФИКСИРОВАНО (НЕ МЕНЯТЬ!)

## 📊 ОБЩАЯ ИНФОРМАЦИЯ

- **Всего эндпоинтов:** 96
- **API Gateway:** 149.154.65.180:8002
- **SFM Core:** Включен

## 🔧 КОНФИГУРАЦИЯ API GATEWAY

```json
{
  "version": "2.1.0",
  "host": "149.154.65.180",
  "port": 8002,
  "protocol": "http",
  "ssl_enabled": false,
  "timeout": 30,
  "max_connections": 1000,
  "rate_limit": {
    "requests_per_minute": 1000,
    "burst_limit": 100
  },
  "cors_origins": [
    "*"
  ],
  "debug_mode": false,
  "log_level": "INFO"
}
```

## 🔐 КОНФИГУРАЦИЯ SFM CORE

```json
{
  "enabled": true,
  "fallback_mode": false,
  "source_identifier": "real_sfm",
  "max_functions": 12,
  "timeout": 25,
  "retry_attempts": 3,
  "health_check_interval": 30,
  "auto_restart": true
}
```

## 📋 СПЕЦИФИКАЦИЯ ЭНДПОИНТОВ

### AUTHENTICATION

- **POST** `/api/auth/register` - locked
- **POST** `/api/auth/login` - locked
- **GET** `/api/auth/profile` - locked
- **POST** `/api/auth/refresh` - locked
- **POST** `/api/auth/logout` - locked

### SUBSCRIPTION

- **GET** `/api/subscription/status` - locked
- **GET** `/api/subscription/plans` - locked
- **GET** `/api/subscription/billing_history` - locked
- **POST** `/api/subscription/upgrade` - locked
- **POST** `/api/subscription/cancel` - locked

### NOTIFICATIONS

- **GET** `/api/notifications/list` - locked
- **GET** `/api/notifications/stats` - locked
- **GET** `/api/notifications/unread_count` - locked
- **POST** `/api/notifications/mark_read/{id}` - locked
- **POST** `/api/notifications/delete/{id}` - locked
- **POST** `/api/notifications/bulk_mark_read` - locked
- **POST** `/api/notifications/test` - locked

### PARENTAL_CONTROL

- **GET** `/api/parental/stats` - locked
- **GET** `/api/parental/activity/{child_id}` - locked
- **POST** `/api/parental/restrict/{child_id}` - locked
- **POST** `/api/parental/alert` - locked

### IDENTITY_PROTECTION

- **GET** `/api/identity/attempts` - locked
- **GET** `/api/identity/stats` - locked
- **GET** `/api/identity/theft/attempts` - locked
- **GET** `/api/identity/theft/stats` - locked
- **GET** `/api/identity/theft/history` - locked
- **POST** `/api/identity/allow` - locked
- **POST** `/api/identity/block` - locked
- **POST** `/api/identity/whitelist` - locked
- **POST** `/api/identity/theft/report/{id}` - locked

### DARKWEB_MONITORING

- **GET** `/api/darkweb/leaks` - locked
- **GET** `/api/darkweb/scans` - locked
- **GET** `/api/darkweb/stats` - locked
- **POST** `/api/darkweb/scan_start` - locked

### LOCATION_TRACKING

- **GET** `/api/location/requests` - locked
- **GET** `/api/location/stats` - locked
- **POST** `/api/location/allow` - locked
- **POST** `/api/location/block` - locked

### DATA_CLEANUP

- **GET** `/api/data/cleanup/records` - locked
- **GET** `/api/data/cleanup/stats` - locked
- **POST** `/api/data/cleanup/start` - locked

### ANTITRACKER

- **GET** `/api/antitracker/categories` - locked
- **GET** `/api/antitracker/trackers` - locked
- **GET** `/api/antitracker/stats` - locked
- **GET** `/api/antitracker/reports` - locked
- **POST** `/api/antitracker/scan` - locked
- **POST** `/api/antitracker/whitelist` - locked
- **POST** `/api/antitracker/allow/{tracker_id}` - locked
- **POST** `/api/antitracker/block/{tracker_id}` - locked
- **PUT** `/api/antitracker/category/{id}` - locked

### ROADSIDE_ASSISTANCE

- **GET** `/api/roadside/history` - locked
- **POST** `/api/roadside/emergency` - locked
- **PUT** `/api/roadside/settings` - locked

### SYSTEM_MANAGEMENT

- **GET** `/api/system/health` - locked
- **GET** `/api/system/info` - locked
- **GET** `/api/system/logs` - locked
- **POST** `/api/system/maintenance` - locked

### ANALYTICS

- **GET** `/api/analytics/overview` - locked
- **GET** `/api/analytics/performance` - locked
- **GET** `/api/analytics/reports` - locked
- **GET** `/api/analytics/security_events` - locked
- **POST** `/api/analytics/export` - locked

### AI_CATEGORIES

- **GET** `/api/ai/categories/stats` - locked
- **GET** `/api/ai/categories/reports` - locked
- **POST** `/api/ai/categories/allow` - locked
- **POST** `/api/ai/categories/block` - locked

### COMPONENTS

- **GET** `/api/components/health` - locked
- **GET** `/api/components/status/sfm_core` - locked
- **GET** `/api/components/config/sfm_core` - locked
- **GET** `/api/components/logs/sfm_core` - locked
- **POST** `/api/components/enable/sfm_core` - locked
- **POST** `/api/components/disable/sfm_core` - locked
- **POST** `/api/components/restart/sfm_core` - locked
- **POST** `/api/components/backup/sfm_core` - locked
- **GET** `/api/components/restore/sfm_core` - locked
- **PUT** `/api/components/config/sfm_core` - locked

### ANTIPHISHING

- **GET** `/api/phishing/sensitivity` - locked
- **GET** `/api/phishing/block_suspicious` - locked
- **GET** `/api/phishing/exclusions` - locked

### ANTIVIRUS

- **GET** `/api/malware/scan_scheduled` - locked
- **GET** `/api/malware/quarantine` - locked
- **POST** `/api/malware/scan_now` - locked

### MOBILE_SECURITY

- **GET** `/api/mobile/app_lock` - locked
- **GET** `/api/mobile/biometric` - locked

### NETWORK_SECURITY

- **GET** `/api/network/firewall_rules` - locked
- **PUT** `/api/network/vpn_config` - locked

### HEALTH_CHECKS

- **GET** `/api/health` - locked
- **GET** `/api/system/health` - locked

### SETTINGS

- **PUT** `/api/analytics/settings` - locked
- **PUT** `/api/location/accuracy` - locked
- **PUT** `/api/notifications/settings` - locked
- **PUT** `/api/parental/settings` - locked
- **PUT** `/api/identity/theft/settings` - locked
- **PUT** `/api/subscription/payment_method` - locked

### ADDITIONAL

- **POST** `/api/darkweb/resolve` - locked
- **POST** `/api/system/backup` - locked


## ⚠️  ВАЖНЫЕ ПРЕДУПРЕЖДЕНИЯ

1. **Эти настройки НЕЛЬЗЯ менять без специального разрешения**
2. **Любые изменения должны быть протестированы на 100%**
3. **Перед изменениями создавать полную резервную копию**
4. **Использовать систему версионирования для отслеживания изменений**

## 🔒 СИСТЕМА ЗАЩИТЫ

- Контрольные суммы всех конфигураций
- Автоматическая проверка целостности
- Логирование всех изменений
- Резервное копирование перед модификациями

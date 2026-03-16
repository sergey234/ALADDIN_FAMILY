# 📋 TODO: ПРИМЕНЕНИЕ WILDCARD PROXY + SFM

## 🔧 ИСПРАВЛЕНИЯ (КРИТИЧНО)

- [ ] **ШАГ 1:** Проверить порядок подключения роутеров в `main.py` - Wildcard Proxy должен быть ПОСЛЕДНИМ
- [ ] **ШАГ 2:** Исправить подключение `analytics_router` - проверить, почему `/api/analytics` попадает в Wildcard Proxy
- [ ] **ШАГ 3:** Добавить список исключений в Wildcard Proxy - пути с конкретными роутерами не должны обрабатываться

## 🔨 РЕАЛИЗАЦИЯ WILDCARD PROXY + SFM

- [ ] **ШАГ 4:** Реализовать функцию `path_to_function_name()` для преобразования пути в имя функции
- [ ] **ШАГ 5:** Интегрировать SFM Adapter в Wildcard Proxy - импортировать и инициализировать
- [ ] **ШАГ 6:** Добавить маппинг API → SFM функции через `get_sfm_function_name()`
- [ ] **ШАГ 7:** Реализовать вызов SFM через `sfm_adapter.execute_function()` в Wildcard Proxy

## 🧪 ТЕСТИРОВАНИЕ REPORTS STATS

- [ ] **ТЕСТ 1:** `/api/reports/driving/stats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 2:** `/api/reports/dark-web/stats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 3:** `/api/reports/identity-theft/stats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 4:** `/api/reports/privacy/location/stats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 5:** `/api/reports/privacy/cleanup/stats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 6:** `/api/reports/privacy/tracker/stats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 7:** `/api/reports/ai-categories/stats` → должен вернуть данные через SFM

## 🧪 ТЕСТИРОВАНИЕ ANALYTICS

- [ ] **ТЕСТ 8:** `/api/analytics` → должен обрабатываться `analytics_router`, НЕ Wildcard Proxy
- [ ] **ТЕСТ 9:** `/api/analytics/threats` → должен вернуть данные через SFM
- [ ] **ТЕСТ 10:** `/api/analytics/top-threats` → должен вернуть данные через SFM

## 🧪 ТЕСТИРОВАНИЕ METRICS

- [ ] **ТЕСТ 11:** `/api/metrics/upload` → должен вернуть данные через SFM

## ✅ ПРОВЕРКА ИСКЛЮЧЕНИЙ

- [ ] **ПРОВЕРКА 1:** `/api/auth/*` → НЕ должен попадать в Wildcard Proxy
- [ ] **ПРОВЕРКА 2:** `/api/components/*` → НЕ должен попадать в Wildcard Proxy
- [ ] **ПРОВЕРКА 3:** `/api/family/*` → НЕ должен попадать в Wildcard Proxy
- [ ] **ПРОВЕРКА 4:** `/api/payments/*` → НЕ должен попадать в Wildcard Proxy
- [ ] **ПРОВЕРКА 5:** `/api/referral/*` → НЕ должен попадать в Wildcard Proxy
- [ ] **ПРОВЕРКА 6:** `/api/protection/*` → НЕ должен попадать в Wildcard Proxy
- [ ] **ПРОВЕРКА 7:** Все Security Routers → НЕ должны попадать в Wildcard Proxy

## 📊 ИТОГОВАЯ ПРОВЕРКА

- [ ] **ФИНАЛ:** Проверить логи - убедиться, что endpoints обрабатываются правильно
- [ ] **ФИНАЛ:** Убедиться, что нет ошибок 404 для endpoints с роутерами
- [ ] **ФИНАЛ:** Убедиться, что endpoints без роутеров возвращают данные через SFM

---

**Статус:** 📋 TODO создан, готов к выполнению

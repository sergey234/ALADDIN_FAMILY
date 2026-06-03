# TestFlight — 15 пунктов UX (r100-0-01)

> **Владелец:** PO + iOS на **реальном устройстве** после билда TestFlight.  
> **Не блокирует:** деплой VPS (см. [WELLNESS_DEPLOY_BACKLOG.md](./WELLNESS_DEPLOY_BACKLOG.md)).

## Companion / герои

1. «Мир героев» открывается, 4 вкладки видны (Главное · AI поддержка · Герои · Мой мир).
2. Подписи героев: Единорог / Аладдин / Джин + стили Игривый / Спокойный / Остроумный.
3. Чат: отправка текста, ответ героя (или понятная ошибка сети).
4. Recap-строка над чатом при наличии сессии.
5. Memory chips — только при consent, не для child raw chat export.
6. Голос: hold-to-talk, reconnect «Повторить голосовой ответ».

## Wellness embedded (вкладка AI поддержка)

7. Consent один раз; Hub без слова «столп» (только «дорожка»).
8. Выбор дорожки → активная метка на карточке.
9. Упражнение → шаги → outcome «легче / так же / хуже».
10. После outcome — **остаёмся в CompanionHome**, не на Main (`finishWellnessFlow`).
11. Check-in → баннер «поговорить с героем» в чате.

## Безопасность / семья

12. L3-триггер → helpline / 112, без шуток героя.
13. Parent playbook — отдельно, не смешивается с чатом ребёнка.
14. Родитель не видит дословный teen-chat.

## Регрессия

15. Reflective / Jung — только разрешённый age_band; prod verify reflective (r100-0-06 ✅).

---

**Автоматизация:** Xcode → Test → `WellnessCompanionNavUITests` / `WellnessModelsTests`.  
**Без Xcode (CI prep):** `./scripts/verify_r100_ios_static.sh` + `./scripts/run_wellness_r100_tests.sh backend`.

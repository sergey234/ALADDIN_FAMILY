# Antifake — landing & KB copy (G-02 SSOT)

**Sync:** `python3 scripts/sync_antifake_marketing_kb.py`  
**Gate:** `python3 scripts/verify_antifake_marketing_claims.py`

---

## Hero card (RU)

**Заголовок:** Защита от фейков  
**Текст:** Проверяйте текст, ссылки, голос и видео **по вашему запросу**. После звонка — загрузите запись, если она у вас есть. Метки на входящих — только для номеров из синхронизированной базы. ALADDIN **не слушает** обычные звонки в фоне.

## Hero card (EN)

**Title:** Protection from fakes  
**Body:** Check text, links, voice, and video **when you tap Check**. After a call, upload a recording if you have one. Incoming labels apply only to numbers from the synced database. ALADDIN **does not listen** to regular calls in the background.

---

## Landing FAQ (RU)

**В:** Слушает ли ALADDIN все мои звонки?  
**О:** Нет. iOS не даёт сторонним приложениям доступ к разговору по SIM. Вы сами загружаете запись **после** звонка или включаете метки Call Directory по списку номеров.

**В:** Это как Truecaller?  
**О:** Нет. Мы не строим глобальную телефонную книгу. Семейный antifake: проверка контента по запросу + метки из нашей базы.

---

## Premium limits (paywall / tariffs)

- Аудио и видео — асинхронная обработка (до нескольких минут).
- Вердикт: likely_fake / uncertain / likely_real — не «100% мошенник».
- Call Directory — только номера из базы, не все незнакомые.

---

## Contact harvest (G-07)

ALADDIN **не собирает** адресную книгу для antifake. Номера передаются только если вы вводите их вручную или загружаете запись звонка.

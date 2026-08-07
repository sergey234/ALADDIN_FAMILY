# Happ Android — TODO Tracker

**SSOT инструкция:** `VPN_HAPP_ANDROID_CONNECT_GUIDE.md` (текст шагов — **только** там).  
**Ids:** `ha-*`  
**Цель:** убрать WIP-заглушку в боте; Android-пользователь видит те же шаги, что в гайде.

Cursor: только `merge: true`. **Не дублировать** шаги в других MD — ссылка на SSOT.

---

## Tasks

- [x] `ha-00-ssot-guide` — написан `VPN_HAPP_ANDROID_CONNECT_GUIDE.md` (простые пункты)
- [x] `ha-1-android-steps-html` — заменить `vpn_happ_android_wip_html` на полноценный HTML по SSOT
- [x] `ha-2-wire-screens` — все Android→Happ экраны зовут одну функцию (не копипаст)
- [x] `ha-3-checklist-android` — в чеклисте бота упомянуть Android + ссылка/кнопка на инструкцию
- [x] `ha-4-tests` — тест: в HTML Android есть Play URL, HWID, `/sub/`, «Вход RU»; нет «в разработке»
- [ ] `ha-5-smoke` — ручной: Play → HWID → оплата → import → VPN вкл

---

## Не делать здесь

- Не писать вторую копию шагов в `VPN71_*`, resilience/profile планах  
- Не менять iOS Happ-инструкцию (`vpn_happ_plus_steps_html`) без отдельной задачи  
- Не путать с HitWave / Hiddify

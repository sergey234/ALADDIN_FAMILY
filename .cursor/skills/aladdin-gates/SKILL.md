---
name: aladdin-gates
description: GATES / unlazy — define acceptance criteria before coding. Use for Voice Safety, Antifake, or any ALADDIN feature closure.
---

# Aladdin GATES (unlazy-inspired)

Идея Asmadey `unlazy`: **сначала критерии готовности, потом код**.

## Когда

- Новая фича / фикс Voice Safety, Antifake Hub, parental
- Перед «готово» / закрытием TODO

## Процесс

1. Записать **GATES** (3–8 пунктов): что должно быть правдой в конце.
2. Для каждого — **доказательство** (тест, скрин, curl, verify script).
3. Код только после GATES.
4. Не закрывать задачу, пока все GATES не PASS.

## Пример (Antifake / Voice)

- [ ] Нет mock/sfm_mock на parental API  
- [ ] Ошибка сети показывается честно  
- [ ] Локализация RU читаема  
- [ ] Safe area / dark mode ок  
- [ ] Verify script или ручной смоук записан  

## Запрет

Auto-merge. Закрытие «на словах» без доказательств.

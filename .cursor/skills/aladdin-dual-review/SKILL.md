---
name: aladdin-dual-review
description: Optional second-pass code review (code-reviewer inspired). Use after swift-reviewer when owner asks for dual review.
---

# Aladdin Dual Review

Идея Asmadey `code-reviewer` — **пилот после недели 2**.

## Когда

Владелец явно просит вторую проверку (риск security / parental / VPN UI).

## Как

1. Сначала штатный `swift-reviewer` / `matt-code-review`.  
2. Второй проход: контракты API, mock bypass, secrets, blast radius.  
3. Список findings: Critical / High / Other — без авто-merge.

---
name: aladdin-no-mistakes
description: Pre-commit / pre-PR blast-radius check. Complements verification-loop for ALADDIN iOS and orch.
---

# Aladdin No-Mistakes

Идея Asmadey `no-mistakes` + стык с `verification-loop`.

## Перед коммитом / PR

1. `git status` / diff — нет `.env`, bot в iOS-релизе, VPN secrets.  
2. Затронуты только нужные пути (blast radius).  
3. Сборка / релевантные verify scripts.  
4. Нет mock bypass на parental.  
5. Если orch — не vendor Asmadey dump.

Если сомнение → остановиться и спросить владельца.

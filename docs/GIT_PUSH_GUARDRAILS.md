# Git Push Guardrails

Короткий обязательный чек перед каждой работой и перед каждым push.

## Перед началом работы

1. `git remote -v`
2. `git branch --show-current`
3. `git log --oneline -n 3`

## Перед push

1. `git merge-base HEAD origin/master` должен вернуть hash.
2. Если hash не вернулся — стоп, не пушить.
3. Проверить, что работа идет в каноническом репозитории, а не в копии с другим `.git`.

## Запреты

- Не работать из временных копий проекта, если push идет в основной remote.
- Не делать `push --force` в `master`, если это не отдельно согласовано.
- Не смешивать разные git-истории через случайные merge/rebase.

## Каноническая точка для этого проекта

- Repo path: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
- Branch for release: `master`
- Remote: `origin` -> `git@github.com:sergey234/ALADDIN_FAMILY.git`

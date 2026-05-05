# Снимок файлов приложения (семья / join / главная)

## Зачем

Перед правками на **сервере** (POST join, лимит на add) и обновлением OpenAPI имеет смысл сохранить копии перечисленных исходников и `openapi.json` из репозитория — чтобы при необходимости сравнить или откатить **локально**, без обязательного git-тега.

## Как сделать полный снимок (копии файлов)

Из корня репозитория iOS:

```bash
chmod +x scripts/snapshot_family_mobile_sources.sh
./scripts/snapshot_family_mobile_sources.sh
```

Каталог появится в **`docs/backup/family-mobile-snapshot-<дата>-<время>/`** с той же структурой подпапок. Эти каталоги **не коммитятся** (см. `.gitignore`).

Снимок на Рабочий стол:

```bash
DEST="$HOME/Desktop/aladdin_family_ios_backup" ./scripts/snapshot_family_mobile_sources.sh
```

## Что входит в снимок

Список путей совпадает со скриптом `scripts/snapshot_family_mobile_sources.sh`. Закоммиченные **отпечатки SHA256** на момент фиксации — **`docs/FAMILY_MOBILE_SNAPSHOT_BASELINE.md`** (обновляйте после правок по этим файлам).

## OpenAPI «до выката»

В снимок кладётся текущий **`docs/release/current/openapi.json`**. После выката на API сохраните новый JSON **отдельно** (вне репозитория или вторым снимком) и при необходимости обновите файл в `docs/release/current/`.

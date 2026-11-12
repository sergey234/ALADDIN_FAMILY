# Family invite Open Graph (JOB13 / H20)

## Files in this folder

| File | Role |
|------|------|
| `family-invite-default-1200x630.jpg` | **B** silhouette — default `og:image` for all social crawlers |
| `family-invite-empty-pin-1200x630.jpg` | **C** empty gold pin — server/iOS composite template |
| `family-invite-two-pins-1200x630.jpg` | **A** two pins — in-app beauty only |
| `family-invite-empty-pin-center.txt` | Normalized pin hole for avatar mask |

## Deploy to aladdin-ai.ru (needs owner GO)

```bash
# Example — adjust paths to real web root
scp landing/og/family-invite-default-1200x630.jpg \
    landing/og/family-invite-empty-pin-1200x630.jpg \
    USER@HOST:/var/www/aladdin-ai.ru/og/
scp landing/family-invite.html USER@HOST:/var/www/aladdin-ai.ru/
# nginx: location /og/ { alias /var/www/aladdin-ai.ru/og/; }
# mkdir -p /var/www/aladdin-ai.ru/og/family-invite  # personal uploads
```

After deploy, Telegram/WhatsApp fetch:
`https://aladdin-ai.ru/family/invite/FAM-…` → meta `og:image` → default JPEG **1200×630**.

Personal photo pin (Life360 parity):
1. App uploads JPEG via `POST /api/family/invite/og.jpg`
2. File stored as `/og/family-invite/{COMPACT}.jpg`
3. Prefer SSR HTML with that URL as `og:image` (crawlers ignore JS). Until SSR: default B still works everywhere.

## API (MAIN / :8002)

- `GET  /api/family/invite/og.jpg?code=FAM-…`
- `POST /api/family/invite/og.jpg` multipart `code` + `file` (jpeg)

Mount: `app/routers/family_invite_og.py` via `main.py`.

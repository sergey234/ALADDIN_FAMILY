### OPS — Аудит проксирования домена и портов (8000 vs 8002)

#### Зачем
Чтобы исключить флап (таймауты/“то работает, то нет”) нужно точно знать:
- какой процесс обслуживает домен `aladdin-ai.ru` (nginx upstream)
- какой порт реально слушает приложение (**8000 uvicorn** vs **8002 gunicorn**)
- совпадают ли health и register-device при доступе:
  - через домен
  - напрямую на `127.0.0.1:8000`
  - напрямую на `127.0.0.1:8002`

#### 1) Проверка снаружи (можно выполнять с любой машины)

```bash
curl -sS -i https://aladdin-ai.ru/api/health | head -n 30
curl -sS -i -X POST https://aladdin-ai.ru/api/auth/register-device \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"ops_probe","device_type":"ios"}' | head -n 60
```

Фиксируем:
- status code
- `Server`, `Date`, `Content-Type`
- наличие `token` в JSON

#### 2) Проверка на сервере (точно определяет, что слушает 8000/8002)

```bash
ss -tuln | grep -E ':(8000|8002)\\b' || true
ps aux | grep -E 'gunicorn|uvicorn' | grep -v grep || true
```

Проверка health напрямую:

```bash
curl -sS -i http://127.0.0.1:8000/api/health | head -n 20
curl -sS -i http://127.0.0.1:8002/api/health | head -n 20
```

Проверка register-device напрямую:

```bash
curl -sS -i -X POST http://127.0.0.1:8000/api/auth/register-device \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"ops_probe_8000","device_type":"ios"}' | head -n 40

curl -sS -i -X POST http://127.0.0.1:8002/api/auth/register-device \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"ops_probe_8002","device_type":"ios"}' | head -n 40
```

#### 3) Nginx: куда проксирует домен

```bash
nginx -T 2>/dev/null | grep -nE 'server_name\\s+aladdin-ai\\.ru|proxy_pass\\s+http://127\\.0\\.0\\.1:(8000|8002)' -n
```

Если `nginx -T` недоступен, смотрим конфиги:

```bash
grep -RIn \"server_name\\s\\+aladdin-ai\\.ru\" /etc/nginx 2>/dev/null
grep -RIn \"proxy_pass\" /etc/nginx 2>/dev/null | grep -E '8000|8002'
```

#### 4) Systemd (если используется)
В репозитории есть пример `docs/server/aladdin-backend.service` (uvicorn:8000). На сервере нужно проверить реальные юниты:

```bash
systemctl list-units --type=service --state=running | grep -iE 'aladdin|backend|api|gunicorn|uvicorn' || true
systemctl status aladdin-backend --no-pager || true
```

#### 5) Важное уточнение: “кто именно держит 8000”
На боевом сервере обнаружено, что порт **8000** держал **не nginx**, а отдельный systemd-юнит:
- `payment_service.service` → `python3 -m uvicorn main:app --port 8000`

То есть это был **второй экземпляр основного API (`main:app`)**, а не изолированный “платёжный микросервис”.
Это создаёт риск рассинхрона (два живых backend’а) и флапов после рестартов.

Рекомендуемая операционная стратегия (Variant A):
- **Оставить один публичный upstream**: `gunicorn` на **8002**
- **Остановить и запретить** все юниты, которые поднимают `main:app` на 8000 (`payment_service.service`, `aladdin-backend.service`)
  - `systemctl stop <unit>; systemctl disable <unit>; systemctl mask <unit>`

Проверка “8000 действительно выключен”:

```bash
ss -plnt 2>/dev/null | egrep ':(8000|8002)\\b' || true
```


#### Автосбор диагностики (expect)
Если SSH-ключи не настроены, можно выполнить автосбор через `expect`:
- Скрипт: `docs/server/collect_500_and_proxy_diagnostics_expect.sh`

Запуск:

```bash
export ALADDIN_SSH_PASSWORD='...'
chmod +x docs/server/collect_500_and_proxy_diagnostics_expect.sh
docs/server/collect_500_and_proxy_diagnostics_expect.sh | tee docs/server/OPS_DIAGNOSTICS_$(date +%Y%m%d_%H%M%S).log
```

#### Выводы, которые нужно зафиксировать в отчёте
- Домен проксирует на: **8000** или **8002**
- Health/register-device стабильно работают на выбранном upstream
- При рестарте используется единый стандарт (systemd/gunicorn) — без “двух живых процессов на разных портах”


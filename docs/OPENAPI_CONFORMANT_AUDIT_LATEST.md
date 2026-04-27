# OpenAPI-conformant audit (method-aware)

- Generated: `2026-04-25T18:16:19.227266+00:00` (UTC)
- Base URL: `http://149.154.65.180:8002`
- OpenAPI: `368` path templates, `395` method operations
- Elapsed: `36s`

## Why this is not the old «POST everywhere» test

A naive client that sends the same `POST` + JSON to every path often gets **404** (there is no such route for POST) or **405** (method not allowed) or **422** (body does not match Pydantic).
That is **not** a proof that the backend is wrong — it is usually proof that the **test was wrong**.

This script reads **OpenAPI** and calls each listed **method** (GET as GET, POST as POST, …) with a **minimal** body when JSON is declared.

## Summary buckets

- **success_2xx**: `192`
- **validation_422**: `121`
- **not_found**: `79`
- **auth_forbidden**: `1`
- **method_not_allowed**: `1`
- **server_5xx**: `1`

- **Route hits (status != 404)**: `316` / `395`
- **2xx count**: `192`
- **5xx count**: `1`

## How to re-run

```bash
ALADDIN_BASE_URL=http://149.154.65.180:8002 \
  python3 scripts/openapi_conformant_audit.py
```

JSON: `OPENAPI_CONFORMANT_AUDIT_20260425T181619.json`

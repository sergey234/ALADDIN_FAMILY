#!/usr/bin/env python3
import json
import re
import subprocess

text = subprocess.check_output(
    "sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 \"tail -n 4000 /opt/aladdin-backend/logs/gunicorn.out 2>/dev/null || true\"",
    shell=True,
    text=True,
)

patterns = {
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"),
    "bearer": re.compile(r"Bearer\\s+[A-Za-z0-9._-]{20,}"),
    "jwt_like": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}"),
    "secret_key_literal": re.compile(r"aladdin-super-secret-key-change-in-production"),
    "token_preview": re.compile(r"token_preview|Token preview|secret_preview|SECRET_KEY preview", re.IGNORECASE),
    "phone_like": re.compile(r"\\+?7\\d{10}|\\b\\d{11}\\b"),
}

counts = {k: len(v.findall(text)) for k, v in patterns.items()}
result = {"pass": all(v == 0 for v in counts.values()), "counts": counts}
print(json.dumps(result, ensure_ascii=False))

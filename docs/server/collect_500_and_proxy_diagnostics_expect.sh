#!/usr/bin/expect -f
# ============================================================================
# Диагностика: 500 ошибки (Identity Theft + Referral) + audit proxy/ports 8000/8002
# ============================================================================
# Требования:
#   export ALADDIN_SSH_PASSWORD='...'
#   (рекомендуется перейти на SSH keys, но для быстрого доступа используем expect)
# ============================================================================

set timeout 90

if {![info exists env(ALADDIN_SSH_PASSWORD)]} {
    puts "❌ SECURITY: ALADDIN_SSH_PASSWORD не задана."
    puts "   Установите переменную окружения и повторите:"
    puts "   export ALADDIN_SSH_PASSWORD='...'"
    exit 1
}

set password $env(ALADDIN_SSH_PASSWORD)
set server "root@149.154.65.180"
set server_path "/opt/aladdin-backend"

puts "=== ✅ Collect diagnostics on $server ==="

set cmd "bash -lc 'set -e; \
echo \"== whoami/host ==\"; whoami; hostname; \
echo; echo \"== ports 8000/8002 ==\"; ss -tuln 2>/dev/null | grep -E \":(8000|8002)\\\\b\" || true; \
echo; echo \"== processes (gunicorn/uvicorn) ==\"; ps aux | grep -E \"gunicorn|uvicorn\" | grep -v grep || true; \
echo; echo \"== nginx upstream (8000/8002) ==\"; (nginx -T 2>/dev/null | grep -nE \"server_name\\\\s+aladdin-ai\\\\.ru|proxy_pass\\\\s+http://127\\\\.0\\\\.0\\\\.1:(8000|8002)\" || true); \
echo; echo \"== project path ==\"; cd $server_path; pwd; \
echo; echo \"== grep: identity-theft routes ==\"; grep -RIn \"identity-theft\" app backend --include=\\\\*.py 2>/dev/null | head -n 120 || true; \
echo; echo \"== grep: referral routes ==\"; grep -RIn \"referral\" app backend --include=\\\\*.py 2>/dev/null | head -n 120 || true; \
echo; echo \"== grep: RussianIdentityTheftProtectionAgent ==\"; grep -RIn \"RussianIdentityTheftProtectionAgent\" . --include=\\\\*.py 2>/dev/null || true; \
echo; echo \"== grep: agent.*config usage ==\"; grep -RIn \"\\\\.config\" app backend security --include=\\\\*.py 2>/dev/null | head -n 120 || true; \
echo; echo \"== grep: anonymous->int ==\"; grep -RIn \"anonymous\" app backend --include=\\\\*.py 2>/dev/null | head -n 120 || true; \
echo; echo \"== done ==\"'"

spawn ssh -o StrictHostKeyChecking=no $server $cmd

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "\n=== ✅ diagnostics finished ==="
    }
    timeout {
        puts "\n⚠️ timeout while collecting diagnostics"
        exit 1
    }
}


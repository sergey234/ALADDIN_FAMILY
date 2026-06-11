#!/usr/bin/env bash
# Локальный Hermes на Mac для dev (задача 3.3). Без prod-ключей.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEV_ROOT="${ALADDIN_HERMES_DEV_ROOT:-$HOME/.aladdin-hermes-dev}"
VENV="${DEV_ROOT}/venv"
HERMES_HOME="${DEV_ROOT}/hermes-home"
KB_LINK="${DEV_ROOT}/knowledge"

echo "=== ALADDIN local Hermes dev setup ==="
echo "Target: ${DEV_ROOT}"

command -v git >/dev/null || { echo "FAIL: git required"; exit 1; }

mkdir -p "${DEV_ROOT}" "${HERMES_HOME}"

pick_py311() {
  local cand ver
  for cand in python3.12 python3.11; do
    if command -v "$cand" >/dev/null 2>&1; then
      ver=$("$cand" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
      if [[ "$ver" == "3.12" || "$ver" == "3.11" ]]; then
        echo "$cand"
        return 0
      fi
    fi
  done
  return 1
}

need_venv=1
if [[ -d "${VENV}" ]]; then
  vver=$("${VENV}/bin/python" -c 'import sys; print(sys.version_info[0]*10+sys.version_info[1])' 2>/dev/null || echo 0)
  [[ "$vver" -ge 311 ]] || { echo "Recreating venv (need 3.11+, had ${vver})"; rm -rf "${VENV}"; }
fi

if [[ ! -d "${VENV}" ]]; then
  if PY311=$(pick_py311); then
    "${PY311}" -m venv "${VENV}"
  else
    echo "Python 3.11+ not found — installing 3.12 via uv..."
    if ! command -v uv >/dev/null 2>&1; then
      curl -LsSf https://astral.sh/uv/install.sh | sh
      export PATH="${HOME}/.local/bin:${PATH}"
    fi
    uv python install 3.12
    uv venv "${VENV}" --python 3.12
  fi
fi

# shellcheck disable=SC1091
source "${VENV}/bin/activate"
if command -v uv >/dev/null 2>&1; then
  uv pip install -q 'hermes-agent>=0.14,<0.17'
else
  python -m ensurepip -q --upgrade 2>/dev/null || true
  pip install -q --upgrade pip
  pip install -q 'hermes-agent>=0.14,<0.17'
fi

ln -sfn "${ROOT}/security/hermes_knowledge" "${KB_LINK}"

cat > "${DEV_ROOT}/dev.env.example" <<'ENV'
# Copy to dev.env — DEV OpenRouter key only (never prod VPS key)
OPENROUTER_API_KEY=sk-or-v1-DEV-KEY-HERE
OPENROUTER_DIRECT_MODEL=deepseek/deepseek-v4-flash
HERMES_HOME=~/.aladdin-hermes-dev/hermes-home
ENV

cat > "${DEV_ROOT}/activate.sh" <<ACTIVATE
#!/usr/bin/env bash
source "${VENV}/bin/activate"
export HERMES_HOME="${HERMES_HOME}"
export PATH="${VENV}/bin:\$PATH"
if [[ -f "${DEV_ROOT}/dev.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${DEV_ROOT}/dev.env"
  set +a
fi
echo "Hermes dev env active (\$(hermes --version 2>/dev/null || echo unknown))"
ACTIVATE
chmod +x "${DEV_ROOT}/activate.sh"

VER=$("${VENV}/bin/hermes" --version 2>/dev/null | head -1 || echo "unknown")
echo "OK: hermes ${VER}"
echo "OK: KB → ${KB_LINK}"
echo ""
echo "Next:"
echo "  cp ${DEV_ROOT}/dev.env.example ${DEV_ROOT}/dev.env  # add DEV key"
echo "  source ${DEV_ROOT}/activate.sh"
echo "  hermes chat -q '1+1?' -Q"

#!/usr/bin/env bash
# Показывает, на чём «застрял» Xcode build (часто LocalizationManager.swift).
set -euo pipefail

echo "==> ALADDIN build monitor $(date '+%H:%M:%S')"
echo ""

# Disk
df -h / | awk 'NR==1 || NR==2 {print}'

echo ""
echo "==> swift-frontend (компилятор Swift):"
if pgrep -lf swift-frontend >/dev/null 2>&1; then
  pgrep -lf swift-frontend | while read -r line; do
    pid=$(echo "$line" | awk '{print $1}')
    etime=$(ps -p "$pid" -o etime= 2>/dev/null | xargs)
    cpu=$(ps -p "$pid" -o pcpu= 2>/dev/null | xargs)
    echo "  PID $pid | время $etime | CPU ${cpu}%"
    echo "$line" | tr ' ' '\n' | grep -E 'LocalizationManager|primary-file' | head -5 | sed 's/^/    /'
  done
else
  echo "  (нет активной компиляции Swift)"
fi

echo ""
DD=$(ls -d ~/Library/Developer/Xcode/DerivedData/ALADDIN-* 2>/dev/null | head -1)
if [[ -n "${DD:-}" ]]; then
  LM_O="$DD/Build/Intermediates.noindex/ALADDIN.build"/*"/ALADDIN.build/Objects-normal"/*/LocalizationManager.o
  shopt -s nullglob
  files=($LM_O)
  shopt -u nullglob
  if [[ ${#files[@]} -gt 0 ]]; then
    echo "==> LocalizationManager.o: готов ($(ls -lh "${files[0]}" | awk '{print $5}'))"
  else
    src="$(cd "$(dirname "$0")/.." && pwd)/Core/Localization/LocalizationManager.swift"
    lines=$(wc -l < "$src" | xargs)
    size=$(ls -lh "$src" | awk '{print $5}')
    echo "==> LocalizationManager.o: ещё компилируется"
    echo "    Файл: ${lines} строк, ${size} — это нормально 5–20 мин на clean build"
  fi
  count=$(find "$DD/Build/Intermediates.noindex" -name '*.o' 2>/dev/null | wc -l | xargs)
  echo "==> Скомпилировано .o файлов: $count"
fi

echo ""
echo "Подсказка: CPU > 30% = идёт работа. CPU ~0% > 5 мин = зависание → bash scripts/unlock_xcode_build_db.sh"

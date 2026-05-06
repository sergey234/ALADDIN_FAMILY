# BUGBOT POLICY (Repository-level)

This repository uses Bugbot in low-noise, high-signal mode.

## Review Scope

- Prioritize only production-impacting issues in:
  - security
  - data loss/corruption
  - crashes
  - auth/session/privacy
  - major functional regressions

## Severity Threshold

- Report only findings equivalent to **critical** or **high** severity.
- Ignore/suppress low and medium issues unless they are direct prerequisites for a critical/high fix.

## Confidence Gate

- Only report when confidence is high.
- If confidence is uncertain, prefer no comment.

## Autofix / PR Generation

- Generate fix PRs only for high-confidence, low-risk, self-contained changes.
- Do not generate broad refactors or architectural rewrites automatically.
- Never modify security-sensitive logic without explicit human confirmation.

## Noise Control

- Prefer one concise summary comment per run.
- Do not repeat the same finding across multiple runs if unchanged.
- Avoid style-only comments unless required to unblock a critical/high issue.

## Output Style

- For each finding include:
  - risk level
  - short impact statement
  - exact file path
  - minimal safe remediation


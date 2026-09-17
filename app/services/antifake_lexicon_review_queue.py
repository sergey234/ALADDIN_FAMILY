"""afhub-p3-01 — lexicon review queue from «это был скам» feedback.

Never auto-writes into SCAM_LEXICON_PATTERNS. Ops reviews JSONL / export,
then manually promotes phrases into lexicon_v2.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUEUE_PATH = ROOT / "data" / "antifake" / "lexicon_review_queue.jsonl"

_WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9][a-zA-Zа-яА-ЯёЁ0-9\-']{1,}", re.U)
_URGENCY_HINTS = {
    "срочно",
    "немедленно",
    "сейчас",
    "urgent",
    "immediately",
    "asap",
    "today",
    "сейчас же",
}


def _queue_path() -> Path:
    import os

    env = os.environ.get("ANTIFAKE_LEXICON_REVIEW_QUEUE", "").strip()
    return Path(env) if env else DEFAULT_QUEUE_PATH


def _existing_lexicon_phrases() -> Set[str]:
    try:
        from app.services.antifake_scam_lexicon import SCAM_LEXICON_PATTERNS, WEAK_SCAM_SINGLES

        out = {p.lower() for _, p in SCAM_LEXICON_PATTERNS}
        out |= {w.lower() for w in WEAK_SCAM_SINGLES}
        return out
    except Exception:
        return set()


def _detect_lang(text: str) -> str:
    cyr = sum(1 for ch in text if "а" <= ch.lower() <= "я" or ch.lower() == "ё")
    lat = sum(1 for ch in text if "a" <= ch.lower() <= "z")
    if cyr and lat:
        return "mixed"
    if cyr:
        return "ru"
    if lat:
        return "en"
    return "unknown"


def _suggest_tag(phrase: str) -> str:
    low = phrase.lower()
    if any(h in low for h in _URGENCY_HINTS):
        return "urgency"
    return "scam"


def extract_lexicon_candidates(
    text: str,
    *,
    max_candidates: int = 5,
    existing: Optional[Set[str]] = None,
) -> List[str]:
    """Pull short phrases from user note / SMS paste — not auto-lexicon."""
    raw = (text or "").strip()
    if len(raw) < 4:
        return []

    known = existing if existing is not None else _existing_lexicon_phrases()
    words = [m.group(0).lower() for m in _WORD_RE.finditer(raw)]
    if not words:
        return []

    candidates: List[str] = []
    seen: Set[str] = set()

    def _add(phrase: str) -> None:
        p = " ".join(phrase.split()).strip().lower()
        if len(p) < 4 or len(p) > 80:
            return
        if p in known or p in seen:
            return
        # skip pure weak singles
        if p in known:
            return
        seen.add(p)
        candidates.append(p)

    # multi-word windows first (more useful for lexicon)
    for n in (4, 3, 2):
        if len(words) < n:
            continue
        for i in range(0, len(words) - n + 1):
            _add(" ".join(words[i : i + n]))
            if len(candidates) >= max_candidates:
                return candidates[:max_candidates]

    # strong singles (≥5 chars) as last resort
    for w in words:
        if len(w) >= 5:
            _add(w)
            if len(candidates) >= max_candidates:
                break

    return candidates[:max_candidates]


def _load_queue(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _write_queue(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def enqueue_from_feedback(
    *,
    note: Optional[str],
    feedback_id: Optional[str] = None,
    user_id: Optional[int] = None,
    job_id: Optional[str] = None,
    verdict: Optional[str] = None,
    feedback: str = "was_scam",
    queue_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Append/merge candidates into review queue. Never mutates live lexicon."""
    path = queue_path or _queue_path()
    known = _existing_lexicon_phrases()
    phrases = extract_lexicon_candidates(note or "", existing=known)
    if not phrases:
        return {
            "queued": False,
            "count": 0,
            "phrases": [],
            "reason": "no_candidates",
        }

    rows = _load_queue(path)
    by_phrase = {
        str(r.get("phrase") or "").lower(): r
        for r in rows
        if str(r.get("status") or "pending") == "pending"
    }
    now = datetime.now(timezone.utc).isoformat()
    added: List[str] = []
    for phrase in phrases:
        existing = by_phrase.get(phrase)
        if existing:
            existing["hit_count"] = int(existing.get("hit_count") or 1) + 1
            existing["updated_at"] = now
            if feedback_id:
                refs = list(existing.get("feedback_ids") or [])
                if feedback_id not in refs:
                    refs.append(feedback_id)
                existing["feedback_ids"] = refs[-20:]
            continue
        entry = {
            "id": str(uuid.uuid4()),
            "phrase": phrase,
            "lang": _detect_lang(phrase),
            "suggested_tag": _suggest_tag(phrase),
            "status": "pending",
            "hit_count": 1,
            "source_feedback": feedback,
            "feedback_ids": [feedback_id] if feedback_id else [],
            "user_id": user_id,
            "job_id": job_id,
            "verdict_at_feedback": verdict,
            "note_excerpt": (note or "")[:240],
            "created_at": now,
            "updated_at": now,
        }
        rows.append(entry)
        by_phrase[phrase] = entry
        added.append(phrase)

    _write_queue(path, rows)
    return {
        "queued": True,
        "count": len(added),
        "phrases": added,
        "queue_path": str(path),
        "pending_total": sum(1 for r in rows if r.get("status") == "pending"),
    }


def list_pending(
    *,
    limit: int = 50,
    queue_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    path = queue_path or _queue_path()
    rows = [
        r
        for r in _load_queue(path)
        if str(r.get("status") or "pending") == "pending"
    ]
    rows.sort(key=lambda r: (-int(r.get("hit_count") or 1), str(r.get("updated_at") or "")))
    return rows[: max(1, min(200, int(limit)))]


def export_review_pack(
    *,
    limit: int = 100,
    queue_path: Optional[Path] = None,
    out_path: Optional[Path] = None,
) -> Path:
    """Write human-readable pack for ops — still not live lexicon."""
    path = queue_path or _queue_path()
    pending = list_pending(limit=limit, queue_path=path)
    dest = out_path or (ROOT / "data" / "antifake" / "lexicon_candidates_pending.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Antifake lexicon candidates (review only)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Pending shown: {len(pending)}",
        "",
        "Do **not** paste blindly into `antifake_scam_lexicon.py` — review each row.",
        "",
    ]
    for row in pending:
        lines.append(
            f"- `{row.get('phrase')}` · tag=`{row.get('suggested_tag')}` · "
            f"lang={row.get('lang')} · hits={row.get('hit_count')} · id={row.get('id')}"
        )
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def mark_status(
    entry_id: str,
    *,
    status: str,
    queue_path: Optional[Path] = None,
) -> bool:
    """pending | accepted | rejected — accepted still does not mutate live lexicon."""
    status = (status or "").strip().lower()
    if status not in ("pending", "accepted", "rejected"):
        return False
    path = queue_path or _queue_path()
    rows = _load_queue(path)
    changed = False
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        if str(row.get("id")) == entry_id:
            row["status"] = status
            row["updated_at"] = now
            changed = True
            break
    if changed:
        _write_queue(path, rows)
    return changed

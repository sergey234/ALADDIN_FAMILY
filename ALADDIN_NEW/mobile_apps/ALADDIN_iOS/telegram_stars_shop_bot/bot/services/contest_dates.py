from __future__ import annotations


def normalize_contest_date(s: str, *, end_of_day: bool) -> str:
    """YYYY-MM-DD → ISO с временем для SQLite datetime()."""
    t = s.strip()
    if len(t) == 10 and t[4] == "-" and t[7] == "-":
        return f"{t} {'23:59:59' if end_of_day else '00:00:00'}"
    return t

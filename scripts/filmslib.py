"""Shared helpers for the Letterboxd films store (_data/films.json).

Used by import_csv.py (one-time history) and update_films.py (weekly RSS delta)
so both produce identical entry ids and an identical file layout.
"""
import json
import re
import unicodedata
from pathlib import Path

STORE = Path(__file__).resolve().parent.parent / "_data" / "films.json"
USER = "lemongiu_cinema"

FIELDS = ["id", "title", "year", "watched", "rating", "liked", "rewatch",
          "review", "tags", "url", "media", "tmdb_id", "poster", "logged_at"]


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def entry_id(title, year, watched):
    return slugify(f"{title} {year} {watched}")


def load(path=STORE):
    if not path.exists():
        return {"user": USER, "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def sort_entries(entries):
    # watched desc, then logged_at desc, then id for a stable order
    entries.sort(key=lambda e: e["id"])
    entries.sort(key=lambda e: e.get("logged_at") or "", reverse=True)
    entries.sort(key=lambda e: e["watched"], reverse=True)
    return entries


def save(store, path=STORE):
    """Write deterministically. Returns False (and writes nothing) if only the
    content-free fields would change."""
    entries = sort_entries([{k: e.get(k) for k in FIELDS} for e in store["entries"]])
    out = {
        "user": store.get("user", USER),
        "last_logged_at": max((e["logged_at"] for e in entries if e["logged_at"]), default=None),
        "entries": entries,
    }
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True

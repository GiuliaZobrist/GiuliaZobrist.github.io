#!/usr/bin/env python3
"""One-time backfill of _data/films.json from a Letterboxd data export.

    python3 scripts/import_csv.py tmp/letterboxd-lemongiu_cinema-…/

Reads diary.csv (required), reviews.csv and likes/films.csv (optional) from the
export folder. Idempotent. Entries that already exist (same id) only get their
*missing* fields filled, so RSS data (posters, TMDB ids) always wins.

Export columns (verified 2026-10-04):
  diary.csv    Date, Name, Year, Letterboxd URI, Rating, Rewatch, Tags, Watched Date
  reviews.csv  Date, Name, Year, Letterboxd URI, Rating, Rewatch, Review, Tags, Watched Date
  likes/films.csv  Date, Name, Year, Letterboxd URI
"""
import csv
import sys
from pathlib import Path

import filmslib


def rows(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main(folder):
    folder = Path(folder)
    diary = rows(folder / "diary.csv")
    if not diary:
        sys.exit(f"no rows in {folder / 'diary.csv'}; nothing changed")

    reviews = {(r["Name"], r["Year"], r["Watched Date"]): r["Review"].strip()
               for r in rows(folder / "reviews.csv") if r["Review"].strip()}
    likes = {(r["Name"], r["Year"]) for r in rows(folder / "likes" / "films.csv")}

    store = filmslib.load()
    by_id = {e["id"]: e for e in store["entries"]}
    new = filled = 0

    for r in diary:
        title, year, watched = r["Name"], int(r["Year"]), r["Watched Date"]
        eid = filmslib.entry_id(title, year, watched)
        entry = {
            "id": eid,
            "title": title,
            "year": year,
            "watched": watched,
            "rating": float(r["Rating"]) if r["Rating"] else None,
            "liked": (title, r["Year"]) in likes,
            "rewatch": r["Rewatch"] == "Yes",
            "review": reviews.get((title, r["Year"], watched)),
            "tags": [t.strip() for t in r["Tags"].split(",") if t.strip()],
            "url": r["Letterboxd URI"],
            "media": "movie",
            "tmdb_id": None,
            "poster": None,
            "logged_at": r["Date"],
        }
        if eid not in by_id:
            by_id[eid] = entry
            new += 1
            continue
        existing = by_id[eid]
        gaps = [k for k in ("rating", "review", "url", "logged_at") if existing.get(k) is None and entry[k] is not None]
        if not existing.get("tags") and entry["tags"]:
            gaps.append("tags")
        for k in gaps:
            existing[k] = entry[k]
        if gaps:
            filled += 1

    store["entries"] = list(by_id.values())
    changed = filmslib.save(store)
    print(f"{len(diary)} rows, {new} new, {filled} filled, "
          f"{len(diary) - new - filled} already present"
          f"{'' if changed else ' (file unchanged)'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

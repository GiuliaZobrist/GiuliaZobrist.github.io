#!/usr/bin/env python3
"""Weekly delta: merge the public Letterboxd RSS feed into _data/films.json.

    LETTERBOXD_USER=<name> python3 scripts/update_films.py

In the Action, LETTERBOXD_USER comes from the repository variable of that name.

The feed holds only ~50 items, in log order (not watch order). It never removes
entries and never touches stored tags (the feed has none). Fails loudly, with the
file untouched, if the feed is unreachable or yields no films.
"""
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import filmslib

NS = {"lb": "https://letterboxd.com", "tmdb": "https://themoviedb.org"}
MAX_BYTES = 2_000_000
# Once set in the store, the feed does not overwrite these: tags (feed has none),
# boxd.it short links (feed has long URLs), bare-date logged_at.
KEEP = {"tags", "url", "logged_at"}


def fetch(user):
    if not re.fullmatch(r"[A-Za-z0-9_]+", user):
        sys.exit(f"invalid Letterboxd user: {user!r}")
    req = urllib.request.Request(
        f"https://letterboxd.com/{user}/rss/",
        headers={"User-Agent": "giuliazobrist.github.io films updater"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(MAX_BYTES)


def text(item, tag):
    el = item.find(tag, NS)
    return el.text if el is not None else None


def review(description):
    """Paragraphs after the poster; a lone 'Watched on ...' line means no review."""
    paras = re.findall(r"<p>(.*?)</p>", description or "", re.S)[1:]
    paras = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", p)).split()) for p in paras]
    body = "\n".join(p for p in paras if p)
    return None if not body or re.fullmatch(r"Watched on .+\.", body) else body


def parse(xml_bytes):
    films = []
    for item in ET.fromstring(xml_bytes).iter("item"):
        title = text(item, "lb:filmTitle")
        if title is None:  # a list, not a film
            continue
        year, watched = int(text(item, "lb:filmYear")), text(item, "lb:watchedDate")
        rating = text(item, "lb:memberRating")
        films.append({
            "id": filmslib.entry_id(title, year, watched),
            "title": title,
            "year": year,
            "watched": watched,
            "rating": float(rating) if rating else None,
            "liked": text(item, "lb:memberLike") == "Yes",
            "rewatch": text(item, "lb:rewatch") == "Yes",
            "review": review(text(item, "description")),
            "tags": [],
            "url": text(item, "link"),
            "media": "tv" if item.find("tmdb:tvId", NS) is not None else "movie",
            "tmdb_id": int(text(item, "tmdb:movieId") or text(item, "tmdb:tvId") or 0) or None,
            "poster": None,
            "logged_at": parsedate_to_datetime(text(item, "pubDate")).date().isoformat(),
        })
    return films


def merge(store, films):
    by_id = {e["id"]: e for e in store["entries"]}
    if by_id and not any(f["id"] in by_id for f in films):
        print("warning: no overlap with stored entries; check for a gap", file=sys.stderr)
    new = updated = 0
    for f in films:
        old = by_id.get(f["id"])
        if old is None:
            by_id[f["id"]] = f
            new += 1
            continue
        before = dict(old)
        for k, v in f.items():
            if not (k in KEEP and old.get(k)):
                old[k] = v
        # Feed likes are per log, the CSV's are per film: a like is never removed.
        old["liked"] = old["liked"] or before["liked"]
        updated += old != before
    store["entries"] = list(by_id.values())
    return new, updated


def main():
    user = filmslib.require_user()
    films = parse(fetch(user))
    if not films:
        sys.exit("feed contained no films; file untouched")
    store = filmslib.load()
    store["user"] = user
    new, updated = merge(store, films)
    filmslib.save(store)
    print(f"{new} new, {updated} updated, {len(films) - new - updated} unchanged")


if __name__ == "__main__":
    main()

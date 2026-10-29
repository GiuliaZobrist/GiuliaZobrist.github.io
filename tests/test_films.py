"""Offline tests for scripts/update_films.py, using the saved feed snapshot.

    python3 -m unittest discover -s tests -v

Fixture: tests/fixtures/rss.xml is the live feed snapshot of 2026-10-04, hand-trimmed
to 7 items (item XML untouched), each kept for one case:
  The Six Billion Dollar Man  first in the feed but not the newest watch (order test)
  Violette                    liked, no review ("Watched on ...")
  We Live in Time             written review
  The Zürrer Bakery           non-ASCII title
  Dark Waters                 stored as liked in the CSV import (per-film like)
  The Queen's Gambit          TV item, &#039; entity
  one list entry              must be skipped
If Letterboxd changes the feed format, these tests won't notice: re-capture the feed,
trim it again, and rely on the weekly Action failing loudly on a feed it can't parse.
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import filmslib  # noqa: E402
import update_films  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "rss.xml"
EMPTY_FEED = b"<rss><channel><item><title>A list</title></item></channel></rss>"


def feed():
    return update_films.parse(FIXTURE.read_bytes())


def by_title(films, title):
    return next(f for f in films if f["title"] == title)


class ParseTests(unittest.TestCase):
    def test_lists_are_skipped(self):
        raw = FIXTURE.read_text(encoding="utf-8")
        items, lists = raw.count("<item>"), raw.count("letterboxd-list-")
        self.assertGreater(lists, 0)  # the fixture really contains lists
        self.assertEqual(len(feed()), items - lists)

    def test_tv_vs_movie(self):
        films = feed()
        self.assertEqual(by_title(films, "The Queen's Gambit")["media"], "tv")
        self.assertEqual(by_title(films, "Violette")["media"], "movie")

    def test_entities_and_non_ascii_decode(self):
        titles = {f["title"] for f in feed()}
        self.assertIn("The Queen's Gambit", titles)  # &#039;
        self.assertIn("The Zürrer Bakery", titles)  # ü

    def test_review_extraction(self):
        films = feed()
        self.assertEqual(by_title(films, "We Live in Time")["review"],
                         "The only movie I cry non stop.")
        self.assertIsNone(by_title(films, "Violette")["review"])  # "Watched on ..."


class MergeTests(unittest.TestCase):
    def test_second_merge_changes_nothing(self):
        store = {"entries": []}
        new, _ = update_films.merge(store, feed())
        self.assertEqual(new, len(feed()))
        self.assertEqual(update_films.merge(store, copy.deepcopy(feed())), (0, 0))

    def test_feed_never_overwrites_stored_fields_or_unlikes(self):
        films = feed()
        violette = by_title(films, "Violette")
        stored = dict(violette, tags=["zff2026"], url="https://boxd.it/x",
                      logged_at="2020-01-01", liked=True, rating=1.0)
        violette["liked"] = False  # the feed says "No" for this log
        store = {"entries": [stored]}
        self.assertEqual(update_films.merge(store, [violette]), (0, 1))
        entry = store["entries"][0]
        self.assertEqual(entry["tags"], ["zff2026"])
        self.assertEqual(entry["url"], "https://boxd.it/x")
        self.assertEqual(entry["logged_at"], "2020-01-01")
        self.assertTrue(entry["liked"])  # a like is never removed
        self.assertEqual(entry["rating"], violette["rating"])  # the feed wins here


class SaveTests(unittest.TestCase):
    def test_sorted_by_watched_not_feed_order(self):
        films = feed()
        watched_in_feed_order = [f["watched"] for f in films]
        self.assertNotEqual(watched_in_feed_order, sorted(watched_in_feed_order, reverse=True))
        store = {"user": "someone", "entries": []}
        update_films.merge(store, films)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "films.json"
            self.assertTrue(filmslib.save(store, path))
            saved = [e["watched"] for e in filmslib.load(path)["entries"]]
            self.assertEqual(saved, sorted(saved, reverse=True))
            self.assertFalse(filmslib.save(filmslib.load(path), path))  # unchanged: no rewrite


class MainTests(unittest.TestCase):
    def test_empty_feed_exits_and_touches_nothing(self):
        with mock.patch.dict("os.environ", {"LETTERBOXD_USER": "someone"}), \
             mock.patch.object(update_films, "fetch", return_value=EMPTY_FEED), \
             mock.patch.object(filmslib, "save") as save:
            with self.assertRaises(SystemExit) as cm:
                update_films.main()
            self.assertNotEqual(cm.exception.code, 0)
            save.assert_not_called()

    def test_missing_user_exits_before_any_request(self):
        with mock.patch.dict("os.environ", {"LETTERBOXD_USER": ""}), \
             mock.patch.object(update_films, "fetch") as fetch:
            with self.assertRaises(SystemExit):
                update_films.main()
            fetch.assert_not_called()

    def test_invalid_user_is_rejected(self):
        with self.assertRaises(SystemExit):
            update_films.fetch("../etc/passwd")


if __name__ == "__main__":
    unittest.main()

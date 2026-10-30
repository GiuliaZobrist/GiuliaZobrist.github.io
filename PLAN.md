# Plan: Letterboxd films on a GitHub Pages site

**How to use this file (Claude Code):** read `AGENTS.md` and `CONTEXT.md` first (this is a Jekyll site, all CSS inline in `_layouts/default.html`). Work through the tasks in order and tick them off. Don't change the **Decisions** section without asking.

**Status (2026-10-30):** All tasks done except optional ones (2, 7). The weekly Action is live on `main`: it runs Mondays 16:05 UTC, commits `_data/films.json` only when it changed, and the site rebuilds. History was imported once (Task 6, 129 entries); the weekly delta keeps it current. See **As built** under Task 4 for where the implementation differs from the original plan.

## Decisions (already made by the human)

- **No Pillow.** Posters are stored as downloaded. No image processing, standard library only.
- **Always sort by `watchedDate` descending**, never by feed order.
- **Weekly delta load**, and the **whole diary scrollable** on the site.
- **Full history comes from a one-time manual Letterboxd CSV export** (Task 6). The RSS feed alone cannot provide it.

## Adaptations to this repo (made 2026-10-04)

The original plan assumed a plain static site with client-side `fetch`. This repo is Jekyll, so:

- **Data lives in `_data/films.json`**, not `data/diary.json`. Jekyll exposes it as `site.data.films` and Liquid renders the list **at build time**. This replaces `films.js`, the `fetch`, the chunked `IntersectionObserver` rendering, the error state and the `<noscript>` fallback: 130 text rows are plain HTML, the whole list is simply the page, and it works without JS. Revisit only if it passes a few thousand rows.
- **No separate stylesheet.** All CSS lives in the single `<style>` block of `_layouts/default.html` (see AGENTS.md). Film styles are the `.films-*` block there, on top of the shared `.expander` card shell.
- **No dark mode.** The site has a single warm palette (`CONTEXT.md`); the films card uses `--bg --ink --muted --sage --rule` only.
- **Text-first, no posters in the UI.** The CSV export has no poster URLs, so 80+ of 130 entries could never have one. A mixed poster/no-poster grid would look broken, so the diary is a typographic table (date, title and year, stars, ♥ liked, ↺ rewatch), in the spirit of the site. Poster caching (Task 2) is now optional and only worth doing if a poster is wanted in the collapsed card.
- **Tags are stored but never rendered.** The export's `Tags` column holds festival tags (`zff2026`, `locarno film festival 2026`, `live_music`) but also `w-<name>` tags naming people Giulia watched with. **Decision (2026-10-04, Giulia): all tags stay in `_data/films.json`, including `w-*` (currently `w-gold`). This is a risk she knowingly owns; do not filter, strip or rewrite git history for them, and do not raise it again.** The only rule that remains: never render tags in the UI. `update_films.py` must keep stored tags on update (the RSS feed carries none).
- **Site type is a user site** (`giuliazobrist.github.io`), and the site already uses root-absolute paths (`/assets/...`, `/blog/`), so the films card does too.
- **Private data stays out.** The export folder (email, watchlist, profile) sits in `tmp/`, which is now in `.gitignore` and in `_config.yml` `exclude` (otherwise Jekyll would publish the CSVs). `scripts/`, `tests/` and `PLAN.md` are excluded from the build too.

## Goal

Show the films logged by Letterboxd user `lemongiu_cinema` (https://letterboxd.com/lemongiu_cinema/) on an existing static HTML site hosted on GitHub Pages. No server, no secrets, no framework. Python is available for tooling (stdlib preferred).

Requirements (confirmed by the human):
- `_data/films.json` is updated by a **weekly delta load**: each run only adds new or changed entries on top of what is already stored. It never rebuilds from scratch.
- The **entire list** (all 129 entries, not just recent ones) is browsable by scrolling on the site.

Two UI pieces:
1. **Homepage card** (`<details id="films">` in `index.html`): the latest 8 films, collapsed by default, opened by the "cinema" link in the paragraph above it, same shell as the Strava card.
2. **Full history inside the same card:** the whole list (all years) is a vertical scroll area, grouped by year with sticky year labels. No separate page.

## Constraints

- GitHub Pages is static, and browsers can't fetch Letterboxd directly (CORS). Data must be fetched ahead of the Jekyll build and committed as JSON.
- The official Letterboxd API is not available for personal projects, so the **public RSS feed** is the data source.
- Python script uses the standard library only (`urllib`, `xml.etree`, `json`, `csv`, `re`, `html`). No third-party packages (no Pillow).
- Frontend: Liquid + inline CSS, matching `CONTEXT.md`. No JS needed for the list itself. No build step beyond Jekyll.

## Verified facts about the feed

Checked against the live feed `https://letterboxd.com/lemongiu_cinema/rss/`. Re-verify with the fixture in Task 0.

- Namespaces: `letterboxd` = `https://letterboxd.com`, `tmdb` = `https://themoviedb.org`, `dc` = `http://purl.org/dc/elements/1.1/`.
- Per-film fields: `letterboxd:filmTitle`, `filmYear`, `watchedDate` (YYYY-MM-DD), `memberRating` (0.5 to 5.0, may be absent), `memberLike` (Yes/No), `rewatch` (Yes/No), `tmdb:movieId`, `link`, `guid`, `pubDate`.
- The feed has about **50 items**, while the profile diary has 130 entries. The feed alone can't give the full history.
- **Feed order is by log time (`pubDate`), not watch date.** This account backfilled many old films in one session (e.g. `watchedDate` 2012 to 2024, all with `pubDate` Dec 2025). The first N items in feed order are therefore NOT the most recently watched. **Always sort by `watchedDate` descending.**
- Lists appear as `<item>` entries with no `filmTitle` (guid prefix `letterboxd-list-`). Skip them.
- Some items are TV, using `tmdb:tvId` instead of `tmdb:movieId` (e.g. The Queen's Gambit).
- `guid` prefix is `letterboxd-watch-` for plain logs and `letterboxd-review-` for entries with a review.
- `<description>` is CDATA HTML: a `<p><img src="...poster..."/></p>` followed by a `<p>`. That paragraph is either `Watched on <Weekday> <Month> <D>, <YYYY>.` (no review) or the **review text**. Treat the "Watched on ..." pattern as "no review".
- Titles contain XML entities (`&#039;`) and non-ASCII characters (`Zürrer`, `Lätscht`). Use a real XML parser and write JSON with `ensure_ascii=False`.
- Poster URLs are on `a.ltrbxd.com` at 600x900.

## Data contract (`_data/films.json`)

This is the only interface between backend and frontend. Keep it stable.

```json
{
  "user": "lemongiu_cinema",
  "last_logged_at": "2026-10-04",
  "entries": [
    {
      "id": "violette-2026-2026-10-01",
      "title": "Violette",
      "year": 2026,
      "watched": "2026-10-01",
      "rating": 4.5,
      "liked": true,
      "rewatch": false,
      "review": null,
      "tags": ["zff2026", "w-gold"],
      "url": "https://boxd.it/gAKk1n",
      "media": "movie",
      "tmdb_id": null,
      "poster": null,
      "logged_at": "2026-10-03"
    }
  ]
}
```

- `id` = `slugify("<title> <year> <watched>")` from `scripts/filmslib.py` (ASCII-folded, lowercase, hyphenated). Both importers use it. This is the dedupe key (it also lets the CSV backfill merge cleanly).
- `rating` is `null` when unrated. `review` is `null` when absent. `tags` is a list (possibly empty), data only, never rendered.
- `logged_at` is a bare date (`YYYY-MM-DD`) for CSV entries and a full timestamp for RSS entries. Both sort correctly as strings.
- `url` is the `boxd.it` short link for CSV entries and the full film URL for RSS entries (RSS wins on merge only if the CSV value is missing, so the short link stays; both resolve to the same film).
- There is no `generated_at` field: it would dirty the file (and git history) on every run.
- `entries` is sorted by `watched` desc, then `logged_at` desc.
- The store is **accumulating**: each run merges new feed items into the existing file and never truncates. This is how history grows beyond the feed's 50-item window.
- `last_logged_at` is the delta cursor: the newest `logged_at` seen so far (`filmslib.save` computes it). It is informational and used for logging ("N new, M updated since <cursor>"). Correctness relies on the `id` merge, not on the cursor, so edits to older entries still propagate while they remain inside the feed's window.
- Weekly cadence caveat: the feed window is about 50 items. If more than about 50 entries are logged or edited between two runs (e.g. a big backfill session), the oldest would fall out of the window. The script should warn when **all** feed items are new (no overlap with the stored data), since that signals possible loss. The fix is a manual `workflow_dispatch` run or a CSV import.

## Repo layout

```
index.html                     # homepage; films card (done)
_includes/films-row.html       # one row, shared by both (done)
_layouts/default.html          # + .films-* CSS block (done)
_data/films.json               # the store (130 entries imported)
scripts/filmslib.py            # slugify, load, deterministic save (done)
scripts/import_csv.py          # one-time history backfill (done)
scripts/update_films.py        # weekly RSS delta (done)
assets/posters/                # only if Task 2 is done
tests/fixtures/rss.xml         # feed snapshot 2026-10-04, trimmed to 7 items (done)
tests/test_films.py            # 10 offline unittest tests (done)
.github/workflows/letterboxd.yml   # weekly Action (done)
```

## Tasks

### Task 0: Fixture and exploration — DONE
- `curl -A "Mozilla/5.0" https://letterboxd.com/lemongiu_cinema/rss/ -o tests/fixtures/rss.xml`.
- Confirm the facts above still hold. Note any difference in a short comment at the top of the script.

**Done when:** fixture committed and facts confirmed. *Committed; later trimmed to 7 hand-picked items, see the docstring of `tests/test_films.py`.*

### Task 1: `scripts/update_films.py` — DONE
~110 lines, standard library only.

- **Config:** `LETTERBOXD_USER` env var only, read by `filmslib.require_user()` (shared with `import_csv.py`). No default, no `--rss-file`, no `--out`. Exits with "LETTERBOXD_USER is not set" if missing.
- **Fetch:** hardcoded `letterboxd.com` host, username validated against `[A-Za-z0-9_]+`, User-Agent, 30s timeout, 2 MB read cap. No retry: the next weekly run is the retry.
- **Parse:** real XML parser; skips items without `filmTitle` (lists); `tvId` means `media: "tv"`; rating float or `None`; review from the paragraphs after the poster, a lone "Watched on ..." means `None`. `logged_at` is the bare date of `pubDate` (same shape as CSV entries). `poster` stays `null` (the UI doesn't use posters).
- **Merge by `id`:** the feed wins for rating, rewatch, review, media, tmdb_id. Once set, the feed never overwrites `tags`, `url` (`boxd.it` links) or `logged_at`. **A like is never removed by the feed** (feed likes are per log, CSV likes are per film). Deleting an entry on Letterboxd does not remove it here.
- Prints `N new, M updated, K unchanged`. Warns if no feed item matches stored entries. Exits non-zero, file untouched, on a failed fetch or 0 films. `filmslib.save` writes deterministically and skips the write if nothing changed.

**Done when:** running it twice produces an identical file the second time. ✔ (`2 new, 48 updated`, then `0 new, 0 updated, 50 unchanged`)

### Task 2 (optional now): Poster caching
- For each entry without a local poster, download the feed's poster URL to `assets/posters/<tmdb_id>.jpg` (or `<id>.jpg` if there is no TMDB id).
- Skip existing files. Sleep about 0.5s between downloads. Never fail the whole run on one bad poster, and leave `poster: null` instead.
- Rationale: avoids hotlinking Letterboxd's CDN and avoids poster URL rot. Posters are saved as downloaded (no resizing). Expect roughly 10 MB or more for about 130 posters; mention this to the human and let them choose hotlinking instead if the repo size matters (open question 4). Since the UI is text-first, skip this unless posters are wanted.
- Entries imported from CSV have no poster URL, so `poster` stays `null` for them.

**Done when:** all RSS entries have a poster file or an explicit `null`.

### Task 3: Tests — DONE
`python3 -m unittest discover -s tests -v` (standard library, no pytest, so the workflow installs nothing). 10 tests in `tests/test_films.py`, offline, using the trimmed fixture: lists skipped, TV vs movie, entities and non-ASCII titles, review extraction, merge idempotency, stored fields kept and likes never removed, sorting by `watched` not feed order, empty feed exits without saving, missing or invalid user rejected. Not covered: `import_csv.py` (one-time script, no CSV fixture).

**Done when:** green with no network access. ✔

### Task 4: GitHub Action (`.github/workflows/letterboxd.yml`) — DONE
- Triggers: `schedule` Mondays `5 16 * * 1` (UTC; 17:05 Zürich in winter, 18:05 in summer) and `workflow_dispatch`.
- **As built, two jobs** (differs from the original single-job plan, for least privilege): `update` (`contents: read`) runs the tests and the script and uploads `_data/films.json` as an artifact; `commit` (`contents: write`, only on `main`) downloads it, checks it (not empty, not smaller than the stored file, entries have `id` and `watched`), requires that only `_data/films.json` differs, then commits as `github-actions[bot]` and pushes if changed. Top-level `permissions: {}`, `concurrency`, `timeout-minutes`, all actions pinned by commit SHA.
- `LETTERBOXD_USER` is a repository **variable** (Settings, Secrets and variables, Actions), passed through `env:`.
- Scheduled workflows are disabled by GitHub after about 60 days without repo activity; re-enable in the Actions tab if the site goes stale. A failed run leaves the site on the last good data.

**Done when:** a manual run produces a commit once, and a second run produces none. ✔ (and the site rebuilt)

### Task 5: Frontend — DONE
Server-side Liquid, no `films.js`, no separate page.

- **Placement:** two expanders in "What I do as well", each directly after the sentence that introduces it. The Strava card ("Statues while running · Logged on Strava") follows the paragraph about runs and statues. The Films card ("Films · Logged on Letterboxd") follows "Since summer 2025 I've been logging the films I watch, more or less consistently." The word "cinema" is an `a[href="#films"]` link that opens and scrolls to the card. Nothing opens on page load (same rule as `#statues`).
- **Card** (`index.html`, `<details id="films" class="films-card">`): same shell as `.project-card` / `.strava-embed-wrap`, round thumbnail, `h3`, muted subline, chevron.
- **List:** a `max-height: 26rem` vertical scroll area (keyboard focusable) with every entry, newest first, grouped by year with sticky year labels (`group_by_exp`; relies on the store being sorted by `watched` desc). A sticky header row reads *Watch date · Film title (year) · Personal review*. Dates are `DD.MM.`.
- **Row** (`_includes/films-row.html`): date, title (links to Letterboxd) and year, ♥ liked, ↺ rewatch, stars (`4.5` as `★★★★½`, with `role="img"` and an `aria-label`). **Review text is never shown**: films with a written review get a small speech-bubble icon next to the stars. Tags are not shown.
- **Hero:** `assets/films/hero.svg`, an original yellow and black leopard-style pattern (the Locarno poster is copyrighted, so it is not used). A small footnote under the list says it is an own illustration inspired by the festival's 2021 look.
- No posters in the UI, no filters, no jump-to-year, no stats. Add only if the list feels long.
- Not verified in a browser by Claude (no Chrome available). Check with `bundle exec jekyll serve`.

### Task 6: One-time history backfill — DONE

**Why manual:** the RSS feed exposes only about 50 items and Letterboxd's API is closed to personal projects. The official export is the supported way to get the complete history, and it only needs to be done once. After that, the weekly delta keeps everything current.

**Human steps (about 2 minutes):**
1. On Letterboxd: Settings, then Import & Export, then "Export your data". Download the zip.
2. Unzip into a gitignored folder (`tmp/` or `import/`, both in `.gitignore` now; the export contains private data such as your email and watchlist, so never commit it).
3. Files needed: `diary.csv`, plus optionally `reviews.csv` (review text) and `likes/films.csv` (liked flag).

**Result:** `python3 scripts/import_csv.py tmp/letterboxd-…/` gave `129 rows, 129 new` from the export taken 2026-10-04 11:30 UTC; a second run is a no-op. 21 liked, 3 reviews, 9 rewatches, 0 unrated, oldest entry Mamma Mia! (watched 2009-07-30). `diary.csv` headers matched the expected ones, plus a `Tags` column that is stored. Rebuild rule: the importer only *fills missing* fields, so to pick up edits made on Letterboxd, delete `_data/films.json` and re-import (safe only while no RSS data has been merged in).

**Claude Code steps (as built):** `scripts/import_csv.py`.
- Verify the real column headers first. Expected for `diary.csv`: Date, Name, Year, Letterboxd URI, Rating, Rewatch, Tags, Watched Date. Don't hard-code assumptions that the files contradict.
- Map each diary row to an entry: `title`, `year`, `watched` (from Watched Date), `rating` (float or `null`), `rewatch` (Yes means true), `logged_at` (from Date), `media: "movie"`, `url` (the Letterboxd URI, or build the film URL if it is a short link), `poster: null`, `tmdb_id: null`.
- Join `reviews.csv` on title, year and watched date to fill `review`. Join the likes file on title and year to fill `liked`. Leave `review: null` and `liked: false` when there is no match.
- Use the same `id` scheme as the RSS importer so entries present in both sources merge instead of duplicating. **RSS data wins** for entries in both, because it has posters and TMDB ids; fill only missing fields from CSV.
- Idempotent: running it twice changes nothing the second time.
- Print a summary (`130 rows, 82 new, 0 filled, 48 already present`).
- Posters: CSV-only entries stay `poster: null` and show the placeholder card. Poster enrichment is optional (see below).

**Done when:** `_data/films.json` holds all logged entries (129, matching the profile) and the list reaches the oldest one. ✔

**Optional poster enrichment (ask the human first):** use the TMDB API to find a poster by title and year, with `TMDB_API_KEY` stored as a GitHub Actions secret and never in client code. It needs a free TMDB account. Not needed while the UI is text-first.

### Task 7 (optional): Stats strip
Films this year, average rating, rating distribution, computed client-side from the accumulated JSON.

## Edge cases to handle

- Unrated films (`memberRating` missing).
- Same film logged twice on different dates (distinct `id`s, both kept).
- Very long reviews and reviews with line breaks or quotes.
- Entries whose `watchedDate` is far in the past (backfill), so group by watch date, never by log date.
- Letterboxd temporarily down, so the Action fails and the site keeps serving the last good JSON.

## Data oddities to surface to the human

- *The Six Billion Dollar Man* was logged twice. Resolved on Letterboxd: the 2025-10-05 duplicate was deleted, the 2025-10-04 entry (logged 2026-10-04) remains. The importer never removes entries, so a deletion on Letterboxd needs a manual removal from `_data/films.json` (or a rebuild, see Task 6).
- The export also has `deleted/` and `orphaned/` folders. They are ignored on purpose.
- The `likes` file is per film, not per log, so a film logged twice shows ♥ on both rows.

## Open questions

Answered:
1. Site type: user site, `giuliazobrist.github.io`.
2. Placement: inside the text, each card after its sentence (see Task 5). No nav link.
3. Reviews: text hidden, icon only.
4. Posters: none, text-first.
6. CSV backfill: done.
7. Design references: `CONTEXT.md` and the `.project-card` pattern.

Answered:
9. `w-*` tags: kept in the data, risk owned by Giulia (see Decisions section above).

Still open:
5. Weekly run time: Monday 16:05 UTC (decided).
8. Letterboxd links: entries link to `boxd.it` short URLs. Fine, or resolve to full film URLs?

## Git plan

Done: the work was merged to `main` in PR #5 (branch `feature/letterboxd-with-actions`). The weekly Action now commits `_data/films.json` to `main` directly, so **pull before you edit**.

Never commit: `tmp/` (the Letterboxd export holds email, watchlist, profile) and `.vscode/` (both gitignored).

## Out of scope

Login or private data, writing back to Letterboxd, the official API, scraping HTML pages.
